# Schema Updates Notice

## Consolidation of Schema Updates

The individual schema update files in this directory have been consolidated into the main schema file. Instead of applying incremental updates, please use the following consolidated schema file:

- **`/schema_mvp_updated.sql`**: Contains all database tables, including user levels, activity logs, quests, and favorites.

## Migration Scripts

The original update scripts in this directory are retained for reference purposes but should not be used directly for updating the database. The individual files include:

- `update_user_levels.sql`: Adds user level functionality
- `create_activity_logs.sql`: Creates activity tracking tables
- `favorites_and_quests.sql`: Adds tables for quests and user favorites

## How to Apply the Schema

### Using Docker:

```bash
docker-compose exec db psql -U ${DB_USER} -d ${DB_NAME} -f /app/schema_mvp_updated.sql
```

### Without Docker:

```bash
psql -U your_username -d learnonline -f schema_mvp_updated.sql
```

## Development Notes

For the proof of concept phase, we've consolidated all schema changes into a single file to simplify the database setup process. This approach eliminates the need for incremental updates and ensures that all database tables are created with the correct dependencies.
