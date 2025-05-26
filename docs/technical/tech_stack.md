# Technology Stack

This document outlines the technology stack used in the LearnOnline.cc project.

## Frontend Technologies

### HTML5, CSS3, and JavaScript (ES6+)

The frontend is built using modern web standards with a focus on simplicity, performance, and accessibility.

- **HTML5**: Semantic markup for better accessibility and SEO
- **CSS3**: Modern styling with Flexbox and Grid layouts
- **JavaScript ES6+**: Modern JavaScript features for clean, maintainable code

### jQuery 3.7.1

jQuery is used for DOM manipulation, event handling, and AJAX requests, providing:

- **Cross-browser compatibility**: Consistent behavior across different browsers
- **Simplified DOM manipulation**: Easy element selection and modification
- **AJAX support**: Streamlined API communication
- **Event handling**: Simplified event binding and delegation

```javascript
// Example jQuery usage for API calls
$.ajax({
    url: '/api/units/',
    method: 'GET',
    success: function(data) {
        displayUnits(data.items);
    },
    error: function(xhr, status, error) {
        showErrorMessage('Failed to load units');
    }
});
```

### Bootstrap 5.3.2

Bootstrap provides a responsive, mobile-first CSS framework with:

- **Responsive grid system**: 12-column layout system
- **Pre-built components**: Buttons, forms, modals, navigation
- **Utility classes**: Spacing, colors, typography
- **JavaScript components**: Interactive elements like modals and dropdowns

```html
<!-- Example Bootstrap components -->
<div class="container">
    <div class="row">
        <div class="col-md-6">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Unit Title</h5>
                    <p class="card-text">Unit description...</p>
                </div>
            </div>
        </div>
    </div>
</div>
```

### Font Awesome

Font Awesome provides scalable vector icons for the user interface:

- **Consistent iconography**: Professional icon set
- **Scalable vectors**: Sharp icons at any size
- **Easy integration**: Simple CSS classes

## Backend Technologies

### FastAPI (Python)

FastAPI is a modern, fast web framework for building APIs with Python 3.7+:

- **High performance**: One of the fastest Python frameworks
- **Automatic API documentation**: Interactive docs with Swagger UI
- **Type hints**: Built-in support for Python type hints
- **Async support**: Native async/await support

```python
# Example FastAPI endpoint
@app.get("/api/units/")
async def get_units(
    page: int = 1,
    size: int = 20,
    search: Optional[str] = None
):
    return await unit_service.get_units(page, size, search)
```

### PostgreSQL

PostgreSQL is used as the primary database:

- **ACID compliance**: Reliable transactions
- **Advanced features**: JSON support, full-text search
- **Scalability**: Handles large datasets efficiently
- **Extensibility**: Custom functions and data types

### SQLAlchemy

SQLAlchemy provides the Object-Relational Mapping (ORM):

- **Database abstraction**: Database-agnostic code
- **Relationship mapping**: Easy handling of table relationships
- **Query building**: Pythonic query construction
- **Migration support**: Database schema versioning

```python
# Example SQLAlchemy model
class Unit(Base):
    __tablename__ = "units"
    
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    
    elements = relationship("Element", back_populates="unit")
```

## Development and Deployment

### Docker

Docker is used for containerization and development environment consistency:

- **Development environment**: Consistent setup across machines
- **Production deployment**: Containerized application deployment
- **Service isolation**: Separate containers for different services
- **Scalability**: Easy horizontal scaling

