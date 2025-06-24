import unittest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
from tkinter import ttk
import sys
import os

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main

class TestSpeedFunctionality(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
        # Mock the DataManager to avoid file I/O during tests
        with patch('main.DataManager') as mock_data_manager:
            mock_instance = Mock()
            mock_instance.load_members.return_value = []
            mock_instance.load_templates.return_value = []
            mock_data_manager.return_value = mock_instance
            
            self.app = main.InGameChatHelper(self.root)
    
    def tearDown(self):
        """Clean up after each test method."""
        if self.root:
            self.root.destroy()
    
    def test_default_sending_speed(self):
        """Test that default sending speed is Normal"""
        self.assertEqual(self.app.sending_speed, "Normal")
        self.assertEqual(self.app.get_sending_delay(), 0.5)
    
    def test_speed_combobox_initialization(self):
        """Test that speed combobox is properly initialized"""
        self.assertTrue(hasattr(self.app, 'speed_combobox'))
        self.assertEqual(self.app.speed_combobox.get(), "Normal")
        self.assertEqual(list(self.app.speed_combobox['values']), ["Fast", "Normal", "Slow"])
    
    def test_get_sending_delay_all_speeds(self):
        """Test get_sending_delay returns correct values for all speeds"""
        # Test Fast
        self.app.sending_speed = "Fast"
        self.assertEqual(self.app.get_sending_delay(), 0.2)
        
        # Test Normal  
        self.app.sending_speed = "Normal"
        self.assertEqual(self.app.get_sending_delay(), 0.5)
        
        # Test Slow
        self.app.sending_speed = "Slow"
        self.assertEqual(self.app.get_sending_delay(), 1.0)
    
    def test_get_sending_delay_invalid_speed(self):
        """Test get_sending_delay defaults to Normal for invalid speed"""
        self.app.sending_speed = "InvalidSpeed"
        self.assertEqual(self.app.get_sending_delay(), 0.5)  # Should default to Normal
    
    def test_on_speed_changed(self):
        """Test speed change handler updates sending_speed"""
        # Simulate speed change to Fast
        self.app.speed_combobox.set("Fast")
        mock_event = Mock()
        self.app.on_speed_changed(mock_event)
        self.assertEqual(self.app.sending_speed, "Fast")
        
        # Simulate speed change to Slow
        self.app.speed_combobox.set("Slow")
        self.app.on_speed_changed(mock_event)
        self.assertEqual(self.app.sending_speed, "Slow")
    
    def test_emergency_stop_setup(self):
        """Test that emergency stop key binding is set up"""
        self.assertTrue(hasattr(self.app, 'setup_global_key_bindings'))
        # The method should exist and be callable
        self.assertTrue(callable(self.app.setup_global_key_bindings))
    
    def test_handle_emergency_stop_when_not_sending(self):
        """Test emergency stop does nothing when not sending"""
        self.app.is_sending = False
        mock_event = Mock()
        
        # Should not change anything when not sending
        with patch('main.messagebox.showinfo') as mock_info:
            self.app.handle_emergency_stop(mock_event)
            mock_info.assert_not_called()
    
    def test_handle_emergency_stop_when_sending(self):
        """Test emergency stop works when sending"""
        self.app.is_sending = True
        self.app.send_all_button = Mock()
        self.app.send_thread = Mock()
        self.app.send_thread.is_alive.return_value = True
        mock_event = Mock()
        
        with patch('main.messagebox.showinfo') as mock_info:
            self.app.handle_emergency_stop(mock_event)
            
            # Should stop sending
            self.assertFalse(self.app.is_sending)
            self.app.send_all_button.config.assert_called_with(text="Send All")
            self.assertIsNone(self.app.send_thread)

if __name__ == '__main__':
    unittest.main()