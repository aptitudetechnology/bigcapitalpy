# 1. UPDATE YOUR IMPORTS (add these to the existing imports at the top)
from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
import subprocess
import os
import json
import threading
import time
import uuid
from datetime import datetime
import shutil
import sqlite3
import gnupg
from sqlalchemy import create_engine, text, inspect  # ADD THESE
import tempfile  # ADD THIS

backup_bp = Blueprint('backup', __name__, url_prefix='/backup')

# REMOVE THE OLD DATABASE_PATH CONFIGURATION
# Replace this section:
# DATABASE_PATH = os.path.join(os.getcwd(), 'bigcapitalpy.db')

# With the new helper function approach (the DATABASE_PATH constant is no longer needed)

# Keep your existing GPG and backup directory configuration
BACKUP_DIR = os.path.join(os.getcwd(), 'backups_temp')
os.makedirs(BACKUP_DIR, exist_ok=True)

GPG_HOME = os.path.join(os.getcwd(), '.gnupg_app')
os.makedirs(GPG_HOME, exist_ok=True)

gpg = gnupg.GPG(gnupghome=GPG_HOME)
gpg.keyserver = 'keyserver.ubuntu.com'

# 2. ADD THE NEW HELPER FUNCTIONS (add these after your existing route functions)

def get_database_path():
    """
    Extracts the database file path from SQLAlchemy configuration.
    """
    db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_uri.startswith('sqlite:///'):
        # Remove 'sqlite:///' prefix to get file path
        relative_path = db_uri.replace('sqlite:///', '')
        # If it's an absolute path, return as-is; otherwise, make it relative to app root
        if os.path.isabs(relative_path):
            return relative_path
        else:
            return os.path.join(current_app.root_path, relative_path)
    elif db_uri.startswith('sqlite://'):
        # Handle sqlite:// (relative path with //)
        relative_path = db_uri.replace('sqlite://', '')
        return os.path.join(current_app.root_path, relative_path)
    else:
        # Fallback for other database types or malformed URIs
        return os.path.join(os.getcwd(), 'bigcapitalpy.db')

def backup_database_with_sqlalchemy(backup_dir: str) -> tuple[str, dict]:
    """
    Creates a database backup using SQLAlchemy's engine for better compatibility.
    Returns (backup_file_path, metadata_dict)
    """
    try:
        # Get database path from SQLAlchemy config
        db_path = get_database_path()
        
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file not found at: {db_path}")
        
        # Create backup using SQLite's backup API through SQLAlchemy
        backup_db_path = os.path.join(backup_dir, "database.db")
        
        # Method 1: Use SQLite's backup API (most reliable)
        engine = create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'])
        
        with engine.connect() as source_conn:
            # Create a backup database engine
            backup_engine = create_engine(f'sqlite:///{backup_db_path}')
            
            # Use SQLite's backup API
            source_raw = source_conn.connection.driver_connection
            
            with backup_engine.connect() as backup_conn:
                backup_raw = backup_conn.connection.driver_connection
                
                # Perform the backup using SQLite's backup API
                source_raw.backup(backup_raw)
        
        # Gather database metadata
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        metadata = {
            "database_path": db_path,
            "backup_method": "SQLite Backup API via SQLAlchemy",
            "database_size": os.path.getsize(db_path),
            "backup_size": os.path.getsize(backup_db_path),
            "table_count": len(table_names),
            "tables": []
        }
        
        # Get row counts for each table
        with engine.connect() as conn:
            for table_name in table_names:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    row_count = result.scalar()
                    metadata["tables"].append({
                        "name": table_name,
                        "rows": row_count
                    })
                except Exception as e:
                    metadata["tables"].append({
                        "name": table_name,
                        "error": str(e)
                    })
        
        return backup_db_path, metadata
        
    except Exception as e:
        # Fallback to file copy if SQLAlchemy method fails
        print(f"SQLAlchemy backup failed, falling back to file copy: {e}")
        
        db_path = get_database_path()
        backup_db_path = os.path.join(backup_dir, "database.db")
        
        if os.path.exists(db_path):
            shutil.copy2(db_path, backup_db_path)
            metadata = {
                "database_path": db_path,
                "backup_method": "File copy (fallback)",
                "database_size": os.path.getsize(db_path),
                "backup_size": os.path.getsize(backup_db_path),
                "note": f"SQLAlchemy backup failed: {str(e)}"
            }
            return backup_db_path, metadata
        else:
            raise FileNotFoundError(f"Database file not found at: {db_path}")

