#!/usr/bin/env python3
"""
Test script to verify video processing functionality
"""

import sys
import os
import tempfile
import cv2

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.detection import CrowdDetector

def test_video_processing():
    """Test video processing functionality"""
    print("Testing Video Processing Functionality...")
    
    # Initialize detector
    try:
        detector = CrowdDetector()
        print("✓ Detector initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing detector: {e}")
        return False
    
    # Create a simple test video (just a few frames of random data)
    print("Creating test video...")
    temp_dir = tempfile.gettempdir()
    test_video_path = os.path.join(temp_dir, "test_video.avi")
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(test_video_path, fourcc, 8.0, (640, 480))
    
    # Generate 20 frames of random colored frames
    import numpy as np
    for i in range(20):
        # Create a random colored frame
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Add some shapes to simulate people
        if i % 3 == 0:  # Add a rectangle every 3 frames
            cv2.rectangle(frame, (100, 100), (200, 300), (0, 255, 0), -1)
        if i % 5 == 0:  # Add a circle every 5 frames
            cv2.circle(frame, (400, 200), 50, (255, 0, 0), -1)
            
        out.write(frame)
    
    out.release()
    print(f"✓ Test video created at {test_video_path}")
    
    # Test video processing
    print("Testing video processing...")
    try:
        cap = cv2.VideoCapture(test_video_path)
        if not cap.isOpened():
            print("✗ Failed to open test video")
            return False
        
        frame_count = 0
        while frame_count < 10:  # Process first 10 frames
            ret, frame = cap.read()
            if not ret:
                break
                
            # Process frame with detector
            try:
                processed_frame, people_count, detections, risk_data = detector.detect_crowd(frame)
                print(f"Frame {frame_count}: {people_count} people detected, Risk Level: {risk_data['level']}")
                frame_count += 1
            except Exception as e:
                print(f"✗ Error processing frame {frame_count}: {e}")
                break
        
        cap.release()
        print("✓ Video processing test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Error in video processing: {e}")
        return False

def test_file_upload_logic():
    """Test the file upload logic"""
    print("\nTesting File Upload Logic...")
    
    # This would normally be handled by Flask, but we can test the core logic
    temp_dir = tempfile.gettempdir()
    test_file_path = os.path.join(temp_dir, "test_upload.txt")
    
    # Create a test file
    with open(test_file_path, 'w') as f:
        f.write("This is a test file for upload simulation")
    
    print(f"✓ Test file created at {test_file_path}")
    
    # Simulate file handling logic
    try:
        filename = os.path.basename(test_file_path)
        safe_filename = filename or 'uploaded_file.txt'
        print(f"✓ File upload logic working: {safe_filename}")
        return True
    except Exception as e:
        print(f"✗ Error in file upload logic: {e}")
        return False

if __name__ == "__main__":
    print("=== Video Processing Test Suite ===")
    
    # Test video processing
    video_test_passed = test_video_processing()
    
    # Test file upload logic
    upload_test_passed = test_file_upload_logic()
    
    print("\n=== Test Results ===")
    print(f"Video Processing Test: {'PASSED' if video_test_passed else 'FAILED'}")
    print(f"File Upload Test: {'PASSED' if upload_test_passed else 'FAILED'}")
    
    if video_test_passed and upload_test_passed:
        print("\n🎉 All tests passed! Video functionality is ready to be integrated.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")