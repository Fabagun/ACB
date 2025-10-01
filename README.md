# AzerothCore Windows AutoBuilder v2.0

## Enhanced PowerShell Automation Script

A comprehensive, modern PowerShell script for automating the entire AzerothCore server setup and build process on Windows with enterprise-grade features.

## 🚀 What's New in v2.0

### Major Improvements
- **Modern Architecture**: Modular design with separate modules for different functionalities
- **Enhanced Security**: Secure credential management, input validation, and file integrity verification
- **Comprehensive Logging**: Structured logging with multiple levels, file rotation, and detailed error tracking
- **Configuration Management**: JSON-based configuration system with validation and schema support
- **Dependency Management**: Automated version checking and installation with minimum requirements enforcement
- **Error Handling**: Robust error handling with rollback capabilities and detailed error reporting
- **User Experience**: Modern GUI for module selection, progress indicators, and better user feedback

### Updated Requirements
- **Windows ≥ 10** (previously supported older versions)
- **Boost ≥ 1.78** (updated from 1.74)
- **MySQL ≥ 8.0** (updated from 5.7, recommended 8.4)
- **OpenSSL ≥ 3.x.x** (updated from 1.1.1)
- **CMake ≥ 3.27** (updated from 3.16)
- **MS Visual Studio (Community) ≥ 17 (2022)** (updated from 2019)

## 📋 Features

### Core Functionality
1. **Dependency Installation**: Automated installation of all required software with version validation
2. **Repository Management**: Clone, update, and clean AzerothCore repositories
3. **Pull Request Testing**: Easy testing of GitHub pull requests
4. **Module Management**: Modern GUI for selecting and managing custom modules
5. **Server Building**: Automated compilation with CMake and Visual Studio
6. **Database Setup**: MySQL initialization and SQL script execution
7. **Server Deployment**: Create personal servers or repacks

### Advanced Features
- **Configuration System**: JSON-based configuration with validation
- **Logging System**: Comprehensive logging with file rotation
- **Security Features**: Secure password handling and file integrity verification
- **Error Recovery**: Robust error handling with detailed diagnostics
- **System Information**: Built-in system diagnostics and dependency status
- **Dry Run Mode**: Preview operations without executing them
- **Parallel Processing**: Optimized build processes with parallel job support

## 🛠️ Installation

### Prerequisites
- Windows 10 or later
- PowerShell 5.1 or later
- Administrator privileges (for dependency installation)
- Internet connection (for downloads)

### Setup
1. **Download the script files**:
   ```
   Start-AzerothCoreAutoBuilder.ps1
   AzerothCore-Config.json
   Modules/
   ├── Logging.psm1
   ├── Security.psm1
   ├── Configuration.psm1
   └── DependencyManager.psm1
   ```

2. **Set execution policy** (run as Administrator):
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Run the script**:
   ```powershell
   .\Start-AzerothCoreAutoBuilder.ps1
   ```

## ⚙️ Configuration

### Configuration File
The script uses `AzerothCore-Config.json` for all settings:

```json
{
  "version": "2.0.0",
  "paths": {
    "downloadFolder": "C:\\WowServer\\ACdownloads\\",
    "baseLocation": "C:\\WowServer\\SourceGit\\",
    "buildFolder": "C:\\WowServer\\Compile\\",
    "personalServerFolder": "C:\\WowServer\\Server\\"
  },
  "database": {
    "rootPassword": "",
    "port": 3306
  },
  "downloads": {
    "downloadData": true,
    "dataUrl": "https://github.com/wowgaming/client-data/releases/download/v12/data.zip"
  },
  "build": {
    "configuration": "Release",
    "parallelJobs": 4
  },
  "logging": {
    "level": "Info",
    "logFile": "C:\\WowServer\\Logs\\AzerothCore-Builder.log",
    "maxLogSize": 10
  }
}
```

### Command Line Options
```powershell
# Basic usage
.\Start-AzerothCoreAutoBuilder.ps1

# Custom configuration
.\Start-AzerothCoreAutoBuilder.ps1 -ConfigPath "C:\MyConfig.json"

# Debug logging
.\Start-AzerothCoreAutoBuilder.ps1 -LogLevel Debug

# Skip dependency installation
.\Start-AzerothCoreAutoBuilder.ps1 -SkipDependencies

# Dry run mode (preview only)
.\Start-AzerothCoreAutoBuilder.ps1 -DryRun
```

## 🎯 Usage Guide

### Quick Start
1. **Run the script** as Administrator
2. **Choose option 1** to install dependencies (first time only)
3. **Choose option 2** to clone/update AzerothCore repository
4. **Choose option 4** to select custom modules (optional)
5. **Choose option 5** to build the server
6. **Choose option 7** to create your personal server

