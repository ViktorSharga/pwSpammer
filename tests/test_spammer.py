import unittest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
import threading
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import InGameChatHelper, MessageEditDialog


class TestSpammerTab(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window for headless testing
        with patch('main.WINDOWS_AVAILABLE', False):
            self.app = InGameChatHelper(self.root)
        self.app.members = ["Alice", "Bob", "Charlie"]
        self.app.templates = [
            {'short_name': 'Template1', 'content': 'Hello!'},
            {'short_name': 'Template2', 'content': 'How are you?'}
        ]
        
    def tearDown(self):
        if hasattr(self.app, 'is_sending'):
            self.app.is_sending = False
        if hasattr(self.app, 'send_thread') and self.app.send_thread:
            self.app.send_thread = None
        try:
            self.root.destroy()
        except tk.TclError:
            pass
    
    def test_refresh_recipients_display(self):
        self.app.refresh_recipients_display()
        
        # Check that all members have checkboxes
        self.assertEqual(len(self.app.selected_recipients), 3)
        for member in self.app.members:
            self.assertIn(member, self.app.selected_recipients)
            self.assertTrue(self.app.selected_recipients[member].get())
    
    def test_unselect_all_recipients(self):
        self.app.refresh_recipients_display()
        self.app.unselect_all_recipients()
        
        for var in self.app.selected_recipients.values():
            self.assertFalse(var.get())
        
        self.assertIn("0 recipients selected", self.app.recipients_count_label['text'])
    
    def test_update_recipients_count(self):
        self.app.refresh_recipients_display()
        
        # All selected by default
        self.app.update_recipients_count()
        self.assertIn("3 recipients selected", self.app.recipients_count_label['text'])
        
        # Unselect one
        self.app.selected_recipients["Alice"].set(False)
        self.app.update_recipients_count()
        self.assertIn("2 recipients selected", self.app.recipients_count_label['text'])
    
    def test_refresh_template_dropdown(self):
        self.app.refresh_template_dropdown()
        
        values = self.app.template_combobox['values']
        self.assertEqual(len(values), 2)
        self.assertIn('Template1', values)
        self.assertIn('Template2', values)
    
    def test_on_template_selected(self):
        self.app.refresh_template_dropdown()
        self.app.template_combobox.current(0)
        
        event = Mock()
        self.app.on_template_selected(event)
        
        self.assertEqual(self.app.selected_template_index, 0)
        self.assertEqual(self.app.message_preview, 'Hello!')
    
    def test_update_message_preview(self):
        test_message = "Test message content"
        self.app.update_message_preview(test_message)
        
        self.assertEqual(self.app.message_preview, test_message)
        content = self.app.message_preview_text.get('1.0', 'end-1c')
        self.assertEqual(content, test_message)
    
    def test_edit_message(self):
        self.app.selected_template_index = 0
        self.app.templates = [{'short_name': 'Test', 'content': 'Original'}]
        self.app.message_preview = "Original"
        
        with patch('main.MessageEditDialog') as mock_dialog:
            mock_instance = Mock()
            mock_instance.result = "Edited message"
            mock_dialog.return_value = mock_instance
            
            self.app.edit_message()
            
            self.assertEqual(self.app.message_preview, "Edited message")
    
    def test_send_next(self):
        self.app.refresh_recipients_display()
        self.app.message_preview = "Test message"
        self.app.selected_template_index = 0
        self.app.refresh_template_dropdown()
        self.app.template_combobox.current(0)
        
        # Mock validation to return True for testing
        with patch.object(self.app, '_validate_send_requirements', return_value=True), \
             patch.object(self.app, 'mock_send_message') as mock_send, \
             patch.object(self.app, 'log_message') as mock_log:
            
            self.app.send_next()
            
            mock_send.assert_called_once_with("Alice", "Test message")
            mock_log.assert_called_once()
            self.assertFalse(self.app.selected_recipients["Alice"].get())
    
    def test_send_next_no_recipients(self):
        self.app.refresh_recipients_display()
        self.app.unselect_all_recipients()
        
        with patch('main.messagebox.showwarning') as mock_warning:
            self.app.send_next()
            mock_warning.assert_called_with("Warning", "No recipients selected")
    
    def test_send_next_no_message(self):
        self.app.refresh_recipients_display()
        self.app.message_preview = ""
        
        with patch('main.messagebox.showwarning') as mock_warning:
            self.app.send_next()
            mock_warning.assert_called_with("Warning", "No message content")
    
    def test_send_all_start_stop(self):
        self.app.refresh_recipients_display()
        self.app.message_preview = "Test message"
        
        # Test starting
        self.assertFalse(self.app.is_sending)
        
        # Mock validation to return True for testing
        with patch.object(self.app, '_validate_send_requirements', return_value=True), \
             patch.object(self.app, 'send_all_worker'):
            self.app.send_all()
            self.assertTrue(self.app.is_sending)
            self.assertEqual(self.app.send_all_button['text'], "Stop")
            
            # Test stopping
            self.app.send_all()
            self.assertFalse(self.app.is_sending)
            self.assertEqual(self.app.send_all_button['text'], "Send All")
    
    def test_send_all_worker(self):
        selected_members = ["Alice", "Bob"]
        self.app.selected_recipients = {
            "Alice": Mock(get=lambda: True, set=lambda x: None),
            "Bob": Mock(get=lambda: True, set=lambda x: None)
        }
        self.app.message_preview = "Test message"
        self.app.selected_template_index = 0
        self.app.template_combobox = Mock(get=lambda: "Template1")
        self.app.is_sending = True
        
        with patch.object(self.app, 'mock_send_message') as mock_send, \
             patch.object(self.app, 'log_message'), \
             patch('time.sleep'):
            
            self.app.send_all_worker(selected_members)
            
            self.assertEqual(mock_send.call_count, 2)
            mock_send.assert_any_call("Alice", "Test message")
            mock_send.assert_any_call("Bob", "Test message")
    
    def test_mock_send_message(self):
        # Test that mock_send_message doesn't raise exceptions
        try:
            self.app.mock_send_message("TestUser", "Test message")
        except Exception as e:
            self.fail(f"mock_send_message raised an exception: {e}")
    
    def test_log_message(self):
        # Test that log_message doesn't raise exceptions
        with patch('builtins.print') as mock_print:
            self.app.log_message("Test log message")
            mock_print.assert_called_once_with("Test log message")


class TestMessageEditDialog(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window for headless testing
        
    def tearDown(self):
        try:
            self.root.destroy()
        except tk.TclError:
            pass
    
    def test_message_edit_dialog_ok(self):
        with patch.object(tk.Toplevel, 'wait_window'):
            dialog = MessageEditDialog(self.root, "Edit", "Template", "Initial content")
            dialog.content_text.delete('1.0', tk.END)
            dialog.content_text.insert('1.0', "Edited content")
            dialog.ok_clicked()
            
            self.assertEqual(dialog.result, "Edited content")
    
    def test_message_edit_dialog_cancel(self):
        with patch.object(tk.Toplevel, 'wait_window'):
            dialog = MessageEditDialog(self.root, "Edit", "Template", "Initial")
            dialog.cancel_clicked()
            
            self.assertIsNone(dialog.result)


if __name__ == '__main__':
    unittest.main()