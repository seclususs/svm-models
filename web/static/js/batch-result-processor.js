document.addEventListener('DOMContentLoaded', () => {
    const resultGrid = document.getElementById('result-grid');
    const batchId = resultGrid.dataset.batchId;
    const filesToProcess = JSON.parse(resultGrid.dataset.files);

    const iconBaseUrl = resultGrid.dataset.iconBaseUrl;
    const fallbackIconUrl = `${iconBaseUrl}default.svg`;

    const processFile = async (file) => {
        const cardElement = document.getElementById(file.id);
        if (!cardElement) return;

        const processingState = cardElement.querySelector('.processing-state');
        const resultState = cardElement.querySelector('.result-state');

        try {
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
            
            const iconElement = resultState.querySelector('.result-icon');
            iconElement.src = `${iconBaseUrl}${result.icon_name}.svg`;
            iconElement.onerror = () => { iconElement.src = fallbackIconUrl; };
            resultState.querySelector('.result-prediction').textContent = result.prediction;
            resultState.querySelector('.result-confidence').textContent = `${result.confidence}%`;

            const detailsContainer = cardElement.querySelector('.probability-details-container');
            detailsContainer.innerHTML = '';
            if (result.all_confidences && result.all_confidences.length > 0) {
                result.all_confidences.forEach((prob, index) => {
                    const [className, classConfidence] = prob;
                    const isTop = index === 0;
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

            const collapseEl = cardElement.querySelector('.collapse');
            const toggleBtn = cardElement.querySelector('[data-bs-toggle="collapse"]');
            if (collapseEl && toggleBtn) {
                collapseEl.addEventListener('show.bs.collapse', () => {
                    toggleBtn.textContent = 'Sembunyikan Rincian';
                });
                collapseEl.addEventListener('hide.bs.collapse', () => {
                    toggleBtn.textContent = 'Tampilkan Rincian';
                });
            }

        } catch (error) {
            console.error(`Gagal memproses ${file.unique_filename}:`, error);
            resultState.querySelector('.result-prediction').textContent = 'Error';
            resultState.querySelector('.result-confidence').textContent = 'N/A';
        } finally {
            if(processingState) processingState.style.display = 'none';
            if(resultState) resultState.style.display = 'block';
        }
    };

    const processAllFiles = () => {
        const allPromises = filesToProcess.map(file => processFile(file));
        Promise.all(allPromises).then(() => {
            document.getElementById('status-text').textContent = 'Semua gambar telah selesai diproses.';
        });
    };

    processAllFiles();
});
