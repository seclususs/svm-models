/**
 * @file performance-chart.js
 * @description Skrip ini bertanggung jawab untuk merender grafik batang (bar chart)
 * yang menampilkan metrik performa model (Precision, Recall, F1-Score)
 * menggunakan pustaka Chart.js.
 */

// Menjalankan skrip setelah seluruh konten DOM selesai dimuat.
document.addEventListener('DOMContentLoaded', () => {
    // Data statis untuk laporan klasifikasi.
    // Dalam aplikasi nyata, data ini bisa diambil dari API.
    const reportData = {
        labels: ['Berawan', 'Hujan', 'Cerah', 'Berkabut'],
        precision: [0.86, 0.85, 0.94, 0.98],
        recall: [0.93, 0.95, 0.83, 0.90],
        f1_score: [0.90, 0.90, 0.88, 0.94]
    };

    // Mengambil elemen canvas dari DOM.
    const ctx = document.getElementById('classificationChart');
    
    // Memeriksa apakah elemen canvas ada sebelum mencoba membuat grafik.
    if (ctx) {
        // Membuat instance Chart baru.
        new Chart(ctx.getContext('2d'), {
            type: 'bar', // Jenis grafik adalah 'bar'.
            data: {
                labels: reportData.labels, // Label untuk sumbu X (kategori cuaca).
                datasets: [{
                    label: 'Precision',
                    data: reportData.precision,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }, {
                    label: 'Recall',
                    data: reportData.recall,
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }, {
                    label: 'F1-Score',
                    data: reportData.f1_score,
                    backgroundColor: 'rgba(255, 159, 64, 0.6)',
                    borderColor: 'rgba(255, 159, 64, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true, // Membuat grafik responsif terhadap ukuran kontainer.
                maintainAspectRatio: false, // Memungkinkan grafik untuk tidak mempertahankan rasio aspek default.
                scales: {
                    y: {
                        beginAtZero: true, // Memulai sumbu Y dari 0.
                        suggestedMax: 1.0, // Menyarankan nilai maksimum sumbu Y adalah 1.0.
                        title: { display: true, text: 'Score' } // Menampilkan judul pada sumbu Y.
                    }
                },
                plugins: {
                    legend: { position: 'top' }, // Menempatkan legenda di bagian atas.
                    tooltip: {
                        // Kustomisasi format tooltip.
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) { label += ': '; }
                                if (context.parsed.y !== null) {
                                    // Memformat nilai menjadi dua angka desimal.
                                    label += (context.parsed.y).toFixed(2);
                                }
                                return label;
                            }
                        }
                    }
                }
            }
        });
    }
});
