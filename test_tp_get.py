#!/usr/bin/env python3
import unittest
import os
import json
import sys
from tp_get import parse_elements_and_pcs

class TestTPGet(unittest.TestCase):
    """Test cases for tp_get.py XML parsing functionality."""
    
    def setUp(self):
        """Setup test environment."""
        # Base path to the XML files
        self.xml_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'tgaWebServiceKit-2021-12-01',
            'xml'
        )
    
    def read_xml_file(self, filename):
        """Helper function to read XML file content."""
        file_path = os.path.join(self.xml_dir, filename)
        if not os.path.exists(file_path):
            self.fail(f"Test file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def test_parse_elements_puaams101(self):
        """Test parsing elements and PCs from PUAAMS101 unit."""
        xml_content = self.read_xml_file('Unit_PUAAMS101_R1.xml')
        elements = parse_elements_and_pcs(xml_content)
        
        # Verify we got elements
        self.assertIsNotNone(elements, "Should parse elements from XML")
        self.assertTrue(len(elements) > 0, "Should find at least one element")
        
        # Print out the elements for debugging
        print("\nPUAAMS101 Elements:")
        for idx, element in enumerate(elements):
            print(f"Element {idx+1}: {element['element_num']} - {element['element_text']}")
            print(f"  Performance Criteria: {len(element['performance_criteria'])}")
            for pc in element['performance_criteria'][:2]:  # Show first 2 PCs
                print(f"    {pc['pc_num']} {pc['pc_text']}")
            if len(element['performance_criteria']) > 2:
                print(f"    ... and {len(element['performance_criteria'])-2} more")
        
        # Verify structure of elements
        for element in elements:
            self.assertIn('element_num', element)
            self.assertIn('element_text', element)
            self.assertIn('performance_criteria', element)
            self.assertIsInstance(element['performance_criteria'], list)
            
            # If there are PCs, verify their structure
            if element['performance_criteria']:
                for pc in element['performance_criteria']:
                    self.assertIn('pc_num', pc)
                    self.assertIn('pc_text', pc)
    
    def test_parse_elements_puaequ002(self):
        """Test parsing elements and PCs from PUAEQU002 unit."""
        xml_content = self.read_xml_file('Unit_PUAEQU002_R1.xml')
        elements = parse_elements_and_pcs(xml_content)
        
        # Verify we got elements
        self.assertIsNotNone(elements, "Should parse elements from XML")
        self.assertTrue(len(elements) > 0, "Should find at least one element")
        
        # Print out the elements for debugging
        print("\nPUAEQU002 Elements:")
        for idx, element in enumerate(elements):
            print(f"Element {idx+1}: {element['element_num']} - {element['element_text']}")
            print(f"  Performance Criteria: {len(element['performance_criteria'])}")
            for pc in element['performance_criteria'][:2]:  # Show first 2 PCs
                print(f"    {pc['pc_num']} {pc['pc_text']}")
            if len(element['performance_criteria']) > 2:
                print(f"    ... and {len(element['performance_criteria'])-2} more")
    
    def test_against_null_xml(self):
        """Test parsing with null or empty XML."""
        self.assertIsNone(parse_elements_and_pcs(None))
        self.assertIsNone(parse_elements_and_pcs(""))
    
    def test_against_invalid_xml(self):
        """Test parsing with invalid XML."""
        self.assertIsNone(parse_elements_and_pcs("<not>valid<xml>"))
    
if __name__ == '__main__':
    unittest.main()
