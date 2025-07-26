// gpg-backup-modal.js

// Variable to store the ID of the selected GPG key
let selectedKeyId = null;

/**
 * Searches for GPG keys on a key server based on the provided email.
 * This function is designed to work with a UI that allows email input and displays results.
 * NOTE: The email input and search button were previously removed from the modal HTML.
 * This function remains here for completeness of the original file's logic,
 * but its direct UI trigger might be absent.
 */
export function searchGPGKeys() {
    // Get references to UI elements
    const emailInput = document.getElementById("gpgEmailInput"); // This element might not exist anymore in HTML
    const resultsContainer = document.getElementById("gpgKeyResults");
    const importBtn = document.getElementById("importKeyBtn");

    // Check if emailInput exists before trying to access its value
    const email = emailInput ? emailInput.value.trim() : '';

    // Basic validation for email
    if (!email) {
        if (resultsContainer) {
            resultsContainer.innerHTML = `<div class="text-danger">Please enter a valid email address.</div>`;
        }
        return;
    }

    // Update UI to show searching status
    if (resultsContainer) {
        resultsContainer.innerHTML = `<div class="text-muted">Searching for keys...</div>`;
    }
    if (importBtn) {
        importBtn.disabled = true;
    }
    selectedKeyId = null; // Reset selected key

    // Fetch GPG keys from the backend
    fetch("/backup/gpg/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email })
    })
    .then(res => res.json())
    .then(data => {
        // Handle no keys found or unsuccessful search
        if (!data.success || !data.keys || !data.keys.length) {
            if (resultsContainer) {
                resultsContainer.innerHTML = `<div class="text-warning">No GPG keys found for <strong>${email}</strong>.</div>`;
            }
            return;
        }

        // Populate radio options with found keys
        if (resultsContainer) {
            resultsContainer.innerHTML = data.keys.map((key, index) => {
                const uidText = key.uids ? key.uids.join(", ") : 'No User IDs';
                return `
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="keySelect" id="keyRadio${index}" value="${key.key_id}">
                        <label class="form-check-label" for="keyRadio${index}">
                            ${key.key_id} – ${uidText}
                        </label>
                    </div>
                `;
            }).join("");

            // Add event listener to the results container for radio button changes
            // This is crucial if `onchange` attributes are removed from HTML
            resultsContainer.addEventListener('change', (event) => {
                if (event.target.matches('input[name="keySelect"]')) {
                    selectGPGKey(event.target.value);
                }
            }, { once: true }); // Use once: true if you only expect one selection per search
        }
    })
    .catch(err => {
        // Log and display error if search fails
        console.error("GPG Key search failed:", err);
        if (resultsContainer) {
            resultsContainer.innerHTML = `<div class="text-danger">Search failed. Please try again later.</div>`;
        }
    });
}

/**
 * Sets the globally selected GPG key ID and enables the import button.
 * @param {string} keyId - The ID of the selected GPG key.
 */
export function selectGPGKey(keyId) {
    selectedKeyId = keyId;
    const importBtn = document.getElementById("importKeyBtn");
    if (importBtn) {
        importBtn.disabled = false;
    }
}

/**
 * Imports the currently selected GPG key from the key server via the backend.
 * Updates the UI based on the import success or failure.
 */
export function importSelectedGPGKey() {
    // Ensure a key is selected
    if (!selectedKeyId) {
        console.warn("No GPG key selected for import.");
        return;
    }

    // Get references to UI elements
    const importBtn = document.getElementById("importKeyBtn");
    const emailInput = document.getElementById("gpgEmailInput"); // This element might not exist anymore in HTML
    const resultsContainer = document.getElementById("gpgKeyResults");
    const encryptEmailSpan = document.getElementById("gpgEncryptEmail");
    const encryptEmailHidden = document.getElementById("gpgModalEmail");
    const selectedKeyInfo = document.getElementById("selectedKeyInfo");
    const statusLine = document.getElementById("gpgStatusLine");
    const confirmBackupBtn = document.getElementById("confirmCreateBackupBtn");

    // Disable import button and show loading spinner
    if (importBtn) {
        importBtn.disabled = true;
        importBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status"></span>Importing...`;
    }

    // Fetch call to import the key
    fetch("/backup/gpg/import", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key_id: selectedKeyId })
    })
    .then(res => res.json())
    .then(data => {
        // Handle import failure
        if (!data.success) {
            if (resultsContainer) {
                resultsContainer.innerHTML = `<div class="text-danger">Import failed: ${data.error}</div>`;
            }
            return;
        }

        // --- Success UI update ---
        // Since gpgEmailInput might be removed, we need a fallback for the email displayed.
        // Ideally, the email to encrypt for should be passed from the backend or a global JS variable.
        const encryptionEmail = emailInput ? emailInput.value : (window.GPG_ENCRYPTION_EMAIL || 'unknown@example.com');

        if (encryptEmailSpan) {
            encryptEmailSpan.textContent = encryptionEmail;
        }
        if (encryptEmailHidden) {
            encryptEmailHidden.value = encryptionEmail;
        }

        // Show selected key info and enable backup confirmation
        if (selectedKeyInfo) selectedKeyInfo.style.display = "flex";
        if (statusLine) statusLine.style.display = "none";
        if (importBtn) importBtn.style.display = "none"; // Hide import button after successful import
        if (confirmBackupBtn) {
            confirmBackupBtn.disabled = false;
            confirmBackupBtn.style.display = "inline-block"; // Show and enable confirm backup button
        }
    })
    .catch(err => {
        // Log and display error if import request fails
        console.error("GPG Key import request failed:", err);
        if (resultsContainer) {
            resultsContainer.innerHTML = `<div class="text-danger">Import request failed. Try again.</div>`;
        }
    })
    .finally(() => {
        // Reset import button state in case of error or if it's re-shown
        if (importBtn) {
            importBtn.disabled = true; // Keep disabled until a new key is selected/searched
            importBtn.innerHTML = `<i class="bi bi-download me-2"></i>Import Selected Key`;
        }
    });
}

