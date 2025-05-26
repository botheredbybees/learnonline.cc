#!/bin/bash
# Apply the user level system database updates

echo "Applying user level system database updates..."

# Source the environment variables for database connection
if [ -f .env ]; then
    source .env
else
    echo "Error: .env file not found"
    exit 1
fi

# Apply the schema updates
echo "Adding user_level type and experience_points to users table..."
psql -U ${DB_USER} -d ${DB_NAME} -h ${DB_HOST:-localhost} -p ${DB_PORT:-5332} -f schema_updates/update_user_levels.sql

echo "Creating user activity logs table..."
psql -U ${DB_USER} -d ${DB_NAME} -h ${DB_HOST:-localhost} -p ${DB_PORT:-5332} -f schema_updates/create_activity_logs.sql

echo "Database updates completed successfully!"
