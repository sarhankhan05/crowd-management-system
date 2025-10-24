from flask import Flask, render_template, jsonify, request, Response
import cv2
import threading
import time
from core.detection import CrowdDetector
import os
from config import Config

app = Flask(__name__, 
            template_folder=Config.TEMPLATE_DIR,
            static_folder=Config.STATIC_DIR)

# Global variables
detector = None
camera = None
camera_lock = threading.Lock()
detection_thread = None
stop_detection = False
current_frame = None
frame_lock = threading.Lock()
detection_stats = {
    'people_count': 0,
    'alert_level': 0,
    'fps': 0
}

def initialize_detector():
    """Initialize the crowd detector"""
    global detector
    try:
        detector = CrowdDetector(Config.DATABASE_FILE)
        print("Detector initialized successfully")
    except Exception as e:
        print(f"Error initializing detector: {e}")
        detector = None

def detect_crowd_continuously():
    """Continuously detect crowd in a separate thread"""
    global camera, current_frame, detection_stats, stop_detection, detector
    
    frame_count = 0
    start_time = time.time()
    
    while not stop_detection:
        with camera_lock:
            if camera is None or not camera.isOpened():
                time.sleep(0.1)
                continue
            
            ret, frame = camera.read()
            if not ret:
                time.sleep(0.1)
                continue
        
        if detector is not None:
            try:
                processed_frame, people_count, detections = detector.detect_crowd(frame)
                
                # Update detection stats
                detection_stats['people_count'] = people_count
                
                # Calculate alert level based on people count
                if people_count <= Config.ALERT_THRESHOLDS["CAUTION"]:
                    detection_stats['alert_level'] = 0  # Normal
                elif people_count <= Config.ALERT_THRESHOLDS["WARNING"]:
                    detection_stats['alert_level'] = 1  # Caution
                elif people_count <= Config.ALERT_THRESHOLDS["CRITICAL"]:
                    detection_stats['alert_level'] = 2  # Warning
                else:
                    detection_stats['alert_level'] = 3  # Critical
                
                # Calculate FPS
                frame_count += 1
                if frame_count % 30 == 0:  # Update FPS every 30 frames
                    elapsed_time = time.time() - start_time
                    detection_stats['fps'] = int(round(frame_count / elapsed_time, 2))
                    frame_count = 0
                    start_time = time.time()
                
                # Store the processed frame
                with frame_lock:
                    current_frame = processed_frame
                    
            except Exception as e:
                print(f"Error in detection: {e}")
                with frame_lock:
                    current_frame = frame
        
        time.sleep(0.03)  # ~30 FPS

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/start_camera')
def start_camera():
    """Start camera feed"""
    global camera, detection_thread, stop_detection
    
    with camera_lock:
        if camera is not None and camera.isOpened():
            return jsonify({'status': 'error', 'message': 'Camera already started'})
        
        # Try to open camera
        camera = cv2.VideoCapture(Config.DEFAULT_CAMERA_ID)
        if not camera.isOpened():
            return jsonify({'status': 'error', 'message': 'Failed to open camera'})
    
    # Start detection thread
    stop_detection = False
    detection_thread = threading.Thread(target=detect_crowd_continuously)
    detection_thread.daemon = True
    detection_thread.start()
    
    return jsonify({'status': 'success', 'message': 'Camera started'})

@app.route('/stop_camera')
def stop_camera():
    """Stop camera feed"""
    global camera, stop_detection
    
    stop_detection = True
    
    with camera_lock:
        if camera is not None:
            camera.release()
            camera = None
    
    return jsonify({'status': 'success', 'message': 'Camera stopped'})

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    def generate_frames():
        global current_frame
        while True:
            with frame_lock:
                if current_frame is not None:
                    # Encode frame as JPEG
                    ret, buffer = cv2.imencode('.jpg', current_frame)
                    if ret:
                        frame_bytes = buffer.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.03)  # ~30 FPS
    
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stats')
def get_stats():
    """Get current detection statistics"""
    return jsonify(detection_stats)

@app.route('/history')
def get_history():
    """Get detection history"""
    if detector is None:
        return jsonify({'status': 'error', 'message': 'Detector not initialized'})
    
    try:
        history = detector.get_detection_history()
        return jsonify({'status': 'success', 'data': history})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/reset_database')
def reset_database():
    """Reset detection database"""
    if detector is None:
        return jsonify({'status': 'error', 'message': 'Detector not initialized'})
    
    try:
        detector.reset_database()
        return jsonify({'status': 'success', 'message': 'Database reset'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/export_data')
def export_data():
    """Export detection data"""
    if detector is None:
        return jsonify({'status': 'error', 'message': 'Detector not initialized'})
    
    try:
        # Generate filename with timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"detection_data_{timestamp}.csv"
        
        # Export to file
        if detector.export_data(filename):
            return jsonify({'status': 'success', 'message': f'Data exported to {filename}'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to export data'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

def main():
    """Main function to run the Crowd Management System"""
    print("Starting Advanced Crowd Management System...")
    
    # Initialize detector
    initialize_detector()
    
    # Run Flask app
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG, threaded=True)

if __name__ == '__main__':
    main()