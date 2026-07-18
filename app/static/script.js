const dropArea = document.getElementById("dropArea");
const fileInput = document.getElementById("fileInput");
const fileNameEl = document.getElementById("filename");
const form = document.getElementById('uploadForm');
const divisionSelect = document.getElementById('division');

// --- Drag and Drop Logic (New FE) ---
dropArea.addEventListener("click", () => {
    fileInput.click();
});

fileInput.addEventListener("change", function(){
    if(this.files.length){
        fileNameEl.innerHTML = this.files[0].name;
    }
});

dropArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropArea.style.background = "#252b38";
});

dropArea.addEventListener("dragleave", () => {
    dropArea.style.background = "#1a1d24";
});

dropArea.addEventListener("drop", (e) => {
    e.preventDefault();
    dropArea.style.background = "#1a1d24";
    const files = e.dataTransfer.files;
    fileInput.files = files;
    if(files.length){
        fileNameEl.innerHTML = files[0].name;
    }
});

// --- Upload Logic (Original FE) ---
form.addEventListener('submit', function (e) {
    e.preventDefault();

    if (!divisionSelect.value) {
        alert('Silakan pilih divisi terlebih dahulu.');
        divisionSelect.focus();
        return;
    }

    if (!fileInput.files[0]) {
        alert('Silakan pilih file terlebih dahulu.');
        return;
    }

    const formData = new FormData(form);
    
    // Visual feedback for buttons
    const submitBtn = e.submitter || document.activeElement;
    if (submitBtn && submitBtn.classList.contains('btn')) {
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Uploading...';

        fetch('/damaskus', {
            method: 'POST',
            body: formData
        })
        .then((response) => response.json())
        .then((data) => {
            alert(data.message);
            if (data.status === 'success') {
                form.reset();
                fileNameEl.innerHTML = 'or click to browse';
            }
        })
        .catch(() => {
            alert('Terjadi kesalahan jaringan');
        })
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        });
    } else {
        // Fallback if submitter is not found
        fetch('/damaskus', {
            method: 'POST',
            body: formData
        })
        .then((response) => response.json())
        .then((data) => {
            alert(data.message);
            if (data.status === 'success') {
                form.reset();
                fileNameEl.innerHTML = 'or click to browse';
            }
        })
        .catch(() => {
            alert('Terjadi kesalahan jaringan');
        });
    }
});
