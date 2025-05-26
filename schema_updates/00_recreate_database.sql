-- Terminate all connections to the database
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'learnonline'
AND pid <> pg_backend_pid();

-- Drop and recreate database
DROP DATABASE IF EXISTS learnonline;
CREATE DATABASE learnonline;
