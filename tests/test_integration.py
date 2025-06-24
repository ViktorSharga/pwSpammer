import unittest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import InGameChatHelper


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window for headless testing
        with patch('main.WINDOWS_AVAILABLE', False):
            self.app = InGameChatHelper(self.root)
        
    def tearDown(self):
        if hasattr(self.app, 'is_sending'):
            self.app.is_sending = False
        try:
            self.root.destroy()
        except tk.TclError:
            pass
    
    def test_member_to_recipient_flow(self):
        # Add members
        self.app.members = ["Alice", "Bob", "Charlie"]
        self.app.refresh_members_list()
        
        # Check they appear in recipients
        self.app.refresh_recipients_display()
        
        self.assertEqual(len(self.app.selected_recipients), 3)
        self.assertIn("Alice", self.app.selected_recipients)
        self.assertIn("Bob", self.app.selected_recipients)
        self.assertIn("Charlie", self.app.selected_recipients)
    
    def test_template_to_message_flow(self):
        # Add templates
        self.app.templates = [
            {'short_name': 'Greeting', 'content': 'Hello there!'},
            {'short_name': 'Question', 'content': 'How are you?'}
        ]
        self.app.refresh_templates_display()
        
        # Check they appear in dropdown
        self.app.refresh_template_dropdown()
        values = self.app.template_combobox['values']
        self.assertIn('Greeting', values)
        self.assertIn('Question', values)
        
        # Select a template
        self.app.template_combobox.current(0)
        event = Mock()
        self.app.on_template_selected(event)
        
        # Check message preview updates
        self.assertEqual(self.app.message_preview, 'Hello there!')
    
    def test_complete_send_workflow(self):
        # Setup members and templates
        self.app.members = ["Alice", "Bob"]
        self.app.templates = [{'short_name': 'Test', 'content': 'Test message'}]
        
        # Refresh displays
        self.app.refresh_members_list()
        self.app.refresh_recipients_display()
        self.app.refresh_templates_display()
        self.app.refresh_template_dropdown()
        
        # Select template
        self.app.template_combobox.current(0)
        event = Mock()
        self.app.on_template_selected(event)
        
        # Check send buttons are enabled
        self.app.update_recipients_count()
        self.assertEqual(str(self.app.send_next_button['state']), 'normal')
        self.assertEqual(str(self.app.send_all_button['state']), 'normal')
        
        # Send to one recipient
        with patch.object(self.app, '_validate_send_requirements', return_value=True), \
             patch.object(self.app, 'mock_send_message') as mock_send, \
             patch.object(self.app, 'log_message'):
            
            self.app.send_next()
            
            mock_send.assert_called_once()
            # Alice should be unselected
            self.assertFalse(self.app.selected_recipients["Alice"].get())
            # Bob should still be selected
            self.assertTrue(self.app.selected_recipients["Bob"].get())
    
    def test_save_and_load_workflow(self):
        # Setup initial data
        self.app.members = ["Alice", "Bob"]
        test_file = "test_members.json"
        
        # Save members
        with patch('main.filedialog.asksaveasfilename', return_value=test_file), \
             patch('builtins.open', unittest.mock.mock_open()) as mock_file, \
             patch('json.dump') as mock_dump, \
             patch('main.messagebox.showinfo'):
            
            self.app.save_members()
            mock_dump.assert_called_once_with(["Alice", "Bob"], mock_file(), indent=2)
        
        # Load members (with duplicates)
        loaded_data = ["Charlie", "Alice", "David"]  # Alice is duplicate
        
        with patch('main.filedialog.askopenfilename', return_value=test_file), \
             patch('builtins.open', unittest.mock.mock_open(read_data=json.dumps(loaded_data))), \
             patch('main.messagebox.showinfo') as mock_info:
            
            self.app.load_members()
            
            # Should have Alice, Bob, Charlie, David (4 total)
            self.assertEqual(len(self.app.members), 4)
            self.assertIn("Charlie", self.app.members)
            self.assertIn("David", self.app.members)
            
            # Check duplicate warning
            info_call = mock_info.call_args[0][1]
            self.assertIn("2 new members", info_call)
            self.assertIn("1 duplicate", info_call)
    
    def test_edit_message_workflow(self):
        # Setup
        self.app.templates = [{'short_name': 'Original', 'content': 'Original message'}]
        self.app.selected_template_index = 0
        self.app.message_preview = "Original message"
        self.app.refresh_template_dropdown()
        self.app.template_combobox.current(0)
        
        # Edit the message
        with patch('main.MessageEditDialog') as mock_dialog:
            mock_instance = Mock()
            mock_instance.result = "Edited message content"
            mock_dialog.return_value = mock_instance
            
            self.app.edit_message()
            
            # Check message preview updated
            self.assertEqual(self.app.message_preview, "Edited message content")
            
            # Original template should remain unchanged
            self.assertEqual(self.app.templates[0]['content'], "Original message")
    
    def test_tab_interaction(self):
        # Add data in MemberList tab
        self.app.members = ["TestUser"]
        self.app.refresh_members_list()
        
        # Add template in Templates tab
        self.app.templates = [{'short_name': 'TestTemplate', 'content': 'Test content'}]
        self.app.refresh_templates_display()
        
        # Switch to Spammer tab and verify data is available
        self.app.notebook.select(2)  # Select Spammer tab
        
        # Check recipients are populated
        self.assertEqual(len(self.app.selected_recipients), 1)
        self.assertIn("TestUser", self.app.selected_recipients)
        
        # Check templates are in dropdown
        values = self.app.template_combobox['values']
        self.assertIn('TestTemplate', values)
    
    def test_coordinate_setting_workflow(self):
        # Setup connection
        self.app.is_connected = True
        self.app.game_window_handle = 12345
        self.app.game_process_id = 54321
        self.app.update_connection_status()
        
        # Set coordinates
        self.app.coord1 = (100, 200)
        self.app.coord2 = (300, 400)
        self.app.coord1_label.config(text="Coord1: (100, 200)")
        self.app.coord2_label.config(text="Coord2: (300, 400)")
        
        # Update button state
        self.app.update_test_button_state()
        
        # Test button should be enabled
        self.assertEqual(str(self.app.test_clear_button['state']), 'normal')
        
        # Labels should show coordinates
        self.assertIn("(100, 200)", self.app.coord1_label['text'])
        self.assertIn("(300, 400)", self.app.coord2_label['text'])


if __name__ == '__main__':
    unittest.main()