# Contributing to AzerothCore Builder (ACB)

Thank you for your interest in contributing to ACB! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

Before creating an issue, please:
1. Check if the issue already exists
2. Search the closed issues as well
3. Provide detailed information about your environment and the problem

When creating an issue, please include:
- Windows version
- Python version
- ACB version
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Console output/logs

### Suggesting Features

We welcome feature suggestions! Please:
1. Check if the feature has been requested before
2. Provide a clear description of the feature
3. Explain why it would be useful
4. Consider implementation complexity

### Code Contributions

#### Getting Started

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/yourusername/azerothcore-builder.git
   cd azerothcore-builder
   ```
3. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### Development Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install pytest black flake8
   ```

2. **Run the application**:
   ```bash
   python ACB.py
   ```

#### Coding Standards

- **Python Style**: Follow PEP 8 guidelines
- **Code Formatting**: Use Black for automatic formatting
- **Linting**: Use flake8 for code quality checks
- **Documentation**: Add docstrings for new functions and classes
- **Comments**: Explain complex logic and business rules

#### Testing

Before submitting a pull request:
1. **Run tests**:
   ```bash
   pytest
   ```
2. **Check formatting**:
   ```bash
   black --check .
   ```
3. **Run linting**:
   ```bash
   flake8 .
   ```
4. **Test the GUI**: Manually test your changes in the application

#### Commit Guidelines

- Use clear, descriptive commit messages
- Keep commits focused on a single change
- Use conventional commit format when possible:
  - `feat:` for new features
  - `fix:` for bug fixes
  - `docs:` for documentation changes
  - `style:` for formatting changes
  - `refactor:` for code refactoring
  - `test:` for test additions/changes

#### Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Update CHANGELOG.md** with your changes
4. **Ensure all checks pass**
5. **Request review** from maintainers

### Pull Request Template

When creating a pull request, please include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Manual testing completed
- [ ] No new warnings or errors

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

## 🏗️ Development Guidelines

### Architecture

ACB follows a modular design:
- **Main Application**: `ACB.py` contains the main `AzerothCoreBuilder` class
- **GUI Components**: Organized in methods within the main class
- **Dependency Management**: Centralized in the `requirements` dictionary
- **Path Management**: Handled through dedicated methods

### Key Components

1. **Dependency Detection**: Automatic detection of required tools
2. **Path Management**: Smart path detection with manual override
3. **Progress Tracking**: Real-time progress updates
4. **Error Handling**: Comprehensive error reporting and recovery

### UI Guidelines

- **Consistent Styling**: Use green progress bars and unified icon design
- **Comprehensive Logging**: All actions should be logged to console
- **User Feedback**: Provide clear feedback for all operations
- **Error Messages**: Use clear, actionable error messages

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment Information**:
   - Windows version (e.g., Windows 10 21H2)
   - Python version
   - ACB version

2. **Reproduction Steps**:
   - Step-by-step instructions
   - Expected behavior
   - Actual behavior

3. **Additional Information**:
   - Screenshots or screen recordings
   - Console output/logs
   - System specifications

## 📝 Documentation

- **Code Comments**: Explain complex logic
- **Docstrings**: Use Google-style docstrings
- **README Updates**: Update README.md for significant changes
- **CHANGELOG**: Document all changes in CHANGELOG.md

## 🚀 Release Process

1. **Version Bumping**: Update version in `setup.py`
2. **CHANGELOG**: Update with new features and fixes
3. **Testing**: Ensure all tests pass
4. **Documentation**: Update documentation if needed
5. **Release Notes**: Create comprehensive release notes

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Code Review**: All PRs require review before merging

## 🙏 Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to ACB! 🎉