/**
 * GPGBackupModal class to manage the state and interactions of the GPG encryption modal.
 */
export class GPGBackupModal {
    /**
     * @param {string} modalId - The ID of the main modal HTML element.
     */
    constructor(modalId) {
        this.modalElement = document.getElementById(modalId);
        if (!this.modalElement) {
            console.warn(`GPGBackupModal: Modal element with ID '${modalId}' not found. Using basic modal functions.`);
            // If the modal element isn't found, we can't initialize Bootstrap's modal or manage steps.
            // Further operations will rely on manual DOM manipulation or fail.
            return;
        }
        // Initialize Bootstrap's modal instance
        this.bootstrapModal = new bootstrap.Modal(this.modalElement);

        // Get references to the different step containers within the modal
        this.keySetupStep = document.getElementById('keySetupStep');
        this.backupProgressStep = document.getElementById('backupProgressStep');
        this.successStep = document.getElementById('successStep');
        this.errorStep = document.getElementById('errorStep');

        // Get references to footer buttons
        this.confirmCreateBackupBtn = document.getElementById('confirmCreateBackupBtn');
        this.downloadBackupBtn = document.getElementById('downloadBackupBtn');
        this.cancelBackupBtn = document.getElementById('cancelBackupBtn');

        // Get references to email display elements
        this.gpgEncryptEmailSpan = document.getElementById("gpgEncryptEmail");
        this.gpgModalEmailHidden = document.getElementById("gpgModalEmail");

        // Set initial step to display when modal is first constructed
        this.showStep('keySetup');

        // Attach event listeners to main action buttons in the modal footer
        if (this.confirmCreateBackupBtn) {
            this.confirmCreateBackupBtn.addEventListener('click', () => this.startBackup());
        }
        if (this.downloadBackupBtn) {
            this.downloadBackupBtn.addEventListener('click', () => this.downloadBackup());
        }
        if (this.cancelBackupBtn) {
            this.cancelBackupBtn.addEventListener('click', () => this.hide());
        }
    }

    /**
     * Displays the modal.
     */
    show() {
        if (this.bootstrapModal) {
            this.bootstrapModal.show();
            this.showStep('keySetup'); // Always reset to the initial step when showing the modal
        }
    }

    /**
     * Hides the modal.
     */
    hide() {
        if (this.bootstrapModal) {
            this.bootstrapModal.hide();
        }
    }

