from flask import Blueprint, render_template, request, jsonify, send_file
from flask_login import login_required, current_user
import subprocess
import os
import json
import threading
import time
import uuid
from datetime import datetime

backup_bp = Blueprint('backup', __name__, url_prefix='/backup')

# In-memory job storage (use Redis or database in production)
backup_jobs = {}

@backup_bp.route('/')
@login_required
def index():
    """Backup & Restore main page"""
    # TODO: Add logic to fetch actual backup history
    return render_template('backup/index.html',
                         last_backup_timestamp=None,
                         previous_backups=None,
                         enable_scheduled_backups=False,
                         user=current_user)


@backup_bp.route('/test', methods=['GET', 'POST'])
@login_required
def test_endpoint():
    """Test endpoint to verify routing works"""
    return jsonify({
        'success': True,
        'message': 'Backup blueprint is working',
        'method': request.method,
        'user': current_user.email if current_user else 'No user'
    })


@backup_bp.route('/gpg/setup', methods=['POST'])
@login_required
def gpg_setup():
    """Validate and import GPG key from Ubuntu keyserver"""
    try:
        # Debug logging
        print(f"Request content type: {request.content_type}")
        print(f"Request data: {request.data}")
        
        data = request.get_json(force=True)
        print(f"Parsed JSON: {data}")
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data received'
            }), 400
        
        email = data.get('email')
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email address is required'
            }), 400
        
        # Check if key already exists locally
        check_result = subprocess.run([
            "gpg", "--list-keys", email
        ], capture_output=True, text=True, timeout=10)
        
        if check_result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'GPG key already available locally'
            })
        
        # Try to import the key directly (non-interactive)
        # This will import the first available key for the email
        import_result = subprocess.run([
            "gpg", 
            "--batch",                           # Non-interactive mode
            "--keyserver", "keyserver.ubuntu.com", 
            "--recv-keys", email
        ], capture_output=True, text=True, timeout=30)
        
        if import_result.returncode != 0:
            # If direct import fails, try searching for key IDs first
            search_result = subprocess.run([
                "gpg", 
                "--batch",                       # Non-interactive mode
                "--keyserver", "keyserver.ubuntu.com",
                "--search-keys", email
            ], capture_output=True, text=True, timeout=30, input="\n")  # Auto-select first key
            
            if search_result.returncode != 0:
                return jsonify({
                    'success': False,
                    'error': 'No GPG key found for this email address',
                    'details': f'Keyserver search failed: {search_result.stderr}'
                })
            
            # Extract key ID from search results and import it
            # This is a fallback - the direct recv-keys should work in most cases
            return jsonify({
                'success': False,
                'error': 'Key found but import failed',
                'details': f'Import failed: {import_result.stderr}'
            })
        
        # Verify the key was imported by listing it
        verify_result = subprocess.run([
            "gpg", "--list-keys", email
        ], capture_output=True, text=True, timeout=10)
        
        if verify_result.returncode != 0:
            return jsonify({
                'success': False,
                'error': 'GPG key import verification failed',
                'details': 'Key was imported but cannot be verified'
            })
        
        return jsonify({
            'success': True,
            'message': 'GPG key imported successfully'
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'GPG operation timed out',
            'details': 'The keyserver request took too long. Please try again.'
        }), 408
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'GPG setup failed',
            'details': str(e)
        }), 500

@backup_bp.route('/create', methods=['POST'])
@login_required
def create_backup():
    """Create backup (async or sync based on request)"""
    try:
        format_type = request.form.get('format', 'zip')
        include_attachments = 'include_attachments' in request.form
        encrypt_gpg = 'encrypt_gpg' in request.form
        gpg_email = request.form.get('gpg_email')
        
        # For GPG backups, use async processing
        if encrypt_gpg and gpg_email:
            job_id = str(uuid.uuid4())
            
            # Initialize job
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
            
            # Start background task
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
            # Synchronous backup for non-GPG
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
    """Get backup progress status"""
    job = backup_jobs.get(job_id)
    
    if not job:
        return jsonify({
            'success': False,
            'error': 'Job not found'
        }), 404
    
    if job.get('error'):
        return jsonify({
            'success': False,
            'error': job['error'],
            'details': job.get('details')
        })
    
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
    """Cancel a backup job"""
    job = backup_jobs.get(job_id)
    
    if not job:
        return jsonify({
            'success': False,
            'error': 'Job not found'
        }), 404
    
    # Mark as cancelled
    job['cancelled'] = True
    job['completed'] = True
    job['error'] = 'Backup cancelled by user'
    
    # Clean up any partial files
    if job.get('file_path') and os.path.exists(job['file_path']):
        try:
            os.remove(job['file_path'])
        except:
            pass
    
    return jsonify({
        'success': True,
        'message': 'Backup cancelled'
    })


@backup_bp.route('/download/<job_id>', methods=['GET'])
@login_required
def download_backup(job_id):
    """Download completed backup"""
    job = backup_jobs.get(job_id)
    
    if not job:
        return jsonify({
            'success': False,
            'error': 'Job not found'
        }), 404
    
    if not job['completed'] or job.get('error'):
        return jsonify({
            'success': False,
            'error': 'Backup not ready or failed'
        }), 400
    
    file_path = job.get('file_path')
    if not file_path or not os.path.exists(file_path):
        return jsonify({
            'success': False,
            'error': 'Backup file not found'
        }), 404
    
    return send_file(file_path, as_attachment=True)


# Cleanup function - you might want to call this periodically
def cleanup_old_jobs():
    """Remove jobs older than 1 hour"""
    cutoff = datetime.now().timestamp() - 3600  # 1 hour ago
    
    jobs_to_remove = []
    for job_id, job in backup_jobs.items():
        if job['created_at'].timestamp() < cutoff:
            # Clean up file if it exists
            if job.get('file_path') and os.path.exists(job['file_path']):
                try:
                    os.remove(job['file_path'])
                except:
                    pass
            jobs_to_remove.append(job_id)
    
    for job_id in jobs_to_remove:
        del backup_jobs[job_id]