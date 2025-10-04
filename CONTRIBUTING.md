# Contributing to AzerothCore Builder (ACB)

Thank you for your interest in contributing to AzerothCore Builder! This document provides guidelines and information for contributors.

## 🤝 Ways to Contribute

### 🐛 Bug Reports
- Search existing issues before creating new ones
- Use the bug report template
- Provide detailed reproduction steps
- Include system information and log files
- Test with the latest version before reporting

### 💡 Feature Requests
- Check if the feature already exists or is planned
- Use the feature request template
- Describe the use case and benefits
- Consider implementation complexity
- Discuss with maintainers for large features

### 📝 Documentation Improvements
- Fix typos and grammatical errors
- Improve clarity and completeness
- Add missing information
- Update outdated content
- Translate documentation (if applicable)

### 🔧 Code Contributions
- Bug fixes and improvements
- New features and enhancements
- Performance optimizations
- Code refactoring and cleanup
- Test coverage improvements

## 🚀 Getting Started

### Prerequisites
1. **Git**: For version control
2. **Python 3.8+**: Programming language
3. **Windows 10/11**: Target platform for testing
4. **IDE**: Visual Studio Code (recommended) or PyCharm

### Development Setup

#### 1. Fork and Clone
```bash
# Fork the repository on GitHub first
git clone https://github.com/your-username/azerothcore-builder.git
cd azerothcore-builder

# Add upstream remote
git remote add upstream https://github.com/original-org/azerothcore-builder.git
```

#### 2. Set Up Environment
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Linux/macOS

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .
```

#### 3. Verify Setup
```bash
# Run the application
python ACB.py

# Run tests
pytest

# Check code style
flake8 ACB.py
black --check ACB.py
```

## 📋 Development Guidelines

### Code Style

#### Python Style Guide
- Follow [PEP 8](https://pep8.org/) standards
- Use [Black](https://black.readthedocs.io/) formatter (line length: 88)
- Use [isort](https://isort.readthedocs.io/) for import organization
- Add type hints where appropriate
- Write docstrings for all public functions and classes

#### Code Formatting
```bash
# Format code
black ACB.py

# Sort imports
isort ACB.py

# Check style
flake8 ACB.py
pylint ACB.py
```

#### Naming Conventions
```python
# Classes: PascalCase
class AzerothCoreBuilder:
    pass

# Functions and variables: snake_case
def create_requirement_row(self):
    pass

# Constants: UPPER_SNAKE_CASE
DEFAULT_TIMEOUT = 30

# Private methods: _snake_case
def _load_config(self):
    pass
```

### Documentation Standards

#### Docstring Format
```python
def method_name(self, param1: str, param2: int) -> bool:
    """
    Brief description of the method's purpose.
    
    Longer description if needed, explaining the method's behavior,
    side effects, and any important implementation details.
    
    Args:
        param1: Description of the first parameter
        param2: Description of the second parameter
        
    Returns:
        Description of the return value and its type
        
    Raises:
        ValueError: Description of when this exception is raised
        ConnectionError: Description of another possible exception
        
    Example:
        >>> builder = AzerothCoreBuilder(root)
        >>> result = builder.method_name("test", 42)
        >>> print(result)
        True
    """
    pass
```

#### Code Comments
```python
# Good: Explain the "why", not the "what"
# Retry connection up to 3 times to handle network instability
for attempt in range(3):
    try:
        result = connect_to_server()
        break
    except ConnectionError:
        if attempt == 2:
            raise
        time.sleep(1)

# Avoid: Obvious comments
count = 0  # Initialize counter (unnecessary)
```

### Testing Guidelines

#### Writing Tests
```python
import unittest
from unittest.mock import Mock, patch, MagicMock
from ACB import AzerothCoreBuilder

