#!/bin/bash

# 🚀 GitHub Readiness Verification Script
# This script verifies that Ghostwire is ready for GitHub upload

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 GitHub Readiness Verification${NC}"
echo "=================================="

# Check required files
echo -e "${YELLOW}📋 Checking required files...${NC}"
required_files=(
    "README.md"
    "LICENSE"
    "setup.py"
    "requirements.txt"
    ".gitignore"
    "install.sh"
    "ghostwire"
    "src/__init__.py"
    "STEGANOGRAPHY_GUIDE.md"
    "Practical_Guide.md"
)

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file${NC}"
        exit 1
    fi
done

# Check source files
echo -e "\n${YELLOW}🐍 Checking source files...${NC}"
src_files=(
    "src/ghostwire_simple.py"
    "src/ghostwire_steganography.py"
    "src/ghostwire.py"
    "src/ghostwire2.py"
    "src/ghostwire_chat.py"
    "src/ghostwire_broadcast.py"
)

for file in "${src_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file${NC}"
        exit 1
    fi
done

# Test basic functionality
echo -e "\n${YELLOW}🧪 Testing basic functionality...${NC}"
if ./ghostwire --help-all &> /dev/null; then
    echo -e "${GREEN}✅ Basic help works${NC}"
else
    echo -e "${RED}❌ Basic help failed${NC}"
    exit 1
fi

# Test steganography with temporary image
echo -e "\n${YELLOW}🖼️ Testing steganography...${NC}"
python3 -c "from PIL import Image; img = Image.new('RGB', (200, 200), 'lightblue'); img.save('temp_test.png')"

if ./ghostwire --stealth-image temp_test.png --message "Test" --output temp_hidden.png &> /dev/null; then
    echo -e "${GREEN}✅ Steganography hide works${NC}"
else
    echo -e "${RED}❌ Steganography hide failed${NC}"
    rm -f temp_test.png temp_hidden.png
    exit 1
fi

if ./ghostwire --stealth-extract temp_hidden.png | grep -q "Test"; then
    echo -e "${GREEN}✅ Steganography extract works${NC}"
else
    echo -e "${RED}❌ Steganography extract failed${NC}"
    rm -f temp_test.png temp_hidden.png
    exit 1
fi

# Clean up
rm -f temp_test.png temp_hidden.png

# Check documentation quality
echo -e "\n${YELLOW}📚 Checking documentation...${NC}"
if grep -q "👻" README.md && grep -q "🔒" README.md; then
    echo -e "${GREEN}✅ README has emojis and good formatting${NC}"
else
    echo -e "${RED}❌ README formatting issues${NC}"
    exit 1
fi

if grep -q "Installation" README.md; then
    echo -e "${GREEN}✅ README has installation instructions${NC}"
else
    echo -e "${RED}❌ README missing installation instructions${NC}"
    exit 1
fi

# Check for sensitive information
echo -e "\n${YELLOW}🔍 Checking for sensitive information...${NC}"
if grep -r "password\|secret\|key" . --include="*.py" --include="*.md" | grep -v -i "example\|test\|demo\|placeholder" | grep -v "password.*:" | head -5; then
    echo -e "${YELLOW}⚠️  Found potential sensitive content (review above)${NC}"
else
    echo -e "${GREEN}✅ No obvious sensitive information found${NC}"
fi

# Check virtual environment is excluded
echo -e "\n${YELLOW}📁 Checking .gitignore...${NC}"
if grep -q "ghostwire_env" .gitignore; then
    echo -e "${GREEN}✅ Virtual environment excluded${NC}"
else
    echo -e "${RED}❌ Virtual environment not excluded${NC}"
    exit 1
fi

# Final summary
echo -e "\n${GREEN}🎉 All checks passed!${NC}"
echo -e "${BLUE}=================================="
echo -e "📦 Project is ready for GitHub upload!"
echo -e "🔗 Repository: https://github.com/Kaiamaterasu/ghostwire"
echo -e "\n${YELLOW}Next steps:"
echo -e "1. git init (if not already done)"
echo -e "2. git add ."
echo -e "3. git commit -m \"Initial commit: Ghostwire v1.0.0\""
echo -e "4. git remote add origin https://github.com/Kaiamaterasu/ghostwire.git"
echo -e "5. git push -u origin main${NC}"
echo -e "\n${GREEN}Happy coding! 👻🔒${NC}"
