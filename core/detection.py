import cv2
import numpy as np
import sqlite3
from datetime import datetime
import os

class CrowdDetector:
    def __init__(self, db_path='detection_database.db'):
        self.db_path = db_path
        self.net = None
        self.classes = []
        self.face_cascade = None
        self.db_conn = None
        self.db_cursor = None
        self.initialize_models()
        self.initialize_database()
        
    def initialize_models(self):
        """Initialize YOLO and Haar Cascade models"""
        try:
            # Load YOLO
            self.net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
            with open("coco.names", "r") as f:
                self.classes = f.read().strip().split("\n")
            
            # Face detection
            cascade_path = "haarcascade_frontalface_default.xml"
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
        except Exception as e:
            print(f"Error initializing models: {e}")
            raise
    
    def initialize_database(self):
        """Initialize SQLite database for storing detection data"""
        try:
            self.db_conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.db_cursor = self.db_conn.cursor()
            self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS object_detections
                                 (timestamp DATETIME, object_label TEXT, confidence REAL)''')
            self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS face_detections
                                 (timestamp DATETIME, x INT, y INT, width INT, height INT, unique_id INT)''')
            self.db_conn.commit()
        except sqlite3.Error as e:
            print(f"Database Error: {e}")
            raise
    
    def detect_crowd(self, frame):
        """Detect people in frame using YOLOv3"""
        # Check if models are loaded
        if self.net is None or self.face_cascade is None:
            raise RuntimeError("Models not initialized properly")
        
        # Check if database is initialized
        if self.db_conn is None or self.db_cursor is None:
            raise RuntimeError("Database not initialized properly")
        
        # Resize frame for processing
        frame = cv2.resize(frame, (700, 500))
        
        # Prepare frame for YOLO
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.get_output_layers(self.net))
        
        boxes, confidences, class_ids = [], [], []
        
        # Collect detections
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x = int(detection[0] * frame.shape[1])
                    center_y = int(detection[1] * frame.shape[0])
                    w = int(detection[2] * frame.shape[1])
                    h = int(detection[3] * frame.shape[0])
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        
        # NMS to remove duplicates
        indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        
        # Process detections
        num_people = 0
        detections = []
        
        if len(indices) > 0:
            # Convert indices to a list of integers using a safe approach
            indices_list = []
            
            # Handle different types of indices
            if isinstance(indices, (list, tuple)):
                for i in indices:
                    if isinstance(i, (int, np.integer)):
                        indices_list.append(int(i))
            elif isinstance(indices, np.ndarray):
                if indices.size > 0:
                    if indices.ndim > 1:
                        flat_indices = indices.flatten()
                    else:
                        flat_indices = indices
                    for i in flat_indices:
                        if isinstance(i, (int, np.integer)):
                            indices_list.append(int(i))
            else:
                # For single values, check type first
                if isinstance(indices, (int, np.integer)):
                    indices_list.append(int(indices))
            
            for idx in indices_list:
                # Ensure index is within bounds
                if idx >= len(boxes) or idx >= len(class_ids) or idx >= len(confidences):
                    continue
                    
                x, y, w, h = boxes[idx]
                label = str(self.classes[class_ids[idx]])
                confidence = confidences[idx]
                
                if label == "person":
                    num_people += 1
                    # Save object detection
                    timestamp = datetime.now()
                    self.db_cursor.execute("INSERT INTO object_detections (timestamp, object_label, confidence) VALUES (?, ?, ?)",
                                         (timestamp, label, confidence))
                    self.db_conn.commit()
                    
                    detection = {
                        'x': x,
                        'y': y,
                        'w': w,
                        'h': h,
                        'label': label,
                        'confidence': confidence
                    }
                    detections.append(detection)
                    
                    # Face detection inside person bounding box
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = self.face_cascade.detectMultiScale(gray[y:y+h, x:x+w], scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))
                    detection['faces'] = []
                    for (fx, fy, fw, fh) in faces:
                        face_data = {
                            'x': x + fx,
                            'y': y + fy,
                            'w': fw,
                            'h': fh
                        }
                        detection['faces'].append(face_data)
        
        return frame, num_people, detections
    
    def get_output_layers(self, net):
        """Get output layers for YOLO"""
        layer_names = net.getLayerNames()
        try:
            # For newer OpenCV versions
            unconnected_layers = net.getUnconnectedOutLayers()
            if hasattr(unconnected_layers, 'flatten'):
                return [layer_names[i - 1] for i in unconnected_layers.flatten()]
            else:
                # For older OpenCV versions
                return [layer_names[i[0] - 1] for i in unconnected_layers]
        except Exception:
            # Fallback method
            output_layers = []
            for i in range(len(layer_names)):
                if 'yolo' in layer_names[i]:
                    output_layers.append(layer_names[i])
            return output_layers
    
    def get_detection_history(self, limit=100):
        """Get recent detection history"""
        # Check if database is initialized
        if self.db_conn is None or self.db_cursor is None:
            raise RuntimeError("Database not initialized properly")
        
        try:
            self.db_cursor.execute("SELECT * FROM object_detections ORDER BY timestamp DESC LIMIT ?", (limit,))
            return self.db_cursor.fetchall()
        except Exception as e:
            print(f"Error fetching detection history: {e}")
            return []
    
    def reset_database(self):
        """Clear all detection data"""
        # Check if database is initialized
        if self.db_conn is None:
            raise RuntimeError("Database not initialized properly")
        
        try:
            self.db_conn.execute("DELETE FROM object_detections")
            self.db_conn.execute("DELETE FROM face_detections")
            self.db_conn.commit()
        except Exception as e:
            print(f"Error resetting database: {e}")
    
    def export_data(self, filepath):
        """Export detection data to CSV"""
        # Check if database is initialized
        if self.db_conn is None or self.db_cursor is None:
            raise RuntimeError("Database not initialized properly")
        
        try:
            import csv
            self.db_cursor.execute("SELECT * FROM object_detections")
            rows = self.db_cursor.fetchall()
            
            with open(filepath, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Object Label", "Confidence"])
                writer.writerows(rows)
            return True
        except Exception as e:
            print(f"Error exporting data: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if hasattr(self, 'db_conn') and self.db_conn:
            self.db_conn.close()