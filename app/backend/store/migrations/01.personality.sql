-- Migration for personality table
-- Creates a table to store personality profiles

CREATE TABLE IF NOT EXISTS personality (
    id UUID PRIMARY KEY, -- Unique identifier for the personality
    name VARCHAR(255), -- Name of the personality profile
    age INTEGER, -- Age of the personality
    gender VARCHAR(50), -- Gender of the personality
    location VARCHAR(255), -- Geographic location
    education_level VARCHAR(100), -- Education level (e.g., High School, Bachelor's, etc.)
    marital_status VARCHAR(50), -- Marital status (e.g., Single, Married, etc.)
    children INTEGER, -- Number of children
    
    -- Professional Details
    occupation VARCHAR(255), -- General occupation field
    job_title VARCHAR(255), -- Specific job title
    industry VARCHAR(255), -- Industry sector
    income DECIMAL(12, 2), -- Annual income
    seniority_level VARCHAR(100), -- Seniority level in career
    
    -- Psychographics (stored as arrays)
    personality_traits TEXT[], -- List of personality traits
    values TEXT[], -- Personal values
    attitudes TEXT[], -- Attitudes toward various topics
    interests TEXT[], -- Personal interests
    lifestyle TEXT[], -- Lifestyle choices
    habits TEXT[], -- Regular habits
    frustrations TEXT[], -- Pain points or frustrations
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(), -- When the record was created
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() -- When the record was last updated
);

-- Add indexes for common query patterns
CREATE INDEX idx_personality_age ON personality(age);
CREATE INDEX idx_personality_gender ON personality(gender);
CREATE INDEX idx_personality_location ON personality(location);
CREATE INDEX idx_personality_income ON personality(income);
CREATE INDEX idx_personality_industry ON personality(industry);

-- Add a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add a trigger to automatically update the updated_at column
CREATE TRIGGER update_personality_updated_at
BEFORE UPDATE ON personality
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Add comments to the table and columns for documentation
COMMENT ON TABLE personality IS 'Stores personality profiles for ad targeting';
COMMENT ON COLUMN personality.id IS 'Unique identifier for the personality profile';
COMMENT ON COLUMN personality.name IS 'Name of the personality profile';
COMMENT ON COLUMN personality.age IS 'Age of the personality';
COMMENT ON COLUMN personality.gender IS 'Gender of the personality';
COMMENT ON COLUMN personality.location IS 'Geographic location of the personality';
COMMENT ON COLUMN personality.education_level IS 'Highest level of education achieved';
COMMENT ON COLUMN personality.marital_status IS 'Current marital status';
COMMENT ON COLUMN personality.children IS 'Number of children';
COMMENT ON COLUMN personality.occupation IS 'General occupation field';
COMMENT ON COLUMN personality.job_title IS 'Specific job title';
COMMENT ON COLUMN personality.industry IS 'Industry sector the personality works in';
COMMENT ON COLUMN personality.income IS 'Annual income in local currency';
COMMENT ON COLUMN personality.seniority_level IS 'Seniority level in career (e.g., Entry, Mid, Senior)';
COMMENT ON COLUMN personality.personality_traits IS 'List of personality traits (e.g., Extroverted, Analytical)';
COMMENT ON COLUMN personality.values IS 'Personal values (e.g., Family, Career, Environment)';
COMMENT ON COLUMN personality.attitudes IS 'Attitudes toward various topics';
COMMENT ON COLUMN personality.interests IS 'Personal interests and hobbies';
COMMENT ON COLUMN personality.lifestyle IS 'Lifestyle choices and preferences';
COMMENT ON COLUMN personality.habits IS 'Regular habits and behaviors';
COMMENT ON COLUMN personality.frustrations IS 'Pain points or frustrations';
