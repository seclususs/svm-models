/**
 * @file result-animation.js
 * @description Skrip ini menangani animasi dan interaksi pada halaman hasil prediksi.
 * Fungsi utamanya adalah menganimasikan bilah probabilitas (progress bar)
 * dan mengelola teks pada tombol "Tampilkan/Sembunyikan Rincian".
 */

// Menjalankan skrip setelah seluruh konten DOM selesai dimuat.
document.addEventListener('DOMContentLoaded', () => {
    
    // Menganimasikan semua bilah probabilitas.
    document.querySelectorAll('.probability-bar').forEach(bar => {
        // Mengambil nilai keyakinan (confidence) dari atribut data.
        const confidenceValue = parseFloat(bar.getAttribute('data-confidence'));
        
        // Mengatur lebar bilah sesuai dengan nilai keyakinan setelah jeda singkat
        // untuk memastikan transisi CSS dapat berjalan.
        setTimeout(() => {
            bar.style.width = `${confidenceValue}%`;
        }, 150);
    });

    // Mengatur warna bilah probabilitas teratas berdasarkan tingkat keyakinan.
    const topBar = document.getElementById('top-progress-bar');
    if (topBar) {
        const confidence = parseFloat(topBar.getAttribute('data-confidence'));
        if (confidence >= 75) topBar.classList.add('bg-success');      // Hijau untuk keyakinan tinggi.
        else if (confidence >= 50) topBar.classList.add('bg-primary'); // Biru untuk keyakinan sedang.
        else topBar.classList.add('bg-warning');                       // Kuning untuk keyakinan rendah.
    }
    
    // Mengelola perubahan teks pada tombol 'toggle' untuk rincian probabilitas.
    const collapseEl = document.getElementById('collapseProbabilities');
    const toggleBtn = document.getElementById('toggle-details-btn');
    if (collapseEl && toggleBtn) {
        // Saat elemen rincian ditampilkan.
        collapseEl.addEventListener('show.bs.collapse', () => {
            toggleBtn.textContent = 'Sembunyikan Rincian';
        });
        // Saat elemen rincian disembunyikan.
        collapseEl.addEventListener('hide.bs.collapse', () => {
            toggleBtn.textContent = 'Tampilkan Rincian';
        });
    }
});
