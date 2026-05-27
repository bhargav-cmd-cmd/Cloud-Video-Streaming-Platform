document.addEventListener('DOMContentLoaded', () => {
    // 1. Auto-fade Flash Alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.add('fade');
            setTimeout(() => {
                alert.remove();
            }, 150);
        }, 5000);
    });

    // 2. Drag & Drop + Upload Progress Handler (Upload Page)
    const dropzone = document.getElementById('upload-dropzone');
    const fileInput = document.getElementById('video-file');
    const fileInfo = document.getElementById('file-info-text');
    const uploadForm = document.getElementById('upload-form');
    const progressContainer = document.getElementById('progress-container');
    const progressBarFill = document.getElementById('progress-bar-fill');
    const progressPercentText = document.getElementById('progress-percent');

    if (dropzone && fileInput) {
        // Trigger file input click when clicking dropzone
        dropzone.addEventListener('click', () => fileInput.click());

        // Highlight dropzone on dragover
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.style.borderColor = '#8B5CF6';
            dropzone.style.backgroundColor = 'rgba(139, 92, 246, 0.08)';
        });

        // Reset highlights
        ['dragleave', 'dragend'].forEach(type => {
            dropzone.addEventListener(type, () => {
                dropzone.style.borderColor = 'rgba(139, 92, 246, 0.4)';
                dropzone.style.backgroundColor = 'rgba(139, 92, 246, 0.03)';
            });
        });

        // Handle drop event
        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.style.borderColor = 'rgba(139, 92, 246, 0.4)';
            dropzone.style.backgroundColor = 'rgba(139, 92, 246, 0.03)';

            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                updateFileInfo();
            }
        });

        // Update file info on manual selection
        fileInput.addEventListener('change', updateFileInfo);

        function updateFileInfo() {
            if (fileInput.files.length > 0) {
                const file = fileInput.files[0];
                const sizeInMB = (file.size / (1024 * 1024)).toFixed(2);
                fileInfo.textContent = `Selected: ${file.name} (${sizeInMB} MB)`;
                
                // If title is empty, prefill with filename without extension
                const titleInput = document.getElementById('title');
                if (titleInput && !titleInput.value) {
                    const nameWithoutExt = file.name.substring(0, file.name.lastIndexOf('.')) || file.name;
                    titleInput.value = nameWithoutExt.split('_').join(' ').split('-').join(' ');
                }
            } else {
                fileInfo.textContent = 'Drag and drop your video file here or click to browse';
            }
        }
    }

    // Handle AJAX Video Upload Progress
    if (uploadForm) {
        uploadForm.addEventListener('submit', (e) => {
            if (!fileInput.files.length) {
                return; // Let standard HTML5 validation handle missing file
            }
            
            // Prevent normal submission to display progress
            e.preventDefault();
            
            const formData = new FormData(uploadForm);
            const xhr = new XMLHttpRequest();
            
            // Show progress bar
            progressContainer.style.display = 'block';
            
            // XHR Upload progress listener
            xhr.upload.addEventListener('progress', (event) => {
                if (event.lengthComputable) {
                    const percent = Math.round((event.loaded / event.total) * 100);
                    progressBarFill.style.width = `${percent}%`;
                    progressPercentText.textContent = `${percent}%`;
                }
            });
            
            // Upload complete / status listener
            xhr.onreadystatechange = () => {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    // Redirect to dashboard (or wherever the backend points to)
                    // If we want flash messages to persist, we let server redirect us
                    // We can check if the response URL was redirected, or read JSON
                    if (xhr.status >= 200 && xhr.status < 400) {
                        window.location.href = xhr.responseURL || '/dashboard';
                    } else {
                        // Show error alert
                        alert('Upload failed. Please check file format or size.');
                        progressContainer.style.display = 'none';
                        progressBarFill.style.width = '0%';
                        progressPercentText.textContent = '0%';
                    }
                }
            };
            
            xhr.open('POST', uploadForm.action, true);
            xhr.send(formData);
        });
    }

    // 3. Watch Page Keyboard Hotkeys for Native HTML5 Player
    const player = document.getElementById('video-player');
    if (player) {
        document.addEventListener('keydown', (e) => {
            // Disable hotkeys if user is focusing on input/textarea fields
            if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA') {
                return;
            }

            switch(e.key.toLowerCase()) {
                case ' ':
                    // Play / Pause
                    e.preventDefault();
                    if (player.paused) {
                        player.play();
                    } else {
                        player.pause();
                    }
                    break;
                case 'm':
                    // Mute / Unmute
                    e.preventDefault();
                    player.muted = !player.muted;
                    break;
                case 'f':
                    // Toggle Fullscreen
                    e.preventDefault();
                    if (!document.fullscreenElement) {
                        player.requestFullscreen().catch(err => {
                            console.error(`Error attempting to enable full-screen mode: ${err.message}`);
                        });
                    } else {
                        document.exitFullscreen();
                    }
                    break;
                case 'arrowleft':
                    // Seek backward 10s
                    e.preventDefault();
                    player.currentTime = Math.max(0, player.currentTime - 10);
                    break;
                case 'arrowright':
                    // Seek forward 10s
                    e.preventDefault();
                    player.currentTime = Math.min(player.duration, player.currentTime + 10);
                    break;
            }
        });
    }

    // 4. Real-time Homepage Client-Side Filter (Optional Progressive Enhancement)
    const homeSearchInput = document.getElementById('home-search');
    if (homeSearchInput) {
        homeSearchInput.addEventListener('input', (e) => {
            const val = e.target.value.toLowerCase().trim();
            const cards = document.querySelectorAll('.video-card-col');
            
            cards.forEach(card => {
                const title = card.querySelector('.video-title-link').textContent.toLowerCase();
                const desc = card.querySelector('.video-uploader').textContent.toLowerCase(); // metadata details
                if (title.includes(val) || desc.includes(val)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

    // 5. Dashboard Edit Modal Event Binding
    const editModal = document.getElementById('editVideoModal');
    if (editModal) {
        editModal.addEventListener('show.bs.modal', (event) => {
            const button = event.relatedTarget;
            
            // Extract info from data-* attributes
            const videoId = button.getAttribute('data-video-id');
            const videoTitle = button.getAttribute('data-video-title');
            const videoDesc = button.getAttribute('data-video-description');
            
            // Update the modal's content.
            const form = editModal.querySelector('#edit-video-form');
            const titleInput = editModal.querySelector('#edit-title');
            const descInput = editModal.querySelector('#edit-description');
            
            form.action = `/video/${videoId}/edit`;
            titleInput.value = videoTitle;
            descInput.value = videoDesc;
        });
    }
});
