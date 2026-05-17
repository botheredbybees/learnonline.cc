# API Documentation

## Overview

This document explains how database tables are exposed through the API and documented in the Swagger interface at `http://localhost:8000/docs`. It's intended for developers who understand databases, APIs, and Swagger but may not be familiar with our specific technology stack.

## Technology Stack

The LearnOnline.cc application uses:

- **FastAPI**: A modern Python web framework for building APIs
- **SQLAlchemy**: An SQL toolkit and Object-Relational Mapping (ORM) library
- **Pydantic**: Data validation and settings management using Python type annotations
- **PostgreSQL**: The underlying database
- **Swagger UI**: For API documentation and testing (via OpenAPI)

## How Database Tables Become API Endpoints

### 1. Database Schema to SQLAlchemy Models

The process starts with defining database tables in our schema files (e.g., `schema.sql`). These tables are represented in code as SQLAlchemy models in `models/tables.py`, which map directly to database tables.

Example of a SQLAlchemy model:

```python
class Unit(Base, TimestampMixin):
    __tablename__ = 'units'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text)
    # ... other fields
```

### 2. Pydantic Schemas for Data Validation

Next, we define Pydantic schemas in `models/schemas.py` to validate request/response data and define the shape of the API responses. These schemas may include or exclude certain fields from the underlying database model.

Example of a Pydantic schema:

```python
class UnitSchema(BaseModel):
    id: int
    code: str
    title: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True  # Previously orm_mode=True in older versions
```

### 3. Router Creation

API routes are defined in Python files within the `routers/` directory (e.g., `units.py`, `users.py`). Each router typically corresponds to a resource type and groups related endpoints.

Example of a router setup:

```python
router = APIRouter(
    prefix="/api/units",
    tags=["units"]
)
```

### 4. Endpoint Definition

Inside each router file, we define functions for different operations (GET, POST, PUT, DELETE) that use the SQLAlchemy models to interact with the database and return responses according to the Pydantic schemas.

Example of an endpoint:

```python
@router.get("/{unit_id}", response_model=UnitSchema)
async def get_unit(unit_id: int, db: Session = Depends(get_db)):
    """Get a specific unit by ID"""
    unit = db.query(models.Unit).filter(models.Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit
```

### 5. Registration with Main Application

Finally, all routers are imported and included in the main FastAPI application in `main.py`:

```python
from routers import auth, users, admin, units, quests, favorites, public

app = FastAPI(title="LearnOnline API")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(units.router)
# ... other routers
```

## Swagger UI Integration

FastAPI automatically generates OpenAPI documentation from your code. It uses:

1. Function names and docstrings for operation descriptions
2. Type annotations and Pydantic models for request/response schemas
3. Path parameters and query parameters from function arguments
4. The `tags` parameter in `APIRouter` for organizing endpoints

To access the Swagger UI, visit `http://localhost:8000/docs` when the application is running.

## Step-by-Step Guide to Add a New API Endpoint

1. **Define or update database tables**
   - Add or modify tables in `schema.sql`
   - Apply changes to the database using `apply_schema.sh`

2. **Create or update SQLAlchemy models**
   - Add or modify model classes in `models/tables.py`

3. **Create or update Pydantic schemas**
   - Define request/response schemas in `models/schemas.py`

4. **Create or update router endpoints**
   - Add new endpoints in the appropriate router file
   - Use proper type annotations and docstrings for clear Swagger documentation

5. **Register the router** (if new)
   - Import and include the router in `main.py`

## Common Errors and Solutions

### 1. SQLAlchemy Column Assignment Errors

**Error**: `Cannot assign to attribute "column_name" for class "Model"`

**Solution**: SQLAlchemy columns are descriptor objects, not actual values. Use these approaches:

```python
# Method 1: Use setattr for column assignments
setattr(model_instance, "column_name", value)

# Method 2: Check before assigning
if "field_name" in data and data.get("field_name") is not None:
    model_instance.field_name = data.get("field_name")
```

### 2. Pydantic Validation Errors

**Error**: `ValidationError: Input should be a valid dict or instance of Model`

**Solution**: Ensure your data matches the Pydantic model structure. Common fixes:

```python
# Convert SQLAlchemy model to a dictionary first
model_dict = {c.name: getattr(db_model, c.name) for c in db_model.__table__.columns}
pydantic_model = PydanticModelName(**model_dict)
```

### 3. Database Connection Issues

**Error**: `ConnectionError: Error connecting to the database`

**Solution**:
- Check database credentials in `.env` file
- Ensure database service is running
- Watch for comments in environment variables (like `DB_PORT=5332  # comment`)

### 4. Authentication/Authorization Errors

**Error**: `HTTPException: Not authenticated` or `HTTPException: Not authorized`

**Solution**:
- Check JWT token expiration
- Verify user has the necessary permissions
- Ensure `JWTBearer()` dependency is correctly applied to protected routes

### 5. Missing Router Registration

**Error**: Endpoints not appearing in Swagger UI

**Solution**: Ensure the router is imported and included in the main FastAPI app:

```python
from routers import my_new_router
app.include_router(my_new_router.router)
```

## Debugging Tips

### 1. FastAPI Debug Mode

Run the application in debug mode for detailed error messages:

```bash
uvicorn main:app --reload --debug
```

### 2. Request Inspection

Use the Swagger UI to test endpoints and inspect request/response data.

### 3. SQLAlchemy Logging

Enable SQLAlchemy logging to see SQL queries:

```python
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### 4. Pydantic Validation Debugging

For complex validation issues, inspect the intermediate data:

```python
try:
    model = MyModel(**data)
except ValidationError as e:
    print(f"Validation error: {e}")
    print(f"Input data: {data}")
    raise
```

### 5. Route Testing Script

Create a simple script to test specific modules or routes:

```python
# check_route.py
try:
    from routers import specific_router
    print('Router loaded successfully')
except Exception as e:
    import traceback
    traceback.print_exc()
```

## Best Practices

1. **Keep models and schemas separate** - SQLAlchemy models represent the database structure, while Pydantic schemas represent API request/response shapes

2. **Use descriptive docstrings** - They appear in the Swagger UI documentation

3. **Organize endpoints with tags** - Makes the Swagger UI more navigable

4. **Use appropriate status codes** - Return correct HTTP status codes for different scenarios

5. **Implement proper error handling** - Use try/except blocks and return meaningful error messages

6. **Use dependency injection** - For database sessions, authentication, and other shared resources

7. **Validate input data** - Use Pydantic models to validate all input data

8. **Test API endpoints** - Write tests to ensure your API behaves as expected

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
