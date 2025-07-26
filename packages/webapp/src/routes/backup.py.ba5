from flask import Blueprint, render_template, request, jsonify, send_file
from flask_login import login_required, current_user
import subprocess
import os
import json
import threading
import time
import uuid
from datetime import datetime
import shutil
import gnupg # Import the gnupg library

backup_bp = Blueprint('backup', __name__, url_prefix='/backup')

# Define a temporary directory for backups. In a production environment,
# this should be configurable and secured.
BACKUP_DIR = os.path.join(os.getcwd(), 'backups_temp')
os.makedirs(BACKUP_DIR, exist_ok=True)

# Define a GPG home directory for the application.
# It's good practice to isolate the GPG keyring used by the application
# from the system's default user keyring.
# Ensure this directory is writable by the user running the Flask app.
GPG_HOME = os.path.join(os.getcwd(), '.gnupg_app')
os.makedirs(GPG_HOME, exist_ok=True)

# Initialize the GPG object
# Specify the gnupghome to use the application-specific keyring
gpg = gnupg.GPG(gnupghome=GPG_HOME)
# You might want to set a keyserver here globally if all operations use the same one
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
                           last_backup_timestamp=None, # This would typically come from a database
                           previous_backups=None,      # This would typically come from a database
                           enable_scheduled_backups=False, # This would typically come from user settings
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
        'user': current_user.email if current_user else 'No user'
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

        # Use gpg.search_keys from the python-gnupg library
        # The keyserver is set globally on the gpg object
        search_result = gpg.search_keys(email, keyserver=gpg.keyserver)

        if not search_result:
            return jsonify({
                'success': False,
                'error': 'No GPG keys found for this email.',
                'details': 'Search returned no results.'
            }), 404

        # The search_keys method returns a list of dictionaries, which is already structured.
        # We'll reformat it slightly to match the previous output structure if needed,
        # but gnupg's output is usually more comprehensive.
        keys_list = []
        for key in search_result:
            # 'keyid' is the primary key ID
            # 'date' is the creation date
            # 'uids' is a list of user IDs
            keys_list.append({
                'key_id': key.get('keyid'),
                'created': key.get('date'),
                'uids': key.get('uids', [])
            })

        return jsonify({'success': True, 'keys': keys_list})
    except Exception as e:
        # gnupg library will raise exceptions for underlying GPG errors
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

        # Use gpg.recv_keys from the python-gnupg library
        # The keyserver is set globally on the gpg object
        import_result = gpg.recv_keys(gpg.keyserver, key_id)

        # The recv_keys method returns an object with attributes like 'fingerprints' and 'results'
        # Check if any keys were actually imported
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
            'fingerprints': import_result.fingerprints # Can return fingerprints of imported keys
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@backup_bp.route('/create', methods=['POST'])
@login_required
def create_backup():
    """
    Initiates a backup creation process. If GPG encryption is requested,
    it starts an asynchronous job. Otherwise, it generates and sends the file directly.
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
            # Start the asynchronous backup process in a new thread
            thread = threading.Thread(
                target=create_backup_async,
                args=(job_id, format_type, include_attachments, encrypt_gpg, gpg_email)
            )
            thread.daemon = True # Allow the thread to exit when the main program exits
            thread.start()
            return jsonify({
                'success': True,
                'job_id': job_id,
                'message': 'Backup started'
            })
        else:
            # If no GPG encryption, generate and send the file synchronously
            backup_path = generate_backup(format=format_type, include_attachments=include_attachments)
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
    Cancels an ongoing backup job and attempts to clean up any partial files.
    """
    job = backup_jobs.get(job_id)
    if not job:
        return jsonify({'success': False, 'error': 'Job not found'}), 404
    job['cancelled'] = True # Set a flag to signal the async function to stop
    job['completed'] = True
    job['error'] = 'Backup cancelled by user'
    # Attempt to remove any created files
    if job.get('file_path') and os.path.exists(job['file_path']):
        try:
            os.remove(job['file_path'])
        except Exception as e:
            print(f"Error cleaning up cancelled backup file {job['file_path']}: {e}")
    if job.get('encrypted_file_path') and os.path.exists(job['encrypted_file_path']):
        try:
            os.remove(job['encrypted_file_path'])
        except Exception as e:
            print(f"Error cleaning up cancelled encrypted backup file {job['encrypted_file_path']}: {e}")
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
    # Ensure the job is completed and has no errors before allowing download
    if not job['completed'] or job.get('error'):
        return jsonify({'success': False, 'error': 'Backup not ready or failed'}), 400
    
    # Prioritize the encrypted file if it exists, otherwise the original
    file_path = job.get('encrypted_file_path') or job.get('file_path')
    
    if not file_path or not os.path.exists(file_path):
        return jsonify({'success': False, 'error': 'Backup file not found'}), 404
    
    # Send the file as an attachment
    return send_file(file_path, as_attachment=True)

