#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Check if script is run as root (sudo)
if [ "$EUID" -ne 0 ]; then
  echo "[-] Error: Please run this installer with root privileges."
  echo "    Usage: sudo ./install.sh"
  exit 1
fi

echo "[+] Detecting Linux Distribution and installing dependencies..."

if command -v apt &> /dev/null; then
    # Debian / Ubuntu / Linux Mint / Pop!_OS
    echo "[*] Detected Debian/Ubuntu-based distribution (APT)."
    apt update
    apt install -y python3 python3-pyqt5 python3-pyqt5.qtwebengine

elif command -v pacman &> /dev/null; then
    # Arch Linux / Manjaro / EndeavourOS
    echo "[*] Detected Arch-based distribution (Pacman)."
    pacman -S --noconfirm python python-pyqt5 python-pyqtwebengine

elif command -v dnf &> /dev/null; then
    # Fedora / RHEL / CentOS Stream
    echo "[*] Detected Fedora-based distribution (DNF)."
    dnf install -y python3 python3-qt5 python3-qt5-webengine

else
    echo "[-] Warning: Could not detect package manager automatically."
    echo "    Please ensure python3, PyQt5, and QtWebEngine are installed manually before running."
fi

echo "[+] Setting up Simple Browser application directories..."
INSTALL_DIR="/usr/share/simple-browser"
mkdir -p "$INSTALL_DIR"

# Copy the python script
if [ -f "simple_browser.py" ]; then
    cp simple_browser.py "$INSTALL_DIR/simple_browser.py"
else
    echo "[-] Error: simple_browser.py not found in the current directory!"
    exit 1
fi

# Copy the icon if it exists
if [ -f "simple-browser.png" ]; then
    mkdir -p /usr/share/pixmaps
    cp simple-browser.png /usr/share/pixmaps/simple-browser.png
    echo "[+] App icon installed successfully."
else
    echo "[!] Notice: simple-browser.png not found. Skipping app icon installation."
fi

echo "[+] Creating global command wrapper (/usr/bin/simple-browser)..."
cat << 'EOF' > /usr/bin/simple-browser
#!/bin/bash
python3 /usr/share/simple-browser/simple_browser.py "$@"
EOF
chmod +x /usr/bin/simple-browser

echo "[+] Creating desktop application menu entry..."
mkdir -p /usr/share/applications
cat << 'EOF' > /usr/share/applications/simple-browser.desktop
[Desktop Entry]
Name=Simple Browser
Comment=A modern Python web browser built with PyQt5
Exec=/usr/bin/simple-browser
Icon=simple-browser
Terminal=false
Type=Application
Categories=Network;WebBrowser;
EOF

# Refresh system desktop database so it shows up instantly
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database
fi

echo ""
echo "[✓] Installation complete!"
echo "    You can now open 'Simple Browser' from your desktop application menu or type 'simple-browser' in any terminal."
