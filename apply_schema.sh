#!/bin/bash
# Apply the consolidated database schema

# Load environment variables from .env file
if [ -f .env ]; then
  source .env
else
  echo "Error: .env file not found"
  echo "Please create a .env file based on env_example.txt"
  exit 1
fi

echo "Applying consolidated database schema..."

# Check if we're using docker
if [ -n "$(docker ps -q -f name=learnonline.cc_db)" ]; then
  echo "Detected running Docker container, applying schema via Docker..."
  docker-compose exec db psql -U ${DB_USER} -d ${DB_NAME} -f /app/schema_mvp_updated.sql
else
  # Otherwise apply directly using psql
  echo "Applying schema directly using psql..."
  psql -U ${DB_USER} -d ${DB_NAME} -h ${DB_HOST:-localhost} -p ${DB_PORT:-5432} -f schema_mvp_updated.sql
fi

echo "Schema application completed!"
