"""
Runtime hook for PyInstaller to ensure proper Windows API initialization
"""

import sys
import os
import logging

# Set up early logging for runtime hook
if hasattr(sys, 'frozen'):
    # Running as PyInstaller executable
    print("Runtime hook: Running as frozen executable")
    
    # Add bundle directory to path for DLL loading
    if hasattr(sys, '_MEIPASS'):
        bundle_dir = sys._MEIPASS
        print(f"Runtime hook: Bundle directory: {bundle_dir}")
        
        # Add to PATH for DLL resolution
        os.environ['PATH'] = bundle_dir + os.pathsep + os.environ.get('PATH', '')
        
        # Try to preload critical Windows DLLs
        try:
            import ctypes
            # Preload user32.dll and kernel32.dll
            ctypes.windll.user32
            ctypes.windll.kernel32
            print("Runtime hook: Successfully preloaded Windows DLLs")
        except Exception as e:
            print(f"Runtime hook: Failed to preload DLLs: {e}")
    
    # Initialize Windows API modules early
    try:
        import win32api
        import win32gui  
        import win32con
        import win32process
        import psutil
        print("Runtime hook: Windows API modules imported successfully")
    except ImportError as e:
        print(f"Runtime hook: Failed to import Windows modules: {e}")
        
    # Test GetAsyncKeyState early
    try:
        import win32api
        # Test with a safe key (left mouse button)
        test_result = win32api.GetAsyncKeyState(0x01)
        print(f"Runtime hook: GetAsyncKeyState test successful: {test_result}")
    except Exception as e:
        print(f"Runtime hook: GetAsyncKeyState test failed: {e}")

print("Runtime hook: Initialization complete")