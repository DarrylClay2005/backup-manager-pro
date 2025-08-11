#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read the requirements
def get_requirements():
    """Get requirements from requirements.txt if it exists"""
    req_file = "requirements.txt"
    if os.path.exists(req_file):
        with open(req_file, "r") as f:
            lines = f.readlines()
            # Filter out comments and empty lines
            requirements = [line.strip() for line in lines 
                          if line.strip() and not line.strip().startswith('#')]
            return requirements
    return []

setup(
    name="backup-manager-pro",
    version="1.0.0",
    author="Desmond Clay",
    author_email="desmond@example.com",
    description="A comprehensive backup management system with modern GUI for Linux systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DarrylClay2005/backup-manager-pro",
    project_urls={
        "Bug Tracker": "https://github.com/DarrylClay2005/backup-manager-pro/issues",
        "Repository": "https://github.com/DarrylClay2005/backup-manager-pro",
        "Documentation": "https://github.com/DarrylClay2005/backup-manager-pro#readme",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Environment :: X11 Applications",
        "Topic :: Desktop Environment",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=get_requirements(),
    extras_require={
        "dev": ["build", "wheel", "twine"],
    },
    entry_points={
        "console_scripts": [
            "backup-manager-pro=backup_manager_gui:main",
        ],
        "gui_scripts": [
            "backup-manager-pro-gui=backup_manager_gui:main",
        ],
    },
    data_files=[
        ("share/applications", ["data/backup-manager-pro.desktop"]),
        ("share/backup-manager-pro", ["backup_manager_script.sh"]),
        ("share/doc/backup-manager-pro", ["README.md", "LICENSE"]),
    ],
    include_package_data=True,
    zip_safe=False,
    keywords="backup, system, timeshift, google-drive, gui, linux",
    platforms=["Linux"],
)
