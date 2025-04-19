-- Migration for category table
-- Creates a table to store categories and category assignments

-- First, create the category table
CREATE TABLE IF NOT EXISTS category (
    id UUID PRIMARY KEY, -- Unique identifier for the category
    name VARCHAR(255) NOT NULL, -- Name of the category
    description TEXT, -- Description of what this category represents
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(), -- When the record was created
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() -- When the record was last updated
);

-- Add a trigger to automatically update the updated_at column
CREATE TRIGGER update_category_updated_at
BEFORE UPDATE ON category
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Add a unique index on category name to prevent duplicates
CREATE UNIQUE INDEX idx_category_name ON category(name);

-- Add comments to the table and columns for documentation
COMMENT ON TABLE category IS 'Stores categories for classifying personalities and ads';
COMMENT ON COLUMN category.id IS 'Unique identifier for the category';
COMMENT ON COLUMN category.name IS 'Name of the category';
COMMENT ON COLUMN category.description IS 'Description of what this category represents';

-- Now create the category_assignment table to link personalities to categories
CREATE TABLE IF NOT EXISTS category_assignment (
    id UUID PRIMARY KEY, -- Unique identifier for the assignment
    personality_id UUID NOT NULL, -- Reference to the personality
    category_id UUID NOT NULL, -- Reference to the category
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(), -- When the record was created
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(), -- When the record was last updated
    
    -- Add foreign key constraints
    CONSTRAINT fk_personality
        FOREIGN KEY(personality_id)
        REFERENCES personality(id)
        ON DELETE CASCADE,
    
    CONSTRAINT fk_category
        FOREIGN KEY(category_id)
        REFERENCES category(id)
        ON DELETE CASCADE
);

-- Add a trigger to automatically update the updated_at column
CREATE TRIGGER update_category_assignment_updated_at
BEFORE UPDATE ON category_assignment
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Add indexes for faster lookups
CREATE INDEX idx_category_assignment_personality ON category_assignment(personality_id);
CREATE INDEX idx_category_assignment_category ON category_assignment(category_id);

-- Add a unique constraint to prevent duplicate assignments
CREATE UNIQUE INDEX idx_unique_personality_category ON category_assignment(personality_id, category_id);

-- Add comments to the table and columns for documentation
COMMENT ON TABLE category_assignment IS 'Links personalities to their assigned categories';
COMMENT ON COLUMN category_assignment.id IS 'Unique identifier for the category assignment';
COMMENT ON COLUMN category_assignment.personality_id IS 'Reference to the personality';
COMMENT ON COLUMN category_assignment.category_id IS 'Reference to the category';
