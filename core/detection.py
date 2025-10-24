import cv2
import numpy as np
import sqlite3
from datetime import datetime
import os
from collections import deque

class StampedeRiskAssessment:
    """Class to assess stampede risk based on crowd dynamics"""
    
    def __init__(self):
        # Risk factors with weights
        self.risk_factors = {
            'density': 0.3,      # Crowd density
            'velocity': 0.25,    # Movement speed
            'direction': 0.25,   # Movement coherence
            'acceleration': 0.2  # Rate of change in movement
        }
        
        # Risk thresholds
        self.thresholds = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.8
        }
    
    def calculate_density_risk(self, people_count, area_pixels):
        """Calculate risk based on crowd density"""
        if area_pixels == 0:
            return 0
            
        # Calculate actual density (people per 1000 pixels for better scaling)
        density = (people_count * 1000) / area_pixels if area_pixels > 0 else 0
        
        # Normalize density with better scaling for crowd scenarios
        # Assuming max reasonable density is 2.0 people/1000 pixels for safety
        normalized_density = min(density / 2.0, 1.0)
        return normalized_density
    
    def calculate_velocity_risk(self, velocity_history):
        """Calculate risk based on movement velocity"""
        if len(velocity_history) < 2:
            return 0
            
        avg_velocity = np.mean(velocity_history)
        # Higher velocities increase risk (normalize to max 3 pixels/frame for normal walking)
        # Anything above 3 pixels/frame is considered fast movement
        normalized_velocity = min(avg_velocity / 3.0, 1.0)
        return normalized_velocity
    
    def calculate_direction_risk(self, direction_history):
        """Calculate risk based on movement direction coherence"""
        if len(direction_history) < 2:
            return 0
            
        # Calculate variance in directions (more variance = less coherent = higher risk)
        directions = np.array(direction_history)
        variance = np.var(directions)
        # Normalize (assuming max variance is π^2/4 for completely random directions)
        # π^2/4 ≈ 2.47 for directions in range [-π/2, π/2]
        normalized_variance = min(variance / 2.47, 1.0)
        return normalized_variance
    
    def calculate_acceleration_risk(self, acceleration_history):
        """Calculate risk based on acceleration changes"""
        if len(acceleration_history) < 2:
            return 0
            
        avg_acceleration = np.mean(np.abs(acceleration_history))
        # Normalize (assuming max acceleration is 1.0 pixels/frame^2 for normal movement)
        normalized_acceleration = min(avg_acceleration / 1.0, 1.0)
        return normalized_acceleration
    
    def assess_risk(self, people_count, area_pixels, velocity_history, 
                   direction_history, acceleration_history):
        """Calculate overall stampede risk score"""
        # Calculate individual risk factors
        density_risk = self.calculate_density_risk(people_count, area_pixels)
        velocity_risk = self.calculate_velocity_risk(velocity_history)
        direction_risk = self.calculate_direction_risk(direction_history)
        acceleration_risk = self.calculate_acceleration_risk(acceleration_history)
        
        # Weighted sum for overall risk
        total_risk = (
            density_risk * self.risk_factors['density'] +
            velocity_risk * self.risk_factors['velocity'] +
            direction_risk * self.risk_factors['direction'] +
            acceleration_risk * self.risk_factors['acceleration']
        )
        
        # Determine risk level
        if total_risk <= self.thresholds['low']:
            risk_level = 'LOW'
        elif total_risk <= self.thresholds['medium']:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'HIGH'
            
        return {
            'score': total_risk,
            'level': risk_level,
            'factors': {
                'density': density_risk,
                'velocity': velocity_risk,
                'direction': direction_risk,
                'acceleration': acceleration_risk
            }
        }

