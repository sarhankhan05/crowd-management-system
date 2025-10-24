# System Architecture

## Overview

The Advanced Crowd Management System is a modern web application built with Flask that provides real-time crowd monitoring and analysis capabilities. The system uses computer vision techniques to detect and count people in video feeds, providing alerts when crowd density exceeds predefined thresholds.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Web Browser Client                           │
└─────────────────────────────┬───────────────────────────────────────┘
                              │ HTTP/WebSocket
┌─────────────────────────────▼───────────────────────────────────────┐
│                          Flask Web Server                           │
│                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   Web Routes    │    │   Templates     │    │    Static       │ │
│  │  (app.py)       │    │ (templates/)    │    │   (static/)     │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘ │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                         Core Detection Module                       │
│                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │  CrowdDetector  │    │   OpenCV CV     │    │    Database     │ │
│  │ (core/detection)│    │   Functions     │    │   (SQLite)      │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘ │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                          Camera Hardware                            │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. Web Interface Layer (Flask)

**File: app.py**
- Main Flask application server
- REST API endpoints for camera control and data retrieval
- Video streaming endpoint for real-time feed
- Thread management for concurrent operations

**File: templates/index.html**
- Main user interface template
- Responsive design for various screen sizes
- Real-time updates via JavaScript

**File: static/css/style.css**
- Modern, dark-themed styling
- Responsive design principles
- Visual feedback for different alert levels

**File: static/js/main.js**
- Client-side JavaScript for UI interactions
- Real-time updates of statistics and alerts
- AJAX calls to backend API endpoints

### 2. Core Logic Layer

**File: core/detection.py**
- Main computer vision logic
- YOLOv3 object detection integration
- Haar Cascade face detection
- Database operations for storing detection data
- Thread-safe operations for concurrent access

**File: config.py**
- Application configuration settings
- Threshold values for alerts
- Camera and detection parameters
- Environment-specific configurations

### 3. Data Layer

**File: detection_database.db**
- SQLite database for persistent storage
- Tables for object detections and face detections
- Historical data tracking

### 4. Models and Configuration

**File: yolov3.cfg**
- YOLOv3 neural network configuration
- Model architecture definition

**File: yolov3.weights**
- Pre-trained YOLOv3 weights (downloaded separately)

**File: coco.names**
- Class names for COCO dataset objects

**File: haarcascade_frontalface_default.xml**
- Pre-trained Haar Cascade for face detection

## Data Flow

1. **Initialization**: Application starts Flask server and initializes detection module
2. **User Interaction**: User accesses web interface and starts camera
3. **Camera Capture**: Flask captures video frames in a separate thread
4. **Object Detection**: CrowdDetector processes frames using YOLOv3
5. **Face Detection**: Additional face detection within person bounding boxes
6. **Data Storage**: Detection results stored in SQLite database
7. **Real-time Updates**: Statistics streamed to web interface via AJAX
8. **Alert System**: Dynamic alerts based on crowd density thresholds
9. **User Feedback**: Visual and numerical feedback in web interface

## Threading Model

The application uses a multi-threaded approach to handle concurrent operations:

- **Main Thread**: Flask web server
- **Camera Thread**: Continuous frame capture and processing
- **UI Thread**: Browser rendering and user interactions
- **Database Thread**: SQLite operations (handled by SQLite's thread safety)

## Security Considerations

- All processing happens locally (no cloud dependencies)
- Camera access is limited to local machine
- Database files stored locally with appropriate permissions
- No external network requests in core functionality

## Scalability

- Modular design allows for easy extension
- Configuration-based threshold settings
- Database schema designed for future expansion
- REST API design supports additional endpoints