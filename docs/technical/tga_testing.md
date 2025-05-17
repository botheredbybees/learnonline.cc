# TGA XML Testing Environment

This document describes how to set up and use the testing environment for TGA XML processing.

## Prerequisites

Before you begin testing the TGA XML processing functionality, ensure you have:

1. A working installation of LearnOnline.cc backend
2. Python 3.9 or higher
3. PostgreSQL database with the correct schema
4. TGA XML files (provided in tgaWebServiceKit-2021-12-01/xml directory)
5. Environment variables configured (.env file)

## Setting Up the Test Environment

### 1. Install Required Packages

Make sure all required Python packages are installed:

```bash
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory with the following variables:

```
DB_NAME=learnonline
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

### 3. Configure Database

Make sure your database has the correct schema. Run the schema.sql script if needed:

```bash
psql -U your_db_user -d learnonline -f schema.sql
```

## Running Tests

### Unit Tests

Run the unit tests to verify the XML parsing functionality:

```bash
cd /path/to/learnonline.cc
python -m unittest backend/tests/test_unit_xml_parser.py
```

### Manual Testing

You can manually test the XML parsing functionality using the provided utility scripts:

1. **Parse a specific unit XML file**:
   ```bash
   python backend/scripts/tga_utils.py parse --unit PUAAMS101
   ```

2. **Parse all XML files**:
   ```bash
   python backend/scripts/tga_utils.py parse --all --output output
   ```

3. **Store unit elements in the database**:
   ```bash
   python backend/scripts/tga_utils.py store --unit PUAAMS101 --create-unit
   ```

4. **Process all local XML files** (imports into database):
   ```bash
   python backend/scripts/tga_utils.py process-local
   ```

### Example Scripts

Several example scripts are provided to demonstrate how to use the TGA XML processing functionality:

1. **Parse XML Example** - Demonstrates parsing XML files:
   ```bash
   python backend/scripts/examples/parse_xml_example.py
   ```

2. **Database Example** - Demonstrates querying units and elements from the database:
   ```bash
   python backend/scripts/examples/database_example.py
   ```

3. **TGA Utils Example** - Interactive tutorial for using the tga_utils.py tool:
   ```bash
   backend/scripts/examples/tga_utils_example.sh
   ```

## Test Data

Test XML files are located in the `tgaWebServiceKit-2021-12-01/xml` directory. These files include:

- Unit XML files (e.g., `Unit_PUAAMS101_R1.xml`)
- Assessment Requirements XML files (e.g., `PUAAMS101_AssessmentRequirements_R1.xml`)
- Qualification XML files (e.g., `Qualification_PUA21622_R1.xml`)

## Using the Admin Interface

You can also test the XML processing functionality through the Admin interface:

1. Log in as an administrator
2. Navigate to the Admin page
3. Use the "Process Unit Elements" section to process specific units or all units

## Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Verify your database credentials in the .env file
   - Make sure the PostgreSQL server is running
   - Check that the database exists and has the correct schema

2. **XML Parsing Error**:
   - Verify that the XML files are in the correct format
   - Check that the file path is correct
   - Look for specific error messages in the logs

3. **Module Import Error**:
   - Make sure you're running the scripts from the correct directory
   - Verify that all required packages are installed

### Getting Help

If you encounter issues, you can:

1. Check the logs for error messages
2. Run tests with increased verbosity: `python -m unittest -v backend/tests/test_unit_xml_parser.py`
3. Contact the development team for assistance
