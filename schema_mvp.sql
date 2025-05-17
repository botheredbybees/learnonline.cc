-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users and Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Training Package table (basic version)
CREATE TABLE training_packages (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50),
    release_date DATE,
    last_checked TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Units table
CREATE TABLE units (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    training_package_id INTEGER REFERENCES training_packages(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50),
    release_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Qualifications table
CREATE TABLE qualifications (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    training_package_id INTEGER REFERENCES training_packages(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50),
    release_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Skillsets table
CREATE TABLE skillsets (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    training_package_id INTEGER REFERENCES training_packages(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50),
    release_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Admin tasks table for background jobs
CREATE TABLE admin_tasks (
    id SERIAL PRIMARY KEY,
    task_type VARCHAR(50) NOT NULL,
    created_by UUID REFERENCES users(id),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    params TEXT,
    result TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_training_packages_code ON training_packages(code);
CREATE INDEX idx_training_packages_title ON training_packages(title);

CREATE INDEX idx_units_code ON units(code);
CREATE INDEX idx_units_title ON units(title);
CREATE INDEX idx_units_training_package_id ON units(training_package_id);

CREATE INDEX idx_qualifications_code ON qualifications(code);
CREATE INDEX idx_qualifications_title ON qualifications(title);
CREATE INDEX idx_qualifications_training_package_id ON qualifications(training_package_id);

CREATE INDEX idx_skillsets_code ON skillsets(code);
CREATE INDEX idx_skillsets_title ON skillsets(title);
CREATE INDEX idx_skillsets_training_package_id ON skillsets(training_package_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for all tables
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_training_packages_updated_at
    BEFORE UPDATE ON training_packages
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_units_updated_at
    BEFORE UPDATE ON units
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_qualifications_updated_at
    BEFORE UPDATE ON qualifications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_skillsets_updated_at
    BEFORE UPDATE ON skillsets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_admin_tasks_updated_at
    BEFORE UPDATE ON admin_tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
