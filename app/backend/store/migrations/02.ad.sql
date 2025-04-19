-- Migration for ad table
-- Creates a table to store advertisement data

CREATE TABLE IF NOT EXISTS ad (
    id UUID PRIMARY KEY, -- Unique identifier for the ad
    image TEXT, -- URL or path to the ad image
    copy TEXT, -- Ad copy/text content
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(), -- When the record was created
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() -- When the record was last updated
);

-- Add a trigger to automatically update the updated_at column
CREATE TRIGGER update_ad_updated_at
BEFORE UPDATE ON ad
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Add comments to the table and columns for documentation
COMMENT ON TABLE ad IS 'Stores advertisement data for testing with personalities';
COMMENT ON COLUMN ad.id IS 'Unique identifier for the advertisement';
COMMENT ON COLUMN ad.image IS 'URL or path to the advertisement image';
COMMENT ON COLUMN ad.copy IS 'Advertisement copy/text content';