    /**
     * Controls which step of the modal is visible.
     * @param {string} stepName - The name of the step to show ('keySetup', 'progress', 'success', 'error').
     */
    showStep(stepName) {
        // Hide all step containers first
        if (this.keySetupStep) this.keySetupStep.style.display = 'none';
        if (this.backupProgressStep) this.backupProgressStep.style.display = 'none';
        if (this.successStep) this.successStep.style.display = 'none';
        if (this.errorStep) this.errorStep.style.display = 'none';

        // Show the requested step and manage button visibility/state
        switch (stepName) {
            case 'keySetup':
                if (this.keySetupStep) this.keySetupStep.style.display = 'block';
                if (this.confirmCreateBackupBtn) this.confirmCreateBackupBtn.style.display = 'none';
                if (this.downloadBackupBtn) this.downloadBackupBtn.style.display = 'none';
                if (this.cancelBackupBtn) this.cancelBackupBtn.style.display = 'inline-block';
                break;
            case 'progress':
                if (this.backupProgressStep) this.backupProgressStep.style.display = 'block';
                if (this.confirmCreateBackupBtn) this.confirmCreateBackupBtn.style.display = 'none';
                if (this.downloadBackupBtn) this.downloadBackupBtn.style.display = 'none';
                if (this.cancelBackupBtn) this.cancelBackupBtn.style.display = 'inline-block';
                break;
            case 'success':
                if (this.successStep) this.successStep.style.display = 'block';
                if (this.confirmCreateBackupBtn) this.confirmCreateBackupBtn.style.display = 'none';
                if (this.downloadBackupBtn) this.downloadBackupBtn.style.display = 'inline-block';
                if (this.cancelBackupBtn) this.cancelBackupBtn.style.display = 'none'; // Cancel button might be hidden on success
                break;
            case 'error':
                if (this.errorStep) this.errorStep.style.display = 'block';
                if (this.confirmCreateBackupBtn) this.confirmCreateBackupBtn.style.display = 'none';
                if (this.downloadBackupBtn) this.downloadBackupBtn.style.display = 'none';
                if (this.cancelBackupBtn) this.cancelBackupBtn.style.display = 'inline-block'; // Or a 'Retry' button
                break;
            default:
                console.warn(`GPGBackupModal: Unknown step name provided: ${stepName}`);
        }
    }

    /**
     * Initiates the encrypted backup process.
     * This will typically involve an AJAX call to your Flask backend.
     */
    startBackup() {
        this.showStep('progress'); // Transition to the progress step
        console.log("Starting encrypted backup process...");

        // Example: Simulate an asynchronous backup process with a timeout
        // In a real application, this would be a fetch() call to your Flask backend
        // that performs the actual backup and encryption.
        setTimeout(() => {
            // After the simulated backup, transition to success or error
            const backupSuccessful = Math.random() > 0.2; // Simulate success/failure
            if (backupSuccessful) {
                this.showStep('success');
                console.log("Backup process completed successfully.");
            } else {
                this.showStep('error');
                // You might want to set an error message here based on backend response
                const errorMessageElement = document.getElementById('errorMessage');
                if (errorMessageElement) {
                    errorMessageElement.textContent = "Backup failed due to a server error. Please try again.";
                }
                console.error("Backup process failed.");
            }
        }, 3000); // Simulate 3 seconds for backup process
    }

    /**
     * Handles the download of the created backup file.
     * This will typically trigger a file download from your Flask backend.
     */
    downloadBackup() {
        console.log("Initiating backup download...");
        // In a real application, this would trigger a file download,
        // e.g., by navigating to a download URL or making a fetch request
        // that returns a blob.
        // Example: window.location.href = '/backup/download';
    }

    /**
     * Sets the email address displayed in the modal for encryption.
     * @param {string} email - The email address to display.
     */
    setEncryptionEmail(email) {
        if (this.gpgEncryptEmailSpan) {
            this.gpgEncryptEmailSpan.textContent = email;
        }
        if (this.gpgModalEmailHidden) {
            this.gpgModalEmailHidden.value = email;
        }
    }
}

// --- Initialization Logic ---
// This part ensures the GPGBackupModal is instantiated and ready when the DOM is loaded.
// It also attaches the event listener for the button that opens the modal.
document.addEventListener('DOMContentLoaded', () => {
    // Instantiate the GPGBackupModal class.
    // Make it globally accessible for easier debugging and interaction from other scripts.
    window.gpgBackupModalInstance = new GPGBackupModal('gpgConfirmationModal');

    // Set the encryption email. This should ideally come from your Flask backend
    // as a Jinja2 variable (e.g., `{{ current_user.email }}`) embedded in a script tag
    // or passed via a data attribute on an element.
    // For demonstration, using a placeholder. Replace 'chris@caston.id.au'
    // with your actual dynamic email source.
    window.gpgBackupModalInstance.setEncryptionEmail('chris@caston.id.au');

    // Attach event listener to the button that opens the GPG backup modal.
    // Replace 'openBackupModalBtn' with the actual ID of your button.
    const openBackupModalButton = document.getElementById('openBackupModalBtn');
    if (openBackupModalButton) {
        openBackupModalButton.addEventListener('click', () => {
            window.gpgBackupModalInstance.show();
        });
    }

    // If you still have an 'Import Selected Key' button and it's not handled by the class,
    // ensure its event listener is attached here.
    const importKeyBtn = document.getElementById('importKeyBtn');
    if (importKeyBtn) {
        // Ensure the button is enabled/disabled based on selectedKeyId
        // This might be managed by the class's showStep or other methods.
        importKeyBtn.addEventListener('click', importSelectedGPGKey);
    }
});
