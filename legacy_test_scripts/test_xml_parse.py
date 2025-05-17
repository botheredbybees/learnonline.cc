#!/usr/bin/env python3
import os
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

# XML file path
xml_path = '/home/peter_sha/sourcecode/learnonline.cc/tgaWebServiceKit-2021-12-01/xml/Unit_PUAAMS101_R1.xml'

print(f"Checking XML file: {xml_path}")
if not os.path.exists(xml_path):
    print(f"ERROR: File not found: {xml_path}")
    exit(1)
    
print(f"File exists, size: {os.path.getsize(xml_path)} bytes")

# Read the file content
with open(xml_path, 'r', encoding='utf-8') as f:
    xml_content = f.read()
    
print(f"Read {len(xml_content)} bytes")
print(f"First 100 characters: {xml_content[:100]}")

# Try parsing with XML ElementTree
print("\nTrying to parse with ElementTree...")
try:
    root = ET.fromstring(xml_content)
    print(f"Parsed XML root element: {root.tag}")
    
    # Look for Elements section
    for elem in root.iter():
        if 'Element' in elem.tag:
            print(f"Found tag: {elem.tag}")
except Exception as e:
    print(f"ElementTree parsing error: {e}")
    
# Try parsing with BeautifulSoup
print("\nTrying to parse with BeautifulSoup...")
try:
    soup = BeautifulSoup(xml_content, 'xml')
    print(f"Created soup object: {type(soup)}")
    
    # Look for Elements section
    elements = soup.find_all('Element')
    print(f"Found {len(elements)} Element tags")
    
    if len(elements) > 0:
        print(f"First Element: {elements[0]}")
except Exception as e:
    print(f"BeautifulSoup parsing error: {e}")
    
print("\nDone.")
