// gpg-backup-modal.js
class GPGBackupModal {
    constructor(modalSelector) {
        this.modal = document.querySelector(modalSelector);
        if (!this.modal) {
            console.error("GPG modal element not found.");
            return;
        }

        // Get all the elements
        this.emailDisplay = this.modal.querySelector("#gpgEncryptEmail");
        this.statusLine = this.modal.querySelector("#gpgStatusLine");
        this.backupForm = document.querySelector("#backupForm");
        this.createButton = this.modal.querySelector("#confirmCreateBackupBtn");
        this.cancelButton = this.modal.querySelector("#cancelBackupBtn");
        this.downloadButton = this.modal.querySelector("#downloadBackupBtn");
        this.showErrorDetailsBtn = this.modal.querySelector("#showErrorDetails");
        
        // Step elements
        this.keySetupStep = this.modal.querySelector("#keySetupStep");
        this.backupProgressStep = this.modal.querySelector("#backupProgressStep");
        this.successStep = this.modal.querySelector("#successStep");
        this.errorStep = this.modal.querySelector("#errorStep");
        
        // Progress elements
        this.progressBar = this.modal.querySelector("#progressBar");
        this.progressPercentage = this.modal.querySelector("#progressPercentage");
        this.progressLabel = this.modal.querySelector("#progressLabel");
        this.backupStatusMessage = this.modal.querySelector("#backupStatusMessage");
        
        // Error elements
        this.errorMessage = this.modal.querySelector("#errorMessage");
        this.errorDetails = this.modal.querySelector("#errorDetails");

        // Current backup job ID for polling
        this.currentJobId = null;
        this.progressInterval = null;
        this.downloadUrl = null;

        // Bind methods
        this.handleCreateClick = this.handleCreateClick.bind(this);
        this.handleCancelClick = this.handleCancelClick.bind(this);
        this.handleDownloadClick = this.handleDownloadClick.bind(this);
        this.handleShowErrorDetails = this.handleShowErrorDetails.bind(this);

        // Add event listeners
        this.createButton?.addEventListener("click", this.handleCreateClick);
        this.cancelButton?.addEventListener("click", this.handleCancelClick);
        this.downloadButton?.addEventListener("click", this.handleDownloadClick);
        this.showErrorDetailsBtn?.addEventListener("click", this.handleShowErrorDetails);
    }

    updateEmailDisplay() {
        const emailInput = document.querySelector("#gpgEmail");
        if (emailInput && this.emailDisplay) {
            this.emailDisplay.textContent = emailInput.value;
        }
    }

    resetModalState() {
        // Hide all steps
        this.keySetupStep.style.display = "block";
        this.backupProgressStep.style.display = "none";
        this.successStep.style.display = "none";
        this.errorStep.style.display = "none";

        // Reset buttons
        this.createButton.style.display = "inline-block";
        this.createButton.disabled = true;
        this.downloadButton.style.display = "none";

        // Reset status
        this.statusLine.innerHTML = `
            <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <span class="text-muted">Setting up encryption...</span>
        `;

        // Clear any intervals
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }

