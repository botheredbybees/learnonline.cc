#!/usr/bin/env python3
"""
TGA API Integration Script

This script handles fetching and parsing data from the Training.gov.au API.
It includes functions for downloading XML files and extracting elements and PCs.
"""
from zeep import Client
from zeep.transports import Transport
from requests import Session
from requests.auth import HTTPBasicAuth
import psycopg2
from psycopg2.extras import DictCursor, Json
import os
from dotenv import load_dotenv
import sys
import logging
import re
import json
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import time
import tempfile
from datetime import datetime
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database connection parameters
DB_PARAMS = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

# ** Training.gov.au endpoints **
wsdl_url = "https://ws.sandbox.training.gov.au/Deewr.Tga.Webservices/TrainingComponentServiceV12.svc?wsdl"
xml_base_url = "https://training.gov.au/TrainingComponentFiles/"

# ** Authentication credentials **
username = "WebService.Read"
password = "Asdf098"

def store_training_package(cursor, tp):
    """Store a training package in the database."""
    try:
        cursor.execute("""
            INSERT INTO training_packages (code, title, description, status, release_date, last_checked)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (code) DO UPDATE
            SET title = EXCLUDED.title,
                description = EXCLUDED.description,
                status = EXCLUDED.status,
                last_checked = EXCLUDED.last_checked
            RETURNING id
        """, (tp.Code, tp.Title, getattr(tp, 'Description', None), 
              getattr(tp, 'Status', None), getattr(tp, 'ReleaseDate', None), datetime.now()))
        return cursor.fetchone()[0]
    except Exception as e:
        logger.error(f"Error storing training package {tp.Code}: {e}")
        return None

def store_unit(cursor, unit, training_package_id):
    """Store a unit in the database."""
    try:
        cursor.execute("""
            INSERT INTO units (training_package_id, code, title, description, status, release_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (code) DO UPDATE
            SET title = EXCLUDED.title,
                description = EXCLUDED.description,
                status = EXCLUDED.status,
                release_date = EXCLUDED.release_date
            RETURNING id
        """, (training_package_id, unit.Code, unit.Title, 
              getattr(unit, 'Description', None), getattr(unit, 'Status', None),
              getattr(unit, 'ReleaseDate', None)))
        return cursor.fetchone()[0]
    except Exception as e:
        logger.error(f"Error storing unit {unit.Code}: {e}")
        return None

def store_qualification(cursor, qual, training_package_id):
    """Store a qualification in the database."""
    try:
        cursor.execute("""
            INSERT INTO qualifications (training_package_id, code, title, description, status, release_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (code) DO UPDATE
            SET title = EXCLUDED.title,
                description = EXCLUDED.description,
                status = EXCLUDED.status,
                release_date = EXCLUDED.release_date
        """, (training_package_id, qual.Code, qual.Title, 
              getattr(qual, 'Description', None), getattr(qual, 'Status', None),
              getattr(qual, 'ReleaseDate', None)))
        return True
    except Exception as e:
        logger.error(f"Error storing qualification {qual.Code}: {e}")
        return False

def store_skillset(cursor, skillset, training_package_id):
    """Store a skillset in the database."""
    try:
        cursor.execute("""
            INSERT INTO skillsets (training_package_id, code, title, description, status, release_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (code) DO UPDATE
            SET title = EXCLUDED.title,
                description = EXCLUDED.description,
                status = EXCLUDED.status,
                release_date = EXCLUDED.release_date
        """, (training_package_id, skillset.Code, skillset.Title, 
              getattr(skillset, 'Description', None), getattr(skillset, 'Status', None),
              getattr(skillset, 'ReleaseDate', None)))
        return True
    except Exception as e:
        logger.error(f"Error storing skillset {skillset.Code}: {e}")
        return False

