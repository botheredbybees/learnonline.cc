# TGA XML Integration Documentation

This document describes the integration with Training.gov.au (TGA) API and XML parsing functionality in the LearnOnline system.

## Overview

The system integrates with Training.gov.au to fetch training packages, qualifications, skillsets, and units of competency. 
For units of competency, the system extracts elements and performance criteria from the provided XML files.

## Components

1. **TGA API Integration** (`/backend/scripts/tga/tp_get.py`): 
   - Connects to Training.gov.au API
   - Fetches and stores training packages and their components
   - Processes XML files to extract elements and performance criteria

2. **Testing Utilities** (`/backend/scripts/tga_utils.py`):
   - Command-line tool for testing XML parsing
   - Supports parsing local XML files
   - Can store parsed elements in the database

3. **XML Testing** (`/backend/tests/test_tga_xml.py`):
   - Tests XML parsing and database storage
   - Can process specific unit codes or all available XML files

4. **Admin Interface** (`/frontend/src/views/Admin.vue`):
   - UI for administrators to trigger TGA synchronization
   - Process elements and performance criteria
   - View task status and results

## Database Schema

The system uses the following tables to store training package data:

- `training_packages`: Training package metadata
- `qualifications`: Qualifications within training packages
- `skillsets`: Skill sets within training packages
- `units`: Units of competency
- `unit_elements`: Elements within units
- `unit_performance_criteria`: Performance criteria for each element
- `admin_tasks`: Background tasks executed by administrators

## XML Parsing Process

The XML parsing process works as follows:

1. XML files are downloaded from TGA or loaded from local directory
2. BeautifulSoup is used to parse the HTML-like structure in the XML files
3. Tables containing elements and performance criteria are identified
4. Elements and their associated performance criteria are extracted
5. Extracted data is stored in the database and also as JSON in the units table

## Usage Instructions

### Admin Interface

1. Navigate to the Admin page
2. Use the "Sync from TGA" button to synchronize training packages
   - Optionally specify particular TP codes
3. Use the "Process Units" section to process elements from XML:
   - Specify a unit code or ID to process a specific unit
   - Enable "Use local XML files" to process from local files instead of TGA API

### Command Line Utilities

For developers, several command-line utilities are available:

#### Process All Units from TGA API

```bash
python backend/scripts/tga/tp_get.py --process-existing
```

#### Process Local XML Files

```bash
python backend/scripts/tga/tp_get.py --process-local
```

#### Parse Specific Unit XML

```bash
python backend/scripts/tga_utils.py parse --unit PUAAMS101
```

#### Store Unit Elements in Database

```bash
python backend/scripts/tga_utils.py store --unit PUAAMS101 --create-unit
```

#### Process All Local XML Files

```bash
python backend/scripts/tga_utils.py process-local
```

## Troubleshooting

### XML Parsing Issues

If XML parsing fails or extracts incorrect elements:

1. Check the XML file structure with the TGA XML viewer
2. Run the test_tga_xml.py script with the specific unit code
3. Review the XML format in the TGA documentation

### TGA API Connectivity Issues

If unable to connect to TGA API:

1. Check network connectivity
2. Verify API credentials in environment variables
3. Ensure WSDL URL is accessible

### Database Storage Issues

If elements are not being stored correctly:

1. Verify database connection parameters
2. Check that tables exist with correct schema
3. Run with logging level set to DEBUG for more details

## Future Improvements

1. Add support for processing specific training package codes when parsing local XML files
2. Enhance XML parsing for different unit formats
3. Implement batch processing for better efficiency
4. Add support for qualification and skillset XML parsing
