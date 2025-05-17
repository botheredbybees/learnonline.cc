#!/usr/bin/env python3
"""
Test script for XML parsing and database storage functions.

This script can be used to test:
1. Parsing XML files from training.gov.au
2. Parsing local XML files
3. Storing elements and performance criteria in the database
"""
import os
import sys
import argparse
import json
import logging
from datetime import datetime
import psycopg2
from psycopg2.extras import DictCursor, Json
from dotenv import load_dotenv
import pathlib

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.tga import parse_elements_and_pcs, process_unit_xml_from_file

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

def parse_xml_files(xml_dir, output_dir=None):
    """
    Parse all XML files in the given directory and extract elements and PCs.
    Optionally save the results to JSON files in the output directory.
    """
    if not output_dir:
        output_dir = os.path.join(os.getcwd(), "output")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all unit XML files
    files = os.listdir(xml_dir)
    unit_files = [f for f in files if f.startswith('Unit_') and f.endswith('.xml')]
    
    logger.info(f"Found {len(unit_files)} unit XML files")
    
    results = []
    for filename in unit_files:
        unit_code = filename.split('_')[1].split('_')[0]
        logger.info(f"Processing {unit_code} from {filename}...")
        
        # Read XML content
        file_path = os.path.join(xml_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
                
            # Parse elements and PCs
            elements = parse_elements_and_pcs(xml_content)
            
            if not elements:
                logger.warning(f"No elements found in {filename}")
                continue
                
            # Print summary
            logger.info(f"Found {len(elements)} elements")
            for element in elements:
                pc_count = len(element.get('performance_criteria', []))
                logger.info(f"Element {element.get('element_num', 'N/A')}: "
                      f"{element.get('element_text', 'No text')} "
                      f"({pc_count} PCs)")
                
            # Save to JSON file
            output_file = os.path.join(output_dir, f"{unit_code}_elements.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(elements, f, indent=2)
                
            logger.info(f"Saved elements to {output_file}")
            
            # Add to results
            results.append({
                'unit_code': unit_code,
                'filename': filename,
                'element_count': len(elements),
                'pc_count': sum(len(element.get('performance_criteria', [])) for element in elements)
            })
        
        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")
    
    # Save summary
    summary_file = os.path.join(output_dir, "summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            'processed_at': datetime.now().isoformat(),
            'file_count': len(unit_files),
            'success_count': len(results),
            'results': results
        }, f, indent=2)
    
    logger.info(f"Processed {len(results)} of {len(unit_files)} files successfully")
    logger.info(f"Summary saved to {summary_file}")
    
    return results

def process_single_unit(unit_code, xml_dir):
    """
    Process a single unit XML file and print the extracted elements and PCs.
    """
    # Find the XML file for the unit
    file_pattern = f"Unit_{unit_code}_"
    matching_files = [f for f in os.listdir(xml_dir) if f.startswith(file_pattern) and f.endswith('.xml')]
    
    if not matching_files:
        logger.error(f"No XML file found for unit {unit_code}")
        return False
    
    filename = matching_files[0]  # Use the first matching file
    file_path = os.path.join(xml_dir, filename)
    
    logger.info(f"Processing {unit_code} from {filename}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
            
        # Parse elements and PCs
        elements = parse_elements_and_pcs(xml_content)
        
        if not elements:
            logger.error(f"No elements found in {filename}")
            return False
            
        # Print detailed information
        logger.info(f"Found {len(elements)} elements:")
        for i, element in enumerate(elements):
            logger.info(f"Element {i+1}: {element.get('element_num', 'N/A')} - {element.get('element_text', 'No text')}")
            
            pcs = element.get('performance_criteria', [])
            if pcs:
                logger.info(f"  Performance criteria:")
                for j, pc in enumerate(pcs):
                    logger.info(f"    {pc.get('pc_num', 'N/A')}: {pc.get('pc_text', 'No text')}")
            else:
                logger.info("  No performance criteria found")
        
        return elements
    
    except Exception as e:
        logger.error(f"Error processing {filename}: {e}")
        return False

def store_unit_in_db(unit_code, elements, create_if_missing=False):
    """
    Store unit elements and performance criteria in the database.
    """
    if not elements:
        logger.error("No elements provided")
        return False
    
    try:
        # Connect to the database
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                # Check if unit exists
                cur.execute("SELECT id FROM units WHERE code = %s", (unit_code,))
                unit = cur.fetchone()
                
                if not unit:
                    if create_if_missing:
                        # Create a new unit
                        cur.execute("""
                            INSERT INTO units (code, title)
                            VALUES (%s, %s)
                            RETURNING id
                        """, (unit_code, f"Unit {unit_code} (from test)"))
                        
                        unit_id = cur.fetchone()[0]
                        logger.info(f"Created new unit: {unit_code} (ID: {unit_id})")
                    else:
                        logger.error(f"Unit {unit_code} not found in database")
                        return False
                else:
                    unit_id = unit['id']
                    logger.info(f"Found unit: {unit_code} (ID: {unit_id})")
                
                # Delete existing elements and PCs
                cur.execute("DELETE FROM unit_performance_criteria WHERE unit_id = %s", (unit_id,))
                cur.execute("DELETE FROM unit_elements WHERE unit_id = %s", (unit_id,))
                
                # Store each element
                for element in elements:
                    # Insert element
                    cur.execute("""
                        INSERT INTO unit_elements (unit_id, element_num, element_text)
                        VALUES (%s, %s, %s)
                        RETURNING id
                    """, (unit_id, element.get('element_num', ''), element.get('element_text', '')))
                    
                    element_id = cur.fetchone()[0]
                    
                    # Store PCs for this element
                    pcs = element.get('performance_criteria', [])
                    for pc in pcs:
                        cur.execute("""
                            INSERT INTO unit_performance_criteria (element_id, unit_id, pc_num, pc_text)
                            VALUES (%s, %s, %s, %s)
                        """, (element_id, unit_id, pc.get('pc_num', ''), pc.get('pc_text', '')))
                        
                # Store JSON representation in units table
                cur.execute("""
                    UPDATE units
                    SET elements_json = %s
                    WHERE id = %s
                """, (Json(elements), unit_id))
                
                # Commit changes
                conn.commit()
                
                logger.info(f"Successfully stored elements and PCs for unit {unit_code}")
                return True
    
    except Exception as e:
        logger.error(f"Error storing elements for unit {unit_code}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Test XML parsing and database storage')
    parser.add_argument('--parse-all', action='store_true', help='Parse all XML files in the directory')
    parser.add_argument('--unit', help='Process a specific unit code')
    parser.add_argument('--store', action='store_true', help='Store elements in the database')
    parser.add_argument('--create-unit', action='store_true', help='Create unit if it doesn\'t exist')
    parser.add_argument('--xml-dir', default=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'tgaWebServiceKit-2021-12-01', 'xml'),
                        help='Directory containing XML files')
    parser.add_argument('--output-dir', help='Directory to save JSON output')
    args = parser.parse_args()
    
    # Check if XML directory exists
    if not os.path.exists(args.xml_dir):
        logger.error(f"XML directory not found: {args.xml_dir}")
        return 1
    
    if args.parse_all:
        # Parse all XML files
        parse_xml_files(args.xml_dir, args.output_dir)
    elif args.unit:
        # Process a specific unit
        elements = process_single_unit(args.unit, args.xml_dir)
        
        # Store in database if requested
        if args.store and elements:
            store_unit_in_db(args.unit, elements, args.create_unit)
    else:
        logger.error("No action specified. Use --parse-all or --unit")
        parser.print_help()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