def get_xml_file(client, code):
    """
    Get the XML file for a unit, qualification, or skillset.
    Returns the XML file name if successful, None otherwise.
    """
    logger.info(f"Getting XML file for {code}")
    
    try:
        # Create information request
        information_request = {
            'ShowClassifications': False,
            'ShowCompletionMapping': False,
            'ShowComponents': False, 
            'ShowContacts': False,
            'ShowCurrencyPeriods': False,
            'ShowDataManagers': False,
            'ShowFiles': True,  # We need files
            'ShowMappingInformation': False,
            'ShowRecognitionManagers': False,
            'ShowReleases': True,  # We need releases
            'ShowUnitGrid': False,
            'ShowUsageRecommendation': False
        }
        
        # Create details request
        details_request = {
            'Code': code,
            'InformationRequest': information_request
        }
        
        # Get details
        results = client.service.GetDetails(request=details_request)
        
        if not hasattr(results, 'GetDetailsResult') or not results.GetDetailsResult:
            logger.error(f"No details found for {code}")
            return None, None
            
        # Get releases
        releases = results.GetDetailsResult.Releases
        if not releases or not hasattr(releases, 'Release'):
            logger.error(f"No releases found for {code}")
            return None, None
            
        # Get current release
        release = releases.Release
        if isinstance(release, list):
            # Take the latest release if multiple
            release = release[0]
            
        # Get files
        if not hasattr(release, 'Files') or not release.Files:
            logger.error(f"No files found for {code}")
            return None, None
            
        # Find XML file
        xml_file = None
        ar_file = None
        
        if hasattr(release.Files, 'ReleaseFile'):
            files = release.Files.ReleaseFile
            if not isinstance(files, list):
                files = [files]
                
            for file in files:
                if not hasattr(file, 'Filename'):
                    continue
                    
                filename = file.Filename
                if not filename.endswith('.xml'):
                    continue
                    
                # Skip assessment requirements for now
                if 'AssessmentRequirements' in filename:
                    ar_file = filename
                    continue
                    
                # Found the main XML file
                xml_file = filename
                
        # Check if we found both files        
        if not xml_file:
            logger.error(f"No XML file found for {code}")
            return None, None
            
        logger.info(f"Found XML file {xml_file} for {code}")
        if ar_file:
            logger.info(f"Found Assessment Requirements file {ar_file} for {code}")
            
        return xml_file, ar_file
        
    except Exception as e:
        logger.error(f"Error getting XML file for {code}: {e}")
        return None, None

def download_xml(code, filename):
    """
    Download an XML file from training.gov.au.
    Returns the XML content if successful, None otherwise.
    """
    if not filename:
        return None
        
    try:
        # Construct URL
        url = f"{xml_base_url}{filename}"
        
        # Download file
        response = requests.get(url)
        if response.status_code != 200:
            logger.error(f"Failed to download {url}: {response.status_code}")
            return None
            
        return response.text
        
    except Exception as e:
        logger.error(f"Error downloading XML for {code}: {e}")
        return None

