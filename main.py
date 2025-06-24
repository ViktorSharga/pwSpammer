import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import time
import threading
import platform

# Platform-specific imports
if platform.system() == "Windows":
    try:
        import win32gui
        import win32api
        import win32con
        import win32process
        import psutil
        WINDOWS_AVAILABLE = True
    except ImportError:
        WINDOWS_AVAILABLE = False
else:
    WINDOWS_AVAILABLE = False

class InGameChatHelper:
    def __init__(self, root):
        self.root = root
        self.root.title("In-Game Chat Helper")
        self.root.geometry("800x600")
        
        self.members = []
        self.selected_member_index = None
        self.templates = []
        self.selected_template_tile = None
        
        # Setup Tab variables
        self.is_connected = False
        self.game_window_handle = None
        self.game_process_id = None
        self.coord1 = None
        self.coord2 = None
        self.setting_coordinate = None
        
        self.create_widgets()
        self.setup_hotkeys()
    
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
        
        # Control buttons frame
        control_buttons_frame = ttk.Frame(self.templates_frame)
        control_buttons_frame.pack(fill='x', padx=10, pady=5)
        
        # Control buttons
        ttk.Button(control_buttons_frame, text="Add", command=self.add_template).pack(side='left', padx=5)
        self.edit_template_button = ttk.Button(control_buttons_frame, text="Edit", command=self.edit_template, state='disabled')
        self.edit_template_button.pack(side='left', padx=5)
        self.remove_template_button = ttk.Button(control_buttons_frame, text="Remove", command=self.remove_template, state='disabled')
        self.remove_template_button.pack(side='left', padx=5)
        
        # Templates display area with scrollbar
        templates_canvas_frame = ttk.Frame(self.templates_frame)
        templates_canvas_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create canvas and scrollbar
        self.templates_canvas = tk.Canvas(templates_canvas_frame, highlightthickness=0)
        templates_scrollbar = ttk.Scrollbar(templates_canvas_frame, orient='vertical', command=self.templates_canvas.yview)
        self.templates_canvas.configure(yscrollcommand=templates_scrollbar.set)
        
        # Pack canvas and scrollbar
        self.templates_canvas.pack(side='left', fill='both', expand=True)
        templates_scrollbar.pack(side='right', fill='y')
        
        # Create scrollable frame inside canvas
        self.templates_scrollable_frame = ttk.Frame(self.templates_canvas)
        self.templates_canvas_window = self.templates_canvas.create_window((0, 0), window=self.templates_scrollable_frame, anchor='nw')
        
        # Bind canvas resize event
        self.templates_canvas.bind('<Configure>', self.on_templates_canvas_configure)
        self.templates_scrollable_frame.bind('<Configure>', self.on_templates_frame_configure)
        
        # Bind mousewheel scrolling
        self.templates_canvas.bind_all('<MouseWheel>', self.on_templates_mousewheel)
    
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
        
        # Connection Management Section
        connection_frame = ttk.LabelFrame(self.setup_frame, text="Connection Management", padding="10")
        connection_frame.pack(fill='x', padx=10, pady=10)
        
        # Status display
        status_frame = ttk.Frame(connection_frame)
        status_frame.pack(fill='x', pady=5)
        
        ttk.Label(status_frame, text="Status:").pack(side='left')
        self.status_label = ttk.Label(status_frame, text="UNCONNECTED", foreground='red')
        self.status_label.pack(side='left', padx=(5, 0))
        
        # PID display
        self.pid_label = ttk.Label(status_frame, text="")
        self.pid_label.pack(side='left', padx=(10, 0))
        
        # Hotkey info
        hotkey_frame = ttk.Frame(connection_frame)
        hotkey_frame.pack(fill='x', pady=5)
        
        ttk.Label(hotkey_frame, text="Hotkey: CTRL+SHIFT+1 (Connect to focused window)").pack(side='left')
        
        # Test Connection button
        test_conn_frame = ttk.Frame(connection_frame)
        test_conn_frame.pack(fill='x', pady=5)
        
        self.test_connection_button = ttk.Button(test_conn_frame, text="Test Connection", 
                                               command=self.test_game_connection, state='disabled')
        self.test_connection_button.pack(side='left')
        
        # Chat Calibration Section
        calibration_frame = ttk.LabelFrame(self.setup_frame, text="Chat Calibration", padding="10")
        calibration_frame.pack(fill='x', padx=10, pady=10)
        
        # Coordinate setting buttons
        coord_buttons_frame = ttk.Frame(calibration_frame)
        coord_buttons_frame.pack(fill='x', pady=5)
        
        self.set_coord1_button = ttk.Button(coord_buttons_frame, text="Set Coordinate 1", 
                                          command=lambda: self.set_coordinate(1), state='disabled')
        self.set_coord1_button.pack(side='left', padx=5)
        
        self.set_coord2_button = ttk.Button(coord_buttons_frame, text="Set Coordinate 2", 
                                          command=lambda: self.set_coordinate(2), state='disabled')
        self.set_coord2_button.pack(side='left', padx=5)
        
        # Coordinate display
        coord_display_frame = ttk.Frame(calibration_frame)
        coord_display_frame.pack(fill='x', pady=10)
        
        ttk.Label(coord_display_frame, text="Saved Coordinates:").pack(anchor='w')
        self.coord1_label = ttk.Label(coord_display_frame, text="Coord1: Not set")
        self.coord1_label.pack(anchor='w', padx=20)
        self.coord2_label = ttk.Label(coord_display_frame, text="Coord2: Not set")
        self.coord2_label.pack(anchor='w', padx=20)
        
        # Test button
        test_frame = ttk.Frame(calibration_frame)
        test_frame.pack(fill='x', pady=5)
        
        self.test_clear_button = ttk.Button(test_frame, text="Test ClearChatArea", 
                                          command=self.test_clear_chat_area, state='disabled')
        self.test_clear_button.pack(side='left')
        
        # Platform warning
        if not WINDOWS_AVAILABLE:
            warning_frame = ttk.Frame(self.setup_frame)
            warning_frame.pack(fill='x', padx=10, pady=10)
            
            warning_label = ttk.Label(warning_frame, text="⚠ Windows-specific features not available on this platform", 
                                    foreground='orange')
            warning_label.pack()
    
    # MemberList Tab Methods
    def is_duplicate_member(self, member_name):
        """Check if member name already exists (case-insensitive)"""
        return member_name.lower() in [member.lower() for member in self.members]
    
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
            clipboard_content = self.root.clipboard_get().strip()
            if len(clipboard_content) <= 100:
                if self.is_duplicate_member(clipboard_content):
                    messagebox.showwarning("Warning", f"Member '{clipboard_content}' already exists")
                else:
                    self.members.append(clipboard_content)
                    self.refresh_members_list()
            else:
                messagebox.showwarning("Warning", "Clipboard content exceeds 100 characters limit")
        except tk.TclError:
            messagebox.showerror("Error", "No content in clipboard")
    
    def add_member(self):
        dialog = MemberDialog(self.root, "Add Member")
        if dialog.result:
            if self.is_duplicate_member(dialog.result):
                messagebox.showwarning("Warning", f"Member '{dialog.result}' already exists")
            else:
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
                    loaded_members = json.load(f)
                
                # Filter out duplicates (case-insensitive)
                new_members = []
                duplicates = []
                existing_lower = [member.lower() for member in self.members]
                
                for member in loaded_members:
                    member = member.strip()
                    if member.lower() not in existing_lower and member.lower() not in [m.lower() for m in new_members]:
                        new_members.append(member)
                        existing_lower.append(member.lower())
                    else:
                        duplicates.append(member)
                
                # Add new members to existing list
                self.members.extend(new_members)
                self.refresh_members_list()
                
                # Show result message
                if duplicates:
                    messagebox.showinfo("Success", 
                        f"Loaded {len(new_members)} new members.\n"
                        f"Skipped {len(duplicates)} duplicates: {', '.join(duplicates[:5])}"
                        f"{'...' if len(duplicates) > 5 else ''}")
                else:
                    messagebox.showinfo("Success", f"Loaded {len(new_members)} members successfully")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load: {str(e)}")
    
    # Templates Tab Methods
    def on_templates_canvas_configure(self, event):
        self.templates_canvas.configure(scrollregion=self.templates_canvas.bbox('all'))
        canvas_width = event.width
        self.templates_canvas.itemconfig(self.templates_canvas_window, width=canvas_width)
    
    def on_templates_frame_configure(self, event):
        self.templates_canvas.configure(scrollregion=self.templates_canvas.bbox('all'))
    
    def on_templates_mousewheel(self, event):
        self.templates_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def add_template(self):
        dialog = TemplateDialog(self.root, "Add Template")
        if dialog.result:
            self.templates.append(dialog.result)
            self.refresh_templates_display()
    
    def edit_template(self):
        if self.selected_template_tile is not None:
            template_index = self.selected_template_tile
            current_template = self.templates[template_index]
            dialog = TemplateDialog(self.root, "Edit Template", current_template['short_name'], current_template['content'])
            if dialog.result:
                self.templates[template_index] = dialog.result
                self.refresh_templates_display()
    
    def remove_template(self):
        if self.selected_template_tile is not None:
            del self.templates[self.selected_template_tile]
            self.refresh_templates_display()
            self.selected_template_tile = None
            self.edit_template_button.config(state='disabled')
            self.remove_template_button.config(state='disabled')
    
    def refresh_templates_display(self):
        # Clear existing tiles
        for widget in self.templates_scrollable_frame.winfo_children():
            widget.destroy()
        
        # Create new tiles
        for i, template in enumerate(self.templates):
            self.create_template_tile(i, template)
        
        # Update scroll region
        self.templates_scrollable_frame.update_idletasks()
        self.templates_canvas.configure(scrollregion=self.templates_canvas.bbox('all'))
    
    def create_template_tile(self, index, template):
        # Create tile frame
        tile_frame = ttk.Frame(self.templates_scrollable_frame, relief='solid', borderwidth=1)
        tile_frame.pack(fill='x', padx=5, pady=2)
        
        # Short name label
        short_name_label = ttk.Label(tile_frame, text=template['short_name'], font=('TkDefaultFont', 10, 'bold'))
        short_name_label.pack(anchor='w', padx=10, pady=(5, 0))
        
        # Content label (truncated if needed)
        content_text = template['content']
        if len(content_text) > 100:
            content_text = content_text[:100] + "..."
        
        content_label = ttk.Label(tile_frame, text=content_text, wraplength=400, justify='left')
        content_label.pack(anchor='w', padx=10, pady=(0, 5))
        
        # Bind click events for selection
        def on_tile_click(event, tile_index=index):
            self.select_template_tile(tile_index)
        
        tile_frame.bind('<Button-1>', on_tile_click)
        short_name_label.bind('<Button-1>', on_tile_click)
        content_label.bind('<Button-1>', on_tile_click)
    
    def select_template_tile(self, index):
        # Deselect previous tile
        if self.selected_template_tile is not None:
            self.update_tile_selection(self.selected_template_tile, False)
        
        # Select new tile
        self.selected_template_tile = index
        self.update_tile_selection(index, True)
        
        # Enable buttons
        self.edit_template_button.config(state='normal')
        self.remove_template_button.config(state='normal')
    
    def update_tile_selection(self, index, selected):
        tiles = self.templates_scrollable_frame.winfo_children()
        if index < len(tiles):
            tile = tiles[index]
            if selected:
                tile.configure(style='Selected.TFrame')
            else:
                tile.configure(style='TFrame')
    
    # Setup Tab Methods
    def setup_hotkeys(self):
        if WINDOWS_AVAILABLE:
            # Register global hotkey CTRL+SHIFT+1
            threading.Thread(target=self.hotkey_listener, daemon=True).start()
    
    def hotkey_listener(self):
        if not WINDOWS_AVAILABLE:
            return
        
        while True:
            try:
                # Check for CTRL+SHIFT+1 hotkey
                if (win32api.GetAsyncKeyState(win32con.VK_CONTROL) & 0x8000 and
                    win32api.GetAsyncKeyState(win32con.VK_SHIFT) & 0x8000 and
                    win32api.GetAsyncKeyState(0x31) & 0x8000):  # '1' key
                    
                    self.root.after(0, self.handle_hotkey)
                    time.sleep(0.5)  # Prevent multiple triggers
                
                time.sleep(0.1)
            except Exception:
                time.sleep(1)
    
    def handle_hotkey(self):
        if not WINDOWS_AVAILABLE:
            messagebox.showerror("Error", "Windows-specific features not available")
            return
        
        try:
            # Get the currently focused window
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                messagebox.showerror("Error", "No window is currently focused")
                return
            
            # Get window title and process info
            window_title = win32gui.GetWindowText(hwnd)
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            # Get process name
            try:
                process = psutil.Process(pid)
                process_name = process.name()
            except:
                messagebox.showerror("Error", "Could not get process information")
                return
            
            # Validate process and window title
            if process_name.lower() != "elementclient.exe":
                messagebox.showerror("Error", f"Expected 'elementclient.exe', found '{process_name}'")
                return
            
            if "Asgard Perfect World" not in window_title:
                messagebox.showerror("Error", f"Expected window title containing 'Asgard Perfect World', found '{window_title}'")
                return
            
            # Store connection info
            self.game_window_handle = hwnd
            self.game_process_id = pid
            self.is_connected = True
            
            # Update UI
            self.update_connection_status()
            
            messagebox.showinfo("Success", f"Connected to game window (PID: {pid})")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {str(e)}")
    
    def update_connection_status(self):
        if self.is_connected:
            self.status_label.config(text="CONNECTED", foreground='green')
            self.pid_label.config(text=f"PID: {self.game_process_id}")
            self.test_connection_button.config(state='normal')
            self.set_coord1_button.config(state='normal')
            self.set_coord2_button.config(state='normal')
            self.update_test_button_state()
        else:
            self.status_label.config(text="UNCONNECTED", foreground='red')
            self.pid_label.config(text="")
            self.test_connection_button.config(state='disabled')
            self.set_coord1_button.config(state='disabled')
            self.set_coord2_button.config(state='disabled')
            self.test_clear_button.config(state='disabled')
    
    def test_game_connection(self):
        if not WINDOWS_AVAILABLE:
            messagebox.showerror("Error", "Windows-specific features not available")
            return
        
        if not self.is_connected or not self.game_window_handle:
            messagebox.showerror("Error", "Not connected to game window")
            return
        
        try:
            # Check if window still exists
            if not win32gui.IsWindow(self.game_window_handle):
                self.is_connected = False
                self.update_connection_status()
                messagebox.showerror("Error", "Game window no longer exists")
                return
            
            # Bring window to front
            win32gui.SetForegroundWindow(self.game_window_handle)
            messagebox.showinfo("Success", "Game window brought to focus")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to focus window: {str(e)}")
    
    def set_coordinate(self, coord_num):
        if not WINDOWS_AVAILABLE:
            messagebox.showerror("Error", "Windows-specific features not available")
            return
        
        if not self.is_connected or not self.game_window_handle:
            messagebox.showerror("Error", "Not connected to game window")
            return
        
        self.setting_coordinate = coord_num
        
        # Focus game window
        try:
            win32gui.SetForegroundWindow(self.game_window_handle)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to focus game window: {str(e)}")
            return
        
        # Hide main window temporarily
        self.root.withdraw()
        
        # Create overlay window for coordinate capture
        self.create_coordinate_overlay()
    
    def create_coordinate_overlay(self):
        if not WINDOWS_AVAILABLE:
            return
        
        # Create transparent overlay
        overlay = tk.Toplevel()
        overlay.attributes('-alpha', 0.3)
        overlay.attributes('-topmost', True)
        overlay.configure(bg='red')
        
        # Make it fullscreen
        overlay.state('zoomed')
        overlay.overrideredirect(True)
        
        # Add instruction label
        label = tk.Label(overlay, text=f"Click to set Coordinate {self.setting_coordinate}\nPress ESC to cancel", 
                        fg='white', bg='red', font=('Arial', 16))
        label.pack(expand=True)
        
        # Bind click event
        def on_click(event):
            x, y = event.x_root, event.y_root
            if self.setting_coordinate == 1:
                self.coord1 = (x, y)
                self.coord1_label.config(text=f"Coord1: ({x}, {y})")
            else:
                self.coord2 = (x, y)
                self.coord2_label.config(text=f"Coord2: ({x}, {y})")
            
            self.update_test_button_state()
            overlay.destroy()
            self.root.deiconify()
            self.setting_coordinate = None
        
        def on_escape(event):
            overlay.destroy()
            self.root.deiconify()
            self.setting_coordinate = None
        
        overlay.bind('<Button-1>', on_click)
        overlay.bind('<Escape>', on_escape)
        overlay.focus_set()
    
    def update_test_button_state(self):
        if self.is_connected and self.coord1 and self.coord2:
            self.test_clear_button.config(state='normal')
        else:
            self.test_clear_button.config(state='disabled')
    
    def test_clear_chat_area(self):
        if not WINDOWS_AVAILABLE:
            messagebox.showerror("Error", "Windows-specific features not available")
            return
        
        if not self.is_connected or not self.coord1 or not self.coord2:
            messagebox.showerror("Error", "Missing connection or coordinates")
            return
        
        try:
            self.clear_chat_area()
            messagebox.showinfo("Success", "ClearChatArea executed successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to execute ClearChatArea: {str(e)}")
    
    def clear_chat_area(self):
        if not WINDOWS_AVAILABLE:
            return
        
        # Focus game window
        win32gui.SetForegroundWindow(self.game_window_handle)
        time.sleep(0.1)
        
        # Click Coord2
        win32api.SetCursorPos(self.coord2)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        
        # Wait 100ms
        time.sleep(0.1)
        
        # Click Coord1
        win32api.SetCursorPos(self.coord1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


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


class TemplateDialog:
    def __init__(self, parent, title, initial_short_name="", initial_content=""):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Short name field
        ttk.Label(self.dialog, text="Short Name:").pack(pady=(10, 5))
        self.short_name_entry = ttk.Entry(self.dialog, width=40)
        self.short_name_entry.pack(pady=5)
        self.short_name_entry.insert(0, initial_short_name)
        
        # Content field
        ttk.Label(self.dialog, text="Message Content (max 300 characters):").pack(pady=(10, 5))
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(self.dialog)
        text_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.content_text = tk.Text(text_frame, height=15, width=50, wrap='word')
        content_scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.content_text.yview)
        self.content_text.configure(yscrollcommand=content_scrollbar.set)
        
        self.content_text.pack(side='left', fill='both', expand=True)
        content_scrollbar.pack(side='right', fill='y')
        
        self.content_text.insert('1.0', initial_content)
        
        # Character count label
        self.char_count_label = ttk.Label(self.dialog, text=f"Characters: {len(initial_content)}/300")
        self.char_count_label.pack(pady=5)
        
        # Bind text change event
        self.content_text.bind('<KeyRelease>', self.on_text_change)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side='left', padx=5)
        
        # Focus on short name entry
        self.short_name_entry.focus()
        self.short_name_entry.select_range(0, tk.END)
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def on_text_change(self, event):
        content = self.content_text.get('1.0', 'end-1c')
        char_count = len(content)
        self.char_count_label.config(text=f"Characters: {char_count}/300")
        
        # Change color if over limit
        if char_count > 300:
            self.char_count_label.config(foreground='red')
        else:
            self.char_count_label.config(foreground='black')
    
    def ok_clicked(self):
        short_name = self.short_name_entry.get().strip()
        content = self.content_text.get('1.0', 'end-1c').strip()
        
        if not short_name:
            messagebox.showerror("Error", "Short name is required")
            return
        
        if not content:
            messagebox.showerror("Error", "Message content is required")
            return
        
        if len(content) > 300:
            messagebox.showerror("Error", "Message content exceeds 300 characters limit")
            return
        
        self.result = {
            'short_name': short_name,
            'content': content
        }
        self.dialog.destroy()
    
    def cancel_clicked(self):
        self.dialog.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = InGameChatHelper(root)
    root.mainloop()