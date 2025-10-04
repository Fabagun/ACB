# Developer Documentation - AzerothCore Builder (ACB)

## Table of Contents
1. [Development Environment Setup](#development-environment-setup)
2. [Architecture Overview](#architecture-overview)
3. [Code Structure](#code-structure)
4. [Contributing Guidelines](#contributing-guidelines)
5. [Building and Packaging](#building-and-packaging)
6. [Testing](#testing)
7. [Release Process](#release-process)

## Development Environment Setup

### Prerequisites
- **Python 3.8+**: Primary development language
- **Git**: Version control
- **Windows 10/11**: Target platform for development and testing
- **Visual Studio Code**: Recommended IDE with Python extension

### Required Python Packages
```bash
pip install tkinter pillow psutil pyinstaller
```

### Development Dependencies
```bash
pip install pytest pytest-cov black flake8 mypy
```

### Repository Setup
```bash
git clone https://github.com/your-org/azerothcore-builder
cd azerothcore-builder
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### IDE Configuration

#### Visual Studio Code Settings
Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreter": "./venv/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=88"],
    "files.associations": {
        "*.py": "python"
    }
}
```

#### Launch Configuration
Create `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "ACB Debug",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/ACB.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

## Architecture Overview

### High-Level Architecture
ACB follows a Model-View-Controller (MVC) pattern with the following components:

```
┌─────────────────────────────────────────────┐
│                GUI Layer                    │
│  (tkinter widgets, event handling)          │
├─────────────────────────────────────────────┤
│              Business Logic                 │
│  (AzerothCoreBuilder class methods)         │
├─────────────────────────────────────────────┤
│               Data Layer                    │
│  (File I/O, Git operations, subprocess)     │
└─────────────────────────────────────────────┘
```

### Key Design Patterns

#### Singleton Pattern
The main `AzerothCoreBuilder` class acts as a singleton, managing all application state and operations.

#### Observer Pattern  
GUI widgets observe model state changes through callback functions and update accordingly.

#### Command Pattern
User actions are encapsulated as methods that can be called from GUI events or programmatically.

#### Factory Pattern
Widget creation is abstracted through factory methods like `create_requirement_row()` and `create_source_row()`.

### Threading Model
- **Main Thread**: GUI operations and event handling
- **Worker Threads**: Long-running operations (Git clones, builds, downloads)
- **Thread Safety**: GUI updates from worker threads use `tkinter.after()`

## Code Structure

### Main Class: AzerothCoreBuilder

#### Initialization Methods
```python
def __init__(self, root)              # Main constructor
def _init_app_directory(self)         # Determine app paths  
def _setup_logging(self)              # Initialize logging
def setup_ui(self)                    # Create GUI interface
```

#### GUI Creation Methods
```python
def create_requirement_row(...)       # Requirements tab rows
def create_source_rows(...)           # Build tab source rows  
def create_module_buttons(...)        # Module selection buttons
def add_app_icon(...)                # Application icon handling
```

#### Core Functionality Methods
```python
def detect_requirements(self)         # Scan for installed tools
def clone_source(self, key)          # Git clone operations
def cmake_build(self)                # CMake configuration  
def msbuild_compile(self)            # Visual Studio compilation
def create_repack(self)              # Server package creation
```

#### Module Management Methods
```python
def show_*_modules_window(self)      # Display module selection
def load_*_modules(...)              # Fetch module lists
def clone_selected_modules(...)       # Install selected modules
def detect_cloned_modules(...)        # Check module status
```

#### Utility Methods
```python
def log_to_console(self, message)    # Logging and console output
def update_*_status(...)             # Status updates
def _load_*_config(self)             # Configuration management
def _save_*_config(self)             # Configuration persistence
```

### Configuration System

#### File Locations
- `config/custom_urls.json`: Custom repository URLs
- `config/cloned_source.txt`: Active source repository
- `config/heidisql_config.json`: HeidiSQL preferences

#### Configuration Classes
```python
class ConfigManager:
    def load_config(self, filename)
    def save_config(self, filename, data)
    def get_config_path(self, filename)
```

### Error Handling Strategy

#### Error Types
1. **User Errors**: Invalid inputs, missing files
2. **System Errors**: Permission issues, disk space
3. **Network Errors**: Download failures, Git operations
4. **Build Errors**: Compilation failures, missing dependencies

#### Error Handling Pattern
```python
try:
    # Operation
    self.log_to_console("✅ Success message")
except SpecificException as e:
    error_msg = f"Specific error context: {str(e)}"
    messagebox.showerror("Error Title", error_msg) 
    self.log_to_console(f"❌ {error_msg}")
except Exception as e:
    error_msg = f"Unexpected error: {str(e)}"
    messagebox.showerror("Unexpected Error", error_msg)
    self.log_to_console(f"❌ {error_msg}")
```

### Logging System

#### Log Levels
- **Info**: General operation messages (✅, 📁, 🔍)
- **Warning**: Non-fatal issues (⚠️)  
- **Error**: Fatal issues (❌)
- **Progress**: Build progress updates

#### Log Output
- **Console Widget**: Real-time display with colors
- **File Output**: Timestamped session logs
- **Retention**: Automatic cleanup of old logs

## Contributing Guidelines

### Code Style

#### Python Style Guide
- Follow PEP 8 standards
- Use Black formatter with 88-character line length
- Use type hints where appropriate
- Document all public methods and classes

#### Naming Conventions
```python
# Classes: PascalCase
class AzerothCoreBuilder:
    
# Methods: snake_case  
def create_requirement_row(self):

# Constants: UPPER_SNAKE_CASE
DEFAULT_TIMEOUT = 30

# Private methods: _snake_case
def _load_config(self):
```

#### Documentation Standards
```python
def method_name(self, param1: str, param2: int) -> bool:
    """
    Brief description of method purpose.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: Description of when this exception is raised
    """
    pass
```

### Git Workflow

#### Branch Strategy
- **main**: Stable, release-ready code
- **develop**: Integration branch for features
- **feature/**: Individual feature branches
- **hotfix/**: Critical bug fixes
- **release/**: Release preparation branches

#### Commit Message Format
```
type(scope): brief description

Detailed explanation if needed

- Bullet points for multiple changes
- Reference issues with #123

Closes #123
```

**Types**: feat, fix, docs, style, refactor, test, chore

#### Pull Request Process
1. Create feature branch from `develop`
2. Implement changes with tests
3. Run full test suite and linting
4. Submit PR with clear description
5. Address review feedback
6. Merge after approval

### Testing Strategy

#### Unit Tests
```python
import unittest
from unittest.mock import Mock, patch
from ACB import AzerothCoreBuilder

class TestAzerothCoreBuilder(unittest.TestCase):
    def setUp(self):
        self.mock_root = Mock()
        self.acb = AzerothCoreBuilder(self.mock_root)
    
    def test_detect_requirements(self):
        # Test requirement detection logic
        pass
        
    @patch('subprocess.run')
    def test_git_operations(self, mock_subprocess):
        # Test Git clone operations
        pass
```

#### Integration Tests
```python
class TestIntegration(unittest.TestCase):
    def test_full_build_process(self):
        # Test complete build workflow
        pass
        
    def test_module_installation(self):
        # Test module cloning and integration
        pass
```

#### GUI Tests
```python
import tkinter as tk
from tkinter import ttk

class TestGUI(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.acb = AzerothCoreBuilder(self.root)
        
    def tearDown(self):
        self.root.destroy()
        
    def test_widget_creation(self):
        # Test GUI widget creation and layout
        pass
```

### Performance Guidelines

#### Memory Management
- Use generators for large data sets
- Clean up subprocess handles
- Avoid circular references
- Monitor memory usage during long operations

#### Threading Best Practices
- Keep GUI operations on main thread
- Use thread-safe queues for communication
- Implement proper thread cleanup
- Handle thread exceptions gracefully

#### I/O Optimization
- Use asynchronous operations where possible
- Implement progress callbacks for long operations
- Cache expensive operations
- Batch file operations when possible

## Building and Packaging

### Development Build
```bash
python ACB.py
```

### Creating Executable
```bash
pyinstaller --onefile --windowed --icon=icons/ACB.ico ACB.py
```

### Advanced PyInstaller Options
```bash
pyinstaller --onefile \
            --windowed \
            --icon=icons/ACB.ico \
            --add-data "icons;icons" \
            --name="AzerothCore-Builder" \
            --version-file=version.txt \
            ACB.py
```

### Version File (version.txt)
```python
# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1,0,0,0),
    prodvers=(1,0,0,0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable('040904B0', [
        StringStruct('CompanyName', 'AzerothCore Community'),
        StringStruct('FileDescription', 'AzerothCore Builder'),
        StringStruct('FileVersion', '1.0.0.0'),
        StringStruct('InternalName', 'ACB'),
        StringStruct('LegalCopyright', 'MIT License'),
        StringStruct('OriginalFilename', 'ACB.exe'),
        StringStruct('ProductName', 'AzerothCore Builder'),
        StringStruct('ProductVersion', '1.0.0.0')
      ])
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
```

### Build Automation
Create `build.bat`:
```batch
@echo off
echo Building AzerothCore Builder...
python -m venv build_env
call build_env\Scripts\activate
pip install -r requirements.txt
pyinstaller ACB.spec
echo Build completed: dist/ACB.exe
pause
```

### Distribution Package
```
ACB-v1.0.0/
├── ACB.exe
├── README.md
├── LICENSE
├── CHANGELOG.md
└── icons/
    └── ACB.ico
```

## Testing

### Test Environment Setup
```bash
pip install pytest pytest-cov pytest-mock
```

### Running Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=ACB --cov-report=html

# Specific test file
pytest tests/test_requirements.py

# Verbose output
pytest -v
```

### Test Structure
```
tests/
├── __init__.py
├── test_requirements.py      # Dependency detection tests
├── test_git_operations.py    # Git functionality tests  
├── test_build_system.py      # Build process tests
├── test_gui.py              # GUI component tests
├── test_config.py           # Configuration tests
└── fixtures/                # Test data and mocks
    ├── sample_repos.json
    └── mock_processes.py
```

### Continuous Integration

#### GitHub Actions Workflow
Create `.github/workflows/test.yml`:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', 3.11]
        
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
        
    - name: Run tests
      run: |
        pytest --cov=ACB --cov-report=xml
        
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Release Process

### Version Management

#### Semantic Versioning
- **MAJOR**: Breaking changes
- **MINOR**: New features, backwards compatible
- **PATCH**: Bug fixes, backwards compatible

#### Version Update Process
1. Update version in `ACB.py`
2. Update `CHANGELOG.md`
3. Create version tag
4. Build release executable
5. Create GitHub release

### Release Checklist

#### Pre-Release
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Version numbers updated
- [ ] Changelog updated
- [ ] Build tested on clean Windows systems

#### Release Creation
- [ ] Create release branch
- [ ] Build final executable
- [ ] Test executable thoroughly
- [ ] Create GitHub release with assets
- [ ] Update documentation links

#### Post-Release
- [ ] Monitor for critical issues
- [ ] Update development version
- [ ] Plan next release features
- [ ] Community announcement

### Deployment

#### GitHub Releases
```bash
# Create tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Create release with GitHub CLI
gh release create v1.0.0 ./dist/ACB.exe --title "AzerothCore Builder v1.0.0" --notes-file CHANGELOG.md
```

#### Release Assets
- `ACB.exe` - Main executable
- `ACB-Portable.zip` - Portable version with dependencies
- `Source-Code.zip` - Source code archive
- `CHANGELOG.md` - Version changelog

### Maintenance

#### Long-term Support
- Security updates for critical vulnerabilities
- Compatibility updates for Windows versions
- Bug fixes for reported issues
- Dependency updates for security

#### End of Life Policy
- Announce EOL 6 months in advance
- Provide migration path to newer versions
- Archive old releases but keep accessible
- Maintain security fixes until EOL date