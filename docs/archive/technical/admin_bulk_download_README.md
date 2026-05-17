# Admin Bulk Download Feature - Implementation Guide

This document provides a comprehensive guide to the Admin Bulk Download feature implementation for LearnOnline.cc.

## Overview

The Admin Bulk Download feature allows administrators to:
- Download lists of available training packages from TGA
- Select and bulk download training packages
- Download lists of available training units
- Select and bulk download training units
- Monitor download progress and job status
- Automatically populate database tables with downloaded content

## Architecture

### Backend Components

#### 1. Download Manager Service (`backend/services/download_manager.py`)
- Manages asynchronous download jobs
- Tracks job status and progress
- Handles job queuing and execution
- Provides job status reporting

#### 2. Training Packages Router (`backend/routers/training_packages.py`)
- `/api/training-packages/available` - Get available packages from TGA
- `/api/training-packages/bulk-download` - Start bulk download job
- `/api/training-packages/download-status/{job_id}` - Check job status

#### 3. Units Router (`backend/routers/units.py`)
- `/api/units/available` - Get available units from TGA
- `/api/units/bulk-download` - Start bulk download job
- `/api/units/download-status/{job_id}` - Check job status

### Frontend Components

#### 1. Admin Panel (`frontend/admin.html`)
- Tabbed interface for different admin functions
- Bulk download management interface
- Real-time job status monitoring
- Search and filter capabilities

#### 2. API Client (`frontend/js/api.js`)
- JavaScript functions for API communication
- Authentication handling
- Error management

## Database Schema

The feature populates the following tables:

### Core Tables
- `training_packages` - Training package metadata
- `units` - Unit of competency details
- `qualifications` - Qualification information
- `skillsets` - Skill set definitions

### Relationship Tables
- `unit_elements` - Elements within units
- `unit_performance_criteria` - Performance criteria for elements
- `unit_critical_aspects` - Critical aspects of assessment
- `unit_required_skills` - Required skills and knowledge

## API Endpoints

### Training Packages

#### GET `/api/training-packages/available`
Returns list of available training packages from TGA.

**Response:**
```json
{
  "packages": [
    {
      "code": "ICT",
      "title": "Information and Communications Technology",
      "version": "4.0",
      "release_date": "2023-01-01",
      "status": "current"
    }
  ]
}
```

#### POST `/api/training-packages/bulk-download`
Starts bulk download of selected training packages.

**Request:**
```json
["ICT", "BSB", "SIT"]
```

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "started",
  "message": "Bulk download job started"
}
```

#### GET `/api/training-packages/download-status/{job_id}`
Returns status of download job.

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "running",
  "progress": 45,
  "total_items": 100,
  "completed_items": 45,
  "current_item": "ICT30120",
  "started_at": "2023-01-01T10:00:00Z",
  "estimated_completion": "2023-01-01T10:30:00Z"
}
```

### Training Units

#### GET `/api/units/available`
Returns list of available units from TGA.

#### POST `/api/units/bulk-download`
Starts bulk download of selected units.

#### GET `/api/units/download-status/{job_id}`
Returns status of unit download job.

## Frontend Interface

### Admin Panel Layout

The admin panel uses a tabbed interface with three main sections:

1. **Bulk Download** - Main download management interface
2. **Content Management** - Content review and management
3. **System Settings** - System configuration options

### Bulk Download Tab

#### Training Packages Section
- Load available packages button
- Search and filter functionality
- Select all/individual package selection
- Download selected packages button
- Progress indicator

#### Training Units Section
- Load available units button
- Search and filter functionality
- Select all/individual unit selection
- Download selected units button
- Progress indicator

#### Download Jobs Section
- Active jobs list
- Job status monitoring
- Progress bars
- Refresh jobs button

## Testing

### Backend Tests

#### Unit Tests
- `test_download_manager.py` - Download manager functionality
- `test_training_packages_bulk.py` - Training packages API tests
- `test_units_bulk.py` - Units API tests

#### Integration Tests
- End-to-end download workflow tests
- Database population verification
- Error handling scenarios

### Frontend Tests

#### Selenium Tests
- `test_admin_frontend.py` - Admin panel UI tests
- Page load and navigation tests
- Form interaction tests
- Error handling UI tests

### Running Tests

```bash
# Run all bulk download tests
./run_tests.sh bulk-download

# Run individual test suites
./run_tests.sh download-mgr
./run_tests.sh training-pkg
./run_tests.sh units-bulk
./run_tests.sh admin-frontend
```

## Configuration

### Environment Variables

```bash
# TGA API Configuration
TGA_BASE_URL=https://training.gov.au
TGA_USERNAME=your_username
TGA_PASSWORD=your_password

# Download Configuration
MAX_CONCURRENT_DOWNLOADS=5
DOWNLOAD_TIMEOUT=300
RETRY_ATTEMPTS=3
```

### Database Configuration

Ensure the following tables exist in your database:
- All tables defined in `schema.sql`
- Proper indexes for performance
- Foreign key constraints

## Deployment

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Redis (for job queuing)
- Chrome/Chromium (for Selenium tests)

### Installation Steps

1. **Install Dependencies**
   ```bash
   pip install -r backend/requirements.txt
   pip install -r backend/requirements-test.txt
   ```

2. **Database Setup**
   ```bash
   # Run migrations
   alembic upgrade head
   
   # Verify schema
   psql -d learnonline -f schema.sql
   ```

3. **Environment Configuration**
   ```bash
   cp backend/.env.example backend/.env
   # Edit .env with your configuration
   ```

4. **Start Services**
   ```bash
   # Development
   docker-compose up -d
   
   # Production
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Verification

1. **Backend API**
   - Visit `http://localhost:8000/docs`
   - Test authentication endpoints
   - Verify admin endpoints are accessible

2. **Frontend Interface**
   - Visit `http://localhost:8080/admin.html`
   - Login as admin user
   - Test bulk download functionality

3. **Run Test Suite**
   ```bash
   ./run_tests.sh all
   ```

## Usage Guide

### For Administrators

#### Initial Setup
1. Login to the admin panel
2. Navigate to the Bulk Download tab
3. Click "Load Available Packages" to fetch current TGA data
4. Click "Load Available Units" to fetch unit data

#### Downloading Training Packages
1. Use search/filter to find desired packages
2. Select packages individually or use "Select All"
3. Click "Download Selected" to start the job
4. Monitor progress in the Download Jobs section

#### Downloading Training Units
1. Use search/filter to find desired units
2. Select units individually or use "Select All"
3. Click "Download Selected" to start the job
4. Monitor progress in the Download Jobs section

#### Monitoring Downloads
- Jobs appear in the Download Jobs section
- Progress bars show completion status
- Click "Refresh Jobs" to update status
- Completed jobs show success/failure status

### For Developers

#### Adding New Download Types
1. Create new router in `backend/routers/`
2. Add download logic to `download_manager.py`
3. Update frontend interface
4. Add corresponding tests

#### Customizing Download Behavior
- Modify `download_manager.py` for job handling
- Update TGA client in `backend/services/tga/`
- Adjust database models as needed

## Troubleshooting

### Common Issues

#### 1. TGA Authentication Failures
- Verify TGA credentials in environment variables
- Check TGA service status
- Review authentication logs

#### 2. Download Job Failures
- Check Redis connection
- Verify database connectivity
- Review job logs in download manager

#### 3. Frontend Loading Issues
- Verify backend API is running
- Check browser console for JavaScript errors
- Ensure proper authentication

#### 4. Database Population Issues
- Check database schema
