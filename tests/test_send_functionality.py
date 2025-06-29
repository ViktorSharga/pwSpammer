import unittest
from unittest.mock import Mock, patch, MagicMock, call
import tkinter as tk
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import InGameChatHelper, WINDOWS_AVAILABLE


class TestSendFunctionality(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window for headless testing
        with patch('main.WINDOWS_AVAILABLE', False):
            self.app = InGameChatHelper(self.root)
        
        # Set up test data
        self.app.members = ["Alice", "Bob", "Charlie"]
        self.app.templates = [{'short_name': 'Test', 'content': 'Hello!'}]
        self.app.refresh_members_list()
        self.app.refresh_templates_display()
        self.app.refresh_template_dropdown()
        self.app.template_combobox.current(0)
        self.app.update_message_preview("Hello!")
        
    def tearDown(self):
        if hasattr(self.app, 'is_sending'):
            self.app.is_sending = False
        try:
            self.root.destroy()
        except tk.TclError:
            pass
    
    def test_validate_send_requirements_no_windows(self):
        """Test validation when Windows features are not available"""
        with patch('main.WINDOWS_AVAILABLE', False):
            result = self.app._validate_send_requirements()
            self.assertFalse(result)
    
    @patch('main.WINDOWS_AVAILABLE', True)
    def test_validate_send_requirements_not_connected(self):
        """Test validation when not connected to game"""
        self.app.is_connected = False
        self.app.game_window_handle = None
        
        with patch('main.messagebox.showwarning') as mock_warning:
            result = self.app._validate_send_requirements()
            self.assertFalse(result)
            mock_warning.assert_called_once()
            self.assertIn("Not connected", mock_warning.call_args[0][1])
    
    @patch('main.WINDOWS_AVAILABLE', True)
    def test_validate_send_requirements_no_coordinates(self):
        """Test validation when coordinates are not set"""
        self.app.is_connected = True
        self.app.game_window_handle = 12345
        self.app.coord1 = None
        self.app.coord2 = None
        
        with patch('main.messagebox.showwarning') as mock_warning:
            result = self.app._validate_send_requirements()
            self.assertFalse(result)
            mock_warning.assert_called_once()
            self.assertIn("coordinates not set", mock_warning.call_args[0][1])
    
    def test_validate_send_requirements_window_gone(self):
        """Test validation when game window no longer exists"""
        self.app.is_connected = True
        self.app.game_window_handle = 12345
        self.app.coord1 = (100, 200)
        self.app.coord2 = (300, 400)
        
        import main
        from unittest.mock import Mock
        
        # Create mock Windows modules
        mock_win32gui = Mock()
        mock_win32gui.IsWindow.return_value = False
        
        # Inject win32gui into main module temporarily  
        original_win32gui = getattr(main, 'win32gui', None)
        main.win32gui = mock_win32gui
        
        try:
            with patch.object(main, 'WINDOWS_AVAILABLE', True), \
                 patch('main.messagebox.showerror') as mock_error, \
                 patch.object(self.app, 'update_connection_status') as mock_update:
                result = self.app._validate_send_requirements()
                self.assertFalse(result)
                self.assertFalse(self.app.is_connected)
                mock_update.assert_called_once()
                mock_error.assert_called_once()
        finally:
            # Restore original state
            if original_win32gui is not None:
                main.win32gui = original_win32gui
            elif hasattr(main, 'win32gui'):
                delattr(main, 'win32gui')
    
    def test_validate_send_requirements_success(self):
        """Test successful validation"""
        self.app.is_connected = True
        self.app.game_window_handle = 12345
        self.app.coord1 = (100, 200)
        self.app.coord2 = (300, 400)
        
        # Patch the global variable and inject Windows modules
        import main
        from unittest.mock import Mock
        
        # Create mock Windows modules
        mock_win32gui = Mock()
        mock_win32gui.IsWindow.return_value = True
        
        # Inject win32gui into main module temporarily  
        original_win32gui = getattr(main, 'win32gui', None)
        main.win32gui = mock_win32gui
        
        try:
            with patch.object(main, 'WINDOWS_AVAILABLE', True):
                result = self.app._validate_send_requirements()
                self.assertTrue(result)
        finally:
            # Restore original state
            if original_win32gui is not None:
                main.win32gui = original_win32gui
            elif hasattr(main, 'win32gui'):
                delattr(main, 'win32gui')
    
    def test_send_next_no_recipients(self):
        """Test send_next with no recipients selected"""
        # Unselect all recipients
        for var in self.app.selected_recipients.values():
            var.set(False)
        
        with patch('main.messagebox.showwarning') as mock_warning:
            self.app.send_next()
            mock_warning.assert_called_with("Warning", "No recipients selected")
    
    def test_send_next_no_message(self):
        """Test send_next with no message content"""
        self.app.update_message_preview("")
        
        with patch('main.messagebox.showwarning') as mock_warning:
            self.app.send_next()
            mock_warning.assert_called_with("Warning", "No message content")
    
    def test_send_next_validation_failure(self):
        """Test send_next when validation fails"""
        with patch.object(self.app, '_validate_send_requirements', return_value=False):
            with patch.object(self.app, 'send_message') as mock_send:
                self.app.send_next()
                mock_send.assert_not_called()
    
    def test_send_next_success_mock(self):
        """Test successful send_next with mock implementation"""
        with patch.object(self.app, '_validate_send_requirements', return_value=True), \
             patch.object(self.app, 'mock_send_message') as mock_send, \
             patch.object(self.app, 'log_message') as mock_log:
            
            self.app.send_next()
            
            mock_send.assert_called_once_with("Alice", "Hello!")
            mock_log.assert_called_once()
            self.assertFalse(self.app.selected_recipients["Alice"].get())
    
    @patch('main.WINDOWS_AVAILABLE', True)
    def test_send_next_success_real(self):
        """Test successful send_next with real implementation"""
        self.app.is_connected = True
        
        with patch.object(self.app, '_validate_send_requirements', return_value=True), \
             patch.object(self.app, 'send_message') as mock_send, \
             patch.object(self.app, 'log_message') as mock_log:
            
            self.app.send_next()
            
            mock_send.assert_called_once_with("Alice", "Hello!")
            mock_log.assert_called_once()
            self.assertFalse(self.app.selected_recipients["Alice"].get())
    
    def test_send_next_exception_handling(self):
        """Test send_next exception handling"""
        with patch.object(self.app, '_validate_send_requirements', return_value=True), \
             patch.object(self.app, 'mock_send_message', side_effect=Exception("Test error")), \
             patch('main.messagebox.showerror') as mock_error:
            
            self.app.send_next()
            mock_error.assert_called_once()
            self.assertIn("Test error", mock_error.call_args[0][1])
    
    def test_send_all_validation_failure(self):
        """Test send_all when validation fails"""
        with patch.object(self.app, '_validate_send_requirements', return_value=False):
            self.app.send_all()
            self.assertFalse(self.app.is_sending)
    
    def test_send_all_start_stop(self):
        """Test send_all start and stop functionality"""
        with patch.object(self.app, '_validate_send_requirements', return_value=True), \
             patch.object(self.app, 'send_all_worker'):
            
            # Start sending
            self.app.send_all()
            self.assertTrue(self.app.is_sending)
            self.assertEqual(self.app.send_all_button['text'], "Stop")
            
            # Stop sending
            self.app.send_all()
            self.assertFalse(self.app.is_sending)
            self.assertEqual(self.app.send_all_button['text'], "Send All")
    
    def test_send_all_worker_success(self):
        """Test send_all_worker successful execution"""
        selected_members = ["Alice", "Bob"]
        self.app.is_sending = True
        
        with patch.object(self.app, 'mock_send_message') as mock_send, \
             patch('time.sleep'), \
             patch.object(self.app.root, 'after') as mock_after:
            
            self.app.send_all_worker(selected_members)
            
            # Verify send_message was called for each member
            self.assertEqual(mock_send.call_count, 2)
            mock_send.assert_any_call("Alice", "Hello!")
            mock_send.assert_any_call("Bob", "Hello!")
            
            # Verify UI updates were scheduled
            self.assertTrue(mock_after.called)
    
    def test_send_all_worker_exception_handling(self):
        """Test send_all_worker exception handling"""
        selected_members = ["Alice", "Bob"]
        self.app.is_sending = True
        
        with patch.object(self.app, 'mock_send_message', side_effect=Exception("Test error")), \
             patch.object(self.app.root, 'after') as mock_after:
            
            self.app.send_all_worker(selected_members)
            
            # Verify error handling was called
            self.assertTrue(mock_after.called)
    
    def test_send_all_worker_early_stop(self):
        """Test send_all_worker stops when is_sending becomes False"""
        selected_members = ["Alice", "Bob", "Charlie"]
        self.app.is_sending = True
        
        def side_effect(*args):
            self.app.is_sending = False  # Stop after first message
        
        with patch.object(self.app, 'mock_send_message', side_effect=side_effect) as mock_send, \
             patch('time.sleep'):
            
            self.app.send_all_worker(selected_members)
            
            # Should only send to first member before stopping
            self.assertEqual(mock_send.call_count, 1)


class TestSendMessageImplementation(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
    def tearDown(self):
        try:
            self.root.destroy()
        except tk.TclError:
            pass
    
    @patch('main.WINDOWS_AVAILABLE', True)
    def test_send_message_not_connected(self):
        """Test send_message when not connected"""
        with patch('main.WINDOWS_AVAILABLE', True):
            app = InGameChatHelper(self.root)
            app.is_connected = False
            
            with self.assertRaises(Exception) as context:
                app.send_message("Alice", "Hello")
            
            self.assertIn("Not connected to game window", str(context.exception))
    
    @patch('main.WINDOWS_AVAILABLE', True)
    def test_send_message_no_coordinates(self):
        """Test send_message when coordinates not set"""
        with patch('main.WINDOWS_AVAILABLE', True):
            app = InGameChatHelper(self.root)
            app.is_connected = True
            app.game_window_handle = 12345
            app.coord1 = None
            app.coord2 = None
            
            with self.assertRaises(Exception) as context:
                app.send_message("Alice", "Hello")
            
            self.assertIn("Chat coordinates not set", str(context.exception))
    
    def test_send_message_success(self):
        """Test successful send_message execution"""
        import main
        from unittest.mock import Mock
        
        # Create comprehensive mock Windows modules
        mock_win32gui = Mock()
        mock_win32gui.IsWindow.return_value = True
        mock_win32gui.IsIconic.return_value = False
        mock_win32gui.GetForegroundWindow.return_value = 12345
        
        mock_win32api = Mock()
        
        mock_win32con = Mock()
        mock_win32con.WM_CHAR = 0x0102
        mock_win32con.KEYEVENTF_KEYUP = 0x0002
        mock_win32con.VK_RETURN = 0x0D
        
        # Inject modules into main namespace temporarily
        original_win32gui = getattr(main, 'win32gui', None)
        original_win32api = getattr(main, 'win32api', None)
        original_win32con = getattr(main, 'win32con', None)
        main.win32gui = mock_win32gui
        main.win32api = mock_win32api
        main.win32con = mock_win32con
        
        try:
            with patch.object(main, 'WINDOWS_AVAILABLE', True):
                app = InGameChatHelper(self.root)
                app.is_connected = True
                app.game_window_handle = 12345
                app.coord1 = (100, 200)
                app.coord2 = (300, 400)
                
                with patch('time.sleep'), \
                     patch.object(app, 'clear_chat_area') as mock_clear:
                    
                    app.send_message("Alice", "Hello World")
                    
                    # Verify window focusing
                    mock_win32gui.SetForegroundWindow.assert_called_with(12345)
                    mock_win32gui.BringWindowToTop.assert_called_with(12345)
                    mock_win32gui.SetActiveWindow.assert_called_with(12345)
                    
                    # Verify clear_chat_area was called
                    mock_clear.assert_called_once()
                    
                    # Verify keybd_event was called
                    mock_win32api.keybd_event.assert_called()
        finally:
            # Restore original state
            if original_win32gui is not None:
                main.win32gui = original_win32gui
            elif hasattr(main, 'win32gui'):
                delattr(main, 'win32gui')
            if original_win32api is not None:
                main.win32api = original_win32api
            elif hasattr(main, 'win32api'):
                delattr(main, 'win32api')
            if original_win32con is not None:
                main.win32con = original_win32con
            elif hasattr(main, 'win32con'):
                delattr(main, 'win32con')
    
    def test_focus_game_window_not_exists(self):
        """Test _focus_game_window when window doesn't exist"""
        import main
        from unittest.mock import Mock
        
        # Create mock Windows module
        mock_win32gui = Mock()
        mock_win32gui.IsWindow.return_value = False
        
        # Inject win32gui into main module temporarily  
        original_win32gui = getattr(main, 'win32gui', None)
        main.win32gui = mock_win32gui
        
        try:
            with patch.object(main, 'WINDOWS_AVAILABLE', True):
                app = InGameChatHelper(self.root)
                app.game_window_handle = 12345
                
                with self.assertRaises(Exception) as context:
                    app._focus_game_window()
                
                self.assertIn("Game window no longer exists", str(context.exception))
        finally:
            # Restore original state
            if original_win32gui is not None:
                main.win32gui = original_win32gui
            elif hasattr(main, 'win32gui'):
                delattr(main, 'win32gui')


if __name__ == '__main__':
    unittest.main()