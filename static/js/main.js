// Main JavaScript for Crowd Management System

document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const videoFeed = document.getElementById('video-feed');
    const noFeedMessage = document.getElementById('no-feed-message');
    const peopleCount = document.getElementById('people-count');
    const alertLevel = document.getElementById('alert-level');
    const fps = document.getElementById('fps');
    const alertMessage = document.getElementById('alert-message');
    const resetBtn = document.getElementById('reset-btn');
    const exportBtn = document.getElementById('export-btn');
    const dataMessage = document.getElementById('data-message');

    // Event listeners
    startBtn.addEventListener('click', startCamera);
    stopBtn.addEventListener('click', stopCamera);
    resetBtn.addEventListener('click', resetDatabase);
    exportBtn.addEventListener('click', exportData);

    // Variables
    let statsInterval = null;

    // Start camera function
    async function startCamera() {
        try {
            const response = await fetch('/start_camera');
            const data = await response.json();
            
            if (data.status === 'success') {
                // Update UI
                startBtn.disabled = true;
                stopBtn.disabled = false;
                
                // Show video feed
                videoFeed.style.display = 'block';
                noFeedMessage.style.display = 'none';
                videoFeed.src = '/video_feed';
                
                // Start stats updates
                if (statsInterval) clearInterval(statsInterval);
                statsInterval = setInterval(updateStats, 1000);
                
                // Update alert message
                alertMessage.textContent = 'Camera started. Detecting crowd...';
                alertMessage.className = 'alert-message';
            } else {
                alertMessage.textContent = `Error: ${data.message}`;
                alertMessage.className = 'alert-message';
            }
        } catch (error) {
            console.error('Error starting camera:', error);
            alertMessage.textContent = 'Error starting camera. Please check console for details.';
            alertMessage.className = 'alert-message';
        }
    }

    // Stop camera function
    async function stopCamera() {
        try {
            const response = await fetch('/stop_camera');
            const data = await response.json();
            
            if (data.status === 'success') {
                // Update UI
                startBtn.disabled = false;
                stopBtn.disabled = true;
                
                // Hide video feed
                videoFeed.style.display = 'none';
                noFeedMessage.style.display = 'block';
                videoFeed.src = '';
                
                // Stop stats updates
                if (statsInterval) {
                    clearInterval(statsInterval);
                    statsInterval = null;
                }
                
                // Reset stats display
                peopleCount.textContent = '0';
                alertLevel.textContent = 'Normal';
                alertLevel.className = 'stat-value alert-normal';
                fps.textContent = '0.00';
                
                // Update alert message
                alertMessage.textContent = 'Camera stopped. System ready.';
                alertMessage.className = 'alert-message';
            } else {
                alertMessage.textContent = `Error: ${data.message}`;
                alertMessage.className = 'alert-message';
            }
        } catch (error) {
            console.error('Error stopping camera:', error);
            alertMessage.textContent = 'Error stopping camera. Please check console for details.';
            alertMessage.className = 'alert-message';
        }
    }

    // Update stats function
    async function updateStats() {
        try {
            const response = await fetch('/stats');
            const stats = await response.json();
            
            // Update people count
            peopleCount.textContent = stats.people_count;
            
            // Update alert level
            updateAlertLevel(stats.alert_level);
            
            // Update FPS
            fps.textContent = stats.fps.toFixed(2);
        } catch (error) {
            console.error('Error updating stats:', error);
        }
    }

    // Update alert level display
    function updateAlertLevel(level) {
        switch(level) {
            case 0:
                alertLevel.textContent = 'Normal';
                alertLevel.className = 'stat-value alert-normal';
                alertMessage.textContent = 'System operating normally.';
                alertMessage.className = 'alert-message';
                break;
            case 1:
                alertLevel.textContent = 'Caution';
                alertLevel.className = 'stat-value alert-caution';
                alertMessage.textContent = 'CAUTION: Moderate crowd detected.';
                alertMessage.className = 'alert-message';
                break;
            case 2:
                alertLevel.textContent = 'Warning';
                alertLevel.className = 'stat-value alert-warning';
                alertMessage.textContent = 'WARNING: Large crowd detected.';
                alertMessage.className = 'alert-message';
                break;
            case 3:
                alertLevel.textContent = 'Critical';
                alertLevel.className = 'stat-value alert-critical alert-critical-animated';
                alertMessage.textContent = 'CRITICAL: Overcrowding detected!';
                alertMessage.className = 'alert-message';
                break;
            default:
                alertLevel.textContent = 'Unknown';
                alertLevel.className = 'stat-value';
        }
    }

    // Reset database function
    async function resetDatabase() {
        try {
            dataMessage.textContent = 'Resetting database...';
            dataMessage.className = 'data-message';
            
            const response = await fetch('/reset_database');
            const data = await response.json();
            
            if (data.status === 'success') {
                dataMessage.textContent = 'Database reset successfully!';
                dataMessage.className = 'data-message';
                setTimeout(() => {
                    dataMessage.textContent = '';
                }, 3000);
            } else {
                dataMessage.textContent = `Error: ${data.message}`;
                dataMessage.className = 'data-message';
            }
        } catch (error) {
            console.error('Error resetting database:', error);
            dataMessage.textContent = 'Error resetting database. Please check console for details.';
            dataMessage.className = 'data-message';
        }
    }

    // Export data function
    async function exportData() {
        try {
            dataMessage.textContent = 'Exporting data...';
            dataMessage.className = 'data-message';
            
            const response = await fetch('/export_data');
            const data = await response.json();
            
            if (data.status === 'success') {
                dataMessage.textContent = data.message;
                dataMessage.className = 'data-message';
                setTimeout(() => {
                    dataMessage.textContent = '';
                }, 5000);
            } else {
                dataMessage.textContent = `Error: ${data.message}`;
                dataMessage.className = 'data-message';
            }
        } catch (error) {
            console.error('Error exporting data:', error);
            dataMessage.textContent = 'Error exporting data. Please check console for details.';
            dataMessage.className = 'data-message';
        }
    }

    // Initialize
    console.log('Crowd Management System loaded');
});