### Testing Pull Requests
1. **Choose option 2** to ensure clean repository
2. **Choose option 3** and enter the PR number
3. **Choose option 5** to build with PR changes
4. **Choose option 6** to start test server

### Module Management
- **Option 4** opens a modern GUI for module selection
- Modules are automatically downloaded and configured
- SQL scripts are automatically applied to appropriate databases

## 🔧 Advanced Features

### Logging System
- **Multiple Levels**: Debug, Info, Warning, Error
- **File Rotation**: Automatic log rotation when files get too large
- **Structured Logging**: Timestamps, caller information, and exception details
- **Console Output**: Color-coded console output for better readability

### Security Features
- **Secure Password Handling**: Uses PowerShell SecureString for sensitive data
- **Input Validation**: Validates all user inputs and file paths
- **File Integrity**: SHA256 checksums for downloaded files
- **Secure Downloads**: BITS transfer with resume capability

### Error Handling
- **Comprehensive Try-Catch**: All operations wrapped in error handling
- **Detailed Error Messages**: Clear error descriptions with context
- **Rollback Capabilities**: Automatic cleanup on failed operations
- **Recovery Options**: Resume functionality for interrupted operations

### Performance Optimizations
- **Parallel Downloads**: Multiple files downloaded simultaneously
- **Parallel Builds**: CMake builds with configurable parallel jobs
- **Intelligent Caching**: Avoids re-downloading existing files
- **Progress Indicators**: Real-time progress feedback for long operations

## 📊 System Requirements

### Minimum Requirements
- **OS**: Windows 10 (build 1903 or later)
- **RAM**: 8 GB (16 GB recommended)
- **Storage**: 50 GB free space
- **CPU**: 4 cores (8 cores recommended)
- **Network**: Stable internet connection

### Software Dependencies
| Software | Minimum Version | Recommended Version |
|----------|----------------|-------------------|
| Windows | 10 | 11 |
| PowerShell | 5.1 | 7.x |
| Git | 2.45.0 | Latest |
| CMake | 3.27.0 | 3.28+ |
| Visual Studio | 17.0.0 (2022) | Latest |
| MySQL | 8.0.0 | 8.4.0 |
| OpenSSL | 3.0.0 | 3.3.x |
| Boost | 1.78.0 | 1.84.0 |

## 🐛 Troubleshooting

### Common Issues

#### "Access Denied" Errors
- Ensure you're running PowerShell as Administrator
- Check that antivirus software isn't blocking the script
- Verify file permissions on target directories

#### Download Failures
- Check internet connection
- Verify firewall settings
- Try running with `-SkipDependencies` if only some downloads fail

#### Build Failures
- Ensure all dependencies are installed and up to date
- Check available disk space (builds require significant space)
- Verify Visual Studio is properly installed with C++ workload

#### Database Issues
- Ensure MySQL is properly installed
- Check that no other MySQL instances are running
- Verify database credentials and permissions

### Log Analysis
- Check the log file for detailed error information
- Use `-LogLevel Debug` for more verbose output
- Look for specific error codes and exception details

### Getting Help
1. Check the log file for detailed error information
2. Run with `-LogLevel Debug` for verbose output
3. Use `-DryRun` to preview operations without executing
4. Check system information with option 9 in the main menu

## 🔄 Migration from v1.x

### Configuration Migration
The new configuration system is not backward compatible. You'll need to:
1. Run the script to create a new configuration file
2. Manually migrate any custom settings
3. Update paths if you've changed default locations

### File Structure Changes
- Script is now modular with separate `.psm1` files
- Configuration is now in JSON format
- Logs are now in a dedicated directory

## 📝 Changelog

### v2.0.0 (Current)
- Complete rewrite with modern architecture
- Enhanced security and error handling
- Comprehensive logging system
- JSON-based configuration
- Updated dependency requirements
- Modern GUI for module management
- Performance optimizations
- Better user experience

### v1.x (Legacy)
- Basic automation functionality
- Hardcoded configuration
- Limited error handling
- Basic logging
- Older dependency versions

## 🤝 Contributing

### Development Setup
1. Clone the repository
2. Install PowerShell 7.x for development
3. Use VS Code with PowerShell extension
4. Follow PowerShell best practices

### Code Standards
- Use PowerShell 5.1+ compatible syntax
- Follow PSScriptAnalyzer rules
- Include comprehensive error handling
- Add detailed comments and documentation
- Write unit tests for new functions

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- AzerothCore team for the excellent server core
- PowerShell community for best practices and modules
- Contributors who provided feedback and suggestions

## 📞 Support

For issues, questions, or contributions:
- Check the troubleshooting section first
- Review log files for detailed error information
- Use the built-in system diagnostics (option 9)
- Consider running with debug logging enabled

---

**Note**: This script is designed for educational and development purposes. Ensure you comply with all applicable terms of service and licensing requirements for the software and content you're working with.