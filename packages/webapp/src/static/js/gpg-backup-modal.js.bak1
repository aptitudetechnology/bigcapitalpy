// gpg-backup-modal.js

class GPGBackupModal {
  constructor(modalSelector) {
    this.modal = document.querySelector(modalSelector);
    if (!this.modal) {
      console.error("GPG modal element not found.");
      return;
    }

    this.emailDisplay = this.modal.querySelector("#gpgEncryptEmail");
    this.statusLine = this.modal.querySelector("#gpgStatusLine");
    this.backupForm = document.querySelector("#backupForm");
    this.createButton = this.modal.querySelector("#confirmCreateBackupBtn");
    this.cancelButton = this.modal.querySelector("#cancelBackupBtn");

    this.handleCreateClick = this.handleCreateClick.bind(this);
    this.handleCancelClick = this.handleCancelClick.bind(this);

    this.createButton.addEventListener("click", this.handleCreateClick);
    this.cancelButton.addEventListener("click", this.handleCancelClick);
  }

  updateEmailDisplay() {
    const emailInput = document.querySelector("#gpgEmail");
    if (emailInput && this.emailDisplay) {
      this.emailDisplay.textContent = emailInput.value;
    }
  }

  resetModalState() {
    this.statusLine.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Setting up encryption...`;
  }

  setupEncryption() {
    // Simulate async setup delay
    setTimeout(() => {
      this.statusLine.innerHTML = "Ready to encrypt backup.";
      this.createButton.disabled = false;
    }, 1000);
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

  handleCreateClick() {
    this.modal.querySelector("form")?.submit();
  }

  handleCancelClick() {
    const modalInstance = bootstrap.Modal.getInstance(this.modal);
    modalInstance?.hide();
  }
}

// On DOM load
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
});
