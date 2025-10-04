# AzerothCore Builder (ACB)

A comprehensive Windows GUI application for building AzerothCore World of Warcraft server from source code. ACB simplifies the complex process of setting up, compiling, and managing an AzerothCore server installation.

## 🎯 Overview

AzerothCore Builder (ACB) is designed to automate and streamline the process of building AzerothCore - an open-source World of Warcraft: Wrath of the Lich King server emulator. The application provides a user-friendly interface for:

- **Dependency Management**: Automatically detects and helps install required build tools
- **Source Code Management**: Clones and manages different AzerothCore variants
- **Module Integration**: Easy installation of community modules and extensions
- **Build Automation**: Automated CMake configuration and Visual Studio compilation
- **Server Management**: Built-in tools for starting/stopping server components

## ✨ Features

### 🔧 Automated Dependency Detection
- **Git for Windows**: Version control and repository management
- **Boost Libraries**: C++ library dependencies (1.78-1.84 support)
- **MySQL Server**: Database backend for game data
- **OpenSSL**: Cryptographic library for secure connections
- **CMake**: Build system generator
- **Visual Studio 2022**: Primary compilation toolchain
- **HeidiSQL**: Optional database management tool

### 🌟 AzerothCore Variants Support
- **Standard AzerothCore**: Official repository build
- **NPCBots Integration**: AI-controlled non-player characters
- **PlayerBots Integration**: Advanced bot system for players
- **Custom Repository**: Support for custom forks and modifications

### 📦 Module Management
- **AzerothCore Modules**: Official modules from the core team
- **Community Modules**: Third-party extensions and modifications
- **NPCBot Modules**: Specialized modules for NPCBot functionality
- **PlayerBot Modules**: Extensions for PlayerBot systems

### 🏗️ Build Process
- **Automated CMake**: Intelligent configuration with proper paths
- **Visual Studio Integration**: Seamless compilation with MSBuild
- **Progress Tracking**: Real-time build progress and status updates
- **Error Handling**: Comprehensive error reporting and troubleshooting

### 🎮 Server Management
- **Repack Creation**: Automated server package generation
- **Database Setup**: Integrated world and character database management
- **Server Startup**: Direct launch of auth and world servers
- **Log Management**: Comprehensive logging and debugging tools

## 📋 Requirements

### System Requirements
- **Operating System**: Windows 10/11 (64-bit)
- **RAM**: Minimum 8GB (16GB recommended)
- **Storage**: 50GB+ free space for full build
- **Internet**: Stable connection for downloading dependencies

### Required Software (Auto-detected/Installed)
1. **Git for Windows** (2.44.0+)
2. **Boost Libraries** (1.78.0 - 1.84.0)
3. **MySQL Server** (8.0+)
4. **OpenSSL** (3.5.2+)
5. **CMake** (3.28.1+)
6. **Visual Studio 2022** (Community/Professional/Enterprise)

## 🚀 Installation

