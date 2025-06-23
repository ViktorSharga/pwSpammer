import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json

class InGameChatHelper:
    def __init__(self, root):
        self.root = root
        self.root.title("In-Game Chat Helper")
        self.root.geometry("800x600")
        
        self.members = []
        self.selected_member_index = None
        
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
        
        # Top control buttons frame
        top_buttons_frame = ttk.Frame(self.memberlist_frame)
        top_buttons_frame.pack(fill='x', padx=10, pady=5)
        
        # Top control buttons
        ttk.Button(top_buttons_frame, text="Add from Clipboard", command=self.add_from_clipboard).pack(side='left', padx=2)
        ttk.Button(top_buttons_frame, text="Add", command=self.add_member).pack(side='left', padx=2)
        self.edit_button = ttk.Button(top_buttons_frame, text="Edit", command=self.edit_member, state='disabled')
        self.edit_button.pack(side='left', padx=2)
        self.remove_button = ttk.Button(top_buttons_frame, text="Remove", command=self.remove_member, state='disabled')
        self.remove_button.pack(side='left', padx=2)
        ttk.Button(top_buttons_frame, text="Delete All", command=self.delete_all_members).pack(side='left', padx=2)
        
        # Members list frame with scrollbar
        list_frame = ttk.Frame(self.memberlist_frame)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Scrollable listbox
        self.members_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.members_listbox.yview)
        self.members_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.members_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind selection event
        self.members_listbox.bind('<<ListboxSelect>>', self.on_member_select)
        
        # Bottom buttons frame
        bottom_buttons_frame = ttk.Frame(self.memberlist_frame)
        bottom_buttons_frame.pack(fill='x', padx=10, pady=5)
        
        # Bottom buttons
        ttk.Button(bottom_buttons_frame, text="SAVE", command=self.save_members).pack(side='left', padx=10)
        ttk.Button(bottom_buttons_frame, text="LOAD", command=self.load_members).pack(side='right', padx=10)
    
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
    
    # MemberList Tab Methods
    def on_member_select(self, event):
        selection = self.members_listbox.curselection()
        if selection:
            self.selected_member_index = selection[0]
            self.edit_button.config(state='normal')
            self.remove_button.config(state='normal')
        else:
            self.selected_member_index = None
            self.edit_button.config(state='disabled')
            self.remove_button.config(state='disabled')
    
    def add_from_clipboard(self):
        try:
            clipboard_content = self.root.clipboard_get()
            if len(clipboard_content) <= 100:
                self.members.append(clipboard_content)
                self.refresh_members_list()
            else:
                messagebox.showwarning("Warning", "Clipboard content exceeds 100 characters limit")
        except tk.TclError:
            messagebox.showerror("Error", "No content in clipboard")
    
    def add_member(self):
        dialog = MemberDialog(self.root, "Add Member")
        if dialog.result:
            self.members.append(dialog.result)
            self.refresh_members_list()
    
    def edit_member(self):
        if self.selected_member_index is not None:
            current_member = self.members[self.selected_member_index]
            dialog = MemberDialog(self.root, "Edit Member", current_member)
            if dialog.result:
                self.members[self.selected_member_index] = dialog.result
                self.refresh_members_list()
    
    def remove_member(self):
        if self.selected_member_index is not None:
            del self.members[self.selected_member_index]
            self.refresh_members_list()
            self.selected_member_index = None
            self.edit_button.config(state='disabled')
            self.remove_button.config(state='disabled')
    
    def delete_all_members(self):
        if self.members and messagebox.askyesno("Confirm", "Delete all members?"):
            self.members.clear()
            self.refresh_members_list()
            self.selected_member_index = None
            self.edit_button.config(state='disabled')
            self.remove_button.config(state='disabled')
    
    def refresh_members_list(self):
        self.members_listbox.delete(0, tk.END)
        for member in self.members:
            self.members_listbox.insert(tk.END, member)
    
    def save_members(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.members, f, indent=2)
                messagebox.showinfo("Success", "Members saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def load_members(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    self.members = json.load(f)
                self.refresh_members_list()
                messagebox.showinfo("Success", "Members loaded successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load: {str(e)}")


class MemberDialog:
    def __init__(self, parent, title, initial_value=""):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("300x150")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Entry field
        ttk.Label(self.dialog, text="Member name:").pack(pady=10)
        self.entry = ttk.Entry(self.dialog, width=30)
        self.entry.pack(pady=5)
        self.entry.insert(0, initial_value)
        self.entry.select_range(0, tk.END)
        self.entry.focus()
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side='left', padx=5)
        
        # Bind Enter key to OK
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def ok_clicked(self):
        value = self.entry.get().strip()
        if value:
            self.result = value
        self.dialog.destroy()
    
    def cancel_clicked(self):
        self.dialog.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = InGameChatHelper(root)
    root.mainloop()