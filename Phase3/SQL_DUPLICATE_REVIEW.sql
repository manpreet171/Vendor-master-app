-- Add duplicates_reviewed flag to requirements_bundles table
-- This tracks whether operator has reviewed duplicate project items in a bundle

ALTER TABLE requirements_bundles
ADD duplicates_reviewed BIT DEFAULT 0;

-- Verify the column was added
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'requirements_bundles' 
AND COLUMN_NAME = 'duplicates_reviewed';
