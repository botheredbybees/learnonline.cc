-- Roles and Permissions
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE role_permissions (
    role_id INTEGER REFERENCES roles(id),
    permission_id INTEGER REFERENCES permissions(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (role_id, permission_id)
);

-- Users and Authentication
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role_id INTEGER REFERENCES roles(id),
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User Profiles
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    avatar_url VARCHAR(255),
    bio TEXT,
    experience_points INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Training Package table
CREATE TABLE training_packages (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    status VARCHAR(50),
    release_date TIMESTAMP WITH TIME ZONE,
    xml_file VARCHAR(255),
    processed CHAR(1) DEFAULT 'N',
    visible BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_training_packages_code ON training_packages(code);
CREATE INDEX idx_training_packages_title ON training_packages(title);
CREATE INDEX idx_training_packages_status ON training_packages(status);
CREATE INDEX idx_training_packages_release_date ON training_packages(release_date);

-- Full text search index
CREATE INDEX idx_training_packages_fts ON training_packages USING gin(to_tsvector('english', title || ' ' || description));

-- Units table
CREATE TABLE units (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    training_package_id INTEGER REFERENCES training_packages(id),
    title TEXT NOT NULL,
    description TEXT,
    status VARCHAR(50),
    release_date TIMESTAMP WITH TIME ZONE,
    xml_file VARCHAR(255),
    assessment_requirements_file VARCHAR(255),
    unit_descriptor TEXT,
    unit_application TEXT,
    licensing_information TEXT,
    unit_prerequisites TEXT,
    employability_skills TEXT,
    unit_elements TEXT,
    unit_required_skills TEXT,
    unit_evidence TEXT,
    unit_range TEXT,
    unit_sectors TEXT,
    unit_competency_field TEXT,
    unit_corequisites TEXT,
    unit_foundation_skills TEXT,
    performance_evidence TEXT,
    knowledge_evidence TEXT,
    assessment_conditions TEXT,
    nominal_hours INTEGER,
    difficulty_level INTEGER DEFAULT 1,
    experience_points INTEGER DEFAULT 100,
    processed CHAR(1) DEFAULT 'N',
    visible BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for units
CREATE INDEX idx_units_code ON units(code);
CREATE INDEX idx_units_title ON units(title);
CREATE INDEX idx_units_training_package_id ON units(training_package_id);
CREATE INDEX idx_units_release_date ON units(release_date);
CREATE INDEX idx_units_fts ON units USING gin(to_tsvector('english', title || ' ' || description || ' ' || unit_descriptor || ' ' || unit_application));

-- Unit Elements table
CREATE TABLE unit_elements (
    id SERIAL PRIMARY KEY,
    unit_id INTEGER REFERENCES units(id),
    element_num VARCHAR(50),
    element_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Unit Performance Criteria table
CREATE TABLE unit_performance_criteria (
    id SERIAL PRIMARY KEY,
    element_id INTEGER REFERENCES unit_elements(id),
    unit_id INTEGER REFERENCES units(id),
    pc_num VARCHAR(50),
    pc_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Unit Critical Aspects table
CREATE TABLE unit_critical_aspects (
    id SERIAL PRIMARY KEY,
    unit_id INTEGER REFERENCES units(id),
    section VARCHAR(255),
    critical_aspect TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Unit Required Skills table
CREATE TABLE unit_required_skills (
    id SERIAL PRIMARY KEY,
    unit_id INTEGER REFERENCES units(id),
    skill_type VARCHAR(100),
    skill_section VARCHAR(255),
    skill_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Qualifications table
CREATE TABLE qualifications (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    training_package_id INTEGER REFERENCES training_packages(id),
    title TEXT NOT NULL,
    description TEXT,
    modification_history TEXT,
    pathways_information TEXT,
    licensing_information TEXT,
    entry_requirements TEXT,
    employability_skills TEXT,
    packaging_rules TEXT,
    unit_grid TEXT,
    release_date TIMESTAMP WITH TIME ZONE,
    xml_file VARCHAR(255),
    processed CHAR(1) DEFAULT 'N',
    visible BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for qualifications
CREATE INDEX idx_qualifications_code ON qualifications(code);
CREATE INDEX idx_qualifications_title ON qualifications(title);
CREATE INDEX idx_qualifications_training_package_id ON qualifications(training_package_id);
CREATE INDEX idx_qualifications_release_date ON qualifications(release_date);
CREATE INDEX idx_qualifications_fts ON qualifications USING gin(to_tsvector('english', title || ' ' || description));

-- Skillsets table
CREATE TABLE skillsets (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    training_package_id INTEGER REFERENCES training_packages(id),
    title TEXT NOT NULL,
    description TEXT,
    modification_history TEXT,
    pathways_information TEXT,
    licensing_information TEXT,
    entry_requirements TEXT,
    target_group TEXT,
    statement_of_attainment TEXT,
    unit_grid TEXT,
    release_date TIMESTAMP WITH TIME ZONE,
    xml_file VARCHAR(255),
    processed CHAR(1) DEFAULT 'N',
    visible BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for skillsets
CREATE INDEX idx_skillsets_code ON skillsets(code);
CREATE INDEX idx_skillsets_title ON skillsets(title);
CREATE INDEX idx_skillsets_training_package_id ON skillsets(training_package_id);
CREATE INDEX idx_skillsets_release_date ON skillsets(release_date);
CREATE INDEX idx_skillsets_fts ON skillsets USING gin(to_tsvector('english', title || ' ' || description));

-- User Progress
CREATE TABLE user_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    unit_id INTEGER REFERENCES units(id),
    status VARCHAR(50) DEFAULT 'not_started',
    progress_percentage INTEGER DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, unit_id)
);

-- Assessments
CREATE TABLE assessments (
    id SERIAL PRIMARY KEY,
    unit_id INTEGER REFERENCES units(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL,
    difficulty_level INTEGER DEFAULT 1,
    experience_points INTEGER DEFAULT 50,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Assessment Questions
CREATE TABLE assessment_questions (
    id SERIAL PRIMARY KEY,
    assessment_id INTEGER REFERENCES assessments(id),
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL,
    correct_answer TEXT,
    points INTEGER DEFAULT 10,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User Submissions
CREATE TABLE user_submissions (
    id SERIAL PRIMARY KEY,
    assessment_id INTEGER REFERENCES assessments(id),
    user_id INTEGER REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'pending',
    score INTEGER,
    feedback TEXT,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    graded_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Achievements
CREATE TABLE achievements (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    icon_url VARCHAR(255),
    experience_points INTEGER DEFAULT 100,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User Achievements
CREATE TABLE user_achievements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    achievement_id INTEGER REFERENCES achievements(id),
    awarded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, achievement_id)
);

-- Badges
CREATE TABLE badges (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    icon_url VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User Badges
CREATE TABLE user_badges (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    badge_id INTEGER REFERENCES badges(id),
    awarded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, badge_id)
);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role_id ON users(role_id);
CREATE INDEX idx_user_progress_user_id ON user_progress(user_id);
CREATE INDEX idx_user_progress_unit_id ON user_progress(unit_id);
CREATE INDEX idx_user_submissions_user_id ON user_submissions(user_id);
CREATE INDEX idx_user_submissions_assessment_id ON user_submissions(assessment_id);
CREATE INDEX idx_user_achievements_user_id ON user_achievements(user_id);
CREATE INDEX idx_user_badges_user_id ON user_badges(user_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for all tables
CREATE TRIGGER update_roles_updated_at
    BEFORE UPDATE ON roles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_permissions_updated_at
    BEFORE UPDATE ON permissions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
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

CREATE TRIGGER update_unit_required_skills_updated_at
    BEFORE UPDATE ON unit_required_skills
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_progress_updated_at
    BEFORE UPDATE ON user_progress
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_assessments_updated_at
    BEFORE UPDATE ON assessments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_assessment_questions_updated_at
    BEFORE UPDATE ON assessment_questions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_submissions_updated_at
    BEFORE UPDATE ON user_submissions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_achievements_updated_at
    BEFORE UPDATE ON achievements
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_achievements_updated_at
    BEFORE UPDATE ON user_achievements
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_badges_updated_at
    BEFORE UPDATE ON badges
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_badges_updated_at
    BEFORE UPDATE ON user_badges
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

CREATE TRIGGER update_unit_critical_aspects_updated_at
    BEFORE UPDATE ON unit_critical_aspects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
