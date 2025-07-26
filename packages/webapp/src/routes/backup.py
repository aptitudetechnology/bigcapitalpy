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
import tempfile

# Try to import SQLAlchemy components with fallback
try:
    from sqlalchemy import create_engine, text, inspect
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    print("Warning: SQLAlchemy not available. Database backup will use fallback method.")

backup_bp = Blueprint('backup', __name__, url_prefix='/backup')

# Define a temporary directory for backups
BACKUP_DIR = os.path.join(os.getcwd(), 'backups_temp')
os.makedirs(BACKUP_DIR, exist_ok=True)

# Define a GPG home directory for the application
GPG_HOME = os.path.join(os.getcwd(), '.gnupg_app')
os.makedirs(GPG_HOME, exist_ok=True)

# Initialize the GPG object
gpg = gnupg.GPG(gnupghome=GPG_HOME)
gpg.keyserver = 'keyserver.ubuntu.com'

# In-memory job storage (use Redis or database in production)
backup_jobs = {}

@backup_bp.route('/')
@login_required
def index():
    """
    Renders the backup index page.
    """
    return render_template('backup/index.html',
                           last_backup_timestamp=None,
                           previous_backups=None,
                           enable_scheduled_backups=False,
                           user=current_user)

@backup_bp.route('/test', methods=['GET', 'POST'])
@login_required
def test_endpoint():
    """
    A simple test endpoint to verify the blueprint is working.
    """
    return jsonify({
        'success': True,
        'message': 'Backup blueprint is working',
        'method': request.method,
        'user': current_user.email if current_user else 'No user',
        'sqlalchemy_available': SQLALCHEMY_AVAILABLE
    })

