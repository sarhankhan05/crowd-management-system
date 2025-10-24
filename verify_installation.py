#!/usr/bin/env python3
"""
Verification script to check if all components are properly installed
"""

import sys
import os

def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} - Required: 3.8+")
        return False

def check_dependencies():
    """Check if all dependencies are installed"""
    print("\nChecking dependencies...")
    
    dependencies = [
        ('cv2', 'opencv-python'),
        ('numpy', 'numpy'),
        ('flask', 'Flask'),
        ('sqlite3', 'sqlite3')
    ]
    
    all_good = True
    
    for module, package in dependencies:
        try:
            __import__(module)
            print(f"✓ {package} - OK")
        except ImportError:
            print(f"✗ {package} - Not installed (pip install {package})")
            all_good = False
    
    return all_good

def check_files():
    """Check if required files exist"""
    print("\nChecking required files...")
    
    required_files = [
        'yolov3.cfg',
        'coco.names',
        'haarcascade_frontalface_default.xml',
        'app.py',
        'core/detection.py',
        'templates/index.html',
        'static/css/style.css',
        'static/js/main.js'
    ]
    
    all_good = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path} - Found")
        else:
            print(f"✗ {file_path} - Missing")
            all_good = False
    
    # Check if YOLO weights exist (warning only)
    if os.path.exists('yolov3.weights'):
        print("✓ yolov3.weights - Found")
    else:
        print("⚠ yolov3.weights - Missing (download from https://pjreddie.com/darknet/yolo/)")
    
    return all_good

def check_directories():
    """Check if required directories exist"""
    print("\nChecking directories...")
    
    required_dirs = [
        'core',
        'templates',
        'static',
        'static/css',
        'static/js',
        'static/images',
        'components',
        'docs',
        'tests'
    ]
    
    all_good = True
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            print(f"✓ {dir_path} - Found")
        else:
            print(f"✗ {dir_path} - Missing")
            all_good = False
    
    return all_good

def main():
    """Main verification function"""
    print("=== Crowd Management System Installation Verification ===\n")
    
    checks = [
        check_python_version,
        check_dependencies,
        check_directories,
        check_files
    ]
    
    all_passed = True
    
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n=== Summary ===")
    if all_passed:
        print("✓ All checks passed! The system is ready to use.")
        print("\nTo start the application, run:")
        print("  python app.py")
        print("\nThen open your browser to http://localhost:5000")
    else:
        print("✗ Some checks failed. Please address the issues above.")
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)