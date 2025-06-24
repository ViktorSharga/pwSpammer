import unittest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import InGameChatHelper, MemberDialog


class TestMemberListTab(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = InGameChatHelper(self.root)
        
    def tearDown(self):
        self.root.destroy()
    
    def test_is_duplicate_member(self):
        self.app.members = ["Alice", "Bob", "Charlie"]
        
        self.assertTrue(self.app.is_duplicate_member("Alice"))
        self.assertTrue(self.app.is_duplicate_member("alice"))
        self.assertTrue(self.app.is_duplicate_member("ALICE"))
        self.assertFalse(self.app.is_duplicate_member("David"))
        self.assertFalse(self.app.is_duplicate_member(""))
    
    def test_add_member(self):
        with patch('main.MemberDialog') as mock_dialog:
            mock_instance = Mock()
            mock_instance.result = "NewMember"
            mock_dialog.return_value = mock_instance
            
            initial_count = len(self.app.members)
            self.app.add_member()
            
            self.assertEqual(len(self.app.members), initial_count + 1)
            self.assertIn("NewMember", self.app.members)
    
    def test_add_member_duplicate(self):
        self.app.members = ["ExistingMember"]
        
        with patch('main.MemberDialog') as mock_dialog, \
             patch('main.messagebox.showwarning') as mock_warning:
            mock_instance = Mock()
            mock_instance.result = "ExistingMember"
            mock_dialog.return_value = mock_instance
            
            self.app.add_member()
            
            mock_warning.assert_called_once()
            self.assertEqual(len(self.app.members), 1)
    
    def test_add_from_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append("ClipboardMember")
        
        initial_count = len(self.app.members)
        self.app.add_from_clipboard()
        
        self.assertEqual(len(self.app.members), initial_count + 1)
        self.assertIn("ClipboardMember", self.app.members)
    
    def test_add_from_clipboard_too_long(self):
        with patch('main.messagebox.showwarning') as mock_warning:
            self.root.clipboard_clear()
            self.root.clipboard_append("x" * 101)
            
            initial_count = len(self.app.members)
            self.app.add_from_clipboard()
            
            mock_warning.assert_called_once()
            self.assertEqual(len(self.app.members), initial_count)
    
    def test_remove_member(self):
        self.app.members = ["Alice", "Bob", "Charlie"]
        self.app.selected_member_index = 1
        
        self.app.remove_member()
        
        self.assertEqual(len(self.app.members), 2)
        self.assertNotIn("Bob", self.app.members)
        self.assertIsNone(self.app.selected_member_index)
    
    def test_edit_member(self):
        self.app.members = ["Alice", "Bob", "Charlie"]
        self.app.selected_member_index = 1
        
        with patch('main.MemberDialog') as mock_dialog:
            mock_instance = Mock()
            mock_instance.result = "UpdatedBob"
            mock_dialog.return_value = mock_instance
            
            self.app.edit_member()
            
            self.assertEqual(self.app.members[1], "UpdatedBob")
            self.assertNotIn("Bob", self.app.members)
    
    def test_delete_all_members(self):
        self.app.members = ["Alice", "Bob", "Charlie"]
        
        with patch('main.messagebox.askyesno', return_value=True):
            self.app.delete_all_members()
            
            self.assertEqual(len(self.app.members), 0)
            self.assertIsNone(self.app.selected_member_index)
    
    def test_save_members(self):
        self.app.members = ["Alice", "Bob"]
        
        with patch('main.filedialog.asksaveasfilename', return_value="test.json"), \
             patch('builtins.open', unittest.mock.mock_open()) as mock_file, \
             patch('main.messagebox.showinfo') as mock_info:
            
            self.app.save_members()
            
            mock_file.assert_called_once_with("test.json", 'w')
            mock_info.assert_called_once()
    
    def test_load_members(self):
        existing_members = ["Alice"]
        self.app.members = existing_members.copy()
        
        loaded_data = ["Bob", "Charlie", "Alice"]  # Alice is duplicate
        
        with patch('main.filedialog.askopenfilename', return_value="test.json"), \
             patch('builtins.open', unittest.mock.mock_open(read_data='["Bob", "Charlie", "Alice"]')), \
             patch('main.messagebox.showinfo') as mock_info:
            
            self.app.load_members()
            
            self.assertEqual(len(self.app.members), 3)  # Alice, Bob, Charlie
            self.assertIn("Bob", self.app.members)
            self.assertIn("Charlie", self.app.members)
            mock_info.assert_called_once()


class TestMemberDialog(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        
    def tearDown(self):
        self.root.destroy()
    
    def test_member_dialog_ok(self):
        with patch.object(tk.Toplevel, 'wait_window'):
            dialog = MemberDialog(self.root, "Test Dialog", "Initial")
            dialog.entry.delete(0, tk.END)
            dialog.entry.insert(0, "TestMember")
            dialog.ok_clicked()
            
            self.assertEqual(dialog.result, "TestMember")
    
    def test_member_dialog_cancel(self):
        with patch.object(tk.Toplevel, 'wait_window'):
            dialog = MemberDialog(self.root, "Test Dialog")
            dialog.cancel_clicked()
            
            self.assertIsNone(dialog.result)


if __name__ == '__main__':
    unittest.main()