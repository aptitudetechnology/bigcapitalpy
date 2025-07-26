from flask import request, send_file
import gnupg
import os

@app.route('/backup/create', methods=['POST'])
def create_backup():
    format = request.form.get('format', 'zip')
    include_attachments = 'include_attachments' in request.form
    encrypt_gpg = 'encrypt_gpg' in request.form
    gpg_email = request.form.get('gpg_email')
    
    backup_path = generate_backup(format=format, include_attachments=include_attachments)
    
    if encrypt_gpg and gpg_email:
        # Initialize GPG
        gpg = gnupg.GPG()
        
        # Import key from keyserver
        import_result = gpg.recv_keys('keyserver.ubuntu.com', gpg_email)
        
        # Read the backup file
        with open(backup_path, 'rb') as f:
            backup_data = f.read()
        
        # Encrypt the data
        encrypted_data = gpg.encrypt(backup_data, gpg_email)
        
        if encrypted_data.ok:
            encrypted_path = f"{backup_path}.gpg"
            
            # Write encrypted data to file
            with open(encrypted_path, 'wb') as f:
                f.write(str(encrypted_data).encode())
            
            # Remove original backup file
            os.remove(backup_path)
            
            return send_file(encrypted_path, as_attachment=True)
        else:
            # Handle encryption failure
            raise Exception(f"GPG encryption failed: {encrypted_data.stderr}")
    
    return send_file(backup_path, as_attachment=True)