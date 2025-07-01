#!/bin/bash

# 👻 Ghostwire Installation Script 🔒
# This script installs Ghostwire and all its dependencies

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Emojis
CHECKMARK="✅"
CROSS="❌"
ROCKET="🚀"
GHOST="👻"
LOCK="🔒"
GEAR="⚙️"

echo -e "${PURPLE}${GHOST} Welcome to Ghostwire Installation ${LOCK}${NC}"
echo -e "${CYAN}===============================================${NC}"

# Function to print colored output
print_status() {
    echo -e "${GREEN}${CHECKMARK} $1${NC}"
}

print_error() {
    echo -e "${RED}${CROSS} $1${NC}"
}

print_info() {
    echo -e "${BLUE}${GEAR} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Check Python version
print_info "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP 'Python \K[0-9]+\.[0-9]+')
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)"; then
    print_status "Python $python_version found"
else
    print_error "Python 3.7+ is required. Found: $python_version"
    exit 1
fi

# Check if pip is installed
print_info "Checking pip..."
if command -v pip3 &> /dev/null; then
    print_status "pip3 found"
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    print_status "pip found"
    PIP_CMD="pip"
else
    print_error "pip not found. Please install pip first."
    exit 1
fi

# Check if we're in the right directory
if [[ ! -f "ghostwire" ]] || [[ ! -f "setup.py" ]]; then
    print_error "Please run this script from the ghostwire project directory"
    exit 1
fi

# Check if system uses externally managed Python
print_info "Checking Python environment..."
if python3 -c "import sys; print(sys.prefix)" 2>/dev/null | grep -q "/usr"; then
    print_warning "Detected externally managed Python environment"
    USE_VENV=true
else
    USE_VENV=false
fi

# Create virtual environment if needed
if $USE_VENV; then
    print_info "Creating virtual environment..."
    if python3 -m venv ghostwire_env; then
        print_status "Virtual environment created"
        source ghostwire_env/bin/activate
        PIP_CMD="ghostwire_env/bin/pip"
        PYTHON_CMD="ghostwire_env/bin/python"
        print_status "Virtual environment activated"
    else
        print_error "Failed to create virtual environment"
        exit 1
    fi
else
    PYTHON_CMD="python3"
fi

# Install dependencies
print_info "Installing Python dependencies..."
if $PIP_CMD install -r requirements.txt; then
    print_status "Dependencies installed successfully"
else
    print_error "Failed to install dependencies"
    exit 1
fi

# Try to install the package in development mode
print_info "Installing Ghostwire..."
if $PIP_CMD install -e . 2>/dev/null; then
    print_status "Ghostwire installed successfully via pip"
    INSTALLATION_TYPE="pip"
else
    print_warning "pip install failed, using alternative installation..."
    
    # Make ghostwire executable
    chmod +x ghostwire
    print_status "Made ghostwire executable"
    INSTALLATION_TYPE="manual"
    
    # Update shebang to use virtual environment python if needed
    if $USE_VENV; then
        print_info "Updating ghostwire to use virtual environment..."
        sed -i "1s|.*|#!$(pwd)/ghostwire_env/bin/python3|" ghostwire
        print_status "Updated ghostwire shebang"
    fi
fi

# Test installation
print_info "Testing installation..."
if ./ghostwire --help-all &> /dev/null; then
    print_status "Installation test passed"
else
    print_error "Installation test failed"
    exit 1
fi

# Create example images for testing steganography
print_info "Creating test images for steganography..."
if command -v convert &> /dev/null; then
    convert -size 500x500 xc:lightblue test_example.png 2>/dev/null || true
    convert -size 200x200 gradient:blue-red small_example.png 2>/dev/null || true
    print_status "Test images created"
else
    print_warning "ImageMagick not found. Test images not created."
    print_info "You can install ImageMagick with: sudo apt-get install imagemagick"
fi

# Final success message
echo ""
echo -e "${GREEN}${ROCKET} Installation Complete! ${ROCKET}${NC}"
echo -e "${CYAN}===============================================${NC}"

# Show virtual environment info if used
if $USE_VENV; then
    echo -e "${YELLOW}🐍 Virtual Environment Info:${NC}"
    echo -e "${BLUE}Virtual environment created at: ${CYAN}$(pwd)/ghostwire_env${NC}"
    echo -e "${BLUE}To activate manually: ${CYAN}source ghostwire_env/bin/activate${NC}"
    echo -e "${BLUE}To deactivate: ${CYAN}deactivate${NC}"
    echo ""
fi

echo -e "${YELLOW}Quick Start Commands:${NC}"
echo ""
echo -e "${BLUE}# Start a secure chat room${NC}"
echo -e "${CYAN}./ghostwire --enable --key1 k1 --key2 k2 --key3 k3 --alias \"my-room\"${NC}"
echo ""
echo -e "${BLUE}# Send a message${NC}"
echo -e "${CYAN}./ghostwire --send \"Hello World!\" --user \"myname\" --all${NC}"
echo ""
echo -e "${BLUE}# Hide a message in an image${NC}"
echo -e "${CYAN}./ghostwire --stealth-image test_example.png --message \"Secret!\" --output hidden.png${NC}"
echo ""
echo -e "${BLUE}# Extract hidden message${NC}"
echo -e "${CYAN}./ghostwire --stealth-extract hidden.png${NC}"
echo ""
echo -e "${BLUE}# Show all help${NC}"
echo -e "${CYAN}./ghostwire --help-all${NC}"
echo ""
echo -e "${GREEN}📚 Documentation:${NC}"
echo -e "${BLUE}- README.md - Main documentation${NC}"
echo -e "${BLUE}- STEGANOGRAPHY_GUIDE.md - Detailed steganography guide${NC}"
echo -e "${BLUE}- Practical_Guide.md - Practical usage scenarios${NC}"
echo ""
echo -e "${PURPLE}Happy secure communicating! ${GHOST}${LOCK}${NC}"
