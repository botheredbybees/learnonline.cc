#!/usr/bin/env python3
"""
Example script for working with TGA XML files

This script shows how to:
1. Parse a unit XML file and extract elements and performance criteria
2. Store the extracted elements in the database
3. Access elements and PCs from the database
"""
import os
import sys
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, ROOT_DIR)

# Import the TGA modules
from backend.scripts.tga.tp_get import parse_elements_and_pcs

def example_parse_xml():
    """
    Example of parsing XML files and extracting elements and PCs
    """
    # Define paths
    xml_dir = os.path.join(ROOT_DIR, 'tgaWebServiceKit-2021-12-01', 'xml')
    unit_code = 'PUAAMS101'
    xml_file = os.path.join(xml_dir, f'Unit_{unit_code}_R1.xml')
    
    if not os.path.exists(xml_file):
        logger.error(f"XML file not found: {xml_file}")
        logger.info(f"Available XML files in {xml_dir}:")
        for file in os.listdir(xml_dir):
            if file.startswith('Unit_') and file.endswith('.xml'):
                logger.info(f"  {file}")
        return
    
    # Read the XML file
    logger.info(f"Reading {xml_file}...")
    with open(xml_file, 'r', encoding='utf-8') as f:
        xml_content = f.read()
    
    # Parse elements and PCs
    logger.info("Parsing elements and performance criteria...")
    elements = parse_elements_and_pcs(xml_content)
    
    if not elements:
        logger.error("No elements found in the XML")
        return
    
    # Display the elements and PCs
    logger.info(f"Found {len(elements)} elements:")
    
    for i, element in enumerate(elements):
        logger.info(f"Element {i+1}: {element['element_num']} - {element['element_text']}")
        
        pcs = element.get('performance_criteria', [])
        if pcs:
            logger.info(f"  Performance criteria:")
            for j, pc in enumerate(pcs):
                logger.info(f"    {pc['pc_num']}: {pc['pc_text']}")
        else:
            logger.info("  No performance criteria found")
    
    # Save to JSON file for inspection
    output_dir = os.path.join(ROOT_DIR, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{unit_code}_elements.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(elements, f, indent=2)
    
    logger.info(f"Saved elements to {output_file}")

if __name__ == "__main__":
    example_parse_xml()
