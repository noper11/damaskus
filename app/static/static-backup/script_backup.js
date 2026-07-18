// --- Mobile sidebar drawer ---
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('sidebarOverlay');
const menuToggle = document.getElementById('menuToggle');

function openSidebar() {
    sidebar.classList.add('open');
    overlay.classList.add('show');
    menuToggle.setAttribute('aria-expanded', 'true');
    const firstLink = sidebar.querySelector('.nav-item');
    if (firstLink) firstLink.focus();
}

function closeSidebar() {
    sidebar.classList.remove('open');
    overlay.classList.remove('show');
    menuToggle.setAttribute('aria-expanded', 'false');
    menuToggle.focus();
}

menuToggle.addEventListener('click', () => {
    sidebar.classList.contains('open') ? closeSidebar() : openSidebar();
});

overlay.addEventListener('click', closeSidebar);

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && sidebar.classList.contains('open')) {
        closeSidebar();
    }
});

// --- File selection, preview, and validation ---
const fileInput = document.getElementById('fileInput');
const dropZone = document.getElementById('dropZone');
const dropZoneText = document.getElementById('dropZoneText');
const fileSelected = document.getElementById('fileSelected');
const fileNameEl = document.getElementById('fileName');
const fileRemove = document.getElementById('fileRemove');
const fileError = document.getElementById('fileError');

const MAX_SIZE_MB = 10;
const ALLOWED_TYPES = ['application/pdf', 'image/jpeg', 'image/png'];

function showFileError(message) {
    fileError.textContent = message;
    fileError.hidden = false;
    dropZone.classList.add('invalid');
}

function clearFileError() {
    fileError.textContent = '';
    fileError.hidden = true;
    dropZone.classList.remove('invalid');
}

function showFilePreview(file) {
    dropZoneText.hidden = true;
    fileSelected.hidden = false;
    fileNameEl.textContent = file.name;
    dropZone.classList.add('has-file');
}

function resetFileInput() {
    fileInput.value = '';
    dropZoneText.hidden = false;
    fileSelected.hidden = true;
    dropZone.classList.remove('has-file');
    clearFileError();
}

fileInput.addEventListener('change', () => {
    clearFileError();
    const file = fileInput.files[0];

    if (!file) {
        resetFileInput();
        return;
    }

    if (!ALLOWED_TYPES.includes(file.type)) {
        fileInput.value = '';
        showFileError('Format tidak didukung. Gunakan PDF, JPG, atau PNG.');
        return;
    }

    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
        fileInput.value = '';
        showFileError(`Ukuran file melebihi ${MAX_SIZE_MB}MB.`);
        return;
    }

    showFilePreview(file);
});

fileRemove.addEventListener('click', () => {
    resetFileInput();
});

// --- Form submission ---
const form = document.getElementById('uploadForm');
const submitBtn = document.getElementById('submitBtn');
const btnText = submitBtn.querySelector('.btn-text');
const btnSpinner = submitBtn.querySelector('.btn-spinner');
const notification = document.getElementById('notification');
const divisionSelect = document.getElementById('division');

function setLoading(isLoading) {
    submitBtn.disabled = isLoading;
    btnSpinner.hidden = !isLoading;
    btnText.textContent = isLoading ? 'Mengunggah...' : 'Upload & Compress';
}

function showNotification(type, message) {
    notification.setAttribute('role', type === 'error' ? 'alert' : 'status');
    notification.textContent = message;
    notification.className = 'notification ' + type + ' show';

    setTimeout(() => {
        notification.className = 'notification ' + type;
    }, 5000);
}

form.addEventListener('submit', function (e) {
    e.preventDefault();

    if (!divisionSelect.value) {
        divisionSelect.focus();
        return;
    }

    if (!fileInput.files[0]) {
        showFileError('Pilih file terlebih dahulu.');
        return;
    }

    const formData = new FormData(form);
    setLoading(true);

    fetch('/damaskus', {
        method: 'POST',
        body: formData
    })
        .then((response) => response.json())
        .then((data) => {
            showNotification(data.status === 'success' ? 'success' : 'error', data.message);
            if (data.status === 'success') {
                form.reset();
                resetFileInput();
            }
        })
        .catch(() => {
            showNotification('error', 'Terjadi kesalahan jaringan');
        })
        .finally(() => {
            setLoading(false);
        });
});
