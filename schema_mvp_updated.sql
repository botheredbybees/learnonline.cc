-- LearnOnline.cc MVP Schema
-- Consolidated schema with all updates (user levels, activities, quests, favorites)

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create user level enum type
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_level') THEN
        CREATE TYPE user_level AS ENUM ('guest', 'player', 'mentor');
    END IF;
END
$$;

-- Users and Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_admin BOOLEAN DEFAULT FALSE,
    experience_points INTEGER DEFAULT 0,
    level user_level DEFAULT 'guest',
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    disabled BOOLEAN DEFAULT FALSE
);

-- Create a function to automatically update user level based on experience points
CREATE OR REPLACE FUNCTION update_user_level()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.experience_points >= 1001 THEN
        NEW.level = 'mentor';
    ELSIF NEW.experience_points >= 101 THEN
        NEW.level = 'player';
    ELSE
        NEW.level = 'guest';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create a trigger to update level when experience points change
DROP TRIGGER IF EXISTS update_user_level_trigger ON users;
CREATE TRIGGER update_user_level_trigger
BEFORE INSERT OR UPDATE OF experience_points ON users
FOR EACH ROW
EXECUTE FUNCTION update_user_level();

-- Create user activity logs table to track experience points and activities
CREATE TABLE user_activity_logs (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL,
    points INTEGER DEFAULT 0,
    reason TEXT,
    admin_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Training Package table
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
    xml_file TEXT,
    assessment_requirements_file TEXT,
    elements_json JSONB, -- JSON representation of elements and PCs for quick access
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Unit Elements table
CREATE TABLE unit_elements (
    id SERIAL PRIMARY KEY,
    unit_id INTEGER REFERENCES units(id) ON DELETE CASCADE,
    element_num VARCHAR(20),
    element_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Unit Performance Criteria table
CREATE TABLE unit_performance_criteria (
    id SERIAL PRIMARY KEY,
    element_id INTEGER REFERENCES unit_elements(id) ON DELETE CASCADE,
    unit_id INTEGER REFERENCES units(id) ON DELETE CASCADE, -- For faster queries
    pc_num VARCHAR(20),
    pc_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Foundation skills table
CREATE TABLE foundation_skills (
    id SERIAL PRIMARY KEY,
    unit_id INTEGER REFERENCES units(id) ON DELETE CASCADE,
    skill_type VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Assessment conditions table
CREATE TABLE assessment_conditions (
    id SERIAL PRIMARY KEY,
    unit_id INTEGER REFERENCES units(id) ON DELETE CASCADE,
    condition_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Qualifications table
CREATE TABLE qualifications (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    level VARCHAR(10),
    status VARCHAR(50),
    release_date DATE,
    xml_file TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Skillsets table
CREATE TABLE skillsets (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50),
    xml_file TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Admin tasks tracking table
CREATE TABLE admin_tasks (
    id SERIAL PRIMARY KEY,
    task_name VARCHAR(100) NOT NULL,
    task_description TEXT,
    last_run_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Quests table - Defines structured sets of units (either created by mentors or based on qualifications/skillsets)
CREATE TABLE quests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    creator_id UUID REFERENCES users(id),
    is_public BOOLEAN DEFAULT false,
    is_introductory BOOLEAN DEFAULT false, -- Flag for quests accessible to guests without accounts
    quest_type VARCHAR(50) NOT NULL CHECK (quest_type IN ('mentor_created', 'qualification_based', 'skillset_based', 'introductory')),
    source_id VARCHAR(50), -- Reference to qualification_id or skillset_id if based on them
    experience_points INTEGER DEFAULT 100, -- Points awarded for completing the quest
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Quest Units - Linking table between quests and units
CREATE TABLE quest_units (
    quest_id UUID REFERENCES quests(id) ON DELETE CASCADE,
    unit_id INTEGER REFERENCES units(id) ON DELETE CASCADE,
    sequence_number INTEGER NOT NULL, -- For ordering units within the quest
    is_required BOOLEAN DEFAULT true, -- Some units may be optional within a quest
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (quest_id, unit_id)
);

-- User Favorite Training Packages
CREATE TABLE user_favorite_training_packages (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    training_package_id INTEGER REFERENCES training_packages(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, training_package_id)
);

-- User Favorite Units
CREATE TABLE user_favorite_units (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    unit_id INTEGER REFERENCES units(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, unit_id)
);

-- User Favorite Quests
CREATE TABLE user_favorite_quests (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    quest_id UUID REFERENCES quests(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, quest_id)
);

-- Guest Progress table - For temporarily storing guest progress before account creation
CREATE TABLE guest_progress (
    guest_id VARCHAR(100) PRIMARY KEY, -- Unique identifier from cookie
    quest_id UUID REFERENCES quests(id) ON DELETE CASCADE,
    unit_progress JSONB NOT NULL, -- Stores progress on units as JSON
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(50),
    user_agent TEXT
);

-- User Quest Progress table - For tracking user progress on quests
CREATE TABLE user_quest_progress (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    quest_id UUID REFERENCES quests(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'in_progress' CHECK (status IN ('not_started', 'in_progress', 'completed')),
    progress_data JSONB DEFAULT '{}', -- Detailed progress data as JSON
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, quest_id)
);

-- Utility function to update updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Define triggers for updating timestamps
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
    
CREATE TRIGGER update_unit_elements_updated_at
    BEFORE UPDATE ON unit_elements
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_unit_performance_criteria_updated_at
    BEFORE UPDATE ON unit_performance_criteria
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_foundation_skills_updated_at
    BEFORE UPDATE ON foundation_skills
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_assessment_conditions_updated_at
    BEFORE UPDATE ON assessment_conditions
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

CREATE TRIGGER update_quests_updated_at
    BEFORE UPDATE ON quests
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_quest_progress_updated_at
    BEFORE UPDATE ON user_quest_progress
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create indexes for better query performance
CREATE INDEX idx_users_experience_points ON users(experience_points);
CREATE INDEX idx_users_level ON users(level);
CREATE INDEX idx_user_activity_logs_user_id ON user_activity_logs(user_id);
CREATE INDEX idx_user_activity_logs_activity_type ON user_activity_logs(activity_type);
CREATE INDEX idx_user_activity_logs_created_at ON user_activity_logs(created_at);
CREATE INDEX idx_quests_creator_id ON quests(creator_id);
CREATE INDEX idx_quests_quest_type ON quests(quest_type);
CREATE INDEX idx_quests_is_public ON quests(is_public);
CREATE INDEX idx_quests_is_introductory ON quests(is_introductory);
CREATE INDEX idx_quest_units_unit_id ON quest_units(unit_id);
CREATE INDEX idx_guest_progress_quest_id ON guest_progress(quest_id);
CREATE INDEX idx_user_quest_progress_quest_id ON user_quest_progress(quest_id);
