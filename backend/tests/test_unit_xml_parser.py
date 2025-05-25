#!/usr/bin/env python3
"""
Unit tests for TGA XML parsing and database functionality
"""
import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import json
from pathlib import Path

# Add the parent directory to sys.path to import our modules
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
sys.path.insert(0, ROOT_DIR)

# Import the modules we want to test
from scripts.tga.tp_get import parse_elements_and_pcs, store_elements_and_pcs

class TestElementParsing(unittest.TestCase):
    """Test cases for element and performance criteria parsing"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Path to test XML files
        self.xml_dir = os.path.join(ROOT_DIR, 'tgaWebServiceKit-2021-12-01', 'xml')
        
        # Sample unit codes for testing
        self.unit_codes = ['PUAAMS101']
        
    def test_parse_elements_puaams101(self):
        """Test parsing PUAAMS101 elements and PCs"""
        # Load the XML content
        xml_file = os.path.join(self.xml_dir, 'Unit_PUAAMS101_R1.xml')
        if not os.path.exists(xml_file):
            self.skipTest(f"Test XML file not found: {xml_file}")
            
        with open(xml_file, 'r', encoding='utf-8') as f:
            xml_content = f.read()
            
        # Parse elements and PCs
        elements = parse_elements_and_pcs(xml_content)
        
        # Verify the results
        self.assertIsNotNone(elements, "Elements should not be None")
        self.assertGreater(len(elements), 0, "Should find at least one element")
        
        # Verify the first element
        first_element = elements[0]
        self.assertEqual(first_element['element_num'], '1', "First element number should be '1'")
        self.assertIn("Work effectively as a member of a search and rescue crew", 
                     first_element['element_text'], 
                     "First element text should match expected content")
                     
        # Verify performance criteria
        self.assertGreater(len(first_element['performance_criteria']), 0, 
                         "First element should have performance criteria")
                         
        # Check the content of the first PC
        first_pc = first_element['performance_criteria'][0]
        self.assertEqual(first_pc['pc_num'], '1.1', "First PC number should be '1.1'")
        self.assertIn("Crew functions", first_pc['pc_text'], "First PC text should match expected content")
    
    @unittest.skip("Integration test requires database connection")
    def test_store_elements_mock(self):
        """Test storing elements and PCs with mocked database"""
        # Create mock cursor and connection
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [1]  # Mock element ID return
        
        # Sample elements data
        elements = [
            {
                'element_num': '1',
                'element_text': 'Test element',
                'performance_criteria': [
                    {
                        'pc_num': '1.1',
                        'pc_text': 'Test PC'
                    }
                ]
            }
        ]
        
        # Call the function with mocked cursor
        result = store_elements_and_pcs(mock_cursor, 123, elements)
        
        # Verify the function returned True
        self.assertTrue(result, "Function should return True on success")
        
        # Verify cursor methods were called the expected number of times
        self.assertEqual(mock_cursor.execute.call_count, 5, 
                       "Should execute 5 SQL statements (2 deletes, 1 element insert, 1 PC insert, 1 update)")
        
        # Verify parameters for element insert
        mock_cursor.execute.assert_any_call(unittest.mock.ANY, (123, '1', 'Test element'))
        
        # Verify parameters for PC insert
        mock_cursor.execute.assert_any_call(unittest.mock.ANY, (1, 123, '1.1', 'Test PC'))

if __name__ == '__main__':
    unittest.main()
