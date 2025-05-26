#!/usr/bin/env python3
"""
Parse XML file containing unit elements with multiple columns
This parser specifically looks at the structure of the table cells
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
try:
    with open(file_path, 'r', encoding='utf-8') as file:
        xml_content = file.read()
        print(f"File size: {len(xml_content)} bytes")
except Exception as e:
    print(f"Error reading file: {e}")
    exit(1)

# Parse with Beautiful Soup
print("\nParsing with BeautifulSoup...")
soup = BeautifulSoup(xml_content, 'lxml')

# Find all tables
tables = soup.find_all('table')
print(f"Found {len(tables)} tables")

# Create direct text dump of the elements table to see the structure
def dump_table_text(table):
    print("\n--- TABLE TEXT DUMP ---")
    rows = table.find_all('tr')
    for i, row in enumerate(rows):
        cells = row.find_all('td')
        print(f"Row {i}: {len(cells)} cells")
        for j, cell in enumerate(cells):
            text = cell.get_text().strip()
            print(f"  Cell {j}: '{text}'")

# Extract elements using direct text analysis
def extract_elements_from_table(table):
    rows = table.find_all('tr')
    if len(rows) < 3:  # Need header row, description row, and at least one data row
        return []
        
    # Skip header rows
    data_rows = rows[2:]
    elements = []
    current_element = None
    
    for row in data_rows:
        cells = row.find_all('td')
        
        # Get text from all cells
        cell_texts = [cell.get_text().strip() for cell in cells]
        print(f"Row cells: {cell_texts}")
        
        # Skip empty rows
        if not any(cell_texts):
            continue
            
        # Check for element in first column
        if len(cells) >= 2 and re.match(r'^[1-9][0-9]*$', cell_texts[0]):
            # This looks like an element row
            element_num = cell_texts[0]
            element_text = cell_texts[1] if len(cell_texts) > 1 else ""
            
            print(f"Found Element {element_num}: {element_text}")
            
            current_element = {
                'element_num': element_num,
                'element_text': element_text,
                'performance_criteria': []
            }
            elements.append(current_element)
            
            # Check if this row also has a PC
            if len(cell_texts) >= 4 and re.match(r'^[1-9][0-9]*\.[1-9][0-9]*$', cell_texts[2]):
                pc_num = cell_texts[2]
                pc_text = cell_texts[3] if len(cell_texts) > 3 else ""
                
                print(f"  PC {pc_num}: {pc_text}")
                
                current_element['performance_criteria'].append({
                    'pc_num': pc_num,
                    'pc_text': pc_text
                })
        
        # Check for performance criteria in cells 3 & 4 (if element exists)
        elif current_element and len(cells) >= 4 and re.match(r'^[1-9][0-9]*\.[1-9][0-9]*$', cell_texts[2]):
            pc_num = cell_texts[2]
            pc_text = cell_texts[3]
            
            print(f"  PC {pc_num}: {pc_text}")
            
            current_element['performance_criteria'].append({
                'pc_num': pc_num,
                'pc_text': pc_text
            })
    
    return elements

# Print the first row of each table to identify the elements table
for i, table in enumerate(tables):
    rows = table.find_all('tr')
    if not rows:
        print(f"Table {i+1}: No rows")
        continue
        
    first_row = rows[0]
    cells = first_row.find_all('td')
    cell_texts = [cell.get_text().strip() for cell in cells]
    
    print(f"Table {i+1}: First row: {cell_texts}")
    
    # Check if this looks like the elements table
    if len(cell_texts) >= 2 and "Elements" in cell_texts[0] and "Performance" in cell_texts[1]:
        print(f"Found elements table! Table {i+1}")
        
        # Dump the table structure
        dump_table_text(table)
        
        # Extract elements
        elements = extract_elements_from_table(table)
        
        # Print summary
        print("\nSUMMARY OF ELEMENTS AND PCs:")
        for i, element in enumerate(elements):
            print(f"Element {i+1}: {element['element_num']} - {element['element_text']}")
            print(f"  {len(element['performance_criteria'])} Performance Criteria")
            
            for j, pc in enumerate(element['performance_criteria']):
                print(f"    PC {j+1}: {pc['pc_num']} - {pc['pc_text']}")
