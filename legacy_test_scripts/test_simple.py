#!/usr/bin/env python3
import os
import sys
from bs4 import BeautifulSoup
import json

# Check if the XML file exists
xml_dir = '/home/peter_sha/sourcecode/learnonline.cc/tgaWebServiceKit-2021-12-01/xml'
xml_file = os.path.join(xml_dir, 'Unit_PUAAMS101_R1.xml')

if not os.path.exists(xml_file):
    print(f"ERROR: XML file does not exist: {xml_file}")
    exit(1)
else:
    print(f"XML file exists: {xml_file}")

# Read the XML file and print the first 200 characters to verify content
with open(xml_file, 'r', encoding='utf-8') as file:
    xml_content = file.read()
    print(f"XML file size: {len(xml_content)} bytes")
    print(f"XML content preview: {xml_content[:200]}...")

# Define a simple function to parse elements and PCs for testing
def parse_elements_test(xml_content):
    """Test function to parse elements from XML."""
    if not xml_content:
        print("No XML content provided")
        return None
        
    try:
        print("Parsing XML with BeautifulSoup...")
        soup = BeautifulSoup(xml_content, 'lxml-xml')
        print(f"Parsed soup object: {type(soup)}")
        
        # Extract elements and PCs
        elements = []
        elements_section = soup.find('Elements')
        
        if elements_section:
            print(f"Found Elements section: {elements_section.name}")
            element_items = elements_section.find_all('Element')
            print(f"Found {len(element_items)} element items")
            
            for element_item in element_items:
                element_num = element_item.get('elementNumber', '')
                element_text = ''
                element_desc = element_item.find('ElementName')
                if element_desc:
                    element_text = element_desc.get_text().strip()
                
                print(f"Processing Element {element_num}: {element_text}")
                
                # Create element object
                element = {
                    'element_num': element_num,
                    'element_text': element_text,
                    'performance_criteria': []
                }
                
                # Find PCs
                pcs_section = element_item.find('PerformanceCriteria')
                if pcs_section:
                    print(f"  Found PerformanceCriteria section")
                    pc_items = pcs_section.find_all('PerformanceCriterion')
                    print(f"  Found {len(pc_items)} performance criteria")
                    
                    for pc_item in pc_items:
                        pc_num = pc_item.get('criterionNumber', '')
                        pc_text = pc_item.get_text().strip()
                        
                        element['performance_criteria'].append({
                            'pc_num': pc_num,
                            'pc_text': pc_text
                        })
                
                elements.append(element)
                
            return elements
        else:
            print("No Elements section found in XML")
            return None
                
    except Exception as e:
        print(f"Error parsing elements and PCs: {e}")
        return None

# Try to parse the XML content
print("\nAttempting to parse elements from XML...")
elements = parse_elements_test(xml_content)

# Print results
if elements:
    print(f"\nSuccessfully parsed {len(elements)} elements.")
    for idx, element in enumerate(elements):
        print(f"\nElement {idx+1}: {element['element_num']} - {element['element_text']}")
        print(f"Performance Criteria: {len(element['performance_criteria'])}")
        for pc_idx, pc in enumerate(element['performance_criteria']):
            print(f"  {pc['pc_num']} {pc['pc_text']}")
else:
    print("Failed to parse elements and PCs from the XML file.")
