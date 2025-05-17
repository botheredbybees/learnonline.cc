-- Add experience points and level to users table

-- First add the user_level type if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_level') THEN
        CREATE TYPE user_level AS ENUM ('guest', 'player', 'mentor');
    END IF;
END
$$;

-- Add new columns to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS experience_points INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS level user_level DEFAULT 'guest';

-- Update existing users to player level if they've been active
UPDATE users 
SET level = 'player' 
WHERE last_login IS NOT NULL 
AND level IS NULL;

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

-- Create index for experience points for faster sorting
CREATE INDEX IF NOT EXISTS idx_users_experience_points ON users(experience_points);