        this.currentJobId = null;
        this.downloadUrl = null;
    }

    async setupEncryption() {
        const email = this.emailDisplay.textContent.trim();
        if (!email) {
            this.showError("No email address provided for encryption.");
            return;
        }

        try {
            const response = await fetch('/backup/gpg/setup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email: email })
            });

            const result = await response.json();

            if (result.success) {
                this.statusLine.innerHTML = `
                    <i class="bi bi-check-circle text-success me-2"></i>
                    <span class="text-success">Encryption ready</span>
                `;
                this.createButton.disabled = false;
            } else {
                this.showError(result.error || "Failed to setup GPG encryption", result.details);
            }
        } catch (error) {
            console.error("GPG setup error:", error);
            this.showError("Network error during encryption setup");
        }
    }

    async handleCreateClick() {
        // Transition to progress step
        this.keySetupStep.style.display = "none";
        this.backupProgressStep.style.display = "block";
        this.createButton.style.display = "none";

        // Get form data
        const formData = new FormData(this.backupForm);
        formData.set('encrypt_gpg', 'on');
        formData.set('gpg_email', this.emailDisplay.textContent.trim());

        try {
            const response = await fetch('/backup/create', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                if (result.job_id) {
                    // Async job - start polling
                    this.currentJobId = result.job_id;
                    this.startProgressPolling();
                } else if (result.download_url) {
                    // Immediate completion
                    this.downloadUrl = result.download_url;
                    this.showSuccess();
                }
            } else {
                this.showError(result.error || "Failed to create backup", result.details);
            }
        } catch (error) {
            console.error("Backup creation error:", error);
            this.showError("Network error during backup creation");
        }
    }

    startProgressPolling() {
        if (!this.currentJobId) return;

        this.progressInterval = setInterval(async () => {
            try {
                const response = await fetch(`/backup/progress/${this.currentJobId}`);
                const result = await response.json();

                if (result.success) {
                    this.updateProgress(result.progress);

                    if (result.completed) {
                        clearInterval(this.progressInterval);
                        this.progressInterval = null;

                        if (result.download_url) {
                            this.downloadUrl = result.download_url;
                            this.showSuccess();
                        } else {
                            this.showError("Backup completed but download URL not available");
                        }
                    }
                } else if (result.error) {
                    clearInterval(this.progressInterval);
                    this.progressInterval = null;
                    this.showError(result.error, result.details);
                }
            } catch (error) {
                console.error("Progress polling error:", error);
                // Continue polling unless it's a critical error
            }
        }, 1000); // Poll every second
    }

    updateProgress(progress) {
        const percentage = Math.round(progress.percentage || 0);
        const status = progress.status || "Processing...";

        this.progressBar.style.width = `${percentage}%`;
        this.progressPercentage.textContent = `${percentage}%`;
        this.progressLabel.textContent = progress.label || "Creating backup...";
        
        this.backupStatusMessage.innerHTML = `
            <div class="spinner-border spinner-border-sm text-success me-2" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <span class="text-muted">${status}</span>
        `;
    }

    showSuccess() {
        this.backupProgressStep.style.display = "none";
        this.successStep.style.display = "block";
        this.downloadButton.style.display = "inline-block";
    }

    showError(message, details = null) {
        // Hide other steps
        this.keySetupStep.style.display = "none";
        this.backupProgressStep.style.display = "none";
        this.successStep.style.display = "none";
        
        // Show error step
        this.errorStep.style.display = "block";
        this.errorMessage.textContent = message;
        
        if (details) {
            this.errorDetails.textContent = details;
            this.showErrorDetailsBtn.style.display = "inline-block";
        } else {
            this.showErrorDetailsBtn.style.display = "none";
        }

        // Show cancel button
        this.createButton.style.display = "none";
        this.downloadButton.style.display = "none";
    }

    handleDownloadClick() {
        if (this.downloadUrl) {
            window.location.href = this.downloadUrl;
            // Close modal after download starts
            setTimeout(() => {
                const modalInstance = bootstrap.Modal.getInstance(this.modal);
                modalInstance?.hide();
            }, 1000);
        }
    }

    handleShowErrorDetails() {
        const isVisible = this.errorDetails.style.display !== "none";
        this.errorDetails.style.display = isVisible ? "none" : "block";
        this.showErrorDetailsBtn.textContent = isVisible ? "Show technical details" : "Hide technical details";
    }

    handleCancelClick() {
        // Cancel any ongoing job
        if (this.currentJobId) {
            fetch(`/backup/cancel/${this.currentJobId}`, { method: 'POST' })
                .catch(error => console.error("Cancel request failed:", error));
        }

        const modalInstance = bootstrap.Modal.getInstance(this.modal);
        modalInstance?.hide();
    }

    showModal() {
        if (!this.modal) {
            console.error("Modal element missing in showModal()");
            return;
        }

        this.resetModalState();
        this.updateEmailDisplay();

        const modal = new bootstrap.Modal(this.modal, {
            backdrop: 'static',
            keyboard: false
        });

        modal.show();
        this.setupEncryption();
    }
}

// Initialize when DOM is loaded
window.addEventListener("DOMContentLoaded", () => {
    const gpgModal = new GPGBackupModal("#gpgConfirmationModal");
    const form = document.querySelector("#backupForm");
    const encryptCheckbox = document.querySelector("#encryptBackup");

    if (form && encryptCheckbox) {
        form.addEventListener("submit", (e) => {
            if (encryptCheckbox.checked) {
                e.preventDefault();
                gpgModal.showModal();
            }
        });
    }

    // Make gpgModal globally available for debugging
    window.gpgModal = gpgModal;
});