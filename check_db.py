#!/usr/bin/env python3
"""
Check BigCapitalPy database contents
"""

import sqlite3
import os

def check_database(db_path='instance/bigcapitalpy.db'):
    """Check database contents"""

    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return

    print(f"🔍 Checking database: {db_path}")
    print("-" * 40)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check users table
    print("👥 Users:")
    cursor.execute("SELECT id, email, first_name, last_name, role, is_active FROM users")
    users = cursor.fetchall()
    if users:
        for user in users:
            print(f"  ID: {user[0]}, Email: {user[1]}, Name: {user[2]} {user[3]}, Role: {user[4]}, Active: {user[5]}")
    else:
        print("  No users found")

    # Check organizations table
    print("\n🏢 Organizations:")
    cursor.execute("SELECT id, name FROM organizations")
    orgs = cursor.fetchall()
    if orgs:
        for org in orgs:
            print(f"  ID: {org[0]}, Name: {org[1]}")
    else:
        print("  No organizations found")

    # Check if tables exist
    print("\n📋 Tables:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for table in tables:
        print(f"  {table[0]}")

    conn.close()

if __name__ == '__main__':
    check_database()