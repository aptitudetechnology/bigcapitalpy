#!/bin/bash
# BigCapitalPy Database Rebuild Script
# This script rebuilds the database from scratch with the complete schema

set -e

echo "🔄 Rebuilding BigCapitalPy database..."

# Database file location (adjust if needed)
DB_FILE="bigcapitalpy.db"

# Backup existing database if it exists
if [ -f "$DB_FILE" ]; then
    BACKUP_FILE="${DB_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "📦 Backing up existing database to $BACKUP_FILE"
    cp "$DB_FILE" "$BACKUP_FILE"
fi

# Remove existing database
if [ -f "$DB_FILE" ]; then
    echo "🗑️  Removing existing database..."
    rm "$DB_FILE"
fi

# Create new database from schema
echo "🏗️  Creating new database from schema..."
sqlite3 "$DB_FILE" < schema.sql

echo "✅ Database rebuilt successfully!"
echo "📍 Database file: $DB_FILE"
echo ""
echo "Next steps:"
echo "1. Start your BigCapitalPy server"
echo "2. Visit http://your-server.com to set up your account"
echo "3. Use the API key endpoints to generate API keys for programmatic access"