/**
 * @file main-upload.js
 * @description Skrip ini menangani interaksi pengguna pada halaman utama,
 * terutama untuk fungsionalitas pengunggahan berkas. Ini mencakup
 * pembaruan tampilan saat berkas dipilih, penanganan seret dan lepas (drag and drop),
 * dan menampilkan indikator pemuatan saat formulir dikirim.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Mengambil elemen-elemen DOM yang diperlukan.
    const form = document.getElementById('prediction-form');
    const fileInput = document.getElementById('files');
    const fileDropArea = document.querySelector('.file-drop-area');
    const fileNamePreview = document.getElementById('file-name-preview');
    const uploadCard = document.getElementById('upload-card');
    const loadingSpinner = document.getElementById('loading-spinner');
    const submitBtn = document.getElementById('submit-btn');

    /**
     * @function updateFileDisplay
     * @description Memperbarui antarmuka pengguna (UI) berdasarkan berkas yang dipilih.
     * Ini menampilkan nama berkas atau jumlah berkas, mengaktifkan tombol kirim,
     * dan mengubah gaya area 'drop'.
     */
    const updateFileDisplay = () => {
        const files = fileInput.files;
        if (files.length > 0) {
            if (files.length === 1) {
                // Kasus jika hanya satu berkas yang dipilih.
                fileNamePreview.innerHTML = `✓ File: <strong>${files[0].name}</strong>`;
                submitBtn.textContent = 'Analisis Cuaca';
            } else {
                // Kasus jika beberapa berkas dipilih.
                fileNamePreview.innerHTML = `✓ <strong>${files.length}</strong> file dipilih.`;
                submitBtn.textContent = `Analisis ${files.length} Gambar`;
            }
            fileDropArea.classList.add('has-file'); // Menambahkan kelas untuk menandai ada berkas.
            submitBtn.disabled = false; // Mengaktifkan tombol kirim.
        } else {
            // Mengatur ulang UI jika tidak ada berkas yang dipilih.
            fileNamePreview.textContent = '';
            fileDropArea.classList.remove('has-file');
            submitBtn.disabled = true; // Menonaktifkan tombol kirim.
            submitBtn.textContent = 'Analisis Cuaca';
        }
    };

    // Menambahkan event listener untuk input berkas.
    fileInput.addEventListener('change', updateFileDisplay);

    // Mencegah perilaku default browser untuk event drag and drop.
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        fileDropArea.addEventListener(eventName, e => {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });

    // Menambahkan/menghapus kelas 'is-dragging' untuk umpan balik visual saat berkas diseret di atas area.
    ['dragenter', 'dragover'].forEach(eventName => {
        fileDropArea.addEventListener(eventName, () => fileDropArea.classList.add('is-dragging'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        fileDropArea.addEventListener(eventName, () => fileDropArea.classList.remove('is-dragging'), false);
    });

    // Menangani event 'drop' untuk menetapkan berkas yang dilepas ke input berkas.
    fileDropArea.addEventListener('drop', e => {
        fileInput.files = e.dataTransfer.files;
        updateFileDisplay(); // Memperbarui tampilan setelah berkas dilepas.
    }, false);

    // Menangani event pengiriman formulir.
    form.addEventListener('submit', () => {
        // Jika formulir valid, sembunyikan kartu unggah dan tampilkan spinner pemuatan.
        if (form.checkValidity()) {
            uploadCard.style.display = 'none';
            loadingSpinner.style.display = 'block';
        }
    });
});
