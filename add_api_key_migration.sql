-- Migration: Add API key fields to users table
-- Run this SQL script to add API key functionality to existing BigCapitalPy database

-- Add API key columns to users table (without UNIQUE constraint initially)
ALTER TABLE users ADD COLUMN api_key VARCHAR(64);
ALTER TABLE users ADD COLUMN api_key_created_at DATETIME;

-- Create index on api_key for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_api_key ON users(api_key);

-- Note: UNIQUE constraint is not added here to avoid issues with existing data
-- API keys will be enforced as unique in the application logic