@backup_bp.route('/gpg/search', methods=['POST'])
@login_required
def gpg_search():
    """
    Searches for GPG keys on a keyserver by email address using python-gnupg.
    """
    try:
        data = request.get_json(force=True)
        email = data.get('email')
        if not email:
            return jsonify({'success': False, 'error': 'Email is required'}), 400

        search_result = gpg.search_keys(email, keyserver=gpg.keyserver)

        if not search_result:
            return jsonify({
                'success': False,
                'error': 'No GPG keys found for this email.',
                'details': 'Search returned no results.'
            }), 404

        keys_list = []
        for key in search_result:
            keys_list.append({
                'key_id': key.get('keyid'),
                'created': key.get('date'),
                'uids': key.get('uids', [])
            })

        return jsonify({'success': True, 'keys': keys_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@backup_bp.route('/gpg/import', methods=['POST'])
@login_required
def gpg_import():
    """
    Imports a GPG public key from a keyserver using python-gnupg.
    """
    try:
        data = request.get_json(force=True)
        key_id = data.get('key_id')
        if not key_id:
            return jsonify({'success': False, 'error': 'Key ID is required'}), 400

        import_result = gpg.recv_keys(gpg.keyserver, key_id)

        if not import_result or not import_result.fingerprints:
            return jsonify({
                'success': False,
                'error': 'Failed to import key',
                'details': import_result.results if import_result else 'No key imported.'
            })

        return jsonify({
            'success': True,
            'message': 'Key imported successfully',
            'key_id': key_id,
            'fingerprints': import_result.fingerprints
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@backup_bp.route('/create', methods=['POST'])
@login_required
def create_backup():
    """
    Initiates a backup creation process.
    """
    try:
        format_type = request.form.get('format', 'zip')
        include_attachments = 'include_attachments' in request.form
        encrypt_gpg = 'encrypt_gpg' in request.form
        gpg_email = request.form.get('gpg_email')

        if encrypt_gpg and gpg_email:
            job_id = str(uuid.uuid4())
            backup_jobs[job_id] = {
                'id': job_id,
                'created_at': datetime.now(),
                'status': 'Starting backup...',
                'progress': 0,
                'completed': False,
                'error': None,
                'details': None,
                'download_url': None,
                'file_path': None
            }
            
            thread = threading.Thread(
                target=create_backup_async,
                args=(job_id, format_type, include_attachments, encrypt_gpg, gpg_email)
            )
            thread.daemon = True
            thread.start()
            return jsonify({
                'success': True,
                'job_id': job_id,
                'message': 'Backup started'
            })
        else:
            # Fixed the parameter name issue here
            backup_path = generate_backup(format_type=format_type, include_attachments=include_attachments)
            return send_file(backup_path, as_attachment=True)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to create backup',
            'details': str(e)
        }), 500

@backup_bp.route('/progress/<job_id>', methods=['GET'])
@login_required
def backup_progress(job_id):
    """
    Retrieves the current progress and status of an asynchronous backup job.
    """
    job = backup_jobs.get(job_id)
    if not job:
        return jsonify({'success': False, 'error': 'Job not found'}), 404
    if job.get('error'):
        return jsonify({'success': False, 'error': job['error'], 'details': job.get('details')})
    return jsonify({
        'success': True,
        'progress': {
            'percentage': job['progress'],
            'status': job['status'],
            'label': f"Progress: {job['progress']}%"
        },
        'completed': job['completed'],
        'download_url': job.get('download_url')
    })

@backup_bp.route('/cancel/<job_id>', methods=['POST'])
@login_required
def cancel_backup(job_id):
    """
    Cancels an ongoing backup job.
    """
    job = backup_jobs.get(job_id)
    if not job:
        return jsonify({'success': False, 'error': 'Job not found'}), 404
    job['cancelled'] = True
    job['completed'] = True
    job['error'] = 'Backup cancelled by user'
    
    # Clean up files
    for file_key in ['file_path', 'encrypted_file_path']:
        file_path = job.get(file_key)
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error cleaning up cancelled backup file {file_path}: {e}")
    
    return jsonify({'success': True, 'message': 'Backup cancelled'})

@backup_bp.route('/download/<job_id>', methods=['GET'])
@login_required
def download_backup(job_id):
    """
    Allows downloading of a completed backup file.
    """
    job = backup_jobs.get(job_id)
    if not job:
        return jsonify({'success': False, 'error': 'Job not found'}), 404
    
    if not job['completed'] or job.get('error'):
        return jsonify({'success': False, 'error': 'Backup not ready or failed'}), 400
    
    file_path = job.get('encrypted_file_path') or job.get('file_path')
    
    if not file_path or not os.path.exists(file_path):
        return jsonify({'success': False, 'error': 'Backup file not found'}), 404
    
    return send_file(file_path, as_attachment=True)

def get_database_path():
    """
    Extracts the database file path from SQLAlchemy configuration.
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
            # Fallback
            return os.path.join(os.getcwd(), 'bigcapitalpy.db')
    except Exception:
        # Fallback if current_app is not available
        return os.path.join(os.getcwd(), 'bigcapitalpy.db')

def backup_database_with_sqlalchemy(backup_dir: str):
    """
    Creates a database backup using SQLAlchemy if available, otherwise falls back to file copy.
    Returns (backup_file_path, metadata_dict)
    """
    db_path = get_database_path()
    backup_db_path = os.path.join(backup_dir, "database.db")
    
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at: {db_path}")
    
    if SQLALCHEMY_AVAILABLE:
        try:
            # Use SQLAlchemy method
            engine = create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'])
            
            with engine.connect() as source_conn:
                backup_engine = create_engine(f'sqlite:///{backup_db_path}')
                
                source_raw = source_conn.connection.driver_connection
                
                with backup_engine.connect() as backup_conn:
                    backup_raw = backup_conn.connection.driver_connection
                    source_raw.backup(backup_raw)
            
            # Gather metadata
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
            print(f"SQLAlchemy backup failed, falling back to file copy: {e}")
    
    # Fallback method
    shutil.copy2(db_path, backup_db_path)
    metadata = {
        "database_path": db_path,
        "backup_method": "File copy (fallback)",
        "database_size": os.path.getsize(db_path),
        "backup_size": os.path.getsize(backup_db_path),
        "sqlalchemy_available": SQLALCHEMY_AVAILABLE
    }
    return backup_db_path, metadata

def export_database_to_json():
    """
    Exports all database tables to JSON format.
    """
    if not SQLALCHEMY_AVAILABLE:
        return {
            "export_method": "SQLAlchemy not available",
            "error": "SQLAlchemy is required for JSON export",
            "data": {}
        }
    
    try:
        engine = create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'])
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        database_data = {}
        
        with engine.connect() as conn:
            for table_name in table_names:
                try:
                    result = conn.execute(text(f"SELECT * FROM {table_name}"))
                    rows = result.fetchall()
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

def generate_backup(format_type: str, include_attachments: bool) -> str:
    """
    Creates a backup file including the SQLite database.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename_base = f"bigcapitalpy_backup_{timestamp}"
    backup_file_path = os.path.join(BACKUP_DIR, backup_filename_base)

    try:
        if format_type == 'zip':
            backup_content_dir = os.path.join(BACKUP_DIR, f"backup_content_{uuid.uuid4()}")
            os.makedirs(backup_content_dir, exist_ok=True)

            try:
                # Backup database
                db_backup_path, db_metadata = backup_database_with_sqlalchemy(backup_content_dir)
                print(f"Database backed up successfully: {db_backup_path}")

                # Create metadata
                metadata = {
                    "backup_created": datetime.now().isoformat(),
                    "backup_type": "BigCapitalPy Full Backup",
                    "format": format_type,
                    "include_attachments": include_attachments,
                    "database_info": db_metadata,
                    "sqlalchemy_available": SQLALCHEMY_AVAILABLE,
                    "backup_version": "2.0"
                }
                
                # Add SQLAlchemy URI if available
                try:
                    metadata["sqlalchemy_uri"] = current_app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')
                except:
                    metadata["sqlalchemy_uri"] = "Not available (no app context)"
                
                with open(os.path.join(backup_content_dir, "backup_metadata.json"), "w") as f:
                    json.dump(metadata, f, indent=2, default=str)

                # Include attachments if requested
                if include_attachments:
                    attachments_dir = os.path.join(backup_content_dir, "attachments")
                    os.makedirs(attachments_dir, exist_ok=True)
                    
                    # Common attachment directories
                    possible_attachment_dirs = [
                        os.path.join(os.getcwd(), 'uploads'),
                        os.path.join(os.getcwd(), 'static', 'uploads'),
                        os.path.join(os.getcwd(), 'attachments'),
                        os.path.join(os.getcwd(), 'user_files')
                    ]
                    
                    # Add Flask-specific directories if available
                    try:
                        possible_attachment_dirs.extend([
                            os.path.join(current_app.root_path, 'uploads'),
                            os.path.join(current_app.root_path, 'static', 'uploads'),
                            os.path.join(current_app.root_path, 'attachments'),
                            os.path.join(current_app.root_path, 'user_files')
                        ])
                        if hasattr(current_app, 'instance_path'):
                            possible_attachment_dirs.append(os.path.join(current_app.instance_path, 'uploads'))
                    except:
                        pass  # current_app not available
                    
                    attachments_found = False
                    attachment_summary = []
                    
                    for source_dir in possible_attachment_dirs:
                        if os.path.exists(source_dir) and os.path.isdir(source_dir):
                            dest_subdir = os.path.join(attachments_dir, os.path.basename(source_dir))
                            shutil.copytree(source_dir, dest_subdir, dirs_exist_ok=True)
                            
                            file_count = sum([len(files) for r, d, files in os.walk(dest_subdir)])
                            attachment_summary.append({
                                "source": source_dir,
                                "destination": os.path.basename(source_dir),
                                "files_copied": file_count
                            })
                            attachments_found = True
                            print(f"Copied {file_count} files from: {source_dir}")
                    
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

                # Update metadata file
                with open(os.path.join(backup_content_dir, "backup_metadata.json"), "w") as f:
                    json.dump(metadata, f, indent=2, default=str)

                # Create ZIP archive
                final_zip_path = shutil.make_archive(backup_file_path, 'zip', root_dir=backup_content_dir)
                
                # Cleanup
                shutil.rmtree(backup_content_dir)
                return final_zip_path

            except Exception as e:
                if os.path.exists(backup_content_dir):
                    shutil.rmtree(backup_content_dir)
                raise e

        elif format_type == 'json':
            final_json_path = f"{backup_file_path}.json"
            
            backup_data = {
                "backup_created": datetime.now().isoformat(),
                "backup_type": "BigCapitalPy JSON Export",
                "format": format_type,
                "include_attachments": include_attachments,
                "sqlalchemy_available": SQLALCHEMY_AVAILABLE,
                "database_export": export_database_to_json()
            }
            
            try:
                backup_data["sqlalchemy_uri"] = current_app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')
            except:
                backup_data["sqlalchemy_uri"] = "Not available (no app context)"

            with open(final_json_path, "w") as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            return final_json_path

        else:  # Text format fallback
            final_txt_path = f"{backup_file_path}.txt"
            
            with open(final_txt_path, "w") as f:
                f.write("=== BIGCAPITALPY BACKUP SUMMARY ===\n")
                f.write(f"Backup created at: {datetime.now()}\n")
                f.write(f"Format: {format_type}\n")
                f.write(f"Include attachments: {include_attachments}\n")
                f.write(f"SQLAlchemy available: {SQLALCHEMY_AVAILABLE}\n")
                
                try:
                    f.write(f"SQLAlchemy URI: {current_app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}\n\n")
                except:
                    f.write("SQLAlchemy URI: Not available (no app context)\n\n")
                
                # Database info
                try:
                    db_path = get_database_path()
                    if os.path.exists(db_path):
                        f.write("=== DATABASE INFO ===\n")
                        f.write(f"Database file: {db_path}\n")
                        f.write(f"Database size: {os.path.getsize(db_path):,} bytes\n")
                        
                        if SQLALCHEMY_AVAILABLE:
                            try:
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
                            except Exception as e:
                                f.write(f"Error reading database with SQLAlchemy: {e}\n")
                        else:
                            f.write("SQLAlchemy not available for detailed database analysis.\n")
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

def create_backup_async(job_id: str, format_type: str, include_attachments: bool, encrypt_gpg: bool, gpg_email: str):
    """
    Asynchronously creates a backup, optionally encrypting it with GPG.
    """
    job = backup_jobs.get(job_id)
    if not job:
        print(f"Job {job_id} not found in async function.")
        return

    original_file_path = None
    encrypted_file_path = None

    try:
        job['status'] = 'Generating backup content...'
        job['progress'] = 10
        time.sleep(1)

        # Generate backup
        original_file_path = generate_backup(format_type=format_type, include_attachments=include_attachments)
        job['file_path'] = original_file_path

        if job.get('cancelled'):
            raise Exception("Backup cancelled during content generation.")

        job['status'] = 'Backup content generated.'
        job['progress'] = 50
        time.sleep(1)

        if encrypt_gpg:
            job['status'] = 'Encrypting backup with GPG...'
            job['progress'] = 70
            
            encrypted_file_path = f"{original_file_path}.gpg"
            
            with open(original_file_path, 'rb') as f:
                encrypt_result = gpg.encrypt_file(f, recipients=[gpg_email], output=encrypted_file_path)

            if not encrypt_result.ok:
                raise Exception(f"GPG encryption failed: {encrypt_result.status} - {encrypt_result.stderr}")
            
            if os.path.exists(original_file_path):
                os.remove(original_file_path)
            
            job['encrypted_file_path'] = encrypted_file_path
            job['status'] = 'Backup encrypted successfully.'
            job['progress'] = 90
            time.sleep(1)

        job['status'] = 'Backup process completed.'
        job['progress'] = 100
        job['completed'] = True
        job['download_url'] = f"/backup/download/{job_id}"

    except Exception as e:
        job['error'] = str(e)
        job['details'] = f"An error occurred during backup: {e}"
        job['completed'] = True
        job['progress'] = 100
        print(f"Error in async backup job {job_id}: {e}")
        
        # Cleanup
        for file_path in [original_file_path, encrypted_file_path]:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as cleanup_e:
                    print(f"Error cleaning up file {file_path}: {cleanup_e}")
    finally:
        if not job['completed']:
            job['completed'] = True
            job['error'] = job.get('error', 'Unknown error completed job.')
            job['progress'] = 100

def cleanup_old_jobs():
    """
    Periodically cleans up old backup jobs and their associated files.
    """
    cutoff = datetime.now().timestamp() - 3600  # 1 hour cutoff
    jobs_to_remove = []
    for job_id, job in backup_jobs.items():
        if job['created_at'].timestamp() < cutoff:
            # Clean up files
            for file_key in ['file_path', 'encrypted_file_path']:
                file_path = job.get(file_key)
                if file_path and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error cleaning up old backup file {file_path}: {e}")
            jobs_to_remove.append(job_id)
    for job_id in jobs_to_remove:
        del backup_jobs[job_id]