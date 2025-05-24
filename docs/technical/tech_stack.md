# Technology Stack Guide

This guide explains the LearnOnline.cc technology stack for developers who may be new to these technologies.

## Overview Architecture

LearnOnline.cc uses a lightweight three-tier architecture:

1. **Frontend**: HTML5 + jQuery + Bootstrap static application
2. **Backend**: FastAPI REST API
3. **Database**: PostgreSQL relational database

All components are containerized using Docker for consistent development and deployment environments. The frontend is served by Nginx and communicates with the backend via AJAX calls.

## Frontend Technologies Explained

### Vue.js 3

Vue.js is a progressive JavaScript framework used to build user interfaces. The project uses Vue.js 3 with the Composition API.

**Key concepts for new developers:**
- **Components**: Reusable UI elements with their own templates, logic, and styling
- **Props**: Data passed from parent to child components
- **Emits**: Events sent from child to parent components
- **Reactive data**: Vue's reactivity system automatically updates the UI when data changes

**Main files and directories:**
- `/frontend/src/main.js`: Application entry point
- `/frontend/src/App.vue`: Root component
- `/frontend/src/components/`: Reusable UI components
- `/frontend/src/views/`: Page components
- `/frontend/src/router/`: Navigation configuration
- `/frontend/src/store/`: Vuex state management

### Element Plus

Element Plus is a Vue 3 UI library that provides pre-built components following a consistent design system.

**Usage:**
```javascript
// Element Plus components are imported and registered in main.js
import { ElButton, ElForm } from 'element-plus'
```

### Vuex

Vuex is Vue's centralized state management library, similar to Redux for React.

**Key concepts:**
- **State**: Central data store
- **Getters**: Computed properties for the store
- **Mutations**: Synchronous functions that modify state
- **Actions**: Asynchronous operations that commit mutations

## Backend Technologies Explained

### FastAPI

FastAPI is a modern, high-performance Python web framework for building APIs. It's based on standard Python type hints.

**Key concepts for new developers:**
- **Path Operations**: Functions that handle HTTP requests (GET, POST, etc.)
- **Pydantic Models**: Define data validation, conversion, and documentation
- **Dependency Injection**: Manage shared logic between endpoints
- **Automatic Documentation**: OpenAPI/Swagger docs at `/docs` endpoint

**Main files and directories:**
- `/backend/main.py`: Application entry point
- `/backend/routers/`: API route definitions
- `/backend/models/`: Database models
- `/backend/schemas/`: Pydantic models for request/response validation
- `/backend/services/`: Business logic

### PostgreSQL

PostgreSQL is an advanced, open-source relational database.

**Key concepts:**
- **Tables**: Structured data storage
- **Relationships**: Connections between data (foreign keys)
- **Transactions**: Atomic operations for data consistency
- **pgcrypto extension**: Used for password hashing and security

## Data Flow

Understanding the flow of data through the application:

1. **User interaction** triggers an event in a Vue component
2. Component calls a **Vuex action**
3. Action makes an **HTTP request** to the backend API using Axios
4. FastAPI **endpoint** receives and validates the request
5. Backend processes the request, interacts with the **database**
6. FastAPI returns a **response**
7. Vuex action receives the response and **updates the state**
8. Vue components **reactively update** to reflect the new state

## Authentication Flow

The application uses JWT (JSON Web Token) authentication:

1. User submits login credentials
2. Backend validates credentials and issues a JWT
3. Token is stored in the browser (localStorage)
4. Subsequent API requests include the token in Authorization header
5. Backend validates token for protected endpoints

## Development Workflow

1. Make changes to Vue components or FastAPI routes
2. Docker's development setup automatically reloads changes
3. Test changes in the browser or API client
4. If tests pass, commit changes to version control

## API Communication

Frontend and backend communicate via REST API:
- Standard HTTP methods (GET, POST, PUT, DELETE)
- JSON request and response bodies
- JWT authentication using Authorization headers

Example API request from Vue/Axios:
```javascript
// Frontend API call
import axios from 'axios'

const response = await axios.get('/api/courses', {
  headers: { Authorization: `Bearer ${token}` }
})
const courses = response.data
```

Corresponding backend endpoint:
```python
# Backend API endpoint
from fastapi import APIRouter, Depends
from typing import List

router = APIRouter()

@router.get("/api/courses", response_model=List[CourseSchema])
async def get_courses(current_user = Depends(get_current_user)):
    courses = await course_service.get_all_courses()
    return courses
```

## Recommended Learning Resources

If you're new to these technologies, here are some resources to get started:

- **Vue.js**: [Vue.js Documentation](https://vuejs.org/guide/introduction.html)
- **FastAPI**: [FastAPI Documentation](https://fastapi.tiangolo.com/)
- **PostgreSQL**: [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- **Docker**: [Docker Documentation](https://docs.docker.com/)
