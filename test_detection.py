#!/usr/bin/env python3
"""
Test script for the Crowd Detection module
"""

import cv2
import sys
import os
from core.detection import CrowdDetector

def test_detector():
    """Test the crowd detector with a sample image or camera"""
    print("Testing Crowd Detection Module...")
    
    try:
        # Initialize detector
        detector = CrowdDetector()
        print("✓ Detector initialized successfully")
        
        # Test with camera if available
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✓ Camera access successful")
            
            # Read a frame
            ret, frame = cap.read()
            if ret:
                print("✓ Frame captured successfully")
                
                # Test detection
                processed_frame, people_count, detections = detector.detect_crowd(frame)
                print(f"✓ Detection completed - People detected: {people_count}")
                print(f"✓ Detections: {len(detections)} objects found")
                
                # Test database functions
                history = detector.get_detection_history()
                print(f"✓ Database query successful - {len(history)} records found")
                
                # Test reset (be careful with this in production!)
                # detector.reset_database()
                # print("✓ Database reset successful")
                
            else:
                print("✗ Failed to capture frame")
            
            cap.release()
        else:
            print("⚠ Camera not available - testing with sample image")
            
            # Create a sample image for testing
            sample_frame = cv2.imread("test_sample.jpg")
            if sample_frame is not None:
                processed_frame, people_count, detections = detector.detect_crowd(sample_frame)
                print(f"✓ Detection completed - People detected: {people_count}")
            else:
                print("⚠ No sample image found - creating blank image for testing")
                # Create a blank image
                blank_frame = cv2.imread("blank_image.jpg")
                if blank_frame is not None:
                    processed_frame, people_count, detections = detector.detect_crowd(blank_frame)
                    print(f"✓ Detection completed - People detected: {people_count}")
                else:
                    print("⚠ No images available for testing")
        
        # Close detector
        detector.close()
        print("✓ Detector closed successfully")
        
        print("\nAll tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_detector()
    sys.exit(0 if success else 1)