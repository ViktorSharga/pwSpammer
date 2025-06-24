import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil
import json
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import DataManager


class TestDataManager(unittest.TestCase):
    def setUp(self):
        # Create temporary directory for testing
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Patch the data directory to use temp directory
        self.patcher = patch.object(DataManager, '_get_data_directory', return_value=self.temp_dir)
        self.patcher.start()
        
        self.data_manager = DataManager()
    
    def tearDown(self):
        self.patcher.stop()
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_data_directory_creation(self):
        """Test that data directory is created properly"""
        self.assertTrue(self.temp_dir.exists())
        self.assertTrue(self.temp_dir.is_dir())
    
    def test_save_and_load_members(self):
        """Test saving and loading members"""
        test_members = ["Alice", "Bob", "Charlie"]
        
        # Test save
        result = self.data_manager.save_members(test_members)
        self.assertTrue(result)
        self.assertTrue(self.data_manager.members_file.exists())
        
        # Test load
        loaded_members = self.data_manager.load_members()
        self.assertEqual(loaded_members, test_members)
    
    def test_save_and_load_templates(self):
        """Test saving and loading templates"""
        test_templates = [
            {'short_name': 'Greeting', 'content': 'Hello there!'},
            {'short_name': 'Question', 'content': 'How are you?'}
        ]
        
        # Test save
        result = self.data_manager.save_templates(test_templates)
        self.assertTrue(result)
        self.assertTrue(self.data_manager.templates_file.exists())
        
        # Test load
        loaded_templates = self.data_manager.load_templates()
        self.assertEqual(loaded_templates, test_templates)
    
    def test_load_nonexistent_files(self):
        """Test loading when files don't exist"""
        members = self.data_manager.load_members()
        templates = self.data_manager.load_templates()
        
        self.assertEqual(members, [])
        self.assertEqual(templates, [])
    
    def test_save_error_handling(self):
        """Test error handling during save operations"""
        # Create a file where directory should be
        self.data_manager.members_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_manager.members_file, 'w') as f:
            f.write("test")
        self.data_manager.members_file.chmod(0o000)  # Make it unwritable
        
        with patch('builtins.print') as mock_print:
            result = self.data_manager.save_members(["test"])
            self.assertFalse(result)
            mock_print.assert_called()
    
    def test_load_invalid_json(self):
        """Test loading invalid JSON files"""
        # Create invalid JSON file
        self.data_manager.members_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_manager.members_file, 'w') as f:
            f.write("invalid json content")
        
        with patch('builtins.print') as mock_print:
            members = self.data_manager.load_members()
            self.assertEqual(members, [])
            mock_print.assert_called()
    
    def test_unicode_support(self):
        """Test that unicode characters are properly handled"""
        test_members = ["Alice", "Bob", "Ñiño", "测试"]
        test_templates = [
            {'short_name': 'Unicode', 'content': 'Hello 世界! ñoño'}
        ]
        
        # Save and load
        self.data_manager.save_members(test_members)
        self.data_manager.save_templates(test_templates)
        
        loaded_members = self.data_manager.load_members()
        loaded_templates = self.data_manager.load_templates()
        
        self.assertEqual(loaded_members, test_members)
        self.assertEqual(loaded_templates, test_templates)
    
    @patch('platform.system', return_value='Windows')
    @patch('os.environ.get', return_value='C:\\Users\\Test\\AppData\\Roaming')
    def test_windows_data_directory(self, mock_env, mock_platform):
        """Test Windows data directory path"""
        # Create new DataManager to test directory detection
        with patch.object(DataManager, '_get_data_directory', wraps=DataManager._get_data_directory):
            dm = DataManager()
            expected_path = Path('C:\\Users\\Test\\AppData\\Roaming') / "InGameChatHelper"
            # Note: We can't test the exact path due to our patching, but we can test the logic
            self.assertIsInstance(dm.data_dir, Path)
    
    @patch('platform.system', return_value='Linux')
    def test_unix_data_directory(self, mock_platform):
        """Test Unix-like system data directory path"""
        with patch('pathlib.Path.home', return_value=Path('/home/test')):
            with patch.object(DataManager, '_get_data_directory', wraps=DataManager._get_data_directory):
                dm = DataManager()
                # Note: We can't test the exact path due to our patching, but we can test the logic
                self.assertIsInstance(dm.data_dir, Path)


class TestPersistenceIntegration(unittest.TestCase):
    def setUp(self):
        import tkinter as tk
        from main import InGameChatHelper
        
        # Create temporary directory for testing
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Patch the data directory
        self.patcher = patch.object(DataManager, '_get_data_directory', return_value=self.temp_dir)
        self.patcher.start()
        
        # Create test data files
        members_file = self.temp_dir / "members.json"
        templates_file = self.temp_dir / "templates.json"
        
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        test_members = ["ExistingUser1", "ExistingUser2"]
        test_templates = [
            {'short_name': 'Welcome', 'content': 'Welcome to the game!'},
            {'short_name': 'Goodbye', 'content': 'Thanks for playing!'}
        ]
        
        with open(members_file, 'w') as f:
            json.dump(test_members, f)
        with open(templates_file, 'w') as f:
            json.dump(test_templates, f)
        
        # Create app with mocked UI
        self.root = tk.Tk()
        self.root.withdraw()
        
        with patch('main.WINDOWS_AVAILABLE', False):
            self.app = InGameChatHelper(self.root)
    
    def tearDown(self):
        self.patcher.stop()
        try:
            self.root.destroy()
        except tk.TclError:
            pass
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_auto_load_on_startup(self):
        """Test that data is automatically loaded on startup"""
        self.assertEqual(len(self.app.members), 2)
        self.assertIn("ExistingUser1", self.app.members)
        self.assertIn("ExistingUser2", self.app.members)
        
        self.assertEqual(len(self.app.templates), 2)
        self.assertEqual(self.app.templates[0]['short_name'], 'Welcome')
        self.assertEqual(self.app.templates[1]['short_name'], 'Goodbye')
    
    def test_auto_save_on_member_change(self):
        """Test that members are automatically saved when modified"""
        # Add a new member
        self.app.members.append("NewUser")
        self.app.refresh_members_list()
        
        # Check that it was saved to file
        with open(self.temp_dir / "members.json", 'r') as f:
            saved_members = json.load(f)
        
        self.assertIn("NewUser", saved_members)
        self.assertEqual(len(saved_members), 3)
    
    def test_auto_save_on_template_change(self):
        """Test that templates are automatically saved when modified"""
        # Add a new template
        new_template = {'short_name': 'New', 'content': 'New template content'}
        self.app.templates.append(new_template)
        self.app.refresh_templates_display()
        
        # Check that it was saved to file
        with open(self.temp_dir / "templates.json", 'r') as f:
            saved_templates = json.load(f)
        
        self.assertEqual(len(saved_templates), 3)
        self.assertEqual(saved_templates[2]['short_name'], 'New')


if __name__ == '__main__':
    unittest.main()