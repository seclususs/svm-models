document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('prediction-form');
    const fileInput = document.getElementById('files');
    const fileDropArea = document.querySelector('.file-drop-area');
    const fileNamePreview = document.getElementById('file-name-preview');
    const uploadCard = document.getElementById('upload-card');
    const loadingSpinner = document.getElementById('loading-spinner');
    const submitBtn = document.getElementById('submit-btn');

    const updateFileDisplay = () => {
        const files = fileInput.files;
        if (files.length > 0) {
            if (files.length === 1) {
                fileNamePreview.innerHTML = `✓ File: <strong>${files[0].name}</strong>`;
                submitBtn.textContent = 'Analisis Cuaca';
            } else {
                fileNamePreview.innerHTML = `✓ <strong>${files.length}</strong> file dipilih.`;
                submitBtn.textContent = `Analisis ${files.length} Gambar`;
            }
            fileDropArea.classList.add('has-file');
            submitBtn.disabled = false;
        } else {
            fileNamePreview.textContent = '';
            fileDropArea.classList.remove('has-file');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Analisis Cuaca';
        }
    };

    fileInput.addEventListener('change', updateFileDisplay);

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        fileDropArea.addEventListener(eventName, e => {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        fileDropArea.addEventListener(eventName, () => fileDropArea.classList.add('is-dragging'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        fileDropArea.addEventListener(eventName, () => fileDropArea.classList.remove('is-dragging'), false);
    });

    fileDropArea.addEventListener('drop', e => {
        fileInput.files = e.dataTransfer.files;
        updateFileDisplay();
    }, false);

    form.addEventListener('submit', () => {
        if (form.checkValidity()) {
            uploadCard.style.display = 'none';
            loadingSpinner.style.display = 'block';
        }
    });
});