class TestAzerothCoreBuilder(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_root = Mock()
        self.acb = AzerothCoreBuilder(self.mock_root)
    
    def tearDown(self):
        """Clean up after each test method."""
        # Clean up any created files or connections
        pass
    
    def test_dependency_detection(self):
        """Test that dependency detection works correctly."""
        # Test implementation
        pass
        
    @patch('subprocess.run')
    def test_git_clone_operation(self, mock_subprocess):
        """Test Git clone operations with mocked subprocess."""
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "Cloning completed"
        
        result = self.acb.clone_source("azerothcore")
        
        mock_subprocess.assert_called_once()
        self.assertTrue(result)
```

#### Test Coverage
- Aim for >80% test coverage
- Test both success and failure scenarios
- Mock external dependencies (Git, network calls, file system)
- Test GUI components where possible
- Include integration tests for key workflows

#### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ACB --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_requirements.py

# Run with verbose output
pytest -v

# Run tests and open coverage report
pytest --cov=ACB --cov-report=html && start htmlcov/index.html
```

## 🔄 Development Workflow

### Git Workflow

#### Branch Strategy
```bash
# Feature development
git checkout -b feature/new-module-system
git checkout -b fix/git-clone-timeout
git checkout -b docs/improve-installation-guide

# Hotfixes
git checkout -b hotfix/critical-security-issue
```

#### Commit Message Format
```
type(scope): brief description

Detailed explanation of the change, including:
- Why the change was necessary
- What was changed
- Any breaking changes or migration notes

- Use bullet points for multiple changes
- Reference issues with "Fixes #123" or "Closes #456"
- Include co-authors if applicable

Co-authored-by: Name <email@example.com>
Fixes #123
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
**Scopes**: `ui`, `build`, `git`, `modules`, `deps`, `config`

#### Example Commits
```bash
feat(modules): add community module browser with search functionality

- Implement GitHub API integration for fetching community modules
- Add search and filtering capabilities to module selection window
- Include module descriptions and compatibility information
- Cache module data to reduce API calls

Fixes #45
Closes #67

fix(git): handle authentication timeout during large repository clones

- Increase default timeout for Git operations from 30s to 300s
- Add retry logic for network-related clone failures
- Improve error messages for authentication issues
- Log detailed Git output for debugging

Fixes #123

docs(installation): clarify Visual Studio workload requirements

- Add specific workload names and components needed
- Include screenshots of VS installer selections
- Update troubleshooting section with common VS issues
- Add alternative installation methods
```

### Pull Request Process

#### Before Submitting
1. **Update your fork**:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   git push origin main
   ```

2. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make changes and test**:
   ```bash
   # Make your changes
   # Run tests
   pytest
   # Check code style
   black ACB.py
   flake8 ACB.py
   # Update documentation if needed
   ```

4. **Commit and push**:
   ```bash
   git add .
   git commit -m "feat(scope): description"
   git push origin feature/your-feature-name
   ```

#### Pull Request Template
When creating a PR, include:

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)  
- [ ] Breaking change (fix or feature that causes existing functionality to change)
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Performance improvement

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed
- [ ] No breaking changes to existing functionality

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No conflicts with main branch
- [ ] Commit messages follow convention

## Screenshots (if applicable)
Include screenshots of UI changes or new features.

## Related Issues
Fixes #(issue number)
```

#### Review Process
1. **Automated Checks**: CI/CD pipeline runs tests and style checks
2. **Maintainer Review**: Core maintainers review code and functionality
3. **Community Feedback**: Other contributors may provide input
4. **Approval**: At least one maintainer approval required
5. **Merge**: Squash and merge or rebase depending on change size

## 🧪 Testing

### Test Categories

#### Unit Tests
- Test individual functions and methods
- Mock external dependencies
- Fast execution (<1s per test)
- High coverage of core logic

#### Integration Tests
- Test component interactions
- Use real dependencies where safe
- Test complete workflows
- Verify GUI functionality

#### System Tests
- Test full application scenarios
- Use real build tools when possible
- Test on clean Windows systems
- Verify installer and packaging

### Test Environment

#### Local Testing
```bash
# Set up test environment
python -m venv test_env
test_env\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run test suite
pytest tests/ -v
pytest --cov=ACB --cov-report=html

# Test specific functionality
pytest tests/test_git_operations.py::TestGitClone::test_clone_success
```

#### CI/CD Testing
- GitHub Actions runs tests on Windows Server
- Tests run on multiple Python versions (3.8, 3.9, 3.10, 3.11)
- Code coverage reporting via Codecov
- Style checking with Black and Flake8

## 📊 Performance Guidelines

### Code Performance
- Avoid blocking the GUI thread
- Use threading for long-running operations
- Implement progress callbacks for user feedback
- Cache expensive operations where appropriate
- Use generators for large data sets

### Memory Management
- Close file handles and subprocess objects
- Avoid circular references
- Use context managers (`with` statements)
- Monitor memory usage during development
- Clean up temporary files and directories

### Example: Non-blocking Operation
```python
import threading
import tkinter as tk

def long_running_task(callback):
    """Example of a long-running task that doesn't block the GUI."""
    def worker():
        try:
            # Simulate long operation
            for i in range(100):
                time.sleep(0.1)  # Simulate work
                # Update progress on main thread
                root.after(0, lambda p=i: callback(f"Progress: {p}%"))
            
            # Completion callback
            root.after(0, lambda: callback("Completed!"))
            
        except Exception as e:
            # Error callback
            root.after(0, lambda: callback(f"Error: {e}"))
    
    # Start worker thread
    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()

