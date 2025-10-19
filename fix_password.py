#!/usr/bin/env python3
"""
Check and fix BigCapitalPy admin password
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

def check_password(db_path='instance/bigcapitalpy.db'):
    """Check admin password and reset if needed"""

    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return

    print("🔐 Checking admin password...")
    print("-" * 30)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get current password hash
    cursor.execute("SELECT password_hash FROM users WHERE email = 'admin@bigcapitalpy.com'")
    result = cursor.fetchone()

    if not result:
        print("❌ Admin user not found!")
        conn.close()
        return

    current_hash = result[0]
    print(f"Current hash: {current_hash[:20]}...")

    # Test the default password
    test_password = "admin123"
    if check_password_hash(current_hash, test_password):
        print("✅ Password 'admin123' is correct")
    else:
        print("❌ Password 'admin123' is incorrect")
        print("🔄 Resetting password to 'admin123'...")

        new_hash = generate_password_hash(test_password)
        cursor.execute("UPDATE users SET password_hash = ? WHERE email = 'admin@bigcapitalpy.com'", (new_hash,))
        conn.commit()
        print("✅ Password reset complete")

    conn.close()
    print("\n📋 Login credentials:")
    print("Email: admin@bigcapitalpy.com")
    print("Password: admin123")

if __name__ == '__main__':
    check_password()