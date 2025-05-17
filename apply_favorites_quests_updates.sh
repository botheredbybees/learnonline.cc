#!/bin/bash
# Apply the favorites and quests database updates

echo "Applying favorites and quests database schema updates..."

# Source the environment variables for database connection
if [ -f .env ]; then
    source .env
else
    echo "Error: .env file not found"
    exit 1
fi

# Apply the schema updates
echo "Creating tables for favorites and quests..."
psql -U ${DB_USER} -d ${DB_NAME} -h ${DB_HOST:-localhost} -p ${DB_PORT:-5332} -f schema_updates/favorites_and_quests.sql

echo "Database updates completed successfully!"
