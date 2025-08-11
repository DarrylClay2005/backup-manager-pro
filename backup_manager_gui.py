#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import subprocess
import threading
import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

class ModernBackupManagerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔄 Backup Manager Pro")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Modern color scheme
        self.colors = {
            'primary': '#2196F3',
            'primary_dark': '#1976D2', 
            'secondary': '#4CAF50',
            'error': '#F44336',
            'warning': '#FF9800',
            'success': '#4CAF50',
            'bg_light': '#FAFAFA',
            'bg_dark': '#F5F5F5',
            'text': '#212121',
            'text_secondary': '#757575'
        }
        
        # Configuration
        self.script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backup_manager_script.sh")
        self.log_file = "/var/log/backup_manager.log"
        self.config_file = "/home/desmond/.backup_manager_config.json"
        
        # Load configuration
        self.load_config()
        
        # Setup modern styling
        self.setup_styling()
        
        # Setup GUI
        self.setup_gui()
        
        # Start log monitoring
        self.start_log_monitoring()
        
        # Auto-refresh status
        self.auto_refresh_status()
        
        # Set window icon and initial focus
        try:
            self.root.attributes('-topmost', True)
            self.root.after(2000, lambda: self.root.attributes('-topmost', False))
        except:
            pass
    
    def load_config(self):
        """Load configuration from file"""
        default_config = {
            "auto_start": True,
            "local_backup_path": "/home/desmond/Local_Backups",
            "max_backup_size_gb": 4,
            "max_snapshots": 10,
            "refresh_interval": 30,
            "theme": "modern"
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self.config = {**default_config, **loaded_config}
            else:
                self.config = default_config
                self.save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = default_config
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def setup_styling(self):
        """Setup modern TTK styling"""
        style = ttk.Style()
        
        # Configure modern button style
        style.configure('Modern.TButton',
                       padding=(20, 10),
                       font=('Segoe UI', 10))
        
        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground='white',
                       focuscolor='none')
        
        style.configure('Primary.TButton',
                       background=self.colors['primary'],
                       foreground='white',
                       focuscolor='none')
        
        style.configure('Warning.TButton',
                       background=self.colors['warning'],
                       foreground='white',
                       focuscolor='none')
        
        # Configure labels
        style.configure('Title.TLabel',
                       font=('Segoe UI', 18, 'bold'),
                       foreground=self.colors['text'])
        
        style.configure('Subtitle.TLabel',
                       font=('Segoe UI', 12, 'bold'),
                       foreground=self.colors['text'])
        
        style.configure('Status.Success.TLabel',
                       foreground=self.colors['success'],
                       font=('Segoe UI', 10, 'bold'))
        
        style.configure('Status.Error.TLabel',
                       foreground=self.colors['error'],
                       font=('Segoe UI', 10, 'bold'))
        
        style.configure('Status.Warning.TLabel',
                       foreground=self.colors['warning'],
                       font=('Segoe UI', 10, 'bold'))
    
    def setup_gui(self):
        """Setup the modern GUI components"""
        # Configure root
        self.root.configure(bg=self.colors['bg_light'])
        
        # Main container with padding
        main_container = tk.Frame(self.root, bg=self.colors['bg_light'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(main_container)
        
        # Content area
        content_frame = tk.Frame(main_container, bg=self.colors['bg_light'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Left panel (status and controls)
        left_panel = tk.Frame(content_frame, bg=self.colors['bg_light'], width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Right panel (logs)
        right_panel = tk.Frame(content_frame, bg=self.colors['bg_light'])
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Setup panels
        self.create_status_panel(left_panel)
        self.create_controls_panel(left_panel)
        self.create_log_panel(right_panel)
        
        # Initial status check
        self.refresh_status()
        
        # Auto-run backup on startup if configured
        if self.config.get("auto_start", True):
            self.root.after(3000, self.create_backup)  # Delay 3 seconds
    
    def create_header(self, parent):
        """Create modern header"""
        header_frame = tk.Frame(parent, bg=self.colors['bg_light'], height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Title with icon
        title_frame = tk.Frame(header_frame, bg=self.colors['bg_light'])
        title_frame.pack(expand=True)
        
        title_label = ttk.Label(title_frame, text="🔄 Backup Manager Pro", style='Title.TLabel')
        title_label.pack(pady=(20, 5))
        
        subtitle_label = ttk.Label(title_frame, text="Automated System & Data Protection", 
                                  style='Subtitle.TLabel')
        subtitle_label.pack()
        
        # Separator
        separator = ttk.Separator(parent, orient='horizontal')
        separator.pack(fill=tk.X, pady=(10, 0))
    
    def create_status_panel(self, parent):
        """Create status monitoring panel"""
        # Status card
        status_card = tk.LabelFrame(parent, text=" 📊 System Status ", 
                                   font=('Segoe UI', 11, 'bold'),
                                   bg='white', fg=self.colors['text'],
                                   padx=15, pady=15)
        status_card.pack(fill=tk.X, pady=(0, 15))
        
        # Status indicators with modern design
        status_items = [
            ("Google Drive:", "gdrive_status", "🌐"),
            ("Local Backup:", "local_backup_status", "💾"),
            ("Timeshift:", "timeshift_status", "⏰"),
            ("Last Backup:", "backup_status", "📅")
        ]
        
        for i, (label_text, attr_name, icon) in enumerate(status_items):
            item_frame = tk.Frame(status_card, bg='white')
            item_frame.pack(fill=tk.X, pady=5)
            
            # Icon and label
            icon_label = tk.Label(item_frame, text=icon, bg='white', font=('Segoe UI', 12))
            icon_label.pack(side=tk.LEFT)
            
            text_label = tk.Label(item_frame, text=label_text, bg='white', 
                                font=('Segoe UI', 10), fg=self.colors['text'])
            text_label.pack(side=tk.LEFT, padx=(10, 20))
            
            # Status label
            status_label = ttk.Label(item_frame, text="Checking...", 
                                   style='Status.Warning.TLabel')
            status_label.pack(side=tk.RIGHT)
            setattr(self, attr_name, status_label)
        
        # Progress bar
        progress_frame = tk.Frame(status_card, bg='white')
        progress_frame.pack(fill=tk.X, pady=(15, 0))
        
        tk.Label(progress_frame, text="Operation Progress:", bg='white',
               font=('Segoe UI', 10), fg=self.colors['text']).pack(anchor=tk.W)
        
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate', 
                                      style='TProgressbar')
        self.progress.pack(fill=tk.X, pady=(5, 0))
    
    def create_controls_panel(self, parent):
        """Create control buttons panel"""
        # Controls card
        controls_card = tk.LabelFrame(parent, text=" ⚡ Quick Actions ",
                                    font=('Segoe UI', 11, 'bold'),
                                    bg='white', fg=self.colors['text'],
                                    padx=15, pady=15)
        controls_card.pack(fill=tk.X, pady=(0, 15))
        
        # Primary actions
        primary_frame = tk.Frame(controls_card, bg='white')
        primary_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.backup_btn = tk.Button(primary_frame, text="🔄 Create Backup Now",
                                  command=self.create_backup,
                                  bg=self.colors['success'], fg='white',
                                  font=('Segoe UI', 11, 'bold'),
                                  relief='flat', padx=20, pady=10,
                                  cursor='hand2')
        self.backup_btn.pack(fill=tk.X, pady=2)
        
        # Secondary actions
        secondary_frame = tk.Frame(controls_card, bg='white')
        secondary_frame.pack(fill=tk.X)
        
        buttons = [
            ("🌐 Mount Google Drive", self.mount_gdrive, self.colors['primary']),
            ("📁 Select Local Backup Path", self.select_backup_path, self.colors['warning']),
            ("⚙️ Settings", self.show_settings, self.colors['text_secondary']),
            ("🔄 Refresh Status", self.refresh_status, self.colors['text_secondary'])
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(secondary_frame, text=text, command=command,
                          bg=color, fg='white' if color != self.colors['text_secondary'] else self.colors['text'],
                          font=('Segoe UI', 10),
                          relief='flat', padx=15, pady=8,
                          cursor='hand2')
            btn.pack(fill=tk.X, pady=2)
    
    def create_log_panel(self, parent):
        """Create activity log panel"""
        # Log card
        log_card = tk.LabelFrame(parent, text=" 📝 Activity Log ",
                               font=('Segoe UI', 11, 'bold'),
                               bg='white', fg=self.colors['text'],
                               padx=15, pady=15)
        log_card.pack(fill=tk.BOTH, expand=True)
        
        # Log controls
        log_controls = tk.Frame(log_card, bg='white')
        log_controls.pack(fill=tk.X, pady=(0, 10))
        
        # Auto-scroll checkbox
        self.auto_scroll_var = tk.BooleanVar(value=True)
        auto_scroll_cb = tk.Checkbutton(log_controls, text="Auto-scroll", 
                                      variable=self.auto_scroll_var,
                                      bg='white', fg=self.colors['text'],
                                      font=('Segoe UI', 9))
        auto_scroll_cb.pack(side=tk.LEFT)
        
        # Clear log button
        clear_btn = tk.Button(log_controls, text="🗑️ Clear", 
                            command=self.clear_log,
                            bg='white', fg=self.colors['text'],
                            font=('Segoe UI', 9),
                            relief='flat', padx=10, pady=5,
                            cursor='hand2')
        clear_btn.pack(side=tk.RIGHT)
        
        # Log text area with modern styling
        log_frame = tk.Frame(log_card, bg='white')
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=20,
            font=('Consolas', 9),
            bg='#F8F9FA',
            fg=self.colors['text'],
            selectbackground=self.colors['primary'],
            selectforeground='white',
            wrap=tk.WORD,
            relief='flat',
            borderwidth=1
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure log text tags for colored output
        self.log_text.tag_configure('INFO', foreground=self.colors['primary'])
        self.log_text.tag_configure('WARN', foreground=self.colors['warning'])
        self.log_text.tag_configure('ERROR', foreground=self.colors['error'])
        self.log_text.tag_configure('SUCCESS', foreground=self.colors['success'])
    
    def select_backup_path(self):
        """Allow user to select local backup path"""
        current_path = self.config.get('local_backup_path', '/home/desmond/Local_Backups')
        new_path = filedialog.askdirectory(
            title="Select Local Backup Directory (Max 4GB)",
            initialdir=current_path
        )
        
        if new_path:
            # Check available space
            import shutil
            total, used, free = shutil.disk_usage(new_path)
            free_gb = free // (1024**3)
            
            if free_gb < 5:
                messagebox.showwarning("Low Disk Space", 
                    f"Warning: Only {free_gb}GB free space available.\nBackups may fail if disk becomes full.")
            
            self.config['local_backup_path'] = new_path
            self.save_config()
            self.log_message('INFO', f"📁 Local backup path updated: {new_path}")
            self.log_message('INFO', f"💾 Available space: {free_gb}GB")
            messagebox.showinfo("Backup Path Updated", 
                              f"Local backup directory set to:\n{new_path}\n\nAvailable space: {free_gb}GB")
    
    def log_message(self, level, message):
        """Add styled message to log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Insert with appropriate tag
        self.log_text.insert(tk.END, f"[{timestamp}] [{level}] {message}\n", level)
        
        # Auto-scroll if enabled
        if self.auto_scroll_var.get():
            self.log_text.see(tk.END)
        
        self.log_text.update()
        
        # Also update status if it's a status message
        if "Google Drive" in message:
            if "mounted" in message.lower() or "connected" in message.lower():
                self.gdrive_status.config(text="Connected", style='Status.Success.TLabel')
            else:
                self.gdrive_status.config(text="Disconnected", style='Status.Error.TLabel')
    
    def clear_log(self):
        """Clear the log display"""
        self.log_text.delete(1.0, tk.END)
        self.log_message('INFO', "📝 Log cleared")
    
    def run_command(self, command, show_progress=True):
        """Run a command and return the result"""
        try:
            if show_progress:
                self.progress.start()
            
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=300
            )
            
            if show_progress:
                self.progress.stop()
            
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            if show_progress:
                self.progress.stop()
            return False, "", "Command timed out"
        except Exception as e:
            if show_progress:
                self.progress.stop()
            return False, "", str(e)
    
    def create_backup(self):
        """Create a backup using the enhanced shell script"""
        def backup_thread():
            self.log_message('INFO', "🔄 Starting comprehensive backup process...")
            self.backup_btn.config(state='disabled')
            
            success, stdout, stderr = self.run_command(f"bash {self.script_path}")
            
            if success:
                self.log_message('SUCCESS', "✅ Backup completed successfully!")
                self.backup_status.config(text=f"Completed at {datetime.now().strftime('%H:%M:%S')}", 
                                        style='Status.Success.TLabel')
            else:
                self.log_message('ERROR', f"❌ Backup failed: {stderr}")
                self.backup_status.config(text="Failed", style='Status.Error.TLabel')
            
            if stdout:
                for line in stdout.split('\n'):
                    if line.strip():
                        if '[INFO]' in line:
                            self.log_message('INFO', line)
                        elif '[WARN]' in line:
                            self.log_message('WARN', line)
                        elif '[ERROR]' in line:
                            self.log_message('ERROR', line)
                        else:
                            self.log_message('INFO', line)
            
            self.backup_btn.config(state='normal')
            self.refresh_status()
        
        threading.Thread(target=backup_thread, daemon=True).start()
    
    def mount_gdrive(self):
        """Mount Google Drive with enhanced error handling"""
        def mount_thread():
            self.log_message('INFO', "🌐 Attempting to mount Google Drive...")
            self.gdrive_status.config(text="Connecting...", style='Status.Warning.TLabel')
            
            # First check if google-drive-ocamlfuse is available
            check_success, _, _ = self.run_command("which google-drive-ocamlfuse")
            if not check_success:
                self.log_message('ERROR', "❌ Google Drive FUSE not installed")
                self.log_message('INFO', "💡 Installing Google Drive FUSE...")
                install_success, _, _ = self.run_command("echo '5566' | sudo -S apt update && echo '5566' | sudo -S apt install -y google-drive-ocamlfuse")
                if not install_success:
                    self.gdrive_status.config(text="Install Failed", style='Status.Error.TLabel')
                    return
            
            # Test authentication first
            success, stdout, stderr = self.run_command(f"bash {self.script_path} test-gdrive")
            
            if not success:
                self.log_message('WARN', "⚠️  Google Drive authentication required")
                self.log_message('INFO', "🔐 Setting up authentication...")
                
                # Try to set up authentication
                auth_success, _, _ = self.run_command(
                    "google-drive-ocamlfuse -label uxzheavenlyyei@gmail.com"
                )
                if auth_success:
                    self.log_message('SUCCESS', "✅ Google Drive authentication initiated")
                else:
                    self.log_message('ERROR', "❌ Google Drive authentication failed")
                    self.gdrive_status.config(text="Auth Failed", style='Status.Error.TLabel')
                    return
            
            # Now try to mount
            mount_success, mount_out, mount_err = self.run_command(
                f"bash {self.script_path} mount-gdrive"
            )
            
            if mount_success and "Google Drive mounted" in mount_out:
                self.log_message('SUCCESS', "✅ Google Drive mounted successfully!")
                self.gdrive_status.config(text="Connected", style='Status.Success.TLabel')
            else:
                self.log_message('ERROR', f"❌ Google Drive mount failed: {mount_err}")
                self.gdrive_status.config(text="Disconnected", style='Status.Error.TLabel')
            
            self.refresh_status()
        
        threading.Thread(target=mount_thread, daemon=True).start()
    
    def refresh_status(self):
        """Refresh all status indicators"""
        def status_thread():
            # Check Google Drive mount
            success, _, _ = self.run_command("mountpoint -q /home/desmond/GoogleDrive", show_progress=False)
            if success:
                self.gdrive_status.config(text="Connected", style='Status.Success.TLabel')
            else:
                self.gdrive_status.config(text="Disconnected", style='Status.Error.TLabel')
            
            # Check local backup
            local_backup_path = self.config.get('local_backup_path', '/home/desmond/Local_Backups')
            if os.path.exists(f"{local_backup_path}/latest_backup.txt"):
                try:
                    with open(f"{local_backup_path}/latest_backup.txt", 'r') as f:
                        latest_path = f.read().strip()
                        if os.path.exists(latest_path):
                            backup_time = datetime.fromtimestamp(os.path.getmtime(latest_path))
                            self.local_backup_status.config(text=backup_time.strftime("%m-%d %H:%M"), 
                                                           style='Status.Success.TLabel')
                        else:
                            self.local_backup_status.config(text="Not Found", style='Status.Error.TLabel')
                except:
                    self.local_backup_status.config(text="Error", style='Status.Error.TLabel')
            else:
                self.local_backup_status.config(text="None", style='Status.Warning.TLabel')
            
            # Check Timeshift
            timeshift_success, _, _ = self.run_command("sudo -n timeshift --list >/dev/null 2>&1", show_progress=False)
            if timeshift_success:
                if os.path.exists("/home/desmond/Timeshift_Snapshots/latest_snapshot.txt"):
                    self.timeshift_status.config(text="Available", style='Status.Success.TLabel')
                else:
                    self.timeshift_status.config(text="No Snapshots", style='Status.Warning.TLabel')
            else:
                self.timeshift_status.config(text="Not Available", style='Status.Error.TLabel')
        
        threading.Thread(target=status_thread, daemon=True).start()
    
    def auto_refresh_status(self):
        """Auto-refresh status at regular intervals"""
        self.refresh_status()
        interval = self.config.get('refresh_interval', 30) * 1000
        self.root.after(interval, self.auto_refresh_status)
    
    def show_settings(self):
        """Show enhanced settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Backup Manager Settings")
        settings_window.geometry("550x500")
        settings_window.resizable(False, False)
        settings_window.configure(bg='white')
        
        # Make modal
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        main_frame = tk.Frame(settings_window, bg='white', padx=30, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="⚙️ Settings", 
                             font=('Segoe UI', 16, 'bold'),
                             bg='white', fg=self.colors['text'])
        title_label.pack(pady=(0, 20))
        
        # Local backup path
        path_frame = tk.LabelFrame(main_frame, text=" 📁 Local Backup Configuration ", 
                                  font=('Segoe UI', 11, 'bold'),
                                  bg='white', fg=self.colors['text'], padx=15, pady=15)
        path_frame.pack(fill=tk.X, pady=(0, 15))
        
        current_path = self.config.get('local_backup_path', '/home/desmond/Local_Backups')
        path_var = tk.StringVar(value=current_path)
        
        tk.Label(path_frame, text="Backup directory:", bg='white',
               fg=self.colors['text'], font=('Segoe UI', 10)).pack(anchor=tk.W)
        
        path_display_frame = tk.Frame(path_frame, bg='white')
        path_display_frame.pack(fill=tk.X, pady=(5, 10))
        
        path_entry = tk.Entry(path_display_frame, textvariable=path_var, 
                            font=('Segoe UI', 9), state='readonly')
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        def browse_path():
            new_path = filedialog.askdirectory(initialdir=path_var.get())
            if new_path:
                path_var.set(new_path)
        
        browse_btn = tk.Button(path_display_frame, text="📁 Browse", command=browse_path,
                             bg=self.colors['primary'], fg='white',
                             font=('Segoe UI', 9), relief='flat',
                             padx=15, pady=5, cursor='hand2')
        browse_btn.pack(side=tk.RIGHT)
        
        # Display current space info
        try:
            import shutil
            total, used, free = shutil.disk_usage(current_path)
            free_gb = free // (1024**3)
            space_info = tk.Label(path_frame, text=f"💾 Available space: {free_gb} GB", 
                                bg='white', fg=self.colors['text_secondary'],
                                font=('Segoe UI', 9))
            space_info.pack(anchor=tk.W)
        except:
            pass
        
        # Settings sections
        settings_frame = tk.LabelFrame(main_frame, text=" ⚙️ General Settings ",
                                     font=('Segoe UI', 11, 'bold'),
                                     bg='white', fg=self.colors['text'], padx=15, pady=15)
        settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        variables = {}
        
        # Auto-start option
        auto_start_var = tk.BooleanVar(value=self.config.get("auto_start", True))
        cb1 = tk.Checkbutton(settings_frame, text="Auto-start backup on launch", variable=auto_start_var,
                           bg='white', fg=self.colors['text'], font=('Segoe UI', 10))
        cb1.pack(anchor=tk.W, pady=5)
        variables["auto_start"] = auto_start_var
        
        # Max backup size
        size_frame = tk.Frame(settings_frame, bg='white')
        size_frame.pack(fill=tk.X, pady=5)
        tk.Label(size_frame, text="Maximum backup size (GB):", bg='white',
               fg=self.colors['text'], font=('Segoe UI', 10)).pack(anchor=tk.W)
        max_size_var = tk.IntVar(value=self.config.get("max_backup_size_gb", 4))
        size_spinbox = tk.Spinbox(size_frame, from_=1, to=50, textvariable=max_size_var,
                               width=10, font=('Segoe UI', 10))
        size_spinbox.pack(anchor=tk.W, pady=(5, 0))
        variables["max_backup_size_gb"] = max_size_var
        
        # Max snapshots
        snapshots_frame = tk.Frame(settings_frame, bg='white')
        snapshots_frame.pack(fill=tk.X, pady=5)
        tk.Label(snapshots_frame, text="Maximum snapshots to keep:", bg='white',
               fg=self.colors['text'], font=('Segoe UI', 10)).pack(anchor=tk.W)
        max_snapshots_var = tk.IntVar(value=self.config.get("max_snapshots", 10))
        snapshots_spinbox = tk.Spinbox(snapshots_frame, from_=1, to=50, textvariable=max_snapshots_var,
                                     width=10, font=('Segoe UI', 10))
        snapshots_spinbox.pack(anchor=tk.W, pady=(5, 0))
        variables["max_snapshots"] = max_snapshots_var
        
        # Refresh interval
        refresh_frame = tk.Frame(settings_frame, bg='white')
        refresh_frame.pack(fill=tk.X, pady=5)
        tk.Label(refresh_frame, text="Status refresh interval (seconds):", bg='white',
               fg=self.colors['text'], font=('Segoe UI', 10)).pack(anchor=tk.W)
        refresh_var = tk.IntVar(value=self.config.get("refresh_interval", 30))
        refresh_spinbox = tk.Spinbox(refresh_frame, from_=5, to=300, textvariable=refresh_var,
                                   width=10, font=('Segoe UI', 10))
        refresh_spinbox.pack(anchor=tk.W, pady=(5, 0))
        variables["refresh_interval"] = refresh_var
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill=tk.X, pady=(30, 0))
        
        def save_settings():
            # Save all settings
            for key, var in variables.items():
                self.config[key] = var.get()
            self.config['local_backup_path'] = path_var.get()
            
            self.save_config()
            settings_window.destroy()
            messagebox.showinfo("Settings Saved", "Settings have been saved successfully!")
        
        def cancel_settings():
            settings_window.destroy()
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=cancel_settings,
                             bg='white', fg=self.colors['text'],
                             font=('Segoe UI', 10), relief='flat',
                             padx=20, pady=8, cursor='hand2')
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        save_btn = tk.Button(button_frame, text="💾 Save Settings", command=save_settings,
                           bg=self.colors['success'], fg='white',
                           font=('Segoe UI', 10, 'bold'), relief='flat',
                           padx=20, pady=8, cursor='hand2')
        save_btn.pack(side=tk.RIGHT)
    
    def start_log_monitoring(self):
        """Monitor log file for changes"""
        self.log_message('INFO', "🚀 Backup Manager Pro started")
        self.log_message('INFO', f"📁 Local backup path: {self.config.get('local_backup_path')}")
        self.log_message('INFO', f"💾 Max backup size: {self.config.get('max_backup_size_gb')}GB")
    
    def run(self):
        """Start the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f'+{x}+{y}')
        
        self.root.mainloop()
    
    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit the Backup Manager?"):
            self.root.destroy()

if __name__ == "__main__":
    app = ModernBackupManagerGUI()
    app.run()
