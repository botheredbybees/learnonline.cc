#!/usr/bin/env python3
"""
Simple script to test the XML parsing functionality in tp_get.py
"""
import os
import sys
import json

# Add backend directory to path so we can import tp_get from the correct location
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))
from scripts.tga.tp_get import parse_elements_and_pcs

def main():
    # Base path to XML files
    xml_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'tgaWebServiceKit-2021-12-01',
        'xml'
    )
    
    # List all unit XML files
    unit_files = [f for f in os.listdir(xml_dir) if f.startswith('Unit_') and f.endswith('.xml')]
    print(f"Found {len(unit_files)} unit XML files")
    
    # Process each file
    for filename in unit_files:
        unit_code = filename.split('_')[1]
        print(f"\nProcessing {unit_code} from {filename}...")
        
        # Read XML content
        with open(os.path.join(xml_dir, filename), 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        # Parse elements
        elements = parse_elements_and_pcs(xml_content)
        
        if not elements:
            print(f"  No elements found in {filename}")
            continue
        
        # Print summary
        print(f"  Found {len(elements)} elements")
        for element in elements:
            pc_count = len(element.get('performance_criteria', []))
            print(f"  Element {element.get('element_num', 'N/A')}: "
                  f"{element.get('element_text', 'No text')} "
                  f"({pc_count} PCs)")
        
        # Write to JSON file for inspection
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{unit_code}_elements.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(elements, f, indent=2)
        
        print(f"  Saved elements to {output_file}")

if __name__ == "__main__":
    main()
