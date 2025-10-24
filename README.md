# Advanced Crowd Management System with Stampede Prevention

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.0%2B-blue.svg)](https://palletsprojects.com/p/flask/)

An intelligent crowd monitoring and management system designed to prevent stampedes in crowded environments using computer vision and real-time analytics.

## Features

### Core Detection Capabilities
- **Real-time People Detection**: Uses YOLOv3 object detection to identify and count people in video feeds
- **Face Recognition**: Haar Cascade face detection for additional identification
- **Multi-person Tracking**: Tracks individual movement patterns over time
- **Database Storage**: SQLite database for storing detection history and incidents

### Stampede Prevention Features
- **Risk Assessment Algorithms**: Calculates stampede risk based on multiple factors:
  - **Crowd Density**: Monitors how densely packed people are in the area
  - **Movement Velocity**: Tracks how fast people are moving
  - **Direction Coherence**: Analyzes if people are moving in coordinated or chaotic directions
  - **Acceleration Changes**: Detects sudden changes in movement patterns
- **Real-time Risk Scoring**: Continuous assessment with visual indicators
- **Predictive Analytics**: Early warning system for potential stampede conditions
- **Emergency Alert System**: Automatic notifications when high-risk situations are detected
- **Incident Documentation**: Automatic logging of all high-risk events
- **Historical Trend Analysis**: Review past incidents and patterns

For detailed information about stampede prevention features, see [Stampede Prevention Features Documentation](docs/STAMPEDE_PREVENTION_FEATURES.md).

### User Interface
- **Modern Web Dashboard**: Responsive web interface for monitoring
- **Live Video Feed**: Real-time camera feed with detection overlays
- **Statistics Panel**: Current people count, alert levels, and risk scores
- **Risk Factor Visualization**: Progress bars showing individual risk components
- **Incident History**: List of recent high-risk events
- **Data Export**: Export detection data and stampede reports to CSV

## System Architecture

```
Crowd Management System
├── Core Detection Module (core/detection.py)
│   ├── YOLOv3 Object Detection
│   ├── Haar Cascade Face Detection
│   ├── Stampede Risk Assessment
│   ├── Movement Pattern Analysis
│   └── Database Integration
├── Web Interface (app.py)
│   ├── Flask Web Server
│   ├── REST API Endpoints
│   ├── Real-time Video Streaming
│   └── Data Management
├── Frontend (templates/, static/)
│   ├── HTML Templates
│   ├── CSS Styling
│   └── JavaScript Interactivity
└── Utilities
    ├── Installation Scripts
    ├── Model Downloaders
    └── System Checkers
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Camera device (webcam or IP camera)

### Quick Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sarhankhan05/crowd-management-system
   cd crowd-management-system
   ```

2. **Run the installation script**:
   ```bash
   # On Windows
   install.bat
   
   # On Linux/Mac
   ./install.sh
   ```

3. **Download YOLOv3 weights**:
   ```bash
   python download_weights.py
   ```

4. **Verify installation**:
   ```bash
   python verify_installation.py
   ```

### Manual Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Download YOLOv3 weights**:
   - Download from: https://pjreddie.com/media/files/yolov3.weights
   - Place in the project root directory

## Usage

### Starting the System

1. **Run the application**:
   ```bash
   # On Windows
   run.bat
   
   # On Linux/Mac
   ./run.sh
   
   # Or directly
   python app.py
   ```

2. **Access the web interface**:
   - Open your browser to `http://localhost:5000`

### Operating the System

1. **Start Camera**: Click the "Start Camera" button to begin detection
2. **Monitor Crowd**: Watch the live feed and statistics panel
3. **Check Risk Levels**: Monitor the stampede risk indicator
4. **Review Incidents**: Check the incident history for high-risk events
5. **Export Data**: Use the export buttons to save reports

### Alert Levels

- **Normal (Green)**: Low crowd density, no risk factors
- **Caution (Yellow)**: Moderate crowd detected
- **Warning (Orange)**: Large crowd, increased monitoring needed
- **Critical (Red)**: Overcrowding detected, immediate attention required
- **Stampede Risk (Flashing Red)**: High probability of stampede, emergency response needed

### Risk Factors

1. **Density**: How crowded the area is (0-100%)
2. **Velocity**: Average speed of movement (0-100%)
3. **Direction**: Coherence of movement directions (0-100%)
4. **Acceleration**: Rate of speed changes (0-100%)

## Configuration

The system can be configured through `config.py`:

- **Camera Settings**: Adjust camera ID and resolution
- **Detection Thresholds**: Modify confidence levels for detection
- **Alert Thresholds**: Set crowd count levels for different alerts
- **Risk Thresholds**: Configure risk scoring parameters

## API Endpoints

- `GET /` - Main dashboard
- `GET /start_camera` - Start camera feed
- `GET /stop_camera` - Stop camera feed
- `GET /video_feed` - Live video stream
- `GET /stats` - Current statistics
- `GET /history` - Detection history
- `GET /stampede_incidents` - Stampede incident reports
- `GET /reset_database` - Clear all data
- `GET /export_data` - Export detection data
- `GET /export_stampede_report` - Export stampede report

## Development

### Project Structure
```
crowd-management-system/
├── core/                 # Core detection logic
├── templates/            # HTML templates
├── static/               # CSS, JavaScript, images
├── tests/                # Unit tests
├── docs/                 # Documentation
├── requirements.txt      # Python dependencies
├── app.py               # Main Flask application
├── config.py            # Configuration settings
├── setup.py             # Installation script
└── README.md            # This file
```

### Running Tests
```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and development process.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- YOLOv3 for object detection capabilities
- OpenCV for computer vision functions
- Flask for web framework
- Haar Cascades for face detection

## Support

For support, please open an issue on GitHub or contact the development team.

---

**Prevent stampedes. Save lives.**