### Option 1: Pre-built Executable (Recommended)
1. Download the latest `ACB.exe` from the releases page
2. Place it in a dedicated folder (e.g., `C:\AzerothCore-Builder\`)
3. Run `ACB.exe` as Administrator (required for some operations)

### Option 2: Python Script
1. Ensure Python 3.8+ is installed
2. Install required dependencies:
   ```bash
   pip install tkinter pillow psutil
   ```
3. Run the script:
   ```bash
   python ACB.py
   ```

## 📖 Usage Guide

### 1. Initial Setup
1. **Launch ACB** and navigate to the "Requirements" tab
2. **Check Dependencies**: ACB will automatically scan for installed tools
3. **Install Missing Tools**: Click "Install" for any missing dependencies
4. **Verify Installation**: Ensure all requirements show green status

### 2. Source Code Management
1. **Switch to Build Tab**: Access source management features
2. **Choose AzerothCore Variant**:
   - Standard: `https://github.com/azerothcore/azerothcore-wotlk`
   - NPCBots: `https://github.com/trickerer/AzerothCore-wotlk-with-NPCBots`
   - PlayerBots: `https://github.com/liyunfan1223/azerothcore-wotlk.git`
   - Custom: Set your own repository URL
3. **Clone Repository**: Click "Clone" to download source code
4. **Update Sources**: Use "Update" to pull latest changes

### 3. Module Installation
1. **Access Module Buttons**: Click on module type buttons
   - 🧩 AzerothCore Modules
   - 🌐 Community Modules  
   - 🤖 NPCBot Modules
   - 👤 PlayerBot Modules
2. **Select Modules**: Choose desired modules from the list
3. **Clone Selected**: Install chosen modules to your build

### 4. Building AzerothCore
1. **Configure Build Options**:
   - Enable/disable extractor generation
   - Set build configuration (Release recommended)
2. **Start Build Process**: Click "Build" to begin compilation
3. **Monitor Progress**: Watch real-time build status and logs
4. **Handle Errors**: Check console for detailed error information

### 5. Server Deployment
1. **Create Repack**: Generate server deployment package
2. **Setup Database**: Import world and character databases
3. **Configure Server**: Edit configuration files as needed
4. **Start Servers**: Launch Auth and World servers
5. **Monitor Logs**: Use console tab for server monitoring

## 🗂️ Directory Structure

```
ACB Installation/
├── ACB.exe                 # Main application executable
├── icons/                  # Application icons and resources
├── logs/                   # Session logs and error reports
├── config/                 # Configuration files and settings
├── GitSource/              # Cloned source repositories
│   ├── azerothcore-wotlk/  # Main AzerothCore source
│   └── modules/            # Additional modules
├── Build/                  # Compilation output and binaries
├── Repack/                 # Server deployment package
│   ├── authserver.exe      # Authentication server
│   ├── worldserver.exe     # World server
│   ├── configs/            # Server configuration files
│   └── data/               # Game data and databases
└── Data/                   # World database and assets
```

## ⚙️ Configuration

### Custom URLs
ACB supports custom repository URLs for:
- **AzerothCore Source**: Custom forks and modifications
- **Module Repositories**: Personal or organization modules
- **HeidiSQL Download**: Alternative download sources
- **Game Data**: Custom database and asset sources

### Build Options
- **Generator Selection**: Visual Studio 2022 (default)
- **Architecture**: x64 (64-bit) builds
- **Configuration**: Release (optimized) or Debug
- **Extractor Generation**: Tools for game asset extraction

## 🔧 Troubleshooting

### Common Issues

#### Build Failures
- **Missing Dependencies**: Ensure all requirements are installed
- **Path Issues**: Check for spaces in installation paths
- **Permissions**: Run ACB as Administrator
- **Disk Space**: Ensure sufficient free space (50GB+)

#### Git Issues
- **Authentication**: Configure Git credentials for private repos
- **Network**: Check firewall settings for Git operations
- **Submodules**: Some modules require recursive cloning

#### Compilation Errors
- **Visual Studio**: Verify VS2022 C++ workload is installed
- **Boost Libraries**: Ensure correct Boost version is detected
- **MySQL**: Verify MySQL development libraries are available

### Log Files
ACB generates detailed logs for troubleshooting:
- **Session Logs**: `logs/acb_session_YYYYMMDD_HHMMSS.log`
- **Build Logs**: Integrated in console output
- **Error Reports**: Detailed stack traces for failures

## 🤝 Contributing

### Reporting Issues
1. Check existing issues in the repository
2. Include ACB version and system information
3. Attach relevant log files
4. Provide step-by-step reproduction steps

### Feature Requests
1. Describe the proposed feature clearly
2. Explain the use case and benefits
3. Consider implementation complexity
4. Discuss with maintainers before large changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AzerothCore Team**: For the excellent server emulator
- **Module Developers**: Community contributors and module creators
- **Tool Authors**: Developers of build tools and dependencies
- **Community**: Users providing feedback and bug reports

## 📞 Support

- **Documentation**: Check this README and inline help
- **Issues**: Use GitHub Issues for bug reports
- **Community**: Join AzerothCore Discord for discussions
- **Logs**: Always include log files when seeking help

---

**Made with ❤️ for the AzerothCore Community**