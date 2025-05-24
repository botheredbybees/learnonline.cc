-- Drop existing tables if they exist (in correct order to handle dependencies)
DROP TABLE IF EXISTS role_permissions CASCADE;
DROP TABLE IF EXISTS permissions CASCADE;
DROP TABLE IF EXISTS user_profiles CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS roles CASCADE;
DROP TABLE IF EXISTS unit_elements CASCADE;
DROP TABLE IF EXISTS units CASCADE;
DROP TABLE IF EXISTS training_packages CASCADE;
DROP TABLE IF EXISTS training_components CASCADE;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ...copy all table creation SQL from schema.sql here...