def parse_elements_and_pcs(unit_xml):
    """
    Parse elements and performance criteria from unit XML.
    Returns a list of elements with their performance criteria.
    """
    if not unit_xml:
        return None
        
    try:
        # Parse XML
        soup = BeautifulSoup(unit_xml, 'lxml')
        if not soup:
            logger.error("Failed to create BeautifulSoup object")
            return None
            
        # Extract elements and PCs
        elements = []
        
        # Find all tables
        tables = soup.find_all('table')
        if not tables:
            logger.warning("No tables found in XML")
            return None
        
        # Look for a table with Elements and Performance criteria
        elements_table = None
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) >= 2:  # Need at least headers and one data row
                cells = rows[0].find_all('td')
                if len(cells) >= 2:
                    cell1_text = cells[0].get_text().strip()
                    cell2_text = cells[1].get_text().strip()
                    # Different patterns we might see in table headers
                    if any([
                        ("Elements" in cell1_text and "Performance" in cell2_text),
                        ("ELEMENT" in cell1_text.upper() and "PERFORMANCE" in cell2_text.upper()),
                        (cell1_text == "Elements" and cell2_text == "Performance criteria"),
                        # Add additional patterns here if needed
                    ]):
                        elements_table = table
                        break
        
        if elements_table:
            rows = elements_table.find_all('tr')
            # Skip the first two rows (headers and explanation)
            data_rows = rows[2:]
            
            current_element = None
            
            for row in data_rows:
                cells = row.find_all('td')
                if len(cells) < 2:
                    continue
                
                # Get text from all cells
                cell_texts = [cell.get_text().strip() for cell in cells]
                
                # Check for element in first column - various patterns
                is_element_row = False
                
                if len(cells) >= 2:
                    # Check for common element number patterns
                    if re.match(r'^[1-9][0-9]*$', cell_texts[0]):  # Simple number: 1, 2, 3
                        is_element_row = True
                        element_num = cell_texts[0]
                    elif re.match(r'^Element\s+[1-9][0-9]*$', cell_texts[0], re.IGNORECASE):  # "Element 1"
                        is_element_row = True
                        element_num = cell_texts[0].split()[-1]
                    elif re.match(r'^[A-Z][1-9][0-9]*$', cell_texts[0]):  # Format like: A1, B2, etc.
                        is_element_row = True
                        element_num = cell_texts[0]
                
                if is_element_row:    
                    # This looks like an element row
                    element_text = cell_texts[1] if len(cell_texts) > 1 else ""
                    
                    current_element = {
                        'element_num': element_num,
                        'element_text': element_text,
                        'performance_criteria': []
                    }
                    elements.append(current_element)
                    
                    # Check if this row also has a PC
                    if len(cell_texts) >= 4:
                        # Check common PC number patterns
                        pc_pattern_match = (
                            re.match(r'^[1-9][0-9]*\.[1-9][0-9]*$', cell_texts[2]) or  # 1.1, 1.2
                            re.match(r'^[1-9][0-9]*\.[1-9][0-9]*\.[1-9][0-9]*$', cell_texts[2]) or  # 1.1.1, 1.1.2
                            re.match(r'^[A-Z][1-9][0-9]*\.[1-9][0-9]*$', cell_texts[2])  # A1.1, B2.3
                        )
                        
                        if pc_pattern_match:
                            pc_num = cell_texts[2]
                            pc_text = cell_texts[3] if len(cell_texts) > 3 else ""
                            
                            current_element['performance_criteria'].append({
                                'pc_num': pc_num,
                                'pc_text': pc_text
                            })
                
                # Check for performance criteria in cells 3 & 4 (if element exists)
                elif current_element and len(cells) >= 4:
                    # Check common PC number patterns
                    pc_pattern_match = (
                        re.match(r'^[1-9][0-9]*\.[1-9][0-9]*$', cell_texts[2]) or  # 1.1, 1.2
                        re.match(r'^[1-9][0-9]*\.[1-9][0-9]*\.[1-9][0-9]*$', cell_texts[2]) or  # 1.1.1, 1.1.2
                        re.match(r'^[A-Z][1-9][0-9]*\.[1-9][0-9]*$', cell_texts[2])  # A1.1, B2.3
                    )
                    
                    if pc_pattern_match:
                    pc_num = cell_texts[2]
                    pc_text = cell_texts[3]
                    
                    current_element['performance_criteria'].append({
                        'pc_num': pc_num,
                        'pc_text': pc_text
                    })
        
        return elements
                
    except Exception as e:
        logger.error(f"Error parsing elements and PCs: {e}")
        return None

