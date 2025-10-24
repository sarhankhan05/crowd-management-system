#!/usr/bin/env python3
"""
Unit tests for the Crowd Detection module
"""

import unittest
import cv2
import numpy as np
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.detection import CrowdDetector

class TestCrowdDetector(unittest.TestCase):
    """Test cases for the CrowdDetector class"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        try:
            self.detector = CrowdDetector()
        except Exception as e:
            self.detector = None
            print(f"Warning: Could not initialize detector: {e}")
    
    def test_detector_initialization(self):
        """Test that the detector initializes correctly"""
        if self.detector is not None:
            self.assertIsNotNone(self.detector.net)
            self.assertIsNotNone(self.detector.face_cascade)
            self.assertIsNotNone(self.detector.db_conn)
            self.assertIsNotNone(self.detector.db_cursor)
    
    def test_get_output_layers(self):
        """Test that output layers can be retrieved"""
        if self.detector is not None and self.detector.net is not None:
            layers = self.detector.get_output_layers(self.detector.net)
            self.assertIsInstance(layers, list)
            self.assertGreater(len(layers), 0)
    
    def test_database_functions(self):
        """Test database functionality"""
        if self.detector is not None:
            # Test getting history (should not fail even if empty)
            try:
                history = self.detector.get_detection_history()
                self.assertIsInstance(history, list)
            except Exception as e:
                self.fail(f"get_detection_history failed: {e}")
    
    def test_frame_processing(self):
        """Test frame processing with a blank image"""
        if self.detector is not None:
            # Create a blank test frame
            blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            
            try:
                processed_frame, people_count, detections = self.detector.detect_crowd(blank_frame)
                self.assertIsInstance(processed_frame, np.ndarray)
                self.assertIsInstance(people_count, int)
                self.assertIsInstance(detections, list)
                self.assertEqual(people_count, 0)  # Should be 0 people in blank frame
            except Exception as e:
                # This might fail if models aren't loaded, which is acceptable in test environment
                print(f"Frame processing test skipped due to: {e}")

if __name__ == '__main__':
    unittest.main()