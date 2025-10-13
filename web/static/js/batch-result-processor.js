/**
 * @file batch-result-processor.js
 * @description Skrip ini bertanggung jawab untuk memproses dan menampilkan hasil klasifikasi
 * untuk beberapa gambar yang diunggah secara bersamaan (mode massal).
 * Skrip akan mengambil data setiap berkas dari atribut data HTML, mengirimkan
 * permintaan ke server untuk setiap berkas, dan kemudian memperbarui antarmuka
 * pengguna (UI) dengan hasil prediksi yang diterima.
 */

// Menjalankan skrip setelah seluruh konten DOM (Document Object Model) selesai dimuat.
document.addEventListener('DOMContentLoaded', () => {
    
    // Mengambil elemen-elemen dan data yang diperlukan dari DOM.
    const resultGrid = document.getElementById('result-grid');
    const batchId = resultGrid.dataset.batchId; // ID unik untuk sesi unggah massal.
    const filesToProcess = JSON.parse(resultGrid.dataset.files); // Daftar berkas yang akan diproses.

    const iconBaseUrl = resultGrid.dataset.iconBaseUrl; // URL dasar untuk ikon cuaca.
    const fallbackIconUrl = `${iconBaseUrl}default.svg`; // URL ikon cadangan jika ikon spesifik tidak ditemukan.

    /**
     * @function processFile
     * @description Mengirim permintaan ke server untuk memproses satu berkas gambar
     * dan memperbarui kartu (card) yang sesuai dengan hasilnya.
     * @param {object} file - Objek yang berisi informasi tentang berkas yang akan diproses.
     */
    const processFile = async (file) => {
        const cardElement = document.getElementById(file.id);
        if (!cardElement) return; // Hentikan jika elemen kartu tidak ditemukan.

        // Elemen-elemen di dalam kartu yang akan dimanipulasi.
        const processingState = cardElement.querySelector('.processing-state');
        const resultState = cardElement.querySelector('.result-state');

        try {
            // Mengirim permintaan POST ke server dengan ID batch dan nama berkas.
            const response = await fetch(resultGrid.dataset.processUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    batch_id: batchId, 
                    filename: file.unique_filename 
                })
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const result = await response.json();
            
            // Mengambil elemen-elemen untuk menampilkan hasil.
            const iconElement = resultState.querySelector('.result-icon');
            const predictionElement = resultState.querySelector('.result-prediction');
            const confidenceElement = resultState.querySelector('.result-confidence');
            const detailsContainer = cardElement.querySelector('.probability-details-container');
            const toggleBtn = cardElement.querySelector('[data-bs-toggle="collapse"]');
            const collapseEl = cardElement.querySelector('.collapse');
            const confidenceWrapper = confidenceElement ? confidenceElement.parentElement : null;

            if (result.is_anomaly) {
                // Menangani kasus anomali (misalnya, gambar tidak valid atau tidak dapat diproses).
                iconElement.src = `${iconBaseUrl}default.svg`;
                predictionElement.textContent = result.prediction;
                predictionElement.classList.add('text-danger');
                if (confidenceWrapper) {
                    confidenceWrapper.innerHTML = `<span class="fw-medium">Tidak terdeteksi.</span>`;
                    confidenceWrapper.classList.remove('text-muted');
                }
                if(detailsContainer) detailsContainer.innerHTML = '';
                if(toggleBtn) toggleBtn.style.display = 'none'; // Sembunyikan tombol rincian.
            } else {
                // Menangani kasus normal di mana prediksi berhasil.
                predictionElement.classList.remove('text-danger');
                iconElement.src = `${iconBaseUrl}${result.icon_name}.svg`;
                iconElement.onerror = () => { iconElement.src = fallbackIconUrl; }; // Atur ikon cadangan jika terjadi kesalahan.
                predictionElement.textContent = result.prediction;
                
                if (confidenceElement) confidenceElement.textContent = `${result.confidence}%`;

                // Mengisi kontainer rincian probabilitas.
                if(detailsContainer) detailsContainer.innerHTML = '';
                if (result.all_confidences && result.all_confidences.length > 0) {
                    result.all_confidences.forEach((prob, index) => {
                        const [className, classConfidence] = prob;
                        const isTop = index === 0; // Tandai probabilitas tertinggi.
                        const itemHtml = `
                            <div class="probability-item">
                                <div class="d-flex justify-content-between mb-1">
                                    <span class="fw-medium small ${isTop ? 'fw-bold' : ''}">${className}</span>
                                    <span class="fw-bold text-muted small ${isTop ? 'prediction-text' : ''}">${classConfidence}%</span>
                                </div>
                                <div class="progress" style="height: ${isTop ? '12px' : '6px'};" role="progressbar">
                                    <div class="progress-bar probability-bar" style="width: ${classConfidence}%; background-color: ${isTop ? 'var(--primary-500)' : 'var(--gray-400)'};"></div>
                                </div>
                            </div>
                        `;
                        detailsContainer.insertAdjacentHTML('beforeend', itemHtml);
                    });
                }
                
                // Menambahkan event listener untuk mengubah teks tombol "Tampilkan/Sembunyikan Rincian".
                if (collapseEl && toggleBtn) {
                    collapseEl.addEventListener('show.bs.collapse', () => toggleBtn.textContent = 'Sembunyikan Rincian');
                    collapseEl.addEventListener('hide.bs.collapse', () => toggleBtn.textContent = 'Tampilkan Rincian');
                }
            }

        } catch (error) {
            // Menangani kesalahan jaringan atau server.
            console.error(`Gagal memproses ${file.unique_filename}:`, error);
            const predictionElement = resultState.querySelector('.result-prediction');
            const confidenceElement = resultState.querySelector('.result-confidence');

            if (predictionElement) predictionElement.textContent = 'Error';
            if (confidenceElement) confidenceElement.textContent = 'N/A';
        } finally {
            // Menyembunyikan status "memproses" dan menampilkan hasil akhir.
            if(processingState) processingState.style.display = 'none';
            if(resultState) resultState.style.display = 'block';
        }
    };

    /**
     * @function processAllFiles
     * @description Memulai proses untuk semua berkas secara paralel dan menunggu
     * semuanya selesai.
     */
    const processAllFiles = () => {
        const allPromises = filesToProcess.map(file => processFile(file));
        Promise.all(allPromises).then(() => {
            // Memperbarui teks status setelah semua proses selesai.
            document.getElementById('status-text').textContent = 'Semua gambar telah selesai diproses.';
        });
    };

    // Memulai pemrosesan semua berkas.
    processAllFiles();
});
