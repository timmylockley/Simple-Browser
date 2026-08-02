#!/bin/bash
set -e

# Repository configuration
REPO_USER="timmylockley"
REPO_NAME="Simple-Browser"
BRANCH="main"

SCRIPT_URL="https://raw.githubusercontent.com/${REPO_USER}/${REPO_NAME}/${BRANCH}/simple_browser.py"
ICON_URL="https://raw.githubusercontent.com/${REPO_USER}/${REPO_NAME}/${BRANCH}/simple-browser.png"

echo "=== Simple Browser Universal Installer ==="

# 1. Check for Python 3 and pip
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed." >&2
    exit 1
fi

# 2. Install PyInstaller if not present
if ! command -v pyinstaller &> /dev/null; then
    echo "Installing PyInstaller..."
    pip3 install --user pyinstaller
    export PATH="$HOME/.local/bin:$PATH"
fi

# 3. Create a temporary working workspace
WORK_DIR=$(mktemp -d)
cd "$WORK_DIR"
echo "Downloading source files from GitHub..."

# 4. Pull the script and icon directly from your repository
curl -sSL "$SCRIPT_URL" -o simple_browser.py
curl -sSL "$ICON_URL" -o simple-browser.png

if [ ! -f "simple_browser.py" ]; then
    echo "Error: Failed to download simple_browser.py from GitHub." >&2
    exit 1
fi

# 5. Compile into a standalone executable using PyInstaller
echo "Compiling application executable..."
pyinstaller --onefile --windowed simple_browser.py

# 6. Install globally onto the system
echo "Installing application files system-wide..."
sudo mkdir -p /usr/local/share/simple-browser
sudo mkdir -p /usr/local/bin
sudo mkdir -p /usr/share/pixmaps

sudo cp dist/simple_browser /usr/local/bin/simple-browser
sudo cp simple-browser.png /usr/share/pixmaps/simple-browser.png

# 7. Create system-wide Desktop Menu Shortcut
sudo bash -c 'cat > /usr/share/applications/simple-browser.desktop << 'DESKTOP'
[Desktop Entry]
Name=Simple Browser
Comment=A lightweight Python web browser
Exec=simple-browser
Icon=simple-browser
Terminal=false
Type=Application
Categories=Network;WebBrowser;
DESKTOP'

# 8. Refresh Desktop Database
if command -v update-desktop-database &> /dev/null; then
    sudo update-desktop-database -q
fi

# Clean up temporary files
cd ~
rm -rf "$WORK_DIR"

echo "=== Installation Complete! Simple Browser is ready to use. ==="
