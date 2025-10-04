# AzerothCore Builder - User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Requirements Setup](#requirements-setup)
3. [Source Code Management](#source-code-management)
4. [Module Installation](#module-installation)
5. [Building AzerothCore](#building-azerothcore)
6. [Server Setup and Launch](#server-setup-and-launch)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)

## Getting Started

### First Launch
1. Download `ACB.exe` from the releases page
2. Create a dedicated folder (e.g., `C:\AzerothCore-Builder\`)
3. Place `ACB.exe` in this folder
4. **Right-click** on `ACB.exe` and select **"Run as Administrator"**
5. The application will create necessary folders and files on first launch

### Understanding the Interface
ACB has three main tabs:
- **Requirements**: Check and install build dependencies
- **Build**: Manage source code and compile the server
- **Console**: Monitor operations and view detailed logs

## Requirements Setup

### Step 1: Check Dependencies
1. Open the **Requirements** tab
2. ACB will automatically scan your system for installed tools
3. Each requirement shows:
   - ✅ **Green**: Installed and detected
   - ❌ **Red**: Missing or not detected
   - ⚠️ **Yellow**: Partially detected or issues found

### Step 2: Install Missing Dependencies

#### Git for Windows
- **Purpose**: Version control and repository management
- **Auto-Install**: Click "Install" button to download and launch installer
- **Manual Install**: Download from [git-scm.com](https://git-scm.com/)
- **Verification**: ACB checks `git --version` command

#### Boost Libraries
- **Purpose**: C++ library dependencies required by AzerothCore
- **Supported Versions**: 1.78.0 through 1.84.0
- **Installation**: 
  - Click "Install" to download pre-built binaries
  - Extract to `C:\local\boost_1_XX_0\` folder
  - ACB searches common installation paths automatically

#### MySQL Server
- **Purpose**: Database backend for character and world data
- **Recommended**: MySQL 8.0 or later
- **Installation**:
  - Download MySQL Installer from [mysql.com](https://mysql.com/)
  - Choose "Custom" installation
  - Install MySQL Server and MySQL Workbench
  - Set root password (remember this for later)

#### OpenSSL
- **Purpose**: Cryptographic library for secure connections
- **Installation**: ACB provides direct download link
- **Path**: Usually installs to `C:\Program Files\OpenSSL-Win64\`

#### CMake
- **Purpose**: Build system generator
- **Version**: 3.28.1 or later recommended
- **Installation**: ACB downloads portable version
- **Alternative**: Install from [cmake.org](https://cmake.org/)

#### Visual Studio 2022
- **Purpose**: Primary C++ compiler and build environment
- **Editions**: Community (free), Professional, or Enterprise
- **Required Workloads**:
  - "Desktop development with C++"
  - "C++ CMake tools for Visual Studio"
- **Installation**: 
  - Click "Install" to download VS installer
  - Select required workloads during installation

#### HeidiSQL (Optional)
- **Purpose**: Database management and query tool
- **Installation**: Click "Install" for portable version
- **Alternative**: Use MySQL Workbench or any MySQL client

### Step 3: Verify Installation
1. Click **"🔄 Refresh"** button in Requirements tab
2. Ensure all required tools show ✅ green status
3. Check that paths and versions are correctly detected

## Source Code Management

### Understanding AzerothCore Variants

#### Standard AzerothCore
- **Repository**: `https://github.com/azerothcore/azerothcore-wotlk`
- **Description**: Official AzerothCore repository
- **Best For**: Standard WoTLK server experience
- **Stability**: Most stable and well-tested

#### AzerothCore with NPCBots
- **Repository**: `https://github.com/trickerer/AzerothCore-wotlk-with-NPCBots`
- **Description**: Includes AI-controlled NPCs that can join player groups
- **Features**: 
  - NPCs can be hired as group members
  - AI-controlled combat and movement
  - Configurable NPC behavior
- **Best For**: Solo players or small groups wanting AI companions

#### AzerothCore with PlayerBots
- **Repository**: `https://github.com/liyunfan1223/azerothcore-wotlk.git`
- **Description**: Advanced bot system with player-like behavior
- **Features**:
  - More sophisticated AI than NPCBots
  - Player-like decision making
  - Advanced group coordination
- **Best For**: Servers wanting realistic bot players

#### Custom Repository
- **Purpose**: Use your own fork or modified version
- **Setup**: Enter your repository URL in the custom field
- **Use Cases**: 
  - Personal modifications
  - Organization-specific forks
  - Testing experimental features

### Cloning Source Code

#### First-Time Clone
1. Go to **Build** tab
2. Choose your preferred AzerothCore variant
3. Click **"📥 Clone"** button for selected variant
4. Monitor progress in the Console tab
5. Wait for "✅ Clone completed" message

#### Updating Existing Source
1. Click **"🔄 Update"** button for your cloned repository
2. ACB will perform `git pull` to get latest changes
3. Conflicts will be automatically handled where possible
4. Check console for any manual conflict resolution needed

### Managing Multiple Sources
- ACB can have multiple variants cloned simultaneously
- Only one can be "active" for building at a time
- Switch between sources by cloning different variants
- Each variant is stored in separate folders under `GitSource/`

## Module Installation

### Understanding Module Types

#### AzerothCore Official Modules
- **Source**: Official AzerothCore organization repositories
- **Quality**: High quality, well-maintained
- **Examples**: 
  - mod-individual-progression
  - mod-server-auto-shutdown
  - mod-transmog
- **Installation**: Managed through ACB's module system

#### Community Modules
- **Source**: Community-contributed modifications
- **Variety**: Wide range of gameplay modifications
- **Quality**: Varies, check descriptions and ratings
- **Examples**: Custom classes, new zones, gameplay tweaks

#### NPCBot Modules
- **Purpose**: Extend NPCBot functionality
- **Requirements**: Only compatible with NPCBot variant
- **Features**: Additional bot behaviors, commands, configurations

#### PlayerBot Modules  
- **Purpose**: Enhance PlayerBot systems
- **Requirements**: Only compatible with PlayerBot variant
- **Features**: Advanced AI behaviors, coordination systems

### Installing Modules

#### Step 1: Browse Available Modules
1. Click module type button (🧩 AzerothCore, 🌐 Community, etc.)
2. Wait for module list to load from GitHub
3. Browse available modules with descriptions
4. Note compatibility requirements

#### Step 2: Select Modules
1. Check boxes next to desired modules
2. Read descriptions carefully
3. Consider dependencies and compatibility
4. Verify module works with your AzerothCore variant

#### Step 3: Clone Selected Modules
1. Click **"📥 Clone Selected Modules"** 
2. Choose target repository (if multiple variants are cloned)
3. Monitor cloning progress in console
4. Wait for completion messages

#### Step 4: Rebuild AzerothCore
1. After adding modules, rebuild AzerothCore
2. CMake will detect new modules automatically
3. Compilation will include module code
4. Test module functionality after build

### Managing Modules

#### Viewing Installed Modules
- Installed modules appear with ✅ status in module windows
- Check `GitSource/azerothcore-wotlk/modules/` directory
- Each module has its own subdirectory

#### Updating Modules
- Use "Update" buttons in module windows
- Updates pull latest changes from module repositories
- Rebuild AzerothCore after module updates

#### Removing Modules
- Manually delete module folders from `modules/` directory
- Rebuild AzerothCore to remove module code
- Clean build recommended after module removal

## Building AzerothCore

### Pre-Build Checklist
1. ✅ All requirements installed and detected
2. ✅ AzerothCore source cloned successfully  
3. ✅ Desired modules installed
4. ✅ At least 50GB free disk space
5. ✅ Stable internet connection (for downloading dependencies)

### Build Process

#### Step 1: Configure Build Options
1. In **Build** tab, locate build controls
2. **Generate extractors**: 
   - ✅ **Checked** (Recommended): Creates map/vmap/mmaps extractors
   - ⬜ **Unchecked**: Skip extractor generation (faster build)
3. **Build Configuration**: Automatically set to Release (optimized)

#### Step 2: Start Build Process
1. Click **"🔨 Build"** button
2. Build process has two phases:
   - **CMake Configuration**: Sets up build system
   - **MSBuild Compilation**: Compiles source code

#### Step 3: Monitor Progress
1. Watch progress bars for current operation
2. Monitor console output for detailed information
3. Build time: 30-90 minutes depending on system specs
4. **Do not close ACB during build process**

#### Step 4: Handle Build Completion
- **Success**: ✅ "Build completed successfully" message
- **Failure**: ❌ Check console for error details
- **Cancellation**: Click "❌ Cancel Build" if needed

### Build Phases Explained

#### CMake Configuration Phase
- **Duration**: 2-5 minutes
- **Purpose**: 
  - Detect installed libraries (Boost, MySQL, OpenSSL)
  - Configure build system for Visual Studio
  - Generate project files and makefiles
- **Output**: Creates `.sln` and `.vcxproj` files in `Build/` directory

#### MSBuild Compilation Phase  
- **Duration**: 25-85 minutes
- **Purpose**:
  - Compile C++ source code
  - Link libraries and dependencies  
  - Generate executable files
- **Output**: Creates `authserver.exe`, `worldserver.exe`, and tools

### Build Output Files
After successful build, check `Build/bin/Release/` directory:
- `authserver.exe` - Authentication server
- `worldserver.exe` - World server  
- `mmaps_generator.exe` - Movement map generator
- `vmap4_assembler.exe` - Visual map assembler
- `vmap4_extractor.exe` - Visual map extractor
- `map_extractor.exe` - Map data extractor

## Server Setup and Launch

### Creating Server Repack

#### Step 1: Generate Repack
1. After successful build, click **"📦 Create Repack"**
2. ACB copies executables and creates server structure
3. Monitor console for repack creation progress
4. Repack created in `Repack/` directory

#### Step 2: Repack Structure
```
Repack/
├── authserver.exe          # Authentication server
├── worldserver.exe         # World server
├── configs/                # Configuration files
│   ├── authserver.conf     # Auth server config
│   └── worldserver.conf    # World server config
├── data/                   # Game data (when added)
└── logs/                   # Server log files
```

### Database Setup

#### Step 1: Download World Database
1. Click **"🌍 Download World DB"** button  
2. ACB downloads latest TDB (Trinity Database)
3. Database saved to `Data/` directory
4. File format: `.sql` scripts for MySQL import

#### Step 2: Import Database
1. Open MySQL Workbench or HeidiSQL
2. Connect to your MySQL server
3. Create databases:
   ```sql
   CREATE DATABASE acore_auth;
   CREATE DATABASE acore_characters;  
   CREATE DATABASE acore_world;
   ```
4. Import database files:
   - Auth DB: Import from AzerothCore repository
   - Characters DB: Import from AzerothCore repository  
   - World DB: Import downloaded TDB file

#### Step 3: Configure Database Connection
1. Edit `Repack/configs/authserver.conf`:
   ```ini
   LoginDatabaseInfo = "127.0.0.1;3306;root;password;acore_auth"
   ```
2. Edit `Repack/configs/worldserver.conf`:
   ```ini
   LoginDatabaseInfo = "127.0.0.1;3306;root;password;acore_auth"
   CharacterDatabaseInfo = "127.0.0.1;3306;root;password;acore_characters"
   WorldDatabaseInfo = "127.0.0.1;3306;root;password;acore_world"
   ```

### Server Launch

#### Step 1: Start Authentication Server
1. Click **"▶️ Start Auth"** button
2. New console window opens with authserver.exe
3. Wait for "Auth server ready" message
4. Leave this window open while server runs

#### Step 2: Start World Server  
1. Click **"▶️ Start World"** button
2. New console window opens with worldserver.exe
3. Server loads maps, creatures, and game data
4. Wait for "World server ready" message

#### Step 3: Verify Server Status
1. Both servers should show "ready" status
2. Check for error messages in server consoles
3. Test connection with WoW 3.3.5a client
4. Create GM account if needed

### Creating Game Master Account
1. In world server console, type:
   ```
   account create username password
   account set gmlevel username 3 -1
   ```
2. Use this account to log in with GM privileges
3. GM level 3 provides full administrative access

## Advanced Features

### Custom Repository URLs

#### Setting Custom AzerothCore URL
1. In Build tab, find Custom repository row
2. Click **"🔗 Edit URL"** button
3. Enter your custom repository URL
4. Save and clone as normal

#### Module URL Customization
1. In module windows, click **"🔗"** next to module names
2. Edit URLs to point to your forks
3. Useful for:
   - Personal module modifications
   - Organization-specific versions
   - Testing unreleased changes

### Configuration Management

#### Saving Configurations
ACB automatically saves:
- Custom repository URLs
- Last cloned source type
- HeidiSQL download preferences
- Window positions and settings

#### Configuration Files Location
- `config/custom_urls.json` - Custom repository URLs
- `config/cloned_source.txt` - Last active source
- `config/heidisql_config.json` - HeidiSQL preferences

#### Resetting Configuration
1. Click **"🗑️ Delete Config"** in Console tab
2. Confirm deletion
3. Restart ACB for fresh configuration

### Log Management

#### Session Logs
- Every ACB session creates unique log file
- Location: `logs/acb_session_YYYYMMDD_HHMMSS.log`
- Contains all console output and error details

#### Log Features
1. **Clear Console**: Clears current session display
2. **Save Log**: Export current console to file
3. **Open Logs Folder**: Browse all session logs
4. **Delete Logs**: Remove old log files

#### Log Cleanup
- ACB automatically removes logs older than 30 days
- Manual cleanup via "Delete Logs" button
- Keep recent logs for troubleshooting

### Cleanup Operations

#### Selective Cleanup
- **Delete Config**: Remove saved settings
- **Delete Repack**: Remove server deployment
- **Delete GitSource**: Remove all source code
- **Delete Build**: Remove compilation artifacts

#### Complete Reset
1. Delete Repack (removes server files)
2. Delete GitSource (removes source code)  
3. Delete Build (removes compiled binaries)
4. Delete Config (removes settings)
5. Delete Logs (removes session history)

## Troubleshooting

### Common Build Issues

#### "CMake Error: Could not find Boost"
**Symptoms**: CMake fails with Boost detection error
**Solutions**:
1. Verify Boost is installed in `C:\local\boost_1_XX_0\`
2. Check ACB detected Boost in Requirements tab
3. Try different Boost version (1.78-1.84 supported)
4. Reinstall Boost using ACB installer

#### "MSBuild Error: Cannot find Visual Studio"
**Symptoms**: MSBuild fails to start or find compiler
**Solutions**:
1. Verify Visual Studio 2022 is installed
2. Ensure "Desktop development with C++" workload installed
3. Run Visual Studio Installer to modify installation
4. Restart ACB after Visual Studio installation

#### "Git Authentication Failed"
**Symptoms**: Cannot clone private repositories
**Solutions**:
1. Configure Git credentials: `git config --global user.name "Your Name"`
2. Set up SSH keys for GitHub authentication
3. Use HTTPS URLs with personal access tokens
4. Check firewall settings for Git operations

#### "Insufficient Disk Space"
**Symptoms**: Build fails with disk space errors
**Solutions**:
1. Free up disk space (need 50GB+ for full build)
2. Clean temporary files and old builds
3. Move ACB to drive with more space
4. Delete unused AzerothCore variants

### Network Issues

#### "Module List Failed to Load"
**Symptoms**: Module windows show loading errors
**Solutions**:
1. Check internet connection
2. Verify GitHub is accessible
3. Try again later (GitHub API rate limits)
4. Check firewall settings for ACB.exe

#### "Download Failed" Errors
**Symptoms**: Dependency downloads fail
**Solutions**:
1. Check internet connectivity
2. Verify download URLs are accessible
3. Try manual download and installation
4. Check antivirus blocking downloads

### Performance Optimization

#### Slow Build Times
**Solutions**:
1. Close unnecessary applications during build
2. Ensure sufficient RAM (8GB minimum, 16GB recommended)
3. Use SSD storage for better I/O performance
4. Disable real-time antivirus scanning on build folders

#### Memory Issues
**Solutions**:
1. Close other memory-intensive applications
2. Increase virtual memory (page file) size
3. Build individual targets instead of full solution
4. Upgrade to more RAM if consistently problematic

### Getting Help

#### Before Asking for Help
1. Check console output for specific error messages
2. Save current log file for reference
3. Note your system specifications
4. Try basic troubleshooting steps

#### Information to Provide
- ACB version and build date
- Windows version and architecture
- Complete error messages from console
- Session log file (`logs/acb_session_*.log`)
- Steps that led to the issue

#### Support Channels
- GitHub Issues for bug reports
- AzerothCore Discord for community help
- ACB documentation and troubleshooting guides