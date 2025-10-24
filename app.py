from flask import Flask, render_template, jsonify, request, Response
import cv2
import threading
import time
from core.detection import CrowdDetector
import os
from config import Config
import numpy as np
import tempfile

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
    'fps': 0,
    'stampede_risk': {
        'score': 0.0,
        'level': 'LOW',
        'factors': {}
    }
}

# Video processing variables
video_capture = None
video_processing = False
video_filename = None

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
    last_stats_update = time.time()
    
    while not stop_detection:
        with camera_lock:
            if camera is None or not camera.isOpened():
                time.sleep(0.005)  # Very short sleep for better responsiveness
                continue
            
            ret, frame = camera.read()
            if not ret:
                time.sleep(0.005)  # Very short sleep
                continue
        
        if detector is not None:
            try:
                processed_frame, people_count, detections, risk_data = detector.detect_crowd(frame)
                
                # Update detection stats more frequently for real-time updates
                current_time = time.time()
                if current_time - last_stats_update >= 0.1:  # Update every 100ms for real-time feel
                    # Update detection stats
                    detection_stats['people_count'] = people_count
                    
                    # Update stampede risk data
                    detection_stats['stampede_risk'] = risk_data
                    
                    # Calculate alert level based on people count and stampede risk
                    # Fix: Use risk_data['level'] instead of risk_data['risk_level']
                    risk_level = risk_data.get('level', 'LOW')
                    if risk_level == 'HIGH':
                        detection_stats['alert_level'] = 4  # Stampede Risk
                    elif risk_level == 'MEDIUM':
                        detection_stats['alert_level'] = 3  # High Risk
                    elif people_count <= Config.ALERT_THRESHOLDS["CAUTION"]:
                        detection_stats['alert_level'] = 0  # Normal
                    elif people_count <= Config.ALERT_THRESHOLDS["WARNING"]:
                        detection_stats['alert_level'] = 1  # Caution
                    elif people_count <= Config.ALERT_THRESHOLDS["CRITICAL"]:
                        detection_stats['alert_level'] = 2  # Warning
                    else:
                        detection_stats['alert_level'] = 3  # Critical
                    
                    # Calculate FPS more frequently for better accuracy
                    frame_count += 1
                    if frame_count % 10 == 0:  # Update FPS every 10 frames
                        elapsed_time = time.time() - start_time
                        if elapsed_time > 0:  # Avoid division by zero
                            detection_stats['fps'] = round(frame_count / elapsed_time, 2)
                        frame_count = 0
                        start_time = time.time()
                    
                    last_stats_update = current_time
                
                # Store the processed frame
                with frame_lock:
                    current_frame = processed_frame
                    
            except Exception as e:
                print(f"Error in detection: {e}")
                with frame_lock:
                    current_frame = frame
        
        # Very short sleep for maximum performance
        time.sleep(0.001)

