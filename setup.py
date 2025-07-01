#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith('#')]

setup(
    name="ghostwire",
    version="1.0.0",
    author="Kaiamaterasu",
    author_email="",
    description="🔒 Encrypted P2P Communication Tool with Steganographic Capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Kaiamaterasu/ghostwire",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Communications :: Chat",
        "Topic :: Security :: Cryptography",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ghostwire=src.ghostwire_simple:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.png", "*.jpg"],
    },
    project_urls={
        "Bug Reports": "https://github.com/Kaiamaterasu/ghostwire/issues",
        "Source": "https://github.com/Kaiamaterasu/ghostwire",
        "Documentation": "https://github.com/Kaiamaterasu/ghostwire/blob/main/README.md",
    },
)
