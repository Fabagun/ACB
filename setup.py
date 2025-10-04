#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AzerothCore Builder (ACB) - Setup Script

This setup script allows ACB to be installed as a Python package.
"""

import os
import sys
from pathlib import Path
from setuptools import setup, find_packages

# Ensure Python version compatibility
if sys.version_info < (3, 8):
    sys.exit("AzerothCore Builder requires Python 3.8 or later")

# Get the long description from the README file
HERE = Path(__file__).parent.resolve()
LONG_DESCRIPTION = (HERE / "README.md").read_text(encoding="utf-8")

# Get version from ACB.py without importing it
def get_version():
    """Extract version from ACB.py without importing the module."""
    version_file = HERE / "ACB.py"
    if version_file.exists():
        # Look for version in ACB.py (you might need to add a __version__ variable)
        return "1.2.0"  # Default version
    return "1.0.0"

# Read requirements
def read_requirements(filename):
    """Read requirements from a file."""
    req_file = HERE / filename
    if req_file.exists():
        with open(req_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f 
                   if line.strip() and not line.startswith('#')]
    return []

# Package data (include icons and other assets)
def find_package_data():
    """Find all package data files."""
    data_files = []
    for root, dirs, files in os.walk("icons"):
        for file in files:
            data_files.append(os.path.join(root, file))
    return data_files

setup(
    # Basic package information
    name="azerothcore-builder",
    version=get_version(),
    author="F@bagun",
    author_email="",  # Add email if desired
    description="A GUI tool for building AzerothCore World of Warcraft server from source",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/azerothcore-builder",
    project_urls={
        "Bug Reports": "https://github.com/your-org/azerothcore-builder/issues",
        "Source": "https://github.com/your-org/azerothcore-builder",
        "Documentation": "https://github.com/your-org/azerothcore-builder#readme",
    },

    # Package classification
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators", 
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Installation/Setup",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Microsoft :: Windows",
        "Environment :: Win32 (MS Windows)",
        "Natural Language :: English",
    ],

    # Package requirements
    python_requires=">=3.8",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": read_requirements("requirements-dev.txt"),
        "docs": [
            "sphinx>=5.3.0",
            "sphinx-rtd-theme>=1.1.0",
            "myst-parser>=0.18.0",
        ],
        "build": [
            "pyinstaller>=5.7.0",
            "auto-py-to-exe>=2.25.0",
        ],
    },

    # Package structure
    packages=find_packages(exclude=["tests", "tests.*"]),
    py_modules=["ACB"],
    package_data={
        "": ["*.md", "*.txt", "*.ico", "*.png"],
        "icons": ["*.ico", "*.png"],
    },
    include_package_data=True,
    data_files=[
        ("", ["README.md", "LICENSE", "CHANGELOG.md"]),
        ("docs", [
            "API_DOCUMENTATION.md",
            "USER_GUIDE.md", 
            "DEVELOPER_GUIDE.md",
            "INSTALLATION_GUIDE.md",
            "DOCUMENTATION_INDEX.md",
        ]),
        ("icons", find_package_data()),
    ],

    # Entry points for command line usage
    entry_points={
        "console_scripts": [
            "acb=ACB:main",
            "azerothcore-builder=ACB:main",
        ],
        "gui_scripts": [
            "acb-gui=ACB:main",
        ],
    },

    # Additional metadata
    keywords="azerothcore wow world-of-warcraft server builder gui cmake msbuild",
    zip_safe=False,  # Required for PyInstaller compatibility

    # Custom commands can be added here
    cmdclass={},

    # Platform-specific options
    options={
        "bdist_wheel": {
            "plat_name": "win_amd64",  # Windows 64-bit only
        },
        "build_exe": {
            "packages": ["tkinter", "PIL", "psutil"],
            "include_files": [
                ("icons/", "icons/"),
                ("README.md", "README.md"),
                ("LICENSE", "LICENSE"),
            ],
        },
    },
)

# Additional setup for development environment
if __name__ == "__main__":
    # Check if we're in development mode
    if "develop" in sys.argv or "install" in sys.argv:
        print("\n" + "="*60)
        print("AzerothCore Builder Setup Complete!")
        print("="*60)
        print("\nNext steps:")
        print("1. Run 'acb' or 'python ACB.py' to start the application")
        print("2. Check the documentation in the docs/ folder")
        print("3. Report issues at: https://github.com/your-org/azerothcore-builder/issues")
        print("\nFor development:")
        print("- Install dev requirements: pip install -r requirements-dev.txt")
        print("- Run tests: pytest")
        print("- Format code: black ACB.py")
        print("- Check style: flake8 ACB.py")
        print("="*60)