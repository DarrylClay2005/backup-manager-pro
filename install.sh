#!/bin/bash

# Backup Manager Pro Installation Script
# Installs dependencies and sets up the application

set -e

echo "🔄 Backup Manager Pro - Installation Script"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.local/share/backup-manager-pro"
DESKTOP_FILE="$HOME/.local/share/applications/backup-manager-pro.desktop"
BIN_FILE="$HOME/.local/bin/backup-manager-pro"

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✅${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌${NC} $1"
}

# Check if Python 3 is installed
check_python() {
    log "Checking Python 3 installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_success "Python 3 found: $PYTHON_VERSION"
        return 0
    else
        log_error "Python 3 is required but not installed."
        return 1
    fi
}

# Install system dependencies
install_dependencies() {
    log "Installing system dependencies..."
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        log_error "Please don't run this script as root. It will ask for sudo when needed."
        exit 1
    fi
    
    # Update package list
    log "Updating package list..."
    sudo apt update || log_warning "Failed to update package list"
    
    # Install required packages
    local packages="python3-tk timeshift"
    log "Installing packages: $packages"
    sudo apt install -y $packages || log_warning "Some packages may have failed to install"
    
    # Try to add Google Drive FUSE PPA and install
    log "Setting up Google Drive FUSE (optional)..."
    if sudo add-apt-repository -y ppa:alessandro-strada/ppa 2>/dev/null; then
        sudo apt update 2>/dev/null || true
        sudo apt install -y google-drive-ocamlfuse 2>/dev/null || log_warning "Google Drive FUSE installation failed - you can install it later"
    else
        log_warning "Could not add Google Drive FUSE PPA - you can install google-drive-ocamlfuse manually if needed"
    fi
    
    log_success "Dependency installation completed"
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    mkdir -p "$HOME/.local/bin"
    mkdir -p "$HOME/.local/share/applications"
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$HOME/Local_Backups"
    mkdir -p "$HOME/Timeshift_Snapshots"
    mkdir -p "$HOME/GoogleDrive"
    
    log_success "Directories created"
}

# Copy application files
copy_files() {
    log "Copying application files..."
    
    # Copy main application files
    cp "$SCRIPT_DIR/backup_manager_gui.py" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/backup_manager_script.sh" "$INSTALL_DIR/"
    chmod +x "$INSTALL_DIR/backup_manager_script.sh"
    
    # Copy README if exists
    if [ -f "$SCRIPT_DIR/README.md" ]; then
        cp "$SCRIPT_DIR/README.md" "$INSTALL_DIR/"
    fi
    
    log_success "Application files copied to $INSTALL_DIR"
}

# Create desktop entry
create_desktop_entry() {
    log "Creating desktop entry..."
    
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=Backup Manager Pro
Comment=Modern backup system with local storage and Google Drive support
Icon=drive-harddisk-system
Exec=python3 $INSTALL_DIR/backup_manager_gui.py
Terminal=false
Categories=System;Utility;
StartupNotify=true
Keywords=backup;system;timeshift;google-drive;
EOF
    
    chmod +x "$DESKTOP_FILE"
    log_success "Desktop entry created at $DESKTOP_FILE"
}

# Create launcher script
create_launcher() {
    log "Creating launcher script..."
    
    cat > "$BIN_FILE" << EOF
#!/bin/bash
# Backup Manager Pro Launcher
cd "$INSTALL_DIR"
python3 "$INSTALL_DIR/backup_manager_gui.py" "\$@"
EOF
    
    chmod +x "$BIN_FILE"
    log_success "Launcher script created at $BIN_FILE"
}

# Set up log file permissions
setup_logging() {
    log "Setting up logging..."
    
    # Create log directory if it doesn't exist
    sudo mkdir -p /var/log 2>/dev/null || true
    
    # Try to create the log file and set permissions
    sudo touch /var/log/backup_manager.log 2>/dev/null || true
    sudo chown $USER:$USER /var/log/backup_manager.log 2>/dev/null || {
        log_warning "Could not set up system log file, will use fallback location"
    }
    
    log_success "Logging setup completed"
}

# Main installation function
main() {
    echo
    log "Starting Backup Manager Pro installation..."
    echo
    
    # Check prerequisites
    if ! check_python; then
        log_error "Installation failed. Please install Python 3 first."
        exit 1
    fi
    
    # Install dependencies
    install_dependencies
    
    # Create directories
    create_directories
    
    # Copy files
    copy_files
    
    # Create desktop integration
    create_desktop_entry
    create_launcher
    
    # Setup logging
    setup_logging
    
    echo
    log_success "Installation completed successfully!"
    echo
    echo -e "${GREEN}🎉 Backup Manager Pro is now installed!${NC}"
    echo
    echo "You can now:"
    echo -e "  • Launch from Applications menu: ${BLUE}Backup Manager Pro${NC}"
    echo -e "  • Run from terminal: ${BLUE}backup-manager-pro${NC}"
    echo -e "  • Run directly: ${BLUE}python3 $INSTALL_DIR/backup_manager_gui.py${NC}"
    echo
    echo -e "${YELLOW}First Run Tips:${NC}"
    echo "  • The application will automatically check dependencies"
    echo "  • Configure your backup preferences in Settings"
    echo "  • Google Drive integration is optional"
    echo "  • Check the logs for any setup issues"
    echo
    echo -e "${YELLOW}Note:${NC} Some features may require sudo privileges during operation."
    echo
}

# Run the installation
main "$@"
