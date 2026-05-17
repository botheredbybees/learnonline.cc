# Training Components Integration

This document describes the integration between LearnOnline.cc and the Training.gov.au (TGA) API for managing training components.

## Overview

The training components system provides a seamless integration with TGA's SOAP API to fetch and manage training components (units of competency). The system includes:

- Search functionality for training components
- Caching of component data in the local database
- Automatic retrieval of elements and performance criteria
- Real-time synchronization with TGA

## API Endpoints

### List Training Components

```
GET /api/training-components
```

Returns a paginated list of all training components in the system.

Query Parameters:
- `skip` (optional): Number of items to skip (default: 0)
- `limit` (optional): Maximum number of items to return (default: 100)

### Search Training Components

```
GET /api/training-components/search
```

Search for training components using the TGA API.

Query Parameters:
- `query`: Search text to find components
- `training_package_code` (optional): Filter by training package
- `page` (optional): Page number for pagination (default: 1)
- `page_size` (optional): Items per page (default: 20)

### Get Training Component Details

```
GET /api/training-components/{component_code}
```

Get detailed information about a specific training component. If the component is not in the local database, it will be fetched from TGA and cached.

### Get Training Component Elements

```
GET /api/training-components/{component_code}/elements
```

Get elements and performance criteria for a specific training component. This endpoint will:
1. Check the local database for cached elements
2. If not found or outdated, fetch from TGA and update the cache
3. Return the structured elements data

## Database Schema

The system uses a `training_components` table to store component data:

```sql
CREATE TABLE training_components (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    tga_id VARCHAR(100),
    training_package_code VARCHAR(50),
    release_date DATE,
    elements_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Data Flow

1. Client requests training component data
2. Backend checks local database for cached data
3. If not found or outdated:
   - Fetch from TGA SOAP API
   - Parse and transform data
   - Store in local database
4. Return data to client

## Error Handling

The system handles various error cases:
- TGA API unavailable
- Invalid component codes
- XML parsing errors
- Database connection issues

## Future Improvements

Planned enhancements for the training components system:
- Bulk import functionality
- Automatic synchronization scheduling
- Version tracking
- Change notification system
- Advanced search features

For more information on TGA integration, see the [TGA Integration Documentation](tga_integration.md) and [TGA Testing Documentation](tga_testing.md).
