#!/usr/bin/env python3
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
    print(f"First 100 chars: {xml_content[:100]}")

# Parse with Beautiful Soup
print("\nParsing with BeautifulSoup...")
soup = BeautifulSoup(xml_content, 'lxml')

# Find all tables
tables = soup.find_all('table')
print(f"Found {len(tables)} tables")

# Find text patterns that might be elements
element_pattern = re.compile(r'^[1-9][0-9]*$')
pc_pattern = re.compile(r'^[1-9][0-9]*\.[1-9][0-9]*$')

# Look through all p tags to find potential elements
print("\nScanning all paragraphs for elements...")
elements_found = []

for p in soup.find_all('p'):
    text = p.get_text().strip()
    if element_pattern.match(text):
        elements_found.append(text)

print(f"Found {len(elements_found)} potential elements: {elements_found}")

# Process each table
for i, table in enumerate(tables):
    print(f"\nTable {i+1}:")
    
    # Get all rows
    rows = table.find_all('tr')
    print(f"  {len(rows)} rows")
    
    # Print first row (headers) if exists
    if len(rows) > 0:
        cells = rows[0].find_all('td')
        if cells and len(cells) >= 2:
            col1 = cells[0].get_text().strip()
            col2 = cells[1].get_text().strip()
            print(f"  Headers: '{col1}' | '{col2}'")
            
            # Look at the first data row
            if len(rows) > 2:  # Skip header and explanation row
                cells = rows[2].find_all('td')
                if cells and len(cells) >= 2:
                    cell1 = cells[0].get_text().strip()
                    cell2 = cells[1].get_text().strip()
                    print(f"  First data: '{cell1}' | '{cell2}'")

print("\nDirect table navigation:")

# Try to directly find the elements table by looking for structure
elements_table = None
for table in tables:
    rows = table.find_all('tr')
    if len(rows) >= 3:  # Need at least header + explanation + one element
        cells = rows[0].find_all('td')
        if len(cells) >= 2:
            # Check if headers look like elements and performance criteria
            header1 = cells[0].get_text().strip().lower()
            header2 = cells[1].get_text().strip().lower()
            
            if 'elements' in header1 or 'performance' in header2:
                elements_table = table
                print(f"Found elements table with {len(rows)} rows")
                break

if elements_table:
    # Skip first two rows (header and explanation)
    rows = elements_table.find_all('tr')[2:]
    
    elements = []
    current_element = None
    
    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 2:
            continue
            
        cell1 = cells[0].get_text().strip()
        cell2 = cells[1].get_text().strip()
        
        if element_pattern.match(cell1):
            print(f"\nElement {cell1}: {cell2}")
            current_element = {'num': cell1, 'text': cell2, 'pcs': []}
            elements.append(current_element)
        elif current_element and pc_pattern.match(cell1):
            print(f"  PC {cell1}: {cell2}")
            current_element['pcs'].append({'num': cell1, 'text': cell2})
    
    print(f"\nExtracted {len(elements)} elements")
    for i, element in enumerate(elements):
        print(f"Element {i+1}: {element['num']} - {element['text']}")
        print(f"  {len(element['pcs'])} performance criteria")

# Check for elements in the XML structure
print("\nLooking for structured elements...")
elements_section = soup.find('Elements')
if elements_section:
    print("Found <Elements> tag")
else:
    print("No <Elements> tag found")
