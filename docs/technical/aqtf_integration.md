# AQTF Data Integration Technical Specifications

## SOAP API Integration

### API Endpoints

- **Training Component Service**: `https://ws.sandbox.training.gov.au/Deewr.Tga.Webservices/TrainingComponentServiceV12.svc`
- **Authentication**: Basic Auth
- **WSDL Version**: 12.2

### Data Types

- Training Packages
- Qualifications
- Units of Competency
- Skill Sets
- Assessment Requirements

### API Operations

1. **Search**

   - Filter by component type
   - Pagination support
   - Include/exclude deleted/superseded

2. **Get Details**

   - Full component information
   - Related components
   - Version history

3. **Get Changes**

   - Delta updates
   - Change tracking
   - Version comparison

## XML Data Processing

### Schema Validation

- XSD validation
- Data type checking
- Required field validation

### Data Transformation

- XML to JSON conversion
- Data normalization
- Relationship mapping

### Error Handling

- Validation errors
- API errors
- Network errors
- Retry mechanism

## Database Synchronization

### Tables

```sql
CREATE TABLE training_packages (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    status VARCHAR(50),
    release_date TIMESTAMP WITH TIME ZONE,
    xml_file VARCHAR(255),
    processed CHAR(1) DEFAULT 'N',
    visible BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE qualifications (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    training_package_id INTEGER REFERENCES training_packages(id),
    title TEXT NOT NULL,
    description TEXT,
    modification_history TEXT,
    pathways_information TEXT,
    licensing_information TEXT,
    entry_requirements TEXT,
    employability_skills TEXT,
    packaging_rules TEXT,
    unit_grid TEXT,
    release_date TIMESTAMP WITH TIME ZONE,
    xml_file VARCHAR(255),
    processed CHAR(1) DEFAULT 'N',
    visible BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE units (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    training_package_id INTEGER REFERENCES training_packages(id),
    title TEXT NOT NULL,
    description TEXT,
    status VARCHAR(50),
    release_date TIMESTAMP WITH TIME ZONE,
    xml_file VARCHAR(255),
    assessment_requirements_file VARCHAR(255),
    unit_descriptor TEXT,
    unit_application TEXT,
    licensing_information TEXT,
    unit_prerequisites TEXT,
    employability_skills TEXT,
    unit_elements TEXT,
    unit_required_skills TEXT,
    unit_evidence TEXT,
    unit_range TEXT,
    unit_sectors TEXT,
    unit_competency_field TEXT,
    unit_corequisites TEXT,
    unit_foundation_skills TEXT,
    performance_evidence TEXT,
    knowledge_evidence TEXT,
    assessment_conditions TEXT,
    nominal_hours INTEGER,
    difficulty_level INTEGER DEFAULT 1,
    experience_points INTEGER DEFAULT 100,
    processed CHAR(1) DEFAULT 'N',
    visible BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE skillsets (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    training_package_id INTEGER REFERENCES training_packages(id),
    title TEXT NOT NULL,
    description TEXT,
    modification_history TEXT,
    pathways_information TEXT,
    licensing_information TEXT,
    entry_requirements TEXT,
    target_group TEXT,
    statement_of_attainment TEXT,
    unit_grid TEXT,
    release_date TIMESTAMP WITH TIME ZONE,
    xml_file VARCHAR(255),
    processed CHAR(1) DEFAULT 'N',
    visible BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Synchronization Process

1. **Initial Load**

   - Full data import
   - Relationship establishment
   - Index creation

2. **Incremental Updates**

   - Change detection
   - Delta application
   - Conflict resolution

3. **Data Validation**

   - Referential integrity
   - Data consistency
   - Business rules

### Performance Optimization

- Batch processing
- Parallel processing
- Index optimization
- Query optimization

## Monitoring and Logging

### Metrics

- API response times
- Data processing times
- Error rates
- Sync status

### Logging

- API requests/responses
- Data transformations
- Error details
- Performance metrics

### Alerts

- API failures
- Sync failures
- Data inconsistencies
- Performance issues 