class CrowdDetector:
    def __init__(self, db_path='detection_database.db'):
        self.db_path = db_path
        self.net = None
        self.classes = []
        self.face_cascade = None
        self.db_conn = None
        self.db_cursor = None
        
        # Stampede prevention attributes
        self.stampede_assessor = StampedeRiskAssessment()
        self.position_history = {}  # Track positions over time
        self.velocity_history = deque(maxlen=30)  # Last 30 frames
        self.direction_history = deque(maxlen=30)
        self.acceleration_history = deque(maxlen=30)
        self.frame_history = deque(maxlen=5)  # Reduced for better performance
        
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
            # Table for stampede incidents
            self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS stampede_incidents
                                 (timestamp DATETIME, risk_level TEXT, people_count INT, 
                                  risk_score REAL, factors TEXT)''')
            self.db_conn.commit()
        except sqlite3.Error as e:
            print(f"Database Error: {e}")
            raise
    
    def detect_crowd(self, frame):
        """Detect people in frame using YOLOv3 with fallback methods"""
        # Check if models are loaded
        if self.net is None or self.face_cascade is None:
            raise RuntimeError("Models not initialized properly")
        
        # Check if database is initialized
        if self.db_conn is None or self.db_cursor is None:
            raise RuntimeError("Database not initialized properly")
        
        # Store frame for flow analysis (only if we have movement analysis enabled)
        if len(self.velocity_history) > 0 or len(self.direction_history) > 0:
            self.frame_history.append(frame.copy())
        
        # Use original frame size for better display (but process at reasonable size for performance)
        original_height, original_width = frame.shape[:2]
        # Process at a reasonable size for performance but not too small
        process_width, process_height = 640, 480
        process_frame = cv2.resize(frame, (process_width, process_height))
        
        # Calculate scaling factors for accurate coordinate mapping
        width_scale = original_width / process_width
        height_scale = original_height / process_height
        
        # Prepare frame for YOLO
        blob = cv2.dnn.blobFromImage(process_frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.get_output_layers(self.net))
        
        boxes, confidences, class_ids = [], [], []
        
        # Collect detections
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                # Increase confidence threshold for better accuracy
                if confidence > 0.6:
                    center_x = int(detection[0] * process_frame.shape[1])
                    center_y = int(detection[1] * process_frame.shape[0])
                    w = int(detection[2] * process_frame.shape[1])
                    h = int(detection[3] * process_frame.shape[0])
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    # Scale back to original frame size with improved precision
                    x = int(round(x * width_scale))
                    y = int(round(y * height_scale))
                    w = int(round(w * width_scale))
                    h = int(round(h * height_scale))
                    
                    # Ensure bounding boxes are within frame bounds
                    x = max(0, min(x, original_width - 1))
                    y = max(0, min(y, original_height - 1))
                    w = max(1, min(w, original_width - x))
                    h = max(1, min(h, original_height - y))
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        
        # NMS to remove duplicates with improved threshold for crowd detection
        indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.6, 0.3)
        
        # Process detections
        num_people = 0
        detections = []
        current_positions = {}
        
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
            
            # Filter out overlapping boxes more aggressively for better accuracy
            filtered_boxes = []
            filtered_confidences = []
            filtered_class_ids = []
            
            for idx in indices_list:
                # Ensure index is within bounds
                if idx >= len(boxes) or idx >= len(class_ids) or idx >= len(confidences):
                    continue
                
                # Additional filtering for person class only
                if str(self.classes[class_ids[idx]]) == "person":
                    filtered_boxes.append(boxes[idx])
                    filtered_confidences.append(confidences[idx])
                    filtered_class_ids.append(class_ids[idx])
            
            # Apply second round of NMS for person detections only
            if filtered_boxes:
                final_indices = cv2.dnn.NMSBoxes(filtered_boxes, filtered_confidences, 0.6, 0.3)
                
                if len(final_indices) > 0:
                    # Convert final indices
                    final_indices_list = []
                    if isinstance(final_indices, (list, tuple)):
                        for i in final_indices:
                            if isinstance(i, (int, np.integer)):
                                final_indices_list.append(int(i))
                    elif isinstance(final_indices, np.ndarray):
                        if final_indices.size > 0:
                            if final_indices.ndim > 1:
                                flat_indices = final_indices.flatten()
                            else:
                                flat_indices = final_indices
                            for i in flat_indices:
                                if isinstance(i, (int, np.integer)):
                                    final_indices_list.append(int(i))
                    else:
                        if isinstance(final_indices, (int, np.integer)):
                            final_indices_list.append(int(final_indices))
                    
                    for idx in final_indices_list:
                        # Ensure index is within bounds
                        if idx >= len(filtered_boxes) or idx >= len(filtered_class_ids) or idx >= len(filtered_confidences):
                            continue
                            
                        x, y, w, h = filtered_boxes[idx]
                        label = str(self.classes[filtered_class_ids[idx]])
                        confidence = filtered_confidences[idx]
                        
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
                            
                            # Track position for movement analysis
                            person_id = f"person_{num_people}"
                            current_positions[person_id] = (x + w/2, y + h/2)  # Center point
                            
                            # Face detection inside person bounding box (only for first few people for performance)
                            if num_people <= 3:  # Limit face detection for performance
                                # Make sure coordinates are within frame bounds
                                x1 = max(0, x)
                                y1 = max(0, y)
                                x2 = min(original_width, x + w)
                                y2 = min(original_height, y + h)
                                
                                if x2 > x1 and y2 > y1:  # Check if valid region
                                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                                    faces = self.face_cascade.detectMultiScale(gray[y1:y2, x1:x2], scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))
                                    detection['faces'] = []
                                    for (fx, fy, fw, fh) in faces:
                                        face_data = {
                                            'x': x1 + fx,
                                            'y': y1 + fy,
                                            'w': fw,
                                            'h': fh
                                        }
                                        detection['faces'].append(face_data)
        
        # Fallback detection using motion detection for better accuracy in videos
        if num_people == 0 and len(self.frame_history) >= 2:
            fallback_count = self._fallback_detection(frame)
            if fallback_count > 0:
                num_people = fallback_count
                # Update detections list if fallback found people
                step_x = original_width // (num_people + 1) if num_people > 0 else original_width // 2
                for i in range(num_people):
                    detection = {
                        'x': i * step_x if num_people > 1 else original_width // 2,
                        'y': original_height // 2,
                        'w': 50,
                        'h': 100,
                        'label': 'person',
                        'confidence': 0.7
                    }
                    detections.append(detection)
        
        # Analyze movement patterns for stampede risk (only if we have people)
        if num_people > 0:
            self._analyze_movement_patterns(current_positions)
        else:
            # Clear histories when no people detected
            self.velocity_history.clear()
            self.direction_history.clear()
            self.acceleration_history.clear()
            self.position_history.clear()
        
        # Calculate stampede risk
        area_pixels = original_width * original_height
        risk_assessment = self.stampede_assessor.assess_risk(
            num_people, area_pixels,
            list(self.velocity_history),
            list(self.direction_history),
            list(self.acceleration_history)
        )
        
        # Store high-risk incidents (only for actual high risk, not just high people count)
        if risk_assessment['level'] == 'HIGH' and risk_assessment['score'] > 0.8:
            timestamp = datetime.now()
            factors_str = str(risk_assessment['factors'])
            self.db_cursor.execute("""INSERT INTO stampede_incidents 
                                 (timestamp, risk_level, people_count, risk_score, factors) 
                                 VALUES (?, ?, ?, ?, ?)""",
                                 (timestamp, risk_assessment['level'], num_people, 
                                  risk_assessment['score'], factors_str))
            self.db_conn.commit()
        
        # Return the original frame size for proper display
        return frame, num_people, detections, risk_assessment
    
    def _analyze_movement_patterns(self, current_positions):
        """Analyze movement patterns for stampede risk"""
        if not self.position_history:
            # First frame, just store positions
            self.position_history = current_positions
            return
        
        # Calculate velocities and directions
        velocities = []
        directions = []
        
        for person_id, current_pos in current_positions.items():
            if person_id in self.position_history:
                prev_pos = self.position_history[person_id]
                # Calculate displacement
                dx = current_pos[0] - prev_pos[0]
                dy = current_pos[1] - prev_pos[1]
                
                # Calculate velocity (distance per frame)
                velocity = np.sqrt(dx**2 + dy**2)
                velocities.append(velocity)
                
                # Calculate direction (angle in radians)
                if velocity > 0:  # Avoid division by zero
                    direction = np.arctan2(dy, dx)
                    directions.append(direction)
        
        # Update histories
        if velocities:
            avg_velocity = np.mean(velocities)
            self.velocity_history.append(avg_velocity)
            
            # Calculate acceleration (change in velocity)
            if len(self.velocity_history) >= 2:
                acceleration = abs(avg_velocity - self.velocity_history[-2])
                self.acceleration_history.append(acceleration)
        
        if directions:
            # Measure coherence of directions (variance)
            avg_direction = np.mean(directions)
            self.direction_history.append(avg_direction)
        
        # Update position history
        self.position_history = current_positions
    
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
    
    def _fallback_detection(self, frame):
        """Fallback detection method using motion detection"""
        if len(self.frame_history) < 2:
            return 0
        
        # Get previous frame
        prev_frame = self.frame_history[-2]
        
        # Ensure both frames have the same size
        if prev_frame.shape != frame.shape:
            # Resize previous frame to match current frame
            prev_frame = cv2.resize(prev_frame, (frame.shape[1], frame.shape[0]))
        
        # Convert to grayscale
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate absolute difference between frames
        frame_diff = cv2.absdiff(prev_gray, curr_gray)
        
        # Apply threshold to get binary image
        _, thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)
        
        # Apply morphological operations to remove noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Count significant moving objects
        person_count = 0
        for contour in contours:
            # Calculate contour area
            area = cv2.contourArea(contour)
            # Filter by minimum area (adjust based on your needs)
            if area > 500:  # Minimum area for a person-like object
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                # Check aspect ratio (people are typically taller than wide)
                aspect_ratio = h / w if w > 0 else 0
                if 1.0 < aspect_ratio < 4.0:  # Reasonable aspect ratio for people
                    person_count += 1
        
        return person_count
    
    def get_heatmap(self, frame_shape, detections):
        """Generate crowd density heatmap"""
        if not detections:
            return np.zeros((frame_shape[0], frame_shape[1]), dtype=np.uint8)
        
        # Create heatmap
        heatmap = np.zeros((frame_shape[0], frame_shape[1]), dtype=np.uint8)
        
        # Add intensity for each person detection
        for detection in detections:
            x, y, w, h = detection['x'], detection['y'], detection['w'], detection['h']
            # Create a circular intensity around each person
            center_x, center_y = int(x + w/2), int(y + h/2)
            radius = max(w, h) // 2
            
            # Draw filled circle with decreasing intensity from center
            for i in range(radius, 0, -1):
                intensity = int(255 * (i / radius))
                cv2.circle(heatmap, (center_x, center_y), i, intensity, -1)
        
        # Apply Gaussian blur to smooth heatmap
        heatmap = cv2.GaussianBlur(heatmap, (15, 15), 0)
        return heatmap
    
    def get_flow_directions(self, frame):
        """Analyze optical flow for movement directions"""
        if len(self.frame_history) < 2:
            return None
            
        # Get last two frames
        prev_frame = self.frame_history[-2]
        curr_frame = self.frame_history[-1]
        
        # Convert to grayscale
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate optical flow - initialize flow matrix with zeros
        flow = np.zeros((prev_gray.shape[0], prev_gray.shape[1], 2), dtype=np.float32)
        flow = cv2.calcOpticalFlowFarneback(prev_gray, curr_gray, flow, 0.5, 3, 15, 3, 5, 1.2, 0)
        
        # Sample flow vectors
        step = 20  # Sample every 20 pixels
        flow_vectors = []
        
        for y in range(0, flow.shape[0], step):
            for x in range(0, flow.shape[1], step):
                fx, fy = flow[y, x]
                magnitude = np.sqrt(fx**2 + fy**2)
                # Only consider significant movements
                if magnitude > 1.0:
                    direction = np.arctan2(fy, fx)
                    flow_vectors.append({
                        'x': x,
                        'y': y,
                        'direction': direction,
                        'magnitude': magnitude
                    })
        
        return flow_vectors
    
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
    
    def get_stampede_incidents(self, limit=50):
        """Get recent stampede incidents"""
        # Check if database is initialized
        if self.db_conn is None or self.db_cursor is None:
            raise RuntimeError("Database not initialized properly")
            
        try:
            self.db_cursor.execute("SELECT * FROM stampede_incidents ORDER BY timestamp DESC LIMIT ?", (limit,))
            return self.db_cursor.fetchall()
        except Exception as e:
            print(f"Error fetching stampede incidents: {e}")
            return []
    
    def reset_database(self):
        """Clear all detection data"""
        # Check if database is initialized
        if self.db_conn is None:
            raise RuntimeError("Database not initialized properly")
        
        try:
            self.db_conn.execute("DELETE FROM object_detections")
            self.db_conn.execute("DELETE FROM face_detections")
            self.db_conn.execute("DELETE FROM stampede_incidents")
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
    
    def export_stampede_report(self, filepath):
        """Export stampede incident report to CSV"""
        # Check if database is initialized
        if self.db_conn is None or self.db_cursor is None:
            raise RuntimeError("Database not initialized properly")
            
        try:
            import csv
            self.db_cursor.execute("SELECT * FROM stampede_incidents")
            rows = self.db_cursor.fetchall()
            
            with open(filepath, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Risk Level", "People Count", "Risk Score", "Factors"])
                writer.writerows(rows)
            return True
        except Exception as e:
            print(f"Error exporting stampede report: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if hasattr(self, 'db_conn') and self.db_conn:
            self.db_conn.close()