# Usage in GUI
def start_operation():
    progress_label.config(text="Starting...")
    long_running_task(lambda msg: progress_label.config(text=msg))
```

## 🔒 Security Considerations

### Input Validation
```python
import os
import re
from pathlib import Path

def validate_git_url(url: str) -> bool:
    """Validate Git repository URL to prevent injection attacks."""
    if not url:
        return False
    
    # Allow only HTTPS and SSH Git URLs
    pattern = r'^(https://github\.com/|git@github\.com:)[\w\-\.]+/[\w\-\.]+\.git$'
    return bool(re.match(pattern, url))

def validate_file_path(path: str) -> bool:
    """Validate file path to prevent directory traversal."""
    try:
        # Resolve path and check if it's within allowed directories
        resolved = Path(path).resolve()
        allowed_base = Path.cwd().resolve()
        return allowed_base in resolved.parents or resolved == allowed_base
    except (OSError, ValueError):
        return False
```

### Subprocess Security
```python
import subprocess
import shlex

def safe_subprocess_call(command: list, cwd: str = None, timeout: int = 30):
    """Safely execute subprocess with proper argument handling."""
    try:
        # Use list form to prevent shell injection
        result = subprocess.run(
            command,  # Already a list, no shell=True
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False  # Handle return codes manually
        )
        return result
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"Command timed out after {timeout} seconds")
    except Exception as e:
        raise RuntimeError(f"Subprocess failed: {e}")

# Good: Safe subprocess call
result = safe_subprocess_call(["git", "clone", validated_url, target_dir])

# Avoid: Shell injection risk
# result = subprocess.run(f"git clone {url} {target}", shell=True)  # Dangerous!
```

## 🎯 Code Review Checklist

### For Authors
- [ ] Code follows style guidelines (Black, PEP 8)
- [ ] All tests pass locally
- [ ] New functionality includes tests
- [ ] Documentation updated for new features
- [ ] No sensitive information in code or commits
- [ ] Error handling implemented appropriately
- [ ] Performance impact considered
- [ ] Backward compatibility maintained (or breaking changes documented)

### For Reviewers
- [ ] Code solves the stated problem
- [ ] Implementation is clear and maintainable
- [ ] Edge cases are handled
- [ ] Tests adequately cover new functionality
- [ ] Documentation is accurate and complete
- [ ] Security implications considered
- [ ] Performance impact is acceptable
- [ ] Code follows project conventions

## 📞 Getting Help

### Communication Channels
- **GitHub Issues**: Technical discussions and bug reports
- **GitHub Discussions**: General questions and feature discussions
- **Pull Request Comments**: Code-specific discussions
- **AzerothCore Discord**: Community chat and support

### Asking Questions
When asking for help:

1. **Search first**: Check existing issues and discussions
2. **Be specific**: Describe the problem clearly
3. **Provide context**: Include relevant code, errors, and system info
4. **Show effort**: Explain what you've already tried
5. **Be patient**: Maintainers are volunteers with other commitments

### Example Good Question
```markdown
## Issue: Git clone fails with authentication error

**Environment:**
- ACB version: 1.2.0
- Windows: 11 Pro 22H2
- Git version: 2.44.0

**Problem:**
When trying to clone a private repository using the custom URL feature, 
I get an authentication error even though I can clone the same repository 
manually using Git Bash.

**Steps to reproduce:**
1. Enter custom repository URL: https://github.com/myorg/private-repo.git
2. Click "Clone" button
3. Error appears: "Authentication failed"

**What I've tried:**
- Verified Git credentials work in Git Bash
- Checked that URL is correct
- Restarted ACB as administrator

**Expected behavior:**
Repository should clone successfully using existing Git credentials.

**Logs:**
[Attach relevant log file from logs/ directory]
```

## 🎉 Recognition

### Contributors
All contributors are recognized in:
- GitHub contributor list
- CHANGELOG.md acknowledgments  
- Documentation credits
- Special recognition for significant contributions

### Types of Recognition
- **First-time contributors**: Welcome message and guidance
- **Regular contributors**: Contributor badge and privileges
- **Core contributors**: Maintainer status consideration
- **Special contributions**: Feature in project announcements

Thank you for contributing to AzerothCore Builder! Your efforts help make AzerothCore more accessible to the community. 🚀