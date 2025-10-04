# ACB.py API Documentation

## Class: AzerothCoreBuilder

The main application class that handles the GUI interface and all functionality for building AzerothCore from source.

### Constructor

```python
def __init__(self, root)
```

**Parameters:**
- `root` (tk.Tk): The main tkinter window instance

**Description:**
Initializes the AzerothCore Builder application with GUI setup, dependency detection, and configuration loading.

## Core Methods

### Application Initialization

#### `_init_app_directory(self)`
Determines the application directory for both PyInstaller executables and development mode.

**Returns:** None

**Behavior:**
- Sets `self.app_dir` to executable directory when frozen (PyInstaller)
- Sets `self.app_dir` to script directory when running as Python script

#### `_get_app_dir(self)`
**Returns:** `str` - The application directory path

#### `_get_resource_path(self, relative_path)`
**Parameters:**
- `relative_path` (str): Path relative to application directory

**Returns:** `str` - Absolute path to resource file

**Description:**
Resolves resource paths for both PyInstaller bundles and development environments.

### Logging System

#### `_setup_logging(self)`
Initializes the logging system with timestamp-based log files.

**Creates:**
- `logs/` directory in application folder
- Session log file: `acb_session_YYYYMMDD_HHMMSS.log`

#### `log_to_console(self, message)`
**Parameters:**
- `message` (str): Message to log

**Description:**
Logs messages to both the GUI console and log file with timestamps.

### User Interface

#### `setup_ui(self)`
Creates the main GUI interface with three tabs:
- **Requirements Tab**: Dependency checking and installation
- **Build Tab**: Source management and compilation
- **Console Tab**: Real-time logging and controls

#### `add_app_icon(self, parent)`
**Parameters:**
- `parent` (tk.Widget): Parent widget for icon placement

**Description:**
Attempts to load and display the application icon from `icons/AZC.png`.

### Dependency Management

#### `create_requirement_row(self, parent, key, req, row)`
**Parameters:**
- `parent` (tk.Widget): Parent frame for the row
- `key` (str): Requirement identifier key
- `req` (dict): Requirement configuration dictionary
- `row` (int): Grid row position

**Description:**
Creates a GUI row for each software requirement with status, version, and action buttons.

#### `detect_requirements(self)`
Scans the system for installed dependencies using multiple detection methods:
- Registry key checking
- Common path searching
- Version command execution

**Updates:** Requirement status and path information

#### `install_requirement(self, key)`
**Parameters:**
- `key` (str): Requirement identifier

**Description:**
Downloads and launches the installer for missing dependencies.

### Source Code Management

#### Repository Configuration
The application manages multiple AzerothCore variants:

```python
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
```

#### `create_source_rows(self, parent)`
**Parameters:**
- `parent` (tk.Widget): Parent frame

**Description:**
Creates GUI rows for each source repository with clone, update, and status tracking.

#### `clone_source(self, key)`
**Parameters:**
- `key` (str): Repository identifier

**Description:**
Clones the specified AzerothCore repository with progress tracking and error handling.

#### `update_source(self, key)`
**Parameters:**
- `key` (str): Repository identifier

**Description:**
Updates an existing repository using `git pull` with conflict resolution.

#### `detect_azerothcore_type(self)`
**Returns:** `str` - Detected repository type key

**Description:**
Analyzes cloned repositories to determine which AzerothCore variant is active.

### Module Management

#### `show_azerothcore_modules_window(self)`
Opens a window displaying official AzerothCore modules available for installation.

#### `show_community_modules_window(self)`
Opens a window displaying community-contributed modules.

#### `show_npcbot_modules_window(self)`
Opens a window displaying NPCBot-specific modules.

#### `show_playerbot_modules_window(self)`
Opens a window displaying PlayerBot-specific modules.

#### `load_azerothcore_modules(self, parent_frame, window)`
**Parameters:**
- `parent_frame` (tk.Widget): Parent container
- `window` (tk.Toplevel): Module window instance

**Description:**
Fetches and displays the list of available AzerothCore modules from GitHub API.

