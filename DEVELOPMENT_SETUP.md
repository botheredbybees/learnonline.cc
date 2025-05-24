# LearnOnline.cc Development Setup Guide

This guide will walk you through setting up a development environment for LearnOnline.cc on your laptop and running it with administrator privileges.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Git** - For version control
- **Docker and Docker Compose** - For containerization
- **Python 3.9+** - For backend development
- **PostgreSQL** (optional, if not using Docker) - For database
- **Web Browser** with developer tools - For frontend development

## Step 1: Clone the Repository

```bash
git clone https://github.com/botheredbybees/learnonline.cc.git
cd learnonline.cc
```

## Step 2: Set Up Environment Variables

Create a `.env` file in the root directory by copying the example file:

```bash
cp env_example.txt .env
```

Then edit the `.env` file with your specific configurations:

```
# Database connection
DB_NAME=learnonline
DB_USER=your_username
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5332

# JWT Authentication
JWT_SECRET=your_secure_jwt_secret_key_here
JWT_ALGORITHM=HS256
TOKEN_EXPIRE_MINUTES=60

# TGA API Credentials
TGA_USERNAME=WebService.Read
TGA_PASSWORD=Asdf098
```

## Step 3: Download TGA XML Files

The system requires XML files from Training.gov.au for testing and functionality. 

1. Download the TGA WebServiceKit from https://www.training.gov.au/WebServiceKit
2. Extract it to the project root directory as `tgaWebServiceKit-2021-12-01/`

NOTE: If the XML files needed for tests are already included in the repository (excluded from .gitignore), you can skip this step.

## Step 4: Set Up Using Docker (Recommended)

For a consistent development environment, we recommend using Docker:

```bash
# Build and start all services
docker-compose up --build
```

This will start:
- PostgreSQL database
- FastAPI backend server
- Vue.js frontend server
- Other services defined in docker-compose.yml

The application should now be accessible at:
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000/api
- API Documentation: http://localhost:8000/docs

## Step 5: Set Up Without Docker (Alternative)

If you prefer not to use Docker, follow these steps:

### 5.1. Set up the Database

```bash
# Connect to PostgreSQL and create the database
psql -U postgres
CREATE DATABASE learnonline;
\q

# Apply the consolidated database schema
psql -U postgres -d learnonline -f schema_mvp_updated.sql
```

### 5.2. Set up the Backend

```bash
# Navigate to the backend directory
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5.3. Set up the Frontend

In a new terminal:

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run serve
```

## Step 6: Create an Admin Account

To access the admin features, you need to create an admin account:

### Using Docker:

```bash
# Connect to the database container
docker-compose exec db psql -U ${DB_USER} -d ${DB_NAME}

# In the PostgreSQL console, run:
INSERT INTO users (id, email, username, password, full_name, disabled, is_admin, created_at, updated_at)
VALUES (
  gen_random_uuid(),
  'admin@example.com',
  'admin',
  crypt('adminpassword', gen_salt('bf')),
  'Administrator',
  false,
  true,
  CURRENT_TIMESTAMP,
  CURRENT_TIMESTAMP
);
\q
```

### Without Docker:

```bash
# Connect to the PostgreSQL database
psql -U your_username -d learnonline

# In the PostgreSQL console, run:
INSERT INTO users (id, email, username, password_hash, full_name, disabled, is_admin, created_at, updated_at)
VALUES (
  gen_random_uuid(),
  'admin@example.com',
  'admin',
  crypt('adminpassword', gen_salt('bf')),
  'Administrator',
  false,
  true,
  CURRENT_TIMESTAMP,
  CURRENT_TIMESTAMP
);
\q
```

### Rebuilding the Database with Updated Schema:

If you need to rebuild the database with the updated schema:

```bash
# Stop the running containers
docker-compose down

# Start just the database container
docker-compose up -d db

# Connect to the database container
docker-compose exec db bash

# Inside the container, connect to PostgreSQL
psql -U postgres

# Drop the existing database (make sure no connections are active)
DROP DATABASE IF EXISTS ${DB_NAME};

# Create a new empty database
CREATE DATABASE ${DB_NAME};

# Exit psql
\q

# Apply the updated schema
psql -U postgres -d ${DB_NAME} -f /path/to/schema_mvp_updated.sql

# Exit the container
exit

# Restart all services
docker-compose down
docker-compose up -d
```

## Step 7: Log In as Administrator

1. Open your browser and navigate to `http://localhost:8080`
2. Click on the "Login" button
3. Enter the admin credentials:
   - Username: `admin`
   - Password: `adminpassword`
4. Once logged in, you can access the Admin panel from the navigation menu

## Step 8: Admin Tasks

As an administrator, you can:

### 8.1. Synchronize Training Packages

1. Navigate to the Admin page
2. Go to the "Training Packages" tab
3. Enter specific Training Package codes separated by commas (optional)
4. Click "Sync Training Packages"

### 8.2. Process Unit Elements

1. Navigate to the Admin page
2. Go to the "Unit Elements" tab
3. You can:
   - Process all units by leaving fields blank
   - Process a specific unit by entering its ID or code
   - Select "Use local XML files" to process from local files instead of TGA API
4. Click "Process Elements"

### 8.3. View Task Status

1. Navigate to the Admin page
2. Go to the "Tasks" tab
3. View the status and results of background tasks

## Troubleshooting

### Docker Issues

If you encounter problems with Docker containers:

```bash
# Stop and remove all containers and volumes
docker-compose down --volumes

# Rebuild and start
docker-compose up --build
```
### Database Setup Note

The application requires the following PostgreSQL extensions:
- uuid-ossp (for UUID generation)
- pgcrypto (for password hashing)

These extensions are automatically enabled in the Docker setup. If you're using a local PostgreSQL installation, make sure to run:

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

### Database Connection Issues

If the backend can't connect to the database:

1. Check your `.env` file settings
2. Ensure the PostgreSQL server is running
3. Verify the database exists with `psql -l`

### TGA XML Processing Issues

If you encounter issues with XML processing:

1. Ensure the TGA XML files are in the correct directory
2. Check the logs for specific error messages
3. Try running the utility scripts manually:

```bash
# Test XML parsing
python backend/scripts/tga_utils.py parse --unit PUAAMS101

# Process local XML files
python backend/scripts/tga_utils.py process-local
```

### Import Errors in Legacy Scripts

If you need to run legacy test scripts and encounter import errors:

```bash
# Run from project root with Python path set
PYTHONPATH=/path/to/learnonline.cc python legacy_test_scripts/test_tp_get.py
```

## Development Workflow

1. Make your code changes in the appropriate directories
2. Test your changes locally
3. Commit your changes: `git add . && git commit -m "Your descriptive message"`
4. Push to the repository: `git push origin main`

## Additional Resources

- Frontend documentation is in the `/frontend` directory
- Backend API documentation is available at `http://localhost:8000/docs`
- Technical documentation can be found in the `/docs/technical` directory

## Updating Your Development Environment

When new code changes are available in the repository, you can update your development environment:

```bash
# Pull the latest code changes
git pull origin main

# Update dependencies
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..

# Restart containers with the latest code
docker-compose down
docker-compose up --build
```

For more detailed updating instructions, refer to the [Updating Guide](UPDATING.md).

Happy coding with LearnOnline.cc!
