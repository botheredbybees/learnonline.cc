#!/usr/bin/env python3
"""
Helper script for analyzing XML files in a directory

This script finds all XML files in a directory, analyzes their structure,
and prints information about elements and performance criteria.
"""
import os
import sys
import re
import logging
from pathlib import Path
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_xml_files(xml_dir):
    """
    Analyze XML files in the directory
    """
    if not os.path.exists(xml_dir):
        logger.error(f"Directory not found: {xml_dir}")
        return
    
    # Find all unit XML files
    files = os.listdir(xml_dir)
    unit_files = [f for f in files if f.startswith('Unit_') and f.endswith('.xml')]
    
    if not unit_files:
        logger.error(f"No unit XML files found in {xml_dir}")
        return
    
    logger.info(f"Found {len(unit_files)} unit XML files")
    
    # Analyze each file
    for filename in sorted(unit_files):
        file_path = os.path.join(xml_dir, filename)
        logger.info(f"\nAnalyzing {filename}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(xml_content, 'lxml')
            
            # Find tables
            tables = soup.find_all('table')
            logger.info(f"Found {len(tables)} tables")
            
            # Analyze each table
            for i, table in enumerate(tables):
                rows = table.find_all('tr')
                if not rows:
                    continue
                
                logger.info(f"\nTable {i+1}: {len(rows)} rows")
                
                # Analyze first row to detect headers
                header_row = rows[0]
                header_cells = header_row.find_all('td')
                
                if header_cells:
                    header_texts = [cell.get_text().strip() for cell in header_cells]
                    logger.info(f"Headers: {' | '.join(header_texts)}")
                    
                    # Check if this looks like an elements table
                    is_elements_table = False
                    for j, header in enumerate(header_texts):
                        if "element" in header.lower() or "elements" == header.lower():
                            is_elements_table = True
                            logger.info(f"This appears to be an elements table (Element column: {j+1})")
                            break
                    
                    if is_elements_table:
                        # Analyze a few data rows
                        for j, row in enumerate(rows[1:5]):  # Look at first few data rows
                            cells = row.find_all('td')
                            if cells:
                                cell_texts = [cell.get_text().strip() for cell in cells]
                                logger.info(f"Row {j+2}: {' | '.join(cell_texts[:4])}")  # First 4 cells
        
        except Exception as e:
            logger.error(f"Error analyzing {filename}: {e}")

def main():
    # Default XML directory
    default_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
        'tgaWebServiceKit-2021-12-01', 
        'xml'
    )
    
    # Check command line arguments
    xml_dir = default_dir
    if len(sys.argv) > 1:
        xml_dir = sys.argv[1]
    
    logger.info(f"Analyzing XML files in {xml_dir}")
    analyze_xml_files(xml_dir)

if __name__ == "__main__":
    main()
