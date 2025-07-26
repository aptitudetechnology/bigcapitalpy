// GPG Modal JavaScript - gpg-backup-modal.js

class GPGBackupModal {
    constructor() {
        this.modal = document.getElementById('gpgConfirmationModal');
        this.backupForm = document.querySelector('form[action="/backup/create"]');
        this.encryptCheckbox = document.getElementById('encryptWithGPG');
        this.gpgEmailInput = document.getElementById('gpgEmail');
        
        // Modal elements
        this.keySetupStep = document.getElementById('keySetupStep');
        this.backupProgressStep = document.getElementById('backupProgressStep');
        this.successStep = document.getElementById('successStep');
        this.errorStep = document.getElementById('errorStep');
        
        // Status displays
        this.gpgEmailDisplay = document.getElementById('gpgEmailDisplay');
        this.keySetupStatus = document.getElementById('keySetupStatus');
        this.backupStatusMessage = document.getElementById('backupStatusMessage');
        this.progressBar = document.getElementById('progressBar');
        this.progressPercentage = document.getElementById('progressPercentage');
        this.progressLabel = document.getElementById('progressLabel');
        this.footerHelpText = document.getElementById('footerHelpText');
        
        // Buttons
        this.proceedButton = document.getElementById('proceedButton');
        this.cancelButton = document.getElementById('cancelButton');
        this.downloadButton = document.getElementById('downloadButton');
        this.showErrorDetailsButton = document.getElementById('showErrorDetails');
        
        // Error elements
        this.errorMessage = document.getElementById('errorMessage');
        this.errorDetails = document.getElementById('errorDetails');
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        // Intercept form submission when GPG is enabled
        this.backupForm?.addEventListener('submit', (e) => {
            if (this.encryptCheckbox?.checked) {
                e.preventDefault();
                this.showModal();
            }
        });
        
        // Proceed button click
        this.proceedButton?.addEventListener('click', () => {
            this.startBackupProcess();
        });
        
        // Download button click
        this.downloadButton?.addEventListener('click', () => {
            this.downloadBackup();
        });
        
        // Show error details toggle
        this.showErrorDetailsButton?.addEventListener('click', () => {
            this.toggleErrorDetails();
        });
    }
    
    showModal() {
        this.resetModalState();
        this.updateEmailDisplay();
        
        const modal = new bootstrap.Modal(this.modal);
        modal.show();
        
        this.setupEncryption();
    }
    
    resetModalState() {
        // Show only the setup step
        this.keySetupStep.style.display = 'block';
        this.backupProgressStep.style.display = 'none';
        this.successStep.style.display = 'none';
        this.errorStep.style.display = 'none';
        
        // Reset buttons
        this.proceedButton.disabled = true;
        this.proceedButton.style.display = 'inline-block';
        this.downloadButton.style.display = 'none';
        this.cancelButton.textContent = 'Cancel';
        
        // Reset progress
        this.progressBar.style.width = '0%';
        this.progressPercentage.textContent = '0%';
        this.progressLabel.textContent = 'Creating backup...';
        
        // Reset footer text
        this.footerHelpText.textContent = 'Only you will be able to decrypt this backup';
        
        // Reset status message
        this.keySetupStatus.innerHTML = `
            <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <span class="text-muted">Setting up encryption...</span>
        `;
        
        // Hide error details
        this.errorDetails.style.display = 'none';
    }
    
    updateEmailDisplay() {
        const email = this.gpgEmailInput?.value || 'Not specified';
        this.gpgEmailDisplay.textContent = email;
    }
    
    async setupEncryption() {
        try {
            // Make API call to setup GPG encryption
            const response = await this.makeAPICall('/api/gpg/setup', {
                email: this.gpgEmailInput?.value,
                action: 'import_key'
            });
            
            if (response.success) {
                this.showSetupSuccess();
            } else {
                this.showError(response.error || 'Failed to setup encryption');
            }
        } catch (error) {
            this.showError('Unable to connect to server. Please check your connection.');
        }
    }
    
    showSetupSuccess() {
        this.keySetupStatus.innerHTML = `
            <i class="bi bi-check-circle text-success me-2"></i>
            <span class="text-success">Ready to create encrypted backup</span>
        `;
        
        this.proceedButton.disabled = false;
    }
    
