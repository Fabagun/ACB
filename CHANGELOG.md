# Changelog

All notable changes to AzerothCore Builder (ACB) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project setup for GitHub
- Comprehensive README with installation and usage instructions
- GitHub Actions CI/CD pipeline
- Contributing guidelines
- MIT License
- Requirements.txt with all dependencies
- Setup.py for package installation
- .gitignore for Python and Windows development

## [1.0.0] - 2025-01-04

### Added
- Initial release of AzerothCore Builder
- GUI application for building AzerothCore servers
- Automated dependency detection and installation
- Support for Git, CMake, Visual Studio, MySQL, Boost, and OpenSSL
- Real-time progress tracking with green progress bars
- Comprehensive logging system
- Manual path override capabilities
- Modern Windows GUI with consistent styling
- Database management features
- Visual Studio integration
- One-click AzerothCore compilation

### Features
- **Dependency Management**: Automatic detection and installation of required tools
- **Path Management**: Smart path detection with manual override options
- **Progress Tracking**: Real-time progress bars and detailed console logging
- **Error Handling**: Comprehensive error reporting and recovery
- **Database Support**: Automated database creation and configuration
- **Visual Studio Integration**: Automatic detection of Visual Studio components
- **Modern UI**: Clean, responsive interface with consistent green styling

### Technical Details
- Built with Python 3.8+ and tkinter
- Windows-specific optimizations
- PIL/Pillow integration for image handling
- psutil for system monitoring
- Comprehensive error handling and logging
- Modular architecture for easy maintenance

### Dependencies
- Python 3.8 or higher
- Pillow (PIL) for image processing
- psutil for system monitoring
- Windows 10/11 (64-bit)
- Administrator privileges for full functionality

### Installation
- Direct Python execution: `python ACB.py`
- Package installation: `pip install -e .`
- Executable build support (via PyInstaller)

---

## Version History

### v1.0.0 (2025-01-04)
- Initial release
- Core functionality implemented
- All essential features working
- Ready for public use

---

## Future Releases

### Planned Features
- [ ] Executable distribution
- [ ] Advanced configuration options
- [ ] Plugin system
- [ ] Multi-language support
- [ ] Advanced logging options
- [ ] Backup and restore functionality
- [ ] Update checking system
- [ ] Theme customization

### Known Issues
- None currently documented

### Breaking Changes
- None in current version

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