def generate_backup(format_type: str, include_attachments: bool) -> str:
    """
    Simulates the creation of a backup file.
    In a real application, this would involve:
    1. Exporting database data (e.g., user profiles, notes, etc.).
    2. Copying user-uploaded files/attachments if include_attachments is True.
    3. Compressing these into a single file based on format_type.

    For this example, we'll create a simple text file or a dummy zip file.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename_base = f"user_backup_{timestamp}"
    backup_file_path = os.path.join(BACKUP_DIR, backup_filename_base)

    try:
        if format_type == 'zip':
            # Create a dummy directory to zip
            dummy_content_dir = os.path.join(BACKUP_DIR, f"content_{uuid.uuid4()}")
            os.makedirs(dummy_content_dir, exist_ok=True)

            # Create some dummy files inside the directory
            with open(os.path.join(dummy_content_dir, "data.txt"), "w") as f:
                f.write("This is your backed-up data.\n")
                f.write(f"Backup created at {datetime.now()}\n")
            if include_attachments:
                with open(os.path.join(dummy_content_dir, "attachment_example.pdf"), "w") as f:
                    f.write("This is a dummy attachment.\n")

            # Create the zip archive
            final_zip_path = shutil.make_archive(backup_file_path, 'zip', root_dir=dummy_content_dir)
            
            # Clean up the dummy content directory
            shutil.rmtree(dummy_content_dir)
            return final_zip_path
        else: # Default to plain text for simplicity if not zip
            final_txt_path = f"{backup_file_path}.txt"
            with open(final_txt_path, "w") as f:
                f.write("This is your backed-up data.\n")
                f.write(f"Backup created at {datetime.now()}\n")
                if include_attachments:
                    f.write("Attachments were requested but not included in plain text format.\n")
            return final_txt_path
    except Exception as e:
        print(f"Error generating backup: {e}")
        raise

def create_backup_async(job_id: str, format_type: str, include_attachments: bool, encrypt_gpg: bool, gpg_email: str):
    """
    Asynchronously creates a backup, optionally encrypting it with GPG using python-gnupg.
    Updates the backup_jobs dictionary with progress and status.
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
        time.sleep(1) # Simulate work

        # Step 1: Generate the backup file
        original_file_path = generate_backup(format_type, include_attachments)
        job['file_path'] = original_file_path # Store the path even if not encrypted

        if job.get('cancelled'):
            raise Exception("Backup cancelled during content generation.")

        job['status'] = 'Backup content generated.'
        job['progress'] = 50
        time.sleep(1) # Simulate work

        if encrypt_gpg:
            job['status'] = 'Encrypting backup with GPG...'
            job['progress'] = 70
            
            # Determine the output file path for the encrypted file
            encrypted_file_path = f"{original_file_path}.gpg"
            
            # Open the input file for reading in binary mode
            with open(original_file_path, 'rb') as f:
                # Use gpg.encrypt_file for encryption
                # recipients: a list of recipient email addresses or key IDs
                # output: the path to the output encrypted file
                encrypt_result = gpg.encrypt_file(f, recipients=[gpg_email], output=encrypted_file_path)

            if not encrypt_result.ok:
                raise Exception(
                    f"GPG encryption failed: {encrypt_result.status} - {encrypt_result.stderr}"
                )
            
            # Clean up the unencrypted original file after successful encryption
            if os.path.exists(original_file_path):
                os.remove(original_file_path)
            
            job['encrypted_file_path'] = encrypted_file_path # Store the path to the encrypted file
            job['status'] = 'Backup encrypted successfully.'
            job['progress'] = 90
            time.sleep(1) # Simulate work

        job['status'] = 'Backup process completed.'
        job['progress'] = 100
        job['completed'] = True
        # Set the download URL to point to the correct file (encrypted or original)
        job['download_url'] = f"/backup/download/{job_id}"

    except Exception as e:
        job['error'] = str(e)
        job['details'] = f"An error occurred during backup: {e}"
        job['completed'] = True
        job['progress'] = 100
        print(f"Error in async backup job {job_id}: {e}")
        # Ensure cleanup of any partial files on error
        if original_file_path and os.path.exists(original_file_path):
            try:
                os.remove(original_file_path)
            except Exception as cleanup_e:
                print(f"Error cleaning up original file {original_file_path}: {cleanup_e}")
        if encrypted_file_path and os.path.exists(encrypted_file_path):
            try:
                os.remove(encrypted_file_path)
            except Exception as cleanup_e:
                print(f"Error cleaning up encrypted file {encrypted_file_path}: {cleanup_e}")
    finally:
        # Ensure the job is marked as completed even if there's an unhandled error
        if not job['completed']:
            job['completed'] = True
            job['error'] = job.get('error', 'Unknown error completed job.')
            job['progress'] = 100

def cleanup_old_jobs():
    """
    Periodically cleans up old backup jobs and their associated files.
    This function should ideally be run by a background task scheduler (e.g., Celery, APScheduler).
    """
    cutoff = datetime.now().timestamp() - 3600 # 1 hour cutoff
    jobs_to_remove = []
    for job_id, job in backup_jobs.items():
        if job['created_at'].timestamp() < cutoff:
            # Clean up original file
            if job.get('file_path') and os.path.exists(job['file_path']):
                try:
                    os.remove(job['file_path'])
                except Exception as e:
                    print(f"Error cleaning up old original backup file {job['file_path']}: {e}")
            # Clean up encrypted file
            if job.get('encrypted_file_path') and os.path.exists(job['encrypted_file_path']):
                try:
                    os.remove(job['encrypted_file_path'])
                except Exception as e:
                    print(f"Error cleaning up old encrypted backup file {job['encrypted_file_path']}: {e}")
            jobs_to_remove.append(job_id)
    for job_id in jobs_to_remove:
        del backup_jobs[job_id]

# You might want to run cleanup_old_jobs periodically, e.g., using APScheduler
# For a simple example, it's not explicitly called here, but it's a good practice.
