# Advanced Crowd Management System

An intelligent crowd monitoring and management system using computer vision technologies for real-time people counting and crowd analysis.

## Features

- Real-time crowd detection using YOLOv3 object detection
- Facial recognition within detected crowds
- Dynamic crowd alert system with customizable thresholds
- Live camera feed with people counting
- Historical data tracking and analytics
- Export functionality for reports and data
- Modern, intuitive user interface

## Technologies Used

- **Python** - Core programming language
- **PyQt5** - Desktop GUI framework
- **OpenCV** - Computer vision and image processing
- **YOLOv3** - Object detection model
- **SQLite** - Local database storage
- **Haar Cascades** - Face detection

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
python UI.py
```

### Controls

- **Start Camera**: Begin crowd detection on the selected camera feed
- **Stop Camera**: Stop the camera feed
- **Change Camera Feed**: Switch between available camera devices
- **Reset Database**: Clear all stored detection data
- **Export Data**: Export detection history to CSV format

### Alert System

The system provides four levels of crowd alerts:
- **Normal** (Green): Low crowd density
- **Caution** (Yellow): Moderate crowd levels
- **Warning** (Orange): High crowd density
- **Critical** (Red): Overcrowding detected

Alert thresholds can be adjusted in the settings panel.

## Project Structure

```
crowd-management-system/
├── UI.py                 # Main application interface
├── yolov3.cfg            # YOLOv3 configuration
├── yolov3.weights        # YOLOv3 pre-trained weights (needs to be downloaded)
├── coco.names            # Object class names
├── haarcascade_frontalface_default.xml  # Face detection model
├── detection_database.db # SQLite database for storing detection data
├── requirements.txt      # Python dependencies
└── README.md             # This file
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
- PyQt5 for the GUI framework

## Contact

For questions or feedback, please open an issue on the GitHub repository.

For support, email sarhankhan05@gmail.com or file an issue on GitHub.