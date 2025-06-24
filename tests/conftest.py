import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk

# Mock Windows-specific modules for non-Windows environments
if sys.platform != "win32":
    sys.modules['win32gui'] = Mock()
    sys.modules['win32api'] = Mock()
    sys.modules['win32con'] = Mock()
    sys.modules['win32process'] = Mock()
    sys.modules['psutil'] = Mock()

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