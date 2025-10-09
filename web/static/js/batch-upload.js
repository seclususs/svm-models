document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('prediction-form');
    const fileInput = document.getElementById('files');
    const fileDropArea = document.querySelector('.file-drop-area');
    const fileNamePreview = document.getElementById('file-name-preview');
    const uploadCard = document.getElementById('upload-card');
    const loadingSpinner = document.getElementById('loading-spinner');
    const submitBtn = document.getElementById('submit-btn');

    const updateFileName = () => {
        const files = fileInput.files;
        if (files.length > 0) {
            fileNamePreview.innerHTML = `✓ ${files.length} file dipilih.`;
            fileDropArea.classList.add('has-file');
            submitBtn.disabled = false;
            submitBtn.textContent = `Klasifikasi ${files.length} Gambar`;
        } else {
            fileNamePreview.textContent = '';
            fileDropArea.classList.remove('has-file');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Klasifikasi Gambar';
        }
    };

    fileInput.addEventListener('change', updateFileName);

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
        updateFileName();
    }, false);

    form.addEventListener('submit', () => {
        if(form.checkValidity()){
            uploadCard.style.display = 'none';
            loadingSpinner.style.display = 'block';
        }
    });
});
