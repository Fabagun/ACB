import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import subprocess
import winreg
import platform
import json
from pathlib import Path
import threading
import urllib.request
import zipfile
import tempfile
import shutil
import time
import random
import psutil

# Try to import PIL for image handling
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class AzerothCoreBuilder:
    def __init__(self, root):
        self.root = root
        self.root.title("AzerothCore Builder (ACB)")
        self.root.geometry("1200x730")
        self.root.resizable(True, True)
        
        # Set window icon and configure appearance
        self.root.configure(bg='#f0f0f0')
        
        # Determine the application directory (works for both PyInstaller and development)
        self._init_app_directory()
        
        # Set window icon
        try:
            icon_path = self._get_resource_path("icons/ACB.ico")
            print(f"🔍 Looking for window icon at: {icon_path}")
            print(f"🔍 Window icon exists: {os.path.exists(icon_path)}")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
                print(f"✅ Window icon loaded: {icon_path}")
            else:
                print(f"Warning: Icon file not found at {icon_path}")
        except Exception as e:
            print(f"Warning: Could not set window icon: {str(e)}")
        
        # Configure window properties for standard Windows look
        self.root.option_add('*TCombobox*Listbox.selectBackground', '#4a9eff')
        self.root.option_add('*TCombobox*Listbox.selectForeground', 'white')
        
        # Requirements configuration
        self.requirements = {
            "Git": {
                "name": "Git",
                "version_check": "git --version",
                "registry_keys": [
                    r"SOFTWARE\GitForWindows",
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Git_is1"
                ],
                "common_paths": [
                    r"C:\Program Files\Git\bin\git.exe",
                    r"C:\Program Files (x86)\Git\bin\git.exe"
                ],
                "download_url": "https://github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/Git-2.44.0-64-bit.exe",
                "install_path": r"C:\Program Files\Git",
                "detected": False,
                "path": "",
                "version": ""
            },
            "Boost": {
                "name": "Boost",
                "version_check": None,
                "registry_keys": [
                    r"SOFTWARE\Boost",
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Boost"
                ],
                "common_paths": [
                    r"C:\local\boost_1_78_0",
                    r"C:\local\boost_1_79_0",
                    r"C:\local\boost_1_80_0",
                    r"C:\local\boost_1_81_0",
                    r"C:\local\boost_1_82_0",
                    r"C:\local\boost_1_83_0",
                    r"C:\local\boost_1_84_0"
                ],
                "download_url": "https://boostorg.jfrog.io/artifactory/main/release/1.85.0/source/boost_1_85_0.zip",
                "install_path": r"C:\local\boost_1_84_0",
                "detected": False,
                "path": "",
                "version": ""
            },
            "MySQL": {
                "name": "MySQL",
                "version_check": "mysql --version",
                "registry_keys": [
                    r"SOFTWARE\MySQL AB",
                    r"SOFTWARE\Oracle\MySQL"
                ],
                "common_paths": [
                    r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe",
                    r"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe",
                    r"C:\Program Files (x86)\MySQL\MySQL Server 8.0\bin\mysql.exe"
                ],
                "download_url": "https://dev.mysql.com/get/Downloads/MySQL-8.4/mysql-8.4.0-winx64.zip",
                "install_path": r"C:\Program Files\MySQL\MySQL Server 8.4",
                "detected": False,
                "path": "",
                "version": ""
            },
            "OpenSSL": {
                "name": "OpenSSL",
                "version_check": "openssl version",
                "registry_keys": [
                    r"SOFTWARE\OpenSSL"
                ],
                "common_paths": [
                    r"C:\Program Files\OpenSSL-Win64\bin\openssl.exe",
                    r"C:\Program Files (x86)\OpenSSL-Win32\bin\openssl.exe"
                ],
                "download_url": "https://slproweb.com/download/Win64OpenSSL-3_5_2.exe",
                "install_path": r"C:\Program Files\OpenSSL-Win64",
                "detected": False,
                "path": "",
                "version": ""
            },
            "CMake": {
                "name": "CMake",
                "version_check": "cmake --version",
                "registry_keys": [
                    r"SOFTWARE\Kitware\CMake"
                ],
                "common_paths": [
                    r"C:\Program Files\CMake\bin\cmake.exe",
                    r"C:\Program Files (x86)\CMake\bin\cmake.exe"
                ],
                "download_url": "https://github.com/Kitware/CMake/releases/download/v3.28.1/cmake-3.28.1-windows-x86_64.zip",
                "install_path": r"C:\Program Files\CMake",
                "detected": False,
                "path": "",
                "version": ""
            },
            "VisualStudio": {
                "name": "Visual Studio 2022",
                "version_check": None,
                "registry_keys": [
                    r"SOFTWARE\Microsoft\VisualStudio\Setup\VS",
                    r"SOFTWARE\WOW6432Node\Microsoft\VisualStudio\Setup\VS"
                ],
                "common_paths": [
                    r"C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\devenv.exe",
                    r"C:\Program Files\Microsoft Visual Studio\2022\Professional\Common7\IDE\devenv.exe",
                    r"C:\Program Files\Microsoft Visual Studio\2022\Enterprise\Common7\IDE\devenv.exe"
                ],
                "download_url": "https://aka.ms/vs/17/release/vs_community.exe",
                "install_path": r"C:\Program Files\Microsoft Visual Studio\2022\Community",
                "detected": False,
                "path": "",
                "version": ""
            },
            "HeidiSQL": {
                "name": "HeidiSQL (Optional)",
                "version_check": None,
                "registry_keys": [
                    r"SOFTWARE\HeidiSQL",
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\HeidiSQL"
                ],
                "common_paths": [
                    r"C:\Program Files\HeidiSQL\heidisql.exe",
                    r"C:\Program Files (x86)\HeidiSQL\heidisql.exe",
                    r"C:\HeidiSQL\heidisql.exe"
                ],
                "download_url": "https://www.heidisql.com/downloads/releases/HeidiSQL_12.11_32_Portable.zip",
                "install_path": r"C:\HeidiSQL",
                "detected": False,
                "path": "",
                "version": ""
            }
        }
        
        # Initialize firewall notification preference
        self.dont_show_firewall_var = tk.BooleanVar(value=False)
        
        # Initialize build process tracking
        self.current_build_process = None
        self.build_cancelled = False
        self.current_cmake_process = None
        self.current_msbuild_process = None
        
        # Initialize logging system first (before any console output)
        self._setup_logging()
        
        self.setup_ui()
        self.load_saved_paths()
        self._load_custom_urls()
        self._check_source_status()
        
        # Test logging system after UI is ready
        self._test_logging_after_ui()
    
    def _init_app_directory(self):
        """Initialize the application directory path that works for both PyInstaller and development"""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable (PyInstaller)
            # Get the directory where the executable is located
            self.app_dir = os.path.dirname(sys.executable)
            print(f"🔧 Running as compiled executable (PyInstaller)")
            print(f"📁 Application directory: {self.app_dir}")
        else:
            # Running as script
            self.app_dir = os.path.dirname(os.path.abspath(__file__))
            print(f"🐍 Running as Python script (development mode)")
            print(f"📁 Application directory: {self.app_dir}")
    
    def _get_app_dir(self):
        """Get the application directory (works for both PyInstaller and development)"""
        return self.app_dir
    
    def _get_resource_path(self, relative_path):
        """Get the correct path for bundled resources (works for both PyInstaller and development)"""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable (PyInstaller)
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = getattr(sys, '_MEIPASS', self.app_dir)
        else:
            # Running as script
            base_path = self.app_dir
        
        return os.path.join(base_path, relative_path)
    
    def _setup_logging(self):
        """Set up logging system with logs folder and file output"""
        try:
            # Get the main app directory (where ACB.py or .exe is located)
            app_dir = self._get_app_dir()
            logs_dir = os.path.join(app_dir, "logs")
            
            # Create logs directory if it doesn't exist
            os.makedirs(logs_dir, exist_ok=True)
            self.logs_dir = logs_dir
            
            # Create log filename with timestamp
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"acb_session_{timestamp}.log"
            self.log_file_path = os.path.join(logs_dir, log_filename)
            
            # Initialize log file
            with open(self.log_file_path, 'w', encoding='utf-8') as f:
                f.write(f"AzerothCore Builder (ACB) Session Log\n")
                f.write(f"Started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Log File: {self.log_file_path}\n")
                f.write("=" * 80 + "\n\n")
            
            # Write initial setup to log file (console not ready yet)
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 📁 Logs directory: {logs_dir}\n")
                f.write(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 📄 Session log file: {log_filename}\n")
            
            # Clean up old log files (use print since console not ready)
            self._cleanup_old_logs()
            
            print(f"📁 Logs directory: {logs_dir}")
            print(f"📄 Session log file: {log_filename}")
            print("✅ Logging system initialized - all console output will be saved to log file")
            
        except Exception as e:
            # If logging setup fails, continue without file logging
            self.log_file_path = None
            self.logs_dir = None
            print(f"Warning: Could not set up file logging: {str(e)}")
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="AzerothCore Builder", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 5))
        
        # Description
        desc_label = ttk.Label(main_frame, 
                              text="A tool to build AzerothCore from source.",
                              font=("Arial", 10), wraplength=900)
        desc_label.grid(row=1, column=0, columnspan=3, pady=(0, 15))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        
        # Requirements tab
        req_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(req_frame, text="Requirements")
        req_frame.columnconfigure(1, weight=1)
        
        # Build tab
        source_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(source_frame, text="Build")
        source_frame.columnconfigure(0, weight=1)  # Repository column
        source_frame.columnconfigure(1, weight=1)  # Status column
        source_frame.columnconfigure(2, weight=1)  # Progress column
        source_frame.columnconfigure(3, weight=1)  # Actions column
        
        
        # Console tab
        console_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(console_frame, text="Console")
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)
        
        # Console text widget
        self.console_text = tk.Text(console_frame, wrap=tk.WORD, height=20, font=("Consolas", 9),
                                   bg='#000000', fg='#ffffff', insertbackground='#ffffff',
                                   selectbackground='#4a9eff', selectforeground='#ffffff',
                                   borderwidth=1, relief='flat')
        self.console_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Console scrollbar
        console_scrollbar = ttk.Scrollbar(console_frame, orient=tk.VERTICAL, command=self.console_text.yview)
        console_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.console_text.configure(yscrollcommand=console_scrollbar.set)
        
        # Console control buttons
        console_buttons_frame = ttk.Frame(console_frame)
        console_buttons_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))
        
        clear_console_button = ttk.Button(console_buttons_frame, text="🧹    Clear Console", 
                                         command=self.clear_console)
        clear_console_button.pack(side=tk.LEFT, padx=(0, 12))
        
        save_log_button = ttk.Button(console_buttons_frame, text="💾        Save Log", 
                                    command=self.save_console_log)
        save_log_button.pack(side=tk.LEFT, padx=(0, 12))
        
        open_logs_button = ttk.Button(console_buttons_frame, text="📁    Open Logs Folder", 
                                     command=self.open_logs_folder)
        open_logs_button.pack(side=tk.LEFT, padx=(0, 12))
        
        delete_logs_button = ttk.Button(console_buttons_frame, text="🗑️    Delete Logs", 
                                       command=self.delete_logs)
        delete_logs_button.pack(side=tk.LEFT, padx=(0, 12))
        
        delete_config_button = ttk.Button(console_buttons_frame, text="🗑️    Delete Config", 
                                         command=self.delete_config)
        delete_config_button.pack(side=tk.LEFT, padx=(0, 12))
        
        delete_repack_button = ttk.Button(console_buttons_frame, text="🗑️    Delete Repack", 
                                         command=self.delete_repack)
        delete_repack_button.pack(side=tk.LEFT, padx=(0, 12))
        
        delete_gitsource_button = ttk.Button(console_buttons_frame, text="🗑️    Delete GitSource", 
                                           command=self.delete_gitsource)
        delete_gitsource_button.pack(side=tk.LEFT, padx=(0, 12))
        
        delete_build_button = ttk.Button(console_buttons_frame, text="🗑️    Delete Build", 
                                        command=self.delete_build)
        delete_build_button.pack(side=tk.LEFT)
        
        # Initialize console
        self.log_to_console("AzerothCore Builder Console initialized")
        self.log_to_console("Ready to monitor operations...")
        
        # Load custom URL configuration
        self._load_custom_url_config()
        
        # Load HeidiSQL URL configuration
        self._load_heidisql_url_config()
        
        # Load data URL configuration
        self._load_data_url_config()
        
        # Apply modern theme
        self._apply_modern_theme()
        
        # Headers
        ttk.Label(req_frame, text="Requirement", style="Header.TLabel").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(req_frame, text="Status", style="Header.TLabel").grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        ttk.Label(req_frame, text="Version/Path", style="Header.TLabel").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        ttk.Label(req_frame, text="Actions", style="Header.TLabel").grid(row=0, column=3, sticky=tk.W)
        
        # Create requirement rows
        self.req_widgets = {}
        for i, (key, req) in enumerate(self.requirements.items(), 1):
            self.create_requirement_row(req_frame, key, req, i)
        
        # Optional section
        optional_row = len(self.requirements) + 1
        ttk.Label(req_frame, text="Optional", style="Header.TLabel").grid(row=optional_row, column=0, sticky=tk.W, padx=(0, 10), pady=(20, 5))
        
        # Set System Variables button
        system_vars_button = ttk.Button(req_frame, text="⚙️ Set System Variables", 
                                       command=self.set_system_variables, width=20)
        system_vars_button.grid(row=optional_row + 1, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 10))
        
        # Actions header
        actions_header = ttk.Label(req_frame, text="Actions", style="Header.TLabel")
        actions_header.grid(row=len(self.requirements) + 3, column=0, columnspan=4, sticky=tk.W, pady=(20, 5))
        
        # Buttons frame - moved inside Requirements section
        button_frame = ttk.Frame(req_frame)
        button_frame.grid(row=len(self.requirements) + 4, column=0, columnspan=4, pady=(0, 0), sticky=(tk.W, tk.E))
        
        # Create source rows
        self.create_source_rows(source_frame)
        
        # Scan button
        self.scan_button = ttk.Button(button_frame, text="🔍 Scan System", 
                                     command=self.scan_system)
        self.scan_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Save button
        self.save_button = ttk.Button(button_frame, text="💾 Save Paths", 
                                     command=self.save_paths)
        self.save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        self.clear_button = ttk.Button(button_frame, text="🗑️ Clear All", 
                                      command=self.clear_all_paths)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Configure URLs button
        self.update_button = ttk.Button(button_frame, text="🔗 Configure URLs", 
                                       command=self.update_download_urls)
        self.update_button.pack(side=tk.LEFT)
        
        # Progress bar - moved inside Requirements section below buttons
        self.progress = ttk.Progressbar(req_frame, mode='determinate', style='Green.Horizontal.TProgressbar')
        self.progress.grid(row=len(self.requirements) + 5, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Status label - moved inside Requirements section below progress bar
        self.status_label = ttk.Label(req_frame, text="Ready to scan system requirements", 
                                     font=("Arial", 9))
        self.status_label.grid(row=len(self.requirements) + 6, column=0, columnspan=4, pady=(5, 0))
        
        # Configure row weights
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Add icon at the bottom middle of the window
        self.add_app_icon(main_frame)
    
    def add_app_icon(self, parent):
        """Add the application icon to the bottom middle of the window"""
        try:
            # Get the path to the icon file
            icon_path = self._get_resource_path("icons/AZC.png")
            
            # Check if icon file exists and PIL is available
            print(f"🔍 Looking for icon at: {icon_path}")
            print(f"🔍 Icon exists: {os.path.exists(icon_path)}")
            print(f"🔍 PIL available: {PIL_AVAILABLE}")
            
            if os.path.exists(icon_path) and PIL_AVAILABLE:
                # Load the image
                image = Image.open(icon_path)
                
                # Get original dimensions
                original_width, original_height = image.size
                
                # Calculate new dimensions maintaining aspect ratio
                max_size = 64
                if original_width > original_height:
                    # Landscape or square
                    new_width = max_size
                    new_height = int((original_height * max_size) / original_width)
                else:
                    # Portrait
                    new_height = max_size
                    new_width = int((original_width * max_size) / original_height)
                
                # Resize maintaining aspect ratio
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                self.app_icon = ImageTk.PhotoImage(image)
                
                # Create label for the icon
                icon_label = ttk.Label(parent, image=self.app_icon)
                icon_label.grid(row=3, column=0, columnspan=3, pady=(10, 0))
                
                self.log_to_console("✅ Application icon loaded successfully")
            else:
                # If icon doesn't exist or PIL not available, create a placeholder
                placeholder_label = ttk.Label(parent, text="AZC", 
                                           font=("Arial", 24, "bold"), 
                                           foreground="#4a9eff")
                placeholder_label.grid(row=3, column=0, columnspan=3, pady=(10, 0))
                
                if not os.path.exists(icon_path):
                    self.log_to_console(f"⚠️ Icon file not found at {icon_path}, using placeholder")
                else:
                    self.log_to_console("⚠️ PIL not available, using text placeholder for icon")
                
        except Exception as e:
            # Fallback to text placeholder
            placeholder_label = ttk.Label(parent, text="AZC", 
                                       font=("Arial", 24, "bold"), 
                                       foreground="#4a9eff")
            placeholder_label.grid(row=3, column=0, columnspan=3, pady=(10, 0))
            
            self.log_to_console(f"⚠️ Could not load icon: {str(e)}, using text placeholder")
        
    def create_requirement_row(self, parent, key, req, row):
        # Requirement name
        name_label = ttk.Label(parent, text=req["name"], font=("Arial", 9))
        name_label.grid(row=row, column=0, sticky=tk.W, padx=(0, 10), pady=2)
        
        # Status indicator
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=row, column=1, sticky=tk.W, padx=(0, 10), pady=2)
        
        status_icon = ttk.Label(status_frame, text="⏳", font=("Arial", 12))
        status_icon.pack(side=tk.LEFT)
        
        status_text = ttk.Label(status_frame, text="Not Checked", font=("Arial", 9))
        status_text.pack(side=tk.LEFT, padx=(5, 0))
        
        # Version/Path display
        version_var = tk.StringVar()
        version_entry = ttk.Entry(parent, textvariable=version_var, state="readonly", width=70)
        version_entry.grid(row=row, column=2, sticky=(tk.W, tk.E), padx=(0, 10), pady=2)
        
        # Actions frame
        actions_frame = ttk.Frame(parent)
        actions_frame.grid(row=row, column=3, sticky=tk.W, pady=2)
        
        path_button = ttk.Button(actions_frame, text="📁        Set Path", 
                                command=lambda: self.set_manual_path(key))
        path_button.pack(side=tk.LEFT, padx=(0, 5))
        
        browse_button = ttk.Button(actions_frame, text="🔍        Browse", 
                                  command=lambda: self.browse_path(key))
        browse_button.pack(side=tk.LEFT, padx=(0, 5))
        
        install_button = ttk.Button(actions_frame, text="⬇️        Install", 
                                   command=lambda: self.install_dependency(key))
        install_button.pack(side=tk.LEFT)
        
        # Store widgets for later access
        self.req_widgets[key] = {
            "status_icon": status_icon,
            "status_text": status_text,
            "version_var": version_var,
            "version_entry": version_entry,
            "path_button": path_button,
            "browse_button": browse_button,
            "install_button": install_button
        }
    
    def create_source_rows(self, parent):
        """Create the source repository rows"""
        # Headers
        ttk.Label(parent, text="Repository", style="Header.TLabel").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(parent, text="Status", style="Header.TLabel").grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        ttk.Label(parent, text="Progress", style="Header.TLabel").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        ttk.Label(parent, text="Source actions", style="Header.TLabel").grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
        ttk.Label(parent, text="Build actions", style="Header.TLabel").grid(row=0, column=4, sticky=tk.W)
        
        # Main source repositories
        self.source_repos = {
            "azerothcore": {
                "name": "AzerothCore Standard",
                "url": "https://github.com/azerothcore/azerothcore-wotlk",
                "folder": "azerothcore-wotlk"
            },
            "npcbots": {
                "name": "AzerothCore with NPCBots",
                "url": "https://github.com/trickerer/AzerothCore-wotlk-with-NPCBots",
                "folder": "azerothcore-wotlk"
            },
            "playerbots": {
                "name": "AzerothCore with PlayerBots",
                "url": "https://github.com/liyunfan1223/azerothcore-wotlk.git",
                "folder": "azerothcore-wotlk"
            },
            "custom": {
                "name": "Custom",
                "url": "",
                "folder": "azerothcore-wotlk"
            }
        }
        
        # Module definitions
        self.modules = {
            "azerothcore_modules": {
                "name": "AzerothCore Modules",
                "urls": [
                    "https://github.com/azerothcore/mod-resurrection-scroll",
                    "https://github.com/azerothcore/mod-progression-system",
                    "https://github.com/azerothcore/mod-zone-difficulty",
                    "https://github.com/azerothcore/mod-transmog",
                    "https://github.com/azerothcore/mod-acore-subscriptions",
                    "https://github.com/azerothcore/mod-global-chat",
                    "https://github.com/azerothcore/mod-server-auto-shutdown",
                    "https://github.com/azerothcore/mod-npc-beastmaster",
                    "https://github.com/azerothcore/mod-autobalance",
                    "https://github.com/azerothcore/mod-war-effort",
                    "https://github.com/azerothcore/mod-instanced-worldbosses",
                    "https://github.com/azerothcore/mod-starter-guild",
                    "https://github.com/azerothcore/mod-morphsummon",
                    "https://github.com/azerothcore/mod-bg-reward",
                    "https://github.com/azerothcore/mod-npc-morph",
                    "https://github.com/azerothcore/mod-bg-item-reward",
                    "https://github.com/azerothcore/mod-ip-tracker",
                    "https://github.com/azerothcore/mod-dmf-switch",
                    "https://github.com/azerothcore/mod-buff-command",
                    "https://github.com/azerothcore/mod-npc-codebox",
                    "https://github.com/azerothcore/mod-chromie-xp",
                    "https://github.com/azerothcore/mod-pvp-zones",
                    "https://github.com/azerothcore/mod-congrats-on-level",
                    "https://github.com/azerothcore/mod-guild-zone-system",
                    "https://github.com/azerothcore/mod-pvp-quests",
                    "https://github.com/azerothcore/mod-cta-switch",
                    "https://github.com/azerothcore/mod-tic-tac-toe",
                    "https://github.com/azerothcore/mod-fireworks-on-level",
                    "https://github.com/azerothcore/mod-notify-muted",
                    "https://github.com/azerothcore/mod-npc-enchanter",
                    "https://github.com/azerothcore/mod-chat-transmitter",
                    "https://github.com/azerothcore/mod-npc-gambler",
                    "https://github.com/azerothcore/mod-weapon-visual",
                    "https://github.com/azerothcore/mod-npc-all-mounts",
                    "https://github.com/azerothcore/mod-racial-trait-swap",
                    "https://github.com/azerothcore/mod-npc-buffer",
                    "https://github.com/azerothcore/mod-aoe-loot",
                    "https://github.com/azerothcore/mod-queue-list-cache",
                    "https://github.com/azerothcore/mod-pvpstats-announcer",
                    "https://github.com/azerothcore/mod-pvp-titles",
                    "https://github.com/azerothcore/mod-rdf-expansion",
                    "https://github.com/azerothcore/mod-costumes",
                    "https://github.com/azerothcore/mod-duel-reset",
                    "https://github.com/azerothcore/mod-desertion-warnings",
                    "https://github.com/azerothcore/mod-low-level-rbg",
                    "https://github.com/azerothcore/mod-low-level-arena",
                    "https://github.com/azerothcore/mod-npc-services",
                    "https://github.com/azerothcore/mod-azerothshard"
                ],
                "folder": "azerothcore-modules"
            },
            "community_modules": {
                "name": "Community Modules",
                "urls": [
                    "https://github.com/azerothcore/mod-weekend-xp",
                    "https://github.com/azerothcore/mod-eluna",
                    "https://github.com/azerothcore/mod-reward-played-time",
                    "https://github.com/azerothcore/mod-phased-duels",
                    "https://github.com/azerothcore/mod-premium",
                    "https://github.com/azerothcore/mod-item-level-up",
                    "https://github.com/azerothcore/mod-pocket-portal",
                    "https://github.com/azerothcore/mod-system-vip",
                    "https://github.com/azerothcore/mod-spell-regulator",
                    "https://github.com/azerothcore/mod-ah-bot",
                    "https://github.com/azerothcore/mod-random-enchants",
                    "https://github.com/azerothcore/mod-npc-talent-template",
                    "https://github.com/azerothcore/mod-keep-out",
                    "https://github.com/azerothcore/mod-who-logged",
                    "https://github.com/azerothcore/mod-solocraft",
                    "https://github.com/azerothcore/mod-account-mounts",
                    "https://github.com/azerothcore/mod-npc-free-professions",
                    "https://github.com/azerothcore/mod-antifarming",
                    "https://github.com/azerothcore/mod-promotion-azerothcore",
                    "https://github.com/azerothcore/mod-arena-replay",
                    "https://github.com/azerothcore/mod-breaking-news-override",
                    "https://github.com/azerothcore/mod-instance-reset",
                    "https://github.com/azerothcore/mod-learn-spells",
                    "https://github.com/azerothcore/mod-dynamic-xp",
                    "https://github.com/azerothcore/mod-custom-login",
                    "https://github.com/azerothcore/mod-npc-titles-tokens",
                    "https://github.com/azerothcore/mod-skip-dk-starting-area",
                    "https://github.com/azerothcore/mod-top-arena",
                    "https://github.com/azerothcore/mod-morph-all-players",
                    "https://github.com/azerothcore/mod-reward-shop",
                    "https://github.com/azerothcore/mod-character-tools",
                    "https://github.com/azerothcore/mod-quick-teleport",
                    "https://github.com/azerothcore/mod-chat-login",
                    "https://github.com/azerothcore/mod-learn-highest-talent",
                    "https://github.com/azerothcore/mod-mall-teleport",
                    "https://github.com/azerothcore/mod-emblem-transfer",
                    "https://github.com/azerothcore/mod-auto-revive",
                    "https://github.com/azerothcore/mod-quest-status",
                    "https://github.com/azerothcore/mod-detailed-logging",
                    "https://github.com/azerothcore/mod-solo-lfg",
                    "https://github.com/azerothcore/mod-boss-announcer",
                    "https://github.com/azerothcore/mod-gain-honor-guard",
                    "https://github.com/azerothcore/mod-pvpscript",
                    "https://github.com/azerothcore/mod-individual-xp",
                    "https://github.com/azerothcore/mod-guildhouse",
                    "https://github.com/azerothcore/mod-multi-client-check",
                    "https://github.com/azerothcore/mod-arena-3v3-solo-queue",
                    "https://github.com/azerothcore/mod-cfbg",
                    "https://github.com/azerothcore/mod-1v1-arena",
                    "https://github.com/azerothcore/mod-world-chat",
                    "https://github.com/azerothcore/mod-account-achievements",
                    "https://github.com/azerothcore/mod-anticheat",
                    "https://github.com/azerothcore/mod-better-item-reloading",
                    "https://github.com/araxiaonline/mod-mythic-plus",
                    "https://github.com/araxiaonline/mod-auctionator",
                    "https://github.com/araxiaonline/mod-money-for-kills",
                    "https://github.com/araxiaonline/mod-worgoblin",
                    "https://github.com/araxiaonline/mod-boss-runeworder",
                    "https://github.com/araxiaonline/mod-sharedrep",
                    "https://github.com/heyitsbench/mod-arac",
                    "https://github.com/heyitsbench/mod-chromiecraft-smartstone",
                    "https://github.com/ZhengPeiRu21/mod-challenge-modes",
                    "https://github.com/ZhengPeiRu21/mod-reagent-bank",
                    "https://github.com/ZhengPeiRu21/mod-leech",
                    "https://github.com/ZhengPeiRu21/mod-bg-set-level",
                    "https://github.com/talamortis/mod-bg-slaveryvalley",
                    "https://github.com/sogladev/mod-vanilla-naxxramas",
                    "https://github.com/sogladev/mod-dbg-tools",
                    "https://github.com/sogladev/mod-dkp-aio",
                    "https://github.com/sogladev/mod-individual-spellqueue",
                    "https://github.com/sogladev/mod-reset-raid-cooldowns",
                    "https://github.com/sogladev/mod-ghost-speed",
                    "https://github.com/sogladev/mod-deathroll-aio",
                    "https://github.com/sogladev/mod-demonic-pact-classic",
                    "https://github.com/stylo019/SkyWall-HardCore-Mode-3.3.5-WoW",
                    "https://github.com/pangolp/mod-recruit-friend",
                    "https://github.com/tbcstar/mod-high-risk-system",
                    "https://github.com/tbcstar/mod-bounty-hunter",
                    "https://github.com/pangolp/mod-guildfunds",
                    "https://github.com/tbcstar/mod-LadyLuck",
                    "https://github.com/tbcstar/mod-npc-spectator",
                    "https://github.com/tbcstar/mod-antifarming",
                    "https://github.com/tbcstar/mod-TimeIsTime",
                    "https://github.com/pangolp/mod-npc-promotion",
                    "https://github.com/noisiver/mod-progression",
                    "https://github.com/noisiver/mod-appreciation",
                    "https://github.com/noisiver/mod-weekendbonus",
                    "https://github.com/noisiver/mod-junk-to-gold",
                    "https://github.com/noisiver/mod-alterac-valley-additions",
                    "https://github.com/noisiver/mod-groupquests",
                    "https://github.com/noisiver/mod-accountbound",
                    "https://github.com/noisiver/mod-assistant",
                    "https://github.com/Nyeriah/mod-black-portal",
                    "https://github.com/Nyeriah/mod-save-inventory",
                    "https://github.com/noisiver/mod-giftvouchers"
                ],
                "folder": "community-modules"
            },
            "npcbot_modules": {
                "name": "NPCBot Modules",
                "urls": [
                    "https://github.com/trickerer/mod-autobalance",
                    "https://github.com/trickerer/Trinity-Bots",
                    "https://github.com/trickerer/mod-solocraft"
                ],
                "folder": "npcbot-modules"
            },
            "playerbot_modules": {
                "name": "PlayerBot Modules",
                "urls": [
                    "https://github.com/liyunfan1223/mod-playerbots",
                    "https://github.com/noisiver/mod-player-bot-level-brackets",
                    "https://github.com/DustinHendrickson/mod-ollama-chat",
                    "https://github.com/DustinHendrickson/mod-player-bot-reset",
                    "https://github.com/DustinHendrickson/mod-player-bot-guildhouse"
                ],
                "folder": "playerbot-modules"
            }
        }
        
        # Create main source repository rows
        self.source_widgets = {}
        for i, (key, repo) in enumerate(self.source_repos.items(), 1):
            self.create_source_row(parent, key, repo, i)
        
        # Add Modules header after main repositories
        modules_header_row = len(self.source_repos) + 1
        ttk.Label(parent, text="Modules", style="Header.TLabel").grid(row=modules_header_row, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 5))
        
        # Create module buttons on the same line
        self.create_module_buttons(parent, modules_header_row + 1)
        
        # Add Build header
        build_header = ttk.Label(parent, text="Build", style="Header.TLabel")
        build_header.grid(row=len(self.source_repos) + 4, column=0, columnspan=5, sticky=tk.W, pady=(10, 5))
        
        # Add refresh button and progress bar for source repositories
        refresh_frame = ttk.Frame(parent)
        refresh_frame.grid(row=len(self.source_repos) + 5, column=0, columnspan=5, pady=(0, 0), sticky=(tk.W, tk.E))
        
        refresh_button = ttk.Button(refresh_frame, text="🔄    Refresh Status", 
                                   command=self._check_source_status)
        refresh_button.pack(side=tk.LEFT)
        
        # Generate extractors checkbox
        self.generate_extractors_var = tk.BooleanVar(value=True)  # Default to True (current behavior)
        generate_extractors_checkbox = ttk.Checkbutton(refresh_frame, 
                                                      text="Generate extractors", 
                                                      variable=self.generate_extractors_var)
        generate_extractors_checkbox.pack(side=tk.LEFT, padx=(20, 0))
        
        # Add spacer to push cancel button to the right
        spacer_frame = ttk.Frame(refresh_frame)
        spacer_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Cancel build button (initially hidden)
        self.cancel_build_button = ttk.Button(refresh_frame, text="❌    Cancel Build", 
                                            command=self._cancel_build_process,
                                            state=tk.DISABLED)
        self.cancel_build_button.pack(side=tk.RIGHT)
        
        # Store the build progress bar reference (will be set to the main progress bar below)
        self.build_progress_bar = None
        
        # Add main progress bar at the bottom of the Build tab (similar to Requirements tab)
        self.build_main_progress = ttk.Progressbar(parent, mode='determinate', style='Green.Horizontal.TProgressbar')
        self.build_main_progress.grid(row=len(self.source_repos) + 6, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Add build status text under the progress bar
        self.build_status_label = ttk.Label(parent, text="Build progress", 
                                          font=("Arial", 9))
        self.build_status_label.grid(row=len(self.source_repos) + 7, column=0, columnspan=5, pady=(5, 0))
        
        # Add Repack section header
        repack_header = ttk.Label(parent, text="Repack", 
                                 style="Header.TLabel")
        repack_header.grid(row=len(self.source_repos) + 8, column=0, columnspan=5, sticky=tk.W, pady=(5, 5))
        
        # Create Repack buttons with 7 buttons per row
        # Row 1: First 7 buttons
        repack_row1_frame = ttk.Frame(parent)
        repack_row1_frame.grid(row=len(self.source_repos) + 9, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=(0, 5))
        repack_row1_frame.columnconfigure(6, weight=1)  # Make last column expandable
        
        create_repack_button = ttk.Button(repack_row1_frame, text="📦        Create Repack", 
                                        command=self.create_repack, width=22)
        create_repack_button.grid(row=0, column=0, padx=(0, 7))
        
        create_configs_button = ttk.Button(repack_row1_frame, text="⚙️        Create configs", 
                                         command=self.create_configs, width=22)
        create_configs_button.grid(row=0, column=1, padx=(0, 7))
        
        config_paths_button = ttk.Button(repack_row1_frame, text="📁        Config paths", 
                                       command=self.config_paths_dialog, width=22)
        config_paths_button.grid(row=0, column=2, padx=(0, 7))
        
        create_dlls_button = ttk.Button(repack_row1_frame, text="📚        Create DLL's", 
                                      command=self.create_dlls, width=22)
        create_dlls_button.grid(row=0, column=3, padx=(0, 7))
        
        create_mysql_button = ttk.Button(repack_row1_frame, text="🗄️        Create MySQL", 
                                       command=self.create_mysql, width=22)
        create_mysql_button.grid(row=0, column=4, padx=(0, 7))
        
        init_mysql_button = ttk.Button(repack_row1_frame, text="🚀    Initialize MySQL", 
                                     command=self.initialize_mysql, width=22)
        init_mysql_button.grid(row=0, column=5, padx=(0, 7))
        
        create_myini_button = ttk.Button(repack_row1_frame, text="📄        Create My.ini", 
                                       command=self.create_myini, width=22)
        create_myini_button.grid(row=0, column=6, sticky=tk.E)
        
        # Row 2: Next 7 buttons
        repack_row2_frame = ttk.Frame(parent)
        repack_row2_frame.grid(row=len(self.source_repos) + 10, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=(0, 5))
        repack_row2_frame.columnconfigure(6, weight=1)  # Make last column expandable
        
        create_mysql_bat_button = ttk.Button(repack_row2_frame, text="📄    Create MySQL.bat", 
                                           command=self.create_mysql_bat, width=22)
        create_mysql_bat_button.grid(row=0, column=0, padx=(0, 7))
        
        start_mysql_button = ttk.Button(repack_row2_frame, text="▶️        Start MySQL", 
                                      command=self.start_mysql, width=22)
        start_mysql_button.grid(row=0, column=1, padx=(0, 7))
        
        config_mysql_button = ttk.Button(repack_row2_frame, text="⚙️        Config MySQL", 
                                       command=self.config_mysql, width=22)
        config_mysql_button.grid(row=0, column=2, padx=(0, 7))
        
        create_database_button = ttk.Button(repack_row2_frame, text="🗃️   Create Database", 
                                          command=self.create_database, width=22)
        create_database_button.grid(row=0, column=3, padx=(0, 7))
        
        config_data_url_button = ttk.Button(repack_row2_frame, text="⚙️   Configure Data URL", 
                                          command=self.config_data_url, width=22)
        config_data_url_button.grid(row=0, column=4, padx=(0, 7))
        
        get_data_button = ttk.Button(repack_row2_frame, text="📥      Download Data", 
                                   command=self.get_data, width=22)
        get_data_button.grid(row=0, column=5, padx=(0, 7))
        
        copy_data_button = ttk.Button(repack_row2_frame, text="📁    Copy/Extract Data", 
                                    command=self.copy_data, width=22)
        copy_data_button.grid(row=0, column=6, sticky=tk.E)
        
        # Row 3: Last 7 buttons
        repack_row3_frame = ttk.Frame(parent)
        repack_row3_frame.grid(row=len(self.source_repos) + 11, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=(0, 5))
        repack_row3_frame.columnconfigure(6, weight=1)  # Make last column expandable
        
        run_module_sql_button = ttk.Button(repack_row3_frame, text="📚        Run module SQL", 
                                         command=self.run_module_sql, width=22)
        run_module_sql_button.grid(row=0, column=0, padx=(0, 7))
        
        create_heidisql_bat_button = ttk.Button(repack_row3_frame, text="📄    Create HeidiSQL.bat", 
                                              command=self.create_heidisql_bat, width=22)
        create_heidisql_bat_button.grid(row=0, column=1, padx=(0, 7))
        
        autoupdater_off_button = ttk.Button(repack_row3_frame, text="⏸️    Autoupdater OFF", 
                                          command=self.set_autoupdater_off, width=22)
        autoupdater_off_button.grid(row=0, column=2, padx=(0, 7))
        
        autoupdater_on_button = ttk.Button(repack_row3_frame, text="▶️    Autoupdater ON", 
                                         command=self.set_autoupdater_on, width=22)
        autoupdater_on_button.grid(row=0, column=3, padx=(0, 7))
        
        wipe_repack_button = ttk.Button(repack_row3_frame, text="🗑️        Wipe Repack", 
                                      command=self.wipe_repack, width=22)
        wipe_repack_button.grid(row=0, column=4, padx=(0, 7))
        
        start_auth_button = ttk.Button(repack_row3_frame, text="▶️        Start Auth", 
                                     command=self.start_auth, width=22)
        start_auth_button.grid(row=0, column=5, padx=(0, 7))
        
        start_world_button = ttk.Button(repack_row3_frame, text="▶️        Start World", 
                                      command=self.start_world, width=22)
        start_world_button.grid(row=0, column=6, sticky=tk.E)
        
        # Set the main progress bar as the build progress bar reference
        self.build_progress_bar = self.build_main_progress
    
    def create_source_row(self, parent, key, repo, row):
        """Create a single source repository row"""
        # Repository name frame (to hold name and URL button for custom)
        name_frame = ttk.Frame(parent)
        name_frame.grid(row=row, column=0, sticky=tk.W, padx=(0, 10), pady=2)
        
        # Repository name
        name_label = ttk.Label(name_frame, text=repo["name"], font=("Arial", 9))
        name_label.pack(side=tk.LEFT)
        
        # Add URL button for custom source
        if key == "custom":
            url_button = ttk.Button(name_frame, text="🔗", width=3,
                                  command=lambda: self.set_custom_url())
            url_button.pack(side=tk.LEFT, padx=(5, 0))
        else:
            url_button = None
        
        # Status indicator
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=row, column=1, sticky=tk.W, padx=(0, 10), pady=2)
        
        status_icon = ttk.Label(status_frame, text="⏳", font=("Arial", 12))
        status_icon.pack(side=tk.LEFT)
        
        status_text = ttk.Label(status_frame, text="Not Cloned", font=("Arial", 9))
        status_text.pack(side=tk.LEFT, padx=(5, 0))
        
        # Progress bar frame - centered with buttons
        progress_frame = ttk.Frame(parent)
        progress_frame.grid(row=row, column=2, sticky=(tk.W, tk.E), padx=(0, 10), pady=2)
        progress_frame.columnconfigure(0, weight=1)
        
        # Progress bar - shows visual progress during cloning (shorter for 4 buttons)
        progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=120, style='Green.Horizontal.TProgressbar')
        progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Source actions frame
        source_actions_frame = ttk.Frame(parent)
        source_actions_frame.grid(row=row, column=3, sticky=tk.W, pady=2)
        
        clone_button = ttk.Button(source_actions_frame, text="📥        Clone", 
                                 command=lambda: self.clone_repository(key))
        clone_button.pack(side=tk.LEFT, padx=(0, 5))
        
        clean_button = ttk.Button(source_actions_frame, text="🧹        Clean", 
                                 command=lambda: self.clean_repository(key))
        clean_button.pack(side=tk.LEFT, padx=(0, 5))
        
        update_button = ttk.Button(source_actions_frame, text="🔄        Update", 
                                 command=lambda: self.update_repository(key),
                                 state="disabled")
        update_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Build actions frame
        build_actions_frame = ttk.Frame(parent)
        build_actions_frame.grid(row=row, column=4, sticky=tk.W, pady=2)
        
        build_button = ttk.Button(build_actions_frame, text="🔨        Build", 
                                 command=lambda: self.build_repository(key))
        build_button.pack(side=tk.LEFT, padx=(0, 5))
        
        nuke_button = ttk.Button(build_actions_frame, text="💥        Nuke", 
                                command=lambda: self.nuke_build_folder())
        nuke_button.pack(side=tk.LEFT)
        
        # Store widgets for later access
        self.source_widgets[key] = {
            "status_icon": status_icon,
            "status_text": status_text,
            "progress_bar": progress_bar,
            "clone_button": clone_button,
            "clean_button": clean_button,
            "update_button": update_button,
            "build_button": build_button,
            "nuke_button": nuke_button,
            "url_button": url_button
        }
    
    def create_module_buttons(self, parent, row):
        """Create module buttons on a single line"""
        # Create a frame for the module buttons
        module_frame = ttk.Frame(parent)
        module_frame.grid(row=row, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=5)
        
        # Create buttons for each module
        for i, (key, module) in enumerate(self.modules.items()):
            module_button = ttk.Button(module_frame, text=module["name"], 
                                     command=lambda k=key: self.handle_module_click(k))
            module_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Add Clean Modules button
        clean_modules_button = ttk.Button(module_frame, text="🧹    Clean Modules", 
                                        command=self.clean_all_modules)
        clean_modules_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # Store module buttons for later access
        self.module_widgets = {}
        for key, module in self.modules.items():
            self.module_widgets[key] = {
                "button": module_button
            }
    
    def handle_module_click(self, key):
        """Handle module button clicks"""
        module = self.modules[key]
        self.log_to_console(f"🔘 Module button clicked: {module['name']}")
        
        if key == "azerothcore_modules":
            self.show_azerothcore_modules_window()
        elif key == "community_modules":
            self.show_community_modules_window()
        elif key == "npcbot_modules":
            self.show_npcbot_modules_window()
        elif key == "playerbot_modules":
            self.show_playerbot_modules_window()
        else:
            # Fallback for any other module types
            messagebox.showinfo("Module Clicked", f"You clicked on {module['name']}\n\nFunctionality to be implemented.")
    
    def show_azerothcore_modules_window(self):
        """Show window with all available AzerothCore modules"""
        self.log_to_console("🔍 Opening AzerothCore modules selection window")
        
        # Create the modules window
        modules_window = tk.Toplevel(self.root)
        modules_window.title("AzerothCore Modules")
        modules_window.geometry("1000x700")
        modules_window.transient(self.root)
        modules_window.grab_set()
        
        # Center the window
        modules_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))
        
        # Main frame
        main_frame = ttk.Frame(modules_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Available AzerothCore Modules", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Description
        desc_label = ttk.Label(main_frame, text="Select the modules you want to clone:", font=("Arial", 9))
        desc_label.pack(pady=(0, 10))
        
        # Load modules directly
        self.load_azerothcore_modules(main_frame, modules_window)
    
    def load_azerothcore_modules(self, parent_frame, window):
        """Load comprehensive hardcoded list of AzerothCore modules"""
        self.log_to_console("📋 Loading comprehensive AzerothCore modules list...")
        
        # Show loading message
        loading_label = ttk.Label(parent_frame, text="Loading modules list...", font=("Arial", 10))
        loading_label.pack(pady=20)
        
        # Get modules from configuration
        module_urls = self.modules["azerothcore_modules"]["urls"]
        
        # Convert URLs to module objects
        modules = []
        for url in module_urls:
            # Extract module name from URL
            module_name = url.split('/')[-1]
            full_name = url.replace('https://github.com/', '')
            
            modules.append({
                'name': module_name,
                'full_name': full_name,
                'description': f'{module_name} - AzerothCore module',
                'url': url,
                'topics': ['azerothcore-module']
            })
        
        # Combine with any additional modules if needed
        # modules.extend(additional_modules)
        
        # Legacy hardcoded modules (keeping for backward compatibility)
        legacy_modules = [
            {
                'name': 'mod-eluna',
                'full_name': 'azerothcore/mod-eluna',
                'description': 'Eluna Lua Engine for AzerothCore - Scripting engine',
                'url': 'https://github.com/azerothcore/mod-eluna.git',
                'topics': ['azerothcore-module', 'lua', 'scripting']
            },
            {
                'name': 'mod-transmog',
                'full_name': 'azerothcore/mod-transmog',
                'description': 'Transmogrification module for AzerothCore',
                'url': 'https://github.com/azerothcore/mod-transmog.git',
                'topics': ['azerothcore-module', 'transmog']
            },
            {
                'name': 'mod-ah-bot',
                'full_name': 'azerothcore/mod-ah-bot',
                'description': 'Auction House Bot for AzerothCore',
                'url': 'https://github.com/azerothcore/mod-ah-bot.git',
                'topics': ['azerothcore-module', 'auction-house']
            },
            {
                'name': 'mod-premium',
                'full_name': 'azerothcore/mod-premium',
                'description': 'Premium account features for AzerothCore',
                'url': 'https://github.com/azerothcore/mod-premium.git',
                'topics': ['azerothcore-module', 'premium']
            },
            {
                'name': 'mod-progression-system',
                'full_name': 'azerothcore/mod-progression-system',
                'description': 'Progression system for AzerothCore',
                'url': 'https://github.com/azerothcore/mod-progression-system.git',
                'topics': ['azerothcore-module', 'progression']
            },
            {
                'name': 'mod-random-enchants',
                'full_name': 'azerothcore/mod-random-enchants',
                'description': 'Random enchantments for items',
                'url': 'https://github.com/azerothcore/mod-random-enchants.git',
                'topics': ['azerothcore-module', 'enchants']
            },
            {
                'name': 'mod-npc-talent-template',
                'full_name': 'azerothcore/mod-npc-talent-template',
                'description': 'Template NPC with gear and talents',
                'url': 'https://github.com/azerothcore/mod-npc-talent-template.git',
                'topics': ['azerothcore-module', 'npc']
            },
            {
                'name': 'mod-weekend-xp',
                'full_name': 'azerothcore/mod-weekend-xp',
                'description': 'Weekend XP bonus module',
                'url': 'https://github.com/azerothcore/mod-weekend-xp.git',
                'topics': ['azerothcore-module', 'xp']
            },
            {
                'name': 'mod-zone-difficulty',
                'full_name': 'azerothcore/mod-zone-difficulty',
                'description': 'Zone difficulty adjustments',
                'url': 'https://github.com/azerothcore/mod-zone-difficulty.git',
                'topics': ['azerothcore-module', 'difficulty']
            },
            {
                'name': 'mod-spell-regulator',
                'full_name': 'azerothcore/mod-spell-regulator',
                'description': 'Spell regulation and balancing',
                'url': 'https://github.com/azerothcore/mod-spell-regulator.git',
                'topics': ['azerothcore-module', 'spells']
            },
            {
                'name': 'mod-keep-out',
                'full_name': 'azerothcore/mod-keep-out',
                'description': 'Keep players out of restricted zones',
                'url': 'https://github.com/azerothcore/mod-keep-out.git',
                'topics': ['azerothcore-module', 'zones']
            },
            {
                'name': 'mod-server-auto-shutdown',
                'full_name': 'azerothcore/mod-server-auto-shutdown',
                'description': 'Automatic server shutdown functionality',
                'url': 'https://github.com/azerothcore/mod-server-auto-shutdown.git',
                'topics': ['azerothcore-module', 'server']
            },
            {
                'name': 'mod-global-chat',
                'full_name': 'azerothcore/mod-global-chat',
                'description': 'Global chat system for AzerothCore',
                'url': 'https://github.com/azerothcore/mod-global-chat.git',
                'topics': ['azerothcore-module', 'chat']
            },
            {
                'name': 'mod-phased-duels',
                'full_name': 'azerothcore/mod-phased-duels',
                'description': 'Phased duels system',
                'url': 'https://github.com/azerothcore/mod-phased-duels.git',
                'topics': ['azerothcore-module', 'duels']
            },
            {
                'name': 'mod-resurrection-scroll',
                'full_name': 'azerothcore/mod-resurrection-scroll',
                'description': 'Resurrection scroll functionality',
                'url': 'https://github.com/azerothcore/mod-resurrection-scroll.git',
                'topics': ['azerothcore-module', 'resurrection']
            },
            {
                'name': 'mod-item-level-up',
                'full_name': 'azerothcore/mod-item-level-up',
                'description': 'Item level up system',
                'url': 'https://github.com/azerothcore/mod-item-level-up.git',
                'topics': ['azerothcore-module', 'items']
            },
            {
                'name': 'mod-pocket-portal',
                'full_name': 'azerothcore/mod-pocket-portal',
                'description': 'Pocket portal script',
                'url': 'https://github.com/azerothcore/mod-pocket-portal.git',
                'topics': ['azerothcore-module', 'portals']
            },
            {
                'name': 'mod-system-vip',
                'full_name': 'azerothcore/mod-system-vip',
                'description': 'VIP system for AzerothCore',
                'url': 'https://github.com/azerothcore/mod-system-vip.git',
                'topics': ['azerothcore-module', 'vip']
            },
            {
                'name': 'mod-acore-subscriptions',
                'full_name': 'azerothcore/mod-acore-subscriptions',
                'description': 'ACore CMS subscriptions module',
                'url': 'https://github.com/azerothcore/mod-acore-subscriptions.git',
                'topics': ['azerothcore-module', 'subscriptions']
            },
            {
                'name': 'mod-arena-stats',
                'full_name': 'azerothcore/arena-stats',
                'description': 'Arena statistics for AzerothCore',
                'url': 'https://github.com/azerothcore/arena-stats.git',
                'topics': ['azerothcore-module', 'arena']
            },
            {
                'name': 'mod-keira3',
                'full_name': 'azerothcore/keira3',
                'description': 'Official Database Editor for AzerothCore',
                'url': 'https://github.com/azerothcore/keira3.git',
                'topics': ['azerothcore-tools', 'database']
            },
            {
                'name': 'mod-acore-cms',
                'full_name': 'azerothcore/acore-cms',
                'description': 'ACore CMS based on WordPress',
                'url': 'https://github.com/azerothcore/acore-cms.git',
                'topics': ['azerothcore-tools', 'cms']
            },
            {
                'name': 'mod-wiki',
                'full_name': 'azerothcore/wiki',
                'description': 'Wiki for AzerothCore',
                'url': 'https://github.com/azerothcore/wiki.git',
                'topics': ['documentation', 'wiki']
            },
            {
                'name': 'mod-server-status',
                'full_name': 'azerothcore/server-status',
                'description': 'AzerothCore Server status',
                'url': 'https://github.com/azerothcore/server-status.git',
                'topics': ['azerothcore-tools', 'status']
            },
            {
                'name': 'mod-acore-reactive-cms',
                'full_name': 'azerothcore/acore-reactive-cms',
                'description': 'ReactJS CMS for ACore',
                'url': 'https://github.com/azerothcore/acore-reactive-cms.git',
                'topics': ['azerothcore-tools', 'react']
            },
            {
                'name': 'mod-acore-reactive-cms-template',
                'full_name': 'azerothcore/acore-reactive-cms-template',
                'description': 'Template for ACore Reactive CMS',
                'url': 'https://github.com/azerothcore/acore-reactive-cms-template.git',
                'topics': ['azerothcore-tools', 'template']
            },
            {
                'name': 'mod-doxygen',
                'full_name': 'azerothcore/doxygen',
                'description': 'Doxygen for AzerothCore',
                'url': 'https://github.com/azerothcore/doxygen.git',
                'topics': ['documentation', 'doxygen']
            },
            {
                'name': 'mod-acore-cms-wp-plugin',
                'full_name': 'azerothcore/acore-cms-wp-plugin',
                'description': 'ACore CMS WordPress Plugin',
                'url': 'https://github.com/azerothcore/acore-cms-wp-plugin.git',
                'topics': ['azerothcore-tools', 'wordpress']
            },
            {
                'name': 'mod-bash-lib',
                'full_name': 'azerothcore/bash-lib',
                'description': 'Bash scripts for git used by AzerothCore projects',
                'url': 'https://github.com/azerothcore/bash-lib.git',
                'topics': ['tools', 'bash']
            }
        ]
        
        self.log_to_console(f"✅ Loaded {len(modules)} comprehensive modules list")
        
        # Update UI on main thread
        self.root.after(0, lambda: self.display_modules(parent_frame, window, modules, loading_label))
    
    def show_community_modules_window(self):
        """Show window with all available Community modules"""
        self.log_to_console("🔍 Opening Community modules selection window")
        
        # Create the modules window
        modules_window = tk.Toplevel(self.root)
        modules_window.title("Community Modules")
        modules_window.geometry("1000x700")
        modules_window.transient(self.root)
        modules_window.grab_set()
        
        # Center the window
        modules_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))
        
        # Main frame
        main_frame = ttk.Frame(modules_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Available Community Modules", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Description
        desc_label = ttk.Label(main_frame, text="Select the modules you want to clone:", font=("Arial", 9))
        desc_label.pack(pady=(0, 10))
        
        # Load modules directly
        self.load_community_modules(main_frame, modules_window)
    
    def load_community_modules(self, parent_frame, window):
        """Load comprehensive hardcoded list of Community modules"""
        self.log_to_console("📋 Loading comprehensive Community modules list...")
        
        # Show loading message
        loading_label = ttk.Label(parent_frame, text="Loading modules list...", font=("Arial", 10))
        loading_label.pack(pady=20)
        
        # Get modules from configuration
        module_urls = self.modules["community_modules"]["urls"]
        
        # Convert URLs to module objects
        modules = []
        for url in module_urls:
            # Extract module name from URL
            module_name = url.split('/')[-1]
            full_name = url.replace('https://github.com/', '')
            
            modules.append({
                'name': module_name,
                'full_name': full_name,
                'description': f'{module_name} - Community module',
                'url': url,
                'topics': ['community-module']
            })
        
        self.log_to_console(f"✅ Loaded {len(modules)} community modules list")
        
        # Update UI on main thread
        self.root.after(0, lambda: self.display_modules(parent_frame, window, modules, loading_label))
    
    def show_npcbot_modules_window(self):
        """Show window with all available NPCBot modules"""
        self.log_to_console("🔍 Opening NPCBot modules selection window")
        
        # Create the modules window
        modules_window = tk.Toplevel(self.root)
        modules_window.title("NPCBot Modules")
        modules_window.geometry("1000x700")
        modules_window.transient(self.root)
        modules_window.grab_set()
        
        # Center the window
        modules_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))
        
        # Main frame
        main_frame = ttk.Frame(modules_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Available NPCBot Modules", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Description
        desc_label = ttk.Label(main_frame, text="Select the modules you want to clone:", font=("Arial", 9))
        desc_label.pack(pady=(0, 10))
        
        # Load modules directly
        self.load_npcbot_modules(main_frame, modules_window)
    
    def load_npcbot_modules(self, parent_frame, window):
        """Load comprehensive hardcoded list of NPCBot modules"""
        self.log_to_console("📋 Loading comprehensive NPCBot modules list...")
        
        # Show loading message
        loading_label = ttk.Label(parent_frame, text="Loading modules list...", font=("Arial", 10))
        loading_label.pack(pady=20)
        
        # Get modules from configuration
        module_urls = self.modules["npcbot_modules"]["urls"]
        
        # Convert URLs to module objects
        modules = []
        for url in module_urls:
            # Extract module name from URL
            module_name = url.split('/')[-1]
            full_name = url.replace('https://github.com/', '')
            
            modules.append({
                'name': module_name,
                'full_name': full_name,
                'description': f'{module_name} - NPCBot module',
                'url': url,
                'topics': ['npcbot-module']
            })
        
        self.log_to_console(f"✅ Loaded {len(modules)} NPCBot modules list")
        
        # Update UI on main thread
        self.root.after(0, lambda: self.display_modules(parent_frame, window, modules, loading_label))
    
    def show_playerbot_modules_window(self):
        """Show window with all available PlayerBot modules"""
        self.log_to_console("🔍 Opening PlayerBot modules selection window")
        
        # Create the modules window
        modules_window = tk.Toplevel(self.root)
        modules_window.title("PlayerBot Modules")
        modules_window.geometry("1000x700")
        modules_window.transient(self.root)
        modules_window.grab_set()
        
        # Center the window
        modules_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))
        
        # Main frame
        main_frame = ttk.Frame(modules_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Available PlayerBot Modules", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Description
        desc_label = ttk.Label(main_frame, text="Select the modules you want to clone:", font=("Arial", 9))
        desc_label.pack(pady=(0, 10))
        
        # Load modules directly
        self.load_playerbot_modules(main_frame, modules_window)
    
    def load_playerbot_modules(self, parent_frame, window):
        """Load comprehensive hardcoded list of PlayerBot modules"""
        self.log_to_console("📋 Loading comprehensive PlayerBot modules list...")
        
        # Show loading message
        loading_label = ttk.Label(parent_frame, text="Loading modules list...", font=("Arial", 10))
        loading_label.pack(pady=20)
        
        # Get modules from configuration
        module_urls = self.modules["playerbot_modules"]["urls"]
        
        # Convert URLs to module objects
        modules = []
        for url in module_urls:
            # Extract module name from URL
            module_name = url.split('/')[-1]
            full_name = url.replace('https://github.com/', '')
            
            modules.append({
                'name': module_name,
                'full_name': full_name,
                'description': f'{module_name} - PlayerBot module',
                'url': url,
                'topics': ['playerbot-module']
            })
        
        self.log_to_console(f"✅ Loaded {len(modules)} PlayerBot modules list")
        
        # Update UI on main thread
        self.root.after(0, lambda: self.display_modules(parent_frame, window, modules, loading_label))
    
    def edit_module_url(self, module, url_var):
        """Open dialog to edit module URL"""
        self.log_to_console(f"✏️ Opening URL edit dialog for {module['name']}")
        
        # Create URL edit dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit URL for {module['name']}")
        dialog.geometry("600x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 150, self.root.winfo_rooty() + 150))
        
        # Main frame
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text=f"Edit URL for {module['name']}", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Description
        desc_label = ttk.Label(main_frame, text=module['description'], font=("Arial", 9), foreground="gray")
        desc_label.pack(pady=(0, 10))
        
        # Current URL label
        current_label = ttk.Label(main_frame, text="Current URL:", font=("Arial", 9))
        current_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Current URL display
        current_url_label = ttk.Label(main_frame, text=url_var.get(), font=("Arial", 8), foreground="blue")
        current_url_label.pack(anchor=tk.W, pady=(0, 10))
        
        # New URL label
        new_label = ttk.Label(main_frame, text="New URL:", font=("Arial", 9))
        new_label.pack(anchor=tk.W, pady=(0, 5))
        
        # New URL entry
        new_url_var = tk.StringVar(value=url_var.get())
        new_url_entry = ttk.Entry(main_frame, textvariable=new_url_var, width=70, font=("Arial", 9))
        new_url_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        # Save button
        def save_url():
            new_url = new_url_var.get().strip()
            if new_url:
                url_var.set(new_url)
                self.log_to_console(f"✅ Updated URL for {module['name']}: {new_url}")
                dialog.destroy()
                messagebox.showinfo("Success", f"URL updated for {module['name']}")
            else:
                messagebox.showerror("Error", "Please enter a valid URL")
        
        save_button = ttk.Button(button_frame, text="Save", command=save_url)
        save_button.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Cancel button
        cancel_button = ttk.Button(button_frame, text="Cancel", command=dialog.destroy)
        cancel_button.pack(side=tk.RIGHT)
        
        # Reset to default button
        def reset_url():
            default_url = module['url']
            new_url_var.set(default_url)
            self.log_to_console(f"🔄 Reset URL for {module['name']} to default")
        
        reset_button = ttk.Button(button_frame, text="Reset to Default", command=reset_url)
        reset_button.pack(side=tk.LEFT)
        
        # Focus on URL entry
        new_url_entry.focus_set()
        new_url_entry.select_range(0, tk.END)
    

    
    def detect_azerothcore_type(self):
        """Detect which type of AzerothCore is cloned and return the source key"""
        git_source_dir = os.path.join(self._get_app_dir(), "GitSource")
        azerothcore_dir = os.path.join(git_source_dir, "azerothcore-wotlk")
        
        if not os.path.exists(azerothcore_dir):
            return None
        
        # Check for NPCBot indicators
        npcbot_indicators = [
            "src/server/scripts/Custom/npcbot",
            "src/server/scripts/Custom/bot",
            "modules/npcbot"
        ]
        
        # Check for PlayerBot indicators  
        playerbot_indicators = [
            "src/server/scripts/Custom/playerbot",
            "modules/playerbot"
        ]
        
        for indicator in npcbot_indicators:
            if os.path.exists(os.path.join(azerothcore_dir, indicator)):
                self.log_to_console(f"🔍 Detected NPCBot AzerothCore installation")
                return "npcbots"
        
        for indicator in playerbot_indicators:
            if os.path.exists(os.path.join(azerothcore_dir, indicator)):
                self.log_to_console(f"🔍 Detected PlayerBot AzerothCore installation")
                return "playerbots"
        
        self.log_to_console(f"🔍 Detected standard AzerothCore installation")
        return "azerothcore"

    def detect_cloned_modules(self, modules):
        """Detect which modules are already cloned in the main AzerothCore source"""
        cloned_modules = set()
        
        # Get the GitSource directory
        git_source_dir = os.path.join(self._get_app_dir(), "GitSource")
        azerothcore_dir = os.path.join(git_source_dir, "azerothcore-wotlk")
        modules_dir = os.path.join(azerothcore_dir, "modules")
        
        if os.path.exists(modules_dir):
            self.log_to_console(f"🔍 Checking modules in: {modules_dir}")
            
            # List all directories in the modules folder
            try:
                for item in os.listdir(modules_dir):
                    item_path = os.path.join(modules_dir, item)
                    if os.path.isdir(item_path):
                        # Check if this is a valid Git repository (has .git folder)
                        git_dir = os.path.join(item_path, ".git")
                        if os.path.exists(git_dir) and os.path.isdir(git_dir):
                            # Check if this directory name matches any of our modules
                            for module in modules:
                                if item == module['name']:
                                    cloned_modules.add(module['name'])
                                    self.log_to_console(f"✅ Found cloned module: {module['name']}")
                                    break
            except Exception as e:
                self.log_to_console(f"⚠️ Error reading modules directory {modules_dir}: {str(e)}")
        
        return cloned_modules
    
    def display_modules(self, parent_frame, window, modules, loading_label):
        """Display the loaded modules with single checkbox per module"""
        # Remove loading label if it exists
        if loading_label:
            loading_label.destroy()
        
        if not modules:
            no_modules_label = ttk.Label(parent_frame, text="No modules found or failed to load.", font=("Arial", 10))
            no_modules_label.pack(pady=20)
            return
        
        self.log_to_console(f"✅ Found {len(modules)} modules")
        
        # Detect AzerothCore type
        azerothcore_type_key = self.detect_azerothcore_type()
        if azerothcore_type_key is None:
            self.log_to_console("⚠️ No AzerothCore source detected")
            azerothcore_type_name = "None"
        else:
            azerothcore_type_name = self.source_repos[azerothcore_type_key]["name"]
            self.log_to_console(f"🔍 Detected {azerothcore_type_name} installation")
        
        # Detect already cloned modules
        cloned_modules = self.detect_cloned_modules(modules)
        if cloned_modules:
            self.log_to_console(f"🔍 Found {len(cloned_modules)} already cloned modules: {', '.join(cloned_modules)}")
        else:
            self.log_to_console("🔍 No previously cloned modules detected")
        
        # Create variables to store checkbox states, URLs, and widget references
        module_vars = {}
        module_urls = {}
        module_checkboxes = {}
        
        # Create scrollable frame for modules
        canvas = tk.Canvas(parent_frame)
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create module entries with single checkbox each
        for module in modules:
            # Create frame for each module
            module_frame = ttk.Frame(scrollable_frame)
            module_frame.pack(fill=tk.X, pady=2, padx=5)
            
            # Checkbox variable - set to True if module is already cloned
            is_cloned = module['name'] in cloned_modules
            var = tk.BooleanVar(value=is_cloned)
            module_vars[module['name']] = var
            
            # Checkbox with styling for already cloned modules
            checkbox_text = module['name']
            if is_cloned:
                checkbox_text = f"{module['name']} (Already Cloned)"
            
            checkbox = ttk.Checkbutton(module_frame, text=checkbox_text, variable=var)
            checkbox.pack(side=tk.LEFT)
            
            # Store checkbox reference for later updates
            module_checkboxes[module['name']] = checkbox
            
            # Disable checkbox if module is already cloned
            if is_cloned:
                checkbox.config(state='disabled')
            
            # Description (if available)
            if module['description']:
                desc_label = ttk.Label(module_frame, text=f" - {module['description']}", 
                                     font=("Arial", 8), foreground="gray")
                desc_label.pack(side=tk.LEFT, padx=(5, 10))
            
            # URL variable
            url_var = tk.StringVar(value=module['url'])
            module_urls[module['name']] = url_var
            
            # URL display (read-only)
            url_label = ttk.Label(module_frame, textvariable=url_var, 
                                font=("Arial", 8), foreground="blue")
            url_label.pack(side=tk.LEFT, padx=(5, 10))
            
            # Create a fixed-width frame for buttons to ensure alignment
            button_frame = ttk.Frame(module_frame)
            button_frame.pack(side=tk.RIGHT)
            
            # Clean button (always present) - positioned rightmost
            clean_button = ttk.Button(button_frame, text="🗑️ Clean", 
                                    command=lambda m=module: self.clean_individual_module(m))
            clean_button.pack(side=tk.RIGHT, padx=(5, 0))
            
            # URL edit button (always present) - positioned to the left of Clean button
            edit_button = ttk.Button(button_frame, text="✏️ Edit URL", 
                                   command=lambda m=module, v=url_var: self.edit_module_url(m, v))
            edit_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Store module data and variables for later use
        window.module_data = modules
        window.module_vars = module_vars
        window.module_urls = module_urls
        window.module_checkboxes = module_checkboxes
        
        # Create bottom frame for buttons
        button_frame = ttk.Frame(window)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        # Status label to show selection count
        status_text = f"Active Source: {azerothcore_type_name}"
        status_label = ttk.Label(button_frame, text=status_text, 
                                font=("Arial", 9), foreground="gray")
        status_label.pack(side=tk.LEFT)
        
        # Clone button
        clone_button = ttk.Button(button_frame, text="📥 Clone Selected Modules", 
                                 command=lambda: self.clone_selected_modules(window))
        clone_button.pack(side=tk.RIGHT)
        
        # Cancel button
        cancel_button = ttk.Button(button_frame, text="Cancel", 
                                  command=window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Store status label for updates
        window.status_label = status_label
    
    def show_modules_error(self, parent_frame, window, error_msg, loading_label):
        """Show error message when modules fail to load"""
        loading_label.destroy()
        
        error_label = ttk.Label(parent_frame, text=f"Error: {error_msg}", 
                               font=("Arial", 10), foreground="red")
        error_label.pack(pady=20)
        
        # Add retry button
        retry_button = ttk.Button(parent_frame, text="Retry", 
                                 command=lambda: self.load_azerothcore_modules(parent_frame, window))
        retry_button.pack(pady=10)
        
        # Add cancel button
        cancel_button = ttk.Button(parent_frame, text="Cancel", 
                                  command=window.destroy)
        cancel_button.pack(pady=5)
    
    def clone_selected_modules(self, window):
        """Clone the selected modules to the main AzerothCore source"""
        # Get selected modules (skip already cloned ones)
        selected_modules = []
        already_cloned_count = 0
        
        for module_name, var in window.module_vars.items():
            if var.get():
                # Find the module data
                for module in window.module_data:
                    if module['name'] == module_name:
                        # Check if this module is already cloned (checkbox would be disabled)
                        # We can detect this by checking if the text contains "(Already Cloned)"
                        # or by checking if the module is in the cloned modules set
                        git_source_dir = os.path.join(self._get_app_dir(), "GitSource")
                        azerothcore_dir = os.path.join(git_source_dir, "azerothcore-wotlk")
                        modules_dir = os.path.join(azerothcore_dir, "modules")
                        module_dir = os.path.join(modules_dir, module_name)
                        
                        if os.path.exists(module_dir):
                            already_cloned_count += 1
                            self.log_to_console(f"⏭️ Skipping already cloned module: {module_name}")
                        else:
                            # Create a copy of the module with the edited URL
                            module_copy = module.copy()
                            module_copy['url'] = window.module_urls[module_name].get()
                            selected_modules.append(module_copy)
                        break
        
        if not selected_modules:
            if already_cloned_count > 0:
                messagebox.showinfo("Info", f"All selected modules are already cloned. Skipped {already_cloned_count} modules.")
                self.log_to_console(f"ℹ️ All selected modules are already cloned")
            else:
                messagebox.showwarning("No Selection", "Please select at least one module to clone.")
            return
        
        self.log_to_console(f"📥 Selected {len(selected_modules)} modules for cloning (skipped {already_cloned_count} already cloned)")
        
        # Clone modules to the main AzerothCore source
        self.perform_single_repo_module_clone(selected_modules, window)
    
    def perform_single_repo_module_clone(self, selected_modules, modules_window):
        """Clone modules to the main AzerothCore source"""
        git_source_dir = os.path.join(self._get_app_dir(), "GitSource")
        azerothcore_dir = os.path.join(git_source_dir, "azerothcore-wotlk")
        modules_dir = os.path.join(azerothcore_dir, "modules")
        
        # Check if AzerothCore source exists
        if not os.path.exists(azerothcore_dir):
            messagebox.showerror("Error", "AzerothCore source not found. Please clone the main AzerothCore source first.")
            self.log_to_console("❌ AzerothCore source not found")
            return
        
        cloned_count = 0
        failed_count = 0
        total_modules = len(selected_modules)
        
        self.log_to_console(f"🚀 Starting module cloning to AzerothCore...")
        
        # Ensure modules directory exists
        os.makedirs(modules_dir, exist_ok=True)
        
        for module in selected_modules:
            try:
                if self.clone_single_module(module, modules_dir):
                    cloned_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                self.log_to_console(f"❌ Failed to clone {module['name']}: {str(e)}")
                failed_count += 1
        
        # Show completion message
        if cloned_count == total_modules:
            messagebox.showinfo("Module Cloning Complete", f"Successfully cloned all {cloned_count} modules!")
            self.log_to_console(f"✅ Successfully cloned all {cloned_count} modules")
        elif cloned_count > 0:
            messagebox.showwarning("Module Cloning Partial Success", 
                                 f"Cloned {cloned_count} out of {total_modules} modules successfully.\n"
                                 f"Failed: {failed_count} modules.\n\n"
                                 f"Check the console for details.")
            self.log_to_console(f"⚠️ Cloned {cloned_count} out of {total_modules} modules ({failed_count} failed)")
        else:
            messagebox.showerror("Module Cloning Failed", 
                               f"Failed to clone all {total_modules} modules.\n\n"
                               f"Check the console for details.")
            self.log_to_console(f"❌ Failed to clone all {total_modules} modules")
        
        # Close the modules window
        modules_window.destroy()
    
    def clean_all_modules(self):
        """Remove all cloned modules from the AzerothCore source"""
        git_source_dir = os.path.join(self._get_app_dir(), "GitSource")
        azerothcore_dir = os.path.join(git_source_dir, "azerothcore-wotlk")
        modules_dir = os.path.join(azerothcore_dir, "modules")
        
        # Check if AzerothCore source exists
        if not os.path.exists(azerothcore_dir):
            messagebox.showerror("Error", "AzerothCore source not found. Please clone the main AzerothCore source first.")
            self.log_to_console("❌ AzerothCore source not found")
            return
        
        # Check if modules directory exists
        if not os.path.exists(modules_dir):
            messagebox.showinfo("Info", "No modules directory found. Nothing to clean.")
            self.log_to_console("ℹ️ No modules directory found")
            return
        
        # Get list of all modules
        try:
            module_dirs = [d for d in os.listdir(modules_dir) 
                          if os.path.isdir(os.path.join(modules_dir, d))]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read modules directory: {str(e)}")
            self.log_to_console(f"❌ Failed to read modules directory: {str(e)}")
            return
        
        if not module_dirs:
            messagebox.showinfo("Info", "No modules found to clean.")
            self.log_to_console("ℹ️ No modules found to clean")
            return
        
        # Confirm deletion
        result = messagebox.askyesno("Confirm Clean Modules", 
                                   f"Are you sure you want to remove ALL {len(module_dirs)} modules?\n\n"
                                   f"This will permanently delete:\n" + 
                                   "\n".join(f"• {module}" for module in module_dirs[:10]) +
                                   (f"\n• ... and {len(module_dirs) - 10} more" if len(module_dirs) > 10 else ""))
        
        if not result:
            self.log_to_console("❌ Module cleaning cancelled by user")
            return
        
        # Remove all modules
        removed_count = 0
        failed_modules = []
        
        self.log_to_console(f"🧹 Starting to clean {len(module_dirs)} modules...")
        
        for module_dir in module_dirs:
            module_path = os.path.join(modules_dir, module_dir)
            try:
                import shutil
                import stat
                
                def handle_remove_readonly(func, path, exc):
                    """Handle readonly files by making them writable and retrying"""
                    if os.path.exists(path):
                        os.chmod(path, stat.S_IWRITE)
                        func(path)
                
                # Try to remove the directory with readonly file handling
                shutil.rmtree(module_path, onerror=handle_remove_readonly)
                removed_count += 1
                self.log_to_console(f"✅ Removed module: {module_dir}")
            except PermissionError as e:
                failed_modules.append(module_dir)
                self.log_to_console(f"❌ Permission denied when removing {module_dir}: {str(e)}")
            except Exception as e:
                failed_modules.append(module_dir)
                self.log_to_console(f"❌ Failed to remove {module_dir}: {str(e)}")
        
        # Show completion message
        if removed_count == len(module_dirs):
            messagebox.showinfo("Success", f"Successfully removed all {removed_count} modules!")
            self.log_to_console(f"✅ Successfully removed all {removed_count} modules")
        else:
            messagebox.showwarning("Partial Success", 
                                 f"Removed {removed_count} out of {len(module_dirs)} modules.\n"
                                 f"Failed to remove: {', '.join(failed_modules)}\n"
                                 f"Check the console for details.")
            self.log_to_console(f"⚠️ Removed {removed_count} out of {len(module_dirs)} modules")
    
    def clean_individual_module(self, module):
        """Remove a specific individual module"""
        git_source_dir = os.path.join(self._get_app_dir(), "GitSource")
        azerothcore_dir = os.path.join(git_source_dir, "azerothcore-wotlk")
        modules_dir = os.path.join(azerothcore_dir, "modules")
        module_dir = os.path.join(modules_dir, module['name'])
        
        # Check if AzerothCore source exists
        if not os.path.exists(azerothcore_dir):
            messagebox.showerror("Error", "AzerothCore source not found. Please clone the main AzerothCore source first.")
            self.log_to_console("❌ AzerothCore source not found")
            return
        
        # Check if module exists
        if not os.path.exists(module_dir):
            messagebox.showinfo("Info", f"Module {module['name']} is not cloned. Nothing to clean.")
            self.log_to_console(f"ℹ️ Module {module['name']} is not cloned")
            return
        
        # Confirm deletion
        result = messagebox.askyesno("Confirm Clean Module", 
                                   f"Are you sure you want to remove the module '{module['name']}'?\n\n"
                                   f"This will permanently delete the module from:\n{module_dir}")
        
        if not result:
            self.log_to_console(f"❌ Module {module['name']} cleaning cancelled by user")
            return
        
        # Remove the module with proper error handling for Git files
        try:
            import shutil
            import stat
            
            def handle_remove_readonly(func, path, exc):
                """Handle readonly files by making them writable and retrying"""
                if os.path.exists(path):
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
            
            # Try to remove the directory with readonly file handling
            shutil.rmtree(module_dir, onerror=handle_remove_readonly)
            messagebox.showinfo("Success", f"Successfully removed module '{module['name']}'!")
            self.log_to_console(f"✅ Successfully removed module: {module['name']}")
            
            # Update the checkbox state in the current window
            self.root.after(500, lambda: self.update_checkbox_after_clean(module['name']))
            
        except PermissionError as e:
            error_msg = f"Permission denied when removing module '{module['name']}'.\n\n"
            error_msg += "This usually happens when:\n"
            error_msg += "• The module is currently in use by another program\n"
            error_msg += "• Git processes are still running\n"
            error_msg += "• Files are locked by Windows\n\n"
            error_msg += "Try closing any programs that might be using the module and try again."
            messagebox.showerror("Permission Error", error_msg)
            self.log_to_console(f"❌ Permission denied when removing {module['name']}: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove module '{module['name']}': {str(e)}")
            self.log_to_console(f"❌ Failed to remove {module['name']}: {str(e)}")
    
    def update_checkbox_after_clean(self, module_name):
        """Update checkbox state after a module is cleaned"""
        # Find the currently open module window
        for child in self.root.winfo_children():
            if isinstance(child, tk.Toplevel) and "Modules" in child.title():
                # Check if this window has the required attributes
                if (hasattr(child, 'module_vars') and hasattr(child, 'module_checkboxes') and 
                    module_name in child.module_vars and module_name in child.module_checkboxes):
                    
                    # Get the checkbox widget directly
                    checkbox = child.module_checkboxes[module_name]
                    var = child.module_vars[module_name]
                    
                    # Update the checkbox state
                    var.set(False)  # Uncheck the checkbox
                    checkbox.config(state='normal')  # Enable the checkbox
                    
                    # Update the text to remove "(Already Cloned)" if present
                    current_text = checkbox.cget('text')
                    if "(Already Cloned)" in current_text:
                        new_text = current_text.replace(" (Already Cloned)", "")
                        checkbox.config(text=new_text)
                    
                    self.log_to_console(f"✅ Updated checkbox for {module_name}: unchecked, enabled, and text cleaned")
                    return
                else:
                    self.log_to_console(f"⚠️ Could not find checkbox reference for {module_name}")
                break
    
    
    def refresh_module_window(self):
        """Refresh the current module window to update the UI after cleaning"""
        # Find the currently open module window and refresh it
        for child in self.root.winfo_children():
            if isinstance(child, tk.Toplevel) and "Modules" in child.title():
                # Get the current window's module data
                if hasattr(child, 'module_data'):
                    # Clear the current content (except the bottom button frame)
                    for widget in child.winfo_children():
                        if isinstance(widget, tk.Frame) and not hasattr(widget, 'button_frame'):
                            widget.destroy()
                    
                    # Create a new main frame for the refreshed content
                    main_frame = ttk.Frame(child)
                    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                    
                    # Reload the modules
                    if "AzerothCore" in child.title():
                        self.load_azerothcore_modules(child)
                    elif "Community" in child.title():
                        self.load_community_modules(child)
                    elif "NPCBot" in child.title():
                        self.load_npcbot_modules(child)
                    elif "PlayerBot" in child.title():
                        self.load_playerbot_modules(child)
                break
    
    def show_repository_selection_window(self, selected_modules, modules_window):
        """Show window to select which AzerothCore repository to clone modules into"""
        self.log_to_console("🔍 Opening repository selection window")
        
        # Create repository selection window
        repo_window = tk.Toplevel(modules_window)
        repo_window.title("Select Target Repository")
        repo_window.geometry("500x300")
        repo_window.transient(modules_window)
        repo_window.grab_set()
        
        # Center the window
        repo_window.geometry("+%d+%d" % (modules_window.winfo_rootx() + 50, modules_window.winfo_rooty() + 50))
        
        # Main frame
        main_frame = ttk.Frame(repo_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Select Target Repository", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Description
        desc_label = ttk.Label(main_frame, text="Choose which AzerothCore repository to clone modules into:", font=("Arial", 9))
        desc_label.pack(pady=(0, 10))
        
        # Check which repositories are cloned
        git_source_dir = os.path.join(self._get_app_dir(), "GitSource")
        cloned_repos = []
        
        for key, repo in self.source_repos.items():
            repo_dir = os.path.join(git_source_dir, repo["folder"])
            if os.path.exists(repo_dir):
                # Check if it's a valid Git repository
                git_dir = os.path.join(repo_dir, ".git")
                if os.path.exists(git_dir) and os.path.isdir(git_dir):
                    cloned_repos.append({
                        'key': key,
                        'name': repo['name'],
                        'folder': repo['folder'],
                        'path': repo_dir
                    })
        
        if not cloned_repos:
            messagebox.showerror("No Repositories", 
                               "No cloned AzerothCore repositories found.\n\n"
                               "Please clone at least one AzerothCore repository first.")
            repo_window.destroy()
            return
        
        # Create radio buttons for repository selection
        repo_var = tk.StringVar()
        repo_var.set(cloned_repos[0]['key'])  # Default to first repository
        
        for repo in cloned_repos:
            radio = ttk.Radiobutton(main_frame, text=repo['name'], 
                                   variable=repo_var, value=repo['key'])
            radio.pack(anchor=tk.W, pady=2)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        
        # Clone button
        clone_button = ttk.Button(button_frame, text="📥    Clone Modules", 
                                 command=lambda: self.perform_module_clone(selected_modules, repo_var.get(), repo_window, modules_window))
        clone_button.pack(side=tk.RIGHT)
        
        # Cancel button
        cancel_button = ttk.Button(button_frame, text="Cancel", 
                                  command=repo_window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=(0, 10))
    
    def perform_module_clone(self, selected_modules, target_repo_key, repo_window, modules_window):
        """Perform the actual module cloning"""
        # Get target repository info
        target_repo = self.source_repos[target_repo_key]
        git_source_dir = os.path.join(self._get_app_dir(), "GitSource")
        target_repo_dir = os.path.join(git_source_dir, target_repo["folder"])
        modules_dir = os.path.join(target_repo_dir, "modules")
        
        # Create modules directory if it doesn't exist
        os.makedirs(modules_dir, exist_ok=True)
        
        self.log_to_console(f"📁 Target repository: {target_repo['name']}")
        self.log_to_console(f"📁 Modules directory: {modules_dir}")
        
        # Close the selection windows
        repo_window.destroy()
        modules_window.destroy()
        
        # Clone each selected module
        cloned_count = 0
        failed_count = 0
        total_modules = len(selected_modules)
        
        self.log_to_console(f"🚀 Starting module cloning to {target_repo['name']}...")
        
        for module in selected_modules:
            try:
                if self.clone_single_module(module, modules_dir):
                    cloned_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                self.log_to_console(f"❌ Failed to clone {module['name']}: {str(e)}")
                failed_count += 1
        
        # Show completion message
        if cloned_count == total_modules:
            messagebox.showinfo("Module Cloning Complete", f"Successfully cloned all {cloned_count} modules to {target_repo['name']}!")
            self.log_to_console(f"✅ Successfully cloned all {cloned_count} modules to {target_repo['name']}")
        elif cloned_count > 0:
            messagebox.showwarning("Module Cloning Partial Success", 
                                 f"Cloned {cloned_count} out of {total_modules} modules successfully to {target_repo['name']}.\n"
                                 f"Failed: {failed_count} modules.\n\n"
                                 f"Check the console for details.")
            self.log_to_console(f"⚠️ Cloned {cloned_count} out of {total_modules} modules to {target_repo['name']} ({failed_count} failed)")
        else:
            messagebox.showerror("Module Cloning Failed", 
                               f"Failed to clone all {total_modules} modules to {target_repo['name']}.\n\n"
                               f"Check the console for details.")
            self.log_to_console(f"❌ Failed to clone all {total_modules} modules to {target_repo['name']}")
    
    def clone_single_module(self, module, modules_dir):
        """Clone a single module into the modules directory"""
        module_name = module['name']
        module_url = module['url']
        module_dir = os.path.join(modules_dir, module_name)
        
        self.log_to_console(f"📥 Cloning module: {module_name}")
        self.log_to_console(f"📁 Target directory: {module_dir}")
        
        # Check if module already exists
        if os.path.exists(module_dir):
            if messagebox.askyesno("Module Exists", 
                                  f"Module {module_name} already exists.\n\n"
                                  f"Location: {module_dir}\n\n"
                                  "Do you want to clone it again?"):
                try:
                    import shutil
                    shutil.rmtree(module_dir)
                    self.log_to_console(f"🗑️ Removed existing {module_name} module")
                except Exception as e:
                    self.log_to_console(f"❌ Failed to remove existing {module_name} module: {str(e)}")
                    messagebox.showerror("Error", f"Failed to remove existing module:\n{str(e)}")
                    return
            else:
                self.log_to_console(f"❌ Skipping {module_name} - user chose not to re-clone")
                return
        
        # Clone the module
        try:
            result = subprocess.run([
                "git", "clone", module_url, module_name
            ], cwd=modules_dir, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.log_to_console(f"✅ Successfully cloned {module_name}")
                return True
            else:
                error_msg = result.stderr if result.stderr else "Unknown error occurred"
                self.log_to_console(f"❌ Failed to clone {module_name}: {error_msg}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_to_console(f"⏰ Clone operation timed out for {module_name}")
            return False
        except Exception as e:
            self.log_to_console(f"❌ Error cloning {module_name}: {str(e)}")
            return False
    
    def clone_repository(self, key):
        """Clone a Git repository"""
        repo = self.source_repos[key]
        git_source_dir = os.path.join(self._get_app_dir(), "GitSource")
        repo_dir = os.path.join(git_source_dir, repo["folder"])
        
        # Check if custom source has URL set
        if key == "custom" and not repo["url"]:
            self.log_to_console(f"❌ Cannot clone {repo['name']} - no URL set")
            messagebox.showwarning("No URL Set", 
                                 f"Please set a Git URL for the custom source first.\n\n"
                                 "Click the 🔗 button next to 'Custom' to set the URL.")
            return
        
        # Check if already cloned
        if os.path.exists(repo_dir):
            if messagebox.askyesno("Repository Exists", 
                                  f"{repo['name']} is already cloned.\n\n"
                                  f"Location: {repo_dir}\n\n"
                                  "Do you want to clone it again?"):
                # Remove existing directory
                try:
                    import shutil
                    self.log_to_console(f"🗑️ Removing existing {repo['name']} repository for re-clone")
                    shutil.rmtree(repo_dir)
                    self.log_to_console(f"✅ Successfully removed existing {repo['name']} repository")
                except Exception as e:
                    self.log_to_console(f"❌ Failed to remove existing {repo['name']} repository: {str(e)}")
                    messagebox.showerror("Error", f"Failed to remove existing directory:\n{str(e)}")
                    return
            else:
                self.log_to_console(f"❌ Clone cancelled for {repo['name']} - user chose not to re-clone")
                return
        
        # Create GitSource directory if it doesn't exist
        os.makedirs(git_source_dir, exist_ok=True)
        
        # Update status and start progress display
        self.update_source_status(key, "⏳", "Cloning...")
        self.start_source_progress(key)
        self.log_to_console(f"📥 Starting Git clone operation for {repo['name']}")
        self.log_to_console(f"📁 Clone URL: {repo['url']}")
        self.log_to_console(f"📁 Target directory: {repo_dir}")
        self.log_to_console(f"💡 Note: Git clone operations cannot be cancelled once started")
        
        # Run clone in separate thread
        clone_thread = threading.Thread(target=self._perform_clone, args=(key, repo, git_source_dir))
        clone_thread.daemon = True
        clone_thread.start()
    
    def _perform_clone(self, key, repo, git_source_dir):
        """Perform the actual Git clone operation"""
        try:
            repo_dir = os.path.join(git_source_dir, repo["folder"])
            
            self.log_to_console(f"🔄 Executing Git clone command for {repo['name']}")
            
            # Start progress simulation
            self._start_progress_simulation(key)
            
            # Record start time for actual clone operation
            clone_start_time = time.time()
            
            # Prepare clone command based on repository type
            if key == "playerbots":
                # Clone with Playerbot branch
                clone_cmd = ["git", "clone", repo["url"], "--branch=Playerbot", repo["folder"]]
                self.log_to_console(f"🔧 Executing: git clone {repo['url']} --branch=Playerbot {repo['folder']}")
            else:
                # Standard clone
                clone_cmd = ["git", "clone", repo["url"], repo["folder"]]
                self.log_to_console(f"🔧 Executing: git clone {repo['url']} {repo['folder']}")
            
            # Clone the repository
            result = subprocess.run(clone_cmd, cwd=git_source_dir, capture_output=True, text=True, timeout=300)
            
            # Calculate actual clone time
            clone_time = time.time() - clone_start_time
            
            # Log that Git clone operation has completed
            self.log_to_console(f"🔧 Git clone operation completed for {repo['name']} in {clone_time:.1f} seconds")
            
            # Stop progress simulation
            self._stop_progress_simulation(key)
            
            if result.returncode == 0:
                self.root.after(0, lambda: self.stop_source_progress(key))
                self.root.after(0, lambda: self.update_source_status(key, "✅", "Cloned"))
                self.root.after(0, lambda: self.log_to_console(f"✅ Successfully cloned {repo['name']} to {repo_dir}"))
                # Save cloned source to config
                self.root.after(0, lambda: self._save_cloned_source(key))
                self.root.after(0, lambda: messagebox.showinfo("Success", 
                    f"{repo['name']} has been cloned successfully!\n\n"
                    f"Location: {repo_dir}"))
            else:
                error_msg = result.stderr if result.stderr else "Unknown error occurred"
                self.root.after(0, lambda: self.stop_source_progress(key))
                self.root.after(0, lambda: self.update_source_status(key, "❌", "Clone Failed"))
                self.root.after(0, lambda: self.log_to_console(f"❌ Failed to clone {repo['name']}: {error_msg}"))
                self.root.after(0, lambda: messagebox.showerror("Clone Failed", 
                    f"Failed to clone {repo['name']}:\n\n{error_msg}"))
                
        except subprocess.TimeoutExpired:
            self._stop_progress_simulation(key)
            self.root.after(0, lambda: self.stop_source_progress(key))
            self.root.after(0, lambda: self.update_source_status(key, "❌", "Timeout"))
            self.root.after(0, lambda: self.log_to_console(f"⏰ Clone operation timed out for {repo['name']}"))
            self.root.after(0, lambda: messagebox.showerror("Clone Failed", 
                f"Clone operation timed out for {repo['name']}"))
        except Exception as e:
            self._stop_progress_simulation(key)
            self.root.after(0, lambda: self.stop_source_progress(key))
            self.root.after(0, lambda: self.update_source_status(key, "❌", "Error"))
            self.root.after(0, lambda: self.log_to_console(f"❌ Error during clone of {repo['name']}: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("Clone Failed", 
                f"Error cloning {repo['name']}:\n\n{str(e)}"))
    
    def _start_progress_simulation(self, key):
        """Start progress simulation for cloning operation"""
        self.progress_simulation_active = True
        self.progress_simulation_thread = threading.Thread(target=self._simulate_progress, args=(key,))
        self.progress_simulation_thread.daemon = True
        self.progress_simulation_thread.start()
        
        # Log that progress simulation has started
        repo_name = self.source_repos[key]["name"]
        self.log_to_console(f"📊 Starting progress simulation for {repo_name}")
    
    def _stop_progress_simulation(self, key):
        """Stop progress simulation for cloning operation"""
        self.progress_simulation_active = False
        
        # Log that progress simulation has stopped
        repo_name = self.source_repos[key]["name"]
        self.log_to_console(f"📊 Progress simulation completed for {repo_name}")
    
    def _simulate_progress(self, key):
        """Simulate progress updates during cloning"""
        # Estimated clone time (varies by repository size)
        estimated_time = random.randint(30, 120)  # 30 seconds to 2 minutes
        start_time = time.time()
        
        while self.progress_simulation_active:
            elapsed = time.time() - start_time
            if elapsed >= estimated_time:
                # Instead of breaking, continue with a slower progress rate
                # This ensures the simulation continues until the actual clone completes
                progress = min(95 + int((elapsed - estimated_time) / 10), 98)  # Slow progress after estimated time
            else:
                # Calculate progress percentage during estimated time
                progress = min(int((elapsed / estimated_time) * 100), 95)  # Cap at 95% during estimated time
            
            # Update progress display
            self.root.after(0, lambda p=progress: self.update_source_progress(key, p))
            
            # Log progress to console (every 10% or every 15 seconds)
            if progress % 10 == 0 or int(elapsed) % 15 == 0:
                repo_name = self.source_repos[key]["name"]
                if elapsed < estimated_time:
                    remaining_time = estimated_time - elapsed
                    self.root.after(0, lambda p=progress, name=repo_name, rem=remaining_time: 
                                  self.log_to_console(f"📥 {name} cloning progress: {p}% (est. {int(rem)}s remaining)"))
                else:
                    extra_time = elapsed - estimated_time
                    self.root.after(0, lambda p=progress, name=repo_name, extra=extra_time: 
                                  self.log_to_console(f"📥 {name} cloning progress: {p}% (continuing... +{int(extra_time)}s)"))
            
            # Wait before next update
            time.sleep(1)
        
        # If simulation stopped naturally, show completion
        if self.progress_simulation_active:
            self.root.after(0, lambda: self.update_source_progress(key, 100))
            repo_name = self.source_repos[key]["name"]
            self.root.after(0, lambda name=repo_name: 
                          self.log_to_console(f"📥 {name} cloning progress: 100%"))
    
    def clean_repository(self, key):
        """Clean (delete) a cloned repository"""
        repo = self.source_repos[key]
        git_source_dir = os.path.join(self._get_app_dir(), "GitSource")
        repo_dir = os.path.join(git_source_dir, repo["folder"])
        
        if not os.path.exists(repo_dir):
            messagebox.showinfo("Not Found", f"{repo['name']} is not cloned yet.")
            return
        
        if messagebox.askyesno("Confirm Clean", 
                              f"Are you sure you want to delete {repo['name']}?\n\n"
                              f"This will permanently remove:\n{repo_dir}\n\n"
                              "This action cannot be undone!"):
            try:
                self.log_to_console(f"🧹 Starting cleanup of {repo['name']} repository")
                
                # First try to remove Git attributes that might be read-only
                git_dir = os.path.join(repo_dir, ".git")
                if os.path.exists(git_dir):
                    # Remove read-only attributes from Git files
                    try:
                        subprocess.run(["git", "config", "--local", "--unset", "core.filemode"], 
                                     cwd=repo_dir, capture_output=True, timeout=10)
                        self.log_to_console(f"🔧 Removed Git file mode restrictions for {repo['name']}")
                    except:
                        pass  # Ignore if this fails
                
                # Try to remove the directory with shutil first
                try:
                    import shutil
                    shutil.rmtree(repo_dir, ignore_errors=True)
                    self.log_to_console(f"🗑️ Removed {repo['name']} directory using shutil")
                except:
                    pass
                
                # If directory still exists, try using Git clean command
                if os.path.exists(repo_dir):
                    try:
                        # Force remove the Git repository
                        subprocess.run(["git", "clean", "-fdx"], cwd=repo_dir, 
                                     capture_output=True, timeout=30)
                        # Remove the parent directory
                        os.rmdir(repo_dir)
                        self.log_to_console(f"🧹 Used Git clean command for {repo['name']}")
                    except:
                        # Last resort: try to remove with elevated permissions
                        try:
                            import stat
                            def remove_readonly(func, path, _):
                                os.chmod(path, stat.S_IWRITE)
                                func(path)
                            
                            shutil.rmtree(repo_dir, onerror=remove_readonly)
                            self.log_to_console(f"🔧 Used elevated permissions to remove {repo['name']}")
                        except Exception as e2:
                            raise Exception(f"Failed to remove repository: {str(e)}. Additional error: {str(e2)}")
                
                self.update_source_status(key, "⏳", "Not Cloned")
                # Remove cloned source from config since repository is cleaned
                self._remove_cloned_source_from_config()
                self.log_to_console(f"✅ Successfully cleaned {repo['name']} repository")
                messagebox.showinfo("Success", f"{repo['name']} has been cleaned successfully!")
                
            except Exception as e:
                self.log_to_console(f"❌ Failed to clean {repo['name']}: {str(e)}")
                messagebox.showerror("Error", f"Failed to clean {repo['name']}:\n\n{str(e)}\n\n"
                                    "You may need to manually delete the folder or close any applications "
                                    "that might be using files in this directory.")
    
    def update_repository(self, key):
        """Update (git pull) a cloned repository to latest commits"""
        repo = self.source_repos[key]
        git_source_dir = os.path.join(self._get_app_dir(), "GitSource")
        repo_dir = os.path.join(git_source_dir, repo["folder"])
        
        if not os.path.exists(repo_dir):
            self.log_to_console(f"❌ Cannot update {repo['name']} - repository not cloned")
            messagebox.showwarning("Not Found", 
                                 f"{repo['name']} must be cloned before updating.\n\n"
                                 "Please use the Clone button first.")
            return
        
        # Check if it's a valid Git repository
        git_dir = os.path.join(repo_dir, ".git")
        if not os.path.exists(git_dir):
            self.log_to_console(f"❌ Cannot update {repo['name']} - not a valid Git repository")
            messagebox.showerror("Invalid Repository", 
                               f"{repo['name']} is not a valid Git repository.\n\n"
                               "Please clone it again using the Clone button.")
            return
        
        self.log_to_console(f"🔄 Starting update of {repo['name']} repository")
        self.update_source_status(key, "⏳", "Updating...")
        self.start_source_progress(key)
        
        # Run update in separate thread
        update_thread = threading.Thread(target=self._perform_update, args=(key, repo, repo_dir))
        update_thread.daemon = True
        update_thread.start()
    
    def _perform_update(self, key, repo, repo_dir):
        """Perform the actual Git update operation"""
        try:
            self.log_to_console(f"🔄 Executing Git pull command for {repo['name']}")
            
            # Start progress simulation
            self._start_progress_simulation(key)
            
            # Record start time for actual update operation
            update_start_time = time.time()
            
            # First, fetch the latest changes
            fetch_cmd = ["git", "fetch", "origin"]
            self.log_to_console(f"🔧 Executing: git fetch origin")
            fetch_result = subprocess.run(fetch_cmd, cwd=repo_dir, capture_output=True, text=True, timeout=60)
            
            if fetch_result.returncode != 0:
                error_msg = fetch_result.stderr if fetch_result.stderr else "Unknown error occurred"
                self._stop_progress_simulation(key)
                self.root.after(0, lambda: self.stop_source_progress(key))
                self.root.after(0, lambda: self.update_source_status(key, "❌", "Fetch Failed"))
                self.root.after(0, lambda: self.log_to_console(f"❌ Failed to fetch updates for {repo['name']}: {error_msg}"))
                self.root.after(0, lambda: messagebox.showerror("Update Failed", 
                    f"Failed to fetch updates for {repo['name']}:\n\n{error_msg}"))
                return
            
            # Then pull the changes
            pull_cmd = ["git", "pull", "origin"]
            self.log_to_console(f"🔧 Executing: git pull origin")
            pull_result = subprocess.run(pull_cmd, cwd=repo_dir, capture_output=True, text=True, timeout=120)
            
            # Calculate actual update time
            update_time = time.time() - update_start_time
            
            # Log that Git update operation has completed
            self.log_to_console(f"🔧 Git update operation completed for {repo['name']} in {update_time:.1f} seconds")
            
            # Stop progress simulation
            self._stop_progress_simulation(key)
            
            if pull_result.returncode == 0:
                self.root.after(0, lambda: self.stop_source_progress(key))
                self.root.after(0, lambda: self.update_source_status(key, "✅", "Updated"))
                self.root.after(0, lambda: self.log_to_console(f"✅ Successfully updated {repo['name']} to latest commits"))
                
                # Show what was updated
                if pull_result.stdout:
                    self.root.after(0, lambda: self.log_to_console(f"📄 Update output: {pull_result.stdout.strip()}"))
                
                self.root.after(0, lambda: messagebox.showinfo("Success", 
                    f"{repo['name']} has been updated successfully!\n\n"
                    f"Location: {repo_dir}"))
            else:
                error_msg = pull_result.stderr if pull_result.stderr else "Unknown error occurred"
                self.root.after(0, lambda: self.stop_source_progress(key))
                self.root.after(0, lambda: self.update_source_status(key, "❌", "Update Failed"))
                self.root.after(0, lambda: self.log_to_console(f"❌ Failed to update {repo['name']}: {error_msg}"))
                self.root.after(0, lambda: messagebox.showerror("Update Failed", 
                    f"Failed to update {repo['name']}:\n\n{error_msg}"))
                
        except subprocess.TimeoutExpired:
            self._stop_progress_simulation(key)
            self.root.after(0, lambda: self.stop_source_progress(key))
            self.root.after(0, lambda: self.update_source_status(key, "❌", "Timeout"))
            self.root.after(0, lambda: self.log_to_console(f"⏰ Update operation timed out for {repo['name']}"))
            self.root.after(0, lambda: messagebox.showerror("Update Failed", 
                f"Update operation timed out for {repo['name']}"))
        except Exception as e:
            self._stop_progress_simulation(key)
            self.root.after(0, lambda: self.stop_source_progress(key))
            self.root.after(0, lambda: self.update_source_status(key, "❌", "Error"))
            self.root.after(0, lambda: self.log_to_console(f"❌ Error during update of {repo['name']}: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("Update Failed", 
                f"Error updating {repo['name']}:\n\n{str(e)}"))
    
    def set_custom_url(self):
        """Set custom Git URL for the custom source"""
        self.log_to_console("🔗 Opening custom URL dialog")
        
        # Create URL input dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Set Custom Git URL")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 150, self.root.winfo_rooty() + 150))
        
        # Title
        title_label = ttk.Label(dialog, text="Set Custom Git URL", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(20, 10))
        
        # Description
        desc_label = ttk.Label(dialog, 
                              text="Enter the Git URL for your custom AzerothCore repository:",
                              font=("Arial", 10))
        desc_label.pack(pady=(0, 10))
        
        # URL input frame
        url_frame = ttk.Frame(dialog)
        url_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # URL label
        ttk.Label(url_frame, text="Git URL:", font=("Arial", 10)).pack(anchor=tk.W)
        
        # URL entry
        url_var = tk.StringVar(value=self.source_repos["custom"]["url"])
        url_entry = ttk.Entry(url_frame, textvariable=url_var, width=70, font=("Arial", 10))
        url_entry.pack(fill=tk.X, pady=(5, 0))
        url_entry.focus()
        
        # Examples frame
        examples_frame = ttk.LabelFrame(dialog, text="Examples", padding=10)
        examples_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        examples_text = """• https://github.com/username/azerothcore-wotlk.git
• https://github.com/username/AzerothCore-wotlk-with-NPCBots.git
• https://gitlab.com/username/azerothcore-wotlk.git
• https://bitbucket.org/username/azerothcore-wotlk.git"""
        
        examples_label = ttk.Label(examples_frame, text=examples_text, 
                                 font=("Arial", 9), justify=tk.LEFT)
        examples_label.pack(anchor=tk.W)
        
        # Buttons frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(side=tk.BOTTOM, pady=(10, 20))
        
        # Result variable
        dialog.result = None
        
        # OK button
        def ok_clicked():
            url = url_var.get().strip()
            if not url:
                messagebox.showerror("URL Required", "Please enter a Git URL.")
                return
            
            # Basic URL validation
            if not (url.startswith("http://") or url.startswith("https://") or url.startswith("git@")):
                messagebox.showerror("Invalid URL", 
                                   "Please enter a valid Git URL.\n\n"
                                   "URL should start with:\n"
                                   "• http://\n"
                                   "• https://\n"
                                   "• git@")
                return
            
            dialog.result = url
            dialog.destroy()
        
        ok_button = ttk.Button(button_frame, text="OK", command=ok_clicked)
        ok_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Cancel button
        def cancel_clicked():
            dialog.result = None
            dialog.destroy()
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=cancel_clicked)
        cancel_button.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Bind Enter key to OK button
        url_entry.bind('<Return>', lambda e: ok_clicked())
        
        # Wait for dialog to close
        dialog.wait_window()
        
        if dialog.result:
            # Save the custom URL
            self.source_repos["custom"]["url"] = dialog.result
            self.log_to_console(f"✅ Custom Git URL set: {dialog.result}")
            
            # Save to config file
            self._save_custom_url_config(dialog.result)
            
            # Update status to show URL is set
            self.update_source_status("custom", "⏳", "URL Set")
            
            messagebox.showinfo("URL Set", 
                              f"Custom Git URL has been set successfully!\n\n"
                              f"URL: {dialog.result}\n\n"
                              "You can now use the Clone button to clone this repository.")
        else:
            self.log_to_console("❌ Custom URL setting cancelled")
    
    def _save_custom_url_config(self, url):
        """Save custom URL to configuration file"""
        try:
            config_file = os.path.join(self._get_app_dir(), "acb_config.json")
            
            # Load existing config or create new one
            config = {}
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            # Update custom URL
            config["custom_git_url"] = url
            
            # Save config
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            self.log_to_console(f"💾 Custom URL saved to config file: {config_file}")
            
        except Exception as e:
            self.log_to_console(f"⚠️ Could not save custom URL to config: {str(e)}")
    
    def _load_custom_url_config(self):
        """Load custom URL from configuration file"""
        try:
            config_file = os.path.join(self._get_app_dir(), "acb_config.json")
            
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                if "custom_git_url" in config:
                    self.source_repos["custom"]["url"] = config["custom_git_url"]
                    self.log_to_console(f"📁 Loaded custom URL from config: {config['custom_git_url']}")
                    return True
            
        except Exception as e:
            self.log_to_console(f"⚠️ Could not load custom URL from config: {str(e)}")
        
        return False
    
    def _save_cloned_source(self, source_key):
        """Save which source repository was cloned to configuration file"""
        try:
            config_file = os.path.join(self._get_app_dir(), "acb_config.json")
            
            # Load existing config or create new one
            config = {}
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            # Update cloned source
            config["cloned_source"] = source_key
            
            # Save config
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            self.log_to_console(f"💾 Saved cloned source to config: {self.source_repos[source_key]['name']}")
            
        except Exception as e:
            self.log_to_console(f"⚠️ Could not save cloned source to config: {str(e)}")
    
    def _load_cloned_source(self):
        """Load which source repository was cloned from configuration file"""
        try:
            config_file = os.path.join(self._get_app_dir(), "acb_config.json")
            
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                if "cloned_source" in config:
                    cloned_source = config["cloned_source"]
                    # Verify the source key is valid
                    if cloned_source in self.source_repos:
                        return cloned_source
            
        except Exception as e:
            self.log_to_console(f"⚠️ Could not load cloned source from config: {str(e)}")
        
        return None
    
    def _remove_cloned_source_from_config(self):
        """Remove the cloned source from configuration file"""
        try:
            config_file = os.path.join(self._get_app_dir(), "acb_config.json")
            
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Remove cloned_source key if it exists
                if "cloned_source" in config:
                    del config["cloned_source"]
                    
                    # Save updated config
                    with open(config_file, 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=2)
                    
                    self.log_to_console("🗑️ Removed cloned source from config file")
            
        except Exception as e:
            self.log_to_console(f"⚠️ Could not remove cloned source from config: {str(e)}")
    
    def _apply_modern_theme(self):
        """Apply modern theme styling to the application"""
        try:
            # Create style object
            style = ttk.Style()
            
            # Set theme
            style.theme_use('clam')
            
            # Define color scheme - Standard Windows grey theme
            colors = {
                'bg_primary': '#f0f0f0',      # Standard Windows grey background
                'bg_secondary': '#e8e8e8',    # Slightly darker grey
                'bg_tertiary': '#d0d0d0',     # Even darker grey for buttons
                'fg_primary': '#000000',      # Black text
                'fg_secondary': '#333333',    # Dark grey text
                'fg_muted': '#666666',        # Muted text
                'accent': '#4a9eff',          # Blue accent (keep blue highlight)
                'accent_hover': '#5ba8ff',    # Lighter blue for hover
                'success': '#4caf50',         # Green for success
                'warning': '#ff9800',         # Orange for warning
                'error': '#f44336',           # Red for error
                'border': '#a0a0a0',          # Light grey border
                'border_light': '#c0c0c0'     # Lighter border
            }
            
            # Configure main window
            self.root.configure(bg=colors['bg_primary'])
            
            # Configure Notebook (tabs) styling
            style.configure('TNotebook', 
                          background=colors['bg_primary'],
                          borderwidth=0,
                          tabmargins=[0, 0, 0, 0])
            
            # Configure unselected tabs (smaller)
            style.configure('TNotebook.Tab',
                          background=colors['bg_secondary'],
                          foreground=colors['fg_secondary'],
                          padding=[15, 8],
                          borderwidth=0,
                          focuscolor='none')
            
            # Configure selected tab (bigger)
            style.configure('TNotebook.Tab',
                          background=colors['accent'],
                          foreground=colors['fg_primary'],
                          padding=[25, 12],
                          borderwidth=0,
                          focuscolor='none')
            
            style.map('TNotebook.Tab',
                     background=[('selected', colors['accent']),
                                ('active', colors['bg_tertiary']),
                                ('!active', colors['bg_secondary'])],
                     foreground=[('selected', colors['fg_primary']),
                                ('active', colors['fg_primary']),
                                ('!active', colors['fg_secondary'])],
                     padding=[('selected', [25, 12]),
                             ('active', [20, 10]),
                             ('!active', [15, 8])])
            
            # Configure Frame styling
            style.configure('TFrame',
                          background=colors['bg_primary'],
                          borderwidth=0)
            
            # Configure Label styling
            style.configure('TLabel',
                          background=colors['bg_primary'],
                          foreground=colors['fg_primary'],
                          font=('Segoe UI', 9))
            
            style.configure('Header.TLabel',
                          background=colors['bg_primary'],
                          foreground=colors['fg_primary'],
                          font=('Segoe UI', 10, 'bold'))
            
            style.configure('Title.TLabel',
                          background=colors['bg_primary'],
                          foreground=colors['fg_primary'],
                          font=('Segoe UI', 12, 'bold'))
            
            # Configure Button styling
            style.configure('TButton',
                          background=colors['bg_tertiary'],
                          foreground=colors['fg_primary'],
                          borderwidth=1,
                          relief='flat',
                          padding=[10, 5],
                          font=('Segoe UI', 9))
            
            style.map('TButton',
                     background=[('active', colors['accent']),
                                ('pressed', colors['accent_hover'])],
                     foreground=[('active', colors['fg_primary']),
                                ('pressed', colors['fg_primary'])],
                     relief=[('pressed', 'flat'),
                            ('!pressed', 'flat')])
            
            # Configure special button styles
            style.configure('Accent.TButton',
                          background=colors['accent'],
                          foreground=colors['fg_primary'],
                          font=('Segoe UI', 9, 'bold'))
            
            style.map('Accent.TButton',
                     background=[('active', colors['accent_hover']),
                                ('pressed', colors['accent'])],
                     foreground=[('active', colors['fg_primary']),
                                ('pressed', colors['fg_primary'])])
            
            # Configure Entry styling
            style.configure('TEntry',
                          fieldbackground=colors['bg_tertiary'],
                          foreground=colors['fg_primary'],
                          borderwidth=1,
                          relief='flat',
                          insertcolor=colors['fg_primary'],
                          font=('Segoe UI', 9))
            
            style.map('TEntry',
                     focuscolor=colors['accent'],
                     bordercolor=[('focus', colors['accent']),
                                 ('!focus', colors['border'])])
            
            # Configure Checkbutton styling
            style.configure('TCheckbutton',
                          background=colors['bg_primary'],
                          foreground=colors['fg_primary'],
                          focuscolor='none',
                          font=('Segoe UI', 9))
            
            # Configure Progressbar styling
            style.configure('TProgressbar',
                          background=colors['accent'],
                          troughcolor=colors['bg_tertiary'],
                          borderwidth=0,
                          lightcolor=colors['accent'],
                          darkcolor=colors['accent'])
            
            # Configure custom progress bar styles
            style.configure('Green.Horizontal.TProgressbar',
                          background=colors['success'],
                          troughcolor=colors['bg_tertiary'],
                          borderwidth=0,
                          lightcolor=colors['success'],
                          darkcolor=colors['success'])
            
            style.configure('Blue.Horizontal.TProgressbar',
                          background=colors['accent'],
                          troughcolor=colors['bg_tertiary'],
                          borderwidth=0,
                          lightcolor=colors['accent'],
                          darkcolor=colors['accent'])
            
            # Configure Scrollbar styling
            style.configure('TScrollbar',
                          background=colors['bg_tertiary'],
                          troughcolor=colors['bg_secondary'],
                          borderwidth=0,
                          arrowcolor=colors['fg_secondary'],
                          darkcolor=colors['bg_tertiary'],
                          lightcolor=colors['bg_tertiary'])
            
            style.map('TScrollbar',
                     background=[('active', colors['accent']),
                                ('pressed', colors['accent_hover'])],
                     arrowcolor=[('active', colors['fg_primary']),
                                ('pressed', colors['fg_primary'])])
            
            # Configure LabelFrame styling
            style.configure('TLabelframe',
                          background=colors['bg_primary'],
                          foreground=colors['fg_primary'],
                          borderwidth=1,
                          relief='solid')
            
            style.configure('TLabelframe.Label',
                          background=colors['bg_primary'],
                          foreground=colors['fg_primary'],
                          font=('Segoe UI', 9, 'bold'))
            
            # Configure Combobox styling
            style.configure('TCombobox',
                          fieldbackground=colors['bg_tertiary'],
                          foreground=colors['fg_primary'],
                          borderwidth=1,
                          relief='flat',
                          arrowcolor=colors['fg_secondary'],
                          font=('Segoe UI', 9))
            
            style.map('TCombobox',
                     fieldbackground=[('readonly', colors['bg_tertiary'])],
                     selectbackground=[('focus', colors['accent'])],
                     selectforeground=[('focus', colors['fg_primary'])],
                     bordercolor=[('focus', colors['accent']),
                                 ('!focus', colors['border'])])
            
            # Configure Text widget styling
            style.configure('Text',
                          background=colors['bg_tertiary'],
                          foreground=colors['fg_primary'],
                          insertbackground=colors['fg_primary'],
                          selectbackground=colors['accent'],
                          selectforeground=colors['fg_primary'],
                          borderwidth=1,
                          relief='flat')
            
            # Store colors for later use
            self.theme_colors = colors
            
            self.log_to_console("🎨 Modern theme applied successfully")
            
        except Exception as e:
            self.log_to_console(f"⚠️ Could not apply modern theme: {str(e)}")
    
    def build_repository(self, key):
        """Show firewall notification and start build process"""
        repo = self.source_repos[key]
        
        self.log_to_console(f"🔨 Build button clicked for {repo['name']}")
        
        # Show firewall notification first
        self._show_firewall_notification(key)
    
    def _start_build_process(self, key):
        """Start the actual build process after firewall notification"""
        repo = self.source_repos[key]
        git_source_dir = os.path.join(self._get_app_dir(), "GitSource")
        repo_dir = os.path.join(git_source_dir, repo["folder"])
        
        if not os.path.exists(repo_dir):
            self.log_to_console(f"❌ Cannot build {repo['name']} - repository not cloned")
            messagebox.showwarning("Not Found", 
                                 f"{repo['name']} must be cloned before building.\n\n"
                                 "Please use the Clone button first.")
            return
        
        # Check if CMake is available
        cmake_path = self._find_cmake()
        if not cmake_path:
            self.log_to_console(f"❌ CMake not found - cannot build {repo['name']}")
            messagebox.showerror("CMake Required", 
                               "CMake is required for building AzerothCore.\n\n"
                               "Please install CMake first using the Install button.")
            return
        
        # Check if Visual Studio is available
        vs_path = self._find_visual_studio()
        if not vs_path:
            self.log_to_console(f"❌ Visual Studio not found - cannot build {repo['name']}")
            messagebox.showerror("Visual Studio Required", 
                               "Visual Studio is required for building AzerothCore.\n\n"
                               "Please install Visual Studio first using the Install button.")
            return
        
        # Create build directory
        build_dir = os.path.join(self._get_app_dir(), "Build")
        os.makedirs(build_dir, exist_ok=True)
        self.log_to_console(f"📁 Created build directory: {build_dir}")
        
        # Start the build process
        self.log_to_console(f"🚀 Starting build process for {repo['name']}")
        self._start_build_process_thread(key, repo, repo_dir, build_dir, cmake_path, vs_path)
    
    def _find_cmake(self):
        """Find CMake installation path"""
        # Check common CMake paths
        cmake_paths = [
            r"C:\Program Files\CMake\bin\cmake.exe",
            r"C:\Program Files (x86)\CMake\bin\cmake.exe"
        ]
        
        for path in cmake_paths:
            if os.path.exists(path):
                self.log_to_console(f"✅ Found CMake at: {path}")
                return path
        
        # Check PATH environment variable
        try:
            result = subprocess.run(["cmake", "--version"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log_to_console("✅ Found CMake in PATH")
                return "cmake"
        except:
            pass
        
        return None
    
    def _find_visual_studio(self):
        """Find Visual Studio installation path"""
        try:
            # Check registry for Visual Studio
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SOFTWARE\Microsoft\VisualStudio\Setup\VS") as key:
                install_path, _ = winreg.QueryValueEx(key, "InstallLocation")
                if install_path and os.path.exists(install_path):
                    self.log_to_console(f"✅ Found Visual Studio at: {install_path}")
                    return install_path
        except:
            pass
        
        # Check common Visual Studio paths
        vs_paths = [
            r"C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\devenv.exe",
            r"C:\Program Files\Microsoft Visual Studio\2022\Professional\Common7\IDE\devenv.exe",
            r"C:\Program Files\Microsoft Visual Studio\2022\Enterprise\Common7\IDE\devenv.exe"
        ]
        
        for path in vs_paths:
            if os.path.exists(path):
                self.log_to_console(f"✅ Found Visual Studio at: {path}")
                return path
        
        return None
    
    def _start_build_process_thread(self, key, repo, repo_dir, build_dir, cmake_path, vs_path):
        """Start the automated build process"""
        # Reset build state
        self.build_cancelled = False
        
        # Enable cancel button and update status
        self.cancel_build_button.config(state="normal")
        self.build_status_label.config(text=f"Building {repo['name']}...")
        self.build_main_progress.config(value=0)
        
        # Log build start
        self.log_to_console(f"🔨 Starting build process for {repo['name']}")
        self.log_to_console(f"📁 Source: {repo_dir}")
        self.log_to_console(f"📁 Build: {build_dir}")
        
        # Start build in separate thread
        build_thread = threading.Thread(target=self._perform_build, args=(key, repo, repo_dir, build_dir, cmake_path, vs_path))
        build_thread.daemon = True
        build_thread.start()
    
    def _cancel_build_process(self):
        """Cancel the current build process"""
        if messagebox.askyesno("Cancel Build", 
                              "Are you sure you want to cancel the build process?"):
            self.build_cancelled = True
            self.log_to_console(f"❌ User cancelled build process")
            
            # Terminate running processes
            self._terminate_build_processes()
            
            self._finish_build_process()
        else:
            self.log_to_console(f"🔄 User chose to continue build process")
    
    def _terminate_build_processes(self):
        """Terminate all running build processes"""
        try:
            # Terminate CMake process if running
            if self.current_cmake_process and self.current_cmake_process.poll() is None:
                self.log_to_console("🛑 Terminating CMake process...")
                self.current_cmake_process.terminate()
                try:
                    self.current_cmake_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.log_to_console("⚠️ CMake process did not terminate gracefully, forcing kill...")
                    self.current_cmake_process.kill()
                self.current_cmake_process = None
            
            # Terminate MSBuild process if running
            if self.current_msbuild_process and self.current_msbuild_process.poll() is None:
                self.log_to_console("🛑 Terminating MSBuild process...")
                self.current_msbuild_process.terminate()
                try:
                    self.current_msbuild_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.log_to_console("⚠️ MSBuild process did not terminate gracefully, forcing kill...")
                    self.current_msbuild_process.kill()
                self.current_msbuild_process = None
            
            # Also try to kill any remaining MSBuild processes
            self._kill_remaining_msbuild_processes()
            
            self.log_to_console("✅ All build processes terminated")
            
        except Exception as e:
            self.log_to_console(f"⚠️ Error terminating build processes: {str(e)}")
    
    def _kill_remaining_msbuild_processes(self):
        """Kill any remaining MSBuild processes that might be running"""
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] and 'msbuild' in proc.info['name'].lower():
                        self.log_to_console(f"🛑 Killing remaining MSBuild process (PID: {proc.info['pid']})")
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except ImportError:
            # If psutil is not available, try using taskkill command
            try:
                subprocess.run(['taskkill', '/f', '/im', 'msbuild.exe'], 
                             capture_output=True, timeout=10)
                self.log_to_console("🛑 Used taskkill to terminate MSBuild processes")
            except Exception as e:
                self.log_to_console(f"⚠️ Could not kill remaining MSBuild processes: {str(e)}")
        except Exception as e:
            self.log_to_console(f"⚠️ Error killing remaining MSBuild processes: {str(e)}")
    
    def _finish_build_process(self):
        """Finish the build process and reset UI"""
        self.cancel_build_button.config(state="disabled")
        self.build_status_label.config(text="Build progress")
        self.build_main_progress.config(value=0)
        self.current_build_process = None
        self.current_cmake_process = None
        self.current_msbuild_process = None
    
    def _perform_build(self, key, repo, repo_dir, build_dir, cmake_path, vs_path):
        """Perform the actual build process"""
        try:
            # Check if build was cancelled before starting
            if self.build_cancelled:
                self.log_to_console("❌ Build process cancelled before starting")
                return
            
            # Step 1: CMake Configuration
            self.root.after(0, lambda: self.build_status_label.config(text="Configuring CMake project..."))
            self.log_to_console("🚀 Starting CMake configuration...")
            
            # Run CMake configure
            cmake_config_result = self._run_cmake_configure_new(repo_dir, build_dir, cmake_path)
            if not cmake_config_result or self.build_cancelled:
                self.log_to_console("❌ CMake configuration failed")
                return
            
            # Check if cancelled after CMake configure
            if self.build_cancelled:
                self.log_to_console("❌ Build cancelled after CMake configuration")
                return
            
            # Step 2: CMake Generation
            self.root.after(0, lambda: self.build_status_label.config(text="Generating Visual Studio solution..."))
            self.log_to_console("📋 Generating Visual Studio solution files...")
            
            cmake_generate_result = self._run_cmake_generate_new(build_dir)
            if not cmake_generate_result or self.build_cancelled:
                self.log_to_console("❌ CMake generation failed")
                return
            
            # Check if cancelled after CMake generate
            if self.build_cancelled:
                self.log_to_console("❌ Build cancelled after CMake generation")
                return
            
            # Step 3: Visual Studio Build
            self.root.after(0, lambda: self.build_status_label.config(text="Building with Visual Studio..."))
            self.log_to_console("🔨 Starting Visual Studio build process...")
            
            build_result = self._run_visual_studio_build_new(build_dir)
            if not build_result or self.build_cancelled:
                self.log_to_console("❌ Visual Studio build failed")
                return
            
            # Build completed successfully
            self.root.after(0, lambda: self.build_status_label.config(text="Build completed successfully!"))
            self.log_to_console("🎉 Build completed successfully!")
            self.log_to_console(f"📁 Build output location: {build_dir}")
            
            # Show completion message
            self.root.after(0, lambda: messagebox.showinfo("Build Complete", 
                f"{key} has been built successfully!\n\n"
                f"Build output location: {build_dir}"))
            
            # Finish build process
            self.root.after(0, lambda: self._finish_build_process())
            
        except Exception as e:
            self.log_to_console(f"❌ Build process error: {str(e)}")
            self.root.after(0, lambda: self._finish_build_process())
    
    def _run_cmake_configure_new(self, repo_dir, build_dir, cmake_path):
        """Run CMake configure step without dialog"""
        try:
            self.log_to_console(f"📁 Source directory: {repo_dir}")
            self.log_to_console(f"📁 Build directory: {build_dir}")
            
            # CMake configure command - this generates the Visual Studio solution files
            cmd = [
                cmake_path,
                "-S", repo_dir,
                "-B", build_dir,
                "-G", "Visual Studio 17 2022",
                "-A", "x64",
                "-DCMAKE_BUILD_TYPE=RelWithDebInfo"
            ]
            
            # Add extractor tools option based on checkbox state
            if self.generate_extractors_var.get():
                cmd.append("-DTOOLS_BUILD=all")
                self.log_to_console("🔧 Including extractor tools (DTOOLS) in build")
            else:
                cmd.append("-DTOOLS_BUILD=none")
                self.log_to_console("⏭️ Skipping extractor tools (DTOOLS) in build")
            
            self.log_to_console(f"🔧 Running CMake configure: {' '.join(cmd)}")
            
            # Use Popen to allow process termination
            self.current_cmake_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait for process to complete or be cancelled
            try:
                stdout, stderr = self.current_cmake_process.communicate(timeout=300)
                result = type('Result', (), {'returncode': self.current_cmake_process.returncode, 'stdout': stdout, 'stderr': stderr})()
            except subprocess.TimeoutExpired:
                self.current_cmake_process.kill()
                stdout, stderr = self.current_cmake_process.communicate()
                result = type('Result', (), {'returncode': -1, 'stdout': stdout, 'stderr': stderr})()
            
            # Check if build was cancelled during CMake
            if self.build_cancelled:
                self.log_to_console("❌ Build cancelled during CMake configuration")
                return False
            
            if result.returncode == 0:
                self.log_to_console("✅ CMake configuration completed successfully")
                self.log_to_console("📋 Visual Studio solution files generated")
                # Update build progress - CMake configure is ~30% of total build
                self.root.after(0, lambda: self.build_main_progress.config(value=30))
                return True
            else:
                self.log_to_console(f"❌ CMake configuration failed:")
                self.log_to_console(f"STDOUT: {result.stdout}")
                self.log_to_console(f"STDERR: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_to_console("⏰ CMake configuration timed out")
            return False
        except Exception as e:
            self.log_to_console(f"❌ CMake configuration error: {str(e)}")
            return False
    
    def _run_cmake_generate_new(self, build_dir):
        """Run CMake generate step without dialog - this is now just a verification step"""
        try:
            self.log_to_console("📋 Verifying generated Visual Studio solution files...")
            
            # Check if the solution file was created
            solution_file = os.path.join(build_dir, "AzerothCore.sln")
            if os.path.exists(solution_file):
                self.log_to_console(f"✅ Solution file found: {solution_file}")
                # Update build progress - CMake generate is ~40% of total build
                self.root.after(0, lambda: self.build_main_progress.config(value=40))
                return True
            else:
                self.log_to_console(f"❌ Solution file not found: {solution_file}")
                self.log_to_console("📁 Checking build directory contents:")
                
                # List contents of build directory for debugging
                try:
                    build_contents = os.listdir(build_dir)
                    for item in build_contents:
                        self.log_to_console(f"   - {item}")
                except Exception as e:
                    self.log_to_console(f"   Error listing directory: {str(e)}")
                
                return False
                
        except Exception as e:
            self.log_to_console(f"❌ CMake generation verification error: {str(e)}")
            return False
    
    def _run_visual_studio_build_new(self, build_dir):
        """Run Visual Studio build step without dialog"""
        try:
            self.log_to_console("🔨 Starting Visual Studio build process...")
            
            # Find MSBuild executable
            msbuild_path = self._find_msbuild()
            if not msbuild_path:
                self.log_to_console("❌ MSBuild not found. Please ensure Visual Studio is installed.")
                return False
            
            self.log_to_console(f"🔍 Using MSBuild: {msbuild_path}")
            
            # Build the solution using MSBuild
            solution_file = os.path.join(build_dir, "AzerothCore.sln")
            if not os.path.exists(solution_file):
                self.log_to_console(f"❌ Solution file not found: {solution_file}")
                return False
            
            self.log_to_console(f"📁 Building solution: {solution_file}")
            
            # Use MSBuild to build the solution with full path
            msbuild_cmd = [
                msbuild_path,
                solution_file,
                "/p:Configuration=RelWithDebInfo",
                "/p:Platform=x64",
                "/p:BuildProjectReferences=false",
                "/m"
            ]
            
            self.log_to_console(f"🔧 Running MSBuild: {' '.join(msbuild_cmd)}")
            
            # Use Popen to allow process termination
            self.current_msbuild_process = subprocess.Popen(msbuild_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait for process to complete or be cancelled
            try:
                stdout, stderr = self.current_msbuild_process.communicate(timeout=1800)  # 30 minutes timeout
                result = type('Result', (), {'returncode': self.current_msbuild_process.returncode, 'stdout': stdout, 'stderr': stderr})()
            except subprocess.TimeoutExpired:
                self.current_msbuild_process.kill()
                stdout, stderr = self.current_msbuild_process.communicate()
                result = type('Result', (), {'returncode': -1, 'stdout': stdout, 'stderr': stderr})()
            
            # Check if build was cancelled during MSBuild
            if self.build_cancelled:
                self.log_to_console("❌ Build cancelled during MSBuild compilation")
                return False
            
            if result.returncode == 0:
                self.log_to_console("✅ Visual Studio build completed successfully")
                self.log_to_console(f"📊 Build output: {result.stdout}")
                # Update build progress - Visual Studio build is ~100% of total build
                self.root.after(0, lambda: self.build_main_progress.config(value=100))
                return True
            else:
                self.log_to_console("❌ Visual Studio build failed:")
                self.log_to_console(f"STDOUT: {result.stdout}")
                self.log_to_console(f"STDERR: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_to_console("⏰ Visual Studio build timed out (30 minutes)")
            return False
        except Exception as e:
            self.log_to_console(f"❌ Visual Studio build error: {str(e)}")
            return False
    
    
    def update_source_status(self, key, icon, status):
        """Update the status display for a source repository"""
        if key in self.source_widgets:
            widgets = self.source_widgets[key]
            widgets["status_icon"].config(text=icon)
            widgets["status_text"].config(text=status)
            
            # Update colors based on status
            if icon == "✅":
                widgets["status_text"].config(foreground="green")
                # Enable Update button for cloned repositories
                widgets["update_button"].config(state="normal")
            elif icon == "❌":
                widgets["status_text"].config(foreground="red")
                # Disable Update button for failed states
                widgets["update_button"].config(state="disabled")
            elif icon == "⚠️":
                widgets["status_text"].config(foreground="orange")
                # Disable Update button for warning states
                widgets["update_button"].config(state="disabled")
            else:
                widgets["status_text"].config(foreground="black")
                # Disable Update button for other states (like "Not Cloned", "Cloning...", etc.)
                widgets["update_button"].config(state="disabled")
    
    def start_source_progress(self, key):
        """Start the progress display for a source repository"""
        if key in self.source_widgets:
            widgets = self.source_widgets[key]
            widgets["progress_bar"].config(value=0)
    
    def stop_source_progress(self, key):
        """Stop the progress display for a source repository"""
        if key in self.source_widgets:
            widgets = self.source_widgets[key]
            widgets["progress_bar"].config(value=0)
    
    def update_source_progress(self, key, percentage):
        """Update the progress bar for a source repository"""
        if key in self.source_widgets:
            widgets = self.source_widgets[key]
            widgets["progress_bar"].config(value=percentage)
    
    def start_build_progress(self):
        """Start the build progress bar"""
        if hasattr(self, 'build_progress_bar'):
            self.build_progress_bar.config(value=0)
    
    def stop_build_progress(self):
        """Stop the build progress bar"""
        if hasattr(self, 'build_progress_bar'):
            self.build_progress_bar.config(value=0)
    
    def update_build_progress(self, percentage):
        """Update the build progress bar"""
        if hasattr(self, 'build_progress_bar'):
            self.build_progress_bar.config(value=percentage)
    
    def _check_source_status(self):
        """Check the initial status of source repositories"""
        self.log_to_console("🔍 Checking initial source repository status...")
        git_source_dir = os.path.join(self._get_app_dir(), "GitSource")
        
        # Load saved cloned source from config first
        saved_cloned_source = self._load_cloned_source()
        
        # Detect which source is actually cloned (fallback method)
        detected_source = self.detect_azerothcore_type()
        
        # Use saved source if available, otherwise use detected source
        cloned_source = saved_cloned_source if saved_cloned_source else detected_source
        
        # Log which method was used
        if saved_cloned_source:
            self.log_to_console(f"📁 Loaded cloned source from config: {self.source_repos[saved_cloned_source]['name']}")
        elif detected_source:
            self.log_to_console(f"🔍 Detected cloned source: {self.source_repos[detected_source]['name']}")
        
        for key, repo in self.source_repos.items():
            repo_dir = os.path.join(git_source_dir, repo["folder"])
            if os.path.exists(repo_dir):
                # Check if it's a valid Git repository (has .git folder)
                git_dir = os.path.join(repo_dir, ".git")
                if os.path.exists(git_dir) and os.path.isdir(git_dir):
                    # Only show as cloned if this is the detected source type
                    if key == cloned_source:
                        self.update_source_status(key, "✅", "Cloned")
                        self.log_to_console(f"✅ Found existing {repo['name']} repository: {repo_dir}")
                        # Enable Update button for cloned repositories
                        self.source_widgets[key]["update_button"].config(state="normal")
                    else:
                        # This source exists but is not the active one - show as not cloned
                        self.update_source_status(key, "⏳", "Not Cloned")
                        self.log_to_console(f"⚠️ Found {repo['name']} but it's not the active source")
                        # Disable Update button for non-active sources
                        self.source_widgets[key]["update_button"].config(state="disabled")
                else:
                    # Directory exists but not a valid Git repository - show as not cloned
                    self.update_source_status(key, "⏳", "Not Cloned")
                    self.log_to_console(f"⚠️ Found directory for {repo['name']} but not a valid Git repository: {repo_dir}")
                    # Disable Update button for invalid repositories
                    self.source_widgets[key]["update_button"].config(state="disabled")
            else:
                # Special handling for custom source
                if key == "custom":
                    if repo["url"]:
                        self.update_source_status(key, "⏳", "URL Set")
                        self.log_to_console(f"🔗 Custom source has URL set: {repo['url']}")
                    else:
                        self.update_source_status(key, "⏳", "No URL")
                        self.log_to_console(f"⏳ Custom source - no URL set")
                else:
                    self.update_source_status(key, "⏳", "Not Cloned")
                    self.log_to_console(f"⏳ {repo['name']} repository not found: {repo_dir}")
                
                # Disable Update button for non-existent repositories
                self.source_widgets[key]["update_button"].config(state="disabled")
        
        if cloned_source:
            self.log_to_console(f"✅ Active source: {self.source_repos[cloned_source]['name']}")
        else:
            self.log_to_console("⚠️ No active AzerothCore source detected")
        
        self.log_to_console("✅ Source repository status check completed")
    
    def log_to_console(self, message):
        """Log a message to the console with timestamp"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        # Add message to console
        self.console_text.insert(tk.END, formatted_message)
        self.console_text.see(tk.END)  # Auto-scroll to bottom
        
        # Write to log file if available
        if hasattr(self, 'log_file_path') and self.log_file_path:
            try:
                with open(self.log_file_path, 'a', encoding='utf-8') as f:
                    f.write(formatted_message)
                    f.flush()  # Ensure data is written immediately
            except Exception as e:
                # If file writing fails, continue without it
                print(f"Warning: Could not write to log file: {str(e)}")
        
        # Also print to terminal for debugging
        try:
            print(formatted_message.strip())
        except UnicodeEncodeError:
            # Fallback for Windows console encoding issues
            safe_message = formatted_message.encode('ascii', 'replace').decode('ascii')
            print(safe_message.strip())
    
    def clear_console(self):
        """Clear the console text"""
        self.console_text.delete(1.0, tk.END)
        self.log_to_console("Console cleared")
    
    def save_console_log(self):
        """Save console log to a file in the logs folder"""
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"acb_console_log_{timestamp}.txt"
            
            # Save to logs folder if available, otherwise save to current directory
            if hasattr(self, 'logs_dir') and self.logs_dir:
                filepath = os.path.join(self.logs_dir, filename)
            else:
                filepath = filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.console_text.get(1.0, tk.END))
            
            self.log_to_console(f"Console log saved to: {filepath}")
            messagebox.showinfo("Log Saved", f"Console log has been saved to:\n{filepath}")
            
        except Exception as e:
            self.log_to_console(f"Error saving log: {str(e)}")
            messagebox.showerror("Error", f"Failed to save console log:\n{str(e)}")
    
    def open_logs_folder(self):
        """Open the logs folder in file explorer"""
        try:
            if hasattr(self, 'logs_dir') and self.logs_dir and os.path.exists(self.logs_dir):
                import subprocess
                subprocess.Popen(['explorer', self.logs_dir], shell=True)
                self.log_to_console(f"📁 Opened logs folder: {self.logs_dir}")
            else:
                messagebox.showwarning("Logs Folder Not Found", 
                                     "Logs folder not found. Please ensure the application has been started at least once.")
                self.log_to_console("❌ Logs folder not found")
        except Exception as e:
            self.log_to_console(f"❌ Error opening logs folder: {str(e)}")
            messagebox.showerror("Error", f"Failed to open logs folder:\n{str(e)}")
    
    def _cleanup_old_logs(self, max_logs=50):
        """Clean up old log files to prevent the logs folder from growing too large"""
        try:
            if not hasattr(self, 'logs_dir') or not self.logs_dir or not os.path.exists(self.logs_dir):
                return
            
            # Get all log files
            log_files = []
            for filename in os.listdir(self.logs_dir):
                if filename.startswith('acb_session_') and filename.endswith('.log'):
                    filepath = os.path.join(self.logs_dir, filename)
                    if os.path.isfile(filepath):
                        # Get file modification time
                        mtime = os.path.getmtime(filepath)
                        log_files.append((filepath, mtime))
            
            # Sort by modification time (newest first)
            log_files.sort(key=lambda x: x[1], reverse=True)
            
            # Remove old files if we have more than max_logs
            if len(log_files) > max_logs:
                files_to_remove = log_files[max_logs:]
                for filepath, _ in files_to_remove:
                    try:
                        os.remove(filepath)
                        print(f"🗑️ Cleaned up old log file: {os.path.basename(filepath)}")
                    except Exception as e:
                        print(f"⚠️ Could not remove old log file {os.path.basename(filepath)}: {str(e)}")
                
                print(f"🧹 Log cleanup completed: removed {len(files_to_remove)} old log files")
            
        except Exception as e:
            print(f"⚠️ Error during log cleanup: {str(e)}")
    
    def _test_logging_after_ui(self):
        """Test logging system after UI is ready"""
        try:
            if hasattr(self, 'log_file_path') and self.log_file_path:
                print("[SUCCESS] Logging system is ready - all console output will be saved to log file")
            else:
                print("[WARNING] Logging system not available - no log file path")
        except Exception as e:
            print(f"[ERROR] Logging test error: {str(e)}")
    
    def scan_system(self):
        """Scan the system for all requirements"""
        self.scan_button.config(state="disabled")
        self.progress.config(value=0)  # Start at 0%
        self.status_label.config(text="Scanning system for requirements...")
        self.log_to_console("Starting system requirements scan...")
        
        # Run scan in separate thread to avoid blocking UI
        scan_thread = threading.Thread(target=self._perform_scan)
        scan_thread.daemon = True
        scan_thread.start()
        
    def _perform_scan(self):
        """Perform the actual system scan"""
        try:
            total_requirements = len(self.requirements)
            for i, (key, req) in enumerate(self.requirements.items(), 1):
                # Update progress
                progress_percentage = int((i / total_requirements) * 100)
                self.root.after(0, lambda p=progress_percentage: self.progress.config(value=p))
                
                self.root.after(0, lambda k=key: self.update_status(k, "⏳", "Checking...", ""))
                self.root.after(0, lambda k=key: self.log_to_console(f"Checking requirement: {req['name']}"))
                
                # Check if requirement is detected
                detected, path, version = self.check_requirement(req)
                
                req["detected"] = detected
                req["path"] = path
                req["version"] = version
                
                # Update UI and log result
                if detected:
                    self.root.after(0, lambda k=key, p=path, v=version: 
                                  self.update_status(k, "✅", "Detected", f"{v}\n{p}"))
                    self.root.after(0, lambda k=key, p=path, v=version: 
                                  self.log_to_console(f"✅ {req['name']} detected: {v} at {p}"))
                else:
                    self.root.after(0, lambda k=key: 
                                  self.update_status(k, "❌", "Not Found", ""))
                    self.root.after(0, lambda k=key: 
                                  self.log_to_console(f"❌ {req['name']} not found"))
                
            self.root.after(0, self._scan_complete)
            
        except Exception as e:
            self.root.after(0, lambda: self._scan_error(str(e)))
    
    def check_requirement(self, req):
        """Check if a specific requirement is met"""
        detected = False
        path = ""
        version = ""
        
        # Check common paths first
        for common_path in req["common_paths"]:
            if os.path.exists(common_path):
                detected = True
                path = common_path
                break
        
        # Check registry if not found in common paths
        if not detected and req["registry_keys"]:
            for reg_key in req["registry_keys"]:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_key) as key:
                        install_path, _ = winreg.QueryValueEx(key, "InstallLocation")
                        if install_path and os.path.exists(install_path):
                            detected = True
                            path = install_path
                            break
                except (FileNotFoundError, OSError):
                    continue
        
        # Check PATH environment variable
        if not detected:
            path_dirs = os.environ.get('PATH', '').split(os.pathsep)
            for path_dir in path_dirs:
                if req["name"].lower() in path_dir.lower():
                    potential_path = os.path.join(path_dir, f"{req['name'].lower()}.exe")
                    if os.path.exists(potential_path):
                        detected = True
                        path = potential_path
                        break
        
        # Try to get version if command is available
        if detected and req["version_check"]:
            try:
                result = subprocess.run(req["version_check"], shell=True, 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    version = result.stdout.strip()
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                version = "Version check failed"
        
        # Special handling for Visual Studio
        if req["name"] == "Visual Studio 2022" and detected:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   r"SOFTWARE\Microsoft\VisualStudio\Setup\VS") as key:
                    version, _ = winreg.QueryValueEx(key, "Version")
            except (FileNotFoundError, OSError):
                version = "2022 (detected)"
        
        return detected, path, version
    
    def update_status(self, key, icon, status, info):
        """Update the status display for a requirement"""
        widgets = self.req_widgets[key]
        widgets["status_icon"].config(text=icon)
        widgets["status_text"].config(text=status)
        widgets["version_var"].set(info)
        
        # Update colors based on status
        if icon == "✅":
            widgets["status_text"].config(foreground="green")
        elif icon == "❌":
            widgets["status_text"].config(foreground="red")
        else:
            widgets["status_text"].config(foreground="black")
    
    def _scan_complete(self):
        """Called when scan is complete"""
        self.progress.config(value=0)  # Reset to 0%
        self.scan_button.config(state="normal")
        self.status_label.config(text="System scan completed!")
        
        # Show summary
        detected_count = sum(1 for req in self.requirements.values() if req["detected"])
        total_count = len(self.requirements)
        
        self.log_to_console(f"System scan completed! {detected_count}/{total_count} requirements detected")
        
        if detected_count == total_count:
            messagebox.showinfo("Scan Complete", 
                              f"✅ All requirements detected! ({detected_count}/{total_count})\n\n"
                              "Your system is ready to build AzerothCore!")
            self.log_to_console("🎉 All requirements are satisfied - system ready for AzerothCore build!")
        else:
            messagebox.showwarning("Scan Complete", 
                                 f"⚠️ {detected_count}/{total_count} requirements detected.\n\n"
                                 "Some requirements are missing. Use the 'Set Path' buttons to specify "
                                 "manual paths for missing software.")
            self.log_to_console(f"⚠️ {total_count - detected_count} requirements missing - manual setup required")
    
    def _scan_error(self, error_msg):
        """Called when scan encounters an error"""
        self.progress.config(value=0)  # Reset to 0%
        self.scan_button.config(state="normal")
        self.status_label.config(text=f"Scan failed: {error_msg}")
        self.log_to_console(f"❌ Scan error occurred: {error_msg}")
        messagebox.showerror("Scan Error", f"An error occurred during scanning:\n{error_msg}")
    
    def set_manual_path(self, key):
        """Set manual path for a requirement"""
        req = self.requirements[key]
        current_path = req.get("path", "")
        
        self.log_to_console(f"📁 Opening manual path dialog for {req['name']}")
        if current_path:
            self.log_to_console(f"📁 Current path: {current_path}")
        
        # Create dialog for manual path input
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Set Path for {req['name']}")
        dialog.geometry("500x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Path input
        ttk.Label(dialog, text=f"Enter the path to {req['name']}:").pack(pady=(20, 5))
        
        path_var = tk.StringVar(value=current_path)
        path_entry = ttk.Entry(dialog, textvariable=path_var, width=60)
        path_entry.pack(pady=(0, 10))
        
        # Browse button
        def browse():
            self.log_to_console(f"🔍 Opening file browser for {req['name']}")
            folder = filedialog.askdirectory(title=f"Select {req['name']} directory")
            if folder:
                path_var.set(folder)
                self.log_to_console(f"📁 Selected directory: {folder}")
            else:
                self.log_to_console(f"❌ File browser cancelled for {req['name']}")
        
        ttk.Button(dialog, text="Browse", command=browse).pack(pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack()
        
        def save_path():
            new_path = path_var.get().strip()
            self.log_to_console(f"💾 Attempting to save path for {req['name']}: {new_path}")
            
            if new_path and os.path.exists(new_path):
                req["path"] = new_path
                req["detected"] = True
                req["version"] = "Manual path set"
                self.update_status(key, "✅", "Manual Path", f"Manual path set\n{new_path}")
                self.log_to_console(f"✅ Successfully set manual path for {req['name']}: {new_path}")
                dialog.destroy()
                messagebox.showinfo("Success", f"Path for {req['name']} has been set!")
            else:
                self.log_to_console(f"❌ Invalid path for {req['name']}: {new_path}")
                messagebox.showerror("Invalid Path", "Please enter a valid path that exists.")
        
        def cancel_path():
            self.log_to_console(f"❌ Manual path setting cancelled for {req['name']}")
            dialog.destroy()
        
        ttk.Button(button_frame, text="Save", command=save_path).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=cancel_path).pack(side=tk.LEFT)
        
        # Focus on path entry
        path_entry.focus_set()
    
    def browse_path(self, key):
        """Browse for a requirement's path"""
        req = self.requirements[key]
        
        self.log_to_console(f"🔍 Opening browse dialog for {req['name']}")
        
        if req["name"] == "Visual Studio 2022":
            self.log_to_console(f"📁 Browsing for Visual Studio 2022 installation directory")
            folder = filedialog.askdirectory(title=f"Select {req['name']} installation directory")
        else:
            # For executables, try to find the main executable
            self.log_to_console(f"📁 Browsing for {req['name']} executable file")
            file_path = filedialog.askopenfilename(
                title=f"Select {req['name']} executable",
                filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
            )
            if file_path:
                folder = os.path.dirname(file_path)
                self.log_to_console(f"📁 Selected executable: {file_path}")
                self.log_to_console(f"📁 Extracted directory: {folder}")
            else:
                self.log_to_console(f"❌ File browser cancelled for {req['name']}")
                return
        
        if folder:
            req["path"] = folder
            req["detected"] = True
            req["version"] = "Path selected via browse"
            self.update_status(key, "✅", "Path Selected", f"Path selected via browse\n{folder}")
            self.log_to_console(f"✅ Successfully set path for {req['name']} via browse: {folder}")
            messagebox.showinfo("Success", f"Path for {req['name']} has been set!")
        else:
            self.log_to_console(f"❌ No path selected for {req['name']}")
            messagebox.showwarning("No Path Selected", f"No path was selected for {req['name']}.")
    
    def save_paths(self):
        """Save all current paths to a configuration file"""
        self.log_to_console("💾 Starting to save all configured paths...")
        
        config = {}
        saved_count = 0
        for key, req in self.requirements.items():
            if req["path"]:
                config[key] = {
                    "path": req["path"],
                    "detected": req["detected"],
                    "version": req["version"]
                }
                saved_count += 1
                self.log_to_console(f"📁 Saving path for {req['name']}: {req['path']}")
        
        self.log_to_console(f"📊 Total paths to save: {saved_count}")
        
        try:
            config_file = os.path.join(self._get_app_dir(), "acb_config.json")
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.log_to_console(f"✅ Configuration successfully saved to: {config_file}")
            messagebox.showinfo("Success", f"Configuration saved to:\n{config_file}")
        except Exception as e:
            self.log_to_console(f"❌ Failed to save configuration: {str(e)}")
            messagebox.showerror("Error", f"Failed to save configuration:\n{str(e)}")
    
    def load_saved_paths(self):
        """Load previously saved paths"""
        self.log_to_console("📂 Attempting to load saved configuration...")
        
        try:
            config_file = os.path.join(self._get_app_dir(), "acb_config.json")
            if os.path.exists(config_file):
                self.log_to_console(f"📁 Found configuration file: {config_file}")
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                loaded_count = 0
                for key, data in config.items():
                    if key in self.requirements:
                        self.requirements[key].update(data)
                        if data["detected"]:
                            self.update_status(key, "✅", "Loaded", 
                                            f"{data.get('version', '')}\n{data['path']}")
                            loaded_count += 1
                            self.log_to_console(f"📁 Loaded path for {self.requirements[key]['name']}: {data['path']}")
                
                self.log_to_console(f"✅ Successfully loaded {loaded_count} saved paths")
            else:
                self.log_to_console("📁 No saved configuration file found - starting fresh")
        except Exception as e:
            self.log_to_console(f"❌ Failed to load saved configuration: {str(e)}")
            print(f"Failed to load saved configuration: {e}")
    
    def clear_all_paths(self):
        """Clear all manually set paths"""
        if messagebox.askyesno("Clear All Paths", 
                              "Are you sure you want to clear all manually set paths?"):
            self.log_to_console("🗑️ User confirmed clearing all paths - starting cleanup...")
            
            cleared_count = 0
            for key, req in self.requirements.items():
                if req["path"]:
                    self.log_to_console(f"🗑️ Clearing path for {req['name']}: {req['path']}")
                    req["path"] = ""
                    req["detected"] = False
                    req["version"] = ""
                    self.update_status(key, "⏳", "Not Checked", "")
                    cleared_count += 1
            
            self.log_to_console(f"📊 Cleared {cleared_count} paths")
            
            # Remove config file
            config_file = os.path.join(self._get_app_dir(), "acb_config.json")
            if os.path.exists(config_file):
                try:
                    os.remove(config_file)
                    self.log_to_console(f"🗑️ Removed configuration file: {config_file}")
                except Exception as e:
                    self.log_to_console(f"❌ Failed to remove config file: {str(e)}")
            
            self.log_to_console("✅ All paths and configuration cleared successfully")
            messagebox.showinfo("Cleared", "All paths have been cleared!")
        else:
            self.log_to_console("❌ User cancelled clearing all paths")
    
    def update_download_urls(self):
        """Open manual URL configuration window"""
        self.log_to_console("🔗 Opening URL configuration dialog...")
        self.create_url_config_dialog()
    
    def create_url_config_dialog(self):
        """Create the URL configuration dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Configure Download URLs")
        dialog.geometry("700x500")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(True, True)
        
        # Center dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Title
        title_label = ttk.Label(dialog, text="Configure Download URLs for Dependencies", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(20, 10))
        
        # Description
        desc_label = ttk.Label(dialog, 
                              text="Set custom download URLs for each dependency. Leave empty to use default URLs.",
                              wraplength=600)
        desc_label.pack(pady=(0, 20))
        
        # Create scrollable frame for requirements
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # URL configuration entries
        self.url_entries = {}
        
        for i, (key, req) in enumerate(self.requirements.items()):
            # Requirement frame
            req_frame = ttk.LabelFrame(scrollable_frame, text=req["name"], padding="10")
            req_frame.pack(fill="x", padx=20, pady=5)
            
            # Current URL label
            current_label = ttk.Label(req_frame, text=f"Current: {req['download_url']}", 
                                    font=("Arial", 8), foreground="gray")
            current_label.pack(anchor="w", pady=(0, 5))
            
            # URL entry
            url_var = tk.StringVar(value=req["download_url"])
            url_entry = ttk.Entry(req_frame, textvariable=url_var, width=80)
            url_entry.pack(fill="x", pady=(0, 5))
            
            # Store reference
            self.url_entries[key] = url_var
            
            # Buttons frame
            button_frame = ttk.Frame(req_frame)
            button_frame.pack(fill="x")
            
            # Reset to default button
            def reset_to_default(k=key):
                default_url = self._get_default_url(k)
                self.url_entries[k].set(default_url)
            
            reset_button = ttk.Button(button_frame, text="Reset to Default", 
                                    command=reset_to_default)
            reset_button.pack(side=tk.LEFT, padx=(0, 10))
            
            # Test URL button
            def test_url(k=key):
                url = self.url_entries[k].get().strip()
                if url:
                    self._test_url(k, url)
                else:
                    messagebox.showwarning("Empty URL", f"Please enter a URL for {k}")
            
            test_button = ttk.Button(button_frame, text="Test URL", 
                                   command=test_url)
            test_button.pack(side=tk.LEFT)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0))
        scrollbar.pack(side="right", fill="y")
        
        # Buttons frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        # Save button
        def save_urls():
            self._save_custom_urls()
            dialog.destroy()
            messagebox.showinfo("Success", "Custom download URLs have been saved!")
        
        save_button = ttk.Button(button_frame, text="💾 Save URLs", 
                               command=save_urls, style="Accent.TButton")
        save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        cancel_button = ttk.Button(dialog, text="Cancel", 
                                 command=dialog.destroy)
        cancel_button.pack(side=tk.LEFT)
        
        # Configure canvas scrolling
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
    
    def _get_default_url(self, key):
        """Get the default URL for a dependency"""
        default_urls = {
            "Git": "https://github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/Git-2.44.0-64-bit.exe",
            "Boost": "https://boostorg.jfrog.io/artifactory/main/release/1.85.0/source/boost_1_85_0.zip",
            "MySQL": "https://dev.mysql.com/get/Downloads/MySQL-8.4/mysql-8.4.0-winx64.zip",
            "OpenSSL": "https://slproweb.com/download/Win64OpenSSL-3_5_2.exe",
            "CMake": "https://github.com/CMake/CMake/releases/download/v3.28.1/cmake-3.28.1-windows-x86_64.zip",
            "VisualStudio": "https://aka.ms/vs/17/release/vs_community.exe",
            "HeidiSQL": "https://www.heidisql.com/downloads/releases/HeidiSQL_12.11_32_Portable.zip"
        }
        return default_urls.get(key, "")
    
    def _test_url(self, key, url):
        """Test if a URL is accessible"""
        try:
            import urllib.request
            with urllib.request.urlopen(url, timeout=10) as response:
                if response.status == 200:
                    file_size = response.headers.get('content-length', 'Unknown')
                    if file_size != 'Unknown':
                        file_size = f"{int(file_size) / (1024*1024):.1f} MB"
                    messagebox.showinfo("URL Test", 
                                      f"✅ URL is accessible!\n\n"
                                      f"File size: {file_size}\n"
                                      f"Status: {response.status}")
                else:
                    messagebox.showwarning("URL Test", 
                                         f"⚠️ URL returned status: {response.status}")
        except Exception as e:
            messagebox.showerror("URL Test", 
                               f"❌ URL test failed:\n{str(e)}")
    
    def _save_custom_urls(self):
        """Save custom download URLs to config file"""
        custom_urls = {}
        
        for key, url_var in self.url_entries.items():
            url = url_var.get().strip()
            if url:  # Only save non-empty URLs
                custom_urls[key] = url
                # Update the requirements dictionary
                self.requirements[key]["download_url"] = url
        
        # Save to config file
        try:
            config_file = os.path.join(self._get_app_dir(), "acb_urls_config.json")
            with open(config_file, 'w') as f:
                json.dump(custom_urls, f, indent=2)
            
            print(f"Custom URLs saved to: {config_file}")
        except Exception as e:
            print(f"Failed to save custom URLs: {e}")
    
    def _load_custom_urls(self):
        """Load custom download URLs from config file"""
        try:
            config_file = os.path.join(self._get_app_dir(), "acb_urls_config.json")
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    custom_urls = json.load(f)
                
                # Update requirements with custom URLs
                for key, url in custom_urls.items():
                    if key in self.requirements:
                        self.requirements[key]["download_url"] = url
                        print(f"Loaded custom URL for {key}: {url}")
        except Exception as e:
            print(f"Failed to load custom URLs: {e}")
    
    def install_dependency(self, key):
        """Start the installation process for a dependency"""
        req = self.requirements[key]
        
        if req["detected"]:
            if messagebox.askyesno("Already Installed", 
                                  f"{req['name']} is already detected on your system.\n\n"
                                  f"Current path: {req['path']}\n\n"
                                  "Do you want to reinstall it?"):
                self.log_to_console(f"🔄 User chose to reinstall {req['name']}")
                pass
            else:
                self.log_to_console(f"❌ Installation of {req['name']} cancelled by user")
                return
        
        # Create installation dialog
        self.log_to_console(f"🚀 Starting installation process for {req['name']}")
        self.create_install_dialog(key, req)
    
    def create_install_dialog(self, key, req):
        """Create the installation dialog with download progress"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Installing {req['name']}")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 150, self.root.winfo_rooty() + 150))
        
        # Title
        title_label = ttk.Label(dialog, text=f"Installing {req['name']}", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(20, 10))
        
        # Status label
        status_label = ttk.Label(dialog, text="Preparing download...", font=("Arial", 10))
        status_label.pack(pady=(0, 20))
        
        # Progress bar
        progress = ttk.Progressbar(dialog, mode='determinate', length=400)
        progress.pack(pady=(0, 20))
        
        # Progress text
        progress_text = ttk.Label(dialog, text="0%", font=("Arial", 9))
        progress_text.pack(pady=(0, 20))
        
        # Cancel button
        cancel_button = ttk.Button(dialog, text="Cancel", 
                                  command=lambda: self.cancel_installation(dialog))
        cancel_button.pack(pady=(0, 20))
        
        # Store dialog references and add cancellation flag
        dialog.progress = progress
        dialog.status_label = status_label
        dialog.progress_text = progress_text
        dialog.cancel_button = cancel_button
        dialog.req_key = key  # Store the requirement key for error messages
        dialog.cancelled = False  # Flag to track if dialog was cancelled
        
        # Start download in separate thread
        download_thread = threading.Thread(target=self._download_dependency, 
                                         args=(key, req, dialog))
        download_thread.daemon = True
        download_thread.start()
    
    def _safe_dialog_update(self, dialog, update_func):
        """Safely update dialog widgets, checking if dialog was cancelled"""
        if hasattr(dialog, 'cancelled') and dialog.cancelled:
            return False
        
        try:
            # Check if dialog still exists and is valid
            if dialog.winfo_exists():
                dialog.after(0, update_func)
                return True
        except:
            pass
        return False
    
    def cancel_installation(self, dialog):
        """Cancel the current installation"""
        if messagebox.askyesno("Cancel Installation", 
                              "Are you sure you want to cancel the installation?"):
            dialog.cancelled = True  # Set cancellation flag
            self.log_to_console(f"❌ User cancelled installation for {dialog.req_key}")
            dialog.destroy()
        else:
            self.log_to_console(f"🔄 User chose to continue installation for {dialog.req_key}")
    
    def _download_dependency(self, key, req, dialog):
        """Download the dependency file"""
        try:
            # Try primary URL first
            url = req["download_url"]
            filename = os.path.basename(url)
            
            self.log_to_console(f"📥 Starting download: {filename} from {url}")
            
            # Update status
            if not self._safe_dialog_update(dialog, lambda: dialog.status_label.config(text=f"Downloading {filename}...")):
                self.log_to_console(f"❌ Download cancelled for {req['name']} - dialog was closed")
                return
            
            # Create download directory
            download_dir = os.path.join(self._get_app_dir(), "Downloads")
            os.makedirs(download_dir, exist_ok=True)
            self.log_to_console(f"📁 Created download directory: {download_dir}")
            file_path = os.path.join(download_dir, filename)
            
            # Download with progress
            def progress_callback(block_num, block_size, total_size):
                if total_size > 0:
                    downloaded = block_num * block_size
                    percentage = min(int((downloaded * 100) / total_size), 100)
                    self._safe_dialog_update(dialog, lambda p=percentage: dialog.progress.config(value=p))
                    self._safe_dialog_update(dialog, lambda p=percentage: dialog.progress_text.config(text=f"{p}%"))
            
            # Download the file with timeout
            import socket
            socket.setdefaulttimeout(30)  # 30 second timeout
            urllib.request.urlretrieve(url, file_path, progress_callback)
            
            # Check if cancelled before continuing
            if hasattr(dialog, 'cancelled') and dialog.cancelled:
                return
            
            # Update status
            if not self._safe_dialog_update(dialog, lambda: dialog.status_label.config(text="Download completed! Starting installation...")):
                return
            if not self._safe_dialog_update(dialog, lambda: dialog.progress.config(value=100)):
                return
            if not self._safe_dialog_update(dialog, lambda: dialog.progress_text.config(text="100%")):
                return
            
            # Wait a moment to show completion
            import time
            time.sleep(1)
            
            # Check if cancelled again before prompting
            if hasattr(dialog, 'cancelled') and dialog.cancelled:
                return
            
            # Ask user to proceed with installation
            if not self._safe_dialog_update(dialog, lambda: self._prompt_installation(key, req, file_path, dialog)):
                return
            
        except Exception as e:
            # Try to find the latest release dynamically
            if not self._safe_dialog_update(dialog, lambda: dialog.status_label.config(
                text="Primary URL failed. Searching for latest release...")):
                return
            
            latest_url = self._find_latest_release(key)
            if latest_url and latest_url != req["download_url"]:
                try:
                    if not self._safe_dialog_update(dialog, lambda: dialog.status_label.config(
                        text=f"Found latest release: {os.path.basename(latest_url)}")):
                        return
                    
                    filename = os.path.basename(latest_url)
                    download_dir = os.path.join(self._get_app_dir(), "Downloads")
                    os.makedirs(download_dir, exist_ok=True)
                    file_path = os.path.join(download_dir, filename)
                    
                    # Download with progress
                    def progress_callback(block_num, block_size, total_size):
                        if total_size > 0:
                            downloaded = block_num * block_size
                            percentage = min(int((downloaded * 100) / total_size), 100)
                            self._safe_dialog_update(dialog, lambda p=percentage: dialog.progress.config(value=p))
                            self._safe_dialog_update(dialog, lambda p=percentage: dialog.progress_text.config(text=f"{p}%"))
                    
                    # Set timeout for latest release download
                    import socket
                    socket.setdefaulttimeout(30)  # 30 second timeout
                    urllib.request.urlretrieve(latest_url, file_path, progress_callback)
                    
                    # Check if cancelled before continuing
                    if hasattr(dialog, 'cancelled') and dialog.cancelled:
                        return
                    
                    # Success! Update status and proceed
                    if not self._safe_dialog_update(dialog, lambda: dialog.status_label.config(text="Download completed! Starting installation...")):
                        return
                    if not self._safe_dialog_update(dialog, lambda: dialog.progress.config(value=100)):
                        return
                    if not self._safe_dialog_update(dialog, lambda: dialog.progress_text.config(text="100%")):
                        return
                    
                    import time
                    time.sleep(1)
                    
                    if not self._safe_dialog_update(dialog, lambda: self._prompt_installation(key, req, file_path, dialog)):
                        return
                    return
                    
                except Exception as latest_error:
                    print(f"Latest release download failed: {latest_error}")
            
            # Try alternative URLs if latest release fails
            if self._try_alternative_downloads(key, req, dialog):
                return
            
            # If all alternatives fail, show error
            if not self._safe_dialog_update(dialog, lambda: self._show_download_error(dialog, str(e))):
                return
    
    def _try_alternative_downloads(self, key, req, dialog):
        """Try alternative download URLs if primary fails"""
        alternative_urls = self._get_alternative_urls(key)
        
        if not alternative_urls:
            return False
        
        if not self._safe_dialog_update(dialog, lambda: dialog.status_label.config(
            text=f"Primary URL failed. Trying {len(alternative_urls)} alternative(s)...")):
            return False
        
        for i, alt_url in enumerate(alternative_urls, 1):
            try:
                if not self._safe_dialog_update(dialog, lambda u=alt_url, idx=i, total=len(alternative_urls): 
                           dialog.status_label.config(
                               text=f"Trying alternative {idx}/{total}: {os.path.basename(u)}...")):
                    return False
                
                filename = os.path.basename(alt_url)
                download_dir = os.path.join(self._get_app_dir(), "Downloads")
                os.makedirs(download_dir, exist_ok=True)
                file_path = os.path.join(download_dir, filename)
                
                # Download with progress
                def progress_callback(block_num, block_size, total_size):
                    if total_size > 0:
                        downloaded = block_num * block_size
                        percentage = min(int((downloaded * 100) / total_size), 100)
                        self._safe_dialog_update(dialog, lambda p=percentage: dialog.progress.config(value=p))
                        self._safe_dialog_update(dialog, lambda p=percentage: dialog.progress_text.config(text=f"{p}%"))
                
                # Set timeout for alternative downloads
                import socket
                socket.setdefaulttimeout(30)  # 30 second timeout
                urllib.request.urlretrieve(alt_url, file_path, progress_callback)
                
                # Check if cancelled before continuing
                if hasattr(dialog, 'cancelled') and dialog.cancelled:
                    return False
                
                # Success! Update status and proceed
                if not self._safe_dialog_update(dialog, lambda: dialog.status_label.config(text="Download completed! Starting installation...")):
                    return False
                if not self._safe_dialog_update(dialog, lambda: dialog.progress.config(value=100)):
                    return False
                if not self._safe_dialog_update(dialog, lambda: dialog.progress_text.config(text="100%")):
                    return False
                
                import time
                time.sleep(1)
                
                if not self._safe_dialog_update(dialog, lambda: self._prompt_installation(key, req, file_path, dialog)):
                    return False
                return True
                
            except Exception as e:
                # Log the error but continue to next alternative
                print(f"Alternative URL {i} failed: {str(e)}")
                continue
        
        return False
    
    def _get_alternative_urls(self, key):
        """Get alternative download URLs for a dependency"""
        # Since we now have dynamic latest release detection, 
        # alternative URLs are only used as a final fallback
        alternatives = {
            "Git": [
                "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe",
                "https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0-64-bit.exe"
            ],
            "MySQL": [
                "https://dev.mysql.com/get/Downloads/MySQL-8.3/mysql-8.3.0-winx64.zip",
                "https://dev.mysql.com/get/Downloads/MySQL-8.2/mysql-8.2.0-winx64.zip"
            ],
            "OpenSSL": [
                "https://slproweb.com/download/Win64OpenSSL-3_5_1.exe",
                "https://slproweb.com/download/Win64OpenSSL-3_5_0.exe",
                "https://slproweb.com/download/Win64OpenSSL-3_4_4.exe"
            ],
            "CMake": [
                "https://github.com/Kitware/CMake/releases/download/v3.28.0/cmake-3.28.0-windows-x86_64.zip",
                "https://github.com/Kitware/CMake/releases/download/v3.27.7/cmake-3.27.7-windows-x86_64.zip"
            ],
            "Boost": [
                "https://boostorg.jfrog.io/artifactory/main/release/1.84.0/source/boost_1_84_0.zip",
                "https://boostorg.jfrog.io/artifactory/main/release/1.83.0/source/boost_1_83_0.zip"
            ],
            "VisualStudio": [
                "https://aka.ms/vs/17/release/vs_professional.exe",
                "https://aka.ms/vs/17/release/vs_enterprise.exe",
                "https://aka.ms/vs/16/release/vs_community.exe"
            ],
            "HeidiSQL": [
                "https://www.heidisql.com/downloads/releases/HeidiSQL_12.11_32_Portable.zip"
            ]
        }
        
        return alternatives.get(key, [])
    
    def _find_latest_release(self, key):
        """Dynamically find the latest release URL for a dependency"""
        try:
            if key == "Git":
                return self._find_latest_git()
            elif key == "OpenSSL":
                return self._find_latest_openssl()
            elif key == "CMake":
                return self._find_latest_cmake()
            elif key == "MySQL":
                return self._find_latest_mysql()
            elif key == "Boost":
                return self._find_latest_boost()
            elif key == "VisualStudio":
                return self._find_latest_visualstudio()
            elif key == "HeidiSQL":
                return self._find_latest_heidisql()
            else:
                return None
        except Exception as e:
            print(f"Error finding latest release for {key}: {e}")
            return None
    
    def _find_latest_git(self):
        """Find latest Git for Windows release"""
        try:
            import urllib.request
            import json
            
            # Get latest release info from GitHub API
            api_url = "https://api.github.com/repos/git-for-windows/git/releases/latest"
            with urllib.request.urlopen(api_url, timeout=10) as response:
                data = json.loads(response.read().decode())
                
            # Find the 64-bit Windows installer
            for asset in data.get('assets', []):
                if '64-bit.exe' in asset['name']:
                    return asset['browser_download_url']
            
            return None
        except Exception as e:
            print(f"Error finding latest Git: {e}")
            return None
    
    def _find_latest_openssl(self):
        """Find latest OpenSSL release"""
        try:
            # Try multiple OpenSSL versions in order of preference (newest first)
            openssl_versions = [
                "https://slproweb.com/download/Win64OpenSSL-3_5_2.exe",
                "https://slproweb.com/download/Win64OpenSSL-3_5_1.exe",
                "https://slproweb.com/download/Win64OpenSSL-3_5_0.exe",
                "https://slproweb.com/download/Win64OpenSSL-3_4_4.exe",
                "https://slproweb.com/download/Win64OpenSSL-3_4_3.exe",
                "https://slproweb.com/download/Win64OpenSSL-3_4_2.exe",
                "https://slproweb.com/download/Win64OpenSSL-3_4_1.exe",
                "https://slproweb.com/download/Win64OpenSSL-3_4_0.exe",
                "https://slproweb.com/download/Win64OpenSSL-3_3_2.exe",
                "https://slproweb.com/download/Win64OpenSSL-3_3_1.exe",
                "https://slproweb.com/download/Win64OpenSSL-3_3_0.exe",
                "https://slproweb.com/download/Win64OpenSSL-3_2_2.exe",
                "https://slproweb.com/download/Win64OpenSSL-3_2_1.exe",
                "https://slproweb.com/download/Win64OpenSSL-3_2_0.exe",
                "https://slproweb.com/download/Win64OpenSSL-3_1_5.exe",
                "https://slproweb.com/download/Win64OpenSSL-3_1_4.exe", 
                "https://slproweb.com/download/Win64OpenSSL-3_1_3.exe",
                "https://slproweb.com/download/Win64OpenSSL-3_1_2.exe",
                "https://slproweb.com/download/Win64OpenSSL-3_1_1.exe",
                "https://slproweb.com/download/Win64OpenSSL-3_0_12.exe",
                "https://slproweb.com/download/Win64OpenSSL-3_0_11.exe",
                "https://slproweb.com/download/Win64OpenSSL-3_0_10.exe"
            ]
            
            # Test each URL to see if it's accessible
            for url in openssl_versions:
                try:
                    import urllib.request
                    with urllib.request.urlopen(url, timeout=5) as response:
                        if response.status == 200:
                            print(f"OpenSSL: Found working URL: {url}")
                            return url
                except Exception as e:
                    print(f"OpenSSL: URL {url} failed: {e}")
                    continue
            
            # If none work, return the first one as fallback
            print(f"OpenSSL: No working URLs found, using fallback: {openssl_versions[0]}")
            return openssl_versions[0]
            
        except Exception as e:
            print(f"Error finding latest OpenSSL: {e}")
            return None
    
    def _find_latest_cmake(self):
        """Find latest CMake release"""
        try:
            import urllib.request
            import json
            
            # Get latest release info from GitHub API
            api_url = "https://api.github.com/repos/Kitware/CMake/releases/latest"
            with urllib.request.urlopen(api_url, timeout=10) as response:
                data = json.loads(response.read().decode())
                
            # Find the Windows x64 ZIP
            for asset in data.get('assets', []):
                if 'windows-x86_64.zip' in asset['name']:
                    return asset['browser_download_url']
            
            return None
        except Exception as e:
            print(f"Error finding latest CMake: {e}")
            return None
    
    def _find_latest_mysql(self):
        """Find latest MySQL release"""
        try:
            # Try multiple MySQL ZIP versions in order of preference (newest first)
            mysql_versions = [
                "https://dev.mysql.com/get/Downloads/MySQL-8.4/mysql-8.4.0-winx64.zip",
                "https://dev.mysql.com/get/Downloads/MySQL-8.3/mysql-8.3.0-winx64.zip",
                "https://dev.mysql.com/get/Downloads/MySQL-8.2/mysql-8.2.0-winx64.zip",
                "https://dev.mysql.com/get/Downloads/MySQL-8.1/mysql-8.1.0-winx64.zip",
                "https://dev.mysql.com/get/Downloads/MySQL-8.0/mysql-8.0.36-winx64.zip",
                "https://dev.mysql.com/get/Downloads/MySQL-8.0/mysql-8.0.35-winx64.zip",
                "https://dev.mysql.com/get/Downloads/MySQL-8.0/mysql-8.0.34-winx64.zip"
            ]
            
            # Test each URL to see if it's accessible
            for url in mysql_versions:
                try:
                    import urllib.request
                    with urllib.request.urlopen(url, timeout=5) as response:
                        if response.status == 200:
                            print(f"MySQL: Found working URL: {url}")
                            return url
                except Exception as e:
                    print(f"MySQL: URL {url} failed: {e}")
                    continue
            
            # If none work, return the first one as fallback
            print(f"MySQL: No working URLs found, using fallback: {mysql_versions[0]}")
            return mysql_versions[0]
            
        except Exception as e:
            print(f"Error finding latest MySQL: {e}")
            return None
    
    def _find_latest_boost(self):
        """Find latest Boost release"""
        try:
            # Try multiple Boost versions in order of preference (newest first)
            boost_versions = [
                "https://boostorg.jfrog.io/artifactory/main/release/1.85.0/source/boost_1_85_0.zip",
                "https://boostorg.jfrog.io/artifactory/main/release/1.84.0/source/boost_1_84_0.zip",
                "https://boostorg.jfrog.io/artifactory/main/release/1.83.0/source/boost_1_83_0.zip",
                "https://boostorg.jfrog.io/artifactory/main/release/1.82.0/source/boost_1_82_0.zip",
                "https://boostorg.jfrog.io/artifactory/main/release/1.81.0/source/boost_1_81_0.zip",
                "https://boostorg.jfrog.io/artifactory/main/release/1.80.0/source/boost_1_80_0.zip",
                "https://boostorg.jfrog.io/artifactory/main/release/1.79.0/source/boost_1_79_0.zip",
                "https://boostorg.jfrog.io/artifactory/main/release/1.78.0/source/boost_1_78_0.zip"
            ]
            
            # Test each URL to see if it's accessible
            for url in boost_versions:
                try:
                    import urllib.request
                    with urllib.request.urlopen(url, timeout=5) as response:
                        if response.status == 200:
                            print(f"Boost: Found working URL: {url}")
                            return url
                except Exception as e:
                    print(f"Boost: URL {url} failed: {e}")
                    continue
            
            # If none work, return the first one as fallback
            print(f"Boost: No working URLs found, using fallback: {boost_versions[0]}")
            return boost_versions[0]
            
        except Exception as e:
            print(f"Error finding latest Boost: {e}")
            return None
    
    def _find_latest_visualstudio(self):
        """Find latest Visual Studio release"""
        try:
            # Try multiple Visual Studio versions in order of preference (newest first)
            vs_versions = [
                "https://aka.ms/vs/17/release/vs_community.exe",
                "https://aka.ms/vs/17/release/vs_professional.exe",
                "https://aka.ms/vs/17/release/vs_enterprise.exe",
                "https://aka.ms/vs/16/release/vs_community.exe"
            ]
            
            # Test each URL to see if it's accessible
            for url in vs_versions:
                try:
                    import urllib.request
                    with urllib.request.urlopen(url, timeout=5) as response:
                        if response.status == 200:
                            print(f"Visual Studio: Found working URL: {url}")
                            return url
                except Exception as e:
                    print(f"Visual Studio: URL {url} failed: {e}")
                    continue
            
            # If none work, return the first one as fallback
            print(f"Visual Studio: No working URLs found, using fallback: {vs_versions[0]}")
            return vs_versions[0]
            
        except Exception as e:
            print(f"Error finding latest Visual Studio: {e}")
            return None
    
    def _find_latest_heidisql(self):
        """Find latest HeidiSQL release - same approach as MySQL and OpenSSL (hardcoded working URLs)"""
        try:
            # Use the working hardcoded URL - same as MySQL and OpenSSL do
            working_url = "https://www.heidisql.com/downloads/releases/HeidiSQL_12.11_32_Portable.zip"
            
            # Verify the URL is accessible - same as other requirements
            import urllib.request
            with urllib.request.urlopen(working_url, timeout=5) as response:
                if response.status == 200:
                    print(f"HeidiSQL: Found working URL: {working_url}")
                    return working_url
                else:
                    print(f"HeidiSQL: URL returned status: {response.status}")
                    return None
                    
        except Exception as e:
            print(f"Error finding latest HeidiSQL: {e}")
            return None
    
    def _show_download_error(self, dialog, error_msg):
        """Show download error message"""
        dialog.status_label.config(text="Download failed!")
        dialog.progress_text.config(text="Error")
        
        # Get the requirement name and tried URLs for better error message
        req_name = "the dependency"
        tried_urls = []
        for key, req in self.requirements.items():
            if hasattr(dialog, 'req_key') and dialog.req_key == key:
                req_name = req["name"]
                tried_urls = [req["download_url"]] + self._get_alternative_urls(key)
                break
        
        # Create error message with tried URLs
        error_details = f"Failed to download {req_name}:\n{error_msg}\n\n"
        if tried_urls:
            error_details += f"Tried {len(tried_urls)} URL(s):\n"
            for i, url in enumerate(tried_urls, 1):
                error_details += f"{i}. {url}\n"
            error_details += "\n"
        
        error_details += "All download URLs are currently unavailable.\n\n"
        error_details += "Please:\n"
        error_details += "1. Check your internet connection\n"
        error_details += "2. Download manually from the official website\n"
        error_details += "3. Use 'Set Path' button to specify the installation location"
        
        messagebox.showerror("Download Error", error_details)
        dialog.destroy()
    
    def _prompt_installation(self, key, req, file_path, dialog):
        """Prompt user to start installation"""
        dialog.destroy()
        
        if messagebox.askyesno("Start Installation", 
                              f"Download completed successfully!\n\n"
                              f"File: {os.path.basename(file_path)}\n"
                              f"Size: {os.path.getsize(file_path) / (1024*1024):.1f} MB\n\n"
                              f"Start installation of {req['name']}?"):
            self._start_installation(key, req, file_path)
        else:
            # Clean up downloaded file
            try:
                os.remove(file_path)
                # Don't remove the download directory since it might contain other files
            except:
                pass
            messagebox.showinfo("Installation Cancelled", 
                              f"Installation of {req['name']} was cancelled.\n"
                              "The downloaded file has been removed.")
    
    def _start_installation(self, key, req, file_path):
        """Start the actual installation process"""
        try:
            filename = os.path.basename(file_path)
            
            if filename.endswith('.exe'):
                # Special handling for Visual Studio to ensure C++ workload is installed
                if req["name"] == "Visual Studio 2022":
                    # Use Visual Studio Installer with C++ workload
                    vs_installer_path = os.path.join(os.path.dirname(file_path), "vs_installer.exe")
                    if os.path.exists(vs_installer_path):
                        # Install with Desktop development with C++ workload
                        cmd = [
                            vs_installer_path,
                            "install",
                            "--quiet",
                            "--wait",
                            "--add", "Microsoft.VisualStudio.Workload.NativeDesktop",
                            "--add", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
                            "--add", "Microsoft.VisualStudio.Component.Windows10SDK.19041"
                        ]
                        subprocess.Popen(cmd, shell=True)
                        messagebox.showinfo("Visual Studio Installation Started", 
                                          f"{req['name']} installer has been launched with C++ workload.\n\n"
                                          "The installer will automatically install:\n"
                                          "• Desktop development with C++\n"
                                          "• MSVC v143 - VS 2022 C++ x64/x86 compiler\n"
                                          "• Windows 10 SDK (10.0.19041.0)\n\n"
                                          "Please wait for the installation to complete.\n\n"
                                          "After installation, you can use the 'Scan System' button to detect the new installation.")
                    else:
                        # Fallback to regular installer if vs_installer.exe not found
                        subprocess.Popen([file_path], shell=True)
                        messagebox.showinfo("Visual Studio Installation Started", 
                                          f"{req['name']} installer has been launched.\n\n"
                                          "IMPORTANT: Please manually select 'Desktop development with C++' workload during installation.\n\n"
                                          "After installation, you can use the 'Scan System' button to detect the new installation.")
                else:
                    # Run other .exe installers normally
                    subprocess.Popen([file_path], shell=True)
                    messagebox.showinfo("Installation Started", 
                                      f"{req['name']} installer has been launched.\n\n"
                                      "Please complete the installation process in the installer window.\n\n"
                                      "After installation, you can use the 'Scan System' button to detect the new installation.")
                
            elif filename.endswith('.msi'):
                # Run MSI installer
                subprocess.Popen(['msiexec', '/i', file_path], shell=True)
                messagebox.showinfo("Installation Started", 
                                  f"{req['name']} MSI installer has been launched.\n\n"
                                  "Please complete the installation process in the installer window.\n\n"
                                  "After installation, you can use the 'Scan System' button to detect the new installation.")
                
            elif filename.endswith('.zip'):
                # Extract ZIP file
                self._extract_zip(key, req, file_path)
                
            else:
                messagebox.showwarning("Unknown File Type", 
                                     f"Unknown file type: {filename}\n\n"
                                     "Please install manually and then use 'Set Path' to specify the location.")
            
            # Update the requirement path to the expected install location
            req["path"] = req["install_path"]
            req["detected"] = True
            req["version"] = "Installed via ACB"
            self.update_status(key, "✅", "Installed", f"Installed via ACB\n{req['install_path']}")
            
            # Clean up temporary files after a delay
            self.root.after(5000, lambda: self._cleanup_temp_files(file_path))
            
        except Exception as e:
            messagebox.showerror("Installation Error", 
                               f"Failed to start installation:\n{str(e)}")
    
    def _cleanup_temp_files(self, file_path):
        """Clean up downloaded files"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                # Keep the download directory for future use
        except:
            pass  # Ignore cleanup errors
    
    def _extract_zip(self, key, req, file_path):
        """Extract ZIP file to installation directory"""
        try:
            # Create installation directory
            install_dir = req["install_path"]
            os.makedirs(install_dir, exist_ok=True)
            
            # Extract ZIP file
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(install_dir)
            
            # Special handling for MySQL to set environment variables
            if key == "MySQL":
                self._setup_mysql_environment(install_dir)
            
            # Special handling for HeidiSQL to add to PATH
            if key == "HeidiSQL":
                self._setup_heidisql_environment(install_dir)
            
            # Special handling for Boost to set BOOST_ROOT environment variable
            if key == "Boost":
                self._setup_boost_environment(install_dir)
            
            messagebox.showinfo("Installation Complete", 
                              f"{req['name']} has been extracted to:\n{install_dir}\n\n"
                              "The software is now ready to use!")
            
        except Exception as e:
            messagebox.showerror("Extraction Error", 
                               f"Failed to extract {req['name']}:\n{str(e)}")
    
    def _setup_mysql_environment(self, install_dir):
        """Set MySQL bin, lib, include folders and libmysql.lib as system environment variables"""
        try:
            import winreg
            
            # MySQL paths
            mysql_bin = os.path.join(install_dir, "bin")
            mysql_lib = os.path.join(install_dir, "lib")
            mysql_include = os.path.join(install_dir, "include")
            mysql_libmysql = os.path.join(install_dir, "lib", "libmysql.lib")
            
            # Check if paths exist
            if not os.path.exists(mysql_bin):
                print(f"MySQL bin directory not found: {mysql_bin}")
                return
            if not os.path.exists(mysql_lib):
                print(f"MySQL lib directory not found: {mysql_lib}")
                return
            if not os.path.exists(mysql_include):
                print(f"MySQL include directory not found: {mysql_include}")
                return
            if not os.path.exists(mysql_libmysql):
                print(f"MySQL libmysql.lib not found: {mysql_libmysql}")
                return
            
            # Get current PATH from registry
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 
                                   0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
                    try:
                        current_path, _ = winreg.QueryValueEx(key, "Path")
                    except FileNotFoundError:
                        current_path = ""
            except PermissionError:
                # Try current user environment if system-wide fails
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                       r"Environment", 
                                       0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
                        try:
                            current_path, _ = winreg.QueryValueEx(key, "Path")
                        except FileNotFoundError:
                            current_path = ""
                except PermissionError:
                    print("Failed to access environment variables registry")
                    return
            
            # Check if MySQL paths are already in PATH
            path_dirs = current_path.split(os.pathsep) if current_path else []
            
            if mysql_bin not in path_dirs:
                path_dirs.append(mysql_bin)
                print(f"Added MySQL bin to PATH: {mysql_bin}")
            
            if mysql_lib not in path_dirs:
                path_dirs.append(mysql_lib)
                print(f"Added MySQL lib to PATH: {mysql_lib}")
            
            if mysql_include not in path_dirs:
                path_dirs.append(mysql_include)
                print(f"Added MySQL include to PATH: {mysql_include}")
            
            # Update PATH in registry
            new_path = os.pathsep.join(path_dirs)
            
            try:
                # Try system-wide first
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 
                                   0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                    print("Updated system PATH environment variable")
            except PermissionError:
                # Fallback to current user
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                       r"Environment", 
                                       0, winreg.KEY_WRITE) as key:
                        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                        print("Updated user PATH environment variable")
                except Exception as e:
                    print(f"Failed to update user PATH: {e}")
                    return
            
            # Set MYSQL_HOME environment variable
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 
                                   0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, "MYSQL_HOME", 0, winreg.REG_EXPAND_SZ, install_dir)
                    print(f"Set MYSQL_HOME: {install_dir}")
            except PermissionError:
                # Fallback to current user
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                       r"Environment", 
                                       0, winreg.KEY_WRITE) as key:
                        winreg.SetValueEx(key, "MYSQL_HOME", 0, winreg.REG_EXPAND_SZ, install_dir)
                        print(f"Set MYSQL_HOME: {install_dir}")
                except Exception as e:
                    print(f"Failed to set MYSQL_HOME: {e}")
            
            # Set MYSQL_LIB environment variable pointing to libmysql.lib
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 
                                   0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, "MYSQL_LIB", 0, winreg.REG_EXPAND_SZ, mysql_libmysql)
                    print(f"Set MYSQL_LIB: {mysql_libmysql}")
            except PermissionError:
                # Fallback to current user
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                       r"Environment", 
                                       0, winreg.KEY_WRITE) as key:
                        winreg.SetValueEx(key, "MYSQL_LIB", 0, winreg.REG_EXPAND_SZ, mysql_libmysql)
                        print(f"Set MYSQL_LIB: {mysql_libmysql}")
                except Exception as e:
                    print(f"Failed to set MYSQL_LIB: {e}")
            
            # Set MYSQL_INCLUDE environment variable
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 
                                   0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, "MYSQL_INCLUDE", 0, winreg.REG_EXPAND_SZ, mysql_include)
                    print(f"Set MYSQL_INCLUDE: {mysql_include}")
            except PermissionError:
                # Fallback to current user
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                       r"Environment", 
                                       0, winreg.KEY_WRITE) as key:
                        winreg.SetValueEx(key, "MYSQL_INCLUDE", 0, winreg.REG_EXPAND_SZ, mysql_include)
                        print(f"Set MYSQL_INCLUDE: {mysql_include}")
                except Exception as e:
                    print(f"Failed to set MYSQL_INCLUDE: {e}")
            
            # Notify user about environment variable changes
            messagebox.showinfo("MySQL Environment Setup", 
                              f"MySQL has been installed and environment variables have been set:\n\n"
                              f"• Added to PATH: {mysql_bin}\n"
                              f"• Added to PATH: {mysql_lib}\n"
                              f"• Added to PATH: {mysql_include}\n"
                              f"• Set MYSQL_HOME: {install_dir}\n"
                              f"• Set MYSQL_LIB: {mysql_libmysql}\n"
                              f"• Set MYSQL_INCLUDE: {mysql_include}\n\n"
                              "Note: You may need to restart your terminal/command prompt "
                              "or restart your computer for the changes to take effect.")
            
        except Exception as e:
            print(f"Error setting up MySQL environment: {e}")
            messagebox.showwarning("MySQL Environment Setup", 
                                 f"MySQL was installed but there was an issue setting environment variables:\n\n"
                                 f"Error: {str(e)}\n\n"
                                 "You may need to manually add MySQL to your PATH environment variable.")
    
    def _setup_heidisql_environment(self, install_dir):
        """Add HeidiSQL to PATH environment variable"""
        try:
            import winreg
            
            # Get current PATH from registry
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 
                                   0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
                    try:
                        current_path, _ = winreg.QueryValueEx(key, "Path")
                    except FileNotFoundError:
                        current_path = ""
            except PermissionError:
                # Try current user environment if system-wide fails
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                       r"Environment", 
                                       0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
                        try:
                            current_path, _ = winreg.QueryValueEx(key, "Path")
                        except FileNotFoundError:
                            current_path = ""
                except PermissionError:
                    print("Failed to access environment variables registry")
                    return
            
            # Check if HeidiSQL path is already in PATH
            path_dirs = current_path.split(os.pathsep) if current_path else []
            
            if install_dir not in path_dirs:
                path_dirs.append(install_dir)
                print(f"Added HeidiSQL to PATH: {install_dir}")
                
                # Update PATH in registry
                new_path = os.pathsep.join(path_dirs)
                
                try:
                    # Try system-wide first
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                       r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 
                                       0, winreg.KEY_WRITE) as key:
                        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                        print("Updated system PATH environment variable")
                except PermissionError:
                    # Fallback to current user
                    try:
                        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                           r"Environment", 
                                           0, winreg.KEY_WRITE) as key:
                            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                            print("Updated user PATH environment variable")
                    except Exception as e:
                        print(f"Failed to update user PATH: {e}")
                        return
                
                # Notify user about environment variable changes
                messagebox.showinfo("HeidiSQL Environment Setup", 
                                  f"HeidiSQL has been installed and added to PATH:\n\n"
                                  f"• Added to PATH: {install_dir}\n\n"
                                  "Note: You may need to restart your terminal/command prompt "
                                  "or restart your computer for the changes to take effect.\n\n"
                                  "You can now run 'heidisql' from anywhere in your command prompt.")
            else:
                print(f"HeidiSQL path already in PATH: {install_dir}")
                
        except Exception as e:
            print(f"Error setting up HeidiSQL environment: {e}")
            messagebox.showwarning("HeidiSQL Environment Setup", 
                                 f"HeidiSQL was installed but there was an issue setting environment variables:\n\n"
                                 f"Error: {str(e)}\n\n"
                                 "You may need to manually add HeidiSQL to your PATH environment variable.")
    
    def _setup_boost_environment(self, install_dir):
        """Set BOOST_ROOT environment variable for Boost installation"""
        try:
            import winreg
            
            # Convert backslashes to forward slashes as required by Boost
            boost_root = install_dir.replace('\\', '/')
            
            # Remove trailing slash if present
            if boost_root.endswith('/'):
                boost_root = boost_root[:-1]
            
            print(f"Setting BOOST_ROOT to: {boost_root}")
            
            # Try to set BOOST_ROOT in system environment variables first
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 
                                   0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, "BOOST_ROOT", 0, winreg.REG_EXPAND_SZ, boost_root)
                    print("Set BOOST_ROOT in system environment variables")
            except PermissionError:
                print("Failed to set BOOST_ROOT in system environment variables (permission denied)")
            
            # Also set in user environment variables as fallback/recommendation
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Environment", 
                                   0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, "BOOST_ROOT", 0, winreg.REG_EXPAND_SZ, boost_root)
                    print("Set BOOST_ROOT in user environment variables")
            except Exception as e:
                print(f"Failed to set BOOST_ROOT in user environment variables: {e}")
            
            # Notify user about environment variable changes
            messagebox.showinfo("Boost Environment Setup", 
                              f"Boost has been installed and BOOST_ROOT environment variable has been set:\n\n"
                              f"• Set BOOST_ROOT: {boost_root}\n\n"
                              "Note: You may need to restart your terminal/command prompt "
                              "or restart your computer for the changes to take effect.\n\n"
                              "The BOOST_ROOT variable is required for building projects that use Boost.")
            
        except Exception as e:
            print(f"Error setting up Boost environment: {e}")
            messagebox.showwarning("Boost Environment Setup", 
                                 f"Boost was installed but there was an issue setting environment variables:\n\n"
                                 f"Error: {str(e)}\n\n"
                                 "You may need to manually set BOOST_ROOT environment variable to:\n"
                                 f"{install_dir.replace('\\', '/').rstrip('/')}")
    
    def _find_msbuild(self):
        """Find MSBuild executable from Visual Studio installations"""
        try:
            # Common MSBuild locations for Visual Studio 2022
            possible_paths = [
                r"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe",
                r"C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\MSBuild.exe",
                r"C:\Program Files\Microsoft Visual Studio\2022\Enterprise\MSBuild\Current\Bin\MSBuild.exe",
                r"C:\Program Files (x86)\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe",
                r"C:\Program Files (x86)\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\MSBuild.exe",
                r"C:\Program Files (x86)\Microsoft Visual Studio\2022\Enterprise\MSBuild\Current\Bin\MSBuild.exe",
                # Visual Studio 2019 paths as fallback
                r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe",
                r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\MSBuild\Current\Bin\MSBuild.exe",
                r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Enterprise\MSBuild\Current\Bin\MSBuild.exe",
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    self.log_to_console(f"🔍 Found MSBuild at: {path}")
                    return path
            
            # Try to find from PATH as last resort
            try:
                result = subprocess.run(["where", "msbuild"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    msbuild_path = result.stdout.strip().split('\n')[0]
                    if os.path.exists(msbuild_path):
                        self.log_to_console(f"🔍 Found MSBuild in PATH: {msbuild_path}")
                        return msbuild_path
            except:
                pass
            
            self.log_to_console("❌ MSBuild not found in common locations or PATH")
            return None
            
        except Exception as e:
            self.log_to_console(f"❌ Error finding MSBuild: {str(e)}")
            return None
    
    def _show_build_finished(self, dialog):
        """Show the Build Finished button and hide the Cancel Build button"""
        try:
            # Hide the Cancel Build button
            dialog.cancel_button.pack_forget()
            
            # Show and enable the Build Finished button
            dialog.build_finished_button.config(state=tk.NORMAL)
            
            # Stop the progress bar
            dialog.progress.stop()
            
            # Update status to show completion
            dialog.status_label.config(text="Build completed successfully!", foreground="green")
            
        except Exception as e:
            self.log_to_console(f"❌ Error updating build dialog buttons: {str(e)}")
    
    def _cancel_build(self, dialog):
        """Cancel the current build process"""
        if messagebox.askyesno("Cancel Build", 
                              "Are you sure you want to cancel the build process?"):
            dialog.cancelled = True
            self.log_to_console(f"❌ User cancelled build process")
            dialog.destroy()
        else:
            self.log_to_console(f"🔄 User chose to continue build process")
    
    def nuke_build_folder(self):
        """Erase all files in the Build folder for a fresh start"""
        build_dir = os.path.join(self._get_app_dir(), "Build")
        
        if not os.path.exists(build_dir):
            self.log_to_console("💥 Build folder does not exist - nothing to nuke")
            messagebox.showinfo("Nuke Build", "Build folder does not exist.\nNothing to clean.")
            return
        
        # Count files and folders in Build directory
        try:
            build_contents = os.listdir(build_dir)
            if not build_contents:
                self.log_to_console("💥 Build folder is already empty")
                messagebox.showinfo("Nuke Build", "Build folder is already empty.\nNothing to clean.")
                return
        except Exception as e:
            self.log_to_console(f"❌ Error checking Build folder contents: {str(e)}")
            messagebox.showerror("Error", f"Error checking Build folder:\n{str(e)}")
            return
        
        # Confirm the nuke operation
        confirm_msg = f"Are you sure you want to NUKE the Build folder?\n\n"
        confirm_msg += f"This will permanently delete ALL files and folders in:\n{build_dir}\n\n"
        confirm_msg += f"Found {len(build_contents)} items to delete.\n\n"
        confirm_msg += "This action cannot be undone!"
        
        if not messagebox.askyesno("💥 NUKE BUILD FOLDER", confirm_msg):
            self.log_to_console("❌ Nuke operation cancelled by user")
            return
        
        try:
            self.log_to_console(f"💥 Starting nuke operation on Build folder: {build_dir}")
            
            # Remove the entire Build directory and recreate it
            import shutil
            shutil.rmtree(build_dir)
            os.makedirs(build_dir, exist_ok=True)
            
            self.log_to_console(f"✅ Successfully nuked Build folder - {len(build_contents)} items deleted")
            self.log_to_console(f"📁 Recreated empty Build folder: {build_dir}")
            
            messagebox.showinfo("Nuke Complete", 
                              f"Build folder has been successfully nuked!\n\n"
                              f"Deleted {len(build_contents)} items.\n"
                              f"Build folder is now empty and ready for fresh builds.")
            
        except Exception as e:
            self.log_to_console(f"❌ Failed to nuke Build folder: {str(e)}")
            messagebox.showerror("Nuke Failed", 
                               f"Failed to nuke Build folder:\n\n{str(e)}\n\n"
                               "You may need to manually delete the folder or close any applications "
                               "that might be using files in this directory.")

    def create_repack(self):
        """Create a Repack folder with server executables and configuration files"""
        try:
            # Import shutil at the beginning of the method
            import shutil
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            repack_dir = os.path.join(app_dir, "Repack")
            build_dir = os.path.join(app_dir, "Build")
            build_bin_dir = os.path.join(build_dir, "bin", "RelWithDebInfo")
            
            self.log_to_console("📦 Starting repack creation...")
            
            # Check if Build folder exists
            if not os.path.exists(build_dir):
                messagebox.showerror("Build Folder Not Found", 
                                   "Build folder not found. Please build AzerothCore first before creating a repack.")
                self.log_to_console("❌ Build folder not found")
                return
            
            # Check if Build\bin\RelWithDebInfo folder exists
            if not os.path.exists(build_bin_dir):
                messagebox.showerror("Build Bin Folder Not Found", 
                                   f"Build bin folder not found at:\n{build_bin_dir}\n\n"
                                   "Please build AzerothCore first before creating a repack.")
                self.log_to_console("❌ Build bin folder not found")
                return
            
            # Create Repack directory
            if os.path.exists(repack_dir):
                if not messagebox.askyesno("Repack Exists", 
                                         f"Repack folder already exists at:\n{repack_dir}\n\n"
                                         "Do you want to replace it? This will delete the existing repack."):
                    self.log_to_console("❌ Repack creation cancelled by user")
                    return
                
                # Remove existing repack folder
                shutil.rmtree(repack_dir)
                self.log_to_console("🗑️ Removed existing repack folder")
            
            # Create new repack directory
            os.makedirs(repack_dir, exist_ok=True)
            self.log_to_console(f"📁 Created repack directory: {repack_dir}")
            
            # Files and folders to copy - all from Build\bin\RelWithDebInfo
            items_to_copy = [
                # Executables from Build\bin\RelWithDebInfo
                (os.path.join(build_bin_dir, "authserver.exe"), "authserver.exe"),
                (os.path.join(build_bin_dir, "worldserver.exe"), "worldserver.exe"),
                # Folders from Build\bin\RelWithDebInfo
                (os.path.join(build_bin_dir, "configs"), "configs"),
                (os.path.join(build_bin_dir, "lua_scripts"), "lua_scripts")
            ]
            
            copied_items = []
            missing_items = []
            
            # Copy each item
            for source_path, dest_name in items_to_copy:
                dest_path = os.path.join(repack_dir, dest_name)
                
                if os.path.exists(source_path):
                    if os.path.isfile(source_path):
                        # Copy file
                        shutil.copy2(source_path, dest_path)
                        copied_items.append(f"📄 {dest_name}")
                    elif os.path.isdir(source_path):
                        # Copy directory
                        shutil.copytree(source_path, dest_path)
                        copied_items.append(f"📁 {dest_name}/")
                    
                    self.log_to_console(f"✅ Copied {dest_name}")
                else:
                    missing_items.append(dest_name)
                    self.log_to_console(f"⚠️ Not found: {dest_name}")
            
            # Show completion message
            if copied_items:
                success_msg = f"Repack created successfully!\n\n"
                success_msg += f"Location: {repack_dir}\n\n"
                success_msg += f"Copied items:\n" + "\n".join(copied_items)
                
                if missing_items:
                    success_msg += f"\n\nMissing items:\n" + "\n".join(f"• {item}" for item in missing_items)
                    success_msg += f"\n\nNote: Some items were not found in the Build folder."
                
                messagebox.showinfo("Repack Created", success_msg)
                self.log_to_console("🎉 Repack creation completed successfully!")
            else:
                messagebox.showerror("No Items Copied", 
                                   "No items were copied. Please check if the Build folder contains the required files.")
                self.log_to_console("❌ No items were copied to repack")
                
        except Exception as e:
            error_msg = f"Failed to create repack:\n\n{str(e)}"
            messagebox.showerror("Repack Creation Failed", error_msg)
            self.log_to_console(f"❌ Repack creation failed: {str(e)}")

    def create_configs(self):
        """Transform all .conf.dist files to .conf files in Repack/configs folder"""
        try:
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            repack_dir = os.path.join(app_dir, "Repack")
            configs_dir = os.path.join(repack_dir, "configs")
            
            self.log_to_console("⚙️ Starting config file transformation...")
            
            # Check if Repack folder exists
            if not os.path.exists(repack_dir):
                messagebox.showerror("Repack Folder Not Found", 
                                   "Repack folder not found. Please create a repack first using the 'Create Repack' button.")
                self.log_to_console("❌ Repack folder not found")
                return
            
            # Check if configs folder exists
            if not os.path.exists(configs_dir):
                messagebox.showerror("Configs Folder Not Found", 
                                   f"Configs folder not found at:\n{configs_dir}\n\n"
                                   "Please create a repack first using the 'Create Repack' button.")
                self.log_to_console("❌ Configs folder not found")
                return
            
            # Find all .conf.dist files recursively
            conf_dist_files = []
            for root, dirs, files in os.walk(configs_dir):
                for file in files:
                    if file.endswith('.conf.dist'):
                        conf_dist_files.append(os.path.join(root, file))
            
            if not conf_dist_files:
                messagebox.showinfo("No Config Files Found", 
                                  "No .conf.dist files found in the configs folder.\n\n"
                                  "All config files may already be transformed or the folder is empty.")
                self.log_to_console("ℹ️ No .conf.dist files found")
                return
            
            # Transform each .conf.dist file to .conf
            transformed_count = 0
            failed_files = []
            
            for conf_dist_file in conf_dist_files:
                try:
                    # Create the new .conf filename
                    conf_file = conf_dist_file.replace('.conf.dist', '.conf')
                    
                    # Check if .conf file already exists
                    if os.path.exists(conf_file):
                        self.log_to_console(f"⚠️ Skipping {os.path.basename(conf_dist_file)} - .conf file already exists")
                        continue
                    
                    # Copy .conf.dist to .conf
                    import shutil
                    shutil.copy2(conf_dist_file, conf_file)
                    
                    # Keep the .conf.dist file (don't delete it)
                    
                    transformed_count += 1
                    self.log_to_console(f"✅ Created: {os.path.basename(conf_file)} (kept .conf.dist)")
                    
                except Exception as e:
                    failed_files.append(os.path.basename(conf_dist_file))
                    self.log_to_console(f"❌ Failed to transform {os.path.basename(conf_dist_file)}: {str(e)}")
            
            # Show completion message
            if transformed_count > 0:
                success_msg = f"Config files created successfully!\n\n"
                success_msg += f"Created {transformed_count} .conf files from .conf.dist templates\n"
                success_msg += f"Original .conf.dist files have been preserved"
                
                if failed_files:
                    success_msg += f"\n\nFailed to create:\n" + "\n".join(f"• {file}" for file in failed_files)
                
                messagebox.showinfo("Configs Created", success_msg)
                self.log_to_console(f"🎉 Config creation completed! Created {transformed_count} .conf files (kept .conf.dist)")
            else:
                messagebox.showinfo("No Files Created", 
                                  "No files were created. All .conf.dist files may already have corresponding .conf files.")
                self.log_to_console("ℹ️ No files were created")
                
        except Exception as e:
            error_msg = f"Failed to create configs:\n\n{str(e)}"
            messagebox.showerror("Config Creation Failed", error_msg)
            self.log_to_console(f"❌ Config creation failed: {str(e)}")

    def config_paths_dialog(self):
        """Show dialog to configure custom paths"""
        try:
            # Create dialog window
            dialog = tk.Toplevel(self.root)
            dialog.title("Configure Server Paths")
            dialog.geometry("500x400")
            dialog.resizable(False, False)
            
            # Center the dialog
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Main frame
            main_frame = ttk.Frame(dialog, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            title_label = ttk.Label(main_frame, text="Configure Server Paths", 
                                  font=("Arial", 14, "bold"))
            title_label.pack(pady=(0, 20))
            
            # Description
            desc_label = ttk.Label(main_frame, 
                                 text="Configure the paths that will be set in your server config files.\n"
                                      "Leave empty to use default values.",
                                 font=("Arial", 9), foreground="gray")
            desc_label.pack(pady=(0, 20))
            
            # Path configuration frame
            paths_frame = ttk.Frame(main_frame)
            paths_frame.pack(fill=tk.X, pady=(0, 20))
            
            # Default values
            default_data_dir = "Data"
            default_logs_dir = "Logs"
            default_mysql_exe = ".\\mysql\\bin\\mysql.exe"
            
            # DataDir
            ttk.Label(paths_frame, text="Data Directory:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
            data_dir_var = tk.StringVar(value=default_data_dir)
            data_dir_entry = ttk.Entry(paths_frame, textvariable=data_dir_var, width=40)
            data_dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
            
            # LogsDir
            ttk.Label(paths_frame, text="Logs Directory:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
            logs_dir_var = tk.StringVar(value=default_logs_dir)
            logs_dir_entry = ttk.Entry(paths_frame, textvariable=logs_dir_var, width=40)
            logs_dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
            
            # MySQLExecutable
            ttk.Label(paths_frame, text="MySQL Executable:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
            mysql_exe_var = tk.StringVar(value=default_mysql_exe)
            mysql_exe_entry = ttk.Entry(paths_frame, textvariable=mysql_exe_var, width=40)
            mysql_exe_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
            
            # Configure grid weights
            paths_frame.columnconfigure(1, weight=1)
            
            # Buttons frame
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill=tk.X, pady=(20, 0))
            
            # Use Defaults button
            defaults_button = ttk.Button(buttons_frame, text="Use Defaults", 
                                       command=lambda: self._reset_to_defaults(
                                           data_dir_var, logs_dir_var, mysql_exe_var,
                                           default_data_dir, default_logs_dir, default_mysql_exe))
            defaults_button.pack(side=tk.LEFT)
            
            # Spacer
            ttk.Frame(buttons_frame).pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Cancel button
            cancel_button = ttk.Button(buttons_frame, text="Cancel", 
                                     command=dialog.destroy)
            cancel_button.pack(side=tk.RIGHT, padx=(10, 0))
            
            # Apply button
            apply_button = ttk.Button(buttons_frame, text="Apply Paths", 
                                    command=lambda: self._apply_custom_paths(
                                        dialog, data_dir_var.get(), logs_dir_var.get(), mysql_exe_var.get()))
            apply_button.pack(side=tk.RIGHT)
            
            # Focus on first entry
            data_dir_entry.focus()
            
        except Exception as e:
            messagebox.showerror("Dialog Error", f"Failed to create config paths dialog:\n\n{str(e)}")
            self.log_to_console(f"❌ Config paths dialog failed: {str(e)}")

    def _reset_to_defaults(self, data_var, logs_var, mysql_var, default_data, default_logs, default_mysql):
        """Reset all path variables to default values"""
        data_var.set(default_data)
        logs_var.set(default_logs)
        mysql_var.set(default_mysql)

    def _apply_custom_paths(self, dialog, data_dir, logs_dir, mysql_exe):
        """Apply the custom paths and close dialog"""
        dialog.destroy()
        self.config_paths(data_dir, logs_dir, mysql_exe)

    def config_paths(self, custom_data_dir=None, custom_logs_dir=None, custom_mysql_exe=None):
        """Update paths in worldserver.conf file"""
        try:
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            repack_dir = os.path.join(app_dir, "Repack")
            configs_dir = os.path.join(repack_dir, "configs")
            worldserver_conf = os.path.join(configs_dir, "worldserver.conf")
            
            self.log_to_console("📁 Starting config paths update...")
            
            # Check if Repack folder exists
            if not os.path.exists(repack_dir):
                messagebox.showerror("Repack Folder Not Found", 
                                   "Repack folder not found. Please create a repack first using the 'Create Repack' button.")
                self.log_to_console("❌ Repack folder not found")
                return
            
            # Check if configs folder exists
            if not os.path.exists(configs_dir):
                messagebox.showerror("Configs Folder Not Found", 
                                   f"Configs folder not found at:\n{configs_dir}\n\n"
                                   "Please create a repack first using the 'Create Repack' button.")
                self.log_to_console("❌ Configs folder not found")
                return
            
            # Check if config files exist
            authserver_conf = os.path.join(configs_dir, "authserver.conf")
            config_files = []
            
            if os.path.exists(worldserver_conf):
                config_files.append(("worldserver.conf", worldserver_conf))
            else:
                self.log_to_console("⚠️ worldserver.conf not found")
            
            if os.path.exists(authserver_conf):
                config_files.append(("authserver.conf", authserver_conf))
            else:
                self.log_to_console("⚠️ authserver.conf not found")
            
            if not config_files:
                messagebox.showerror("Config Files Not Found", 
                                   "Neither worldserver.conf nor authserver.conf found.\n\n"
                                   "Please create configs first using the 'Create configs' button.")
                self.log_to_console("❌ No config files found")
                return
            
            # Use custom paths if provided, otherwise use defaults
            data_dir = custom_data_dir if custom_data_dir else "Data"
            logs_dir = custom_logs_dir if custom_logs_dir else "Logs"
            mysql_exe = custom_mysql_exe if custom_mysql_exe else ".\\mysql\\bin\\mysql.exe"
            
            # Define the replacements
            replacements = [
                ('DataDir = "."', f'DataDir = "{data_dir}"'),
                ('LogsDir = ""', f'LogsDir = "{logs_dir}"'),
                ('MySQLExecutable = ""', f'MySQLExecutable = "{mysql_exe}"')
            ]
            
            total_updated_count = 0
            
            # Process each config file
            for config_name, config_path in config_files:
                self.log_to_console(f"📁 Processing {config_name}...")
                
                # Read the current config file
                with open(config_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Apply replacements
                file_updated_count = 0
                for old_value, new_value in replacements:
                    if old_value in content:
                        content = content.replace(old_value, new_value)
                        file_updated_count += 1
                        self.log_to_console(f"✅ Updated in {config_name}: {old_value} → {new_value}")
                    else:
                        self.log_to_console(f"⚠️ Not found in {config_name}: {old_value}")
                
                # Write the updated content back to the file
                with open(config_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                total_updated_count += file_updated_count
                self.log_to_console(f"📄 {config_name}: {file_updated_count} settings updated")
            
            # Show completion message
            if total_updated_count > 0:
                success_msg = f"Config paths updated successfully!\n\n"
                success_msg += f"Updated {total_updated_count} path settings in config files:\n"
                success_msg += f"• DataDir = \"{data_dir}\"\n"
                success_msg += f"• LogsDir = \"{logs_dir}\"\n"
                success_msg += f"• MySQLExecutable = \"{mysql_exe}\"\n\n"
                success_msg += f"Processed files: {', '.join([name for name, _ in config_files])}"
                
                messagebox.showinfo("Config Paths Updated", success_msg)
                self.log_to_console(f"🎉 Config paths update completed! Updated {total_updated_count} settings across {len(config_files)} files")
            else:
                messagebox.showinfo("No Updates Made", 
                                  "No path settings were found to update in the config files.\n\n"
                                  "The paths may already be configured or use different formatting.")
                self.log_to_console("ℹ️ No path settings were updated")
                
        except Exception as e:
            error_msg = f"Failed to update config paths:\n\n{str(e)}"
            messagebox.showerror("Config Paths Update Failed", error_msg)
            self.log_to_console(f"❌ Config paths update failed: {str(e)}")

    def create_mysql(self):
        """Copy MySQL folder from specified path to Repack folder and rename it to 'mysql'"""
        try:
            self.log_to_console("🗄️ Starting MySQL folder creation...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            repack_dir = os.path.join(app_dir, "Repack")
            
            # Check if Repack folder exists
            if not os.path.exists(repack_dir):
                messagebox.showerror("Repack Folder Not Found", 
                                   "Repack folder not found. Please create a repack first using the 'Create Repack' button.")
                self.log_to_console("❌ Repack folder not found")
                return
            
            # Find MySQL installation path
            mysql_path = self._find_mysql_path()
            if not mysql_path:
                messagebox.showerror("MySQL Not Found", 
                                   "MySQL installation not found. Please install MySQL first or specify the path manually.")
                self.log_to_console("❌ MySQL installation not found")
                return
            
            self.log_to_console(f"✅ Found MySQL installation at: {mysql_path}")
            
            # Target path in Repack folder
            target_mysql_dir = os.path.join(repack_dir, "mysql")
            
            # Check if mysql folder already exists in Repack
            if os.path.exists(target_mysql_dir):
                if messagebox.askyesno("MySQL Folder Exists", 
                                     f"MySQL folder already exists in Repack directory:\n\n{target_mysql_dir}\n\n"
                                     "Do you want to replace it? This will delete the existing folder."):
                    self.log_to_console("🗑️ Removing existing MySQL folder...")
                    shutil.rmtree(target_mysql_dir)
                else:
                    self.log_to_console("❌ MySQL folder creation cancelled by user")
                    return
            
            # Copy MySQL folder to Repack directory
            self.log_to_console(f"📁 Copying MySQL from {mysql_path} to {target_mysql_dir}...")
            
            # Show progress dialog
            progress_dialog = self._create_mysql_progress_dialog()
            
            # Copy in a separate thread to avoid blocking UI
            copy_thread = threading.Thread(target=self._copy_mysql_folder, 
                                         args=(mysql_path, target_mysql_dir, progress_dialog))
            copy_thread.daemon = True
            copy_thread.start()
            
        except Exception as e:
            error_msg = f"Failed to create MySQL folder:\n\n{str(e)}"
            messagebox.showerror("MySQL Creation Failed", error_msg)
            self.log_to_console(f"❌ MySQL creation failed: {str(e)}")
    
    def _find_mysql_path(self):
        """Find MySQL installation path from requirements or common locations"""
        # First check if MySQL is detected in requirements
        if self.requirements["MySQL"]["detected"] and self.requirements["MySQL"]["path"]:
            mysql_path = self.requirements["MySQL"]["path"]
            # If it's pointing to mysql.exe, get the parent directory
            if mysql_path.endswith("mysql.exe"):
                mysql_path = os.path.dirname(os.path.dirname(mysql_path))  # Go up two levels (bin -> MySQL Server X.X)
            return mysql_path
        
        # Check common MySQL installation paths
        common_paths = [
            r"C:\Program Files\MySQL\MySQL Server 8.0",
            r"C:\Program Files\MySQL\MySQL Server 8.4",
            r"C:\Program Files (x86)\MySQL\MySQL Server 8.0",
            r"C:\Program Files (x86)\MySQL\MySQL Server 8.4"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _create_mysql_progress_dialog(self):
        """Create progress dialog for MySQL copying"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Creating MySQL Folder")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 200, self.root.winfo_rooty() + 200))
        
        # Title
        title_label = ttk.Label(dialog, text="Creating MySQL Folder", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(20, 10))
        
        # Status label
        status_label = ttk.Label(dialog, text="Preparing to copy MySQL files...", font=("Arial", 10))
        status_label.pack(pady=(0, 20))
        
        # Progress bar
        progress = ttk.Progressbar(dialog, mode='indeterminate', length=300)
        progress.pack(pady=(0, 20))
        progress.start()
        
        # Store references
        dialog.status_label = status_label
        dialog.progress = progress
        
        return dialog
    
    def _copy_mysql_folder(self, source_path, target_path, dialog):
        """Copy MySQL folder in background thread"""
        try:
            # Update status
            self.root.after(0, lambda: dialog.status_label.config(text="Copying MySQL files..."))
            self.log_to_console("📁 Starting MySQL folder copy operation...")
            
            # Copy the entire MySQL directory
            shutil.copytree(source_path, target_path)
            
            # Update status and close dialog
            self.root.after(0, lambda: dialog.status_label.config(text="MySQL folder created successfully!"))
            self.root.after(0, lambda: dialog.progress.stop())
            self.root.after(0, lambda: dialog.destroy())
            
            # Show success message
            self.root.after(0, lambda: messagebox.showinfo("MySQL Created", 
                                                        f"MySQL folder has been successfully created!\n\n"
                                                        f"Source: {source_path}\n"
                                                        f"Target: {target_path}\n\n"
                                                        "The MySQL folder is now ready for use in your repack."))
            
            self.log_to_console(f"✅ MySQL folder created successfully at: {target_path}")
            
        except Exception as e:
            # Update status and close dialog
            self.root.after(0, lambda: dialog.status_label.config(text="Failed to copy MySQL files"))
            self.root.after(0, lambda: dialog.progress.stop())
            self.root.after(0, lambda: dialog.destroy())
            
            # Show error message
            error_msg = f"Failed to copy MySQL folder:\n\n{str(e)}"
            self.root.after(0, lambda: messagebox.showerror("MySQL Copy Failed", error_msg))
            self.log_to_console(f"❌ MySQL folder copy failed: {str(e)}")

    def create_dlls(self):
        """Copy required DLL files from OpenSSL and MySQL to Repack folder"""
        try:
            self.log_to_console("📚 Starting DLL files creation...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            repack_dir = os.path.join(app_dir, "Repack")
            
            # Check if Repack folder exists
            if not os.path.exists(repack_dir):
                messagebox.showerror("Repack Folder Not Found", 
                                   "Repack folder not found. Please create a repack first using the 'Create Repack' button.")
                self.log_to_console("❌ Repack folder not found")
                return
            
            # Find OpenSSL and MySQL paths
            openssl_path = self._find_openssl_path()
            mysql_path = self._find_mysql_path()
            
            if not openssl_path:
                messagebox.showerror("OpenSSL Not Found", 
                                   "OpenSSL installation not found. Please install OpenSSL first or specify the path manually.")
                self.log_to_console("❌ OpenSSL installation not found")
                return
            
            if not mysql_path:
                messagebox.showerror("MySQL Not Found", 
                                   "MySQL installation not found. Please install MySQL first or specify the path manually.")
                self.log_to_console("❌ MySQL installation not found")
                return
            
            self.log_to_console(f"✅ Found OpenSSL installation at: {openssl_path}")
            self.log_to_console(f"✅ Found MySQL installation at: {mysql_path}")
            
            # Debug: Show the actual DLL paths that will be checked
            openssl_bin_path = os.path.join(openssl_path, "bin")
            self.log_to_console(f"🔍 OpenSSL bin directory: {openssl_bin_path}")
            self.log_to_console(f"🔍 Checking for DLLs in: {openssl_bin_path}")
            
            # Define DLL files to copy
            dll_files = [
                {
                    "source_path": os.path.join(openssl_path, "bin", "libcrypto-3-x64.dll"),
                    "name": "libcrypto-3-x64.dll",
                    "type": "OpenSSL"
                },
                {
                    "source_path": os.path.join(openssl_path, "bin", "libssl-3-x64.dll"),
                    "name": "libssl-3-x64.dll",
                    "type": "OpenSSL"
                },
                {
                    "source_path": os.path.join(openssl_path, "bin", "legacy.dll"),
                    "name": "legacy.dll",
                    "type": "OpenSSL"
                },
                {
                    "source_path": os.path.join(mysql_path, "lib", "libmysql.dll"),
                    "name": "libmysql.dll",
                    "type": "MySQL"
                }
            ]
            
            # Check which DLL files exist
            existing_dlls = []
            missing_dlls = []
            
            for dll_info in dll_files:
                self.log_to_console(f"🔍 Checking: {dll_info['source_path']}")
                if os.path.exists(dll_info["source_path"]):
                    existing_dlls.append(dll_info)
                    self.log_to_console(f"✅ Found: {dll_info['name']}")
                else:
                    missing_dlls.append(dll_info)
                    self.log_to_console(f"❌ Missing: {dll_info['name']} at {dll_info['source_path']}")
            
            if missing_dlls:
                missing_list = "\n".join([f"• {dll['name']} ({dll['type']})" for dll in missing_dlls])
                messagebox.showwarning("Some DLL Files Missing", 
                                     f"The following DLL files were not found:\n\n{missing_list}\n\n"
                                     "Only the available DLL files will be copied.")
                self.log_to_console(f"⚠️ Missing DLL files: {[dll['name'] for dll in missing_dlls]}")
            
            if not existing_dlls:
                messagebox.showerror("No DLL Files Found", 
                                   "No required DLL files were found in the specified locations.")
                self.log_to_console("❌ No DLL files found to copy")
                return
            
            # Show progress dialog
            progress_dialog = self._create_dll_progress_dialog()
            
            # Copy DLL files in a separate thread
            copy_thread = threading.Thread(target=self._copy_dll_files, 
                                         args=(existing_dlls, repack_dir, progress_dialog))
            copy_thread.daemon = True
            copy_thread.start()
            
        except Exception as e:
            error_msg = f"Failed to create DLL files:\n\n{str(e)}"
            messagebox.showerror("DLL Creation Failed", error_msg)
            self.log_to_console(f"❌ DLL creation failed: {str(e)}")
    
    def _find_openssl_path(self):
        """Find OpenSSL installation path from requirements or common locations"""
        # First check if OpenSSL is detected in requirements
        if self.requirements["OpenSSL"]["detected"] and self.requirements["OpenSSL"]["path"]:
            openssl_path = self.requirements["OpenSSL"]["path"]
            self.log_to_console(f"🔍 OpenSSL detected path: {openssl_path}")
            
            # If it's pointing to openssl.exe, get the parent directory (bin -> OpenSSL-Win64)
            if openssl_path.endswith("openssl.exe"):
                openssl_path = os.path.dirname(openssl_path)  # Go up one level from bin to OpenSSL-Win64
                self.log_to_console(f"🔍 Adjusted path (from exe): {openssl_path}")
            # If it's pointing to bin directory, get the parent directory (bin -> OpenSSL-Win64)
            elif openssl_path.endswith("bin"):
                openssl_path = os.path.dirname(openssl_path)  # Go up one level from bin to OpenSSL-Win64
                self.log_to_console(f"🔍 Adjusted path (from bin): {openssl_path}")
            else:
                self.log_to_console(f"🔍 Using path as-is: {openssl_path}")
            
            # Verify the path exists and has a bin directory
            if os.path.exists(openssl_path):
                bin_path = os.path.join(openssl_path, "bin")
                if os.path.exists(bin_path):
                    self.log_to_console(f"✅ OpenSSL path verified: {openssl_path} (bin exists)")
                    return openssl_path
                else:
                    self.log_to_console(f"❌ OpenSSL bin directory not found: {bin_path}")
            else:
                self.log_to_console(f"❌ OpenSSL path does not exist: {openssl_path}")
        
        # Check common OpenSSL installation paths
        self.log_to_console("🔍 Checking common OpenSSL installation paths...")
        common_paths = [
            r"C:\Program Files\OpenSSL-Win64",
            r"C:\Program Files (x86)\OpenSSL-Win32",
            r"C:\OpenSSL-Win64",
            r"C:\OpenSSL-Win32"
        ]
        
        for path in common_paths:
            self.log_to_console(f"🔍 Checking: {path}")
            if os.path.exists(path):
                bin_path = os.path.join(path, "bin")
                if os.path.exists(bin_path):
                    self.log_to_console(f"✅ Found OpenSSL at: {path} (bin exists)")
                    return path
                else:
                    self.log_to_console(f"⚠️ Found OpenSSL directory but no bin: {path}")
        
        self.log_to_console("❌ No OpenSSL installation found")
        return None
    
    def _create_dll_progress_dialog(self):
        """Create progress dialog for DLL copying"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Creating DLL Files")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 200, self.root.winfo_rooty() + 200))
        
        # Title
        title_label = ttk.Label(dialog, text="Creating DLL Files", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(20, 10))
        
        # Status label
        status_label = ttk.Label(dialog, text="Preparing to copy DLL files...", font=("Arial", 10))
        status_label.pack(pady=(0, 20))
        
        # Progress bar
        progress = ttk.Progressbar(dialog, mode='indeterminate', length=300, style='Green.Horizontal.TProgressbar')
        progress.pack(pady=(0, 20))
        progress.start()
        
        # Store references
        dialog.status_label = status_label
        dialog.progress = progress
        
        return dialog
    
    def _copy_dll_files(self, dll_files, repack_dir, dialog):
        """Copy DLL files in background thread"""
        try:
            copied_files = []
            failed_files = []
            
            total_files = len(dll_files)
            
            for i, dll_info in enumerate(dll_files):
                # Update status
                progress_text = f"Copying {dll_info['name']} ({i+1}/{total_files})..."
                self.root.after(0, lambda text=progress_text: dialog.status_label.config(text=text))
                self.log_to_console(f"📁 Copying {dll_info['name']} from {dll_info['type']}...")
                
                try:
                    # Copy the DLL file to Repack directory
                    target_path = os.path.join(repack_dir, dll_info["name"])
                    shutil.copy2(dll_info["source_path"], target_path)
                    copied_files.append(dll_info["name"])
                    self.log_to_console(f"✅ Successfully copied {dll_info['name']}")
                    
                except Exception as e:
                    failed_files.append(f"{dll_info['name']}: {str(e)}")
                    self.log_to_console(f"❌ Failed to copy {dll_info['name']}: {str(e)}")
            
            # Update status and close dialog
            if failed_files:
                self.root.after(0, lambda: dialog.status_label.config(text="DLL copying completed with some errors"))
            else:
                self.root.after(0, lambda: dialog.status_label.config(text="All DLL files copied successfully!"))
            
            self.root.after(0, lambda: dialog.progress.stop())
            self.root.after(0, lambda: dialog.destroy())
            
            # Show completion message
            if copied_files and not failed_files:
                # All files copied successfully
                success_msg = f"All DLL files have been successfully copied!\n\n"
                success_msg += f"Copied files:\n"
                for filename in copied_files:
                    success_msg += f"• {filename}\n"
                success_msg += f"\nTarget location: {repack_dir}"
                
                self.root.after(0, lambda: messagebox.showinfo("DLL Files Created", success_msg))
                self.log_to_console(f"✅ All DLL files copied successfully to: {repack_dir}")
                
            elif copied_files and failed_files:
                # Some files copied, some failed
                partial_msg = f"DLL copying completed with some issues:\n\n"
                partial_msg += f"Successfully copied:\n"
                for filename in copied_files:
                    partial_msg += f"• {filename}\n"
                partial_msg += f"\nFailed to copy:\n"
                for failure in failed_files:
                    partial_msg += f"• {failure}\n"
                partial_msg += f"\nTarget location: {repack_dir}"
                
                self.root.after(0, lambda: messagebox.showwarning("DLL Files Partially Created", partial_msg))
                self.log_to_console(f"⚠️ DLL copying completed with {len(failed_files)} failures")
                
            else:
                # No files copied
                error_msg = f"Failed to copy any DLL files:\n\n"
                for failure in failed_files:
                    error_msg += f"• {failure}\n"
                
                self.root.after(0, lambda: messagebox.showerror("DLL Copy Failed", error_msg))
                self.log_to_console(f"❌ Failed to copy any DLL files")
            
        except Exception as e:
            # Update status and close dialog
            self.root.after(0, lambda: dialog.status_label.config(text="Failed to copy DLL files"))
            self.root.after(0, lambda: dialog.progress.stop())
            self.root.after(0, lambda: dialog.destroy())
            
            # Show error message
            error_msg = f"Failed to copy DLL files:\n\n{str(e)}"
            self.root.after(0, lambda: messagebox.showerror("DLL Copy Failed", error_msg))
            self.log_to_console(f"❌ DLL files copy failed: {str(e)}")

    def initialize_mysql(self):
        """Initialize MySQL database with proper paths"""
        try:
            self.log_to_console("🚀 Starting MySQL initialization...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            repack_dir = os.path.join(app_dir, "Repack")
            mysql_dir = os.path.join(repack_dir, "mysql")
            
            # Check if Repack folder exists
            if not os.path.exists(repack_dir):
                messagebox.showerror("Repack Folder Not Found", 
                                   "Repack folder not found. Please create a repack first using the 'Create Repack' button.")
                self.log_to_console("❌ Repack folder not found")
                return
            
            # Check if MySQL folder exists
            if not os.path.exists(mysql_dir):
                messagebox.showerror("MySQL Folder Not Found", 
                                   "MySQL folder not found in Repack directory. Please use the 'Create MySQL' button first.")
                self.log_to_console("❌ MySQL folder not found in Repack")
                return
            
            # Check if mysqld.exe exists
            mysqld_exe = os.path.join(mysql_dir, "bin", "mysqld.exe")
            if not os.path.exists(mysqld_exe):
                messagebox.showerror("MySQL Executable Not Found", 
                                   f"mysqld.exe not found at:\n{mysqld_exe}\n\n"
                                   "Please ensure MySQL was copied correctly.")
                self.log_to_console(f"❌ mysqld.exe not found at: {mysqld_exe}")
                return
            
            self.log_to_console(f"✅ Found mysqld.exe at: {mysqld_exe}")
            
            # Check if MySQL is already initialized
            data_dir = os.path.join(mysql_dir, "data")
            if os.path.exists(data_dir) and os.listdir(data_dir):
                if messagebox.askyesno("MySQL Already Initialized", 
                                     f"MySQL data directory already exists and contains files:\n\n{data_dir}\n\n"
                                     "Do you want to reinitialize MySQL? This will delete existing data."):
                    self.log_to_console("🗑️ Removing existing MySQL data directory...")
                    shutil.rmtree(data_dir)
                else:
                    self.log_to_console("❌ MySQL initialization cancelled by user")
                    return
            
            # Create required directories
            self._create_mysql_directories(mysql_dir)
            
            # Show progress dialog
            progress_dialog = self._create_mysql_init_progress_dialog()
            
            # Initialize MySQL in a separate thread
            init_thread = threading.Thread(target=self._run_mysql_initialization, 
                                         args=(mysqld_exe, mysql_dir, progress_dialog))
            init_thread.daemon = True
            init_thread.start()
            
        except Exception as e:
            error_msg = f"Failed to initialize MySQL:\n\n{str(e)}"
            messagebox.showerror("MySQL Initialization Failed", error_msg)
            self.log_to_console(f"❌ MySQL initialization failed: {str(e)}")
    
    def _create_mysql_directories(self, mysql_dir):
        """Create required MySQL directories"""
        required_dirs = [
            "data",
            "tmp",
            "logs"
        ]
        
        for dir_name in required_dirs:
            dir_path = os.path.join(mysql_dir, dir_name)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                self.log_to_console(f"📁 Created directory: {dir_path}")
            else:
                self.log_to_console(f"✅ Directory exists: {dir_path}")
    
    def _create_mysql_init_progress_dialog(self):
        """Create progress dialog for MySQL initialization"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Initializing MySQL")
        dialog.geometry("450x250")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 200, self.root.winfo_rooty() + 200))
        
        # Title
        title_label = ttk.Label(dialog, text="Initializing MySQL Database", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(20, 10))
        
        # Status label
        status_label = ttk.Label(dialog, text="Preparing MySQL initialization...", font=("Arial", 10))
        status_label.pack(pady=(0, 20))
        
        # Progress bar
        progress = ttk.Progressbar(dialog, mode='indeterminate', length=350, style='Green.Horizontal.TProgressbar')
        progress.pack(pady=(0, 20))
        progress.start()
        
        # Info text
        info_text = tk.Text(dialog, height=4, width=50, wrap=tk.WORD, font=("Arial", 8))
        info_text.pack(pady=(0, 10))
        info_text.insert(tk.END, "This process will:\n• Set up MySQL environment variables\n• Initialize the MySQL data directory\n• Create default database structure")
        info_text.config(state=tk.DISABLED)
        
        # Store references
        dialog.status_label = status_label
        dialog.progress = progress
        dialog.info_text = info_text
        
        return dialog
    
    def _run_mysql_initialization(self, mysqld_exe, mysql_dir, dialog):
        """Run MySQL initialization in background thread"""
        try:
            # Update status
            self.root.after(0, lambda: dialog.status_label.config(text="Setting up MySQL environment..."))
            self.log_to_console("🔧 Setting up MySQL environment variables...")
            
            # Set up MySQL environment variables
            mysql_env = self._setup_mysql_environment(mysql_dir)
            
            # Update status
            self.root.after(0, lambda: dialog.status_label.config(text="Initializing MySQL data directory..."))
            self.log_to_console("🚀 Starting MySQL initialization process...")
            
            # Run MySQL initialization command
            cmd = [mysqld_exe, "--initialize-insecure"]
            
            # Add MySQL paths as environment variables
            env = os.environ.copy()
            env.update(mysql_env)
            
            self.log_to_console(f"📝 Running command: {' '.join(cmd)}")
            self.log_to_console(f"🔧 Environment variables set: {list(mysql_env.keys())}")
            
            # Execute the command
            result = subprocess.run(cmd, 
                                  cwd=mysql_dir,
                                  env=env,
                                  capture_output=True, 
                                  text=True, 
                                  timeout=300)  # 5 minute timeout
            
            if result.returncode == 0:
                # Success
                self.root.after(0, lambda: dialog.status_label.config(text="MySQL initialized successfully!"))
                self.root.after(0, lambda: dialog.progress.stop())
                self.root.after(0, lambda: dialog.destroy())
                
                # Show success message
                success_msg = f"MySQL has been successfully initialized!\n\n"
                success_msg += f"MySQL directory: {mysql_dir}\n"
                success_msg += f"Data directory: {os.path.join(mysql_dir, 'data')}\n\n"
                success_msg += "MySQL is now ready to use with your AzerothCore server."
                
                self.root.after(0, lambda: messagebox.showinfo("MySQL Initialized", success_msg))
                self.log_to_console("✅ MySQL initialization completed successfully!")
                
            else:
                # Error
                error_msg = f"MySQL initialization failed:\n\n"
                error_msg += f"Return code: {result.returncode}\n"
                if result.stderr:
                    error_msg += f"Error output:\n{result.stderr}\n"
                if result.stdout:
                    error_msg += f"Standard output:\n{result.stdout}"
                
                self.root.after(0, lambda: dialog.status_label.config(text="MySQL initialization failed"))
                self.root.after(0, lambda: dialog.progress.stop())
                self.root.after(0, lambda: dialog.destroy())
                
                self.root.after(0, lambda: messagebox.showerror("MySQL Initialization Failed", error_msg))
                self.log_to_console(f"❌ MySQL initialization failed with return code: {result.returncode}")
                if result.stderr:
                    self.log_to_console(f"❌ Error output: {result.stderr}")
                if result.stdout:
                    self.log_to_console(f"📝 Standard output: {result.stdout}")
            
        except subprocess.TimeoutExpired:
            # Timeout
            self.root.after(0, lambda: dialog.status_label.config(text="MySQL initialization timed out"))
            self.root.after(0, lambda: dialog.progress.stop())
            self.root.after(0, lambda: dialog.destroy())
            
            self.root.after(0, lambda: messagebox.showerror("MySQL Initialization Timeout", 
                                                          "MySQL initialization timed out after 5 minutes.\n\n"
                                                          "This might indicate an issue with the MySQL installation or system resources."))
            self.log_to_console("❌ MySQL initialization timed out")
            
        except Exception as e:
            # Other error
            self.root.after(0, lambda: dialog.status_label.config(text="MySQL initialization failed"))
            self.root.after(0, lambda: dialog.progress.stop())
            self.root.after(0, lambda: dialog.destroy())
            
            error_msg = f"Failed to initialize MySQL:\n\n{str(e)}"
            self.root.after(0, lambda: messagebox.showerror("MySQL Initialization Failed", error_msg))
            self.log_to_console(f"❌ MySQL initialization failed: {str(e)}")
    
    def _setup_mysql_environment(self, mysql_dir):
        """Set up MySQL environment variables for proper initialization"""
        mysql_env = {
            # MySQL paths
            "MYSQL_HOME": mysql_dir,
            "MYSQL_BASE": mysql_dir,
            
            # Required paths for MySQL
            "PATH": f"{os.path.join(mysql_dir, 'bin')};{os.environ.get('PATH', '')}",
            
            # MySQL-specific environment variables
            "MYSQL_UNIX_PORT": os.path.join(mysql_dir, "tmp", "mysql.sock"),
            "MYSQL_TCP_PORT": "3306",
        }
        
        # Log the environment setup
        self.log_to_console("🔧 MySQL environment variables:")
        for key, value in mysql_env.items():
            self.log_to_console(f"   {key} = {value}")
        
        return mysql_env

    def create_myini(self):
        """Create my.ini configuration file for MySQL"""
        try:
            self.log_to_console("📄 Starting my.ini file creation...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            repack_dir = os.path.join(app_dir, "Repack")
            mysql_dir = os.path.join(repack_dir, "mysql")
            myini_path = os.path.join(mysql_dir, "my.ini")
            
            # Check if Repack folder exists
            if not os.path.exists(repack_dir):
                messagebox.showerror("Repack Folder Not Found", 
                                   "Repack folder not found. Please create a repack first using the 'Create Repack' button.")
                self.log_to_console("❌ Repack folder not found")
                return
            
            # Check if MySQL folder exists
            if not os.path.exists(mysql_dir):
                messagebox.showerror("MySQL Folder Not Found", 
                                   "MySQL folder not found in Repack directory. Please use the 'Create MySQL' button first.")
                self.log_to_console("❌ MySQL folder not found in Repack")
                return
            
            # Check if my.ini already exists
            if os.path.exists(myini_path):
                if messagebox.askyesno("My.ini Already Exists", 
                                     f"my.ini file already exists at:\n\n{myini_path}\n\n"
                                     "Do you want to replace it? This will overwrite the existing configuration."):
                    self.log_to_console("🔄 Replacing existing my.ini file...")
                else:
                    self.log_to_console("❌ My.ini creation cancelled by user")
                    return
            
            # Create the my.ini content
            myini_content = '''# MySQL 8.4.2 Settings
[mysqld]
    port = 3306
    basedir="."
    datadir="./data"
    socket = /tmp/mysql.sock

[client]
    default-character-set = utf8mb4
    port = 3306
    socket = /tmp/mysql.sock
'''
            
            # Write the my.ini file
            self.log_to_console(f"📝 Creating my.ini file at: {myini_path}")
            with open(myini_path, 'w', encoding='utf-8') as f:
                f.write(myini_content)
            
            # Verify the file was created successfully
            if os.path.exists(myini_path):
                # Get file size for confirmation
                file_size = os.path.getsize(myini_path)
                
                success_msg = f"my.ini file has been successfully created!\n\n"
                success_msg += f"Location: {myini_path}\n"
                success_msg += f"File size: {file_size} bytes\n\n"
                success_msg += "Configuration settings:\n"
                success_msg += "• Port: 3306\n"
                success_msg += "• Base directory: . (current directory - Repack/mysql)\n"
                success_msg += "• Data directory: ./data (Repack/mysql/data)\n"
                success_msg += "• Socket: /tmp/mysql.sock\n"
                success_msg += "• Character set: utf8mb4 (client)\n\n"
                success_msg += "MySQL is now configured and ready to use."
                
                messagebox.showinfo("My.ini Created", success_msg)
                self.log_to_console("✅ my.ini file created successfully!")
                self.log_to_console(f"📁 File location: {myini_path}")
                self.log_to_console(f"📊 File size: {file_size} bytes")
                
            else:
                raise Exception("File was not created successfully")
                
        except Exception as e:
            error_msg = f"Failed to create my.ini file:\n\n{str(e)}"
            messagebox.showerror("My.ini Creation Failed", error_msg)
            self.log_to_console(f"❌ My.ini creation failed: {str(e)}")

    def start_mysql(self):
        """Start MySQL server with console and standalone options"""
        try:
            self.log_to_console("▶️ Starting MySQL server...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            repack_dir = os.path.join(app_dir, "Repack")
            mysql_dir = os.path.join(repack_dir, "mysql")
            
            # Check if Repack folder exists
            if not os.path.exists(repack_dir):
                messagebox.showerror("Repack Folder Not Found", 
                                   "Repack folder not found. Please create a repack first using the 'Create Repack' button.")
                self.log_to_console("❌ Repack folder not found")
                return
            
            # Check if MySQL folder exists
            if not os.path.exists(mysql_dir):
                messagebox.showerror("MySQL Folder Not Found", 
                                   "MySQL folder not found in Repack directory. Please use the 'Create MySQL' button first.")
                self.log_to_console("❌ MySQL folder not found in Repack")
                return
            
            # Check if mysqld.exe exists
            mysqld_exe = os.path.join(mysql_dir, "bin", "mysqld.exe")
            if not os.path.exists(mysqld_exe):
                messagebox.showerror("MySQL Executable Not Found", 
                                   f"mysqld.exe not found at:\n{mysqld_exe}\n\n"
                                   "Please ensure MySQL was copied correctly.")
                self.log_to_console(f"❌ mysqld.exe not found at: {mysqld_exe}")
                return
            
            self.log_to_console(f"✅ Found mysqld.exe at: {mysqld_exe}")
            
            # Check if MySQL is already running
            if hasattr(self, 'mysql_process') and self.mysql_process and self.mysql_process.poll() is None:
                messagebox.showinfo("MySQL Already Running", 
                                  "MySQL server is already running.\n\n"
                                  "If you need to restart MySQL, please stop it first or restart the application.")
                self.log_to_console("ℹ️ MySQL server is already running")
                return
            
            # Show confirmation dialog
            if messagebox.askyesno("Start MySQL Server", 
                                 f"Start MySQL server with the following command?\n\n"
                                 f"Command: {mysqld_exe} --console --standalone\n\n"
                                 f"Working directory: {mysql_dir}\n\n"
                                 "The MySQL server will run in the background and display output in the console."):
                
                self.log_to_console("🚀 Starting MySQL server...")
                self._start_mysql_server_process(mysqld_exe, mysql_dir)
            else:
                self.log_to_console("❌ MySQL server startup cancelled by user")
                
        except Exception as e:
            error_msg = f"Failed to start MySQL server:\n\n{str(e)}"
            messagebox.showerror("MySQL Startup Failed", error_msg)
            self.log_to_console(f"❌ MySQL startup failed: {str(e)}")
    
    def _start_mysql_server_process(self, mysqld_exe, mysql_dir):
        """Start MySQL server process in background"""
        try:
            # Command arguments
            cmd_args = ["--console", "--standalone"]
            
            self.log_to_console(f"📝 Running command: {mysqld_exe} {' '.join(cmd_args)}")
            self.log_to_console(f"📁 Working directory: {mysql_dir}")
            
            # Start MySQL server process
            self.mysql_process = subprocess.Popen([mysqld_exe] + cmd_args,
                                                cwd=mysql_dir,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.STDOUT,
                                                text=True,
                                                bufsize=1,
                                                universal_newlines=True)
            
            self.log_to_console(f"✅ MySQL server started with PID: {self.mysql_process.pid}")
            
            # Start a thread to monitor MySQL output
            monitor_thread = threading.Thread(target=self._monitor_mysql_output, 
                                            args=(self.mysql_process,))
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Show success message
            success_msg = f"MySQL server has been started successfully!\n\n"
            success_msg += f"Process ID: {self.mysql_process.pid}\n"
            success_msg += f"Command: {mysqld_exe} --console --standalone\n"
            success_msg += f"Working directory: {mysql_dir}\n\n"
            success_msg += "MySQL server is now running in the background.\n"
            success_msg += "Check the Console tab for server output and logs."
            
            messagebox.showinfo("MySQL Server Started", success_msg)
            self.log_to_console("🎉 MySQL server startup completed successfully!")
            
        except Exception as e:
            raise Exception(f"Failed to start MySQL server process: {str(e)}")
    
    def _monitor_mysql_output(self, process):
        """Monitor MySQL server output and log it to console"""
        try:
            self.log_to_console("📊 Starting MySQL output monitoring...")
            
            while True:
                # Read output line by line
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    # Process has terminated
                    break
                
                if output:
                    # Log the output to console (strip newline and add timestamp)
                    output_line = output.strip()
                    if output_line:  # Only log non-empty lines
                        self.root.after(0, lambda line=output_line: self.log_to_console(f"MySQL: {line}"))
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
            
            # Process has ended
            return_code = process.poll()
            self.root.after(0, lambda: self.log_to_console(f"📊 MySQL server process ended with return code: {return_code}"))
            
        except Exception as e:
            self.root.after(0, lambda: self.log_to_console(f"❌ Error monitoring MySQL output: {str(e)}"))

    def stop_mysql(self):
        """Stop MySQL server gracefully, then force kill if needed"""
        try:
            self.log_to_console("⏹️ Stopping MySQL server...")
            
            # First check for MySQL processes started by this application
            app_mysql_running = False
            if hasattr(self, 'mysql_process') and self.mysql_process and self.mysql_process.poll() is None:
                app_mysql_running = True
                self.log_to_console(f"✅ Found MySQL process started by this app (PID: {self.mysql_process.pid})")
            
            # Also check for any running MySQL processes on the system
            running_mysql_processes = self._find_running_mysql_processes()
            
            if not app_mysql_running and not running_mysql_processes:
                messagebox.showinfo("MySQL Not Running", 
                                  "No MySQL server processes are currently running.")
                self.log_to_console("ℹ️ No MySQL server processes found")
                return
            
            # Prepare confirmation message
            confirmation_msg = "Stop MySQL server(s)?\n\n"
            
            if app_mysql_running:
                confirmation_msg += f"Application MySQL (PID: {self.mysql_process.pid})\n"
            
            if running_mysql_processes:
                confirmation_msg += "System MySQL processes:\n"
                for pid, cmd in running_mysql_processes:
                    confirmation_msg += f"• PID {pid}: {cmd}\n"
            
            confirmation_msg += "\nThis will:\n"
            confirmation_msg += "1. Send graceful shutdown signal\n"
            confirmation_msg += "2. Wait 10 seconds for graceful shutdown\n"
            confirmation_msg += "3. Force kill if still running"
            
            # Show confirmation dialog
            if messagebox.askyesno("Stop MySQL Server", confirmation_msg):
                self.log_to_console("🛑 Starting MySQL server shutdown...")
                self._stop_mysql_server_process(running_mysql_processes)
            else:
                self.log_to_console("❌ MySQL server shutdown cancelled by user")
                
        except Exception as e:
            error_msg = f"Failed to stop MySQL server:\n\n{str(e)}"
            messagebox.showerror("MySQL Stop Failed", error_msg)
            self.log_to_console(f"❌ MySQL stop failed: {str(e)}")
    
    def _find_running_mysql_processes(self):
        """Find all running MySQL processes on the system"""
        try:
            self.log_to_console("🔍 Scanning for running MySQL processes...")
            
            # Use tasklist to find MySQL processes
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq mysqld.exe', '/FO', 'CSV'], 
                                  capture_output=True, text=True, timeout=10)
            
            mysql_processes = []
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        # Parse CSV format: "Image Name","PID","Session Name","Session#","Mem Usage"
                        parts = line.split('","')
                        if len(parts) >= 2:
                            pid = parts[1].strip('"')
                            try:
                                pid_int = int(pid)
                                # Get command line for this process
                                cmd_result = subprocess.run(['wmic', 'process', 'where', f'ProcessId={pid}', 'get', 'CommandLine', '/format:list'], 
                                                          capture_output=True, text=True, timeout=10)
                                cmd_line = ""
                                if cmd_result.returncode == 0:
                                    for cmd_line_part in cmd_result.stdout.split('\n'):
                                        if 'CommandLine=' in cmd_line_part:
                                            cmd_line = cmd_line_part.replace('CommandLine=', '').strip()
                                            break
                                
                                if cmd_line:
                                    mysql_processes.append((pid_int, cmd_line))
                                else:
                                    mysql_processes.append((pid_int, "mysqld.exe"))
                                    
                            except ValueError:
                                continue
            
            if mysql_processes:
                self.log_to_console(f"✅ Found {len(mysql_processes)} running MySQL process(es)")
                for pid, cmd in mysql_processes:
                    self.log_to_console(f"   PID {pid}: {cmd}")
            else:
                self.log_to_console("ℹ️ No running MySQL processes found")
            
            return mysql_processes
            
        except Exception as e:
            self.log_to_console(f"❌ Error scanning for MySQL processes: {str(e)}")
            return []
    
    def _stop_mysql_server_process(self, external_processes=None):
        """Stop MySQL server process with graceful shutdown and force kill"""
        try:
            # Show progress dialog
            progress_dialog = self._create_mysql_stop_progress_dialog()
            
            # Stop MySQL in a separate thread
            stop_thread = threading.Thread(target=self._run_mysql_shutdown, 
                                         args=(progress_dialog, external_processes or []))
            stop_thread.daemon = True
            stop_thread.start()
            
        except Exception as e:
            raise Exception(f"Failed to start MySQL shutdown process: {str(e)}")
    
    def _create_mysql_stop_progress_dialog(self):
        """Create progress dialog for MySQL shutdown"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Stopping MySQL Server")
        dialog.geometry("450x200")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 200, self.root.winfo_rooty() + 200))
        
        # Title
        title_label = ttk.Label(dialog, text="Stopping MySQL Server", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(20, 10))
        
        # Status label
        status_label = ttk.Label(dialog, text="Sending graceful shutdown signal...", font=("Arial", 10))
        status_label.pack(pady=(0, 20))
        
        # Progress bar
        progress = ttk.Progressbar(dialog, mode='indeterminate', length=350)
        progress.pack(pady=(0, 20))
        progress.start()
        
        # Info text
        info_text = tk.Text(dialog, height=3, width=50, wrap=tk.WORD, font=("Arial", 8))
        info_text.pack(pady=(0, 10))
        info_text.insert(tk.END, "This process will:\n• Send graceful shutdown signal\n• Wait 10 seconds for shutdown\n• Force kill if still running")
        info_text.config(state=tk.DISABLED)
        
        # Store references
        dialog.status_label = status_label
        dialog.progress = progress
        dialog.info_text = info_text
        
        return dialog
    
    def _run_mysql_shutdown(self, dialog, external_processes=None):
        """Run MySQL shutdown process in background thread"""
        try:
            # Step 1: Send graceful shutdown signal to all mysqld processes
            self.root.after(0, lambda: dialog.status_label.config(text="Sending graceful shutdown signal..."))
            self.log_to_console("🛑 Sending graceful shutdown signal to all mysqld processes...")
            
            # Use taskkill to send graceful shutdown to all mysqld.exe processes
            try:
                result = subprocess.run(['taskkill', '/IM', 'mysqld.exe', '/T'], 
                                      capture_output=True, text=True, timeout=15)
                if result.returncode == 0:
                    self.log_to_console("✅ Graceful shutdown signal sent to all mysqld processes")
                else:
                    self.log_to_console(f"⚠️ Graceful shutdown result: {result.stderr.strip()}")
            except Exception as e:
                self.log_to_console(f"⚠️ Error sending graceful shutdown: {str(e)}")
            
            # Also try to terminate the app MySQL process if it exists
            if hasattr(self, 'mysql_process') and self.mysql_process and self.mysql_process.poll() is None:
                try:
                    self.mysql_process.terminate()
                    self.log_to_console(f"✅ Graceful shutdown signal sent to app MySQL PID: {self.mysql_process.pid}")
                except Exception as e:
                    self.log_to_console(f"⚠️ Error terminating app MySQL process: {str(e)}")
            
            # Step 2: Wait for graceful shutdown
            self.root.after(0, lambda: dialog.status_label.config(text="Waiting for graceful shutdown (10 seconds)..."))
            self.log_to_console("⏳ Waiting 10 seconds for graceful shutdown...")
            
            # Wait up to 10 seconds for graceful shutdown
            time.sleep(10)
            
            # Step 3: Check if any mysqld processes are still running
            self.log_to_console("🔍 Checking if any mysqld processes are still running...")
            try:
                result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq mysqld.exe'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and 'mysqld.exe' in result.stdout:
                    # Some processes are still running, force kill them
                    self.log_to_console("⚠️ Some mysqld processes still running, force killing...")
                    self.root.after(0, lambda: dialog.status_label.config(text="Force killing remaining MySQL processes..."))
                    
                    # Force kill all remaining mysqld processes
                    try:
                        kill_result = subprocess.run(['taskkill', '/F', '/IM', 'mysqld.exe', '/T'], 
                                                   capture_output=True, text=True, timeout=15)
                        if kill_result.returncode == 0:
                            self.log_to_console("✅ Force killed all remaining mysqld processes")
                        else:
                            self.log_to_console(f"⚠️ Force kill result: {kill_result.stderr.strip()}")
                    except Exception as e:
                        self.log_to_console(f"❌ Error force killing mysqld processes: {str(e)}")
                    
                    # Wait a moment for kills to take effect
                    time.sleep(2)
                    
                    self.root.after(0, lambda: dialog.status_label.config(text="MySQL processes force killed!"))
                    self.log_to_console("✅ MySQL processes force killed successfully")
                    
                    # Close dialog and show success
                    self.root.after(0, lambda: dialog.progress.stop())
                    self.root.after(0, lambda: dialog.destroy())
                    
                    self.root.after(0, lambda: messagebox.showinfo("MySQL Stopped", 
                                                                "MySQL processes have been force killed."))
                else:
                    # All processes stopped gracefully
                    self.root.after(0, lambda: dialog.status_label.config(text="MySQL stopped gracefully!"))
                    self.log_to_console("✅ All MySQL processes stopped gracefully")
                    
                    # Close dialog and show success
                    self.root.after(0, lambda: dialog.progress.stop())
                    self.root.after(0, lambda: dialog.destroy())
                    
                    self.root.after(0, lambda: messagebox.showinfo("MySQL Stopped", 
                                                                "All MySQL processes have been stopped gracefully."))
            except Exception as e:
                self.log_to_console(f"❌ Error checking for remaining processes: {str(e)}")
                # Assume success if we can't check
                self.root.after(0, lambda: dialog.status_label.config(text="MySQL shutdown completed"))
                self.root.after(0, lambda: dialog.progress.stop())
                self.root.after(0, lambda: dialog.destroy())
                self.root.after(0, lambda: messagebox.showinfo("MySQL Stopped", "MySQL shutdown completed."))
            
        except Exception as e:
            # Error during shutdown
            self.root.after(0, lambda: dialog.status_label.config(text="MySQL shutdown failed"))
            self.root.after(0, lambda: dialog.progress.stop())
            self.root.after(0, lambda: dialog.destroy())
            
            error_msg = f"Failed to stop MySQL server:\n\n{str(e)}"
            self.root.after(0, lambda: messagebox.showerror("MySQL Stop Failed", error_msg))
            self.log_to_console(f"❌ MySQL shutdown failed: {str(e)}")
        
        finally:
            # Clean up the process reference
            if hasattr(self, 'mysql_process'):
                self.mysql_process = None
                self.log_to_console("🧹 MySQL process reference cleaned up")

    def config_mysql(self):
        """Configure MySQL with root password and create configuration files"""
        try:
            self.log_to_console("⚙️ Starting MySQL configuration...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            repack_dir = os.path.join(app_dir, "Repack")
            mysql_dir = os.path.join(repack_dir, "mysql")
            build_dir = os.path.join(app_dir, "Build")
            
            # Check if Repack folder exists
            if not os.path.exists(repack_dir):
                messagebox.showerror("Repack Folder Not Found", 
                                   "Repack folder not found. Please create a repack first using the 'Create Repack' button.")
                self.log_to_console("❌ Repack folder not found")
                return
            
            # Check if MySQL folder exists
            if not os.path.exists(mysql_dir):
                messagebox.showerror("MySQL Folder Not Found", 
                                   "MySQL folder not found in Repack directory. Please use the 'Create MySQL' button first.")
                self.log_to_console("❌ MySQL folder not found in Repack")
                return
            
            # Check if Build folder exists
            if not os.path.exists(build_dir):
                messagebox.showerror("Build Folder Not Found", 
                                   "Build folder not found. Please build the project first.")
                self.log_to_console("❌ Build folder not found")
                return
            
            # Get SQL root password from user
            sql_root_password = self._get_sql_root_password()
            if not sql_root_password:
                self.log_to_console("❌ MySQL configuration cancelled - no password provided")
                return
            
            # Show progress dialog
            progress_dialog = self._create_mysql_config_progress_dialog()
            
            # Configure MySQL in a separate thread
            config_thread = threading.Thread(target=self._run_mysql_configuration, 
                                           args=(mysql_dir, build_dir, sql_root_password, progress_dialog))
            config_thread.daemon = True
            config_thread.start()
            
        except Exception as e:
            error_msg = f"Failed to configure MySQL:\n\n{str(e)}"
            messagebox.showerror("MySQL Configuration Failed", error_msg)
            self.log_to_console(f"❌ MySQL configuration failed: {str(e)}")
    
    def _get_sql_root_password(self):
        """Get SQL root password from user input"""
        # Create password input dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("MySQL Root Password")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 200, self.root.winfo_rooty() + 200))
        
        # Title
        title_label = ttk.Label(dialog, text="MySQL Root Password", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(20, 10))
        
        # Description
        desc_label = ttk.Label(dialog, text="Choose initial MySQL root password:", font=("Arial", 10))
        desc_label.pack(pady=(0, 10))
        
        # Password entry
        password_var = tk.StringVar()
        password_entry = ttk.Entry(dialog, textvariable=password_var, show="*", width=30, font=("Arial", 10))
        password_entry.pack(pady=(0, 20))
        password_entry.focus()
        
        # Buttons frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=(0, 20))
        
        # OK button
        def ok_clicked():
            dialog.result = password_var.get()
            dialog.destroy()
        
        ok_button = ttk.Button(button_frame, text="OK", command=ok_clicked)
        ok_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        def cancel_clicked():
            dialog.result = None
            dialog.destroy()
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=cancel_clicked)
        cancel_button.pack(side=tk.LEFT)
        
        # Bind Enter key to OK button
        password_entry.bind('<Return>', lambda e: ok_clicked())
        
        # Wait for dialog to close
        dialog.wait_window()
        
        return getattr(dialog, 'result', None)
    
    def _create_mysql_config_progress_dialog(self):
        """Create progress dialog for MySQL configuration"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Configuring MySQL")
        dialog.geometry("450x250")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 200, self.root.winfo_rooty() + 200))
        
        # Title
        title_label = ttk.Label(dialog, text="Configuring MySQL", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(20, 10))
        
        # Status label
        status_label = ttk.Label(dialog, text="Preparing MySQL configuration...", font=("Arial", 10))
        status_label.pack(pady=(0, 20))
        
        # Progress bar
        progress = ttk.Progressbar(dialog, mode='indeterminate', length=350)
        progress.pack(pady=(0, 20))
        progress.start()
        
        # Info text
        info_text = tk.Text(dialog, height=4, width=50, wrap=tk.WORD, font=("Arial", 8))
        info_text.pack(pady=(0, 10))
        info_text.insert(tk.END, "This process will:\n• Create MySQLConfigCNF file\n• Create MySQLUpdateCNF file\n• Set MySQL root password")
        info_text.config(state=tk.DISABLED)
        
        # Store references
        dialog.status_label = status_label
        dialog.progress = progress
        dialog.info_text = info_text
        
        return dialog
    
    def _run_mysql_configuration(self, mysql_dir, build_dir, sql_root_password, dialog):
        """Run MySQL configuration in background thread"""
        try:
            # Update status
            self.root.after(0, lambda: dialog.status_label.config(text="Creating MySQL configuration files..."))
            self.log_to_console("📝 Creating MySQL configuration files...")
            
            # Create MySQLConfigCNF file
            mysql_config_cnf = os.path.join(mysql_dir, "mysqlconfig.cnf")
            self._create_mysql_config_file(mysql_config_cnf, sql_root_password)
            self.log_to_console(f"✅ Created MySQLConfigCNF: {mysql_config_cnf}")
            
            # Create MySQLUpdateCNF file
            database_dir = os.path.join(build_dir, "bin", "Release", "database")
            os.makedirs(database_dir, exist_ok=True)
            mysql_update_cnf = os.path.join(database_dir, "mysqlupdate.cnf")
            self._create_mysql_config_file(mysql_update_cnf, sql_root_password)
            self.log_to_console(f"✅ Created MySQLUpdateCNF: {mysql_update_cnf}")
            
            # Update status
            self.root.after(0, lambda: dialog.status_label.config(text="Setting MySQL root password..."))
            self.log_to_console("🔐 Setting MySQL root password...")
            
            # Set MySQL root password
            self._set_mysql_root_password(mysql_dir, sql_root_password)
            
            # Success
            self.root.after(0, lambda: dialog.status_label.config(text="MySQL configuration completed!"))
            self.root.after(0, lambda: dialog.progress.stop())
            self.root.after(0, lambda: dialog.destroy())
            
            # Show success message
            success_msg = f"MySQL has been successfully configured!\n\n"
            success_msg += f"Configuration files created:\n"
            success_msg += f"• {mysql_config_cnf}\n"
            success_msg += f"• {mysql_update_cnf}\n\n"
            success_msg += f"Root password set to: {sql_root_password}\n\n"
            success_msg += "MySQL is now fully configured and ready to use."
            
            self.root.after(0, lambda: messagebox.showinfo("MySQL Configured", success_msg))
            self.log_to_console("✅ MySQL configuration completed successfully!")
            
        except Exception as e:
            # Error
            self.root.after(0, lambda: dialog.status_label.config(text="MySQL configuration failed"))
            self.root.after(0, lambda: dialog.progress.stop())
            self.root.after(0, lambda: dialog.destroy())
            
            error_msg = f"Failed to configure MySQL:\n\n{str(e)}"
            self.root.after(0, lambda: messagebox.showerror("MySQL Configuration Failed", error_msg))
            self.log_to_console(f"❌ MySQL configuration failed: {str(e)}")
    
    def _create_mysql_config_file(self, file_path, sql_root_password):
        """Create MySQL configuration file with client settings"""
        config_content = f"""[client]
user = root
password = {sql_root_password}
host = 127.0.0.1
port = 3306
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        self.log_to_console(f"📄 Created configuration file: {file_path}")
    
    def _set_mysql_root_password(self, mysql_dir, sql_root_password):
        """Set MySQL root password using mysql command"""
        mysql_exe = os.path.join(mysql_dir, "bin", "mysql.exe")
        
        if not os.path.exists(mysql_exe):
            raise Exception(f"mysql.exe not found at: {mysql_exe}")
        
        # SQL command to set root password
        sql_cmd = f"ALTER USER 'root'@'localhost' IDENTIFIED BY '{sql_root_password}';"
        
        # Command arguments
        cmd_args = ["-uroot", f"--execute={sql_cmd}"]
        
        self.log_to_console(f"🔐 Setting root password using: {mysql_exe}")
        self.log_to_console(f"📝 SQL command: {sql_cmd}")
        
        # Execute the command
        result = subprocess.run([mysql_exe] + cmd_args,
                              cwd=mysql_dir,
                              capture_output=True,
                              text=True,
                              timeout=30)
        
        if result.returncode == 0:
            self.log_to_console(f"✅ Root password set successfully")
            self.log_to_console(f"🔐 Root password set to: {sql_root_password}")
        else:
            error_msg = f"Failed to set root password. Return code: {result.returncode}"
            if result.stderr:
                error_msg += f"\nError: {result.stderr}"
            if result.stdout:
                error_msg += f"\nOutput: {result.stdout}"
            raise Exception(error_msg)

    def create_database(self):
        """Create AzerothCore database using the official SQL file"""
        try:
            self.log_to_console("🗃️ Starting database creation...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            repack_dir = os.path.join(app_dir, "Repack")
            mysql_dir = os.path.join(repack_dir, "mysql")
            
            # Check if Repack folder exists
            if not os.path.exists(repack_dir):
                messagebox.showerror("Repack Folder Not Found", 
                                   "Repack folder not found. Please create a repack first using the 'Create Repack' button.")
                self.log_to_console("❌ Repack folder not found")
                return
            
            # Check if MySQL folder exists
            if not os.path.exists(mysql_dir):
                messagebox.showerror("MySQL Folder Not Found", 
                                   "MySQL folder not found in Repack directory. Please use the 'Create MySQL' button first.")
                self.log_to_console("❌ MySQL folder not found in Repack")
                return
            
            # Get MySQL root password from user
            mysql_password = self._get_mysql_password_for_database()
            if not mysql_password:
                self.log_to_console("❌ Database creation cancelled - no password provided")
                return
            
            # Show progress dialog
            progress_dialog = self._create_database_progress_dialog()
            
            # Create database in a separate thread
            db_thread = threading.Thread(target=self._run_database_creation, 
                                       args=(mysql_dir, mysql_password, progress_dialog))
            db_thread.daemon = True
            db_thread.start()
            
        except Exception as e:
            error_msg = f"Failed to create database:\n\n{str(e)}"
            messagebox.showerror("Database Creation Failed", error_msg)
            self.log_to_console(f"❌ Database creation failed: {str(e)}")
    
    def _get_mysql_password_for_database(self):
        """Get MySQL root password from user input for database creation"""
        # Create password input dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("MySQL Root Password")
        dialog.geometry("450x250")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 200, self.root.winfo_rooty() + 200))
        
        # Title
        title_label = ttk.Label(dialog, text="MySQL Root Password", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(20, 10))
        
        # Description
        desc_label = ttk.Label(dialog, text="Enter the MySQL root password to create the AzerothCore database:", 
                              font=("Arial", 10), wraplength=400)
        desc_label.pack(pady=(0, 10))
        
        # Password entry
        password_var = tk.StringVar()
        password_entry = ttk.Entry(dialog, textvariable=password_var, show="*", width=30, font=("Arial", 10))
        password_entry.pack(pady=(0, 20))
        password_entry.focus()
        
        # Buttons frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=(0, 20))
        
        # OK button
        def ok_clicked():
            dialog.result = password_var.get()
            dialog.destroy()
        
        ok_button = ttk.Button(button_frame, text="OK", command=ok_clicked)
        ok_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        def cancel_clicked():
            dialog.result = None
            dialog.destroy()
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=cancel_clicked)
        cancel_button.pack(side=tk.LEFT)
        
        # Bind Enter key to OK button
        password_entry.bind('<Return>', lambda e: ok_clicked())
        
        # Wait for dialog to close
        dialog.wait_window()
        
        return getattr(dialog, 'result', None)
    
    def _create_database_progress_dialog(self):
        """Create progress dialog for database creation"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Creating Database")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 200, self.root.winfo_rooty() + 200))
        
        # Title
        title_label = ttk.Label(dialog, text="Creating AzerothCore Database", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(20, 10))
        
        # Status label
        status_label = ttk.Label(dialog, text="Preparing database creation...", font=("Arial", 10))
        status_label.pack(pady=(0, 20))
        
        # Progress bar
        progress = ttk.Progressbar(dialog, mode='indeterminate', length=400, style='Green.Horizontal.TProgressbar')
        progress.pack(pady=(0, 20))
        progress.start()
        
        # Info text
        info_text = tk.Text(dialog, height=6, width=60, wrap=tk.WORD, font=("Arial", 8))
        info_text.pack(pady=(0, 10))
        info_text.insert(tk.END, "This process will:\n• Download create_mysql.sql from AzerothCore repository\n• Execute the SQL script with MySQL root privileges\n• Create the AzerothCore database structure\n• Set up initial database configuration")
        info_text.config(state=tk.DISABLED)
        
        # Store references
        dialog.status_label = status_label
        dialog.progress = progress
        dialog.info_text = info_text
        
        return dialog
    
    def _run_database_creation(self, mysql_dir, mysql_password, dialog):
        """Run database creation in background thread"""
        try:
            # Update status
            self.root.after(0, lambda: dialog.status_label.config(text="Downloading SQL file from AzerothCore repository..."))
            self.log_to_console("📥 Downloading create_mysql.sql from AzerothCore repository...")
            
            # Download the SQL file
            sql_file_path = self._download_create_mysql_sql()
            self.log_to_console(f"✅ Downloaded SQL file: {sql_file_path}")
            
            # Update status
            self.root.after(0, lambda: dialog.status_label.config(text="Executing SQL script with MySQL..."))
            self.log_to_console("🗃️ Executing SQL script with MySQL...")
            
            # Execute the SQL file
            self._execute_sql_file(mysql_dir, sql_file_path, mysql_password)
            
            # Clean up temp files
            self._cleanup_temp_files(sql_file_path)
            
            # Success
            self.root.after(0, lambda: dialog.status_label.config(text="Database creation completed!"))
            self.root.after(0, lambda: dialog.progress.stop())
            self.root.after(0, lambda: dialog.destroy())
            
            # Show success message
            success_msg = f"AzerothCore database has been successfully created!\n\n"
            success_msg += f"SQL file executed: {sql_file_path}\n\n"
            success_msg += "The database is now ready for use with your AzerothCore server."
            
            self.root.after(0, lambda: messagebox.showinfo("Database Created", success_msg))
            self.log_to_console("✅ Database creation completed successfully!")
            
        except Exception as e:
            # Clean up temp files even on error
            try:
                if 'sql_file_path' in locals():
                    self._cleanup_temp_files(sql_file_path)
            except:
                pass  # Don't let cleanup errors interfere with error reporting
            
            # Error
            self.root.after(0, lambda: dialog.status_label.config(text="Database creation failed"))
            self.root.after(0, lambda: dialog.progress.stop())
            self.root.after(0, lambda: dialog.destroy())
            
            error_msg = f"Failed to create database:\n\n{str(e)}"
            self.root.after(0, lambda: messagebox.showerror("Database Creation Failed", error_msg))
            self.log_to_console(f"❌ Database creation failed: {str(e)}")
    
    def _download_create_mysql_sql(self):
        """Download the create_mysql.sql file from AzerothCore repository"""
        sql_url = "https://raw.githubusercontent.com/azerothcore/azerothcore-wotlk/master/data/sql/create/create_mysql.sql"
        
        # Create temp directory for SQL file
        app_dir = self._get_app_dir()
        temp_dir = os.path.join(app_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        sql_file_path = os.path.join(temp_dir, "create_mysql.sql")
        
        self.log_to_console(f"📥 Downloading from: {sql_url}")
        
        try:
            # Download the file
            urllib.request.urlretrieve(sql_url, sql_file_path)
            
            # Verify the file was downloaded and has content
            if os.path.exists(sql_file_path) and os.path.getsize(sql_file_path) > 0:
                self.log_to_console(f"✅ SQL file downloaded successfully: {sql_file_path}")
                return sql_file_path
            else:
                raise Exception("Downloaded SQL file is empty or corrupted")
                
        except Exception as e:
            raise Exception(f"Failed to download SQL file from {sql_url}: {str(e)}")
    
    def _execute_sql_file(self, mysql_dir, sql_file_path, mysql_password):
        """Execute the SQL file with MySQL root privileges"""
        mysql_exe = os.path.join(mysql_dir, "bin", "mysql.exe")
        
        if not os.path.exists(mysql_exe):
            raise Exception(f"mysql.exe not found at: {mysql_exe}")
        
        if not os.path.exists(sql_file_path):
            raise Exception(f"SQL file not found at: {sql_file_path}")
        
        # Command arguments for MySQL
        cmd_args = [
            "-uroot",
            f"-p{mysql_password}",
            "--execute=source " + sql_file_path.replace("\\", "/")
        ]
        
        self.log_to_console(f"🗃️ Executing SQL file using: {mysql_exe}")
        self.log_to_console(f"📝 SQL file: {sql_file_path}")
        
        # Execute the command
        result = subprocess.run([mysql_exe] + cmd_args,
                              cwd=mysql_dir,
                              capture_output=True,
                              text=True,
                              timeout=120)  # 2 minute timeout for database creation
        
        if result.returncode == 0:
            self.log_to_console(f"✅ SQL file executed successfully")
            if result.stdout:
                self.log_to_console(f"📄 MySQL output: {result.stdout}")
        else:
            error_msg = f"Failed to execute SQL file. Return code: {result.returncode}"
            if result.stderr:
                error_msg += f"\nError: {result.stderr}"
            if result.stdout:
                error_msg += f"\nOutput: {result.stdout}"
            raise Exception(error_msg)
    
    def _cleanup_temp_files(self, sql_file_path):
        """Clean up temporary files and directories created during database creation"""
        try:
            # Get the temp directory path
            temp_dir = os.path.dirname(sql_file_path)
            
            # Remove the SQL file
            if os.path.exists(sql_file_path):
                os.remove(sql_file_path)
                self.log_to_console(f"🗑️ Cleaned up SQL file: {sql_file_path}")
            
            # Remove the temp directory if it's empty
            if os.path.exists(temp_dir):
                try:
                    # Check if directory is empty
                    if not os.listdir(temp_dir):
                        os.rmdir(temp_dir)
                        self.log_to_console(f"🗑️ Cleaned up temp directory: {temp_dir}")
                    else:
                        self.log_to_console(f"⚠️ Temp directory not empty, keeping: {temp_dir}")
                except OSError as e:
                    self.log_to_console(f"⚠️ Could not remove temp directory {temp_dir}: {str(e)}")
                    
        except Exception as e:
            self.log_to_console(f"⚠️ Error during temp file cleanup: {str(e)}")

    def get_data(self):
        """Download and extract the latest data.zip from wowgaming/client-data repository"""
        try:
            self.log_to_console("📥 Starting data download...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            repack_dir = os.path.join(app_dir, "Repack")
            data_dir = os.path.join(repack_dir, "data")
            
            # Check if Repack folder exists
            if not os.path.exists(repack_dir):
                messagebox.showerror("Repack Folder Not Found", 
                                   "Repack folder not found. Please create a repack first using the 'Create Repack' button.")
                self.log_to_console("❌ Repack folder not found")
                return
            
            # Show progress dialog
            progress_dialog = self._create_data_download_progress_dialog()
            
            # Download and extract data in a separate thread
            data_thread = threading.Thread(target=self._run_data_download, 
                                         args=(data_dir, progress_dialog))
            data_thread.daemon = True
            data_thread.start()
            
        except Exception as e:
            error_msg = f"Failed to get data:\n\n{str(e)}"
            messagebox.showerror("Data Download Failed", error_msg)
            self.log_to_console(f"❌ Data download failed: {str(e)}")
    
    def copy_data(self):
        """Open file explorer in the repack directory"""
        try:
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            repack_dir = os.path.join(app_dir, "Repack")
            
            # Check if Repack folder exists
            if not os.path.exists(repack_dir):
                messagebox.showerror("Repack Folder Not Found", 
                                   "Repack folder not found. Please create a repack first using the 'Create Repack' button.")
                self.log_to_console("❌ Repack folder not found")
                return
            
            # Open file explorer in repack directory
            os.startfile(repack_dir)
            self.log_to_console(f"📁 Opened file explorer in: {repack_dir}")
            
        except Exception as e:
            error_msg = f"Failed to open file explorer:\n\n{str(e)}"
            messagebox.showerror("File Explorer Failed", error_msg)
            self.log_to_console(f"❌ Failed to open file explorer: {str(e)}")
    
    def _create_data_download_progress_dialog(self):
        """Create progress dialog for data download and extraction"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Downloading Data")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 200, self.root.winfo_rooty() + 200))
        
        # Title
        title_label = ttk.Label(dialog, text="Downloading AzerothCore Data", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(20, 10))
        
        # Status label
        status_label = ttk.Label(dialog, text="Preparing data download...", font=("Arial", 10))
        status_label.pack(pady=(0, 20))
        
        # Progress bar - blue style like build process
        progress = ttk.Progressbar(dialog, mode='determinate', length=400, style='Blue.Horizontal.TProgressbar')
        progress.pack(pady=(0, 20))
        progress['value'] = 0
        progress['maximum'] = 100
        
        # Info text
        info_text = tk.Text(dialog, height=6, width=60, wrap=tk.WORD, font=("Arial", 8))
        info_text.pack(pady=(0, 10))
        info_text.insert(tk.END, "This process will:\n• Download the latest data.zip from wowgaming/client-data repository\n• Extract all folders from data.zip to Repack/data\n• Set up the complete AzerothCore data structure\n• Include maps, dbc, mmaps, vmaps, and other game data")
        info_text.config(state=tk.DISABLED)
        
        # Button frame for Cancel button
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=(0, 20))
        
        # Cancel button
        cancel_button = ttk.Button(button_frame, text="Cancel Download", 
                                 command=lambda: self._cancel_data_download(dialog))
        cancel_button.pack(side=tk.LEFT)
        
        # Store references
        dialog.status_label = status_label
        dialog.progress = progress
        dialog.info_text = info_text
        dialog.cancelled = False
        dialog.cancel_button = cancel_button
        
        return dialog
    
    def _cancel_data_download(self, dialog):
        """Cancel the current data download process"""
        if messagebox.askyesno("Cancel Download", 
                              "Are you sure you want to cancel the data download process?"):
            dialog.cancelled = True
            self.log_to_console(f"❌ User cancelled data download process")
            dialog.destroy()
        else:
            self.log_to_console(f"🔄 User chose to continue data download process")
    
    def _run_data_download(self, data_dir, dialog):
        """Run data download and extraction in background thread"""
        try:
            # Check for cancellation
            if dialog.cancelled:
                self.log_to_console("❌ Data download cancelled by user")
                return
            
            # Update status and progress
            self.root.after(0, lambda: dialog.status_label.config(text="Getting latest release information..."))
            self.root.after(0, lambda: dialog.progress.config(value=10))
            self.log_to_console("📥 Getting latest release information from wowgaming/client-data...")
            
            # Get the latest release download URL
            download_url = self._get_latest_data_download_url()
            self.log_to_console(f"✅ Found latest release: {download_url}")
            
            # Check for cancellation
            if dialog.cancelled:
                self.log_to_console("❌ Data download cancelled by user")
                return
            
            # Update status and progress
            self.root.after(0, lambda: dialog.status_label.config(text="Downloading data.zip..."))
            self.root.after(0, lambda: dialog.progress.config(value=30))
            self.log_to_console("📥 Downloading data.zip...")
            
            # Download the data.zip file
            zip_file_path = self._download_data_zip(download_url)
            self.log_to_console(f"✅ Downloaded data.zip: {zip_file_path}")
            
            # Check for cancellation
            if dialog.cancelled:
                # Clean up downloaded file if cancelled
                if os.path.exists(zip_file_path):
                    os.remove(zip_file_path)
                    self.log_to_console("🧹 Cleaned up partially downloaded file")
                    # Clean up temp directory if empty
                    temp_dir = os.path.dirname(zip_file_path)
                    try:
                        if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                            os.rmdir(temp_dir)
                            self.log_to_console(f"🧹 Cleaned up temp directory: {temp_dir}")
                    except OSError:
                        pass
                self.log_to_console("❌ Data download cancelled by user")
                return
            
            # Update status and progress
            self.root.after(0, lambda: dialog.status_label.config(text="Extracting data to Repack/data..."))
            self.root.after(0, lambda: dialog.progress.config(value=60))
            self.log_to_console("📦 Extracting data.zip to Repack/data...")
            
            # Extract the zip file
            self._extract_data_zip(zip_file_path, data_dir)
            self.log_to_console(f"✅ Extracted data to: {data_dir}")
            
            # Check for cancellation
            if dialog.cancelled:
                self.log_to_console("❌ Data download cancelled by user")
                return
            
            # Clean up the zip file
            os.remove(zip_file_path)
            self.log_to_console("🧹 Cleaned up temporary zip file")
            
            # Clean up the temp directory if empty
            temp_dir = os.path.dirname(zip_file_path)
            if os.path.exists(temp_dir):
                try:
                    if not os.listdir(temp_dir):
                        os.rmdir(temp_dir)
                        self.log_to_console(f"🧹 Cleaned up temp directory: {temp_dir}")
                    else:
                        self.log_to_console(f"⚠️ Temp directory not empty, keeping: {temp_dir}")
                except OSError as e:
                    self.log_to_console(f"⚠️ Could not remove temp directory: {str(e)}")
            
            # Success - complete progress bar
            self.root.after(0, lambda: dialog.status_label.config(text="Data download completed!"))
            self.root.after(0, lambda: dialog.progress.config(value=100))
            self.root.after(0, lambda: dialog.destroy())
            
            # Show success message
            success_msg = f"AzerothCore data has been successfully downloaded and extracted!\n\n"
            success_msg += f"Data extracted to: {data_dir}\n\n"
            success_msg += "The data folder now contains all necessary game files including maps, dbc, mmaps, and vmaps."
            
            self.root.after(0, lambda: messagebox.showinfo("Data Downloaded", success_msg))
            self.log_to_console("✅ Data download and extraction completed successfully!")
            
        except Exception as e:
            # Check if it was cancelled
            if dialog.cancelled:
                self.log_to_console("❌ Data download cancelled by user")
                return
            
            # Error
            self.root.after(0, lambda: dialog.status_label.config(text="Data download failed"))
            self.root.after(0, lambda: dialog.progress.config(value=0))
            self.root.after(0, lambda: dialog.destroy())
            
            error_msg = f"Failed to download data:\n\n{str(e)}"
            self.root.after(0, lambda: messagebox.showerror("Data Download Failed", error_msg))
            self.log_to_console(f"❌ Data download failed: {str(e)}")
    
    def _get_latest_data_download_url(self):
        """Get the download URL for the latest data.zip from wowgaming/client-data releases or use configured URL"""
        import json
        
        # Check if a custom data URL is configured
        if hasattr(self, 'data_url') and self.data_url:
            self.log_to_console(f"📡 Using configured data URL: {self.data_url}")
            return self.data_url
        
        # GitHub API URL for latest release
        api_url = "https://api.github.com/repos/wowgaming/client-data/releases/latest"
        
        self.log_to_console(f"📡 Fetching release info from: {api_url}")
        
        try:
            # Create request with proper headers
            request = urllib.request.Request(api_url)
            request.add_header('User-Agent', 'AzerothCoreBuilder/1.0')
            
            # Get the release information
            with urllib.request.urlopen(request) as response:
                release_data = json.loads(response.read().decode())
            
            # Find the data.zip asset
            for asset in release_data.get('assets', []):
                if asset['name'] == 'data.zip':
                    download_url = asset['browser_download_url']
                    self.log_to_console(f"✅ Found data.zip download URL: {download_url}")
                    return download_url
            
            raise Exception("data.zip asset not found in latest release")
            
        except Exception as e:
            raise Exception(f"Failed to get latest release information: {str(e)}")
    
    def _download_data_zip(self, download_url):
        """Download the data.zip file"""
        # Create temp directory for zip file
        app_dir = self._get_app_dir()
        temp_dir = os.path.join(app_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        zip_file_path = os.path.join(temp_dir, "data.zip")
        
        self.log_to_console(f"📥 Downloading from: {download_url}")
        
        try:
            # Create request with proper headers
            request = urllib.request.Request(download_url)
            request.add_header('User-Agent', 'AzerothCoreBuilder/1.0')
            
            # Download the file using urlopen and write to file
            with urllib.request.urlopen(request) as response:
                with open(zip_file_path, 'wb') as f:
                    f.write(response.read())
            
            # Verify the file was downloaded and has content
            if os.path.exists(zip_file_path) and os.path.getsize(zip_file_path) > 0:
                file_size = os.path.getsize(zip_file_path)
                self.log_to_console(f"✅ data.zip downloaded successfully: {zip_file_path} ({file_size:,} bytes)")
                return zip_file_path
            else:
                raise Exception("Downloaded data.zip file is empty or corrupted")
                
        except Exception as e:
            raise Exception(f"Failed to download data.zip from {download_url}: {str(e)}")
    
    def _extract_data_zip(self, zip_file_path, data_dir):
        """Extract the data.zip file to Repack/data directory"""
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        self.log_to_console(f"📦 Extracting {zip_file_path} to {data_dir}")
        
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                # Get list of files in the zip
                file_list = zip_ref.namelist()
                self.log_to_console(f"📋 Found {len(file_list)} files in data.zip")
                
                # Extract all files
                zip_ref.extractall(data_dir)
                
                # Log the extracted folders
                extracted_folders = set()
                for file_path in file_list:
                    if '/' in file_path:
                        folder = file_path.split('/')[0]
                        extracted_folders.add(folder)
                
                if extracted_folders:
                    self.log_to_console(f"📁 Extracted folders: {', '.join(sorted(extracted_folders))}")
                
        except Exception as e:
            raise Exception(f"Failed to extract data.zip: {str(e)}")

    def create_mysql_bat(self):
        """Create MySQL.bat file in the Repack directory"""
        try:
            self.log_to_console("📄 Creating MySQL.bat file...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            repack_dir = os.path.join(app_dir, "Repack")
            
            # Check if Repack folder exists
            if not os.path.exists(repack_dir):
                messagebox.showerror("Repack Folder Not Found", 
                                   "Repack folder not found. Please create a repack first using the 'Create Repack' button.")
                self.log_to_console("❌ Repack folder not found")
                return
            
            # Define the MySQL.bat file path
            mysql_bat_path = os.path.join(repack_dir, "MySQL.bat")
            
            # Define the batch file content
            bat_content = '''@echo off
SET NAME=F@bagun's MySQL 8.4.2 Portable Server
TITLE %NAME%
COLOR 0A

echo.
echo  =====================================================================================
echo.
echo                 ====== F@bagun's MySQL 8.4.2 Portable Server =====
echo.
echo    MySQL Server is starting... Please keep this window open while the server runs.
echo    To stop the server, close this window or press CTRL+C.
echo.
echo  =====================================================================================
echo.

cd .\\mysql\\bin
call mysqld --console --standalone --basedir=.. --datadir=..\\data
if errorlevel 1 goto error
goto finish

:error
echo.
echo  =======================================================================================
echo.
echo                                MySQL Startup Failed
echo.
echo    Please check the error messages above and try again.
echo.
echo  =======================================================================================
echo.
pause

:finish'''
            
            # Write the batch file
            with open(mysql_bat_path, 'w', encoding='utf-8') as f:
                f.write(bat_content)
            
            self.log_to_console(f"✅ MySQL.bat file created successfully at: {mysql_bat_path}")
            messagebox.showinfo("MySQL.bat Created", 
                              f"MySQL.bat file has been created successfully!\n\n"
                              f"Location: {mysql_bat_path}\n\n"
                              "This batch file will start your MySQL server in portable mode.")
            
        except Exception as e:
            error_msg = f"Failed to create MySQL.bat file:\n\n{str(e)}"
            messagebox.showerror("MySQL.bat Creation Failed", error_msg)
            self.log_to_console(f"❌ Failed to create MySQL.bat: {str(e)}")

    def run_database_sql(self):
        """Run database SQL files from GitSource/azerothcore-wotlk/data/sql"""
        try:
            self.log_to_console("🗃️ Starting database SQL import process...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            git_source_dir = os.path.join(app_dir, "GitSource")
            azerothcore_dir = os.path.join(git_source_dir, "azerothcore-wotlk")
            sql_base_dir = os.path.join(azerothcore_dir, "data", "sql")
            
            # Check if GitSource directory exists
            if not os.path.exists(git_source_dir):
                messagebox.showerror("GitSource Not Found", 
                                   "GitSource folder not found. Please clone an AzerothCore repository first using the Build tab.")
                self.log_to_console("❌ GitSource folder not found")
                return
            
            # Check if azerothcore-wotlk directory exists
            if not os.path.exists(azerothcore_dir):
                messagebox.showerror("AzerothCore Repository Not Found", 
                                   "azerothcore-wotlk folder not found in GitSource. Please clone an AzerothCore repository first.")
                self.log_to_console("❌ azerothcore-wotlk folder not found")
                return
            
            # Check if SQL directory exists
            if not os.path.exists(sql_base_dir):
                messagebox.showerror("SQL Directory Not Found", 
                                   f"SQL directory not found at: {sql_base_dir}\n\n"
                                   "Please ensure you have cloned a complete AzerothCore repository.")
                self.log_to_console("❌ SQL directory not found")
                return
            
            # Check if MySQL is running
            if not self._check_mysql_running():
                self.log_to_console("❌ Database SQL import cancelled - MySQL not running")
                return
            
            # Get MySQL connection details
            mysql_details = self._get_mysql_connection_details()
            if not mysql_details:
                self.log_to_console("❌ Database SQL import cancelled - no connection details provided")
                return
            
            # Show progress dialog
            progress_dialog = self._create_sql_import_progress_dialog()
            
            # Import SQL files in a separate thread
            import_thread = threading.Thread(target=self._run_sql_import, 
                                           args=(sql_base_dir, mysql_details, progress_dialog))
            import_thread.daemon = True
            import_thread.start()
            
        except Exception as e:
            error_msg = f"Failed to start database SQL import:\n\n{str(e)}"
            messagebox.showerror("SQL Import Failed", error_msg)
            self.log_to_console(f"❌ Database SQL import failed: {str(e)}")

    def _check_mysql_running(self):
        """Check if MySQL is running and show popup dialog"""
        self.log_to_console("🔍 Checking if MySQL is running...")
        
        # Create MySQL running check dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("MySQL Status Check")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 200, self.root.winfo_rooty() + 200))
        
        # Title
        title_label = ttk.Label(dialog, text="MySQL Status Check", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(20, 10))
        
        # Description
        desc_label = ttk.Label(dialog, 
                              text="Is MySQL currently running?\n\n"
                                   "Please ensure MySQL is started before importing SQL files.",
                              font=("Arial", 10), wraplength=350)
        desc_label.pack(pady=(0, 20))
        
        # Buttons frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=(0, 20))
        
        # Result variable
        dialog.result = None
        
        # Yes button
        def yes_clicked():
            dialog.result = True
            dialog.destroy()
        
        yes_button = ttk.Button(button_frame, text="Yes, MySQL is running", command=yes_clicked)
        yes_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # No button
        def no_clicked():
            dialog.result = False
            dialog.destroy()
        
        no_button = ttk.Button(button_frame, text="No, MySQL is not running", command=no_clicked)
        no_button.pack(side=tk.LEFT)
        
        # Wait for dialog result
        dialog.wait_window()
        
        if dialog.result:
            self.log_to_console("✅ User confirmed MySQL is running")
            return True
        else:
            self.log_to_console("❌ User confirmed MySQL is not running")
            messagebox.showinfo("MySQL Not Running", 
                              "Please start MySQL first using the 'Start MySQL' button in the Repack Setup tab.")
            return False

    def _get_mysql_connection_details(self):
        """Get MySQL connection details from user"""
        # Create connection details dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("MySQL Connection Details")
        dialog.geometry("450x350")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 150, self.root.winfo_rooty() + 150))
        
        # Title
        title_label = ttk.Label(dialog, text="MySQL Connection Details", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(20, 10))
        
        # Description
        desc_label = ttk.Label(dialog, 
                              text="Enter MySQL connection details for SQL import.\n"
                                   "Use a standard MySQL account (not root).",
                              font=("Arial", 10), wraplength=400)
        desc_label.pack(pady=(0, 20))
        
        # Connection details frame
        details_frame = ttk.Frame(dialog)
        details_frame.pack(pady=(0, 20))
        
        # Host
        ttk.Label(details_frame, text="Host:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        host_var = tk.StringVar(value="127.0.0.1")
        host_entry = ttk.Entry(details_frame, textvariable=host_var, width=20, font=("Arial", 10))
        host_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Port
        ttk.Label(details_frame, text="Port:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        port_var = tk.StringVar(value="3306")
        port_entry = ttk.Entry(details_frame, textvariable=port_var, width=20, font=("Arial", 10))
        port_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Username
        ttk.Label(details_frame, text="Username:", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        user_var = tk.StringVar(value="acore")
        user_entry = ttk.Entry(details_frame, textvariable=user_var, width=20, font=("Arial", 10))
        user_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Password
        ttk.Label(details_frame, text="Password:", font=("Arial", 10)).grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        password_var = tk.StringVar()
        password_entry = ttk.Entry(details_frame, textvariable=password_var, show="*", width=20, font=("Arial", 10))
        password_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        password_entry.focus()
        
        
        # Buttons frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=(0, 20))
        
        # Result variable
        dialog.result = None
        
        # OK button
        def ok_clicked():
            if not password_var.get().strip():
                messagebox.showerror("Password Required", "Please enter a password.")
                return
            dialog.result = {
                "host": host_var.get().strip(),
                "port": port_var.get().strip(),
                "user": user_var.get().strip(),
                "password": password_var.get().strip()
            }
            dialog.destroy()
        
        ok_button = ttk.Button(button_frame, text="OK", command=ok_clicked)
        ok_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        def cancel_clicked():
            dialog.result = None
            dialog.destroy()
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=cancel_clicked)
        cancel_button.pack(side=tk.LEFT)
        
        # Wait for dialog result
        dialog.wait_window()
        
        if dialog.result:
            self.log_to_console(f"✅ MySQL connection details provided: {dialog.result['user']}@{dialog.result['host']}:{dialog.result['port']}")
            return dialog.result
        else:
            self.log_to_console("❌ MySQL connection details cancelled")
            return None

    def _create_sql_import_progress_dialog(self):
        """Create progress dialog for SQL import"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Importing Database SQL")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))
        
        # Title
        title_label = ttk.Label(dialog, text="Importing Database SQL Files", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(20, 10))
        
        # Status label
        status_label = ttk.Label(dialog, text="Preparing to import SQL files...", font=("Arial", 10))
        status_label.pack(pady=(0, 20))
        
        # Progress bar
        progress = ttk.Progressbar(dialog, mode='determinate', length=400)
        progress.pack(pady=(0, 20))
        
        # Info text
        info_text = tk.Text(dialog, height=6, width=60, wrap=tk.WORD, font=("Arial", 8))
        info_text.pack(pady=(0, 10))
        info_text.insert(tk.END, "This process will import SQL files for:\n• acore_auth database\n• acore_characters database\n• acore_world database\n\nPlease wait while the import process completes...")
        info_text.config(state=tk.DISABLED)
        
        # Store references and add dialog state tracking
        dialog.status_label = status_label
        dialog.progress = progress
        dialog.info_text = info_text
        dialog.is_valid = True  # Flag to track if dialog is still valid
        
        # Override destroy method to set flag
        original_destroy = dialog.destroy
        def safe_destroy():
            dialog.is_valid = False
            original_destroy()
        dialog.destroy = safe_destroy
        
        return dialog

    def _run_sql_import(self, sql_base_dir, mysql_details, dialog):
        """Run SQL import in background thread"""
        try:
            # Ask for root credentials once at the beginning for database creation
            root_credentials = self._ask_root_credentials_once()
            if not root_credentials:
                self.log_to_console("❌ SQL import cancelled - root credentials not provided")
                self._safe_update_dialog(dialog, lambda: dialog.destroy())
                return
            
            # Define database paths (following PowerShell script structure)
            auth_db_scripts_path = os.path.join(sql_base_dir, "base", "db_auth")
            auth_db_update_scripts_path = os.path.join(sql_base_dir, "updates", "db_auth")
            auth_db_pending_update_scripts_path = os.path.join(sql_base_dir, "updates", "pending_db_auth")
            
            character_db_scripts_path = os.path.join(sql_base_dir, "base", "db_characters")
            character_db_update_scripts_path = os.path.join(sql_base_dir, "updates", "db_characters")
            character_db_pending_update_scripts_path = os.path.join(sql_base_dir, "updates", "pending_db_characters")
            
            world_db_scripts_path = os.path.join(sql_base_dir, "base", "db_world")
            world_db_update_scripts_path = os.path.join(sql_base_dir, "updates", "db_world")
            world_db_pending_update_scripts_path = os.path.join(sql_base_dir, "updates", "pending_db_world")
            
            # Log the paths
            self.log_to_console(f"📁 SQL base directory: {sql_base_dir}")
            self.log_to_console(f"📁 Auth DB scripts: {auth_db_scripts_path}")
            self.log_to_console(f"📁 Character DB scripts: {character_db_scripts_path}")
            self.log_to_console(f"📁 World DB scripts: {world_db_scripts_path}")
            
            # Total operations count
            total_operations = 9  # 3 databases × 3 script types each
            current_operation = 0
            
            # Import SQL scripts for acore_auth database
            self._safe_update_dialog(dialog, lambda: dialog.status_label.config(text="Importing acore_auth database scripts..."))
            self._safe_update_dialog(dialog, lambda: dialog.progress.config(value=(current_operation / total_operations) * 100))
            self._import_sql_scripts("acore_auth", auth_db_scripts_path, mysql_details, dialog, root_credentials)
            current_operation += 1
            
            self._safe_update_dialog(dialog, lambda: dialog.progress.config(value=(current_operation / total_operations) * 100))
            self._import_sql_scripts("acore_auth", auth_db_update_scripts_path, mysql_details, dialog, root_credentials)
            current_operation += 1
            
            self._safe_update_dialog(dialog, lambda: dialog.progress.config(value=(current_operation / total_operations) * 100))
            self._import_sql_scripts("acore_auth", auth_db_pending_update_scripts_path, mysql_details, dialog, root_credentials)
            current_operation += 1
            
            # Import SQL scripts for acore_characters database
            self._safe_update_dialog(dialog, lambda: dialog.status_label.config(text="Importing acore_characters database scripts..."))
            self._safe_update_dialog(dialog, lambda: dialog.progress.config(value=(current_operation / total_operations) * 100))
            self._import_sql_scripts("acore_characters", character_db_scripts_path, mysql_details, dialog, root_credentials)
            current_operation += 1
            
            self._safe_update_dialog(dialog, lambda: dialog.progress.config(value=(current_operation / total_operations) * 100))
            self._import_sql_scripts("acore_characters", character_db_update_scripts_path, mysql_details, dialog, root_credentials)
            current_operation += 1
            
            self._safe_update_dialog(dialog, lambda: dialog.progress.config(value=(current_operation / total_operations) * 100))
            self._import_sql_scripts("acore_characters", character_db_pending_update_scripts_path, mysql_details, dialog, root_credentials)
            current_operation += 1
            
            # Import SQL scripts for acore_world database
            self._safe_update_dialog(dialog, lambda: dialog.status_label.config(text="Importing acore_world database scripts..."))
            self._safe_update_dialog(dialog, lambda: dialog.progress.config(value=(current_operation / total_operations) * 100))
            self._import_sql_scripts("acore_world", world_db_scripts_path, mysql_details, dialog, root_credentials)
            current_operation += 1
            
            self._safe_update_dialog(dialog, lambda: dialog.progress.config(value=(current_operation / total_operations) * 100))
            self._import_sql_scripts("acore_world", world_db_update_scripts_path, mysql_details, dialog, root_credentials)
            current_operation += 1
            
            self._safe_update_dialog(dialog, lambda: dialog.progress.config(value=(current_operation / total_operations) * 100))
            self._import_sql_scripts("acore_world", world_db_pending_update_scripts_path, mysql_details, dialog, root_credentials)
            current_operation += 1
            
            # Complete
            self._safe_update_dialog(dialog, lambda: dialog.status_label.config(text="Database SQL import completed!"))
            self._safe_update_dialog(dialog, lambda: dialog.progress.config(value=100))
            self._safe_update_dialog(dialog, lambda: dialog.destroy())
            
            # Show success message
            success_msg = f"Database SQL files have been successfully imported!\n\n"
            success_msg += f"Imported for databases:\n"
            success_msg += f"• acore_auth\n"
            success_msg += f"• acore_characters\n"
            success_msg += f"• acore_world\n\n"
            success_msg += f"All SQL scripts have been processed."
            
            self.root.after(0, lambda: messagebox.showinfo("SQL Import Complete", success_msg))
            self.log_to_console("✅ Database SQL import completed successfully!")
            
        except Exception as e:
            # Error
            self._safe_update_dialog(dialog, lambda: dialog.status_label.config(text="SQL import failed"))
            self._safe_update_dialog(dialog, lambda: dialog.destroy())
            
            error_msg = f"Failed to import database SQL files:\n\n{str(e)}"
            self.root.after(0, lambda: messagebox.showerror("SQL Import Failed", error_msg))
            self.log_to_console(f"❌ Database SQL import failed: {str(e)}")

    def _safe_update_dialog(self, dialog, update_func):
        """Safely update dialog widgets, checking if dialog is still valid"""
        try:
            if hasattr(dialog, 'is_valid') and dialog.is_valid:
                self.root.after(0, update_func)
        except Exception as e:
            # If dialog update fails, just log it and continue
            self.log_to_console(f"⚠️ Dialog update failed (dialog may be closed): {str(e)}")

    def _ask_root_credentials_once(self):
        """Ask for root credentials once at the beginning of SQL import process"""
        # Create root credentials dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Root MySQL Credentials")
        dialog.geometry("500x350")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 150, self.root.winfo_rooty() + 100))
        
        # Title
        title_label = ttk.Label(dialog, text="Root MySQL Credentials", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(20, 10))
        
        # Description
        desc_label = ttk.Label(dialog, 
                              text="Database creation requires root privileges.\n\n"
                                   "Please provide root MySQL credentials that will be used\n"
                                   "to create any missing databases during the SQL import process.\n\n"
                                   "These credentials will be used for all database creation requests.",
                              font=("Arial", 10), wraplength=450)
        desc_label.pack(pady=(0, 20))
        
        # Root credentials frame
        root_frame = ttk.LabelFrame(dialog, text="Root MySQL Credentials", padding=15)
        root_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Root username
        ttk.Label(root_frame, text="Root Username:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        root_user_var = tk.StringVar(value="root")
        root_user_entry = ttk.Entry(root_frame, textvariable=root_user_var, width=20, font=("Arial", 10))
        root_user_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Root password
        ttk.Label(root_frame, text="Root Password:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        root_password_var = tk.StringVar()
        root_password_entry = ttk.Entry(root_frame, textvariable=root_password_var, show="*", width=20, font=("Arial", 10))
        root_password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        root_password_entry.focus()
        
        # Buttons frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=(0, 20))
        
        # Result variable
        dialog.result = None
        
        # OK button
        def ok_clicked():
            if not root_password_var.get().strip():
                messagebox.showerror("Password Required", "Please enter the root password.")
                return
            dialog.result = {
                "create": True,
                "root_user": root_user_var.get().strip(),
                "root_password": root_password_var.get().strip()
            }
            dialog.destroy()
        
        ok_button = ttk.Button(button_frame, text="OK", command=ok_clicked)
        ok_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        def cancel_clicked():
            dialog.result = None
            dialog.destroy()
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=cancel_clicked)
        cancel_button.pack(side=tk.LEFT)
        
        # Wait for dialog result
        dialog.wait_window()
        
        if dialog.result:
            self.log_to_console(f"✅ Root credentials provided: {dialog.result['root_user']}")
            return dialog.result
        else:
            self.log_to_console("❌ Root credentials cancelled")
            return None

    def _import_sql_scripts(self, database_name, scripts_path, mysql_details, dialog, root_credentials):
        """Import SQL scripts from a specific path to a database"""
        try:
            # Check if scripts path exists
            if not os.path.exists(scripts_path):
                self.log_to_console(f"⚠️ Scripts path does not exist: {scripts_path}")
                return
            
            # Get all SQL files in the directory
            sql_files = []
            for file in os.listdir(scripts_path):
                if file.lower().endswith('.sql'):
                    sql_files.append(os.path.join(scripts_path, file))
            
            if not sql_files:
                self.log_to_console(f"⚠️ No SQL files found in: {scripts_path}")
                return
            
            # Sort files for consistent processing
            sql_files.sort()
            
            self.log_to_console(f"📚 Found {len(sql_files)} SQL files in {scripts_path}")
            
            # Import each SQL file
            for sql_file in sql_files:
                self._import_single_sql_file(database_name, sql_file, mysql_details, root_credentials)
                
        except Exception as e:
            self.log_to_console(f"❌ Error importing SQL scripts from {scripts_path}: {str(e)}")
            raise

    def _import_single_sql_file(self, database_name, sql_file, mysql_details, root_credentials=None):
        """Import a single SQL file to the specified database"""
        try:
            # Get MySQL executable path
            mysql_exe = self._get_mysql_executable_path()
            if not mysql_exe:
                raise Exception("MySQL executable not found")
            
            # Check if SQL file contains database creation statements
            required_databases = self._detect_required_databases(sql_file)
            
            # Create any required databases that don't exist
            for required_db in required_databases:
                if not self._database_exists(required_db, mysql_details):
                    if root_credentials and root_credentials.get("create", False):
                        self.log_to_console(f"🗃️ Creating database '{required_db}' using root privileges...")
                        self._create_database(required_db, mysql_details, root_credentials)
                    else:
                        self.log_to_console(f"⚠️ Skipping {os.path.basename(sql_file)} - database {required_db} not created (no root credentials)")
                        return
            
            # Prepare MySQL command using environment variable for password
            import os
            env = os.environ.copy()
            env['MYSQL_PWD'] = mysql_details['password']
            
            cmd = [
                mysql_exe,
                f"-h{mysql_details['host']}",
                f"-P{mysql_details['port']}",
                f"-u{mysql_details['user']}",
                database_name
            ]
            
            self.log_to_console(f"📄 Importing {os.path.basename(sql_file)} to {database_name}...")
            
            # Execute MySQL command with timeout for large files
            with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
                result = subprocess.run(cmd, stdin=f, capture_output=True, text=True, timeout=300, env=env)
            
            if result.returncode == 0:
                self.log_to_console(f"✅ Successfully imported {os.path.basename(sql_file)} to {database_name}")
            else:
                error_msg = f"Failed to import {os.path.basename(sql_file)}: {result.stderr}"
                self.log_to_console(f"❌ {error_msg}")
                
                # Check if error is related to missing database
                if "Access denied" in result.stderr and "database" in result.stderr:
                    self.log_to_console(f"💡 This error might be due to missing database permissions or database not existing")
                
                # Don't raise exception for individual file failures, just log them
                
        except subprocess.TimeoutExpired:
            self.log_to_console(f"⏰ Timeout importing {os.path.basename(sql_file)} - file may be too large")
        except Exception as e:
            self.log_to_console(f"❌ Error importing {os.path.basename(sql_file)}: {str(e)}")

    def _detect_required_databases(self, sql_file):
        """Detect databases that the SQL file requires"""
        required_databases = set()
        
        try:
            with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Look for USE statements
            import re
            use_pattern = r'USE\s+`?([a-zA-Z_][a-zA-Z0-9_]*)`?'
            use_matches = re.findall(use_pattern, content, re.IGNORECASE)
            required_databases.update(use_matches)
            
            # Look for CREATE DATABASE statements (more precise pattern)
            create_db_pattern = r'CREATE\s+DATABASE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?([a-zA-Z_][a-zA-Z0-9_]*)`?'
            create_matches = re.findall(create_db_pattern, content, re.IGNORECASE)
            required_databases.update(create_matches)
            
            # Look for INSERT INTO database.table patterns
            insert_pattern = r'INSERT\s+INTO\s+`?([a-zA-Z_][a-zA-Z0-9_]*)`?\.'
            insert_matches = re.findall(insert_pattern, content, re.IGNORECASE)
            required_databases.update(insert_matches)
            
            # Look for UPDATE database.table patterns
            update_pattern = r'UPDATE\s+`?([a-zA-Z_][a-zA-Z0-9_]*)`?\.'
            update_matches = re.findall(update_pattern, content, re.IGNORECASE)
            required_databases.update(update_matches)
            
            # Look for SELECT FROM database.table patterns
            select_pattern = r'FROM\s+`?([a-zA-Z_][a-zA-Z0-9_]*)`?\.'
            select_matches = re.findall(select_pattern, content, re.IGNORECASE)
            required_databases.update(select_matches)
            
            # Remove common MySQL system databases and SQL keywords
            system_dbs = {'mysql', 'information_schema', 'performance_schema', 'sys'}
            sql_keywords = {'if', 'not', 'exists', 'where', 'from', 'into', 'update', 'select', 'insert', 'delete', 'create', 'drop', 'alter', 'table', 'database', 'index', 'view', 'procedure', 'function', 'trigger', 'event', 'user', 'grant', 'revoke', 'show', 'describe', 'explain', 'use', 'set', 'declare', 'begin', 'end', 'case', 'when', 'then', 'else', 'loop', 'while', 'repeat', 'until', 'leave', 'iterate', 'return', 'call', 'load', 'replace', 'values', 'default', 'null', 'auto_increment', 'primary', 'key', 'unique', 'index', 'foreign', 'references', 'constraint', 'check', 'cascade', 'restrict', 'no', 'action', 'on', 'off', 'true', 'false', 'and', 'or', 'in', 'like', 'between', 'is', 'as', 'order', 'by', 'group', 'having', 'limit', 'offset', 'union', 'all', 'distinct', 'asc', 'desc', 'inner', 'left', 'right', 'outer', 'join', 'cross', 'natural', 'using', 'with', 'recursive', 'window', 'over', 'partition', 'rows', 'range', 'preceding', 'following', 'current', 'row', 'unbounded', 'first', 'last', 'value', 'lag', 'lead', 'rank', 'dense_rank', 'row_number', 'percent_rank', 'cume_dist', 'ntile', 'first_value', 'last_value', 'nth_value'}
            required_databases = required_databases - system_dbs - sql_keywords
            
            if required_databases:
                self.log_to_console(f"🔍 Detected required databases in {os.path.basename(sql_file)}: {', '.join(required_databases)}")
            
            return list(required_databases)
            
        except Exception as e:
            self.log_to_console(f"⚠️ Could not analyze SQL file {os.path.basename(sql_file)}: {str(e)}")
            return []

    def _database_exists(self, database_name, mysql_details):
        """Check if a database exists"""
        try:
            mysql_exe = self._get_mysql_executable_path()
            if not mysql_exe:
                return False
            
            # Use environment variable for password
            import os
            env = os.environ.copy()
            env['MYSQL_PWD'] = mysql_details['password']
            
            # Use SHOW DATABASES to check if database exists
            cmd = [
                mysql_exe,
                f"-h{mysql_details['host']}",
                f"-P{mysql_details['port']}",
                f"-u{mysql_details['user']}",
                "-e", f"SHOW DATABASES LIKE '{database_name}';"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, env=env)
            
            if result.returncode == 0:
                exists = database_name in result.stdout
                if exists:
                    self.log_to_console(f"✅ Database '{database_name}' exists")
                else:
                    self.log_to_console(f"❌ Database '{database_name}' does not exist")
                return exists
            else:
                self.log_to_console(f"⚠️ Could not check if database '{database_name}' exists: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_to_console(f"⚠️ Error checking database '{database_name}': {str(e)}")
            return False

    def _ask_create_database(self, database_name):
        """Ask user if they want to create a new database and get root credentials if needed"""
        # Create database creation dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Database")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 150, self.root.winfo_rooty() + 100))
        
        # Title
        title_label = ttk.Label(dialog, text="Create New Database", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(20, 10))
        
        # Description
        desc_label = ttk.Label(dialog, 
                              text=f"The SQL file requires database '{database_name}' which does not exist.\n\n"
                                   f"Database creation requires root privileges.\n"
                                   f"After creation, the database will be accessible to all users.",
                              font=("Arial", 10), wraplength=450)
        desc_label.pack(pady=(0, 20))
        
        # Root credentials frame
        root_frame = ttk.LabelFrame(dialog, text="Root MySQL Credentials", padding=15)
        root_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Root username
        ttk.Label(root_frame, text="Root Username:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        root_user_var = tk.StringVar(value="root")
        root_user_entry = ttk.Entry(root_frame, textvariable=root_user_var, width=20, font=("Arial", 10))
        root_user_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Root password
        ttk.Label(root_frame, text="Root Password:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        root_password_var = tk.StringVar()
        root_password_entry = ttk.Entry(root_frame, textvariable=root_password_var, show="*", width=20, font=("Arial", 10))
        root_password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        root_password_entry.focus()
        
        # Buttons frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=(0, 20))
        
        # Result variable
        dialog.result = None
        
        # Yes button
        def yes_clicked():
            if not root_password_var.get().strip():
                messagebox.showerror("Password Required", "Please enter the root password.")
                return
            dialog.result = {
                "create": True,
                "root_user": root_user_var.get().strip(),
                "root_password": root_password_var.get().strip()
            }
            dialog.destroy()
        
        yes_button = ttk.Button(button_frame, text="Yes, Create Database", command=yes_clicked)
        yes_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # No button
        def no_clicked():
            dialog.result = {"create": False}
            dialog.destroy()
        
        no_button = ttk.Button(button_frame, text="No, Skip This File", command=no_clicked)
        no_button.pack(side=tk.LEFT)
        
        # Wait for dialog result
        dialog.wait_window()
        
        if dialog.result and dialog.result.get("create", False):
            self.log_to_console(f"✅ User chose to create database '{database_name}' with root privileges")
            return dialog.result
        else:
            self.log_to_console(f"❌ User chose not to create database '{database_name}'")
            return None

    def _create_database(self, database_name, mysql_details, root_credentials):
        """Create a new database using root credentials and grant permissions to acore user"""
        try:
            mysql_exe = self._get_mysql_executable_path()
            if not mysql_exe:
                raise Exception("MySQL executable not found")
            
            self.log_to_console(f"🗃️ Creating database '{database_name}' using root privileges...")
            
            # Create database command using root credentials
            import os
            env = os.environ.copy()
            env['MYSQL_PWD'] = root_credentials['root_password']
            
            # Step 1: Create the database using root
            sql_command = f"CREATE DATABASE IF NOT EXISTS `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            cmd = [
                mysql_exe,
                f"-h{mysql_details['host']}",
                f"-P{mysql_details['port']}",
                f"-u{root_credentials['root_user']}",
                "-e", sql_command
            ]
            
            self.log_to_console(f"🔧 Creating database with root: {' '.join(cmd)}")
            self.log_to_console(f"🔧 SQL Command: {sql_command}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, env=env)
            
            if result.returncode != 0:
                error_msg = f"Failed to create database '{database_name}': {result.stderr}"
                self.log_to_console(f"❌ {error_msg}")
                return False
            
            self.log_to_console(f"✅ Successfully created database '{database_name}' with root privileges")
            
            # Step 2: Grant all privileges on the new database to the acore user
            acore_user = mysql_details['user']
            grant_commands = [
                f"GRANT ALL PRIVILEGES ON `{database_name}`.* TO '{acore_user}'@'localhost';",
                f"GRANT ALL PRIVILEGES ON `{database_name}`.* TO '{acore_user}'@'%';",
                "FLUSH PRIVILEGES;"
            ]
            
            for grant_cmd in grant_commands:
                grant_sql = grant_cmd
                grant_command = [
                    mysql_exe,
                    f"-h{mysql_details['host']}",
                    f"-P{mysql_details['port']}",
                    f"-u{root_credentials['root_user']}",
                    "-e", grant_sql
                ]
                
                self.log_to_console(f"🔧 Granting permissions: {grant_sql}")
                grant_result = subprocess.run(grant_command, capture_output=True, text=True, timeout=30, env=env)
                
                if grant_result.returncode == 0:
                    self.log_to_console(f"✅ Successfully granted permissions for '{acore_user}' on '{database_name}'")
                else:
                    self.log_to_console(f"⚠️ Warning: Could not grant permissions: {grant_result.stderr}")
            
            self.log_to_console(f"🎉 Database '{database_name}' created and configured for '{acore_user}' access")
            return True
                
        except Exception as e:
            self.log_to_console(f"❌ Error creating database '{database_name}': {str(e)}")
            return False

    def _get_mysql_executable_path(self):
        """Get MySQL executable path from Repack folder first, then fallback to system locations"""
        # First priority: Check Repack/mysql/bin directory
        app_dir = self._get_app_dir()
        repack_mysql_bin = os.path.join(app_dir, "Repack", "mysql", "bin", "mysql.exe")
        
        self.log_to_console(f"🔍 Checking Repack MySQL path: {repack_mysql_bin}")
        if os.path.exists(repack_mysql_bin):
            self.log_to_console(f"✅ Using Repack MySQL executable: {repack_mysql_bin}")
            return repack_mysql_bin
        
        # Second priority: Check if MySQL is detected in requirements
        if self.requirements["MySQL"]["detected"] and self.requirements["MySQL"]["path"]:
            mysql_path = self.requirements["MySQL"]["path"]
            self.log_to_console(f"🔍 MySQL detected path: {mysql_path}")
            
            # If it's pointing to mysql.exe, use it directly
            if mysql_path.endswith("mysql.exe"):
                if os.path.exists(mysql_path):
                    self.log_to_console(f"✅ Using MySQL executable: {mysql_path}")
                    return mysql_path
            # If it's pointing to bin directory, look for mysql.exe
            elif mysql_path.endswith("bin"):
                mysql_exe = os.path.join(mysql_path, "mysql.exe")
                if os.path.exists(mysql_exe):
                    self.log_to_console(f"✅ Using MySQL executable: {mysql_exe}")
                    return mysql_exe
        
        # Third priority: Check common MySQL installation paths
        self.log_to_console("🔍 Checking common MySQL installation paths...")
        common_paths = [
            r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe",
            r"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe",
            r"C:\Program Files (x86)\MySQL\MySQL Server 8.0\bin\mysql.exe",
            r"C:\Program Files (x86)\MySQL\MySQL Server 8.4\bin\mysql.exe"
        ]
        
        for path in common_paths:
            self.log_to_console(f"🔍 Checking: {path}")
            if os.path.exists(path):
                self.log_to_console(f"✅ Found MySQL executable at: {path}")
                return path
        
        # Last resort: Check if mysql is in PATH
        try:
            result = subprocess.run(["mysql", "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.log_to_console("✅ MySQL found in system PATH")
                return "mysql"
        except:
            pass
        
        self.log_to_console("❌ No MySQL executable found")
        return None

    def run_module_sql(self):
        """Run module SQL files from GitSource/azerothcore-wotlk/modules"""
        try:
            self.log_to_console("📚 Starting module SQL import process...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            git_source_dir = os.path.join(app_dir, "GitSource")
            azerothcore_dir = os.path.join(git_source_dir, "azerothcore-wotlk")
            modules_dir = os.path.join(azerothcore_dir, "modules")
            
            # Check if GitSource directory exists
            if not os.path.exists(git_source_dir):
                messagebox.showerror("GitSource Not Found", 
                                   "GitSource folder not found. Please clone an AzerothCore repository first using the Build tab.")
                self.log_to_console("❌ GitSource folder not found")
                return
            
            # Check if azerothcore-wotlk directory exists
            if not os.path.exists(azerothcore_dir):
                messagebox.showerror("AzerothCore Repository Not Found", 
                                   "azerothcore-wotlk folder not found in GitSource. Please clone an AzerothCore repository first.")
                self.log_to_console("❌ azerothcore-wotlk folder not found")
                return
            
            # Check if modules directory exists
            if not os.path.exists(modules_dir):
                messagebox.showerror("Modules Directory Not Found", 
                                   f"Modules directory not found at: {modules_dir}\n\n"
                                   "Please ensure you have cloned a complete AzerothCore repository with modules.")
                self.log_to_console("❌ Modules directory not found")
                return
            
            # Check if MySQL is running
            if not self._check_mysql_running():
                self.log_to_console("❌ Module SQL import cancelled - MySQL not running")
                return
            
            # Get MySQL connection details
            mysql_details = self._get_mysql_connection_details()
            if not mysql_details:
                self.log_to_console("❌ Module SQL import cancelled - no connection details provided")
                return
            
            # Show progress dialog
            progress_dialog = self._create_module_sql_import_progress_dialog()
            
            # Import SQL files in a separate thread
            import_thread = threading.Thread(target=self._run_module_sql_import, 
                                           args=(modules_dir, mysql_details, progress_dialog))
            import_thread.daemon = True
            import_thread.start()
            
        except Exception as e:
            error_msg = f"Failed to start module SQL import:\n\n{str(e)}"
            messagebox.showerror("Module SQL Import Failed", error_msg)
            self.log_to_console(f"❌ Module SQL import failed: {str(e)}")

    def _create_module_sql_import_progress_dialog(self):
        """Create progress dialog for module SQL import"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Importing Module SQL Files")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))
        
        # Title
        title_label = ttk.Label(dialog, text="Importing Module SQL Files", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(20, 10))
        
        # Status label
        status_label = ttk.Label(dialog, text="Preparing to import module SQL files...", font=("Arial", 10))
        status_label.pack(pady=(0, 20))
        
        # Progress bar
        progress = ttk.Progressbar(dialog, mode='determinate', length=400)
        progress.pack(pady=(0, 20))
        
        # Info text
        info_text = tk.Text(dialog, height=6, width=60, wrap=tk.WORD, font=("Arial", 8))
        info_text.pack(pady=(0, 10))
        info_text.insert(tk.END, "This process will import SQL files from:\n• auth/character/world folders in modules\n• Other SQL files outside these folders\n\nPlease wait while the import process completes...")
        info_text.config(state=tk.DISABLED)
        
        # Store references and add dialog state tracking
        dialog.status_label = status_label
        dialog.progress = progress
        dialog.info_text = info_text
        dialog.is_valid = True  # Flag to track if dialog is still valid
        
        # Override destroy method to set flag
        original_destroy = dialog.destroy
        def safe_destroy():
            dialog.is_valid = False
            original_destroy()
        dialog.destroy = safe_destroy
        
        return dialog

    def _run_module_sql_import(self, modules_dir, mysql_details, dialog):
        """Run module SQL import in background thread"""
        try:
            self.log_to_console(f"📁 Scanning modules directory: {modules_dir}")
            
            # Ask for root credentials once at the beginning for database creation
            root_credentials = self._ask_root_credentials_once()
            if not root_credentials:
                self.log_to_console("❌ Module SQL import cancelled - root credentials not provided")
                self._safe_update_dialog(dialog, lambda: dialog.destroy())
                return
            
            # First, process SQL files in auth/character/world folders
            self._safe_update_dialog(dialog, lambda: dialog.status_label.config(text="Processing auth/character/world folders..."))
            self._safe_update_dialog(dialog, lambda: dialog.progress.config(value=10))
            
            auth_files = []
            character_files = []
            world_files = []
            other_files = []
            
            # Scan all subdirectories recursively
            for root, dirs, files in os.walk(modules_dir):
                for file in files:
                    if file.lower().endswith('.sql'):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, modules_dir)
                        
                        # Check if file is in auth/character/world folders
                        if 'auth' in relative_path.lower():
                            auth_files.append(file_path)
                        elif 'character' in relative_path.lower():
                            character_files.append(file_path)
                        elif 'world' in relative_path.lower():
                            world_files.append(file_path)
                        else:
                            other_files.append(file_path)
            
            # Log findings
            self.log_to_console(f"📚 Found {len(auth_files)} SQL files in auth folders")
            self.log_to_console(f"📚 Found {len(character_files)} SQL files in character folders")
            self.log_to_console(f"📚 Found {len(world_files)} SQL files in world folders")
            self.log_to_console(f"📚 Found {len(other_files)} SQL files in other locations")
            
            total_files = len(auth_files) + len(character_files) + len(world_files) + len(other_files)
            processed_files = 0
            
            # Process auth files first
            if auth_files:
                self._safe_update_dialog(dialog, lambda: dialog.status_label.config(text=f"Importing {len(auth_files)} auth SQL files..."))
                for sql_file in auth_files:
                    self._import_single_sql_file("acore_auth", sql_file, mysql_details, root_credentials)
                    processed_files += 1
                    progress = 20 + (processed_files / total_files) * 30  # 20-50% for auth files
                    self._safe_update_dialog(dialog, lambda p=progress: dialog.progress.config(value=p))
            
            # Process character files
            if character_files:
                self._safe_update_dialog(dialog, lambda: dialog.status_label.config(text=f"Importing {len(character_files)} character SQL files..."))
                for sql_file in character_files:
                    self._import_single_sql_file("acore_characters", sql_file, mysql_details, root_credentials)
                    processed_files += 1
                    progress = 50 + (processed_files / total_files) * 30  # 50-80% for character files
                    self._safe_update_dialog(dialog, lambda p=progress: dialog.progress.config(value=p))
            
            # Process world files
            if world_files:
                self._safe_update_dialog(dialog, lambda: dialog.status_label.config(text=f"Importing {len(world_files)} world SQL files..."))
                for sql_file in world_files:
                    self._import_single_sql_file("acore_world", sql_file, mysql_details, root_credentials)
                    processed_files += 1
                    progress = 80 + (processed_files / total_files) * 15  # 80-95% for world files
                    self._safe_update_dialog(dialog, lambda p=progress: dialog.progress.config(value=p))
            
            # Process other files (try to determine database based on file content or use acore_world as default)
            if other_files:
                self._safe_update_dialog(dialog, lambda: dialog.status_label.config(text=f"Importing {len(other_files)} other SQL files..."))
                for sql_file in other_files:
                    # Try to determine the target database based on file content
                    target_db = self._determine_target_database(sql_file)
                    self._import_single_sql_file(target_db, sql_file, mysql_details, root_credentials)
                    processed_files += 1
                    progress = 95 + (processed_files / total_files) * 5  # 95-100% for other files
                    self._safe_update_dialog(dialog, lambda p=progress: dialog.progress.config(value=p))
            
            # Complete
            self._safe_update_dialog(dialog, lambda: dialog.status_label.config(text="Module SQL import completed!"))
            self._safe_update_dialog(dialog, lambda: dialog.progress.config(value=100))
            self._safe_update_dialog(dialog, lambda: dialog.destroy())
            
            # Show success message
            success_msg = f"Module SQL files have been successfully imported!\n\n"
            success_msg += f"Processed files:\n"
            success_msg += f"• {len(auth_files)} auth SQL files → acore_auth\n"
            success_msg += f"• {len(character_files)} character SQL files → acore_characters\n"
            success_msg += f"• {len(world_files)} world SQL files → acore_world\n"
            success_msg += f"• {len(other_files)} other SQL files → determined database\n\n"
            success_msg += f"Total: {total_files} SQL files processed."
            
            self.root.after(0, lambda: messagebox.showinfo("Module SQL Import Complete", success_msg))
            self.log_to_console("✅ Module SQL import completed successfully!")
            
        except Exception as e:
            # Error
            self._safe_update_dialog(dialog, lambda: dialog.status_label.config(text="Module SQL import failed"))
            self._safe_update_dialog(dialog, lambda: dialog.destroy())
            
            error_msg = f"Failed to import module SQL files:\n\n{str(e)}"
            self.root.after(0, lambda: messagebox.showerror("Module SQL Import Failed", error_msg))
            self.log_to_console(f"❌ Module SQL import failed: {str(e)}")

    def _determine_target_database(self, sql_file):
        """Determine target database based on SQL file content"""
        try:
            with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
            
            # Check for database-specific keywords
            if any(keyword in content for keyword in ['acore_auth', 'auth', 'account', 'login']):
                return "acore_auth"
            elif any(keyword in content for keyword in ['acore_characters', 'character', 'player', 'inventory']):
                return "acore_characters"
            elif any(keyword in content for keyword in ['acore_world', 'world', 'creature', 'gameobject', 'quest']):
                return "acore_world"
            else:
                # Default to acore_world for unknown files
                return "acore_world"
                
        except Exception as e:
            self.log_to_console(f"⚠️ Could not determine target database for {os.path.basename(sql_file)}: {str(e)}")
            return "acore_world"  # Default fallback

    def _show_firewall_notification(self, key):
        """Show firewall notification dialog for build operations"""
        try:
            # Check if user has chosen not to show this notification
            if hasattr(self, 'dont_show_firewall_var') and self.dont_show_firewall_var.get():
                self.log_to_console("ℹ️ Firewall notification skipped (user chose 'Don't show again')")
                # Start build process directly if notification is skipped
                self._start_build_process(key)
                return
            
            self.log_to_console("🛡️ Showing firewall notification")
            
            # Create firewall notification dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Firewall Notification")
            dialog.geometry("600x350")
            dialog.transient(self.root)
            dialog.grab_set()
            dialog.resizable(False, False)
            
            # Center dialog
            dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 200, self.root.winfo_rooty() + 150))
            
            # Main frame
            main_frame = ttk.Frame(dialog, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            title_label = ttk.Label(main_frame, text="🛡️ Firewall Notification", 
                                  font=("Arial", 14, "bold"))
            title_label.pack(pady=(0, 15))
            
            # Warning icon and message
            warning_frame = ttk.Frame(main_frame)
            warning_frame.pack(fill=tk.X, pady=(0, 15))
            
            warning_icon = ttk.Label(warning_frame, text="⚠️", font=("Arial", 24))
            warning_icon.pack(side=tk.LEFT, padx=(0, 10))
            
            warning_text = ttk.Label(warning_frame, 
                                   text="Your Windows Firewall may block some build features",
                                   font=("Arial", 12, "bold"),
                                   foreground="#ff6b35")
            warning_text.pack(side=tk.LEFT)
            
            # Information text
            info_text = tk.Text(main_frame, height=8, width=60, wrap=tk.WORD, 
                              font=("Arial", 9), bg='#f8f9fa', fg='#333333',
                              borderwidth=1, relief='solid')
            info_text.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
            
            info_content = """During the build process, the following may be blocked by Windows Firewall:

• CMake configuration and generation
• Visual Studio compilation processes
• Git operations and network access
• File system operations and temporary file creation
• Process spawning and inter-process communication

If you encounter build failures or timeouts, consider:

1. Temporarily disabling Windows Firewall during build
2. Adding exceptions for Visual Studio, CMake, and Git
3. Running as Administrator for full system access
4. Checking Windows Defender real-time protection settings

The build process will continue, but some features may be limited."""
            
            info_text.insert(tk.END, info_content)
            info_text.config(state=tk.DISABLED)
            
            # Button frame
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(side=tk.BOTTOM, pady=(10, 0))
            
            # Continue button
            def continue_build():
                dialog.destroy()
                self._start_build_process(key)
            
            continue_button = ttk.Button(button_frame, text="Continue Build", 
                                       command=continue_build, width=15)
            continue_button.pack(side=tk.RIGHT, padx=(10, 0))
            
            # Don't show again checkbox
            self.dont_show_firewall_var = getattr(self, 'dont_show_firewall_var', tk.BooleanVar())
            dont_show_checkbox = ttk.Checkbutton(button_frame, 
                                               text="Don't show this again",
                                               variable=self.dont_show_firewall_var)
            dont_show_checkbox.pack(side=tk.LEFT)
            
            # Store dialog reference for potential future use
            dialog.dont_show_var = self.dont_show_firewall_var
            
            self.log_to_console("✅ Firewall notification displayed")
            
        except Exception as e:
            self.log_to_console(f"⚠️ Could not show firewall notification: {str(e)}")

    def set_system_variables(self):
        """Set system environment variables for MySQL and Boost"""
        try:
            self.log_to_console("⚙️ Opening system variables configuration dialog")
            
            # Show confirmation dialog
            result = messagebox.askyesno("Set System Variables", 
                                       "This will set system environment variables for MySQL and Boost:\n\n"
                                       "• Add MySQL bin and lib folders to system PATH\n"
                                       "• Set BOOST_ROOT environment variable\n\n"
                                       "This requires administrator privileges.\n\n"
                                       "Do you want to continue?")
            
            if not result:
                self.log_to_console("❌ System variables setup cancelled by user")
                return
            
            self.log_to_console("🔧 Starting system variables configuration...")
            
            # Get MySQL and Boost paths from requirements
            mysql_path = self.requirements["MySQL"]["path"]
            boost_path = self.requirements["Boost"]["path"]
            
            if not mysql_path or not os.path.exists(mysql_path):
                messagebox.showerror("MySQL Path Not Found", 
                                   "MySQL path not found or not set.\n\n"
                                   "Please set the MySQL path in the Requirements tab first.")
                self.log_to_console("❌ MySQL path not found or not set")
                return
            
            if not boost_path or not os.path.exists(boost_path):
                messagebox.showerror("Boost Path Not Found", 
                                   "Boost path not found or not set.\n\n"
                                   "Please set the Boost path in the Requirements tab first.")
                self.log_to_console("❌ Boost path not found or not set")
                return
            
            # Normalize paths and convert to forward slashes
            mysql_path = os.path.normpath(mysql_path).replace('\\', '/')
            boost_path = os.path.normpath(boost_path).replace('\\', '/')
            
            # Remove trailing slash from boost_path if present
            if boost_path.endswith('/'):
                boost_path = boost_path[:-1]
            
            self.log_to_console(f"📁 MySQL path: {mysql_path}")
            self.log_to_console(f"📁 Boost path: {boost_path}")
            
            # Set up paths for MySQL
            mysql_bin_path = f"{mysql_path}/bin"
            mysql_lib_path = f"{mysql_path}/lib"
            
            # Configure environment variables
            success = self._configure_system_environment_variables(mysql_bin_path, mysql_lib_path, boost_path)
            
            if success:
                messagebox.showinfo("System Variables Set", 
                                  "System environment variables have been set successfully!\n\n"
                                  f"• Added to PATH: {mysql_bin_path}\n"
                                  f"• Added to PATH: {mysql_lib_path}\n"
                                  f"• BOOST_ROOT: {boost_path}\n\n"
                                  "You may need to restart your command prompt or IDE for changes to take effect.")
                self.log_to_console("✅ System environment variables configured successfully")
            else:
                messagebox.showerror("System Variables Failed", 
                                   "Failed to set system environment variables.\n\n"
                                   "Please run this application as administrator and try again.")
                self.log_to_console("❌ Failed to configure system environment variables")
                
        except Exception as e:
            error_msg = f"Failed to set system variables:\n\n{str(e)}"
            messagebox.showerror("System Variables Error", error_msg)
            self.log_to_console(f"❌ System variables error: {str(e)}")

    def _configure_system_environment_variables(self, mysql_bin_path, mysql_lib_path, boost_path):
        """Configure system environment variables using Windows Registry"""
        try:
            import winreg
            
            self.log_to_console("🔧 Configuring system environment variables...")
            
            # Open system environment variables registry key
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 
                              0, winreg.KEY_ALL_ACCESS) as key:
                
                # Get current PATH
                try:
                    current_path, _ = winreg.QueryValueEx(key, "PATH")
                except FileNotFoundError:
                    current_path = ""
                
                # Add MySQL paths to PATH if not already present
                new_path_entries = []
                if mysql_bin_path not in current_path:
                    new_path_entries.append(mysql_bin_path)
                if mysql_lib_path not in current_path:
                    new_path_entries.append(mysql_lib_path)
                
                if new_path_entries:
                    # Add new entries to PATH
                    updated_path = current_path + ";" + ";".join(new_path_entries)
                    winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, updated_path)
                    self.log_to_console(f"✅ Added to system PATH: {', '.join(new_path_entries)}")
                else:
                    self.log_to_console("ℹ️ MySQL paths already in system PATH")
                
                # Set BOOST_ROOT
                winreg.SetValueEx(key, "BOOST_ROOT", 0, winreg.REG_EXPAND_SZ, boost_path)
                self.log_to_console(f"✅ Set system BOOST_ROOT: {boost_path}")
            
            # Also set in user environment variables
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS) as user_key:
                    winreg.SetValueEx(user_key, "BOOST_ROOT", 0, winreg.REG_EXPAND_SZ, boost_path)
                    self.log_to_console(f"✅ Set user BOOST_ROOT: {boost_path}")
            except Exception as e:
                self.log_to_console(f"⚠️ Could not set user BOOST_ROOT: {str(e)}")
            
            # Broadcast WM_SETTINGCHANGE to notify other applications
            try:
                import ctypes
                from ctypes import wintypes
                
                # Send WM_SETTINGCHANGE message
                ctypes.windll.user32.SendMessageW(
                    wintypes.HWND(-1),  # HWND_BROADCAST
                    0x001A,  # WM_SETTINGCHANGE
                    0,  # wParam
                    "Environment"  # lParam
                )
                self.log_to_console("✅ Broadcasted environment change notification")
            except Exception as e:
                self.log_to_console(f"⚠️ Could not broadcast environment change: {str(e)}")
            
            return True
            
        except PermissionError:
            self.log_to_console("❌ Permission denied - administrator privileges required")
            return False
        except Exception as e:
            self.log_to_console(f"❌ Error configuring environment variables: {str(e)}")
            return False

    def create_heidisql_bat(self):
        """Create HeidiSQL installation and HeidiSQL.bat file in the main Repack folder that launches HeidiSQL without showing a command window"""
        try:
            self.log_to_console("🗄️ Starting HeidiSQL setup and batch file creation...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            repack_dir = os.path.join(app_dir, "Repack")
            tools_dir = os.path.join(repack_dir, "Tools")
            heidisql_dir = os.path.join(tools_dir, "HeidiSQL")
            heidi_exe_path = os.path.join(heidisql_dir, "heidisql.exe")
            
            # Check if Repack folder exists
            if not os.path.exists(repack_dir):
                messagebox.showerror("Repack Folder Not Found", 
                                   "Repack folder not found. Please create a repack first using the 'Create Repack' button.")
                self.log_to_console("❌ Repack folder not found")
                return
            
            # First, ensure HeidiSQL is installed (combine create_heidisql functionality)
            if not os.path.exists(heidi_exe_path):
                self.log_to_console("📥 HeidiSQL not found, setting up HeidiSQL installation...")
                
                # Create Tools directory if it doesn't exist
                os.makedirs(tools_dir, exist_ok=True)
                self.log_to_console(f"📁 Created Tools directory: {tools_dir}")
                
                # Check if HeidiSQL is already configured in requirements
                heidi_path = self.requirements["HeidiSQL"]["path"]
                
                if heidi_path and os.path.exists(heidi_path):
                    # Copy from configured path
                    self.log_to_console(f"📁 Found configured HeidiSQL path: {heidi_path}")
                    self._copy_heidisql_from_path(heidi_path, heidisql_dir)
                else:
                    # Download HeidiSQL
                    self.log_to_console("📥 No configured HeidiSQL path found, downloading...")
                    self._download_heidisql(heidisql_dir)
                
                # Check again if HeidiSQL was successfully installed
                if not os.path.exists(heidi_exe_path):
                    messagebox.showerror("HeidiSQL Installation Failed", 
                                       "Failed to install HeidiSQL. Please check the console for details.")
                    self.log_to_console("❌ HeidiSQL installation failed")
                    return
                else:
                    self.log_to_console("✅ HeidiSQL installation completed successfully")
            
            # Now create the batch file (original create_heidisql_bat functionality)
            self.log_to_console("📄 Creating HeidiSQL.bat file...")
            
            # Define the batch file path
            bat_file_path = os.path.join(repack_dir, "HeidiSQL.bat")
            
            # Create the batch file content that runs HeidiSQL without showing a command window
            bat_content = f'''@echo off
cd /d "{heidisql_dir}"
start "" "{heidi_exe_path}"
'''
            
            # Write the batch file
            with open(bat_file_path, 'w', encoding='utf-8') as f:
                f.write(bat_content)
            
            self.log_to_console(f"✅ HeidiSQL.bat file created successfully at: {bat_file_path}")
            self.log_to_console(f"📁 HeidiSQL executable path: {heidi_exe_path}")
            self.log_to_console(f"📁 HeidiSQL working directory: {heidisql_dir}")
            
            messagebox.showinfo("HeidiSQL Setup Complete", 
                              f"HeidiSQL has been set up and HeidiSQL.bat file created successfully!\n\n"
                              f"Batch file location: {bat_file_path}\n"
                              f"HeidiSQL executable: {heidi_exe_path}\n\n"
                              "You can now double-click HeidiSQL.bat to launch HeidiSQL without showing a command window.")
            
        except Exception as e:
            error_msg = f"Failed to create HeidiSQL.bat file:\n\n{str(e)}"
            messagebox.showerror("HeidiSQL.bat Creation Failed", error_msg)
            self.log_to_console(f"❌ Failed to create HeidiSQL.bat file: {str(e)}")

    def launch_heidisql(self):
        """Launch HeidiSQL from Repack/Tools/HeidiSQL/heidisql.exe"""
        try:
            self.log_to_console("🗄️ Launching HeidiSQL from Repack...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            repack_dir = os.path.join(app_dir, "Repack")
            tools_dir = os.path.join(repack_dir, "Tools")
            heidisql_dir = os.path.join(tools_dir, "HeidiSQL")
            heidi_exe_path = os.path.join(heidisql_dir, "heidisql.exe")
            
            # Check if HeidiSQL executable exists in Repack
            if not os.path.exists(heidi_exe_path):
                messagebox.showerror("HeidiSQL Not Found", 
                                   "Run Create HeidiSQL first!\n\n"
                                   f"HeidiSQL executable not found at:\n{heidi_exe_path}\n\n"
                                   "Please use the 'Create HeidiSQL' button in the Repack Setup section first.")
                self.log_to_console("❌ HeidiSQL executable not found in Repack/Tools/HeidiSQL/")
                return
            
            self.log_to_console(f"🔍 Found HeidiSQL executable: {heidi_exe_path}")
            
            # Launch HeidiSQL - try different methods
            try:
                # Method 1: Direct execution without shell
                subprocess.Popen([heidi_exe_path], cwd=heidisql_dir)
                self.log_to_console(f"✅ HeidiSQL launched successfully (method 1) from: {heidi_exe_path}")
            except:
                try:
                    # Method 2: With shell=True
                    subprocess.Popen(heidi_exe_path, shell=True)
                    self.log_to_console(f"✅ HeidiSQL launched successfully (method 2) from: {heidi_exe_path}")
                except:
                    try:
                        # Method 3: Using os.startfile (Windows specific)
                        os.startfile(heidi_exe_path)
                        self.log_to_console(f"✅ HeidiSQL launched successfully (method 3) from: {heidi_exe_path}")
                    except:
                        # Method 4: Try with full path and quotes
                        subprocess.Popen(f'"{heidi_exe_path}"', shell=True)
                        self.log_to_console(f"✅ HeidiSQL launched successfully (method 4) from: {heidi_exe_path}")
            
            messagebox.showinfo("HeidiSQL Launched", f"HeidiSQL has been launched successfully from Repack!")
            
        except Exception as e:
            error_msg = f"Failed to launch HeidiSQL:\n\n{str(e)}"
            messagebox.showerror("HeidiSQL Launch Failed", error_msg)
            self.log_to_console(f"❌ Failed to launch HeidiSQL: {str(e)}")

    def set_autoupdater_off(self):
        """Set autoupdater OFF by setting Updates.EnableDatabases = 0 in worldserver.conf"""
        try:
            self.log_to_console("⏸️ Setting autoupdater OFF...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            repack_dir = os.path.join(app_dir, "Repack")
            configs_dir = os.path.join(repack_dir, "configs")
            worldserver_conf = os.path.join(configs_dir, "worldserver.conf")
            
            # Check if worldserver.conf exists
            if not os.path.exists(worldserver_conf):
                messagebox.showerror("Config File Not Found", 
                                   f"worldserver.conf not found at:\n{worldserver_conf}\n\n"
                                   "Please create configs first using the 'Create configs' button.")
                self.log_to_console("❌ worldserver.conf not found")
                return
            
            # Read the current config file
            with open(worldserver_conf, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace the Updates.EnableDatabases setting
            import re
            pattern = r'Updates\.EnableDatabases\s*=\s*\d+'
            replacement = 'Updates.EnableDatabases = 0'
            
            if re.search(pattern, content):
                new_content = re.sub(pattern, replacement, content)
                self.log_to_console(f"🔧 Found and updated Updates.EnableDatabases setting")
            else:
                # If setting doesn't exist, add it
                new_content = content + f"\n{replacement}\n"
                self.log_to_console(f"🔧 Added Updates.EnableDatabases = 0 setting")
            
            # Write the updated config file
            with open(worldserver_conf, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.log_to_console(f"✅ Autoupdater set to OFF (Updates.EnableDatabases = 0)")
            messagebox.showinfo("Autoupdater OFF", 
                              "Autoupdater has been set to OFF.\n\n"
                              "Updates.EnableDatabases = 0")
            
        except Exception as e:
            error_msg = f"Failed to set autoupdater OFF:\n\n{str(e)}"
            messagebox.showerror("Autoupdater OFF Failed", error_msg)
            self.log_to_console(f"❌ Failed to set autoupdater OFF: {str(e)}")

    def set_autoupdater_on(self):
        """Set autoupdater ON by setting Updates.EnableDatabases = 7 in worldserver.conf"""
        try:
            self.log_to_console("▶️ Setting autoupdater ON...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            repack_dir = os.path.join(app_dir, "Repack")
            configs_dir = os.path.join(repack_dir, "configs")
            worldserver_conf = os.path.join(configs_dir, "worldserver.conf")
            
            # Check if worldserver.conf exists
            if not os.path.exists(worldserver_conf):
                messagebox.showerror("Config File Not Found", 
                                   f"worldserver.conf not found at:\n{worldserver_conf}\n\n"
                                   "Please create configs first using the 'Create configs' button.")
                self.log_to_console("❌ worldserver.conf not found")
                return
            
            # Read the current config file
            with open(worldserver_conf, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace the Updates.EnableDatabases setting
            import re
            pattern = r'Updates\.EnableDatabases\s*=\s*\d+'
            replacement = 'Updates.EnableDatabases = 7'
            
            if re.search(pattern, content):
                new_content = re.sub(pattern, replacement, content)
                self.log_to_console(f"🔧 Found and updated Updates.EnableDatabases setting")
            else:
                # If setting doesn't exist, add it
                new_content = content + f"\n{replacement}\n"
                self.log_to_console(f"🔧 Added Updates.EnableDatabases = 7 setting")
            
            # Write the updated config file
            with open(worldserver_conf, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.log_to_console(f"✅ Autoupdater set to ON (Updates.EnableDatabases = 7)")
            messagebox.showinfo("Autoupdater ON", 
                              "Autoupdater has been set to ON.\n\n"
                              "Updates.EnableDatabases = 7")
            
        except Exception as e:
            error_msg = f"Failed to set autoupdater ON:\n\n{str(e)}"
            messagebox.showerror("Autoupdater ON Failed", error_msg)
            self.log_to_console(f"❌ Failed to set autoupdater ON: {str(e)}")

    def start_authserver(self):
        """Start the Authserver and show output in console"""
        try:
            self.log_to_console("🔐 Starting Authserver...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            repack_dir = os.path.join(app_dir, "Repack")
            authserver_exe = os.path.join(repack_dir, "authserver.exe")
            
            # Check if Repack folder exists
            if not os.path.exists(repack_dir):
                messagebox.showerror("Repack Folder Not Found", 
                                   "Repack folder not found. Please create a repack first using the 'Create Repack' button.")
                self.log_to_console("❌ Repack folder not found")
                return
            
            # Check if authserver.exe exists
            if not os.path.exists(authserver_exe):
                messagebox.showerror("Authserver Not Found", 
                                   f"authserver.exe not found at:\n{authserver_exe}\n\n"
                                   "Please create a repack first using the 'Create Repack' button.")
                self.log_to_console(f"❌ authserver.exe not found at: {authserver_exe}")
                return
            
            self.log_to_console(f"✅ Found authserver.exe at: {authserver_exe}")
            self.log_to_console("🚀 Starting Authserver process...")
            
            # Start the authserver process with proper error handling
            try:
                process = subprocess.Popen(
                    [authserver_exe],
                    cwd=repack_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # Store process reference for potential future use
                self.authserver_process = process
                
                # Start a thread to read the output and display it in console IMMEDIATELY
                output_thread = threading.Thread(target=self._read_authserver_output, args=(process,))
                output_thread.daemon = True
                output_thread.start()
                
                # Give the process a moment to start and produce output
                time.sleep(0.5)
                
                # Check if the process is still running
                if process.poll() is not None:
                    # Process has already terminated, get the error
                    stdout, _ = process.communicate()
                    error_msg = f"Authserver process terminated immediately.\n\n"
                    if stdout:
                        error_msg += f"Output: {stdout}\n\n"
                    error_msg += "This usually indicates a configuration issue or missing dependencies."
                    
                    messagebox.showerror("Authserver Start Failed", error_msg)
                    self.log_to_console(f"❌ Authserver process terminated immediately")
                    if stdout:
                        self.log_to_console(f"📋 Output: {stdout}")
                    return
                
                # Verify the process is actually running
                if process.poll() is None:
                    self.log_to_console("✅ Authserver started successfully!")
                    self.log_to_console("📋 Authserver output will be displayed in the console below...")
                    self.log_to_console(f"🔍 Process ID: {process.pid}")
                else:
                    self.log_to_console("❌ Authserver process failed to start properly")
                    
            except subprocess.SubprocessError as e:
                error_msg = f"Failed to start Authserver process:\n\n{str(e)}"
                messagebox.showerror("Authserver Start Failed", error_msg)
                self.log_to_console(f"❌ Subprocess error: {str(e)}")
                return
            except FileNotFoundError as e:
                error_msg = f"Authserver executable not found or cannot be executed:\n\n{str(e)}"
                messagebox.showerror("Authserver Start Failed", error_msg)
                self.log_to_console(f"❌ File not found error: {str(e)}")
                return
            
        except Exception as e:
            error_msg = f"Failed to start Authserver:\n\n{str(e)}"
            messagebox.showerror("Authserver Start Failed", error_msg)
            self.log_to_console(f"❌ Failed to start Authserver: {str(e)}")

    def start_worldserver(self):
        """Start the Worldserver and show output in console"""
        try:
            self.log_to_console("🌍 Starting Worldserver...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            repack_dir = os.path.join(app_dir, "Repack")
            worldserver_exe = os.path.join(repack_dir, "worldserver.exe")
            
            # Check if Repack folder exists
            if not os.path.exists(repack_dir):
                messagebox.showerror("Repack Folder Not Found", 
                                   "Repack folder not found. Please create a repack first using the 'Create Repack' button.")
                self.log_to_console("❌ Repack folder not found")
                return
            
            # Check if worldserver.exe exists
            if not os.path.exists(worldserver_exe):
                messagebox.showerror("Worldserver Not Found", 
                                   f"worldserver.exe not found at:\n{worldserver_exe}\n\n"
                                   "Please create a repack first using the 'Create Repack' button.")
                self.log_to_console(f"❌ worldserver.exe not found at: {worldserver_exe}")
                return
            
            self.log_to_console(f"✅ Found worldserver.exe at: {worldserver_exe}")
            self.log_to_console("🚀 Starting Worldserver process...")
            
            # Start the worldserver process
            process = subprocess.Popen(
                [worldserver_exe],
                cwd=repack_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Store process reference for potential future use
            self.worldserver_process = process
            
            # Start a thread to read the output and display it in console
            output_thread = threading.Thread(target=self._read_worldserver_output, args=(process,))
            output_thread.daemon = True
            output_thread.start()
            
            self.log_to_console("✅ Worldserver started successfully!")
            self.log_to_console("📋 Worldserver output will be displayed in the console below...")
            
        except Exception as e:
            error_msg = f"Failed to start Worldserver:\n\n{str(e)}"
            messagebox.showerror("Worldserver Start Failed", error_msg)
            self.log_to_console(f"❌ Failed to start Worldserver: {str(e)}")

    def _load_heidisql_url_config(self):
        """Load HeidiSQL URL configuration from file"""
        try:
            config_file = os.path.join(self._get_app_dir(), "heidisql_url_config.json")
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.heidisql_url = config.get('heidisql_url', '')
                    self.log_to_console(f"[SUCCESS] Loaded HeidiSQL URL configuration")
            else:
                self.heidisql_url = ''
                self.log_to_console("[INFO] No HeidiSQL URL configuration found")
        except Exception as e:
            self.heidisql_url = ''
            self.log_to_console(f"[WARNING] Error loading HeidiSQL URL configuration: {str(e)}")

    def _save_heidisql_url_config(self):
        """Save HeidiSQL URL configuration to file"""
        try:
            config_file = os.path.join(self._get_app_dir(), "heidisql_url_config.json")
            config = {'heidisql_url': self.heidisql_url}
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.log_to_console(f"✅ Saved HeidiSQL URL configuration")
        except Exception as e:
            self.log_to_console(f"❌ Error saving HeidiSQL URL configuration: {str(e)}")

    def _load_data_url_config(self):
        """Load data URL configuration from file"""
        try:
            config_file = os.path.join(self._get_app_dir(), "data_url_config.json")
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.data_url = config.get('data_url', '')
                    self.log_to_console(f"[SUCCESS] Loaded data URL configuration")
            else:
                self.data_url = ''
                self.log_to_console("[INFO] No data URL configuration found")
        except Exception as e:
            self.data_url = ''
            self.log_to_console(f"[WARNING] Error loading data URL configuration: {str(e)}")

    def _save_data_url_config(self):
        """Save data URL configuration to file"""
        try:
            config_file = os.path.join(self._get_app_dir(), "data_url_config.json")
            config = {'data_url': self.data_url}
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.log_to_console(f"✅ Saved data URL configuration")
        except Exception as e:
            self.log_to_console(f"❌ Error saving data URL configuration: {str(e)}")

    def config_data_url(self):
        """Configure custom data download URL"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Configure Data URL")
        dialog.geometry("600x400")
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Configure Data Download URL", 
                               style="Title.TLabel")
        title_label.pack(pady=(0, 20))
        
        # Info text
        info_text = tk.Text(main_frame, height=8, wrap=tk.WORD, font=("Arial", 9))
        info_text.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        info_text.insert(tk.END, 
                        "Configure a custom URL for downloading AzerothCore data files.\n\n"
                        "Default behavior: Downloads the latest data.zip from wowgaming/client-data repository.\n\n"
                        "Custom URL: You can specify a direct download link to a data.zip file.\n\n"
                        "Examples:\n"
                        "• https://github.com/wowgaming/client-data/releases/download/v1.0.0/data.zip\n"
                        "• https://your-server.com/custom-data.zip\n\n"
                        "Leave empty to use the default automatic detection.")
        info_text.config(state=tk.DISABLED)
        
        # URL input frame
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(url_frame, text="Data URL:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        url_var = tk.StringVar(value=self.data_url)
        url_entry = ttk.Entry(url_frame, textvariable=url_var, width=70, font=("Arial", 9))
        url_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        def save_url():
            new_url = url_var.get().strip()
            self.data_url = new_url
            self._save_data_url_config()
            self.log_to_console(f"✅ Data URL configured: {new_url if new_url else 'Default (auto-detect)'}")
            dialog.destroy()
        
        def reset_url():
            url_var.set('')
            self.log_to_console("🔄 Reset data URL to default (auto-detect)")
        
        def test_url():
            test_url_value = url_var.get().strip()
            if not test_url_value:
                messagebox.showinfo("Test URL", "No URL provided. Will use default auto-detection.")
                return
            
            try:
                import urllib.request
                request = urllib.request.Request(test_url_value)
                request.add_header('User-Agent', 'AzerothCoreBuilder/1.0')
                with urllib.request.urlopen(request, timeout=10) as response:
                    if response.status == 200:
                        messagebox.showinfo("Test URL", f"✅ URL is accessible!\n\nStatus: {response.status}\nContent-Type: {response.headers.get('Content-Type', 'Unknown')}")
                    else:
                        messagebox.showwarning("Test URL", f"⚠️ URL returned status: {response.status}")
            except Exception as e:
                messagebox.showerror("Test URL", f"❌ URL test failed:\n\n{str(e)}")
        
        # Buttons
        ttk.Button(buttons_frame, text="Save", command=save_url).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Reset to Default", command=reset_url).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Test URL", command=test_url).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)

    def create_heidisql(self):
        """Create HeidiSQL in Repack/Tools/HeidiSQL by copying from configured path or downloading"""
        try:
            self.log_to_console("🗄️ Starting HeidiSQL setup...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            repack_dir = os.path.join(app_dir, "Repack")
            tools_dir = os.path.join(repack_dir, "Tools")
            heidisql_dir = os.path.join(tools_dir, "HeidiSQL")
            
            # Check if Repack folder exists
            if not os.path.exists(repack_dir):
                messagebox.showerror("Repack Folder Not Found", 
                                   "Repack folder not found. Please create a repack first using the 'Create Repack' button.")
                self.log_to_console("❌ Repack folder not found")
                return
            
            # Create Tools directory if it doesn't exist
            os.makedirs(tools_dir, exist_ok=True)
            self.log_to_console(f"📁 Created Tools directory: {tools_dir}")
            
            # Check if HeidiSQL is already configured in requirements
            heidi_path = self.requirements["HeidiSQL"]["path"]
            
            if heidi_path and os.path.exists(heidi_path):
                # Copy from configured path
                self.log_to_console(f"📁 Found configured HeidiSQL path: {heidi_path}")
                self._copy_heidisql_from_path(heidi_path, heidisql_dir)
            else:
                # Download HeidiSQL
                self.log_to_console("📥 No configured HeidiSQL path found, downloading...")
                self._download_heidisql(heidisql_dir)
            
        except Exception as e:
            error_msg = f"Failed to create HeidiSQL:\n\n{str(e)}"
            messagebox.showerror("HeidiSQL Creation Failed", error_msg)
            self.log_to_console(f"❌ HeidiSQL creation failed: {str(e)}")

    def _copy_heidisql_from_path(self, source_path, target_dir):
        """Copy HeidiSQL from configured path to target directory"""
        try:
            import shutil
            
            # Remove existing target directory if it exists
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
                self.log_to_console(f"🗑️ Removed existing HeidiSQL directory")
            
            # Determine if source_path is a file or directory
            if os.path.isfile(source_path):
                # If it's a file (heidisql.exe), get the parent directory
                source_dir = os.path.dirname(source_path)
                self.log_to_console(f"📁 Source path is a file, using parent directory: {source_dir}")
            else:
                # If it's already a directory, use it directly
                source_dir = source_path
                self.log_to_console(f"📁 Source path is a directory: {source_dir}")
            
            # Verify the source directory exists and contains heidisql.exe
            if not os.path.exists(source_dir):
                raise Exception(f"Source directory does not exist: {source_dir}")
            
            heidisql_exe = os.path.join(source_dir, "heidisql.exe")
            if not os.path.exists(heidisql_exe):
                raise Exception(f"heidisql.exe not found in source directory: {source_dir}")
            
            # Copy the entire HeidiSQL directory
            shutil.copytree(source_dir, target_dir)
            
            # Verify the copy was successful
            if os.path.exists(os.path.join(target_dir, "heidisql.exe")):
                self.log_to_console(f"✅ Successfully copied HeidiSQL from: {source_dir}")
                self.log_to_console(f"📁 HeidiSQL installed to: {target_dir}")
                
                success_msg = f"HeidiSQL has been successfully copied!\n\n"
                success_msg += f"Source: {source_dir}\n"
                success_msg += f"Target: {target_dir}\n\n"
                success_msg += "HeidiSQL is now available in your Repack Tools folder."
                
                messagebox.showinfo("HeidiSQL Copied", success_msg)
            else:
                raise Exception("heidisql.exe not found in copied directory")
                
        except Exception as e:
            self.log_to_console(f"❌ Error copying HeidiSQL: {str(e)}")
            raise

    def _download_heidisql(self, target_dir):
        """Download and extract HeidiSQL to target directory"""
        temp_dir = None
        try:
            # Get HeidiSQL download URL
            if not self.heidisql_url:
                self.heidisql_url = self._prompt_heidisql_url()
                if not self.heidisql_url:
                    self.log_to_console("❌ HeidiSQL download cancelled - no URL provided")
                    return
                # Save the URL to config
                self._save_heidisql_url_config()
            
            self.log_to_console(f"📥 Downloading HeidiSQL from: {self.heidisql_url}")
            
            # Create temporary download directory
            temp_dir = os.path.join(self._get_app_dir(), "temp_heidisql")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Download the file
            import urllib.request
            filename = os.path.basename(self.heidisql_url)
            if not filename.endswith('.zip'):
                filename += '.zip'
            
            zip_path = os.path.join(temp_dir, filename)
            
            def progress_callback(block_num, block_size, total_size):
                if total_size > 0:
                    downloaded = block_num * block_size
                    percentage = min(int((downloaded * 100) / total_size), 100)
                    self.log_to_console(f"📥 Downloading HeidiSQL: {percentage}%")
            
            urllib.request.urlretrieve(self.heidisql_url, zip_path, progress_callback)
            self.log_to_console(f"✅ Downloaded HeidiSQL: {zip_path}")
            
            # Extract the zip file
            self.log_to_console("📦 Extracting HeidiSQL...")
            import zipfile
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find the extracted HeidiSQL directory
            extracted_dirs = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d)) and 'heidisql' in d.lower()]
            
            if not extracted_dirs:
                raise Exception("Could not find HeidiSQL directory in extracted files")
            
            source_dir = os.path.join(temp_dir, extracted_dirs[0])
            
            # Copy to target directory
            import shutil
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            
            shutil.copytree(source_dir, target_dir)
            
            # Clean up temporary files
            shutil.rmtree(temp_dir)
            temp_dir = None  # Mark as cleaned up
            
            # Verify installation
            heidisql_exe = os.path.join(target_dir, "heidisql.exe")
            if os.path.exists(heidisql_exe):
                self.log_to_console(f"✅ HeidiSQL installed successfully to: {target_dir}")
                
                success_msg = f"HeidiSQL has been successfully downloaded and installed!\n\n"
                success_msg += f"Installation directory: {target_dir}\n"
                success_msg += f"Executable: {heidisql_exe}\n\n"
                success_msg += "HeidiSQL is now available in your Repack Tools folder."
                
                messagebox.showinfo("HeidiSQL Installed", success_msg)
            else:
                raise Exception("heidisql.exe not found in installed directory")
                
        except Exception as e:
            self.log_to_console(f"❌ Error downloading HeidiSQL: {str(e)}")
            raise
        finally:
            # Ensure temp directory is cleaned up even if an exception occurs
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    self.log_to_console(f"🧹 Cleaned up temporary directory: {temp_dir}")
                except Exception as cleanup_error:
                    self.log_to_console(f"⚠️ Warning: Could not clean up temp directory {temp_dir}: {cleanup_error}")

    def _prompt_heidisql_url(self):
        """Prompt user for HeidiSQL download URL"""
        dialog = tk.Toplevel(self.root)
        dialog.title("HeidiSQL Download URL")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 150, self.root.winfo_rooty() + 150))
        
        # Title
        title_label = ttk.Label(dialog, text="HeidiSQL Download URL", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(20, 10))
        
        # Description
        desc_label = ttk.Label(dialog, 
                              text="No HeidiSQL path is configured. Please provide a download URL for HeidiSQL.\n\n"
                                   "This URL will be saved and used for future downloads.\n\n"
                                   "Example: https://www.heidisql.com/downloads/releases/HeidiSQL_12.6_64_Portable.zip",
                              font=("Arial", 10), wraplength=450)
        desc_label.pack(pady=(0, 20))
        
        # URL entry
        url_var = tk.StringVar()
        url_entry = ttk.Entry(dialog, textvariable=url_var, width=60, font=("Arial", 10))
        url_entry.pack(pady=(0, 20))
        url_entry.focus()
        
        # Buttons frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=(0, 20))
        
        # Result variable
        dialog.result = None
        
        # OK button
        def ok_clicked():
            url = url_var.get().strip()
            if not url:
                messagebox.showerror("URL Required", "Please enter a download URL.")
                return
            if not url.startswith(('http://', 'https://')):
                messagebox.showerror("Invalid URL", "Please enter a valid HTTP or HTTPS URL.")
                return
            dialog.result = url
            dialog.destroy()
        
        ok_button = ttk.Button(button_frame, text="OK", command=ok_clicked)
        ok_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        def cancel_clicked():
            dialog.result = None
            dialog.destroy()
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=cancel_clicked)
        cancel_button.pack(side=tk.LEFT)
        
        # Wait for dialog result
        dialog.wait_window()
        
        if dialog.result:
            self.log_to_console(f"✅ HeidiSQL URL provided: {dialog.result}")
            return dialog.result
        else:
            self.log_to_console("❌ HeidiSQL URL cancelled")
            return None

    def _read_authserver_output(self, process):
        """Read authserver output and display it in console"""
        try:
            # Read output line by line
            for line in iter(process.stdout.readline, ''):
                if line:
                    # Display the line in console with authserver prefix
                    line_content = line.rstrip()
                    # Fix lambda closure issue by capturing line_content in a default parameter
                    self.root.after(0, lambda l=line_content: self.log_to_console(f"[AUTHSERVER] {l}"))
                    
        except Exception as e:
            self.root.after(0, lambda: self.log_to_console(f"❌ Error reading authserver output: {str(e)}"))
        finally:
            # Process finished
            try:
                process.wait()
                self.root.after(0, lambda: self.log_to_console("🔐 Authserver process ended"))
            except:
                pass

    def _read_worldserver_output(self, process):
        """Read worldserver output and display it in console"""
        try:
            for line in iter(process.stdout.readline, ''):
                if line:
                    # Display the line in console with worldserver prefix
                    line_content = line.rstrip()
                    # Fix lambda closure issue by capturing line_content in a default parameter
                    self.root.after(0, lambda l=line_content: self.log_to_console(f"[WORLDSERVER] {l}"))
        except Exception as e:
            self.root.after(0, lambda: self.log_to_console(f"❌ Error reading worldserver output: {str(e)}"))
        finally:
            # Process finished
            process.wait()
            self.root.after(0, lambda: self.log_to_console("🌍 Worldserver process ended"))

    def wipe_repack(self):
        """Wipe the entire Repack folder with option to keep data folder"""
        try:
            self.log_to_console("🗑️ Starting repack wipe operation...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            repack_dir = os.path.join(app_dir, "Repack")
            
            # Check if Repack folder exists
            if not os.path.exists(repack_dir):
                messagebox.showinfo("Repack Folder Not Found", 
                                  "Repack folder does not exist.\nNothing to wipe.")
                self.log_to_console("💥 Repack folder does not exist - nothing to wipe")
                return
            
            # Check if Repack folder is empty
            try:
                repack_contents = os.listdir(repack_dir)
                if not repack_contents:
                    messagebox.showinfo("Repack Folder Empty", 
                                      "Repack folder is already empty.\nNothing to wipe.")
                    self.log_to_console("💥 Repack folder is already empty - nothing to wipe")
                    return
            except Exception as e:
                self.log_to_console(f"❌ Error checking Repack folder contents: {str(e)}")
                messagebox.showerror("Error", f"Error checking Repack folder:\n{str(e)}")
                return
            
            # Show confirmation dialog with data folder option
            dialog = tk.Toplevel(self.root)
            dialog.title("Wipe Repack")
            dialog.geometry("500x400")
            dialog.transient(self.root)
            dialog.grab_set()
            dialog.resizable(False, False)
            
            # Center dialog
            dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 200, self.root.winfo_rooty() + 200))
            
            # Main frame
            main_frame = ttk.Frame(dialog, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            title_label = ttk.Label(main_frame, text="🗑️ Wipe Repack", 
                                  font=("Arial", 14, "bold"))
            title_label.pack(pady=(0, 20))
            
            # Warning message
            warning_label = ttk.Label(main_frame, 
                                    text="⚠️ WARNING: This will permanently delete all files in the Repack folder!",
                                    font=("Arial", 10, "bold"), foreground="red")
            warning_label.pack(pady=(0, 20))
            
            # Description
            desc_label = ttk.Label(main_frame, 
                                 text="Choose what to do with the data folder:",
                                 font=("Arial", 10))
            desc_label.pack(pady=(0, 20))
            
            # Data folder option
            data_folder_var = tk.BooleanVar(value=True)  # Default to keeping data folder
            
            keep_data_checkbox = ttk.Checkbutton(main_frame, 
                                               text="Keep data folder (Repack/data and its contents)",
                                               variable=data_folder_var)
            keep_data_checkbox.pack(pady=(0, 20))
            
            # Info text
            info_text = tk.Text(main_frame, height=3, width=60, wrap=tk.WORD, font=("Arial", 9))
            info_text.pack(pady=(0, 10))
            info_text.insert(tk.END, "• If checked: All files will be deleted EXCEPT the data folder\n"
                                    "• If unchecked: ALL files including the data folder will be deleted\n\n"
                                    "This action cannot be undone!")
            info_text.config(state=tk.DISABLED)
            
            # Buttons frame
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(pady=(20, 20), fill=tk.X)
            
            # Result variable
            dialog.result = None
            
            # Wipe button
            def wipe_clicked():
                dialog.result = data_folder_var.get()
                dialog.destroy()
            
            wipe_button = ttk.Button(button_frame, text="🗑️ Wipe Repack", 
                                   command=wipe_clicked, style="Accent.TButton")
            wipe_button.pack(side=tk.LEFT, padx=(0, 10))
            
            # Cancel button
            def cancel_clicked():
                dialog.result = None
                dialog.destroy()
            
            cancel_button = ttk.Button(button_frame, text="Cancel", 
                                     command=cancel_clicked)
            cancel_button.pack(side=tk.LEFT)
            
            # Wait for dialog result
            dialog.wait_window()
            
            if dialog.result is None:
                self.log_to_console("❌ Repack wipe cancelled by user")
                return
            
            keep_data_folder = dialog.result
            self.log_to_console(f"🗑️ User chose to {'keep' if keep_data_folder else 'delete'} data folder")
            
            # Perform the wipe operation
            self._perform_repack_wipe(repack_dir, keep_data_folder)
            
        except Exception as e:
            error_msg = f"Failed to wipe repack:\n\n{str(e)}"
            messagebox.showerror("Repack Wipe Failed", error_msg)
            self.log_to_console(f"❌ Repack wipe failed: {str(e)}")
    
    def _perform_repack_wipe(self, repack_dir, keep_data_folder):
        """Perform the actual repack wipe operation"""
        try:
            import shutil
            
            if keep_data_folder:
                # Keep data folder - delete everything except data folder
                self.log_to_console("🗑️ Wiping repack while keeping data folder...")
                
                data_folder = os.path.join(repack_dir, "data")
                
                # Get all items in repack directory
                for item in os.listdir(repack_dir):
                    item_path = os.path.join(repack_dir, item)
                    
                    # Skip data folder
                    if item == "data" and os.path.isdir(item_path):
                        self.log_to_console(f"✅ Keeping data folder: {item_path}")
                        continue
                    
                    # Delete everything else
                    try:
                        if os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                            self.log_to_console(f"🗑️ Deleted folder: {item}")
                        else:
                            os.remove(item_path)
                            self.log_to_console(f"🗑️ Deleted file: {item}")
                    except Exception as e:
                        self.log_to_console(f"❌ Failed to delete {item}: {str(e)}")
                
                messagebox.showinfo("Repack Wiped", 
                                  f"Repack folder has been wiped successfully!\n\n"
                                  f"✅ Data folder preserved: {data_folder}\n"
                                  f"🗑️ All other files and folders deleted")
                self.log_to_console("✅ Repack wipe completed - data folder preserved")
                
            else:
                # Delete everything including data folder
                self.log_to_console("🗑️ Wiping entire repack folder...")
                
                # Delete the entire repack directory
                shutil.rmtree(repack_dir)
                
                # Recreate empty repack directory
                os.makedirs(repack_dir, exist_ok=True)
                
                messagebox.showinfo("Repack Wiped", 
                                  f"Repack folder has been completely wiped!\n\n"
                                  f"🗑️ All files and folders deleted including data folder\n"
                                  f"📁 Empty repack folder recreated")
                self.log_to_console("✅ Repack completely wiped - all files deleted")
                
        except Exception as e:
            error_msg = f"Failed to perform repack wipe:\n\n{str(e)}"
            messagebox.showerror("Repack Wipe Failed", error_msg)
            self.log_to_console(f"❌ Repack wipe operation failed: {str(e)}")

    def delete_logs(self):
        """Delete the Logs folder from the main app location"""
        try:
            self.log_to_console("🗑️ Starting logs deletion...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            logs_dir = os.path.join(app_dir, "Logs")
            
            # Check if Logs folder exists
            if not os.path.exists(logs_dir):
                messagebox.showinfo("Logs Folder Not Found", 
                                  "Logs folder does not exist.\nNothing to delete.")
                self.log_to_console("💥 Logs folder does not exist - nothing to delete")
                return
            
            # Show confirmation dialog
            if messagebox.askyesno("Delete Logs", 
                                 f"Are you sure you want to delete the Logs folder?\n\n"
                                 f"Location: {logs_dir}\n\n"
                                 "This action cannot be undone!"):
                self.log_to_console(f"🗑️ Deleting Logs folder: {logs_dir}")
                
                # Delete the Logs folder
                import shutil
                shutil.rmtree(logs_dir)
                
                messagebox.showinfo("Logs Deleted", 
                                  f"Logs folder has been successfully deleted!\n\n"
                                  f"🗑️ Deleted: {logs_dir}")
                self.log_to_console("✅ Logs folder deleted successfully")
            else:
                self.log_to_console("❌ Logs deletion cancelled by user")
                
        except Exception as e:
            error_msg = f"Failed to delete logs folder:\n\n{str(e)}"
            messagebox.showerror("Logs Deletion Failed", error_msg)
            self.log_to_console(f"❌ Logs deletion failed: {str(e)}")
    
    def delete_config(self):
        """Delete the config file from the main app location"""
        try:
            self.log_to_console("🗑️ Starting config deletion...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            config_file = os.path.join(app_dir, "acb_config.json")
            
            # Check if config file exists
            if not os.path.exists(config_file):
                messagebox.showinfo("Config File Not Found", 
                                  "Config file does not exist.\nNothing to delete.")
                self.log_to_console("💥 Config file does not exist - nothing to delete")
                return
            
            # Show confirmation dialog
            if messagebox.askyesno("Delete Config", 
                                 f"Are you sure you want to delete the config file?\n\n"
                                 f"File: {config_file}\n\n"
                                 "This will remove all custom download URLs.\n"
                                 "This action cannot be undone!"):
                self.log_to_console(f"🗑️ Deleting config file: {config_file}")
                
                # Delete the config file
                os.remove(config_file)
                
                messagebox.showinfo("Config Deleted", 
                                  f"Config file has been successfully deleted!\n\n"
                                  f"🗑️ Deleted: {config_file}\n\n"
                                  "Custom download URLs have been removed.")
                self.log_to_console("✅ Config file deleted successfully")
            else:
                self.log_to_console("❌ Config deletion cancelled by user")
                
        except Exception as e:
            error_msg = f"Failed to delete config file:\n\n{str(e)}"
            messagebox.showerror("Config Deletion Failed", error_msg)
            self.log_to_console(f"❌ Config deletion failed: {str(e)}")

    def delete_repack(self):
        """Delete the Repack folder from the main app location"""
        try:
            self.log_to_console("🗑️ Starting repack deletion...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            repack_dir = os.path.join(app_dir, "Repack")
            
            # Check if Repack folder exists
            if not os.path.exists(repack_dir):
                messagebox.showinfo("Repack Folder Not Found", 
                                  "Repack folder does not exist.\nNothing to delete.")
                self.log_to_console("💥 Repack folder does not exist - nothing to delete")
                return
            
            # Show confirmation dialog
            if messagebox.askyesno("Delete Repack", 
                                 f"Are you sure you want to delete the Repack folder?\n\n"
                                 f"Location: {repack_dir}\n\n"
                                 "This will delete all repack files including:\n"
                                 "• Server executables\n• MySQL data\n• Configuration files\n• Game data\n\n"
                                 "This action cannot be undone!"):
                self.log_to_console(f"🗑️ Deleting Repack folder: {repack_dir}")
                
                # Delete the Repack folder
                import shutil
                shutil.rmtree(repack_dir)
                
                messagebox.showinfo("Repack Deleted", 
                                  f"Repack folder has been successfully deleted!\n\n"
                                  f"🗑️ Deleted: {repack_dir}")
                self.log_to_console("✅ Repack folder deleted successfully")
            else:
                self.log_to_console("❌ Repack deletion cancelled by user")
                
        except Exception as e:
            error_msg = f"Failed to delete repack folder:\n\n{str(e)}"
            messagebox.showerror("Repack Deletion Failed", error_msg)
            self.log_to_console(f"❌ Repack deletion failed: {str(e)}")
    
    def delete_gitsource(self):
        """Delete the GitSource folder from the main app location (with Git clean first)"""
        try:
            self.log_to_console("🗑️ Starting GitSource deletion with Git clean...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            gitsource_dir = os.path.join(app_dir, "GitSource")
            
            # Check if GitSource folder exists
            if not os.path.exists(gitsource_dir):
                messagebox.showinfo("GitSource Folder Not Found", 
                                  "GitSource folder does not exist.\nNothing to delete.")
                self.log_to_console("💥 GitSource folder does not exist - nothing to delete")
                return
            
            # Show confirmation dialog
            if messagebox.askyesno("Delete GitSource", 
                                 f"Are you sure you want to delete the GitSource folder?\n\n"
                                 f"Location: {gitsource_dir}\n\n"
                                 "This will:\n"
                                 "• First clean all Git repositories (git clean -fdx)\n"
                                 "• Then delete all cloned repositories including:\n"
                                 "  - AzerothCore source code\n"
                                 "  - Module repositories\n"
                                 "  - Build files\n\n"
                                 "This action cannot be undone!"):
                
                # First, clean all repositories and modules
                self.log_to_console("🧹 Step 1: Cleaning all Git repositories...")
                self._clean_all_git_repositories(gitsource_dir)
                
                # Then delete the GitSource folder
                self.log_to_console("🗑️ Step 2: Deleting GitSource folder...")
                import shutil
                shutil.rmtree(gitsource_dir)
                
                messagebox.showinfo("GitSource Deleted", 
                                  f"GitSource folder has been successfully cleaned and deleted!\n\n"
                                  f"🧹 All Git repositories were cleaned first\n"
                                  f"🗑️ Deleted: {gitsource_dir}")
                self.log_to_console("✅ GitSource folder cleaned and deleted successfully")
            else:
                self.log_to_console("❌ GitSource deletion cancelled by user")
                
        except Exception as e:
            error_msg = f"Failed to delete GitSource folder:\n\n{str(e)}"
            messagebox.showerror("GitSource Deletion Failed", error_msg)
            self.log_to_console(f"❌ GitSource deletion failed: {str(e)}")
    
    def _clean_all_git_repositories(self, gitsource_dir):
        """Clean all Git repositories in the GitSource directory"""
        try:
            import shutil
            import stat
            
            def handle_remove_readonly(func, path, exc):
                """Handle readonly files by making them writable and retrying"""
                if os.path.exists(path):
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
            
            # Get all directories in GitSource
            if not os.path.exists(gitsource_dir):
                self.log_to_console("ℹ️ GitSource directory does not exist")
                return
            
            # List all items in GitSource directory
            items = os.listdir(gitsource_dir)
            git_repos = []
            modules_dirs = []
            
            for item in items:
                item_path = os.path.join(gitsource_dir, item)
                if os.path.isdir(item_path):
                    # Check if it's a Git repository
                    git_dir = os.path.join(item_path, ".git")
                    if os.path.exists(git_dir):
                        git_repos.append((item, item_path))
                        self.log_to_console(f"🔍 Found Git repository: {item}")
                    # Check if it's a modules directory
                    elif item == "modules" or "modules" in item.lower():
                        modules_dirs.append((item, item_path))
                        self.log_to_console(f"🔍 Found modules directory: {item}")
            
            # Clean all Git repositories
            for repo_name, repo_path in git_repos:
                try:
                    self.log_to_console(f"🧹 Cleaning Git repository: {repo_name}")
                    
                    # First try to remove Git attributes that might be read-only
                    try:
                        subprocess.run(["git", "config", "--local", "--unset", "core.filemode"], 
                                     cwd=repo_path, capture_output=True, timeout=10)
                        self.log_to_console(f"🔧 Removed Git file mode restrictions for {repo_name}")
                    except:
                        pass  # Ignore if this fails
                    
                    # Try Git clean command first
                    try:
                        subprocess.run(["git", "clean", "-fdx"], cwd=repo_path, 
                                     capture_output=True, timeout=30)
                        self.log_to_console(f"✅ Git clean completed for {repo_name}")
                    except:
                        self.log_to_console(f"⚠️ Git clean failed for {repo_name}, using fallback method")
                    
                    # If Git clean didn't remove everything, try shutil with readonly handling
                    if os.path.exists(repo_path):
                        try:
                            shutil.rmtree(repo_path, onerror=handle_remove_readonly)
                            self.log_to_console(f"✅ Removed {repo_name} using shutil")
                        except Exception as e:
                            self.log_to_console(f"❌ Failed to remove {repo_name}: {str(e)}")
                            
                except Exception as e:
                    self.log_to_console(f"❌ Error cleaning {repo_name}: {str(e)}")
            
            # Clean all modules directories
            for modules_name, modules_path in modules_dirs:
                try:
                    self.log_to_console(f"🧹 Cleaning modules directory: {modules_name}")
                    
                    # Get all module subdirectories
                    if os.path.exists(modules_path):
                        module_items = os.listdir(modules_path)
                        for module_item in module_items:
                            module_path = os.path.join(modules_path, module_item)
                            if os.path.isdir(module_path):
                                # Check if it's a Git repository
                                module_git_dir = os.path.join(module_path, ".git")
                                if os.path.exists(module_git_dir):
                                    try:
                                        # Try Git clean for each module
                                        subprocess.run(["git", "clean", "-fdx"], cwd=module_path, 
                                                     capture_output=True, timeout=30)
                                        self.log_to_console(f"✅ Git clean completed for module: {module_item}")
                                    except:
                                        self.log_to_console(f"⚠️ Git clean failed for module: {module_item}")
                                    
                                    # Remove the module directory
                                    try:
                                        shutil.rmtree(module_path, onerror=handle_remove_readonly)
                                        self.log_to_console(f"✅ Removed module: {module_item}")
                                    except Exception as e:
                                        self.log_to_console(f"❌ Failed to remove module {module_item}: {str(e)}")
                    
                except Exception as e:
                    self.log_to_console(f"❌ Error cleaning modules directory {modules_name}: {str(e)}")
            
            self.log_to_console(f"✅ Git cleaning completed for {len(git_repos)} repositories and {len(modules_dirs)} modules directories")
            
        except Exception as e:
            self.log_to_console(f"❌ Error during Git cleaning process: {str(e)}")
            raise
    
    def delete_build(self):
        """Delete the Build folder from the main app location"""
        try:
            self.log_to_console("🗑️ Starting Build deletion...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            build_dir = os.path.join(app_dir, "Build")
            
            # Check if Build folder exists
            if not os.path.exists(build_dir):
                messagebox.showinfo("Build Folder Not Found", 
                                  "Build folder does not exist.\nNothing to delete.")
                self.log_to_console("💥 Build folder does not exist - nothing to delete")
                return
            
            # Show confirmation dialog
            if messagebox.askyesno("Delete Build", 
                                 f"Are you sure you want to delete the Build folder?\n\n"
                                 f"Location: {build_dir}\n\n"
                                 "This will delete all build files including:\n"
                                 "• CMake cache\n• Compiled binaries\n• Build artifacts\n• Generated files\n\n"
                                 "This action cannot be undone!"):
                self.log_to_console(f"🗑️ Deleting Build folder: {build_dir}")
                
                # Delete the Build folder
                import shutil
                shutil.rmtree(build_dir)
                
                messagebox.showinfo("Build Deleted", 
                                  f"Build folder has been successfully deleted!\n\n"
                                  f"🗑️ Deleted: {build_dir}")
                self.log_to_console("✅ Build folder deleted successfully")
            else:
                self.log_to_console("❌ Build deletion cancelled by user")
                
        except Exception as e:
            error_msg = f"Failed to delete build folder:\n\n{str(e)}"
            messagebox.showerror("Build Deletion Failed", error_msg)
            self.log_to_console(f"❌ Build deletion failed: {str(e)}")
    
    def start_mysql(self):
        """Start MySQL server by running Repack/MySQL.bat in a new console window"""
        try:
            self.log_to_console("🗄️ Starting MySQL server...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            repack_dir = os.path.join(app_dir, "Repack")
            mysql_bat = os.path.join(repack_dir, "MySQL.bat")
            
            # Check if Repack folder exists
            if not os.path.exists(repack_dir):
                messagebox.showerror("Repack Folder Not Found", 
                                   "Repack folder not found. Please create a repack first using the 'Create Repack' button.")
                self.log_to_console("❌ Repack folder not found")
                return
            
            # Check if MySQL.bat exists
            if not os.path.exists(mysql_bat):
                messagebox.showerror("MySQL.bat Not Found", 
                                   f"MySQL.bat not found at:\n{mysql_bat}\n\n"
                                   "Please use the 'Create MySQL.bat' button first.")
                self.log_to_console("❌ MySQL.bat not found")
                return
            
            self.log_to_console(f"✅ Found MySQL.bat: {mysql_bat}")
            
            # Launch MySQL.bat in a new console window
            subprocess.Popen(f'start cmd /k "{mysql_bat}"', shell=True, cwd=repack_dir)
            
            self.log_to_console("✅ MySQL server started in new console window")
            
        except Exception as e:
            error_msg = f"Failed to start MySQL server:\n\n{str(e)}"
            messagebox.showerror("MySQL Start Failed", error_msg)
            self.log_to_console(f"❌ Failed to start MySQL server: {str(e)}")
    
    def start_auth(self):
        """Start Auth server by running Repack/authserver.exe in a new console window"""
        try:
            self.log_to_console("🔐 Starting Auth server...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            repack_dir = os.path.join(app_dir, "Repack")
            auth_exe = os.path.join(repack_dir, "authserver.exe")
            
            # Check if Repack folder exists
            if not os.path.exists(repack_dir):
                messagebox.showerror("Repack Folder Not Found", 
                                   "Repack folder not found. Please create a repack first using the 'Create Repack' button.")
                self.log_to_console("❌ Repack folder not found")
                return
            
            # Check if authserver.exe exists
            if not os.path.exists(auth_exe):
                messagebox.showerror("Authserver.exe Not Found", 
                                   f"authserver.exe not found at:\n{auth_exe}\n\n"
                                   "Please use the 'Create Repack' button first.")
                self.log_to_console("❌ authserver.exe not found")
                return
            
            self.log_to_console(f"✅ Found authserver.exe: {auth_exe}")
            
            # Launch authserver.exe in a new console window
            subprocess.Popen(f'start cmd /k "{auth_exe}"', shell=True, cwd=repack_dir)
            
            self.log_to_console("✅ Auth server started in new console window")
            
        except Exception as e:
            error_msg = f"Failed to start Auth server:\n\n{str(e)}"
            messagebox.showerror("Auth Start Failed", error_msg)
            self.log_to_console(f"❌ Failed to start Auth server: {str(e)}")
    
    def start_world(self):
        """Start World server by running Repack/worldserver.exe in a new console window"""
        try:
            self.log_to_console("🌍 Starting World server...")
            
            # Get the main app directory (where ACB.py is located)
            app_dir = self._get_app_dir()
            repack_dir = os.path.join(app_dir, "Repack")
            world_exe = os.path.join(repack_dir, "worldserver.exe")
            
            # Check if Repack folder exists
            if not os.path.exists(repack_dir):
                messagebox.showerror("Repack Folder Not Found", 
                                   "Repack folder not found. Please create a repack first using the 'Create Repack' button.")
                self.log_to_console("❌ Repack folder not found")
                return
            
            # Check if worldserver.exe exists
            if not os.path.exists(world_exe):
                messagebox.showerror("Worldserver.exe Not Found", 
                                   f"worldserver.exe not found at:\n{world_exe}\n\n"
                                   "Please use the 'Create Repack' button first.")
                self.log_to_console("❌ worldserver.exe not found")
                return
            
            self.log_to_console(f"✅ Found worldserver.exe: {world_exe}")
            
            # Launch worldserver.exe in a new console window
            subprocess.Popen(f'start cmd /k "{world_exe}"', shell=True, cwd=repack_dir)
            
            self.log_to_console("✅ World server started in new console window")
            
        except Exception as e:
            error_msg = f"Failed to start World server:\n\n{str(e)}"
            messagebox.showerror("World Start Failed", error_msg)
            self.log_to_console(f"❌ Failed to start World server: {str(e)}")

def main():
    # Check if running on Windows
    if platform.system() != "Windows":
        messagebox.showerror("Platform Error", 
                           "This application is designed for Windows only.\n"
                           "AzerothCore building on other platforms requires different tools.")
        return
    
    root = tk.Tk()
    app = AzerothCoreBuilder(root)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()
