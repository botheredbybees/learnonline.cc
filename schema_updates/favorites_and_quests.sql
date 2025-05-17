-- User Favorites and Quests Schema

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

-- Create indexes for better query performance
CREATE INDEX idx_quests_creator_id ON quests(creator_id);
CREATE INDEX idx_quests_quest_type ON quests(quest_type);
CREATE INDEX idx_quests_is_public ON quests(is_public);
CREATE INDEX idx_quests_is_introductory ON quests(is_introductory);
CREATE INDEX idx_quest_units_unit_id ON quest_units(unit_id);
CREATE INDEX idx_guest_progress_quest_id ON guest_progress(quest_id);
CREATE INDEX idx_user_quest_progress_quest_id ON user_quest_progress(quest_id);

-- Functions to track updates
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add trigger to update the updated_at column
DROP TRIGGER IF EXISTS update_quests_updated_at ON quests;
CREATE TRIGGER update_quests_updated_at
BEFORE UPDATE ON quests
FOR EACH ROW
EXECUTE FUNCTION update_modified_column();
