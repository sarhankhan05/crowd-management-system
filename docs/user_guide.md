# User Guide

## Introduction

The Advanced Crowd Management System is a computer vision application designed to monitor and analyze crowd density in real-time. It uses advanced object detection algorithms to count people and provide alerts when crowd levels exceed predefined thresholds.

## System Requirements

### Hardware
- Computer with at least 4GB RAM
- Camera device (built-in or external)
- Speakers or headphones for audio alerts (optional)

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
python UI.py
```

### Interface Overview

The application interface consists of three main sections:

1. **Video Feed Area**: Displays the live camera feed with people detection overlays
2. **Control Panel**: Contains all user controls and settings
3. **Information Panel**: Shows detection history and alert logs

## Using the Application

### Starting Detection
1. Click the "Start Camera" button to begin crowd detection
2. The live video feed will appear in the main display area
3. Detected people will be highlighted with green bounding boxes
4. Faces within detected bodies will be highlighted with red bounding boxes

### Adjusting Settings
- **Camera Selection**: Use the dropdown to select between available cameras
- **Alert Thresholds**: Adjust crowd density thresholds in the settings panel
- **Export Data**: Save detection history to CSV format

### Monitoring Alerts
The system provides visual and audio alerts when crowd density exceeds thresholds:
- **Normal** (Green indicator): Low crowd density
- **Caution** (Yellow indicator): Moderate crowd levels
- **Warning** (Orange indicator): High crowd density
- **Critical** (Red indicator): Overcrowding detected

## Data Management

### Viewing History
The "Detection History" tab shows a table of all detected objects with timestamps and confidence levels.

### Alert Log
The "Alert Log" tab displays all triggered alerts with timestamps.

### Exporting Data
Click "Export Data" to save detection history to a CSV file for further analysis.

### Resetting Database
Use the "Reset Database" button to clear all stored detection data.

## Troubleshooting

### Camera Not Working
- Ensure your camera is properly connected
- Check that no other applications are using the camera
- Try selecting a different camera from the dropdown

### Poor Detection Accuracy
- Ensure adequate lighting conditions
- Position the camera at an appropriate angle and distance
- Check that the YOLOv3 weights file is properly downloaded

### Application Crashes
- Ensure all dependencies are properly installed
- Check that you're using a supported Python version
- Verify that the application has necessary permissions

## Frequently Asked Questions

### How accurate is the people counting?
The accuracy depends on several factors including camera quality, lighting conditions, and crowd density. Under optimal conditions, the system achieves approximately 90% accuracy.

### Can I use multiple cameras?
Yes, the system supports multiple camera feeds. Use the "Change Camera Feed" button or the camera selector dropdown to switch between available cameras.

### How often are alerts triggered?
Alerts are evaluated in real-time with each frame. Audio alerts are rate-limited to prevent excessive noise.

### Is my data stored securely?
All data is stored locally on your device in an SQLite database. No data is transmitted to external servers.

## Support

For additional support, please open an issue on the GitHub repository or contact the development team.