-- Migration: Add API key fields to users table
-- Run this SQL script to add API key functionality to existing BigCapitalPy database

-- Add API key columns to users table
ALTER TABLE users ADD COLUMN api_key VARCHAR(64) UNIQUE;
ALTER TABLE users ADD COLUMN api_key_created_at DATETIME;

-- Create index on api_key for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_api_key ON users(api_key);

-- Optional: Generate API keys for existing users (uncomment if desired)
-- UPDATE users SET
--     api_key = hex(randomblob(32)),
--     api_key_created_at = datetime('now')
-- WHERE api_key IS NULL AND is_active = 1;