def export_database_to_json() -> dict:
    """
    Exports all database tables to JSON format using SQLAlchemy.
    """
    try:
        engine = create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'])
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        database_data = {}
        
        with engine.connect() as conn:
            for table_name in table_names:
                try:
                    # Get all rows from the table
                    result = conn.execute(text(f"SELECT * FROM {table_name}"))
                    rows = result.fetchall()
                    
                    # Convert to list of dictionaries
                    database_data[table_name] = [dict(row._mapping) for row in rows]
                    
                except Exception as e:
                    database_data[table_name] = {"error": str(e)}
        
        return {
            "export_method": "SQLAlchemy",
            "table_count": len(table_names),
            "tables_exported": list(database_data.keys()),
            "data": database_data
        }
        
    except Exception as e:
        return {
            "export_method": "SQLAlchemy (failed)",
            "error": str(e),
            "data": {}
        }

# 3. REPLACE YOUR EXISTING generate_backup() FUNCTION WITH THIS ONE:

def generate_backup(format_type: str, include_attachments: bool) -> str:
    """
    Creates a backup file including the SQLite database using SQLAlchemy.
    Enhanced version that works better with Flask-SQLAlchemy.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename_base = f"bigcapitalpy_backup_{timestamp}"
    backup_file_path = os.path.join(BACKUP_DIR, backup_filename_base)

    try:
        if format_type == 'zip':
            # Create a temporary directory for backup content
            backup_content_dir = os.path.join(BACKUP_DIR, f"backup_content_{uuid.uuid4()}")
            os.makedirs(backup_content_dir, exist_ok=True)

            try:
                # 1. Backup database using SQLAlchemy-compatible method
                db_backup_path, db_metadata = backup_database_with_sqlalchemy(backup_content_dir)
                print(f"Database backed up successfully: {db_backup_path}")

                # 2. Create comprehensive backup metadata
                metadata = {
                    "backup_created": datetime.now().isoformat(),
                    "backup_type": "BigCapitalPy Full Backup",
                    "format": format_type,
                    "include_attachments": include_attachments,
                    "database_info": db_metadata,
                    "sqlalchemy_uri": current_app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured'),
                    "backup_version": "2.0"
                }
                
                with open(os.path.join(backup_content_dir, "backup_metadata.json"), "w") as f:
                    json.dump(metadata, f, indent=2, default=str)

                # 3. Include attachments if requested
                if include_attachments:
                    attachments_dir = os.path.join(backup_content_dir, "attachments")
                    os.makedirs(attachments_dir, exist_ok=True)
                    
                    # Common Flask attachment directories
                    possible_attachment_dirs = [
                        os.path.join(current_app.root_path, 'uploads'),
                        os.path.join(current_app.root_path, 'static', 'uploads'),
                        os.path.join(current_app.root_path, 'attachments'),
                        os.path.join(current_app.root_path, 'user_files'),
                        os.path.join(current_app.instance_path, 'uploads') if hasattr(current_app, 'instance_path') else None
                    ]
                    
                    # Remove None values
                    possible_attachment_dirs = [d for d in possible_attachment_dirs if d is not None]
                    
                    attachments_found = False
                    attachment_summary = []
                    
                    for source_dir in possible_attachment_dirs:
                        if os.path.exists(source_dir) and os.path.isdir(source_dir):
                            dest_subdir = os.path.join(attachments_dir, os.path.basename(source_dir))
                            shutil.copytree(source_dir, dest_subdir, dirs_exist_ok=True)
                            
                            # Count files
                            file_count = sum([len(files) for r, d, files in os.walk(dest_subdir)])
                            attachment_summary.append({
                                "source": source_dir,
                                "destination": os.path.basename(source_dir),
                                "files_copied": file_count
                            })
                            attachments_found = True
                            print(f"Copied {file_count} files from: {source_dir}")
                    
                    # Update metadata with attachment info
                    metadata["attachments"] = {
                        "included": attachments_found,
                        "directories_searched": possible_attachment_dirs,
                        "directories_copied": attachment_summary
                    }
                    
                    if not attachments_found:
                        with open(os.path.join(attachments_dir, "no_attachments_found.txt"), "w") as f:
                            f.write("No attachment directories were found at the expected locations.\n")
                            f.write(f"Searched locations:\n")
                            for dir_path in possible_attachment_dirs:
                                f.write(f"  - {dir_path} {'(exists)' if os.path.exists(dir_path) else '(not found)'}\n")

                # 4. Update metadata file with final info
                with open(os.path.join(backup_content_dir, "backup_metadata.json"), "w") as f:
                    json.dump(metadata, f, indent=2, default=str)

                # 5. Create the ZIP archive
                final_zip_path = shutil.make_archive(backup_file_path, 'zip', root_dir=backup_content_dir)
                
                # Clean up the temporary directory
                shutil.rmtree(backup_content_dir)
                return final_zip_path

            except Exception as e:
                # Ensure cleanup on error
                if os.path.exists(backup_content_dir):
                    shutil.rmtree(backup_content_dir)
                raise e

        elif format_type == 'json':
            # For JSON format, export database data using SQLAlchemy
            final_json_path = f"{backup_file_path}.json"
            
            backup_data = {
                "backup_created": datetime.now().isoformat(),
                "backup_type": "BigCapitalPy JSON Export",
                "format": format_type,
                "include_attachments": include_attachments,
                "sqlalchemy_uri": current_app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured'),
                "database_export": export_database_to_json()
            }

            with open(final_json_path, "w") as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            return final_json_path

        else:  # CSV or other formats - fallback to text with database info
            final_txt_path = f"{backup_file_path}.txt"
            
            with open(final_txt_path, "w") as f:
                f.write("=== BIGCAPITALPY BACKUP SUMMARY ===\n")
                f.write(f"Backup created at: {datetime.now()}\n")
                f.write(f"Format: {format_type}\n")
                f.write(f"Include attachments: {include_attachments}\n")
                f.write(f"SQLAlchemy URI: {current_app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}\n\n")
                
                # Get database info using SQLAlchemy
                try:
                    db_path = get_database_path()
                    if os.path.exists(db_path):
                        f.write("=== DATABASE INFO ===\n")
                        f.write(f"Database file: {db_path}\n")
                        f.write(f"Database size: {os.path.getsize(db_path):,} bytes\n")
                        
                        engine = create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'])
                        inspector = inspect(engine)
                        table_names = inspector.get_table_names()
                        f.write(f"Number of tables: {len(table_names)}\n\n")
                        
                        with engine.connect() as conn:
                            for table_name in table_names:
                                try:
                                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                                    row_count = result.scalar()
                                    f.write(f"Table '{table_name}': {row_count:,} rows\n")
                                except Exception as e:
                                    f.write(f"Table '{table_name}': Error reading ({str(e)})\n")
                    else:
                        f.write(f"=== DATABASE ERROR ===\n")
                        f.write(f"Database file not found at: {db_path}\n")
                        
                except Exception as e:
                    f.write(f"=== DATABASE ERROR ===\n")
                    f.write(f"Error accessing database: {str(e)}\n")
                
                if include_attachments:
                    f.write("\n=== ATTACHMENTS ===\n")
                    f.write("Note: Attachments cannot be included in text format.\n")
                    f.write("Please use ZIP format for complete backup with attachments.\n")
            
            return final_txt_path

    except Exception as e:
        print(f"Error generating backup: {e}")
        raise

# 4. KEEP ALL YOUR EXISTING ROUTES AND OTHER FUNCTIONS AS THEY ARE
# (index, test_endpoint, gpg_search, gpg_import, create_backup, etc.)
# Only the generate_backup function and helper functions need to be replaced/added