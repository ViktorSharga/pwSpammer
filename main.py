import tkinter as tk
from tkinter import ttk

class InGameChatHelper:
    def __init__(self, root):
        self.root = root
        self.root.title("In-Game Chat Helper")
        self.root.geometry("800x600")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_memberlist_tab()
        self.create_templates_tab()
        self.create_spammer_tab()
        self.create_setup_tab()
    
    def create_memberlist_tab(self):
        # MemberList Tab
        self.memberlist_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.memberlist_frame, text="MemberList")
        
        # TODO: Implement MemberList functionality
        placeholder_label = ttk.Label(self.memberlist_frame, text="MemberList Tab - Coming Soon")
        placeholder_label.pack(pady=20)
    
    def create_templates_tab(self):
        # Templates Tab
        self.templates_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.templates_frame, text="Templates")
        
        # TODO: Implement Templates functionality
        placeholder_label = ttk.Label(self.templates_frame, text="Templates Tab - Coming Soon")
        placeholder_label.pack(pady=20)
    
    def create_spammer_tab(self):
        # Spammer Tab
        self.spammer_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.spammer_frame, text="Spammer")
        
        # TODO: Implement Spammer functionality
        placeholder_label = ttk.Label(self.spammer_frame, text="Spammer Tab - Coming Soon")
        placeholder_label.pack(pady=20)
    
    def create_setup_tab(self):
        # Setup Tab
        self.setup_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.setup_frame, text="Setup")
        
        # TODO: Implement Setup functionality
        placeholder_label = ttk.Label(self.setup_frame, text="Setup Tab - Coming Soon")
        placeholder_label.pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = InGameChatHelper(root)
    root.mainloop()