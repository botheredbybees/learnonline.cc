# TGA API Testing Guide

This document provides comprehensive testing procedures for the Training.gov.au (TGA) API integration in LearnOnline.cc.

## Table of Contents

1. [Overview](#overview)
2. [TGA API Environment Setup](#tga-api-environment-setup)
3. [TGA Client Testing](#tga-client-testing)
4. [XML Processing Testing](#xml-processing-testing)
5. [Data Synchronization Testing](#data-synchronization-testing)
6. [Error Handling Testing](#error-handling-testing)
7. [Performance Testing](#performance-testing)
8. [Integration Testing](#integration-testing)

## Overview

The TGA API integration involves several components:
- **TrainingGovClient**: SOAP client for TGA API communication
- **XML Processing**: Parsing and extracting data from TGA XML files
- **Data Synchronization**: Storing TGA data in local database
- **Error Handling**: Managing API failures and network issues

## TGA API Environment Setup

### Credentials Configuration

```bash
# Set up TGA credentials in environment
export TGA_USERNAME="your_sandbox_username"
export TGA_PASSWORD="your_sandbox_password"

# Or add to .env file
echo "TGA_USERNAME=your_sandbox_username" >> backend/.env
echo "TGA_PASSWORD=your_sandbox_password" >> backend/.env
```

### Test Credentials Verification

```bash
# Test TGA connectivity
curl -u $TGA_USERNAME:$TGA_PASSWORD \
  "https://ws.sandbox.training.gov.au/Deewr.Tga.Webservices/TrainingComponentServiceV12.svc?wsdl"
```

### Environment Variables

```bash
# Required environment variables for testing
TGA_USERNAME=sandbox_username
TGA_PASSWORD=sandbox_password
TGA_WSDL_URL=https://ws.sandbox.training.gov.au/Deewr.Tga.Webservices/TrainingComponentServiceV12.svc?wsdl
TGA_XML_BASE_URL=https://training.gov.au/TrainingComponentFiles/
```

## TGA Client Testing

### Basic Client Functionality

```bash
# Test TGA client initialization
python -c "
from backend.services.tga.client import TrainingGovClient
import os

client = TrainingGovClient(
    username=os.getenv('TGA_USERNAME'),
    password=os.getenv('TGA_PASSWORD')
)
print('TGA Client initialized successfully')
"
```

### Search Components Testing

```python
# tests/test_tga_client.py
import pytest
import os
from backend.services.tga.client import TrainingGovClient
from backend.services.tga.exceptions import TGAClientError

@pytest.fixture
def tga_client():
    return TrainingGovClient(
        username=os.getenv('TGA_USERNAME'),
        password=os.getenv('TGA_PASSWORD')
    )

def test_search_components_basic(tga_client):
    """Test basic component search functionality."""
    result = tga_client.search_components(
        filter_text="ICT",
        page_size=10
    )
    
    assert 'components' in result
    assert isinstance(result['components'], list)
    assert len(result['components']) <= 10

def test_search_components_by_code(tga_client):
    """Test searching for specific component by code."""
    result = tga_client.search_components(
        filter_text="ICTICT214",
        search_code=True,
        page_size=5
    )
    
    assert 'components' in result
    components = result['components']
    
    if components:
        # Verify the component code matches
        found_codes = [comp.Code for comp in components if hasattr(comp, 'Code')]
        assert any('ICTICT214' in code for code in found_codes)

def test_search_components_pagination(tga_client):
    """Test pagination functionality."""
    # Get first page
    page1 = tga_client.search_components(
        filter_text="ICT",
        page=1,
        page_size=5
    )
    
    # Get second page
    page2 = tga_client.search_components(
        filter_text="ICT",
        page=2,
        page_size=5
    )
    
    assert 'components' in page1
    assert 'components' in page2
    
    # Pages should be different (assuming more than 5 ICT components)
    if page1['components'] and page2['components']:
        page1_codes = [comp.Code for comp in page1['components'] if hasattr(comp, 'Code')]
        page2_codes = [comp.Code for comp in page2['components'] if hasattr(comp, 'Code')]
        assert page1_codes != page2_codes

def test_search_components_filter_types(tga_client):
    """Test filtering by component types."""
    result = tga_client.search_components(
        filter_text="ICT",
        component_types={
            'IncludeUnit': True,
            'IncludeQualification': False,
            'IncludeSkillSet': False,
            'IncludeTrainingPackage': False,
            'IncludeAccreditedCourse': False,
            'IncludeAccreditedCourseModule': False,
            'IncludeUnitContextualisation': False
        },
        page_size=10
    )
    
    assert 'components' in result
    components = result['components']
    
    # Verify only units are returned
    if components:
        for comp in components:
            if hasattr(comp, 'ComponentType'):
                assert 'Unit' in comp.ComponentType
```

### Component Details Testing

```python
def test_get_component_details(tga_client):
    """Test retrieving detailed component information."""
    # Use a known unit code
    details = tga_client.get_component_details(
        code="ICTICT214",
        show_files=True,
        show_releases=True
    )
    
    assert details is not None
    
    # Check for expected fields
    if hasattr(details, 'Code'):
        assert details.Code == "ICTICT214"
    
    if hasattr(details, 'Title'):
        assert details.Title is not None
        assert len(details.Title) > 0

def test_get_component_details_invalid_code(tga_client):
    """Test handling of invalid component codes."""
    with pytest.raises(TGAClientError):
        tga_client.get_component_details(code="INVALID_CODE_123")
```

### XML Retrieval Testing

```python
def test_get_component_xml(tga_client):
    """Test XML file retrieval."""
    xml_data = tga_client.get_component_xml(
        code="ICTICT214",
        include_assessment=True
    )
    
    assert 'xml' in xml_data
    assert xml_data['xml'] is not None
    assert len(xml_data['xml']) > 0
    
    # Verify it's valid XML
    from xml.etree import ElementTree as ET
    try:
        ET.fromstring(xml_data['xml'])
    except ET.ParseError:
        pytest.fail("Retrieved XML is not valid")

def test_get_component_xml_assessment(tga_client):
    """Test assessment requirements XML retrieval."""
    xml_data = tga_client.get_component_xml(
        code="ICTICT214",
        include_assessment=True
    )
    
    # Assessment XML may or may not be available
    if 'assessment_xml' in xml_data and xml_data['assessment_xml']:
        from xml.etree import ElementTree as ET
        try:
            ET.fromstring(xml_data['assessment_xml'])
        except ET.ParseError:
            pytest.fail("Retrieved assessment XML is not valid")
```

## XML Processing Testing

### XML Parsing Tests

```python
# tests/test_xml_processing.py
import pytest
from backend.services.tga.client import TrainingGovClient
from bs4 import BeautifulSoup

def test_extract_elements_from_xml():
    """Test extraction of elements and performance criteria from XML."""
    # Sample XML content (you would get this from TGA)
    sample_xml = """
    <div class="element">
        <h4>ELEMENT 1 Operate computer applications</h4>
        <table>
            <tr><td>1.1</td><td>Start up and shut down computer applications</td></tr>
            <tr><td>1.2</td><td>Access and navigate application interface</td></tr>
        </table>
    </div>
    """
    
    client = TrainingGovClient("test", "test")
    elements = client.extract_elements(sample_xml)
    
    assert len(elements) == 1
    element = elements[0]
    
    assert element['number'] == 1
    assert 'Operate computer applications' in element['title']
    assert len(element['performance_criteria']) == 2
    
    pc1 = element['performance_criteria'][0]
    assert pc1['number'] == '1.1'
    assert 'Start up and shut down' in pc1['text']

def test_extract_elements_multiple():
    """Test extraction of multiple elements."""
    sample_xml = """
    <div class="element">
        <h4>ELEMENT 1 First element</h4>
        <table>
            <tr><td>1.1</td><td>First performance criteria</td></tr>
        </table>
    </div>
    <div class="element">
        <h4>ELEMENT 2 Second element</h4>
        <table>
            <tr><td>2.1</td><td>Second performance criteria</td></tr>
            <tr><td>2.2</td><td>Another performance criteria</td></tr>
        </table>
    </div>
    """
    
    client = TrainingGovClient("test", "test")
    elements = client.extract_elements(sample_xml)
    
    assert len(elements) == 2
    assert elements[0]['number'] == 1
    assert elements[1]['number'] == 2
    assert len(elements[1]['performance_criteria']) == 2

def test_extract_elements_malformed_xml():
    """Test handling of malformed XML."""
    malformed_xml = "<div><h4>ELEMENT 1 Test</h4><table><tr><td>1.1</td></tr>"
    
    client = TrainingGovClient("test", "test")
    # Should handle gracefully and return empty list or partial results
    elements = client.extract_elements(malformed_xml)
    assert isinstance(elements, list)
```

## Data Synchronization Testing

### Database Integration Tests

```python
# tests/test_tga_sync.py
import pytest
from sqlalchemy.orm import Session
from backend.models.tables import Unit, Element, PerformanceCriteria
from backend.scripts.tga_utils import sync_unit_from_tga

@pytest.mark.asyncio
async def test_sync_unit_from_tga(test_db: Session):
    """Test synchronizing a unit from TGA to database."""
    unit_code = "ICTICT214"
    
    # Sync unit from TGA
    result = await sync_unit_from_tga(unit_code, test_db)
    
    assert result is not None
    
    # Verify unit was created in database
    unit = test_db.query(Unit).filter(Unit.code == unit_code).first()
    assert unit is not None
    assert unit.code == unit_code
    assert unit.title is not None
    
    # Verify elements were created
    elements = test_db.query(Element).filter(Element.unit_id == unit.id).all()
    assert len(elements) > 0
    
    # Verify performance criteria were created
    for element in elements:
        pcs = test_db.query(PerformanceCriteria).filter(
            PerformanceCriteria.element_id == element.id
        ).all()
        assert len(pcs) > 0

def test_sync_unit_duplicate_handling(test_db: Session):
    """Test handling of duplicate unit synchronization."""
    unit_code = "ICTICT214"
    
    # Create initial unit
    unit1 = Unit(code=unit_code, title="Initial Title")
    test_db.add(unit1)
    test_db.commit()
    
    # Sync same unit again
    result = sync_unit_from_tga(unit_code, test_db)
    
    # Should update existing unit, not create duplicate
    units = test_db.query(Unit).filter(Unit.code == unit_code).all()
    assert len(units) == 1
    
    # Title should be updated from TGA
    updated_unit = units[0]
    assert updated_unit.title != "Initial Title"
```

### Bulk Synchronization Tests

```bash
# Test bulk synchronization script
python backend/scripts/tga/tp_get.py --training-package ICT --limit 5 --test-mode

# Test specific unit synchronization
python backend/scripts/tga_utils.py sync --unit ICTICT214 --verbose

# Test synchronization with error handling
python backend/scripts/tga_utils.py sync --unit INVALID_CODE --verbose
```

## Error Handling Testing

### Network Error Simulation

```python
def test_tga_client_network_error():
    """Test handling of network connectivity issues."""
    # Use invalid URL to simulate network error
    with pytest.raises(TGAConnectionError):
        client = TrainingGovClient(
            username="test",
            password="test",
            wsdl_url="http://invalid-url.example.com/service.wsdl"
        )

def test_tga_client_authentication_error():
    """Test handling of authentication failures."""
    with pytest.raises(TGAAuthenticationError):
        client = TrainingGovClient(
            username="invalid_user",
            password="invalid_password"
        )
        # This should fail when making actual API call
        client.search_components(filter_text="test")

def test_tga_client_timeout_handling():
    """Test handling of API timeouts."""
    # This would require mocking or using a slow endpoint
    # Implementation depends on your mocking strategy
    pass
```

### API Error Response Testing

```python
def test_search_components_empty_results(tga_client):
    """Test handling of searches with no results."""
    result = tga_client.search_components(
        filter_text="NONEXISTENT_COMPONENT_XYZ123",
        page_size=10
    )
    
    assert 'components' in result
    assert result['components'] == [] or result['components'] is None

def test_get_component_details_not_found(tga_client):
    """Test handling of component not found errors."""
    with pytest.raises(TGAClientError):
        tga_client.get_component_details(code="NONEXISTENT123")
```

## Performance Testing

### API Response Time Testing

```python
import time

def test_search_performance(tga_client):
    """Test search API response times."""
    start_time = time.time()
    
    result = tga_client.search_components(
        filter_text="ICT",
        page_size=20
    )
    
    end_time = time.time()
    response_time = end_time - start_time
    
    # API should respond within reasonable time
    assert response_time < 10.0  # 10 seconds max
    assert 'components' in result

def test_xml_retrieval_performance(tga_client):
    """Test XML retrieval performance."""
    start_time = time.time()
    
    xml_data = tga_client.get_component_xml(code="ICTICT214")
    
    end_time = time.time()
    response_time = end_time - start_time
    
    # XML retrieval should be reasonably fast
    assert response_time < 15.0  # 15 seconds max
    assert 'xml' in xml_data
```

### Load Testing

```python
# tests/performance/test_tga_load.py
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

def test_concurrent_searches():
    """Test multiple concurrent TGA searches."""
    def search_worker(search_term):
        client = TrainingGovClient(
            username=os.getenv('TGA_USERNAME'),
            password=os.getenv('TGA_PASSWORD')
        )
        return client.search_components(filter_text=search_term, page_size=5)
    
    search_terms = ["ICT", "BSB", "CHC", "SIT", "AUR"]
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(search_worker, term) for term in search_terms]
        results = [future.result() for future in futures]
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # All searches should complete
    assert len(results) == len(search_terms)
    
    # Should be faster than sequential execution
    assert total_time < 30.0  # Reasonable time for concurrent execution
```

## Integration Testing

### End-to-End TGA Workflow

```python
def test_complete_tga_workflow(test_db):
    """Test complete workflow from TGA search to database storage."""
    # 1. Search for components
    client = TrainingGovClient(
        username=os.getenv('TGA_USERNAME'),
        password=os.getenv('TGA_PASSWORD')
    )
    
    search_result = client.search_components(
        filter_text="ICTICT214",
        page_size=1
    )
    
    assert 'components' in search_result
    assert len(search_result['components']) > 0
    
    # 2. Get component details
    component = search_result['components'][0]
    details = client.get_component_details(component.Code)
    
    assert details is not None
    
    # 3. Get XML content
    xml_data = client.get_component_xml(component.Code)
    
    assert 'xml' in xml_data
    assert xml_data['xml'] is not None
    
    # 4. Extract elements
    elements = client.extract_elements(xml_data['xml'])
    
    assert isinstance(elements, list)
    
    # 5. Store in database (this would be done by sync function)
    unit = Unit(
        code=component.Code,
        title=getattr(component, 'Title', 'Test Title'),
        description=getattr(component, 'Description', 'Test Description')
    )
    test_db.add(unit)
    test_db.commit()
    
    # Verify storage
    stored_unit = test_db.query(Unit).filter(Unit.code == component.Code).first()
    assert stored_unit is not None
```

## Manual Testing Procedures

### TGA API Connectivity Test

```bash
# 1. Test basic connectivity
curl -u $TGA_USERNAME:$TGA_PASSWORD \
  "https://ws.sandbox.training.gov.au/Deewr.Tga.Webservices/TrainingComponentServiceV12.svc?wsdl"

# Expected: WSDL XML content

# 2. Test search functionality
python -c "
from backend.services.tga.client import TrainingGovClient
import os
client = TrainingGovClient(os.getenv('TGA_USERNAME'), os.getenv('TGA_PASSWORD'))
result = client.search_components('ICT', page_size=5)
print(f'Found {len(result[\"components\"])} components')
for comp in result['components'][:3]:
    print(f'- {comp.Code}: {comp.Title}')
"

# 3. Test XML retrieval
python -c "
from backend.services.tga.client import TrainingGovClient
import os
client = TrainingGovClient(os.getenv('TGA_USERNAME'), os.getenv('TGA_PASSWORD'))
xml_data = client.get_component_xml('ICTICT214')
print(f'XML length: {len(xml_data[\"xml\"])} characters')
print('XML starts with:', xml_data['xml'][:100])
"
```

### Database Synchronization Test

```bash
# Test unit synchronization
python backend/scripts/tga_utils.py sync --unit ICTICT214

# Test training package synchronization
python backend/scripts/tga/tp_get.py --training-package ICT --limit 3

# Verify data in database
psql -d learnonline -c "SELECT code, title FROM units WHERE code LIKE 'ICT%' LIMIT 5;"
```

## Troubleshooting Guide

### Common Issues

1. **Authentication Failures**
   ```bash
   # Check credentials
   echo "Username: $TGA_USERNAME"
   echo "Password: [HIDDEN]"
   
   # Test with curl
   curl -u $TGA_USERNAME:$TGA_PASSWORD \
     "https://ws.sandbox.training.gov.au/Deewr.Tga.Webservices/TrainingComponentServiceV12.svc?wsdl"
   ```

2. **Network Connectivity Issues**
   ```bash
   # Test network connectivity
   ping ws.sandbox.training.gov.au
   
   # Test HTTPS connectivity
   curl -I https://ws.sandbox.training.gov.au/
   ```

3. **XML Parsing Errors**
   ```python
   # Debug XML content
   xml_data = client.get_component_xml('ICTICT214')
   print("XML content preview:")
   print(xml_data['xml'][:500])
   
   # Validate XML
   from xml.etree import ElementTree as ET
   try:
       ET.fromstring(xml_data['xml'])
       print("XML is valid")
   except ET.ParseError as e:
       print(f"XML parsing error: {e}")
   ```

4. **Database Connection Issues**
   ```bash
   # Test database connectivity
   psql -d learnonline -c "SELECT 1;"
   
   # Check database schema
   psql -d learnonline -c "\dt"
   ```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run tests with verbose output
pytest tests/test_tga_xml.py -v -s

# Run specific test with debugging
pytest tests/test_tga_xml.py::test_tga_client_search -v -s --tb=long
```

## Test Data

### Known Test Units
- **ICTICT214**: Operate application software packages
- **BSBWHS211**: Contribute to health and safety of self and others
- **CHCCOM005**: Communicate and work in health or community services

### Test Training Packages
- **ICT**: Information and Communications Technology
- **BSB**: Business Services
- **CHC**: Community Services

Use these for consistent testing across different environments.

## Continuous Integration

### CI Pipeline for TGA Testing

```yaml
# .github/workflows/tga-tests.yml
name: TGA Integration Tests

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  tga-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r backend/requirements.txt
        pip install pytest
    
    - name: Run TGA tests
      env:
        TGA_USERNAME: ${{ secrets.TGA_USERNAME }}
        TGA_PASSWORD: ${{ secrets.TGA_PASSWORD }}
      run: |
        cd backend
        pytest tests/test_tga_xml.py -v
```

Remember to store TGA credentials securely in your CI/CD environment and never commit them to version control.
