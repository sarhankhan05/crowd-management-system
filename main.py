#!/usr/bin/env python3
"""
Main entry point for the Crowd Management System
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    # Import and run the UI application
    from UI import QApplication, sys, ModernApp
    
    app = QApplication(sys.argv)
    # Set application style
    app.setStyle('Fusion')
    ex = ModernApp()
    sys.exit(app.exec_())