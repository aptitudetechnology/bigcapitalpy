let selectedKeyId = null;

export function searchGPGKeys() {
    const emailInput = document.getElementById("gpgEmailInput");
    const resultsContainer = document.getElementById("gpgKeyResults");
    const importBtn = document.getElementById("importKeyBtn");

    const email = emailInput.value.trim();
    if (!email) {
        resultsContainer.innerHTML = `<div class="text-danger">Please enter a valid email address.</div>`;
        return;
    }

    resultsContainer.innerHTML = `<div class="text-muted">Searching for keys...</div>`;
    importBtn.disabled = true;
    selectedKeyId = null;

    fetch("/backup/gpg/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email })
    })
    .then(res => res.json())
    .then(data => {
        if (!data.success || !data.keys.length) {
            resultsContainer.innerHTML = `<div class="text-warning">No GPG keys found for <strong>${email}</strong>.</div>`;
            return;
        }

        // Populate radio options
        resultsContainer.innerHTML = data.keys.map((key, index) => {
            const uidText = key.uids.join(", ");
            return `
                <div class="form-check">
                    <input class="form-check-input" type="radio" name="keySelect" id="keyRadio${index}" value="${key.key_id}" onchange="selectGPGKey('${key.key_id}')">
                    <label class="form-check-label" for="keyRadio${index}">
                        ${key.key_id} – ${uidText}
                    </label>
                </div>
            `;
        }).join("");
    })
    .catch(err => {
        console.error(err);
        resultsContainer.innerHTML = `<div class="text-danger">Search failed. Please try again later.</div>`;
    });
}

export function selectGPGKey(keyId) {
    selectedKeyId = keyId;
    const importBtn = document.getElementById("importKeyBtn");
    importBtn.disabled = false;
}

export function importSelectedGPGKey() {
    if (!selectedKeyId) return;

    const importBtn = document.getElementById("importKeyBtn");
    const emailInput = document.getElementById("gpgEmailInput");
    const resultsContainer = document.getElementById("gpgKeyResults");
    const encryptEmailSpan = document.getElementById("gpgEncryptEmail");
    const encryptEmailHidden = document.getElementById("gpgModalEmail");
    const selectedKeyInfo = document.getElementById("selectedKeyInfo");
    const statusLine = document.getElementById("gpgStatusLine");
    const confirmBackupBtn = document.getElementById("confirmCreateBackupBtn");

    importBtn.disabled = true;
    importBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status"></span>Importing...`;

    fetch("/backup/gpg/import", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key_id: selectedKeyId })
    })
    .then(res => res.json())
    .then(data => {
        if (!data.success) {
            resultsContainer.innerHTML = `<div class="text-danger">Import failed: ${data.error}</div>`;
            return;
        }

        // Success UI update
        encryptEmailSpan.textContent = emailInput.value;
        encryptEmailHidden.value = emailInput.value;

        selectedKeyInfo.style.display = "flex";
        statusLine.style.display = "none";
        importBtn.style.display = "none";
        confirmBackupBtn.disabled = false;
        confirmBackupBtn.style.display = "inline-block";
    })
    .catch(err => {
        console.error(err);
        resultsContainer.innerHTML = `<div class="text-danger">Import request failed. Try again.</div>`;
    })
    .finally(() => {
        importBtn.disabled = true;
        importBtn.innerHTML = `<i class="bi bi-download me-2"></i>Import Selected Key`;
    });
}
