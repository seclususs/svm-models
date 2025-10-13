/**
 * @file live-camera.js
 * @description Skrip ini mengelola fungsionalitas deteksi cuaca secara langsung
 * menggunakan kamera perangkat pengguna. Ini mencakup inisialisasi kamera,
 * pengambilan frame video, pengiriman frame ke server untuk prediksi,
 * dan menampilkan hasilnya secara real-time.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Mengambil elemen-elemen DOM yang diperlukan.
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');
    const predictionText = document.getElementById('prediction-text');
    const predictionOverlay = document.getElementById('prediction-overlay');
    const statusOverlay = document.getElementById('status-overlay');
    const statusMessage = document.getElementById('status-message');
    const statusSpinner = document.getElementById('status-spinner');
    const startCameraButton = document.getElementById('start-camera-btn');
    
    let modelInterval; // Variabel untuk menyimpan interval pengiriman frame.

    /**
     * @function initializeCamera
     * @description Meminta akses ke kamera pengguna, menampilkannya di elemen video,
     * dan memulai interval untuk prediksi frame.
     */
    const initializeCamera = async () => {
        startCameraButton.style.display = 'none';
        
        // Memeriksa konteks aman (HTTPS), yang wajib untuk akses kamera di browser modern.
        if (!window.isSecureContext) {
            statusSpinner.style.display = 'none';
            statusMessage.innerHTML = '<strong>Akses kamera memerlukan koneksi aman (HTTPS).</strong><br><small>Fitur ini tidak akan berfungsi jika diakses melalui HTTP di perangkat mobile.</small>';
            startCameraButton.style.display = 'block';
            return;
        }

        // Memeriksa dukungan API mediaDevices.
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            statusSpinner.style.display = 'none';
            statusMessage.innerHTML = '<strong>Browser tidak mendukung akses kamera.</strong><br><small>Silakan gunakan browser modern seperti Chrome atau Firefox di perangkat Anda.</small>';
            startCameraButton.style.display = 'block';
            return;
        }
        
        // Menentukan jenis kamera (belakang untuk mobile, depan untuk desktop).
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

        const constraints = {
            video: {
                facingMode: isMobile ? 'environment' : 'user', 
                width: { ideal: 1280 },
                height: { ideal: 720 }
            },
            audio: false
        };

        try {
            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            
            // Menghentikan stream sebelumnya jika ada.
            if (video.srcObject) {
                video.srcObject.getTracks().forEach(track => track.stop());
            }

            video.srcObject = stream;
            video.style.display = 'block';

            // Setelah metadata video dimuat, mulai prediksi.
            video.onloadedmetadata = () => {
                statusOverlay.style.display = 'none';
                predictionOverlay.style.display = 'flex';
                
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                
                if (modelInterval) clearInterval(modelInterval);
                modelInterval = setInterval(predictFrame, 1000); // Kirim frame setiap 1 detik.
            };
            
        } catch (err) {
            // Menangani berbagai jenis kesalahan yang mungkin terjadi saat mengakses kamera.
            console.error("Error accessing camera:", err);
            statusSpinner.style.display = 'none';
            let errorMessage;
            
            if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                errorMessage = `<strong>Izin kamera ditolak.</strong><br><small>Anda perlu memberikan izin akses kamera di pengaturan browser Anda untuk menggunakan fitur ini.</small>`;
            } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
                errorMessage = `<strong>Tidak ada kamera yang ditemukan.</strong><br><small>Pastikan perangkat Anda memiliki kamera yang sesuai dan tidak sedang digunakan oleh aplikasi lain.</small>`;
            } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
                 errorMessage = `<strong>Kamera sedang digunakan.</strong><br><small>Perangkat kamera Anda mungkin sedang digunakan oleh aplikasi lain. Tutup aplikasi tersebut dan coba lagi.</small>`;
            } else if (err.name === 'OverconstrainedError' || err.name === 'ConstraintNotSatisfiedError') {
                errorMessage = `<strong>Kamera tidak mendukung resolusi yang diminta.</strong><br><small>Gagal memulai kamera dengan resolusi yang diinginkan.</small>`;
            }
            else {
                 errorMessage = `<strong>Gagal mengakses kamera.</strong><br><small>Terjadi kesalahan yang tidak terduga (${err.name}). Coba muat ulang halaman ini.</small>`;
            }
            
            statusMessage.innerHTML = errorMessage;
            startCameraButton.textContent = 'Coba Lagi';
            startCameraButton.style.display = 'block';
        }
    };

    /**
     * @function predictFrame
     * @description Mengambil frame saat ini dari video, mengubahnya menjadi data URL,
     * dan mengirimkannya ke server untuk mendapatkan prediksi.
     */
    const predictFrame = async () => {
        if (!video.srcObject || video.paused || video.ended || video.readyState < 2) return;

        // Menggambar frame video ke canvas dan mengubahnya menjadi format JPEG.
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const dataURL = canvas.toDataURL('image/jpeg', 0.8);

        try {
            // Mengirim data gambar ke endpoint prediksi.
            const response = await fetch(video.dataset.predictUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: dataURL })
            });
            if (response.ok) {
                const result = await response.json();
                // Memperbarui UI berdasarkan hasil prediksi (normal atau anomali).
                if (result.is_anomaly) {
                    predictionText.textContent = `Peringatan: ${result.prediction}`;
                    predictionOverlay.classList.add('bg-danger', 'bg-opacity-75');
                    predictionOverlay.classList.remove('bg-dark', 'bg-opacity-50');
                } else {
                    predictionText.textContent = `Prediksi: ${result.prediction || 'Menganalisis...'}`;
                    predictionOverlay.classList.remove('bg-danger', 'bg-opacity-75');
                    predictionOverlay.classList.add('bg-dark', 'bg-opacity-50');
                }
            } else {
                predictionText.textContent = 'Prediksi: Error Server';
            }
        } catch (error) {
            // Menangani kegagalan koneksi atau prediksi.
            console.error("Prediction failed:", error);
            predictionText.textContent = 'Prediksi: Gagal Terhubung';
            if (modelInterval) clearInterval(modelInterval); // Hentikan prediksi jika gagal terhubung.
        }
    };
    
    // Menambahkan event listener ke tombol untuk memulai kamera.
    startCameraButton.addEventListener('click', initializeCamera);
});
