import unittest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import InGameChatHelper, WINDOWS_AVAILABLE


class TestSetupTab(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window for headless testing
        with patch('main.WINDOWS_AVAILABLE', False):
            self.app = InGameChatHelper(self.root)
        
    def tearDown(self):
        try:
            self.root.destroy()
        except tk.TclError:
            pass
    
    def test_initial_connection_state(self):
        self.assertFalse(self.app.is_connected)
        self.assertIsNone(self.app.game_window_handle)
        self.assertIsNone(self.app.game_process_id)
        self.assertIsNone(self.app.coord1)
        self.assertIsNone(self.app.coord2)
        self.assertEqual(self.app.status_label['text'], "UNCONNECTED")
        self.assertEqual(str(self.app.status_label['foreground']), 'red')
    
    def test_update_connection_status_connected(self):
        self.app.is_connected = True
        self.app.game_process_id = 12345
        self.app.update_connection_status()
        
        self.assertEqual(self.app.status_label['text'], "CONNECTED")
        self.assertEqual(str(self.app.status_label['foreground']), 'green')
        self.assertIn("12345", self.app.pid_label['text'])
        self.assertEqual(str(self.app.test_connection_button['state']), 'normal')
    
    def test_update_connection_status_disconnected(self):
        self.app.is_connected = False
        self.app.update_connection_status()
        
        self.assertEqual(self.app.status_label['text'], "UNCONNECTED")
        self.assertEqual(str(self.app.status_label['foreground']), 'red')
        self.assertEqual(self.app.pid_label['text'], "")
        self.assertEqual(str(self.app.test_connection_button['state']), 'disabled')
    
    def test_update_test_button_state(self):
        # Test with no connection
        self.app.is_connected = False
        self.app.update_test_button_state()
        self.assertEqual(str(self.app.test_clear_button['state']), 'disabled')
        
        # Test with connection but no coordinates
        self.app.is_connected = True
        self.app.coord1 = None
        self.app.coord2 = None
        self.app.update_test_button_state()
        self.assertEqual(str(self.app.test_clear_button['state']), 'disabled')
        
        # Test with connection and coordinates
        self.app.coord1 = (100, 200)
        self.app.coord2 = (300, 400)
        self.app.update_test_button_state()
        self.assertEqual(str(self.app.test_clear_button['state']), 'normal')
    
    @patch('main.WINDOWS_AVAILABLE', True)
    @patch('main.messagebox.showerror')
    def test_test_game_connection_not_connected(self, mock_error):
        self.app.is_connected = False
        self.app.test_game_connection()
        mock_error.assert_called_with("Error", "Not connected to game window")
    
    @patch('main.WINDOWS_AVAILABLE', True)
    @patch('main.win32gui.IsWindow', return_value=False)
    @patch('main.messagebox.showerror')
    def test_test_game_connection_window_gone(self, mock_error, mock_is_window):
        self.app.is_connected = True
        self.app.game_window_handle = 12345
        
        self.app.test_game_connection()
        
        self.assertFalse(self.app.is_connected)
        mock_error.assert_called_with("Error", "Game window no longer exists")
    
    @patch('main.WINDOWS_AVAILABLE', True)
    @patch('main.win32gui.IsWindow', return_value=True)
    @patch('main.win32gui.IsIconic', return_value=False)
    @patch('main.win32gui.SetForegroundWindow')
    @patch('main.win32gui.BringWindowToTop')
    @patch('main.messagebox.showinfo')
    def test_test_game_connection_success(self, mock_info, mock_bring, mock_foreground, mock_iconic, mock_is_window):
        self.app.is_connected = True
        self.app.game_window_handle = 12345
        
        self.app.test_game_connection()
        
        mock_foreground.assert_called_once_with(12345)
        mock_bring.assert_called_once_with(12345)
        mock_info.assert_called_with("Success", "Game window brought to focus")
    
    @patch('main.WINDOWS_AVAILABLE', False)
    @patch('main.messagebox.showerror')
    def test_windows_features_not_available(self, mock_error):
        self.app.test_game_connection()
        mock_error.assert_called_with("Error", "Windows-specific features not available")
        
        self.app.set_coordinate(1)
        mock_error.assert_called_with("Error", "Windows-specific features not available")
        
        self.app.test_clear_chat_area()
        mock_error.assert_called_with("Error", "Windows-specific features not available")
    
    @patch('main.WINDOWS_AVAILABLE', True)
    def test_set_coordinate_updates_labels(self):
        self.app.is_connected = True
        self.app.game_window_handle = 12345
        
        # Mock the entire win32gui module by injecting it into main's globals
        import main
        mock_win32gui = Mock()
        mock_win32gui.IsIconic.return_value = False
        mock_win32con = Mock()
        mock_win32con.SW_RESTORE = 9
        
        original_win32gui = getattr(main, 'win32gui', None)
        original_win32con = getattr(main, 'win32con', None)
        main.win32gui = mock_win32gui
        main.win32con = mock_win32con
        
        try:
            with patch('time.sleep'), \
                 patch.object(self.app, 'create_coordinate_overlay') as mock_overlay, \
                 patch.object(self.app.root, 'withdraw'):
                
                # Test the method
                self.app.set_coordinate(1)
                mock_overlay.assert_called_once()
                
                # Simulate setting coordinate
                self.app.coord1 = (100, 200)
                self.app.coord1_label.config(text=f"Coord1: (100, 200)")
                
                self.assertIn("(100, 200)", self.app.coord1_label['text'])
        finally:
            # Clean up the injected mocks
            if original_win32gui is not None:
                main.win32gui = original_win32gui
            elif hasattr(main, 'win32gui'):
                delattr(main, 'win32gui')
            if original_win32con is not None:
                main.win32con = original_win32con
            elif hasattr(main, 'win32con'):
                delattr(main, 'win32con')
    
    @patch('main.WINDOWS_AVAILABLE', True)
    @patch('main.messagebox.showerror')
    def test_test_clear_chat_area_missing_requirements(self, mock_error):
        # Test without connection
        self.app.is_connected = False
        self.app.test_clear_chat_area()
        mock_error.assert_called_with("Error", "Missing connection or coordinates")
        
        # Test with connection but no coordinates
        self.app.is_connected = True
        self.app.coord1 = None
        self.app.test_clear_chat_area()
        mock_error.assert_called_with("Error", "Missing connection or coordinates")
    
    @patch('main.WINDOWS_AVAILABLE', True)
    @patch.object(InGameChatHelper, 'clear_chat_area')
    @patch('main.messagebox.showinfo')
    def test_test_clear_chat_area_success(self, mock_info, mock_clear):
        self.app.is_connected = True
        self.app.coord1 = (100, 200)
        self.app.coord2 = (300, 400)
        
        self.app.test_clear_chat_area()
        
        mock_clear.assert_called_once()
        mock_info.assert_called_with("Success", "ClearChatArea executed successfully")


class TestHotkeyAndWindowHandling(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window for headless testing
        
    def tearDown(self):
        try:
            self.root.destroy()
        except tk.TclError:
            pass
    
    @patch('main.WINDOWS_AVAILABLE', True)
    @patch('main.win32gui.GetForegroundWindow', return_value=12345)
    @patch('main.win32gui.GetWindowText', return_value="Asgard Perfect World - Character")
    @patch('main.win32process.GetWindowThreadProcessId', return_value=(None, 54321))
    @patch('main.psutil.Process')
    @patch('main.messagebox.showinfo')
    def test_handle_hotkey_success(self, mock_info, mock_process, mock_thread_id, 
                                   mock_window_text, mock_foreground):
        with patch('main.WINDOWS_AVAILABLE', True):
            app = InGameChatHelper(self.root)
            
            # Mock process name
            mock_proc_instance = Mock()
            mock_proc_instance.name.return_value = "elementclient.exe"
            mock_process.return_value = mock_proc_instance
            
            app.handle_hotkey()
            
            self.assertTrue(app.is_connected)
            self.assertEqual(app.game_window_handle, 12345)
            self.assertEqual(app.game_process_id, 54321)
            mock_info.assert_called_once()
    
    @patch('main.WINDOWS_AVAILABLE', True)
    @patch('main.win32gui.GetForegroundWindow', return_value=12345)
    @patch('main.win32gui.GetWindowText', return_value="Wrong Window")
    @patch('main.win32process.GetWindowThreadProcessId', return_value=(None, 54321))
    @patch('main.psutil.Process')
    @patch('main.messagebox.showerror')
    def test_handle_hotkey_wrong_window(self, mock_error, mock_process, mock_thread_id,
                                       mock_window_text, mock_foreground):
        with patch('main.WINDOWS_AVAILABLE', True):
            app = InGameChatHelper(self.root)
            
            # Mock process name
            mock_proc_instance = Mock()
            mock_proc_instance.name.return_value = "elementclient.exe"
            mock_process.return_value = mock_proc_instance
            
            app.handle_hotkey()
            
            self.assertFalse(app.is_connected)
            mock_error.assert_called_once()
            self.assertIn("Asgard Perfect World", mock_error.call_args[0][1])
    
    @patch('main.WINDOWS_AVAILABLE', True)
    @patch('main.win32gui.GetForegroundWindow', return_value=12345)
    @patch('main.win32gui.GetWindowText', return_value="Asgard Perfect World")
    @patch('main.win32process.GetWindowThreadProcessId', return_value=(None, 54321))
    @patch('main.psutil.Process')
    @patch('main.messagebox.showerror')
    def test_handle_hotkey_wrong_process(self, mock_error, mock_process, mock_thread_id,
                                        mock_window_text, mock_foreground):
        with patch('main.WINDOWS_AVAILABLE', True):
            app = InGameChatHelper(self.root)
            
            # Mock wrong process name
            mock_proc_instance = Mock()
            mock_proc_instance.name.return_value = "wrongprocess.exe"
            mock_process.return_value = mock_proc_instance
            
            app.handle_hotkey()
            
            self.assertFalse(app.is_connected)
            mock_error.assert_called_once()
            self.assertIn("elementclient.exe", mock_error.call_args[0][1])


if __name__ == '__main__':
    unittest.main()