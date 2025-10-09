document.addEventListener('DOMContentLoaded', () => {
    
    document.querySelectorAll('.probability-bar').forEach(bar => {
        const confidenceValue = parseFloat(bar.getAttribute('data-confidence'));
        setTimeout(() => {
            bar.style.width = `${confidenceValue}%`;
        }, 150);
    });

    const topBar = document.getElementById('top-progress-bar');
    if (topBar) {
        const confidence = parseFloat(topBar.getAttribute('data-confidence'));
        if (confidence >= 75) topBar.classList.add('bg-success');
        else if (confidence >= 50) topBar.classList.add('bg-primary');
        else topBar.classList.add('bg-warning');
    }
    
    const collapseEl = document.getElementById('collapseProbabilities');
    const toggleBtn = document.getElementById('toggle-details-btn');
    if (collapseEl && toggleBtn) {
        collapseEl.addEventListener('show.bs.collapse', () => {
            toggleBtn.textContent = 'Sembunyikan Rincian';
        });
        collapseEl.addEventListener('hide.bs.collapse', () => {
            toggleBtn.textContent = 'Tampilkan Rincian';
        });
    }
});
