// Main JavaScript for Crowd Management System

document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const videoFeed = document.getElementById('video-feed');
    const noFeedMessage = document.getElementById('no-feed-message');
    const peopleCount = document.getElementById('people-count');
    const alertLevel = document.getElementById('alert-level');
    const stampedeRisk = document.getElementById('stampede-risk');
    const fps = document.getElementById('fps');
    const alertMessage = document.getElementById('alert-message');
    const resetBtn = document.getElementById('reset-btn');
    const exportBtn = document.getElementById('export-btn');
    const exportStampedeBtn = document.getElementById('export-stampede-btn');
    const dataMessage = document.getElementById('data-message');
    const incidentList = document.getElementById('incident-list');
    
    // Video upload elements
    const uploadBtn = document.getElementById('upload-btn');
    const processVideoBtn = document.getElementById('process-video-btn');
    const videoUploadInput = document.getElementById('video-upload');
    
    // Risk factor elements
    const densityProgress = document.getElementById('density-progress');
    const velocityProgress = document.getElementById('velocity-progress');
    const directionProgress = document.getElementById('direction-progress');
    const accelerationProgress = document.getElementById('acceleration-progress');
    const densityValue = document.getElementById('density-value');
    const velocityValue = document.getElementById('velocity-value');
    const directionValue = document.getElementById('direction-value');
    const accelerationValue = document.getElementById('acceleration-value');

    // Event listeners
    startBtn.addEventListener('click', startCamera);
    stopBtn.addEventListener('click', stopCamera);
    resetBtn.addEventListener('click', resetDatabase);
    exportBtn.addEventListener('click', exportData);
    exportStampedeBtn.addEventListener('click', exportStampedeReport);
    
    // Video upload event listeners
    uploadBtn.addEventListener('click', function() {
        videoUploadInput.click();
    });
    
    videoUploadInput.addEventListener('change', handleVideoUpload);
    processVideoBtn.addEventListener('click', processVideo);

    // Variables
    let statsInterval = null;
    let incidentInterval = null;

    // Handle video upload
    function handleVideoUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const formData = new FormData();
        formData.append('video', file);
        
        fetch('/upload_video', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alertMessage.textContent = `Video uploaded: ${data.filename}`;
                alertMessage.className = 'alert-message';
                processVideoBtn.disabled = false;
            } else {
                alertMessage.textContent = `Upload error: ${data.message}`;
                alertMessage.className = 'alert-message';
            }
        })
        .catch(error => {
            console.error('Upload error:', error);
            alertMessage.textContent = 'Error uploading video. Please check console for details.';
            alertMessage.className = 'alert-message';
        });
    }

    // Process video
    function processVideo() {
        fetch('/process_video', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Hide camera controls and show video feed
                startBtn.disabled = true;
                stopBtn.disabled = true;
                processVideoBtn.disabled = true;
                
                // Show video feed
                videoFeed.style.display = 'block';
                noFeedMessage.style.display = 'none';
                videoFeed.src = '/video_feed';
                
                // Start stats updates
                if (statsInterval) clearInterval(statsInterval);
                statsInterval = setInterval(updateStats, 200); // Update every 200ms for real-time feel
                
                // Start incident updates
                if (incidentInterval) clearInterval(incidentInterval);
                incidentInterval = setInterval(updateIncidents, 3000); // Update every 3 seconds
                
                alertMessage.textContent = 'Processing video...';
                alertMessage.className = 'alert-message';
            } else {
                alertMessage.textContent = `Processing error: ${data.message}`;
                alertMessage.className = 'alert-message';
            }
        })
        .catch(error => {
            console.error('Processing error:', error);
            alertMessage.textContent = 'Error processing video. Please check console for details.';
            alertMessage.className = 'alert-message';
        });
    }

    // Start camera function
    async function startCamera() {
        try {
            const response = await fetch('/start_camera');
            const data = await response.json();
            
            if (data.status === 'success') {
                // Update UI
                startBtn.disabled = true;
                stopBtn.disabled = false;
                processVideoBtn.disabled = true;
                
                // Show video feed
                videoFeed.style.display = 'block';
                noFeedMessage.style.display = 'none';
                videoFeed.src = '/video_feed';
                
                // Start stats updates - more frequent for real-time feel
                if (statsInterval) clearInterval(statsInterval);
                statsInterval = setInterval(updateStats, 200); // Update every 200ms for real-time feel
                
                // Start incident updates
                if (incidentInterval) clearInterval(incidentInterval);
                incidentInterval = setInterval(updateIncidents, 3000); // Update every 3 seconds
                
                // Update alert message
                alertMessage.textContent = 'Camera started. Detecting crowd and monitoring for stampede risk...';
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
                processVideoBtn.disabled = false;
                
                // Hide video feed
                videoFeed.style.display = 'none';
                noFeedMessage.style.display = 'block';
                videoFeed.src = '';
                
                // Stop stats updates
                if (statsInterval) {
                    clearInterval(statsInterval);
                    statsInterval = null;
                }
                
                // Stop incident updates
                if (incidentInterval) {
                    clearInterval(incidentInterval);
                    incidentInterval = null;
                }
                
                // Reset stats display
                peopleCount.textContent = '0';
                alertLevel.textContent = 'Normal';
                alertLevel.className = 'stat-value alert-normal';
                stampedeRisk.textContent = 'Low';
                stampedeRisk.className = 'stat-value risk-low';
                fps.textContent = '0.00';
                
                // Reset risk factors
                densityProgress.style.width = '0%';
                velocityProgress.style.width = '0%';
                directionProgress.style.width = '0%';
                accelerationProgress.style.width = '0%';
                densityValue.textContent = '0%';
                velocityValue.textContent = '0%';
                directionValue.textContent = '0%';
                accelerationValue.textContent = '0%';
                
                // Update alert message
                alertMessage.textContent = 'Camera stopped. System ready.';
                alertMessage.className = 'alert-message';
                
                // Clear incident list
                incidentList.innerHTML = '<p>No incidents recorded yet.</p>';
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
            
            // Update stampede risk
            updateStampedeRisk(stats.stampede_risk);
            
            // Update FPS
            if (stats.fps && !isNaN(stats.fps)) {
                fps.textContent = stats.fps.toFixed(2);
            } else {
                fps.textContent = '0.00';
            }
            
            // Update risk factors if available
            if (stats.stampede_risk && stats.stampede_risk.factors) {
                const factors = stats.stampede_risk.factors;
                // Ensure we have valid values, default to 0 if undefined
                const density = factors.density !== undefined ? factors.density : 0;
                const velocity = factors.velocity !== undefined ? factors.velocity : 0;
                const direction = factors.direction !== undefined ? factors.direction : 0;
                const acceleration = factors.acceleration !== undefined ? factors.acceleration : 0;
                
                const densityPercent = Math.round(density * 100);
                const velocityPercent = Math.round(velocity * 100);
                const directionPercent = Math.round(direction * 100);
                const accelerationPercent = Math.round(acceleration * 100);
                
                densityProgress.style.width = `${densityPercent}%`;
                velocityProgress.style.width = `${velocityPercent}%`;
                directionProgress.style.width = `${directionPercent}%`;
                accelerationProgress.style.width = `${accelerationPercent}%`;
                
                densityValue.textContent = `${densityPercent}%`;
                velocityValue.textContent = `${velocityPercent}%`;
                directionValue.textContent = `${directionPercent}%`;
                accelerationValue.textContent = `${accelerationPercent}%`;
            }
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
            case 4:
                alertLevel.textContent = 'STAMPEDE RISK';
                alertLevel.className = 'stat-value risk-critical alert-critical-animated';
                alertMessage.textContent = 'STAMPEDE RISK DETECTED! TAKE IMMEDIATE ACTION!';
                alertMessage.className = 'alert-message alert-critical-animated';
                break;
            default:
                alertLevel.textContent = 'Normal';
                alertLevel.className = 'stat-value alert-normal';
                alertMessage.textContent = 'System operating normally.';
                alertMessage.className = 'alert-message';
        }
    }

    // Update stampede risk display
    function updateStampedeRisk(risk) {
        const riskScore = risk.score || 0;
        const riskLevel = risk.level || 'LOW';
        
        stampedeRisk.textContent = riskLevel;
        
        switch(riskLevel) {
            case 'LOW':
                stampedeRisk.className = 'stat-value risk-low';
                break;
            case 'MEDIUM':
                stampedeRisk.className = 'stat-value risk-medium';
                break;
            case 'HIGH':
                stampedeRisk.className = 'stat-value risk-high risk-high-animated';
                break;
            default:
                stampedeRisk.className = 'stat-value risk-low';
        }
    }

    // Update incidents function
    async function updateIncidents() {
        try {
            const response = await fetch('/stampede_incidents');
            const data = await response.json();
            
            if (data.status === 'success' && data.data.length > 0) {
                // Clear existing content
                incidentList.innerHTML = '';
                
                // Add incidents (limit to 10 most recent)
                const incidents = data.data.slice(0, 10);
                
                incidents.forEach(incident => {
                    // Assuming incident format: [timestamp, risk_level, people_count, risk_score, factors]
                    const incidentElement = document.createElement('div');
                    incidentElement.className = 'incident-item';
                    
                    const timestamp = incident[0];
                    const riskLevel = incident[1];
                    const peopleCount = incident[2];
                    const riskScore = incident[3];
                    
                    // Format timestamp
                    const date = new Date(timestamp);
                    const timeString = date.toLocaleTimeString();
                    
                    // Add risk level class
                    let riskClass = 'incident-risk-low';
                    if (riskLevel === 'HIGH') riskClass = 'incident-risk-high';
                    else if (riskLevel === 'MEDIUM') riskClass = 'incident-risk-medium';
                    
                    incidentElement.innerHTML = `
                        <span class="incident-time">${timeString}</span>
                        <span class="incident-risk ${riskClass}">${riskLevel} RISK</span>
                        <span>People: ${peopleCount}, Score: ${parseFloat(riskScore).toFixed(2)}</span>
                    `;
                    
                    incidentList.appendChild(incidentElement);
                });
            } else {
                incidentList.innerHTML = '<p>No incidents recorded yet.</p>';
            }
        } catch (error) {
            console.error('Error updating incidents:', error);
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

    // Export stampede report function
    async function exportStampedeReport() {
        try {
            dataMessage.textContent = 'Exporting stampede report...';
            dataMessage.className = 'data-message';
            
            const response = await fetch('/export_stampede_report');
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
            console.error('Error exporting stampede report:', error);
            dataMessage.textContent = 'Error exporting stampede report. Please check console for details.';
            dataMessage.className = 'data-message';
        }
    }

    // Initialize
    console.log('Crowd Management System with Stampede Prevention loaded');
});