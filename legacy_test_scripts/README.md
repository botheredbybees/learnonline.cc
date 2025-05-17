# Legacy Test Scripts

This directory contains various test scripts that were originally in the root directory of the project. They were moved here to keep the repository organized while preserving them for reference.

These scripts were used during the early development of the TGA integration features and may contain valuable code examples or techniques.

## Scripts

- `direct_parse_test.py` - Tests direct parsing of TGA XML files
- `four_column_parser.py` - Implements a parser for four-column XML tables
- `improved_parser.py` - An improved version of the XML parser
- `simple_parse_test.py` - A simple test for XML parsing
- `test_db_storage.py` - Tests database storage of TGA data
- `test_element_extraction.py` - Tests extraction of elements from XML
- `test_simple.py` - Simple tests for TGA functionality
- `test_tp_get.py` - Tests for the tp_get.py script
- `test_units_xml.py` - Tests for unit XML parsing
- `test_xml_parse.py` - General XML parsing tests

## Usage

These scripts are kept for reference purposes. The functionality they test has been integrated into the proper test framework in the `backend/tests` directory.

**IMPORTANT:** The `tp_get.py` script has been moved to `backend/scripts/tga/tp_get.py`. The imports in these legacy scripts have been updated to reference the new location, but you'll need to run these scripts from the project root directory for the imports to work properly:

```bash
# Run from the project root directory
cd /home/peter_sha/sourcecode/learnonline.cc
python legacy_test_scripts/test_tp_get.py
python legacy_test_scripts/test_units_xml.py
```

If you get import errors, you can manually set the Python path:

```bash
PYTHONPATH=/home/peter_sha/sourcecode/learnonline.cc python legacy_test_scripts/test_tp_get.py
```
