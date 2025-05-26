-- Create training_components table
CREATE TABLE IF NOT EXISTS training_components (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    tga_id VARCHAR(100),
    training_package_code VARCHAR(50),
    release_date DATE,
    elements_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster searches
CREATE INDEX IF NOT EXISTS idx_training_components_code ON training_components(code);
CREATE INDEX IF NOT EXISTS idx_training_components_training_package ON training_components(training_package_code);

-- Function to update timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to auto-update updated_at
DROP TRIGGER IF EXISTS update_training_component_timestamp ON training_components;
CREATE TRIGGER update_training_component_timestamp
    BEFORE UPDATE ON training_components
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
