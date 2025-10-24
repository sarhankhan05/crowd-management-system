# Advanced Crowd Management System

An intelligent crowd monitoring and management system using computer vision technologies for real-time people counting and crowd analysis with a modern web-based interface.

![System Architecture](docs/architecture.png)

## Features

- Real-time crowd detection using YOLOv3 object detection
- Facial recognition within detected crowds
- Dynamic crowd alert system with customizable thresholds
- Live camera feed with people counting
- Historical data tracking and analytics
- Export functionality for reports and data
- Modern, responsive web interface
- Cross-platform compatibility

## Technologies Used

- **Python** - Core programming language
- **Flask** - Web framework for the user interface
- **OpenCV** - Computer vision and image processing
- **YOLOv3** - Object detection model
- **SQLite** - Local database storage
- **HTML/CSS/JavaScript** - Frontend interface
- **Haar Cascades** - Face detection

## Architecture

The system is organized into the following components:

```
crowd-management-system/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── setup.py               # Package setup
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── .gitignore             # Git ignore rules
├── core/                  # Core logic modules
│   ├── __init__.py        # Package initializer
│   └── detection.py       # Computer vision and detection logic
├── templates/             # HTML templates
│   ├── __init__.py        # Package initializer
│   └── index.html         # Main interface template
├── static/                # Static assets
│   ├── __init__.py        # Package initializer
│   ├── css/               # Stylesheets
│   │   ├── __init__.py    # Package initializer
│   │   └── style.css      # Main stylesheet
│   ├── js/                # JavaScript files
│   │   ├── __init__.py    # Package initializer
│   │   └── main.js        # Frontend logic
│   └── images/            # Image assets
│       ├── __init__.py    # Package initializer
├── components/            # Reusable UI components
│   └── __init__.py        # Package initializer
├── docs/                  # Documentation
│   ├── architecture.md    # System architecture
│   ├── user_guide.md      # User guide
│   └── development.md     # Development guide
├── tests/                 # Unit tests
│   ├── __init__.py        # Package initializer
│   └── test_detection.py  # Detection tests
├── yolov3.cfg             # YOLOv3 configuration
├── yolov3.weights         # YOLOv3 pre-trained weights (needs to be downloaded)
├── coco.names             # Object class names
├── haarcascade_frontalface_default.xml  # Face detection model
├── detection_database.db  # SQLite database for storing detection data
└── verify_installation.py # Installation verification script
```

For detailed architecture information, see [Architecture Documentation](docs/architecture.md).

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.8 or higher
- Windows, macOS, or Linux operating system
- Camera device (built-in or external)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/sarhankhan05/crowd-management-system
   cd crowd-management-system
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Download the YOLOv3 weights file:
   - Download `yolov3.weights` from [YOLO website](https://pjreddie.com/darknet/yolo/)
   - Place the file in the project root directory

## Usage

To run the application, execute:

```bash
python app.py
```

Then open your web browser and navigate to `http://localhost:5000`

### Web Interface Controls

- **Start Camera**: Begin crowd detection on the default camera feed
- **Stop Camera**: Stop the camera feed
- **Reset Database**: Clear all stored detection data
- **Export Data**: Export detection history to CSV format

### Alert System

The system provides four levels of crowd alerts:
- **Normal** (Green): Low crowd density
- **Caution** (Yellow): Moderate crowd levels
- **Warning** (Orange): High crowd density
- **Critical** (Red): Overcrowding detected

## API Endpoints

The application provides the following REST API endpoints:

- `GET /` - Main web interface
- `GET /start_camera` - Start camera feed
- `GET /stop_camera` - Stop camera feed
- `GET /video_feed` - Stream video feed
- `GET /stats` - Get current detection statistics
- `GET /history` - Get detection history
- `GET /reset_database` - Reset detection database
- `GET /export_data` - Export detection data to CSV

## Development

For development information, see [Development Guide](docs/development.md).

### Running Tests

```bash
python -m unittest discover tests
```

### Verification Script

Run the verification script to check if all components are properly installed:

```bash
python verify_installation.py
```

## Docker Deployment

The application can be deployed using Docker:

```bash
docker build -t crowd-management-system .
docker run -p 5000:5000 crowd-management-system
```

Or using docker-compose:

```bash
docker-compose up
```

## Contributing

Contributions to the project are welcome. To contribute:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to the branch (`git push origin feature/AmazingFeature`)
6. Open a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [YOLOv3](https://pjreddie.com/darknet/yolo/) for object detection
- [OpenCV](https://opencv.org/) for computer vision tools
- [Flask](https://flask.palletsprojects.com/) for the web framework

## Contact

For questions or feedback, please open an issue on the GitHub repository.