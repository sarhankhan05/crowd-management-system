# User Guide

## Introduction

The Advanced Crowd Management System is a computer vision application designed to monitor and analyze crowd density in real-time. It uses advanced object detection algorithms to count people and provide alerts when crowd levels exceed predefined thresholds.

## System Requirements

### Hardware
- Computer with at least 4GB RAM
- Camera device (built-in or external)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Software
- Windows 10/11, macOS 10.14+, or Linux
- Python 3.8 or higher
- 500MB available disk space

## Installation

### Step 1: Install Python
If you don't have Python installed, download it from [python.org](https://www.python.org/downloads/).

### Step 2: Download the Application
Clone or download the repository from GitHub:
```bash
git clone https://github.com/yourusername/crowd-management-system.git
```

### Step 3: Install Dependencies
Navigate to the project directory and install the required packages:
```bash
cd crowd-management-system
pip install -r requirements.txt
```

### Step 4: Download YOLOv3 Weights
Download the `yolov3.weights` file from the [YOLO website](https://pjreddie.com/darknet/yolo/) and place it in the project root directory.

## Getting Started

### Launching the Application
Run the application by executing:
```bash
python app.py
```

The application will start a web server on `http://localhost:5000`. Open this URL in your web browser.

### Interface Overview

The web interface consists of several sections:

1. **Video Feed Area**: Displays the live camera feed with people detection overlays
2. **Statistics Panel**: Shows real-time people count, alert level, and FPS
3. **Alert Section**: Displays current system status and alerts
4. **Data Management**: Controls for database operations

## Using the Application

### Starting Detection
1. Click the "Start Camera" button to begin crowd detection
2. The live video feed will appear in the main display area
3. Detected people will be highlighted with green bounding boxes
4. Faces within detected bodies will be highlighted with red bounding boxes

### Monitoring Alerts
The system provides visual alerts when crowd density exceeds thresholds:
- **Normal** (Green text): Low crowd density
- **Caution** (Yellow text): Moderate crowd levels
- **Warning** (Orange text): High crowd density
- **Critical** (Red text with animation): Overcrowding detected

### Data Management
- **Reset Database**: Clears all stored detection data
- **Export Data**: Saves detection history to a CSV file

## Alert System

The alert system uses the following thresholds:
- **Normal**: 0-10 people
- **Caution**: 11-20 people
- **Warning**: 21-30 people
- **Critical**: 31+ people

These thresholds can be adjusted in the `config.py` file.

## Troubleshooting

### Camera Not Working
- Ensure your camera is properly connected
- Check that no other applications are using the camera
- Verify camera permissions for your browser

### Poor Detection Accuracy
- Ensure adequate lighting conditions
- Position the camera at an appropriate angle and distance
- Check that the YOLOv3 weights file is properly downloaded

### Application Not Starting
- Ensure all dependencies are properly installed
- Check that you're using a supported Python version
- Verify that port 5000 is not being used by another application

### Web Interface Issues
- Try refreshing the page
- Clear your browser cache
- Try a different web browser

## Frequently Asked Questions

### How accurate is the people counting?
The accuracy depends on several factors including camera quality, lighting conditions, and crowd density. Under optimal conditions, the system achieves approximately 90% accuracy.

### Can I use multiple cameras?
The current implementation supports a single camera. Multiple camera support can be added by modifying the camera selection logic in `app.py`.

### How often are alerts updated?
Alerts are evaluated in real-time with each frame processed by the detection system.

### Is my data stored securely?
All data is stored locally on your device in an SQLite database. No data is transmitted to external servers.

## API Endpoints

For developers who want to integrate with the system programmatically:

- `GET /` - Main web interface
- `GET /start_camera` - Start camera feed
- `GET /stop_camera` - Stop camera feed
- `GET /video_feed` - Stream video feed
- `GET /stats` - Get current detection statistics
- `GET /history` - Get detection history
- `GET /reset_database` - Reset detection database
- `GET /export_data` - Export detection data to CSV

## Support

For additional support, please open an issue on the GitHub repository or contact the development team.