```dockerfile
# Example Dockerfile for backend
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

Docker Compose orchestrates multi-container applications:

- **Service definition**: Define all application services
- **Network configuration**: Inter-service communication
- **Volume management**: Data persistence
- **Environment configuration**: Environment-specific settings

## Testing Technologies

### Pytest

Pytest is used for backend testing:

- **Simple syntax**: Easy-to-write test cases
- **Fixtures**: Reusable test setup
- **Parametrization**: Test multiple scenarios
- **Plugin ecosystem**: Extensive plugin support

### Selenium

Selenium WebDriver is used for frontend testing:

- **Browser automation**: Real browser testing
- **Cross-browser testing**: Multiple browser support
- **User interaction simulation**: Click, type, navigate
- **Screenshot capture**: Visual regression testing

### Locust

Locust is used for performance and load testing:

- **Python-based**: Write tests in Python
- **Distributed testing**: Scale across multiple machines
- **Web UI**: Real-time monitoring
- **Realistic load simulation**: User behavior modeling

## External Integrations

### Training.gov.au SOAP API

Integration with the Australian government's training data:

- **SOAP client**: Python suds-py3 library
- **XML processing**: BeautifulSoup for parsing
- **Data synchronization**: Automated updates
- **Error handling**: Robust error management

### Authentication

JWT (JSON Web Tokens) for authentication:

- **Stateless authentication**: No server-side sessions
- **Secure transmission**: Signed tokens
- **Role-based access**: User permission management
- **Token expiration**: Automatic security timeout

## Development Workflow

### File Structure

```
learnonline.cc/
├── frontend/
│   ├── index.html              # Main HTML file
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css       # Custom styles
│   │   └── js/
│   │       ├── app.js          # Main application logic
│   │       ├── api.js          # API communication
│   │       ├── auth.js         # Authentication handling
│   │       └── units.js        # Units page functionality
│   └── nginx.conf              # Nginx configuration
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── models/                 # Database models
│   ├── routers/                # API route handlers
│   ├── services/               # Business logic
│   └── auth/                   # Authentication logic
└── docker-compose.yml          # Service orchestration
```

### API Communication

The frontend communicates with the backend through RESTful APIs:

```javascript
// Frontend API call example
class APIClient {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
        this.token = localStorage.getItem('access_token');
    }
    
    async get(endpoint) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
}
```

### Development Process

1. **Frontend changes**: Modify HTML, CSS, or JavaScript files
2. **Backend changes**: Update Python code in the backend directory
3. **Database changes**: Create Alembic migrations for schema updates
4. **Testing**: Run automated tests with pytest and Selenium
5. **Docker rebuild**: Rebuild containers when dependencies change

## Performance Considerations

### Frontend Optimization

- **Minification**: CSS and JavaScript minification
- **Caching**: Browser caching for static assets
- **Lazy loading**: Load content as needed
- **Responsive images**: Optimized images for different screen sizes

### Backend Optimization

- **Database indexing**: Optimized database queries
- **Connection pooling**: Efficient database connections
- **Caching**: Redis for frequently accessed data
- **Async processing**: Non-blocking I/O operations

### Monitoring

- **Application metrics**: Response times and error rates
- **Database performance**: Query performance monitoring
- **User analytics**: Usage patterns and behavior
- **Error tracking**: Automated error reporting

## Security

### Frontend Security

- **Input validation**: Client-side validation for user experience
- **XSS prevention**: Proper output encoding
- **CSRF protection**: Token-based CSRF protection
- **Secure communication**: HTTPS for all communications

### Backend Security

- **Input sanitization**: Server-side validation and sanitization
- **SQL injection prevention**: Parameterized queries with SQLAlchemy
- **Authentication**: JWT-based authentication
- **Authorization**: Role-based access control

## Documentation

- **API Documentation**: Automatic Swagger/OpenAPI documentation
- **Code Documentation**: Inline comments and docstrings
- **User Documentation**: User guides and tutorials
- **Technical Documentation**: Architecture and deployment guides

## External Resources

- **jQuery**: [jQuery Documentation](https://api.jquery.com/)
- **Bootstrap**: [Bootstrap Documentation](https://getbootstrap.com/docs/5.3/)
- **FastAPI**: [FastAPI Documentation](https://fastapi.tiangolo.com/)
- **PostgreSQL**: [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- **Docker**: [Docker Documentation](https://docs.docker.com/)
- **Pytest**: [Pytest Documentation](https://docs.pytest.org/)
- **Selenium**: [Selenium Documentation](https://selenium-python.readthedocs.io/)
