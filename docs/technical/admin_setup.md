# Administrator Setup Guide

This guide provides instructions for setting up and using the administrative features of LearnOnline.cc.

## Getting Started

The LearnOnline.cc platform includes an administrative interface that allows you to:

1. Synchronize training packages from Training.gov.au (TGA)
2. Process unit elements and performance criteria
3. Manage users and their experience levels
4. Award experience points to users
5. Monitor background tasks

## Creating an Administrator Account

To access administrative features, you need an admin account. Here's how to create one:

### Using Docker:

```bash
# Connect to the database container
docker-compose exec db psql -U ${DB_USER} -d ${DB_NAME}

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

### Without Docker:

```bash
# Connect to the PostgreSQL database
psql -U your_username -d learnonline

# In the PostgreSQL console, run the same INSERT statement as above
```

## Accessing the Admin Interface

1. Log in to the application at http://localhost:8080 (or your deployment URL)
2. Use your admin credentials (username: `admin`, password: `adminpassword`)
3. Navigate to the Admin Dashboard using the menu

## User Management

### Managing User Experience Levels

Users progress through three levels as they gain experience points:
- **Guest Level** (0-100 points): Limited access to content, registration, basic browsing
- **Player Level** (101-1000 points): Full access to content, assessments, community features
- **Mentor Level** (1001+ points): Team management, content creation, assessment creation

To manage users:
1. Navigate to Admin Dashboard > Users tab
2. View all users with their experience points and current level
3. Filter users by level to see all guests, players, or mentors
4. Click "Details" to view detailed user information

### Awarding Experience Points

As an administrator, you can award experience points to users:

1. Find the user in the user list
2. Click "Award Points" for the selected user
3. Enter the number of points to award
4. Add a reason for awarding points (optional)
5. Click "Award Points" to confirm

Points are automatically recorded in the activity log and the user's level is updated based on their new total.

## TGA Integration Features

### Synchronizing Training Packages

1. Navigate to Admin Dashboard > Training Packages tab
2. Enter specific Training Package codes in the input field (optional, comma-separated)
3. Click "Sync from TGA"
4. Monitor the synchronization task in the Tasks tab

### Processing Unit Elements

1. Navigate to Admin Dashboard > Training Packages tab
2. Find the "Process Unit Elements" section
3. You can:
   - Process a specific unit (enter Unit Code or ID)
   - Process all units (leave fields blank)
   - Use local XML files (checkbox)
4. Click "Process Units"
5. Monitor the processing task in the Tasks tab

## Managing Background Tasks

1. Navigate to Admin Dashboard > Tasks tab
2. View all background tasks with their:
   - Status (pending, completed, failed)
   - Creation and completion times
   - Task type
3. Click "View Results" on any task to see detailed execution logs

## Troubleshooting

### Task Failures

If a task fails:

1. Check the task details for error messages
2. Verify TGA credentials in the .env file
3. Ensure XML files are present if using local files
4. Check database connectivity

### Database Issues

For database-related problems:

1. Verify database connection parameters in .env
2. Check PostgreSQL logs
3. Ensure tables are properly created using the schema.sql file

## Advanced Administration

### Command Line Tools

For advanced administration, you can use command-line tools:

```bash
# Process units from TGA API
python backend/scripts/tga/tp_get.py --process-existing

# Process local XML files
python backend/scripts/tga/tp_get.py --process-local

# Parse specific unit XML
python backend/scripts/tga_utils.py parse --unit PUAAMS101

# Store unit elements in database
python backend/scripts/tga_utils.py store --unit PUAAMS101 --create-unit
```

### Database Management

Direct database operations (use with caution):

```bash
# Connect to database
docker-compose exec db psql -U ${DB_USER} -d ${DB_NAME}

# Common useful queries
-- View all training packages
SELECT code, title, status, release_date FROM training_packages;

-- View units with elements
SELECT u.code, u.title, 
  (SELECT COUNT(*) FROM unit_elements WHERE unit_id = u.id) as element_count 
FROM units u;

-- View admin tasks
SELECT id, task_type, status, created_at, completed_at 
FROM admin_tasks 
ORDER BY created_at DESC LIMIT 10;
```

## Updating the System

As an administrator, you may need to update the system to the latest version. Here's a quick guide:

### Using Docker (Recommended)

```bash
# Pull the latest code changes
git pull origin main

# Stop and restart the containers
docker-compose down
docker-compose up -d --build
```

### Database Updates

If there are database schema changes:

```bash
# Apply database schema updates
docker-compose exec db psql -U ${DB_USER} -d ${DB_NAME} -f /app/schema_updates/update_to_latest.sql
```

### Post-Update Tasks

After updating:

1. Verify that all services are running correctly
2. Check for any admin tasks that were interrupted
3. Re-sync training packages if necessary
4. Process any pending unit elements

For detailed update instructions, refer to the [Updating Guide](../../UPDATING.md).

For additional administrative functions and technical details, please refer to the full documentation in the [docs/technical](../technical) directory.
