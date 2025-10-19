#!/usr/bin/env python3
"""
BigCapitalPy Database Migration Script
Adds API key columns to existing users table
"""

import sqlite3
import os
import sys

def migrate_database(db_path='bigcapitalpy.db'):
    """Add API key columns to the users table"""

    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        print("Make sure BigCapitalPy has been run at least once to create the database.")
        return False

    print(f"🔄 Migrating database: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'api_key' not in columns:
            print("📝 Adding api_key column...")
            cursor.execute("ALTER TABLE users ADD COLUMN api_key VARCHAR(64)")
        else:
            print("ℹ️  api_key column already exists")

        if 'api_key_created_at' not in columns:
            print("📝 Adding api_key_created_at column...")
            cursor.execute("ALTER TABLE users ADD COLUMN api_key_created_at DATETIME")
        else:
            print("ℹ️  api_key_created_at column already exists")

        # Create index (this is safe to run multiple times)
        print("📝 Creating index on api_key...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_api_key ON users(api_key)")

        # Add unique constraint separately if needed
        try:
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_api_key_unique ON users(api_key)")
        except sqlite3.Error:
            print("⚠️  Could not create unique constraint (may already exist or have duplicates)")

        conn.commit()
        conn.close()

        print("✅ Migration completed successfully!")
        print("🔑 API key functionality is now available.")
        return True

    except sqlite3.Error as e:
        print(f"❌ Migration failed: {e}")
        return False

def main():
    """Main migration function"""
    import argparse

    parser = argparse.ArgumentParser(description='Migrate BigCapitalPy database to add API key support')
    parser.add_argument('db_path', nargs='?', help='Path to the BigCapitalPy database file')
    args = parser.parse_args()

    print("🚀 BigCapitalPy Database Migration")
    print("Adding API key support to users table")
    print("-" * 40)

    db_path = args.db_path
    if not db_path:
        # Try common database locations
        possible_paths = [
            'bigcapitalpy.db',
            './bigcapitalpy.db',
            'instance/bigcapitalpy.db',
            './instance/bigcapitalpy.db',
            '../bigcapitalpy.db',
            '/app/bigcapitalpy.db',  # Docker container
            os.path.expanduser('~/bigcapitalpy.db')
        ]

        for path in possible_paths:
            if os.path.exists(path):
                db_path = path
                print(f"📍 Found database at: {path}")
                break

        if not db_path:
            print("❌ Could not find bigcapitalpy.db database file.")
            print("Please specify the database path as an argument:")
            print("  python3 migrate_db.py /path/to/bigcapitalpy.db")
            sys.exit(1)

    if migrate_database(db_path):
        print("\n📋 Next steps:")
        print("1. Restart your BigCapitalPy server")
        print("2. Generate an API key via /api/v1/auth/api-key")
        print("3. Use the API key for programmatic access")
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()