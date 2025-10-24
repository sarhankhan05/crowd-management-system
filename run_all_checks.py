#!/usr/bin/env python3
"""
Run all system checks
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Success")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print("✗ Failed")
            if result.stderr:
                print(result.stderr)
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Run all verification checks"""
    print("=== Running All System Checks ===")
    
    checks = [
        ("python verify_installation.py", "Installation verification"),
        ("python check_weights.py", "YOLO weights check"),
        ("python -m unittest discover tests", "Unit tests"),
    ]
    
    all_passed = True
    
    for command, description in checks:
        if not run_command(command, description):
            all_passed = False
    
    print("\n=== Summary ===")
    if all_passed:
        print("✓ All checks passed! The system is ready to use.")
    else:
        print("✗ Some checks failed. Please address the issues above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)