#### `clone_selected_modules(self, window)`
**Parameters:**
- `window` (tk.Toplevel): Module selection window

**Description:**
Clones all selected modules into the appropriate directories.

#### `detect_cloned_modules(self, modules)`
**Parameters:**
- `modules` (list): List of module dictionaries

**Returns:** `list` - Modules with clone status updated

**Description:**
Checks which modules are already cloned in the local environment.

### Build System

#### `cmake_build(self)`
Executes the CMake configuration phase with proper generator and architecture settings.

**Process:**
1. Validates source repository exists
2. Creates Build directory
3. Configures CMake with Visual Studio 2022 generator
4. Sets up Boost and MySQL paths
5. Generates build files

#### `msbuild_compile(self)`
Executes the MSBuild compilation phase.

**Process:**
1. Validates CMake configuration exists
2. Compiles using MSBuild with Release configuration
3. Tracks progress and handles errors
4. Updates GUI with build status

#### `create_repack(self)`
Creates a server deployment package (repack).

**Process:**
1. Copies compiled binaries to Repack folder
2. Sets up configuration files
3. Prepares database structure
4. Creates launch scripts

### Server Management

#### `start_auth(self)`
Launches the authentication server (`authserver.exe`) in a new console window.

#### `start_world(self)`
Launches the world server (`worldserver.exe`) in a new console window.

### Configuration Management

#### `_load_custom_url_config(self)`
Loads saved custom repository URL from configuration file.

#### `_save_custom_url_config(self)`
Saves custom repository URL to configuration file.

#### `_load_cloned_source(self)`
**Returns:** `str` - Previously cloned source type

**Description:**
Loads the last successfully cloned source from configuration.

#### `_save_cloned_source(self, source_key)`
**Parameters:**
- `source_key` (str): Source identifier to save

**Description:**
Saves the currently cloned source type to configuration.

### Utility Methods

#### `clear_console(self)`
Clears the console output text widget.

#### `save_console_log(self)`
Opens a file dialog to save current console output to a text file.

#### `open_logs_folder(self)`
Opens the logs directory in Windows Explorer.

#### `delete_logs(self)`
Prompts user and deletes all log files from the logs directory.

#### `delete_config(self)`
Prompts user and deletes all configuration files.

#### `delete_repack(self)`
Prompts user and deletes the server repack directory.

#### `delete_gitsource(self)`
Prompts user and deletes all cloned source repositories.

#### `delete_build(self)`
Prompts user and deletes all build artifacts.

## Data Structures

### Requirements Dictionary Format
```python
{
    "name": "Display Name",
    "version_check": "command --version",  # Command to check version
    "registry_keys": [                     # Windows registry locations
        r"SOFTWARE\Path\To\Key"
    ],
    "common_paths": [                      # Common installation paths
        r"C:\Program Files\App\app.exe"
    ],
    "download_url": "https://...",         # Download URL for installer
    "install_path": r"C:\Program Files\App",  # Default installation path
    "detected": False,                     # Detection status
    "path": "",                           # Detected path
    "version": ""                         # Detected version
}
```

### Module Dictionary Format
```python
{
    "name": "Module Name",
    "description": "Module description",
    "clone_url": "https://github.com/...",
    "html_url": "https://github.com/...",
    "cloned": False                       # Clone status
}
```

## Error Handling

The application implements comprehensive error handling:

- **GUI Error Dialogs**: User-friendly error messages via `messagebox.showerror()`
- **Console Logging**: Detailed error information logged to console
- **File Logging**: All errors saved to session log files
- **Process Recovery**: Graceful handling of subprocess failures
- **Network Resilience**: Retry logic for network operations

## Threading

Long-running operations are executed in separate threads to prevent GUI freezing:

- Repository cloning operations
- Module fetching from GitHub API
- Build processes (CMake and MSBuild)
- File operations and downloads

## Security Considerations

- **Path Validation**: All file paths are validated before operations
- **Process Isolation**: Subprocesses run with limited privileges
- **Input Sanitization**: User inputs are sanitized before shell execution
- **Resource Cleanup**: Temporary files and handles are properly cleaned up