# Updating LearnOnline.cc

This guide provides instructions for updating an existing installation of LearnOnline.cc to the latest version.

## Before You Begin

Before updating your installation, it's recommended to:

1. Back up your database
2. Back up any customized files
3. Review the release notes for breaking changes

## Update Methods

### Method 1: Using Git (Recommended)

If you installed LearnOnline.cc using Git, you can update it by pulling the latest changes:

```bash
# Navigate to your LearnOnline.cc directory
cd /path/to/learnonline.cc

# Fetch the latest changes
git fetch origin

# Create a backup branch of your current state (optional but recommended)
git branch backup-$(date +%Y%m%d)

# Check out the latest version
git checkout main
git pull origin main

# Update dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..
```

### Method 2: Manual Download

If you downloaded the code manually:

1. Download the latest version from https://github.com/botheredbybees/learnonline.cc/archive/refs/heads/main.zip
2. Extract the files
3. Back up your `.env` file and any customized files
4. Replace the old files with the new ones
5. Restore your `.env` file and any customizations
6. Update dependencies as shown in Method 1

## Database Updates

After updating the code, you need to update your database schema with the consolidated schema file:

```bash
# Using Docker
docker-compose exec db psql -U ${DB_USER} -d ${DB_NAME} -f /app/schema_mvp_updated.sql

# Without Docker
psql -U your_username -d learnonline -f schema_mvp_updated.sql
```

## Updating Docker Containers

If you're using Docker:

```bash
# Stop the current containers
docker-compose down

# Pull the latest images (if using pre-built images)
docker-compose pull

# Rebuild and start the containers
docker-compose up --build -d
```

## Updating Configuration

Check for any new configuration options in the updated `.env.example` file:

```bash
# Compare your .env file with the example
diff -u .env env_example.txt
```

Add any new configuration options to your existing `.env` file.

## TGA XML Files Update

If there are updates to the TGA WebServiceKit:

1. Download the latest kit from https://www.training.gov.au/WebServiceKit
2. Extract to `tgaWebServiceKit-YYYY-MM-DD/` (replace with correct date)
3. Update your `.env` file to point to the new directory if needed

## Verifying the Update

After updating:

1. Check the logs for any errors:
   ```bash
   docker-compose logs -f
   ```

2. Open the application in your browser and verify key functionality:
   - Login and admin access
   - Training package synchronization
   - Unit element processing

## Troubleshooting

### Docker Issues

If containers fail to start:

```bash
# View detailed logs
docker-compose logs -f

# Rebuild from scratch if needed
docker-compose down --volumes
docker-compose up --build
```

### Database Migration Issues

If database updates fail:

1. Check the error messages in the logs
2. Restore from your backup if necessary
3. Apply migrations manually as needed

### Frontend Issues

If the frontend doesn't load or has visual issues:

```bash
# Clear the build cache
cd frontend
npm run clean
npm run build
cd ..

# Restart the frontend container
docker-compose restart frontend
```

## Rolling Back

If you need to roll back to a previous version:

### Using Git

```bash
# List your branches including the backup
git branch

# Checkout the backup branch
git checkout backup-YYYYMMDD

# Restart your services
docker-compose down
docker-compose up -d
```

### Using Database Backup

```bash
# Restore your database from backup
docker-compose exec db psql -U ${DB_USER} -d ${DB_NAME} -f /path/to/backup.sql

# Or without Docker
psql -U your_username -d learnonline -f /path/to/backup.sql
```

## Need Help?

If you encounter issues during the update that aren't covered in this guide:

1. Check the GitHub repository issues page
2. Review the documentation in the `docs/technical` directory
3. Contact the development team for assistance
