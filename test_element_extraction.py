#!/usr/bin/env python3
import unittest
import os
import json
import sys
from tp_get import parse_elements_and_pcs, download_xml
import xml.etree.ElementTree as ET

class TestElementExtraction(unittest.TestCase):
    """Tests for element and performance criteria extraction from XML files."""
    
    def setUp(self):
        """Setup test environment."""
        # Base path to the XML files
        self.xml_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'tgaWebServiceKit-2021-12-01',
            'xml'
        )
        
        # Dictionary to store parsed elements by unit code
        self.parsed_elements = {}
    
    def read_xml_file(self, filename):
        """Helper function to read XML file content."""
        file_path = os.path.join(self.xml_dir, filename)
        if not os.path.exists(file_path):
            self.fail(f"Test file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def test_extract_elements_from_all_units(self):
        """Extract elements from all unit XML files in the directory."""
        # Find all Unit XML files
        unit_files = [f for f in os.listdir(self.xml_dir) if f.startswith('Unit_') and f.endswith('.xml')]
        
        print(f"\nFound {len(unit_files)} unit XML files:")
        for filename in unit_files:
            unit_code = filename.split('_')[1]  # Extract unit code from filename
            print(f"\nProcessing {unit_code} from {filename}...")
            
            xml_content = self.read_xml_file(filename)
            elements = parse_elements_and_pcs(xml_content)
            
            self.parsed_elements[unit_code] = elements
            
            # Verify we got elements
            self.assertIsNotNone(elements, f"Should parse elements from {filename}")
            self.assertTrue(len(elements) > 0, f"Should find at least one element in {filename}")
            
            # Print summary
            element_count = len(elements)
            pc_count = sum(len(element.get('performance_criteria', [])) for element in elements)
            
            print(f"  Extracted {element_count} elements and {pc_count} performance criteria")
            
            # Print first element details
            if elements and len(elements) > 0:
                first_element = elements[0]
                print(f"  First element: {first_element.get('element_num', 'N/A')} - {first_element.get('element_text', 'N/A')}")
                
                # Print first PC if available
                if first_element.get('performance_criteria', []):
                    first_pc = first_element['performance_criteria'][0]
                    print(f"    First PC: {first_pc.get('pc_num', 'N/A')} - {first_pc.get('pc_text', 'N/A')}")
            
            # Verify structure of elements
            self._validate_element_structure(elements)
    
    def test_xml_structure_analysis(self):
        """Analyze XML structure of unit files to ensure our parser handles different formats."""
        unit_files = [f for f in os.listdir(self.xml_dir) if f.startswith('Unit_') and f.endswith('.xml')]
        
        print("\nXML Structure Analysis:")
        for filename in unit_files:
            xml_content = self.read_xml_file(filename)
            
            # Look for common element containers
            elements_section_exists = '<Elements>' in xml_content or '<UnitElements>' in xml_content
            element_nodes_exist = '<Element ' in xml_content
            performance_criteria_nodes_exist = '<PerformanceCriteria>' in xml_content or '<PerformanceCriterion>' in xml_content
            tables_exist = '<table>' in xml_content.lower() or '<table ' in xml_content.lower()
            
            print(f"\n{filename} structure:")
            print(f"  Elements section: {'Yes' if elements_section_exists else 'No'}")
            print(f"  Element nodes: {'Yes' if element_nodes_exist else 'No'}")
            print(f"  PC nodes: {'Yes' if performance_criteria_nodes_exist else 'No'}")
            print(f"  Tables: {'Yes' if tables_exist else 'No'}")
    
    def test_element_count_consistency(self):
        """Verify that elements are consistently extracted across different formats."""
        # If we haven't parsed elements yet, do it
        if not self.parsed_elements:
            self.test_extract_elements_from_all_units()
            
        print("\nElement count consistency check:")
        for unit_code, elements in self.parsed_elements.items():
            total_pcs = sum(len(element.get('performance_criteria', [])) for element in elements)
            print(f"{unit_code}: {len(elements)} elements, {total_pcs} PCs")
            
            # Each element should have a number and text
            for element in elements:
                self.assertTrue(element.get('element_num'), f"{unit_code}: Element missing number")
                self.assertTrue(element.get('element_text'), f"{unit_code}: Element missing text")
    
    def _validate_element_structure(self, elements):
        """Helper to validate the structure of parsed elements."""
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
    
    def test_db_ready_output(self):
        """Test that the output can be safely stored in the database."""
        # If we haven't parsed elements yet, do it
        if not self.parsed_elements:
            self.test_extract_elements_from_all_units()
        
        print("\nDatabase readiness check:")
        for unit_code, elements in self.parsed_elements.items():
            # Check if elements can be serialized to JSON
            try:
                json_str = json.dumps(elements)
                print(f"{unit_code}: Successfully serialized to JSON ({len(json_str)} bytes)")
            except Exception as e:
                self.fail(f"{unit_code}: Failed to serialize to JSON: {str(e)}")
            
            # Check we can deserialize it back
            try:
                parsed_back = json.loads(json_str)
                self.assertEqual(len(elements), len(parsed_back))
                print(f"{unit_code}: Successfully deserialized from JSON")
            except Exception as e:
                self.fail(f"{unit_code}: Failed to deserialize from JSON: {str(e)}")

if __name__ == '__main__':
    unittest.main()
