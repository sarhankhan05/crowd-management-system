#!/usr/bin/env python3
"""
Utility script to check if YOLOv3 weights are downloaded
"""

import os
import sys

def check_yolo_weights():
    """Check if YOLOv3 weights file exists"""
    filename = "yolov3.weights"
    
    if os.path.exists(filename):
        # Check file size
        file_size = os.path.getsize(filename)
        print(f"✓ {filename} found")
        print(f"  File size: {file_size / (1024*1024):.2f} MB")
        
        # Check if file size is reasonable (should be around 237MB)
        if file_size > 200 * 1024 * 1024:  # 200MB
            print("  Status: File size looks correct")
            return True
        else:
            print("  Warning: File size seems too small. May be incomplete.")
            return False
    else:
        print(f"✗ {filename} not found")
        print("  Please download from: https://pjreddie.com/media/files/yolov3.weights")
        return False

if __name__ == "__main__":
    success = check_yolo_weights()
    if not success:
        print("\nTo download the weights, run:")
        print("  python download_weights.py")
    sys.exit(0 if success else 1)