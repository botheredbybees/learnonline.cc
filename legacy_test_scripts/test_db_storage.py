#!/usr/bin/env python3
import unittest
import os
import json
import sys
from unittest.mock import MagicMock, patch
from tp_get import parse_elements_and_pcs, store_elements_and_pcs

class MockCursor:
    """Mock database cursor for testing."""
    
    def __init__(self):
        self.executed_queries = []
        self.query_params = []
    
    def execute(self, query, params):
        """Mock execute method."""
        self.executed_queries.append(query)
        self.query_params.append(params)
    
    def fetchone(self):
        """Mock fetchone method."""
        return [1]  # Return element ID 1

class TestDatabaseStorage(unittest.TestCase):
    """Test database storage functions for elements and PCs."""
    
    def setUp(self):
        """Setup test environment."""
        # Base path to the XML files
        self.xml_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'tgaWebServiceKit-2021-12-01',
            'xml'
        )
        
        # Mock cursor
        self.mock_cursor = MockCursor()
        
        # Sample elements from a unit
        self.sample_elements = [
            {
                'element_num': '1',
                'element_text': 'Prepare for search and rescue operation',
                'performance_criteria': [
                    {
                        'pc_num': '1.1',
                        'pc_text': 'Operation and task information is obtained from relevant personnel'
                    },
                    {
                        'pc_num': '1.2',
                        'pc_text': 'Aircraft search and rescue equipment is selected and checked for serviceability'
                    }
                ]
            },
            {
                'element_num': '2',
                'element_text': 'Conduct search',
                'performance_criteria': [
                    {
                        'pc_num': '2.1',
                        'pc_text': 'Planned search pattern is followed'
                    },
                    {
                        'pc_num': '2.2',
                        'pc_text': 'Search equipment is operated to maximise effectiveness'
                    }
                ]
            }
        ]
    
    def read_xml_file(self, filename):
        """Helper function to read XML file content."""
        file_path = os.path.join(self.xml_dir, filename)
        if not os.path.exists(file_path):
            self.fail(f"Test file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def test_store_elements_and_pcs(self):
        """Test storing elements and PCs in the database."""
        # Call store function with mock cursor
        result = store_elements_and_pcs(self.mock_cursor, 123, self.sample_elements)
        
        # Verify function succeeded
        self.assertTrue(result, "store_elements_and_pcs should return True on success")
        
        # Verify expected queries were executed
        expected_queries = 5  # 2 elements + 2 PCs + 1 JSON update
        self.assertEqual(len(self.mock_cursor.executed_queries), expected_queries,
                        f"Expected {expected_queries} queries, got {len(self.mock_cursor.executed_queries)}")
        
        # Check that element insert queries were executed
        element_inserts = sum(1 for q in self.mock_cursor.executed_queries 
                             if "INSERT INTO unit_elements" in q)
        self.assertEqual(element_inserts, 2, "Should have 2 element insert queries")
        
        # Check that PC insert queries were executed
        pc_inserts = sum(1 for q in self.mock_cursor.executed_queries 
                        if "INSERT INTO unit_performance_criteria" in q)
        self.assertEqual(pc_inserts, 2, "Should have 2 PC insert queries")
        
        # Check that JSON update was executed
        json_updates = sum(1 for q in self.mock_cursor.executed_queries 
                          if "UPDATE units" in q and "elements_json" in q)
        self.assertEqual(json_updates, 1, "Should have 1 JSON update query")
        
        # Print query summary
        print("\nDatabase Queries Summary:")
        for i, query in enumerate(self.mock_cursor.executed_queries):
            query_type = "Unknown"
            if "INSERT INTO unit_elements" in query:
                query_type = "Insert element"
            elif "INSERT INTO unit_performance_criteria" in query:
                query_type = "Insert PC"
            elif "UPDATE units" in query:
                query_type = "Update units JSON"
                
            print(f"  Query {i+1}: {query_type}")
            print(f"    Params: {self.mock_cursor.query_params[i]}")
    
    def test_real_data_storage(self):
        """Test storing elements from real XML files."""
        unit_files = [f for f in os.listdir(self.xml_dir) if f.startswith('Unit_') and f.endswith('.xml')]
        
        print("\nTesting storage of elements from real XML files:")
        for filename in unit_files:
            unit_code = filename.split('_')[1]
            print(f"\n  Processing {unit_code} from {filename}...")
            
            # Parse elements
            xml_content = self.read_xml_file(filename)
            elements = parse_elements_and_pcs(xml_content)
            
            if not elements:
                print(f"  No elements found in {filename}")
                continue
                
            # Create fresh mock cursor for this test
            mock_cursor = MockCursor()
            
            # Store elements
            result = store_elements_and_pcs(mock_cursor, 123, elements)
            
            # Verify function succeeded
            self.assertTrue(result, f"store_elements_and_pcs should return True for {filename}")
            
            # Count queries
            element_inserts = sum(1 for q in mock_cursor.executed_queries 
                                if "INSERT INTO unit_elements" in q)
            pc_inserts = sum(1 for q in mock_cursor.executed_queries 
                            if "INSERT INTO unit_performance_criteria" in q)
            
            print(f"  Stored {element_inserts} elements and {pc_inserts} performance criteria")
            
            # Check at least some queries were executed
            expected_min_queries = len(elements) + 1  # At least one query per element + JSON update
            self.assertGreaterEqual(len(mock_cursor.executed_queries), expected_min_queries,
                                  f"Should execute at least {expected_min_queries} queries for {filename}")

if __name__ == '__main__':
    unittest.main()
