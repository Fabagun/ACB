# Installation and Setup Guide - AzerothCore Builder (ACB)

## Quick Start

### For End Users (Recommended)
1. Download `ACB.exe` from the [latest release](https://github.com/your-repo/releases)
2. Create a folder: `C:\AzerothCore-Builder\`
3. Place `ACB.exe` in the folder
4. Right-click `ACB.exe` → "Run as Administrator"
5. Follow the Requirements tab to install dependencies

### For Developers
1. Clone the repository
2. Install Python 3.8+
3. Run `pip install -r python_requirements.txt`
4. Execute `python ACB.py`

## Detailed Installation

### System Requirements
- Windows 10/11 (64-bit)
- 8+ GB RAM (16 GB recommended)
- 50+ GB free disk space
- Stable internet connection

### Step 1: Download ACB

#### Option A: Pre-built Executable (Recommended)
1. Visit the [releases page](https://github.com/your-repo/releases)
2. Download the latest `ACB.exe`
3. No Python installation required

#### Option B: Python Source Code
1. Ensure Python 3.8+ is installed from [python.org](https://python.org)
2. Clone or download the source code
3. Install dependencies: `pip install -r python_requirements.txt`

### Step 2: First Launch
1. Create a dedicated directory (e.g., `C:\AzerothCore-Builder\`)
2. Place `ACB.exe` in this directory
3. **Important**: Right-click → "Run as Administrator"
4. ACB will create necessary folders on first run:
   ```
   AzerothCore-Builder/
   ├── ACB.exe
   ├── logs/           # Session logs
   ├── config/         # Configuration files
   ├── GitSource/      # Source repositories
   ├── Build/          # Compilation output
   ├── Repack/         # Server package
   └── Data/           # Database files
   ```

### Step 3: Install Dependencies
ACB will guide you through installing required build tools:

1. **Open Requirements Tab**: Check current system status
2. **Install Missing Tools**: Click "Install" buttons for red items
3. **Follow Installation Wizards**: Complete each installer
4. **Refresh Status**: Click "🔄 Refresh" to verify installations

#### Required Dependencies (Auto-detected)
- **Git for Windows**: Version control
- **Boost Libraries**: C++ dependencies (1.78-1.84)
- **MySQL Server**: Database backend  
- **OpenSSL**: Cryptographic library
- **CMake**: Build system generator
- **Visual Studio 2022**: C++ compiler

#### Visual Studio 2022 Workloads
When installing VS2022, ensure these workloads are selected:
- ✅ Desktop development with C++
- ✅ C++ CMake tools for Visual Studio
- ✅ Windows 10/11 SDK (latest)

### Step 4: First Build
1. **Switch to Build Tab**
2. **Choose AzerothCore Variant**:
   - Standard: Official AzerothCore
   - NPCBots: With AI companions
   - PlayerBots: Advanced bot system
3. **Clone Repository**: Click "📥 Clone"
4. **Optional**: Install modules via module buttons
5. **Start Build**: Click "🔨 Build" (30-90 minutes)

## Advanced Setup

### Multiple AzerothCore Variants
You can have multiple variants installed:
```
GitSource/
├── azerothcore-wotlk/          # Current active source
├── azerothcore-npcbots/        # NPCBot variant backup
└── modules/                    # Installed modules
    ├── mod-transmog/
    ├── mod-individual-xp/
    └── community-modules/
```

### Custom Development Setup
For developers wanting to modify ACB:

#### 1. Development Environment
```bash
# Clone repository
git clone https://github.com/your-repo/azerothcore-builder
cd azerothcore-builder

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r python_requirements.txt
pip install -r dev_requirements.txt
```

#### 2. IDE Setup (VS Code)
```json
// .vscode/settings.json
{
    "python.defaultInterpreter": "./venv/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black"
}
```

#### 3. Run Development Version
```bash
python ACB.py
```

### Building Executable
To create your own executable:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icons/ACB.ico ACB.py
```

## Configuration

### Network Configuration
If behind corporate firewall or proxy:

#### Git Configuration
```bash
git config --global http.proxy http://proxy:port
git config --global https.proxy https://proxy:port
```

#### Python Proxy
```bash
pip install --proxy http://proxy:port package_name
```

### Performance Optimization

#### For Slow Systems
1. **Disable Windows Defender** real-time scanning for ACB directories
2. **Close Unnecessary Applications** during builds
3. **Use SSD Storage** for better I/O performance
4. **Increase Virtual Memory** if RAM is limited

#### For Build Servers
1. **Automate Dependency Installation** with PowerShell scripts
2. **Use Network Drives** for shared repositories
3. **Schedule Builds** during off-peak hours
4. **Monitor Resource Usage** with built-in logging

### Security Configuration

#### Windows Defender Exclusions
Add these paths to Windows Defender exclusions:
- `C:\AzerothCore-Builder\`
- `C:\AzerothCore-Builder\GitSource\`
- `C:\AzerothCore-Builder\Build\`

#### Firewall Configuration
Ensure these applications can access the internet:
- `ACB.exe`
- `git.exe`
- `cmake.exe`
- `MSBuild.exe`

## Troubleshooting Installation

### Common Issues

#### "ACB.exe is not recognized"
**Cause**: Windows SmartScreen protection
**Solution**: 
1. Right-click ACB.exe → Properties
2. Check "Unblock" if present
3. Click "Run anyway" on SmartScreen prompt

#### "Git not found" after installation
**Cause**: PATH environment not updated
**Solution**:
1. Restart ACB after Git installation
2. Manually add Git to PATH if needed
3. Verify with: `git --version` in Command Prompt

#### "Visual Studio not detected"
**Cause**: Missing required workloads
**Solution**:
1. Run Visual Studio Installer
2. Modify existing installation
3. Add "Desktop development with C++" workload
4. Restart ACB and refresh requirements

#### "Access denied" errors
**Cause**: Insufficient permissions
**Solution**:
1. Always run ACB as Administrator
2. Check folder permissions
3. Temporarily disable antivirus if needed

#### "Build failed with Boost errors"
**Cause**: Boost not found or wrong version
**Solution**:
1. Install Boost to `C:\local\boost_1_XX_0\`
2. Ensure version is 1.78-1.84
3. Verify folder structure has `boost\` subdirectory

### Getting Help

#### Before Seeking Help
1. Check the console output for specific errors
2. Save the current session log
3. Try the troubleshooting steps above
4. Restart ACB and try again

#### When Reporting Issues
Include this information:
- ACB version
- Windows version and architecture
- Complete error message from console
- Session log file (from logs/ folder)
- Steps to reproduce the issue

#### Support Channels
- **GitHub Issues**: Bug reports and feature requests
- **AzerothCore Discord**: Community support
- **Documentation**: Check README and guides first

## Uninstallation

### Remove ACB
1. Close ACB if running
2. Delete the ACB directory (e.g., `C:\AzerothCore-Builder\`)
3. Remove Windows Defender exclusions
4. Optionally remove installed dependencies

### Keep Dependencies
The build tools (Git, Visual Studio, etc.) can be kept for other development work.

### Complete Removal
To remove everything including dependencies:
1. Uninstall via Windows "Add or Remove Programs":
   - Git for Windows
   - Visual Studio 2022
   - MySQL Server
   - CMake
   - OpenSSL
2. Delete remaining folders:
   - `C:\local\boost_*`
   - `C:\MySQL\`
   - Build artifacts and databases

## Next Steps

After successful installation:
1. **Read the User Guide** for detailed usage instructions
2. **Join the Community** on Discord for tips and support  
3. **Check for Updates** regularly for new features
4. **Backup Important Data** before major operations

---

**Need Help?** Check the [User Guide](USER_GUIDE.md) for detailed usage instructions or the [Troubleshooting section](USER_GUIDE.md#troubleshooting) for common solutions.