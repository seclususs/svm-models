document.addEventListener('DOMContentLoaded', () => {
    const reportData = {
        labels: ['Berawan', 'Hujan', 'Cerah', 'Berkabut'],
        precision: [0.86, 0.85, 0.94, 0.98],
        recall: [0.93, 0.95, 0.83, 0.90],
        f1_score: [0.90, 0.90, 0.88, 0.94]
    };

    const ctx = document.getElementById('classificationChart');
    if (ctx) {
        new Chart(ctx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: reportData.labels,
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
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        suggestedMax: 1.0,
                        title: { display: true, text: 'Score' }
                    }
                },
                plugins: {
                    legend: { position: 'top' },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) { label += ': '; }
                                if (context.parsed.y !== null) {
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
