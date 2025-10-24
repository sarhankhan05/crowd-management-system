# Configuration file for Crowd Management System

import os

class Config:
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
    CONFIDENCE_THRESHOLD = 0.6
    NMS_THRESHOLD = 0.3

    # Database settings
    DATABASE_FILE = "detection_database.db"

    # Alert settings
    ALERT_THRESHOLDS = {
        "NORMAL": 0,      # 0 people
        "CAUTION": 10,    # 10+ people
        "WARNING": 20,    # 20+ people
        "CRITICAL": 30    # 30+ people
    }
    
    # Stampede risk thresholds
    STAMPEDE_RISK_THRESHOLDS = {
        "LOW": 0.3,       # Low risk
        "MEDIUM": 0.6,    # Medium risk
        "HIGH": 0.8       # High risk
    }

    # Web server settings
    HOST = "0.0.0.0"
    PORT = 5000
    DEBUG = True

    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
    STATIC_DIR = os.path.join(BASE_DIR, "static")
    CORE_DIR = os.path.join(BASE_DIR, "core")

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    DEBUG = True
    TESTING = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}