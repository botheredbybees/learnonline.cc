#!/usr/bin/env python3
"""
Parse XML file containing unit elements with 4-column structure
"""
import os
import re
from bs4 import BeautifulSoup

# Define the file path
file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'tgaWebServiceKit-2021-12-01',
    'xml',
    'Unit_PUAAMS101_R1.xml'
)

# Read the XML file
print(f"Reading file: {file_path}")
with open(file_path, 'r', encoding='utf-8') as file:
    xml_content = file.read()
    print(f"File size: {len(xml_content)} bytes")

# Parse with Beautiful Soup
print("\nParsing with BeautifulSoup...")
soup = BeautifulSoup(xml_content, 'lxml')

# Find all tables
tables = soup.find_all('table')
print(f"Found {len(tables)} tables")

# Special parsing for the 4-column structure where elements and PCs are mixed
def process_four_column_table(table):
    rows = table.find_all('tr')
    
    # Skip the first 2 rows (header and description)
    data_rows = rows[2:]
    
    elements = []
    current_element = None
    
    for row in data_rows:
        cells = row.find_all('td')
        
        # This table has a weird structure. We expect at least 2 cells
        if len(cells) < 2:
            continue
        
        # Check for element (1st column)
        col1 = cells[0].get_text().strip()
        if col1 and re.match(r'^[0-9]+$', col1):
            # This is a new element
            element_text = cells[1].get_text().strip()
            print(f"Element {col1}: {element_text}")
            
            current_element = {
                'element_num': col1,
                'element_text': element_text,
                'performance_criteria': []
            }
            elements.append(current_element)
        
        # Always check for performance criteria in 3rd and 4th columns
        if len(cells) >= 4 and current_element is not None:
            pc_num = cells[2].get_text().strip()
            pc_text = cells[3].get_text().strip()
            
            if pc_num and pc_text:
                print(f"  PC {pc_num}: {pc_text}")
                current_element['performance_criteria'].append({
                    'pc_num': pc_num,
                    'pc_text': pc_text
                })
    
    return elements

# Process the elements table
elements = []
for table in tables:
    rows = table.find_all('tr')
    if len(rows) >= 3:
        first_row_cells = rows[0].find_all('td')
        if len(first_row_cells) >= 2:
            header1 = first_row_cells[0].get_text().strip()
            header2 = first_row_cells[1].get_text().strip()
            
            if "Elements" in header1 and "Performance criteria" in header2:
                print(f"\nFound elements table with {len(rows)} rows")
                elements = process_four_column_table(table)
                break

# Print summary
if elements:
    print("\nSUMMARY OF ELEMENTS AND PCS:")
    for i, element in enumerate(elements):
        print(f"Element {i+1}: {element['element_num']} - {element['element_text']}")
        
        if element['performance_criteria']:
            print(f"  Performance Criteria:")
            for pc in element['performance_criteria']:
                print(f"    {pc['pc_num']} - {pc['pc_text']}")
        else:
            print("  No performance criteria found")
else:
    print("No elements found")
