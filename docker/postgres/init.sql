-- BigCapitalPy PostgreSQL Initialization Script
-- This script sets up the initial database structure and sample data

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create additional schemas if needed
CREATE SCHEMA IF NOT EXISTS accounting;
CREATE SCHEMA IF NOT EXISTS reporting;

-- Grant permissions to the bigcapital user
GRANT ALL PRIVILEGES ON SCHEMA accounting TO bigcapital;
GRANT ALL PRIVILEGES ON SCHEMA reporting TO bigcapital;
GRANT ALL PRIVILEGES ON SCHEMA public TO bigcapital;

-- Create indexes for better performance (will be created by SQLAlchemy migrations)
-- These are just placeholders for future optimizations

-- Set timezone
SET timezone = 'UTC';
