# SQLite Backup Issue Report and Proposed Solution

## Problem Summary

When attempting to create a backup using the current `backup.py` implementation, the following error occurs:

```
Database file not found at: /home/chris/bigcapitalpy/bigcapitalpy.db
```

This error is triggered because the backup logic is designed for SQLite databases and attempts to locate a `.db` file based on the `SQLALCHEMY_DATABASE_URI` configuration. If the URI is not for SQLite, it falls back to a hardcoded path, which does not exist in PostgreSQL or other DB setups.

## Root Cause

- The function `get_database_path()` only supports SQLite URIs. For any other database (e.g., PostgreSQL), it defaults to a non-existent SQLite file.
- The backup logic in `backup_database_with_sqlalchemy()` and `generate_backup()` assumes a file-based SQLite database is always present.
- If your app is configured for PostgreSQL, this logic will always fail.

## Proposed Solution

1. **Detect Database Type:**
   - Check the `SQLALCHEMY_DATABASE_URI` for the database dialect (e.g., `sqlite`, `postgresql`).
2. **Handle PostgreSQL Gracefully:**
   - If the database is not SQLite, raise a clear error and suggest using `pg_dump` for PostgreSQL backups.
   - Optionally, provide a stub for PostgreSQL backup using `pg_dump` (if desired).
3. **Update Error Messages:**
   - Make error messages explicit about unsupported database types.

## Example Code Changes

Below is a patch to improve the backup logic for non-SQLite databases:

```python
# ...existing code...
def get_database_path():
    """
    Extracts the database file path from SQLAlchemy configuration.
    Only supports SQLite. Raises error for other DBs.
    """
    try:
        db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if db_uri.startswith('sqlite:///'):
            relative_path = db_uri.replace('sqlite:///', '')
            if os.path.isabs(relative_path):
                return relative_path
            else:
                return os.path.join(current_app.root_path, relative_path)
        elif db_uri.startswith('sqlite://'):
            relative_path = db_uri.replace('sqlite://', '')
            return os.path.join(current_app.root_path, relative_path)
        else:
            raise RuntimeError(f"Automatic backup only supports SQLite. Your database URI is: {db_uri}. For PostgreSQL, use pg_dump.")
    except Exception as e:
        raise RuntimeError(f"Could not determine database path: {e}")

# ...existing code...
def backup_database_with_sqlalchemy(backup_dir: str):
    """
    Creates a database backup using SQLAlchemy if available, otherwise falls back to file copy.
    Only supports SQLite. Raises error for other DBs.
    """
    db_path = get_database_path()
    backup_db_path = os.path.join(backup_dir, "database.db")
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at: {db_path}")
    # ...existing code...
```

## PostgreSQL Backup (Optional)

If you want to support PostgreSQL backups, you can use the `pg_dump` utility. Here is a complete example:

```python
import re
import subprocess
import os
from flask import current_app

def backup_postgresql_database(backup_dir: str):
    """
    Creates a PostgreSQL database backup using pg_dump.
    The backup will be saved as a .sql file in backup_dir.
    Requires pg_dump to be installed and accessible in PATH.
    """
    db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
    # Example URI: postgresql://user:password@host:port/dbname
    pattern = r'postgresql://(?P<user>[^:]+):(?P<password>[^@]+)@(?P<host>[^:/]+)(:(?P<port>\d+))?/(?P<dbname>[^?]+)'
    match = re.match(pattern, db_uri)
    if not match:
        raise RuntimeError(f"Could not parse PostgreSQL URI: {db_uri}")
    user = match.group('user')
    password = match.group('password')
    host = match.group('host')
    port = match.group('port') or '5432'
    dbname = match.group('dbname')

    backup_file = os.path.join(backup_dir, f"{dbname}_backup.sql")
    env = os.environ.copy()
    env['PGPASSWORD'] = password
    cmd = [
        'pg_dump',
        '-h', host,
        '-p', port,
        '-U', user,
        '-F', 'c',  # custom format (compressed); use 'plain' for .sql
        '-b',       # include blobs
        '-f', backup_file,
        dbname
    ]
    try:
        subprocess.run(cmd, check=True, env=env)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"pg_dump failed: {e}")
    return backup_file
```

**Notes:**
- This function requires `pg_dump` to be installed and available in your system's PATH.
- The backup will be saved in PostgreSQL's custom format (`.sql` if you change `-F` to `plain`).
- You may need to adjust permissions or connection parameters for your environment.

## Recommendation
- **Short-term:** Apply the above patch to provide a clear error for non-SQLite DBs.
- **Long-term:** Implement PostgreSQL backup support using `pg_dump` if needed.

---

*Generated by GitHub Copilot on 2025-07-26.*