def store_elements_and_pcs(cursor, unit_id, elements):
    """
    Store elements and performance criteria in the database.
    Returns True if successful, False otherwise.
    """
    if not elements:
        return False
        
    try:
        # First, delete existing elements and PCs
        cursor.execute("DELETE FROM unit_performance_criteria WHERE unit_id = %s", (unit_id,))
        cursor.execute("DELETE FROM unit_elements WHERE unit_id = %s", (unit_id,))
        
        # Store each element
        for element in elements:
            # Insert element
            cursor.execute("""
                INSERT INTO unit_elements (unit_id, element_num, element_text)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (unit_id, element.get('element_num', ''), element.get('element_text', '')))
            
            element_id = cursor.fetchone()[0]
            
            # Store PCs for this element
            pcs = element.get('performance_criteria', [])
            for pc in pcs:
                cursor.execute("""
                    INSERT INTO unit_performance_criteria (element_id, unit_id, pc_num, pc_text)
                    VALUES (%s, %s, %s, %s)
                """, (element_id, unit_id, pc.get('pc_num', ''), pc.get('pc_text', '')))
                
        # Store JSON representation in units table for quick access
        cursor.execute("""
            UPDATE units
            SET elements_json = %s
            WHERE id = %s
        """, (Json(elements), unit_id))
        
        return True
        
    except Exception as e:
        logger.error(f"Error storing elements and PCs for unit {unit_id}: {e}")
        return False

def process_unit_xml(client, cursor, unit_id, unit_code):
    """
    Process a unit XML file to extract elements and performance criteria.
    """
    logger.info(f"Processing unit XML for {unit_code} (ID: {unit_id})")
    
    try:
        # Get XML file
        xml_file, ar_file = get_xml_file(client, unit_code)
        if not xml_file:
            logger.warning(f"No XML file found for {unit_code}")
            return False
            
        # Store XML file names in database
        cursor.execute("""
            UPDATE units
            SET xml_file = %s, assessment_requirements_file = %s
            WHERE id = %s
        """, (xml_file, ar_file, unit_id))
            
        # Download XML
        xml_content = download_xml(unit_code, xml_file)
        if not xml_content:
            logger.warning(f"Failed to download XML for {unit_code}")
            return False
            
        # Parse elements and PCs
        elements = parse_elements_and_pcs(xml_content)
        if not elements:
            logger.warning(f"No elements found in XML for {unit_code}")
            return False
            
        # Store elements and PCs
        return store_elements_and_pcs(cursor, unit_id, elements)
        
    except Exception as e:
        logger.error(f"Error processing XML for unit {unit_code}: {e}")
        return False

def process_unit_xml_from_file(cursor, unit_id, unit_code, file_path):
    """
    Process a local unit XML file to extract elements and performance criteria.
    """
    logger.info(f"Processing local XML file for {unit_code} (ID: {unit_id}): {file_path}")
    
    try:
        # Read XML file
        with open(file_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
            
        # Parse elements and PCs
        elements = parse_elements_and_pcs(xml_content)
        if not elements:
            logger.warning(f"No elements found in XML for {unit_code}")
            return False
            
        # Store elements and PCs
        return store_elements_and_pcs(cursor, unit_id, elements)
        
    except Exception as e:
        logger.error(f"Error processing XML for unit {unit_code} from file {file_path}: {e}")
        return False

def fetch_and_store_tp_components(client, cursor, tp_code=None, tp_id=None):
    """Fetch and store training package components (units, qualifications, skillsets)"""
    
    if not tp_code and not tp_id:
        logger.error("Either tp_code or tp_id must be provided")
        return False
        
    if tp_code and not tp_id:
        # Get the training package ID from code
        cursor.execute("SELECT id FROM training_packages WHERE code = %s", (tp_code,))
        result = cursor.fetchone()
        if not result:
            logger.error(f"Training package {tp_code} not found in database")
            return False
        tp_id = result[0]
        
    stats = {
        'units': 0,
        'units_with_elements': 0,
        'qualifications': 0,
        'skillsets': 0
    }
    
    # Fetch units
    units_request = {
        'Filter': tp_code if tp_code else '',
        'IncludeDeleted': False,
        'IncludeSuperseded': True,
        'SearchCode': True,
        'PageNumber': 1,
        'PageSize': 1000,
        'TrainingComponentTypes': {
            'IncludeAccreditedCourse': False,
            'IncludeAccreditedCourseModule': False,
            'IncludeQualification': False,
            'IncludeSkillSet': False,
            'IncludeTrainingPackage': False,
            'IncludeUnit': True,
            'IncludeUnitContextualisation': False
        }
    }
    
    try:
        units_result = client.service.Search(request=units_request)
        if hasattr(units_result, 'Results') and units_result.Results:
            units = units_result.Results.TrainingComponentSummary
            if not isinstance(units, list):
                units = [units]
                
            for unit in units:
                unit_id = store_unit(cursor, unit, tp_id)
                if unit_id:
                    stats['units'] += 1
                    
                    # Process unit XML to extract elements and PCs
                    if process_unit_xml(client, cursor, unit_id, unit.Code):
                        stats['units_with_elements'] += 1
                    
                    # Sleep briefly to avoid overloading the API
                    time.sleep(0.5)
    except Exception as e:
        logger.error(f"Error fetching units: {e}")
        
    # Fetch qualifications
    quals_request = {
        'Filter': tp_code if tp_code else '',
        'IncludeDeleted': False,
        'IncludeSuperseded': True,
        'SearchCode': True,
        'PageNumber': 1,
        'PageSize': 1000,
        'TrainingComponentTypes': {
            'IncludeAccreditedCourse': False,
            'IncludeAccreditedCourseModule': False,
            'IncludeQualification': True,
            'IncludeSkillSet': False,
            'IncludeTrainingPackage': False,
            'IncludeUnit': False,
            'IncludeUnitContextualisation': False
        }
    }
    
    try:
        quals_result = client.service.Search(request=quals_request)
        if hasattr(quals_result, 'Results') and quals_result.Results:
            quals = quals_result.Results.TrainingComponentSummary
            if not isinstance(quals, list):
                quals = [quals]
                
            for qual in quals:
                if store_qualification(cursor, qual, tp_id):
                    stats['qualifications'] += 1
    except Exception as e:
        logger.error(f"Error fetching qualifications: {e}")
        
    # Fetch skillsets
    skillsets_request = {
        'Filter': tp_code if tp_code else '',
        'IncludeDeleted': False,
        'IncludeSuperseded': True,
        'SearchCode': True,
        'PageNumber': 1,
        'PageSize': 1000,
        'TrainingComponentTypes': {
            'IncludeAccreditedCourse': False,
            'IncludeAccreditedCourseModule': False,
            'IncludeQualification': False,
            'IncludeSkillSet': True,
            'IncludeTrainingPackage': False,
            'IncludeUnit': False,
            'IncludeUnitContextualisation': False
        }
    }
    
    try:
        skillsets_result = client.service.Search(request=skillsets_request)
        if hasattr(skillsets_result, 'Results') and skillsets_result.Results:
            skillsets = skillsets_result.Results.TrainingComponentSummary
            if not isinstance(skillsets, list):
                skillsets = [skillsets]
                
            for skillset in skillsets:
                if store_skillset(cursor, skillset, tp_id):
                    stats['skillsets'] += 1
    except Exception as e:
        logger.error(f"Error fetching skillsets: {e}")
        
    return stats

def get_training_packages(tp_codes=None):
    """
    Fetch training packages and their components from TGA.
    If tp_codes is provided, only fetch those training packages.
    Otherwise, fetch all training packages.
    """
    results = {
        'training_packages': 0,
        'units': 0,
        'units_with_elements': 0,
        'qualifications': 0,
        'skillsets': 0
    }
    
    try:
        # Create a session with basic authentication
        session = Session()
        session.auth = HTTPBasicAuth(username, password)
        transport = Transport(session=session)

        # Create a SOAP client
        client = Client(wsdl=wsdl_url, transport=transport)

        # Connect to the database
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                # If specific TP codes provided, fetch only those
                if tp_codes:
                    for tp_code in tp_codes:
                        logger.info(f"Fetching training package: {tp_code}")
                        # Search for the training package
                        tp_request = {
                            'Filter': tp_code,
                            'IncludeDeleted': False,
                            'IncludeSuperseded': True,
                            'SearchCode': True,
                            'PageNumber': 1,
                            'PageSize': 10,
                            'TrainingComponentTypes': {
                                'IncludeAccreditedCourse': False,
                                'IncludeAccreditedCourseModule': False,
                                'IncludeQualification': False,
                                'IncludeSkillSet': False,
                                'IncludeTrainingPackage': True,
                                'IncludeUnit': False,
                                'IncludeUnitContextualisation': False
                            }
                        }
                        
                        tp_result = client.service.Search(request=tp_request)
                        
                        if hasattr(tp_result, 'Results') and tp_result.Results:
                            training_packages = tp_result.Results.TrainingComponentSummary
                            if training_packages:
                                if not isinstance(training_packages, list):
                                    training_packages = [training_packages]
                                    
                                tp = training_packages[0]  # Should only be one
                                logger.info(f"Storing Training Package: {tp.Code} - {tp.Title}")
                                tp_id = store_training_package(cur, tp)
                                if tp_id:
                                    results['training_packages'] += 1
                                    # Now fetch and store components for this TP
                                    component_stats = fetch_and_store_tp_components(client, cur, tp_code=tp.Code, tp_id=tp_id)
                                    if component_stats:
                                        results['units'] += component_stats['units']
                                        results['units_with_elements'] += component_stats['units_with_elements']
                                        results['qualifications'] += component_stats['qualifications']
                                        results['skillsets'] += component_stats['skillsets']
                else:
                    # Fetch all training packages
                    tp_request = {
                        'Filter': '',
                        'IncludeDeleted': False,
                        'IncludeSuperseded': False,
                        'SearchCode': False,
                        'PageNumber': 1,
                        'PageSize': 100,
                        'TrainingComponentTypes': {
                            'IncludeAccreditedCourse': False,
                            'IncludeAccreditedCourseModule': False,
                            'IncludeQualification': False,
                            'IncludeSkillSet': False,
                            'IncludeTrainingPackage': True,
                            'IncludeUnit': False,
                            'IncludeUnitContextualisation': False
                        }
                    }
                    
                    # Call the Search operation
                    search_result = client.service.Search(request=tp_request)

                    if hasattr(search_result, 'Results') and search_result.Results:
                        training_packages = search_result.Results.TrainingComponentSummary
                        if training_packages:
                            if not isinstance(training_packages, list):
                                training_packages = [training_packages]
                                
                            logger.info("Processing Training Packages:")
                            for tp in training_packages:
                                logger.info(f"Storing Training Package: {tp.Code} - {tp.Title}")
                                tp_id = store_training_package(cur, tp)
                                if tp_id:
                                    results['training_packages'] += 1
                                    # Now fetch and store components for this TP
                                    component_stats = fetch_and_store_tp_components(client, cur, tp_code=tp.Code, tp_id=tp_id)
                                    if component_stats:
                                        results['units'] += component_stats['units']
                                        results['units_with_elements'] += component_stats['units_with_elements']
                                        results['qualifications'] += component_stats['qualifications']
                                        results['skillsets'] += component_stats['skillsets']
                
                conn.commit()
                logger.info(
                    f"Successfully stored {results['training_packages']} training packages, "
                    f"{results['units']} units ({results['units_with_elements']} with elements), "
                    f"{results['qualifications']} qualifications, and "
                    f"{results['skillsets']} skillsets in the database."
                )
                return results

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return {"error": str(e)}

def process_existing_units(specific_unit_id=None):
    """
    Process existing units in the database to extract elements and PCs.
    This is useful for updating existing data.
    If specific_unit_id is provided, only process that unit.
    """
    results = {
        'total': 0,
        'processed': 0,
        'with_elements': 0,
        'errors': 0
    }
    
    try:
        # Create a session with basic authentication
        session = Session()
        session.auth = HTTPBasicAuth(username, password)
        transport = Transport(session=session)

        # Create a SOAP client
        client = Client(wsdl=wsdl_url, transport=transport)

        # Connect to the database
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                # Get units to process
                if specific_unit_id:
                    cur.execute("""
                        SELECT id, code
                        FROM units
                        WHERE id = %s
                    """, (specific_unit_id,))
                else:
                    # Get all units without elements
                    cur.execute("""
                        SELECT id, code
                        FROM units
                        WHERE elements_json IS NULL
                        ORDER BY code
                    """)
                
                units = cur.fetchall()
                results['total'] = len(units)
                
                logger.info(f"Found {results['total']} units to process")
                
                for unit in units:
                    unit_id = unit['id']
                    unit_code = unit['code']
                    
                    logger.info(f"Processing unit {unit_code} (ID: {unit_id})")
                    
                    # Process unit XML
                    try:
                        results['processed'] += 1
                        if process_unit_xml(client, cur, unit_id, unit_code):
                            results['with_elements'] += 1
                        
                        # Commit after each unit to avoid losing all work on error
                        conn.commit()
                        
                        # Sleep briefly to avoid overloading the API
                        time.sleep(0.5)
                        
                    except Exception as e:
                        results['errors'] += 1
                        logger.error(f"Error processing unit {unit_code}: {e}")
                        # Continue with next unit
                
                logger.info(
                    f"Processed {results['processed']} units, "
                    f"{results['with_elements']} with elements, "
                    f"{results['errors']} errors"
                )
                
                return results
                
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return {"error": str(e)}

def process_local_xml_files(base_dir=None, tp_code=None):
    """
    Process local XML files to extract elements and PCs.
    If base_dir is not provided, use the default 'tgaWebServiceKit-2021-12-01/xml' directory.
    If tp_code is provided, only process files for that training package.
    """
    if not base_dir:
        base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tgaWebServiceKit-2021-12-01', 'xml')
    
    if not os.path.exists(base_dir):
        logger.error(f"Directory not found: {base_dir}")
        return {"error": f"Directory not found: {base_dir}"}
    
    results = {
        'total': 0,
        'processed': 0,
        'with_elements': 0,
        'errors': 0
    }
    
    try:
        # Connect to the database
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                # Find all unit XML files
                unit_files = []
                for file in os.listdir(base_dir):
                    if file.startswith('Unit_') and file.endswith('.xml'):
                        unit_code = file.split('_')[1].split('_')[0]  # Extract code like 'PUAAMS101' from 'Unit_PUAAMS101_R1.xml'
                        
                        # If tp_code is specified, check if this unit belongs to that TP
                        if tp_code and not unit_code.startswith(tp_code):
                            continue
                            
                        unit_files.append((file, unit_code))
                
                results['total'] = len(unit_files)
                logger.info(f"Found {results['total']} unit XML files")
                
                for file_name, unit_code in unit_files:
                    # Check if this unit exists in the database
                    cur.execute("""
                        SELECT id FROM units WHERE code = %s
                    """, (unit_code,))
                    
                    unit_row = cur.fetchone()
                    if not unit_row:
                        # Create a new unit entry
                        cur.execute("""
                            INSERT INTO units (code, title)
                            VALUES (%s, %s)
                            RETURNING id
                        """, (unit_code, f"Unit {unit_code} (from local XML)"))
                        
                        unit_id = cur.fetchone()[0]
                        logger.info(f"Created new unit: {unit_code} (ID: {unit_id})")
                    else:
                        unit_id = unit_row['id']
                        logger.info(f"Found existing unit: {unit_code} (ID: {unit_id})")
                    
                    # Process the XML file
                    try:
                        results['processed'] += 1
                        if process_unit_xml_from_file(cur, unit_id, unit_code, os.path.join(base_dir, file_name)):
                            results['with_elements'] += 1
                        
                        # Commit after each unit
                        conn.commit()
                        
                    except Exception as e:
                        results['errors'] += 1
                        logger.error(f"Error processing unit XML file {file_name}: {e}")
                        # Continue with next file
                
                logger.info(
                    f"Processed {results['processed']} units, "
                    f"{results['with_elements']} with elements, "
                    f"{results['errors']} errors"
                )
                
                return results
                
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch training packages from TGA')
    parser.add_argument('--tp-codes', nargs='+', help='Optional list of training package codes to fetch')
    parser.add_argument('--process-existing', action='store_true', help='Process existing units to extract elements and PCs')
    parser.add_argument('--unit-id', type=int, help='Process a specific unit by ID')
    parser.add_argument('--process-local', action='store_true', help='Process local XML files')
    parser.add_argument('--xml-dir', help='Directory containing XML files (default: tgaWebServiceKit-2021-12-01/xml)')
    args = parser.parse_args()
    
    if args.process_existing:
        results = process_existing_units(args.unit_id)
        if "error" in results:
            sys.exit(1)
        else:
            print(f"Processed {results['processed']} units")
            print(f"Units with elements: {results['with_elements']}")
            print(f"Errors: {results['errors']}")
            sys.exit(0)
    elif args.process_local:
        results = process_local_xml_files(args.xml_dir)
        if "error" in results:
            sys.exit(1)
        else:
            print(f"Processed {results['processed']} units")
            print(f"Units with elements: {results['with_elements']}")
            print(f"Errors: {results['errors']}")
            sys.exit(0)
    else:
        results = get_training_packages(args.tp_codes)
        
        if "error" in results:
            sys.exit(1)
        else:
            print(f"Training Packages: {results['training_packages']}")
            print(f"Units: {results['units']} (with elements: {results['units_with_elements']})")
            print(f"Qualifications: {results['qualifications']}")
            print(f"Skillsets: {results['skillsets']}")
            sys.exit(0)
