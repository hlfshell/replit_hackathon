-- Migration for rating table
-- Creates a table to store ratings of ads by personalities

CREATE TABLE IF NOT EXISTS rating (
    id UUID PRIMARY KEY, -- Unique identifier for the rating
    personality_id UUID NOT NULL, -- Reference to the personality
    ad_id UUID NOT NULL, -- Reference to the ad
    thought TEXT, -- Thought process about the ad
    emotional_response TEXT, -- Overall emotional response
    emotions TEXT, -- Specific emotions experienced
    categories TEXT[], -- Categories associated with this rating
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(), -- When the record was created
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(), -- When the record was last updated
    
    -- Add foreign key constraints
    CONSTRAINT fk_personality
        FOREIGN KEY(personality_id)
        REFERENCES personality(id)
        ON DELETE CASCADE,
    
    CONSTRAINT fk_ad
        FOREIGN KEY(ad_id)
        REFERENCES ad(id)
        ON DELETE CASCADE
);

-- Add a trigger to automatically update the updated_at column
CREATE TRIGGER update_rating_updated_at
BEFORE UPDATE ON rating
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Add indexes for faster lookups
CREATE INDEX idx_rating_personality ON rating(personality_id);
CREATE INDEX idx_rating_ad ON rating(ad_id);

-- Add a unique constraint to prevent duplicate ratings
CREATE UNIQUE INDEX idx_unique_personality_ad ON rating(personality_id, ad_id);

-- Add a GIN index for efficient searching through the categories array
CREATE INDEX idx_rating_categories ON rating USING GIN(categories);

-- Add comments to the table and columns for documentation
COMMENT ON TABLE rating IS 'Stores ratings of ads by personalities';
COMMENT ON COLUMN rating.id IS 'Unique identifier for the rating';
COMMENT ON COLUMN rating.personality_id IS 'Reference to the personality giving the rating';
COMMENT ON COLUMN rating.ad_id IS 'Reference to the ad being rated';
COMMENT ON COLUMN rating.thought IS 'Thought process or reasoning about the ad';
COMMENT ON COLUMN rating.emotional_response IS 'Overall emotional response to the ad';
COMMENT ON COLUMN rating.emotions IS 'Specific emotions experienced when viewing the ad';
COMMENT ON COLUMN rating.categories IS 'Categories associated with this rating';
