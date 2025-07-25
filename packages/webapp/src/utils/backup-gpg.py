from flask import request, send_file
import subprocess
import os

@app.route('/backup/create', methods=['POST'])
def create_backup():
    format = request.form.get('format', 'zip')
    include_attachments = 'include_attachments' in request.form
    encrypt_gpg = 'encrypt_gpg' in request.form
    gpg_email = request.form.get('gpg_email')

    backup_path = generate_backup(format=format, include_attachments=include_attachments)

    if encrypt_gpg and gpg_email:
        # Import key from keyserver
        subprocess.run([
            "gpg", "--keyserver", "keyserver.ubuntu.com", "--recv-keys", gpg_email
        ], check=False)

        encrypted_path = f"{backup_path}.gpg"
        subprocess.run([
            "gpg", "--output", encrypted_path,
            "--encrypt", "--recipient", gpg_email, backup_path
        ], check=True)
        os.remove(backup_path)
        return send_file(encrypted_path, as_attachment=True)

    return send_file(backup_path, as_attachment=True)
