import unittest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import InGameChatHelper, TemplateDialog


class TestTemplatesTab(unittest.TestCase):
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
    
    def test_add_template(self):
        with patch('main.TemplateDialog') as mock_dialog:
            mock_instance = Mock()
            mock_instance.result = {
                'short_name': 'Test Template',
                'content': 'This is a test message'
            }
            mock_dialog.return_value = mock_instance
            
            initial_count = len(self.app.templates)
            self.app.add_template()
            
            self.assertEqual(len(self.app.templates), initial_count + 1)
            self.assertEqual(self.app.templates[-1]['short_name'], 'Test Template')
            self.assertEqual(self.app.templates[-1]['content'], 'This is a test message')
    
    def test_edit_template(self):
        self.app.templates = [{
            'short_name': 'Original',
            'content': 'Original content'
        }]
        self.app.selected_template_tile = 0
        
        with patch('main.TemplateDialog') as mock_dialog:
            mock_instance = Mock()
            mock_instance.result = {
                'short_name': 'Updated',
                'content': 'Updated content'
            }
            mock_dialog.return_value = mock_instance
            
            self.app.edit_template()
            
            self.assertEqual(self.app.templates[0]['short_name'], 'Updated')
            self.assertEqual(self.app.templates[0]['content'], 'Updated content')
    
    def test_remove_template(self):
        self.app.templates = [
            {'short_name': 'Template1', 'content': 'Content1'},
            {'short_name': 'Template2', 'content': 'Content2'}
        ]
        self.app.selected_template_tile = 0
        
        self.app.remove_template()
        
        self.assertEqual(len(self.app.templates), 1)
        self.assertEqual(self.app.templates[0]['short_name'], 'Template2')
        self.assertIsNone(self.app.selected_template_tile)
    
    def test_select_template_tile(self):
        self.app.templates = [
            {'short_name': 'Template1', 'content': 'Content1'},
            {'short_name': 'Template2', 'content': 'Content2'}
        ]
        self.app.refresh_templates_display()
        
        self.app.select_template_tile(1)
        
        self.assertEqual(self.app.selected_template_tile, 1)
        self.assertEqual(str(self.app.edit_template_button['state']), 'normal')
        self.assertEqual(str(self.app.remove_template_button['state']), 'normal')
    
    def test_update_tile_selection(self):
        self.app.templates = [
            {'short_name': 'Template1', 'content': 'Content1'}
        ]
        self.app.refresh_templates_display()
        
        tiles = self.app.templates_scrollable_frame.winfo_children()
        if tiles:
            initial_relief = tiles[0]['relief']
            self.app.update_tile_selection(0, True)
            self.assertEqual(str(tiles[0]['relief']), 'raised')
            
            self.app.update_tile_selection(0, False)
            self.assertEqual(str(tiles[0]['relief']), 'solid')


class TestTemplateDialog(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window for headless testing
        
    def tearDown(self):
        try:
            self.root.destroy()
        except tk.TclError:
            pass
    
    def test_template_dialog_ok(self):
        with patch.object(tk.Toplevel, 'wait_window'):
            dialog = TemplateDialog(self.root, "Test Dialog")
            dialog.short_name_entry.insert(0, "TestTemplate")
            dialog.content_text.insert('1.0', "Test content")
            dialog.ok_clicked()
            
            self.assertIsNotNone(dialog.result)
            self.assertEqual(dialog.result['short_name'], "TestTemplate")
            self.assertEqual(dialog.result['content'], "Test content")
    
    def test_template_dialog_validation(self):
        with patch.object(tk.Toplevel, 'wait_window'), \
             patch('main.messagebox.showerror') as mock_error:
            dialog = TemplateDialog(self.root, "Test Dialog")
            
            # Test empty short name
            dialog.ok_clicked()
            mock_error.assert_called_with("Error", "Short name is required")
            
            # Test empty content
            dialog.short_name_entry.insert(0, "TestTemplate")
            dialog.ok_clicked()
            mock_error.assert_called_with("Error", "Message content is required")
            
            # Test content too long
            dialog.content_text.insert('1.0', "x" * 301)
            dialog.ok_clicked()
            mock_error.assert_called_with("Error", "Message content exceeds 300 characters limit")
    
    def test_template_dialog_char_count(self):
        with patch.object(tk.Toplevel, 'wait_window'):
            dialog = TemplateDialog(self.root, "Test Dialog")
            
            # Test normal char count
            dialog.content_text.insert('1.0', "Test")
            dialog.on_text_change(None)
            self.assertIn("4/300", dialog.char_count_label['text'])
            
            # Test over limit
            dialog.content_text.delete('1.0', tk.END)
            dialog.content_text.insert('1.0', "x" * 301)
            dialog.on_text_change(None)
            self.assertIn("301/300", dialog.char_count_label['text'])
            self.assertEqual(str(dialog.char_count_label['foreground']), 'red')


if __name__ == '__main__':
    unittest.main()