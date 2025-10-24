# Configuration file for Crowd Management System

# Camera settings
DEFAULT_CAMERA_ID = 0
CAMERA_WIDTH = 700
CAMERA_HEIGHT = 500
FRAME_RATE = 30

# Detection settings
YOLO_CONFIG_FILE = "yolov3.cfg"
YOLO_WEIGHTS_FILE = "yolov3.weights"
COCO_NAMES_FILE = "coco.names"
FACE_CASCADE_FILE = "haarcascade_frontalface_default.xml"

# Detection thresholds
CONFIDENCE_THRESHOLD = 0.5
NMS_THRESHOLD = 0.4

# Database settings
DATABASE_FILE = "detection_database.db"

# Alert settings
DEFAULT_ALERT_THRESHOLD = 30  # Number of people for critical alert
ALERT_LEVELS = {
    "NORMAL": 0,
    "CAUTION": 1,
    "WARNING": 2,
    "CRITICAL": 3
}

# Sound settings
ALERT_SOUND_DURATION = 500  # milliseconds
ALERT_SOUND_FREQUENCY = 1000  # Hz

# UI settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_TITLE = "Advanced Crowd Management System"

# Colors (BGR format for OpenCV)
COLORS = {
    "GREEN": (0, 255, 0),
    "RED": (0, 0, 255),
    "BLUE": (255, 0, 0),
    "YELLOW": (0, 255, 255),
    "ORANGE": (0, 165, 255),
    "PURPLE": (128, 0, 128)
}