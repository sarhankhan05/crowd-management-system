#!/usr/bin/env python3
"""
Utility script to download YOLOv3 weights
"""

import urllib.request
import os
import sys
from tqdm import tqdm

class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

def download_yolo_weights():
    """Download YOLOv3 weights file"""
    url = "https://pjreddie.com/media/files/yolov3.weights"
    filename = "yolov3.weights"
    
    if os.path.exists(filename):
        print(f"{filename} already exists. Skipping download.")
        return True
    
    print(f"Downloading {filename} from {url}")
    print("Note: This file is approximately 237MB. Download may take several minutes.")
    
    try:
        with DownloadProgressBar(unit='B', unit_scale=True,
                               miniters=1, desc=filename) as t:
            urllib.request.urlretrieve(url, filename, reporthook=t.update_to)
        print(f"\n{filename} downloaded successfully!")
        return True
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        print("Please download manually from: https://pjreddie.com/media/files/yolov3.weights")
        return False

if __name__ == "__main__":
    success = download_yolo_weights()
    sys.exit(0 if success else 1)