    async startBackupProcess() {
        this.backupProgressStep.style.display = 'block';
        this.proceedButton.style.display = 'none';
        this.footerHelpText.textContent = 'Creating your secure backup...';
        
        try {
            // Get form data
            const formData = new FormData(this.backupForm);
            
            // Make API call to create encrypted backup
            const response = await this.makeAPICallWithProgress('/api/backup/create-encrypted', formData);
            
            if (response.success) {
                this.showBackupComplete(response.download_url);
            } else {
                this.showError(response.error || 'Failed to create backup');
            }
        } catch (error) {
            this.showError('Unable to create backup. Please try again.');
        }
    }
    
    async makeAPICallWithProgress(url, data) {
        // Simulate progress for now - replace with actual implementation
        return new Promise((resolve) => {
            let progress = 0;
            const messages = [
                'Collecting backup data...',
                'Compressing files...',
                'Encrypting with your public key...',
                'Finalizing secure backup...'
            ];
            let messageIndex = 0;
            
            const interval = setInterval(() => {
                progress += Math.random() * 15 + 5;
                if (progress > 100) progress = 100;
                
                this.updateProgress(progress, messages[messageIndex]);
                
                // Update message
                if (messageIndex < messages.length - 1 && progress > (messageIndex + 1) * 25) {
                    messageIndex++;
                }
                
                if (progress >= 100) {
                    clearInterval(interval);
                    resolve({ 
                        success: true, 
                        download_url: '/api/backup/download/encrypted_backup_' + Date.now() + '.gpg'
                    });
                }
            }, 200);
        });
    }
    
    updateProgress(percentage, message) {
        this.progressBar.style.width = percentage + '%';
        this.progressPercentage.textContent = Math.round(percentage) + '%';
        
        if (message) {
            this.backupStatusMessage.innerHTML = `
                <div class="spinner-border spinner-border-sm text-success me-2" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <span class="text-muted">${message}</span>
            `;
        }
        
        if (percentage >= 100) {
            this.backupStatusMessage.innerHTML = `
                <i class="bi bi-check-circle text-success me-2"></i>
                <span class="text-success">Backup encrypted successfully!</span>
            `;
        }
    }
    
    showBackupComplete(downloadUrl) {
        this.successStep.style.display = 'block';
        this.downloadButton.style.display = 'inline-block';
        this.downloadButton.setAttribute('data-download-url', downloadUrl);
        this.cancelButton.textContent = 'Close';
        this.footerHelpText.textContent = 'Your encrypted backup is ready for download';
    }
    
    showError(message, technicalDetails = null) {
        this.errorStep.style.display = 'block';
        this.errorMessage.textContent = message;
        this.cancelButton.textContent = 'Close';
        this.footerHelpText.textContent = 'Please try again or contact support if the problem persists';
        
        if (technicalDetails) {
            this.errorDetails.innerHTML = `<pre class="small">${technicalDetails}</pre>`;
            this.showErrorDetailsButton.style.display = 'inline-block';
        } else {
            this.showErrorDetailsButton.style.display = 'none';
        }
    }
    
    toggleErrorDetails() {
        const isVisible = this.errorDetails.style.display === 'block';
        this.errorDetails.style.display = isVisible ? 'none' : 'block';
        this.showErrorDetailsButton.textContent = isVisible ? 'Show technical details' : 'Hide technical details';
    }
    
    downloadBackup() {
        const downloadUrl = this.downloadButton.getAttribute('data-download-url');
        if (downloadUrl) {
            // Create download link and trigger
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = '';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            // Close modal
            bootstrap.Modal.getInstance(this.modal).hide();
        }
    }
    
    async makeAPICall(url, data) {
        // Simulate API call for now - replace with actual fetch implementation
        return new Promise((resolve) => {
            setTimeout(() => {
                // Simulate success/failure
                const success = Math.random() > 0.1; // 90% success rate for demo
                resolve({
                    success: success,
                    error: success ? null : 'Public key not found for this email address'
                });
            }, 1500);
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new GPGBackupModal();
});