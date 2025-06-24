import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk

# Mock Windows-specific modules for non-Windows environments
mock_win32gui = Mock()
mock_win32api = Mock()
mock_win32con = Mock()
mock_win32process = Mock()
mock_psutil = Mock()

# Set up common Windows constants
mock_win32con.SW_RESTORE = 9
mock_win32con.MOUSEEVENTF_LEFTDOWN = 0x0002
mock_win32con.MOUSEEVENTF_LEFTUP = 0x0004
mock_win32con.VK_RETURN = 0x0D
mock_win32con.VK_SPACE = 0x20
mock_win32con.KEYEVENTF_KEYUP = 0x0002
mock_win32con.WM_CHAR = 0x0102

# Set up common return values
mock_win32gui.IsWindow.return_value = True
mock_win32gui.IsIconic.return_value = False
mock_win32gui.GetForegroundWindow.return_value = 12345

if sys.platform != "win32":
    sys.modules['win32gui'] = mock_win32gui
    sys.modules['win32api'] = mock_win32api
    sys.modules['win32con'] = mock_win32con
    sys.modules['win32process'] = mock_win32process
    sys.modules['psutil'] = mock_psutil

# Configure Tkinter for headless testing
@pytest.fixture(scope="session", autouse=True)
def setup_headless_tk():
    """Setup Tkinter for headless testing on CI"""
    if 'CI' in os.environ or 'GITHUB_ACTIONS' in os.environ:
        # Mock Tkinter for CI environments
        original_tk_root = tk.Tk
        
        def mock_tk_root(*args, **kwargs):
            root = original_tk_root()
            root.withdraw()  # Hide the window
            # Override mainloop to prevent hanging
            root.mainloop = Mock()
            # Override wait_window to prevent hanging
            root.wait_window = Mock()
            return root
        
        with patch('tkinter.Tk', side_effect=mock_tk_root):
            yield
    else:
        yield

@pytest.fixture(autouse=True)
def mock_tkinter_dialogs():
    """Mock Tkinter dialogs that can hang in headless environments"""
    with patch('tkinter.messagebox.showinfo'), \
         patch('tkinter.messagebox.showwarning'), \
         patch('tkinter.messagebox.showerror'), \
         patch('tkinter.messagebox.askyesno', return_value=True), \
         patch('tkinter.filedialog.asksaveasfilename', return_value='test.json'), \
         patch('tkinter.filedialog.askopenfilename', return_value='test.json'):
        yield

@pytest.fixture
def mock_windows_features():
    """Mock Windows-specific features"""
    with patch('main.WINDOWS_AVAILABLE', False):
        yield