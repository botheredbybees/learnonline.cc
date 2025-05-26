-- Add total_achievements_count column to user_profiles table

ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS total_achievements_count INTEGER DEFAULT 0;

-- Update existing user profiles to count their current achievements
UPDATE user_profiles 
SET total_achievements_count = (
    SELECT COUNT(*) 
    FROM user_achievements 
    WHERE user_achievements.user_id = user_profiles.user_id
)
WHERE total_achievements_count IS NULL OR total_achievements_count = 0;

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_user_profiles_achievements_count ON user_profiles(total_achievements_count);
