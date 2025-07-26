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
    return render_template('backup/index.html',
                           last_backup_timestamp=None,
                           previous_backups=None,
                           enable_scheduled_backups=False,
                           user=current_user)

@backup_bp.route('/test', methods=['GET', 'POST'])
@login_required
def test_endpoint():
    return jsonify({
        'success': True,
        'message': 'Backup blueprint is working',
        'method': request.method,
        'user': current_user.email if current_user else 'No user'
    })

@backup_bp.route('/gpg/search', methods=['POST'])
@login_required
def gpg_search():
    try:
        data = request.get_json(force=True)
        email = data.get('email')
        if not email:
            return jsonify({'success': False, 'error': 'Email is required'}), 400

        search_result = subprocess.run([
            "gpg", "--keyserver", "keyserver.ubuntu.com",
            "--with-colons", "--search-keys", email
        ], capture_output=True, text=True, timeout=30)

        if search_result.returncode != 0 or "pub:" not in search_result.stdout:
            return jsonify({
                'success': False,
                'error': 'No GPG keys found',
                'details': search_result.stderr or search_result.stdout
            }), 404

        keys = []
        current_key = None
        for line in search_result.stdout.splitlines():
            parts = line.split(':')
            if line.startswith('pub'):
                current_key = {
                    'key_id': parts[4],
                    'created': parts[5],
                    'uids': []
                }
                keys.append(current_key)
            elif line.startswith('uid') and current_key:
                uid = parts[9]
                current_key['uids'].append(uid)

        return jsonify({'success': True, 'keys': keys})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@backup_bp.route('/gpg/import', methods=['POST'])
@login_required
def gpg_import():
    try:
        data = request.get_json(force=True)
        key_id = data.get('key_id')
        if not key_id:
            return jsonify({'success': False, 'error': 'Key ID is required'}), 400

        import_result = subprocess.run([
            "gpg", "--keyserver", "keyserver.ubuntu.com",
            "--recv-keys", key_id
        ], capture_output=True, text=True, timeout=30)

        if import_result.returncode != 0:
            return jsonify({
                'success': False,
                'error': 'Failed to import key',
                'details': import_result.stderr
            })

        return jsonify({
            'success': True,
            'message': 'Key imported successfully',
            'key_id': key_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@backup_bp.route('/create', methods=['POST'])
@login_required
def create_backup():
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
    job = backup_jobs.get(job_id)
    if not job:
        return jsonify({'success': False, 'error': 'Job not found'}), 404
    job['cancelled'] = True
    job['completed'] = True
    job['error'] = 'Backup cancelled by user'
    if job.get('file_path') and os.path.exists(job['file_path']):
        try:
            os.remove(job['file_path'])
        except:
            pass
    return jsonify({'success': True, 'message': 'Backup cancelled'})

@backup_bp.route('/download/<job_id>', methods=['GET'])
@login_required
def download_backup(job_id):
    job = backup_jobs.get(job_id)
    if not job:
        return jsonify({'success': False, 'error': 'Job not found'}), 404
    if not job['completed'] or job.get('error'):
        return jsonify({'success': False, 'error': 'Backup not ready or failed'}), 400
    file_path = job.get('file_path')
    if not file_path or not os.path.exists(file_path):
        return jsonify({'success': False, 'error': 'Backup file not found'}), 404
    return send_file(file_path, as_attachment=True)

def cleanup_old_jobs():
    cutoff = datetime.now().timestamp() - 3600
    jobs_to_remove = []
    for job_id, job in backup_jobs.items():
        if job['created_at'].timestamp() < cutoff:
            if job.get('file_path') and os.path.exists(job['file_path']):
                try:
                    os.remove(job['file_path'])
                except:
                    pass
            jobs_to_remove.append(job_id)
    for job_id in jobs_to_remove:
        del backup_jobs[job_id]
