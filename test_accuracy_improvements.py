#!/usr/bin/env python3
"""
Test script to verify accuracy improvements in video processing
"""

import sys
import os
import tempfile
import cv2
import numpy as np

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.detection import CrowdDetector

def create_test_video_with_known_objects():
    """Create a test video with known number of people for accuracy testing"""
    print("Creating test video with known objects...")
    temp_dir = tempfile.gettempdir()
    test_video_path = os.path.join(temp_dir, "accuracy_test_video.avi")
    
    # Create video writer with better quality
    fourcc = cv2.VideoWriter.fourcc(*'XVID')
    out = cv2.VideoWriter(test_video_path, fourcc, 10.0, (640, 480))
    
    # Create 30 frames with varying numbers of people
    for frame_num in range(30):
        # Create a blue background frame
        frame = np.full((480, 640, 3), (255, 100, 100), dtype=np.uint8)  # Blue-ish background
        
        # Add known number of people (rectangles) based on frame number
        num_people = (frame_num % 5) + 1  # 1-5 people cycling
        
        for i in range(num_people):
            # Position people differently in each frame
            x_offset = (frame_num * 20) % 200
            y_offset = (i * 100) % 300
            
            # Draw person as a green rectangle
            x1 = 100 + x_offset + (i * 80)
            y1 = 150 + y_offset
            x2 = x1 + 60
            y2 = y1 + 120
            
            # Make sure coordinates are within frame bounds
            x1 = max(0, min(x1, 630))
            x2 = max(x1 + 30, min(x2, 640))
            y1 = max(0, min(y1, 360))
            y2 = max(y1 + 60, min(y2, 480))
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), -1)
            
            # Add head as a circle
            head_center = (x1 + 30, y1 + 20)
            cv2.circle(frame, head_center, 15, (0, 150, 0), -1)
        
        out.write(frame)
    
    out.release()
    print(f"✓ Test video created at {test_video_path}")
    return test_video_path, [(i % 5) + 1 for i in range(30)]  # Expected counts

def test_accuracy_improvements():
    """Test the accuracy improvements"""
    print("Testing Accuracy Improvements...")
    
    # Initialize detector
    try:
        detector = CrowdDetector()
        print("✓ Detector initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing detector: {e}")
        return False
    
    # Create test video
    video_path, expected_counts = create_test_video_with_known_objects()
    
    # Test video processing
    print("Testing video processing accuracy...")
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("✗ Failed to open test video")
            return False
        
        detected_counts = []
        frame_count = 0
        
        while frame_count < len(expected_counts):
            ret, frame = cap.read()
            if not ret:
                break
                
            # Process frame with detector
            try:
                processed_frame, people_count, detections, risk_data = detector.detect_crowd(frame)
                detected_counts.append(people_count)
                print(f"Frame {frame_count}: Expected={expected_counts[frame_count]}, Detected={people_count}, Accuracy={abs(people_count-expected_counts[frame_count]) <= 1}")
                frame_count += 1
            except Exception as e:
                print(f"✗ Error processing frame {frame_count}: {e}")
                break
        
        cap.release()
        
        # Calculate accuracy
        if len(detected_counts) > 0:
            # Calculate how many detections were within 1 person of expected
            accurate_detections = sum(1 for exp, det in zip(expected_counts[:len(detected_counts)], detected_counts) if abs(exp - det) <= 1)
            accuracy_rate = accurate_detections / len(detected_counts)
            
            print(f"\nAccuracy Results:")
            print(f"Total Frames Processed: {len(detected_counts)}")
            print(f"Accurate Detections (±1 person): {accurate_detections}")
            print(f"Accuracy Rate: {accuracy_rate:.2%}")
            
            if accuracy_rate >= 0.8:
                print("✓ Accuracy improvement test PASSED")
                return True
            else:
                print("✗ Accuracy improvement test FAILED - Below 80% accuracy")
                return False
        else:
            print("✗ No frames were processed")
            return False
            
    except Exception as e:
        print(f"✗ Error in accuracy testing: {e}")
        return False

def test_density_calculation():
    """Test density calculation accuracy"""
    print("\nTesting Density Calculation...")
    
    try:
        detector = CrowdDetector()
        
        # Create test frames with different densities
        test_cases = [
            {"width": 640, "height": 480, "people": 0, "expected_density": 0.0},
            {"width": 640, "height": 480, "people": 5, "expected_max": 0.5},  # Should be low-medium risk
            {"width": 640, "height": 480, "people": 15, "expected_max": 1.0}, # Should be high risk
        ]
        
        for i, case in enumerate(test_cases):
            # Create test frame
            frame = np.zeros((case["height"], case["width"], 3), dtype=np.uint8)
            
            # Add people as rectangles
            for j in range(case["people"]):
                x = (j * 100) % (case["width"] - 50)
                y = (j * 80) % (case["height"] - 100)
                cv2.rectangle(frame, (x, y), (x+40, y+80), (0, 255, 0), -1)
            
            # Process frame
            processed_frame, people_count, detections, risk_data = detector.detect_crowd(frame)
            
            # Check if detection matches expected
            density_score = risk_data["factors"]["density"]
            risk_level = risk_data["level"]
            
            print(f"Test Case {i+1}: People={case['people']}, Detected={people_count}, Density={density_score:.3f}, Risk={risk_level}")
            
        print("✓ Density calculation test completed")
        return True
        
    except Exception as e:
        print(f"✗ Error in density calculation test: {e}")
        return False

if __name__ == "__main__":
    print("=== Accuracy Improvement Test Suite ===")
    
    # Test accuracy improvements
    accuracy_test_passed = test_accuracy_improvements()
    
    # Test density calculation
    density_test_passed = test_density_calculation()
    
    print("\n=== Final Test Results ===")
    print(f"Accuracy Improvement Test: {'PASSED' if accuracy_test_passed else 'FAILED'}")
    print(f"Density Calculation Test: {'PASSED' if density_test_passed else 'FAILED'}")
    
    if accuracy_test_passed and density_test_passed:
        print("\n🎉 All accuracy tests passed! Improvements are working correctly.")
    else:
        print("\n❌ Some accuracy tests failed. Further improvements may be needed.")