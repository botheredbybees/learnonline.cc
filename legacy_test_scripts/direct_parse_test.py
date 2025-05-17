#!/usr/bin/env python3
"""
Script to directly test parsing XML elements and PCs using Beautiful Soup
"""
import os
import re
from bs4 import BeautifulSoup
import sys
import xml.etree.ElementTree as ET

def main():
    # Base path to XML files
    xml_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'tgaWebServiceKit-2021-12-01',
        'xml'
    )
    
    # List all unit XML files
    unit_files = [f for f in os.listdir(xml_dir) if f.startswith('Unit_') and f.endswith('.xml')]
    print(f"Found {len(unit_files)} unit XML files:")
    for f in unit_files:
        print(f"  {f}")
    
    # Process a specific file
    filename = "Unit_PUAAMS101_R1.xml"
    file_path = os.path.join(xml_dir, filename)
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    print(f"\nProcessing {filename}...")
    
    # Read XML content
    with open(file_path, 'r', encoding='utf-8') as f:
        xml_content = f.read()
    
    print(f"File size: {len(xml_content)} bytes")
    
    # Try parsing with ElementTree
    try:
        root = ET.fromstring(xml_content)
        print(f"Successfully parsed XML with ElementTree")
        # Look for tables in the XML
        print("Looking for table elements...")
        
        # Use XPath to find tables
        namespace = {'ns': 'http://www.authorit.com/xml/authorit'}
        tables = root.findall('.//ns:table', namespace)
        print(f"Found {len(tables)} tables using ElementTree")
        
    except Exception as e:
        print(f"Error parsing with ElementTree: {e}")
    
    # Try parsing with Beautiful Soup
    try:
        print("\nParsing with BeautifulSoup...")
        # soup = BeautifulSoup(xml_content, 'xml')  # Using xml parser
        soup = BeautifulSoup(xml_content, 'lxml')  # Using lxml parser
        print(f"Successfully created soup object: {type(soup)}")
        
        # Find all tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        # Look for elements tables
        for i, table in enumerate(tables):
            rows = table.find_all('tr')
            print(f"\nTable {i+1}: {len(rows)} rows")
            
            # Check first row for headers
            if rows and len(rows) > 1:
                first_row_cells = rows[0].find_all('td')
                if first_row_cells and len(first_row_cells) >= 2:
                    cell1_text = first_row_cells[0].get_text().strip()
                    cell2_text = first_row_cells[1].get_text().strip()
                    print(f"First row headers: '{cell1_text}' | '{cell2_text}'")
                    
                    # If this looks like an elements table
                    if "elements" in cell1_text.lower() or "performance" in cell2_text.lower():
                        print("This looks like an elements and performance criteria table!")
                        
                        # Try to extract elements and PCs
                        elements = []
                        current_element = None
                        
                        for row_idx, row in enumerate(rows):
                            cells = row.find_all('td')
                            if not cells or len(cells) < 2:
                                continue
                                
                            cell_text = cells[0].get_text().strip()
                            
                            # Check if this is an element (single digit or digit with period)
                            if re.match(r'^[1-9][0-9]*\.?$', cell_text) and row_idx > 1:
                                print(f"\nFound Element: {cell_text}")
                                element_text = cells[1].get_text().strip()
                                print(f"Element text: {element_text}")
                                
                                current_element = {
                                    'element_num': cell_text,
                                    'element_text': element_text,
                                    'performance_criteria': []
                                }
                                elements.append(current_element)
                                
                            # Check if this is a PC (digit.digit format)
                            elif current_element and re.match(r'^[1-9][0-9]*\.[1-9][0-9]*$', cell_text):
                                pc_text = cells[1].get_text().strip()
                                print(f"  PC {cell_text}: {pc_text}")
                                
                                current_element['performance_criteria'].append({
                                    'pc_num': cell_text,
                                    'pc_text': pc_text
                                })
                        
                        print(f"\nExtracted {len(elements)} elements")
                        for i, element in enumerate(elements):
                            print(f"Element {i+1}: {element['element_num']} - {element['element_text']}")
                            print(f"  {len(element['performance_criteria'])} performance criteria")
        
    except Exception as e:
        print(f"Error parsing with BeautifulSoup: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