def process_video_continuously():
    """Process uploaded video in a separate thread"""
    global video_capture, current_frame, detection_stats, video_processing, detector
    
    frame_count = 0
    start_time = time.time()
    last_stats_update = time.time()
    
    # Get video FPS for better timing
    fps = video_capture.get(cv2.CAP_PROP_FPS) if video_capture else 30
    frame_delay = 1.0 / fps if fps > 0 else 0.033  # Default to 30 FPS if unknown
    
    while video_processing and video_capture is not None:
        ret, frame = video_capture.read()
        if not ret:
            # End of video
            video_processing = False
            break
            
        if detector is not None:
            try:
                processed_frame, people_count, detections, risk_data = detector.detect_crowd(frame)
                
                # Update detection stats more frequently for real-time updates
                current_time = time.time()
                if current_time - last_stats_update >= 0.1:  # Update every 100ms for real-time feel
                    # Update detection stats
                    detection_stats['people_count'] = people_count
                    
                    # Update stampede risk data
                    detection_stats['stampede_risk'] = risk_data
                    
                    # Calculate alert level based on people count and stampede risk
                    risk_level = risk_data.get('level', 'LOW')
                    if risk_level == 'HIGH':
                        detection_stats['alert_level'] = 4  # Stampede Risk
                    elif risk_level == 'MEDIUM':
                        detection_stats['alert_level'] = 3  # High Risk
                    elif people_count <= Config.ALERT_THRESHOLDS["CAUTION"]:
                        detection_stats['alert_level'] = 0  # Normal
                    elif people_count <= Config.ALERT_THRESHOLDS["WARNING"]:
                        detection_stats['alert_level'] = 1  # Caution
                    elif people_count <= Config.ALERT_THRESHOLDS["CRITICAL"]:
                        detection_stats['alert_level'] = 2  # Warning
                    else:
                        detection_stats['alert_level'] = 3  # Critical
                    
                    # Calculate FPS more frequently for better accuracy
                    frame_count += 1
                    if frame_count % 10 == 0:  # Update FPS every 10 frames
                        elapsed_time = time.time() - start_time
                        if elapsed_time > 0:  # Avoid division by zero
                            detection_stats['fps'] = round(frame_count / elapsed_time, 2)
                        frame_count = 0
                        start_time = time.time()
                    
                    last_stats_update = current_time
                
                # Store the processed frame
                with frame_lock:
                    current_frame = processed_frame
                    
            except Exception as e:
                print(f"Error in video processing: {e}")
                with frame_lock:
                    current_frame = frame
        
        # Sleep to match video FPS for accurate real-time processing
        time.sleep(frame_delay)

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

@app.route('/upload_video', methods=['POST'])
def upload_video():
    """Handle video upload"""
    global video_filename
    
    try:
        if 'video' not in request.files:
            return jsonify({'status': 'error', 'message': 'No video file provided'})
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No video file selected'})
        
        if file:
            # Save video to temporary file
            temp_dir = tempfile.gettempdir()
            video_filename = os.path.join(temp_dir, file.filename or 'uploaded_video.mp4')
            file.save(video_filename)
            return jsonify({'status': 'success', 'message': 'Video uploaded successfully', 'filename': file.filename})
        else:
            # This case should not happen, but return an error just in case
            return jsonify({'status': 'error', 'message': 'No video file provided'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/process_video', methods=['POST'])
def process_video():
    """Start processing uploaded video"""
    global video_capture, video_processing, video_filename
    
    try:
        if video_filename is None:
            return jsonify({'status': 'error', 'message': 'No video uploaded'})
        
        # Open video file
        video_capture = cv2.VideoCapture(video_filename)
        if not video_capture.isOpened():
            return jsonify({'status': 'error', 'message': 'Failed to open video file'})
        
        # Start video processing thread
        video_processing = True
        video_thread = threading.Thread(target=process_video_continuously)
        video_thread.daemon = True
        video_thread.start()
        
        return jsonify({'status': 'success', 'message': 'Video processing started'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/stop_video')
def stop_video():
    """Stop video processing"""
    global video_capture, video_processing
    
    video_processing = False
    
    if video_capture is not None:
        video_capture.release()
        video_capture = None
    
    return jsonify({'status': 'success', 'message': 'Video processing stopped'})

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    def generate_frames():
        global current_frame
        while True:
            with frame_lock:
                if current_frame is not None:
                    # Encode frame as JPEG with quality setting for better performance
                    ret, buffer = cv2.imencode('.jpg', current_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                    if ret:
                        frame_bytes = buffer.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.01)  # Short sleep for streaming FPS
    
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

@app.route('/stampede_incidents')
def get_stampede_incidents():
    """Get stampede incidents"""
    if detector is None:
        return jsonify({'status': 'error', 'message': 'Detector not initialized'})
    
    try:
        incidents = detector.get_stampede_incidents()
        return jsonify({'status': 'success', 'data': incidents})
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

@app.route('/export_stampede_report')
def export_stampede_report():
    """Export stampede incident report"""
    if detector is None:
        return jsonify({'status': 'error', 'message': 'Detector not initialized'})
    
    try:
        # Generate filename with timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stampede_report_{timestamp}.csv"
        
        # Export to file
        if detector.export_stampede_report(filename):
            return jsonify({'status': 'success', 'message': f'Stampede report exported to {filename}'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to export stampede report'})
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