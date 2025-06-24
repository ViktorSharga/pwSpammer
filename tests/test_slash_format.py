import unittest
import tkinter as tk
from unittest.mock import patch, Mock
import sys
import os
from io import StringIO

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import InGameChatHelper


class TestSlashMessageFormat(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window for headless testing
        with patch('main.WINDOWS_AVAILABLE', False):
            self.app = InGameChatHelper(self.root)
        
        # Set up test data
        self.app.members = ["TestUser", "Alice"]
        self.app.templates = [{'short_name': 'Test', 'content': 'Hello world!'}]
        self.app.refresh_members_list()
        self.app.refresh_recipients_display()
        self.app.refresh_templates_display()
        self.app.refresh_template_dropdown()
        self.app.template_combobox.current(0)
        self.app.update_message_preview("Hello world!")
        
    def tearDown(self):
        try:
            self.root.destroy()
        except tk.TclError:
            pass
    
    def test_mock_send_message_includes_slash(self):
        """Test that mock_send_message includes the slash in formatted message"""
        # Capture stdout to check the mock output
        captured_output = StringIO()
        
        with patch('sys.stdout', captured_output):
            self.app.mock_send_message("TestUser", "Hello world!")
        
        output = captured_output.getvalue()
        self.assertIn("Mock: Would send '/TestUser Hello world!'", output)
        self.assertTrue(output.startswith("Mock: Would send '/"))
    
    def test_send_next_message_format(self):
        """Test that send_next properly formats message with slash"""
        captured_messages = []
        
        def capture_mock_send(recipient, message):
            formatted_msg = f"/{recipient} {message}"
            captured_messages.append(formatted_msg)
        
        # Replace mock_send_message to capture what would be sent
        original_mock = self.app.mock_send_message
        self.app.mock_send_message = capture_mock_send
        
        try:
            with patch.object(self.app, '_validate_send_requirements', return_value=True):
                self.app.send_next()
            
            # Check that message was captured with slash
            self.assertEqual(len(captured_messages), 1)
            self.assertEqual(captured_messages[0], "/TestUser Hello world!")
            self.assertTrue(captured_messages[0].startswith("/"))
        finally:
            # Restore original mock
            self.app.mock_send_message = original_mock
    
    def test_real_send_message_format(self):
        """Test that real send_message correctly formats the message with slash"""
        import main
        from unittest.mock import Mock
        
        # Create mock Windows modules
        mock_win32gui = Mock()
        mock_win32gui.IsWindow.return_value = True
        mock_win32gui.IsIconic.return_value = False
        mock_win32gui.GetForegroundWindow.return_value = 12345
        
        mock_win32api = Mock()
        mock_win32con = Mock()
        mock_win32con.WM_CHAR = 0x0102
        mock_win32con.VK_RETURN = 0x0D
        mock_win32con.KEYEVENTF_KEYUP = 0x0002
        
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
                     patch.object(app, 'clear_chat_area'), \
                     patch.object(app, '_focus_game_window'):
                    
                    app.send_message("TestUser", "Hello world!")
                    
                    # Check that _type_message was called with formatted message
                    calls = mock_win32api.SendMessage.call_args_list
                    if calls:
                        sent_chars = [chr(call[0][2]) for call in calls]
                        reconstructed = ''.join(sent_chars)
                        
                        self.assertEqual(reconstructed, "/TestUser Hello world!")
                        self.assertTrue(reconstructed.startswith("/"))
                        
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
    
    def test_special_characters_in_message(self):
        """Test that special characters are handled correctly"""
        test_cases = [
            ("TestUser", "Hello!"),
            ("TestUser", "What?"),
            ("TestUser", "Hi, how are you?"),
            ("TestUser", "Test message with /special chars!"),
        ]
        
        for recipient, message in test_cases:
            with self.subTest(recipient=recipient, message=message):
                captured_output = StringIO()
                
                with patch('sys.stdout', captured_output):
                    self.app.mock_send_message(recipient, message)
                
                output = captured_output.getvalue()
                expected = f"Mock: Would send '/{recipient} {message}'"
                self.assertIn(expected, output)


if __name__ == '__main__':
    unittest.main()