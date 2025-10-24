import sys
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QImage, QPixmap, QFont, QIcon, QColor, QPalette
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, 
                             QMessageBox, QGridLayout, QFrame, QVBoxLayout, 
                             QHBoxLayout, QGroupBox, QProgressBar, QComboBox,
                             QStatusBar, QToolBar, QAction, QTabWidget, QTextEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog)
import cv2
import numpy as np
import sqlite3
from datetime import datetime
import winsound
import csv
import os


class ModernApp(QWidget):
    def __init__(self):
        super().__init__()
        self.cam_id = 0  # Default camera ID
        self.title = 'Advanced Crowd Management System'
        self.left_pos = 50
        self.top_pos = 50
        self.window_width = 1200
        self.window_height = 800
        self.detected_crowd = False
        self.alert_level = 0  # 0: Normal, 1: Caution, 2: Warning, 3: Critical
        self.initUI()

        # Database setup
        try:
            self.db_conn = sqlite3.connect('detection_database.db')
            self.db_cursor = self.db_conn.cursor()
            self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS object_detections
                                 (timestamp DATETIME, object_label TEXT, confidence REAL)''')
            self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS face_detections
                                 (timestamp DATETIME, x INT, y INT, width INT, height INT, unique_id INT)''')
            self.db_conn.commit()
        except sqlite3.Error as e:
            print("SQLite Error:", e)
            self.db_conn.close()
            exit(1)

        # Load YOLO
        self.net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
        with open("coco.names", "r") as f:
            self.classes = f.read().strip().split("\n")

        # Face detection
        # Use the direct path to the cascade file
        cascade_path = "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.detected_faces = {}
        self.next_unique_id = 1

        # FPS variables
        self.prev_time = datetime.now()
        self.frame_count = 0
        self.frame_rate = 0
        
        # Continuous sound timer
        self.sound_timer = QTimer(self)
        self.sound_timer.timeout.connect(self.play_alert_sound)
        
        # Statistics
        self.total_detections = 0
        self.peak_crowd_count = 0
        self.alert_history = []
        
        # Apply modern stylesheet
        self.apply_stylesheet()

    def apply_stylesheet(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #3daee9;
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #4db8ff;
            }
            QPushButton:pressed {
                background-color: #2e86c1;
            }
            QPushButton#startBtn {
                background-color: #27ae60;
            }
            QPushButton#startBtn:hover {
                background-color: #2ecc71;
            }
            QPushButton#stopBtn {
                background-color: #e74c3c;
            }
            QPushButton#stopBtn:hover {
                background-color: #ff6b6b;
            }
            QPushButton#resetBtn {
                background-color: #f39c12;
            }
            QPushButton#resetBtn:hover {
                background-color: #f7dc6f;
            }
            QPushButton#exportBtn {
                background-color: #9b59b6;
            }
            QPushButton#exportBtn:hover {
                background-color: #bb8fce;
            }
            QGroupBox {
                border: 2px solid #3daee9;
                border-radius: 8px;
                margin-top: 1ex;
                font-weight: bold;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: #3daee9;
                color: white;
                border-radius: 3px;
            }
            QLabel {
                color: #ffffff;
            }
            QLabel#headerLabel {
                color: white;
                background-color: #3daee9;
                padding: 15px;
                font-size: 20px;
                font-weight: bold;
                border-radius: 8px;
            }
            QLabel#videoLabel {
                background-color: black;
                border: 2px solid #3daee9;
                border-radius: 4px;
            }
            QLabel#counterLabel {
                font-size: 18px;
                font-weight: bold;
                color: #27ae60;
                padding: 10px;
                background-color: #333333;
                border-radius: 6px;
            }
            QLabel#alertLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                border-radius: 6px;
                background-color: #333333;
            }
            QLabel#indicator {
                border-radius: 30px;
                border: 3px solid #ffffff;
            }
            QComboBox {
                background-color: #333333;
                color: white;
                border: 1px solid #3daee9;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #333333;
                color: white;
                selection-background-color: #3daee9;
            }
            QTableWidget {
                background-color: #333333;
                alternate-background-color: #3a3a3a;
                gridline-color: #555555;
                color: white;
            }
            QTableWidget::item:selected {
                background-color: #3daee9;
            }
            QHeaderView::section {
                background-color: #3daee9;
                color: white;
                padding: 5px;
                border: 1px solid #555555;
            }
            QTabWidget::pane {
                border: 1px solid #3daee9;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #333333;
                color: white;
                padding: 8px 12px;
                border: 1px solid #3daee9;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #3daee9;
                font-weight: bold;
            }
        """)

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left_pos, self.top_pos, self.window_width, self.window_height)

        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        self.setLayout(main_layout)

        # Header
        header_label = QLabel('Advanced Crowd Management System', self)
        header_label.setObjectName("headerLabel")
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)

        # Create central widget with horizontal layout
        central_widget = QWidget()
        central_layout = QHBoxLayout()
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(central_layout)
        main_layout.addWidget(central_widget)

        # Video display area
        video_group = QGroupBox("Live Video Feed")
        video_layout = QVBoxLayout()
        video_layout.setContentsMargins(10, 10, 10, 10)
        video_group.setLayout(video_layout)

        self.label = QLabel(self)
        self.label.setObjectName("videoLabel")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMinimumSize(700, 500)
        self.label.setText("Camera Feed Not Started")
        video_layout.addWidget(self.label)

        # Stats panel
        stats_layout = QHBoxLayout()
        self.people_counter_label = QLabel('People Count: 0', self)
        self.people_counter_label.setObjectName("counterLabel")
        self.people_counter_label.setAlignment(Qt.AlignCenter)
        
        self.fps_label = QLabel('FPS: 0.00', self)
        self.fps_label.setObjectName("counterLabel")
        self.fps_label.setAlignment(Qt.AlignCenter)
        
        stats_layout.addWidget(self.people_counter_label)
        stats_layout.addWidget(self.fps_label)
        video_layout.addLayout(stats_layout)

        video_layout.addStretch()
        central_layout.addWidget(video_group)

        # Control panel
        control_panel = QGroupBox("Control Panel")
        control_layout = QVBoxLayout()
        control_layout.setContentsMargins(10, 10, 10, 10)
        control_panel.setLayout(control_layout)
        control_panel.setMaximumWidth(400)

        # Camera controls
        camera_group = QGroupBox("Camera Controls")
        camera_layout = QGridLayout()
        camera_layout.setContentsMargins(10, 10, 10, 10)
        camera_layout.setSpacing(10)
        camera_group.setLayout(camera_layout)

        self.button_start = QPushButton('Start Camera', self)
        self.button_start.setObjectName("startBtn")
        self.button_start.clicked.connect(self.start_camera)
        self.button_start.setToolTip('Start camera')

        self.button_stop = QPushButton('Stop Camera', self)
        self.button_stop.setObjectName("stopBtn")
        self.button_stop.clicked.connect(self.stop_camera)
        self.button_stop.setToolTip('Stop camera')
        self.button_stop.setEnabled(False)

        self.button_change_feed = QPushButton('Change Camera Feed', self)
        self.button_change_feed.clicked.connect(self.change_camera_feed)
        self.button_change_feed.setToolTip('Change camera feed')

        self.camera_selector = QComboBox()
        self.camera_selector.addItem("Primary Camera (0)")
        self.camera_selector.addItem("Secondary Camera (1)")
        self.camera_selector.currentIndexChanged.connect(self.change_camera_index)

        camera_layout.addWidget(self.button_start, 0, 0)
        camera_layout.addWidget(self.button_stop, 0, 1)
        camera_layout.addWidget(self.button_change_feed, 1, 0, 1, 2)
        camera_layout.addWidget(QLabel("Select Camera:"), 2, 0)
        camera_layout.addWidget(self.camera_selector, 2, 1)
        control_layout.addWidget(camera_group)

        # Alert controls
        alert_group = QGroupBox("Alert Settings")
        alert_layout = QVBoxLayout()
        alert_layout.setContentsMargins(10, 10, 10, 10)
        alert_group.setLayout(alert_layout)

        # Threshold settings
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Alert Threshold:"))
        self.threshold_selector = QComboBox()
        self.threshold_selector.addItem("Low (10 people)")
        self.threshold_selector.addItem("Medium (20 people)")
        self.threshold_selector.addItem("High (30 people)")
        self.threshold_selector.setCurrentIndex(2)  # Default to High
        threshold_layout.addWidget(self.threshold_selector)
        alert_layout.addLayout(threshold_layout)

        # Alert indicator
        indicator_layout = QVBoxLayout()
        indicator_layout.setAlignment(Qt.AlignCenter)
        self.crowd_indicator_label = QLabel('Crowd Status', self)
        self.crowd_indicator_label.setAlignment(Qt.AlignCenter)
        self.crowd_indicator = QLabel(self)
        self.crowd_indicator.setObjectName("indicator")
        self.crowd_indicator.setFixedSize(60, 60)
        self.crowd_indicator.setStyleSheet("background-color: green")
        self.crowd_indicator.setAlignment(Qt.AlignCenter)
        self.on_screen_alert = QLabel('', self)
        self.on_screen_alert.setObjectName("alertLabel")
        self.on_screen_alert.setAlignment(Qt.AlignCenter)
        indicator_layout.addWidget(self.crowd_indicator_label)
        indicator_layout.addWidget(self.crowd_indicator)
        indicator_layout.addWidget(self.on_screen_alert)
        alert_layout.addLayout(indicator_layout)

        control_layout.addWidget(alert_group)

        # Data controls
        data_group = QGroupBox("Data Management")
        data_layout = QGridLayout()
        data_layout.setContentsMargins(10, 10, 10, 10)
        data_layout.setSpacing(10)
        data_group.setLayout(data_layout)

        self.button_reset_database = QPushButton('Reset Database', self)
        self.button_reset_database.setObjectName("resetBtn")
        self.button_reset_database.clicked.connect(self.reset_database)
        self.button_reset_database.setToolTip('Reset database')

        self.button_export_data = QPushButton('Export Data', self)
        self.button_export_data.setObjectName("exportBtn")
        self.button_export_data.clicked.connect(self.export_data)
        self.button_export_data.setToolTip('Export detection data to CSV')

        data_layout.addWidget(self.button_reset_database, 0, 0)
        data_layout.addWidget(self.button_export_data, 0, 1)
        control_layout.addWidget(data_group)

        # Statistics panel
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()
        stats_layout.setContentsMargins(10, 10, 10, 10)
        stats_group.setLayout(stats_layout)

        self.stats_label = QLabel("Total Detections: 0\nPeak Crowd: 0", self)
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)
        control_layout.addWidget(stats_group)

        control_layout.addStretch()
        central_layout.addWidget(control_panel)

        # Tabbed section for additional information
        tab_widget = QTabWidget()
        tab_widget.setMinimumHeight(150)
        
        # Detection history tab
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(3)
        self.history_table.setHorizontalHeaderLabels(["Timestamp", "Object", "Confidence"])
        # Fix for table header
        header = self.history_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.Stretch)
        tab_widget.addTab(self.history_table, "Detection History")
        
        # Alert log tab
        self.alert_log = QTextEdit()
        self.alert_log.setReadOnly(True)
        tab_widget.addTab(self.alert_log, "Alert Log")
        
        main_layout.addWidget(tab_widget)

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready")
        main_layout.addWidget(self.status_bar)

        self.show()

    def change_camera_index(self, index):
        self.cam_id = index
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.stop_camera()
            self.start_camera()

    def play_alert_sound(self):
        # Different sounds for different alert levels
        if self.alert_level == 1:  # Caution
            winsound.Beep(800, 300)
        elif self.alert_level == 2:  # Warning
            winsound.Beep(1000, 500)
        elif self.alert_level == 3:  # Critical
            winsound.Beep(1200, 700)

    def start_camera(self):
        self.cap = cv2.VideoCapture(self.cam_id)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Camera Error", "Failed to open camera. Please check your camera connection.")
            return
            
        self.timer = self.startTimer(30)  # Call timer every 30 ms for smoother video
        self.button_start.setEnabled(False)
        self.button_stop.setEnabled(True)
        self.button_change_feed.setEnabled(False)
        self.status_bar.showMessage("Camera started")

    def stop_camera(self):
        if hasattr(self, 'timer'):
            self.killTimer(self.timer)
        if hasattr(self, 'cap'):
            self.cap.release()
        self.sound_timer.stop()
        winsound.PlaySound(None, winsound.SND_PURGE)
        self.button_start.setEnabled(True)
        self.button_stop.setEnabled(False)
        self.button_change_feed.setEnabled(True)
        self.label.setText("Camera Feed Not Started")
        self.status_bar.showMessage("Camera stopped")

    def change_camera_feed(self):
        self.cam_id = 1 - self.cam_id  # Toggle camera
        self.camera_selector.setCurrentIndex(self.cam_id)
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.stop_camera()
            self.start_camera()
        msg = QMessageBox()
        msg.setWindowTitle("Change Camera Feed")
        msg.setText(f"Switched to Camera Feed {self.cam_id}")
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    def reset_database(self):
        reply = QMessageBox.question(self, 'Reset Database', 
                                   'Are you sure you want to reset the database? This action cannot be undone.',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db_conn.execute("DELETE FROM object_detections")
            self.db_conn.execute("DELETE FROM face_detections")
            self.db_conn.commit()
            self.total_detections = 0
            self.peak_crowd_count = 0
            self.update_stats_display()
            self.history_table.setRowCount(0)
            self.alert_log.clear()
            self.status_bar.showMessage("Database reset successfully")

    def export_data(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Data", "", "CSV Files (*.csv)")
        if file_path:
            try:
                # Export object detections
                self.db_cursor.execute("SELECT * FROM object_detections")
                rows = self.db_cursor.fetchall()
                
                with open(file_path, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Timestamp", "Object Label", "Confidence"])
                    writer.writerows(rows)
                
                QMessageBox.information(self, "Export Successful", f"Data exported successfully to {file_path}")
                self.status_bar.showMessage(f"Data exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export data: {str(e)}")

    def calculate_frame_rate(self):
        current_time = datetime.now()
        elapsed_time = current_time - self.prev_time
        if elapsed_time.seconds >= 1:
            self.frame_rate = self.frame_count / elapsed_time.seconds
            self.frame_count = 0
            self.prev_time = current_time
        return self.frame_rate

    def update_stats_display(self):
        self.stats_label.setText(f"Total Detections: {self.total_detections}\nPeak Crowd: {self.peak_crowd_count}")

    def update_alert_indicator(self, level):
        """Update the crowd indicator based on alert level"""
        colors = {
            0: "green",      # Normal
            1: "yellow",     # Caution
            2: "orange",     # Warning
            3: "red"         # Critical
        }
        
        self.alert_level = level
        color = colors.get(level, "green")
        self.crowd_indicator.setStyleSheet(f"background-color: {color}; border-radius: 30px; border: 3px solid white;")

    def timerEvent(self, event):
        if not hasattr(self, 'cap') or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.resize(frame, (700, 500))
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

        num_people = 0
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        
        if len(indices) > 0:
            for i in indices.flatten():
                x, y, w, h = boxes[i]
                label = str(self.classes[class_ids[i]])
                confidence = confidences[i]

                if label == "person":
                    num_people += 1
                    color = (0, 255, 0)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, f"{label} {confidence:.2f}",
                                 (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                    # Save object detection
                    timestamp = datetime.now()
                    self.db_cursor.execute("INSERT INTO object_detections (timestamp, object_label, confidence) VALUES (?, ?, ?)",
                                         (timestamp, label, confidence))
                    self.db_conn.commit()
                    
                    # Add to history table
                    row_position = self.history_table.rowCount()
                    self.history_table.insertRow(row_position)
                    self.history_table.setItem(row_position, 0, QTableWidgetItem(str(timestamp)))
                    self.history_table.setItem(row_position, 1, QTableWidgetItem(label))
                    self.history_table.setItem(row_position, 2, QTableWidgetItem(f"{confidence:.2f}"))
                    
                    # Keep only last 100 entries
                    if row_position > 100:
                        self.history_table.removeRow(0)
                    
                    self.total_detections += 1

                    # Face detection inside person bounding box
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = self.face_cascade.detectMultiScale(gray[y:y+h, x:x+w], scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))
                    for (fx, fy, fw, fh) in faces:
                        cv2.rectangle(frame, (x + fx, y + fy), (x + fx + fw, y + fy + fh), (0, 0, 255), 2)
        
        # Update peak crowd count
        if num_people > self.peak_crowd_count:
            self.peak_crowd_count = num_people
            
        # Update people counter label
        self.people_counter_label.setText(f'People Count: {num_people}')
        
        # Get alert threshold
        thresholds = [10, 20, 30]  # Low, Medium, High
        threshold = thresholds[self.threshold_selector.currentIndex()]
        
        # Update alert level based on crowd size
        if num_people == 0:
            alert_level = 0
            self.on_screen_alert.setText('')
        elif num_people < threshold * 0.5:
            alert_level = 0  # Normal
            self.on_screen_alert.setText('')
        elif num_people < threshold * 0.8:
            alert_level = 1  # Caution
            self.on_screen_alert.setText('CAUTION: Moderate Crowd')
            self.on_screen_alert.setStyleSheet("color: yellow; font-size: 16px; font-weight: bold; padding: 10px; border-radius: 6px; background-color: #333333;")
        elif num_people < threshold:
            alert_level = 2  # Warning
            self.on_screen_alert.setText('WARNING: Large Crowd')
            self.on_screen_alert.setStyleSheet("color: orange; font-size: 16px; font-weight: bold; padding: 10px; border-radius: 6px; background-color: #333333;")
        else:
            alert_level = 3  # Critical
            self.on_screen_alert.setText('CRITICAL: Overcrowding Detected!')
            self.on_screen_alert.setStyleSheet("color: red; font-size: 16px; font-weight: bold; padding: 10px; border-radius: 6px; background-color: #333333;")
            
            # Add to alert log
            alert_msg = f"{current_time}: CRITICAL - {num_people} people detected (threshold: {threshold})"
            self.alert_log.append(alert_msg)
        
        # Update alert indicator
        self.update_alert_indicator(alert_level)
        
        # Handle sound alerts
        if alert_level > 0 and not self.sound_timer.isActive():
            # Play sound every 2 seconds for warning, every 1 second for critical
            interval = 2000 if alert_level == 2 else 1000
            self.sound_timer.start(interval)
        elif alert_level == 0 and self.sound_timer.isActive():
            self.sound_timer.stop()
            winsound.PlaySound(None, winsound.SND_PURGE)

        # Update statistics display
        self.update_stats_display()

        # FPS counter
        self.frame_count += 1
        fps = self.calculate_frame_rate()
        self.fps_label.setText(f'FPS: {fps:.2f}')
        cv2.putText(frame, f'FPS: {fps:.2f}', (10, 30),
                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Convert frame BGR -> RGB for Qt
        rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgbImage.shape
        bytesPerLine = ch * w
        qImg = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(qImg))

    def get_output_layers(self, net):
        layer_names = net.getLayerNames()
        return [layer_names[i - 1] for i in net.getUnconnectedOutLayers().flatten()]


def main():
    """Main function to run the Crowd Management System"""
    app = QApplication(sys.argv)
    # Set application style
    app.setStyle('Fusion')
    ex = ModernApp()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
