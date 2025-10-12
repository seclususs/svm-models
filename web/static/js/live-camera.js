document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');
    const predictionText = document.getElementById('prediction-text');
    const predictionOverlay = document.getElementById('prediction-overlay');
    const statusOverlay = document.getElementById('status-overlay');
    const statusMessage = document.getElementById('status-message');
    const statusSpinner = document.getElementById('status-spinner');
    const startCameraButton = document.getElementById('start-camera-btn');
    
    let modelInterval;

    const initializeCamera = async () => {
        startCameraButton.style.display = 'none';
        statusMessage.textContent = 'Meminta izin kamera...';
        statusSpinner.style.display = 'block';
        
        // Akses kamera pada mobile browser modern WAJIB menggunakan koneksi aman (HTTPS).
        if (!window.isSecureContext) {
            statusSpinner.style.display = 'none';
            statusMessage.innerHTML = '<strong>Akses kamera memerlukan koneksi aman (HTTPS).</strong><br><small>Fitur ini tidak akan berfungsi jika diakses melalui HTTP di perangkat mobile.</small>';
            startCameraButton.style.display = 'block';
            return;
        }

        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            statusSpinner.style.display = 'none';
            statusMessage.innerHTML = '<strong>Browser tidak mendukung akses kamera.</strong><br><small>Silakan gunakan browser modern seperti Chrome atau Firefox di perangkat Anda.</small>';
            startCameraButton.style.display = 'block';
            return;
        }
        
        // Bedakan constraints untuk mobile dan desktop
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

        const constraints = {
            video: {
                // Gunakan kamera belakang untuk mobile, kamera depan (webcam) untuk desktop
                facingMode: isMobile ? 'environment' : 'user', 
                width: { ideal: 1280 },
                height: { ideal: 720 }
            },
            audio: false
        };

        try {
            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            
            if (video.srcObject) {
                video.srcObject.getTracks().forEach(track => track.stop());
            }

            video.srcObject = stream;
            video.style.display = 'block';

            video.onloadedmetadata = () => {
                statusOverlay.style.display = 'none';
                predictionOverlay.style.display = 'flex';
                
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                
                if (modelInterval) clearInterval(modelInterval);
                modelInterval = setInterval(predictFrame, 1000);
            };
            
        } catch (err) {
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

    const predictFrame = async () => {
        if (!video.srcObject || video.paused || video.ended || video.readyState < 2) return;

        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const dataURL = canvas.toDataURL('image/jpeg', 0.8);

        try {
            const response = await fetch(video.dataset.predictUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: dataURL })
            });
            if (response.ok) {
                const result = await response.json();
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
            console.error("Prediction failed:", error);
            predictionText.textContent = 'Prediksi: Gagal Terhubung';
            if (modelInterval) clearInterval(modelInterval);
        }
    };
    
    startCameraButton.addEventListener('click', initializeCamera);
});
