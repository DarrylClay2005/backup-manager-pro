#!/bin/bash

# Enhanced Backup Manager Script
# Creates Timeshift snapshots with local storage fallback and improved Google Drive integration

set -e

# Configuration
GOOGLE_ACCOUNT="uxzheavenlyyei@gmail.com"
TIMESHIFT_SNAPSHOTS_DIR="/home/desmond/Timeshift_Snapshots"
LOCAL_BACKUP_DIR="/home/desmond/Local_Backups"
GDRIVE_MOUNT_POINT="/home/desmond/GoogleDrive"
LOG_FILE="/var/log/backup_manager.log"
CONFIG_FILE="/home/desmond/.backup_manager_config.json"
SUDO_PASSWORD="5566"
MAX_BACKUP_SIZE_GB=4
MAX_BACKUP_SIZE_BYTES=$((MAX_BACKUP_SIZE_GB * 1024 * 1024 * 1024))

# Read configuration from JSON file
load_config() {
    if [ -f "$CONFIG_FILE" ]; then
        LOCAL_BACKUP_DIR=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('local_backup_path', '$LOCAL_BACKUP_DIR'))" 2>/dev/null || echo "$LOCAL_BACKUP_DIR")
        MAX_BACKUP_SIZE_GB=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('max_backup_size_gb', $MAX_BACKUP_SIZE_GB))" 2>/dev/null || echo "$MAX_BACKUP_SIZE_GB")
        MAX_BACKUP_SIZE_BYTES=$((MAX_BACKUP_SIZE_GB * 1024 * 1024 * 1024))
    fi
}

# Enhanced logging function
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# Function to execute commands with sudo
sudo_exec() {
    echo "$SUDO_PASSWORD" | sudo -S "$@" 2>/dev/null
}

# Check available disk space
check_disk_space() {
    local path="$1"
    local required_bytes="$2"
    
    if [ ! -d "$path" ]; then
        mkdir -p "$path" 2>/dev/null || return 1
    fi
    
    local available_bytes=$(df "$path" | awk 'NR==2 {print $4 * 1024}')
    if [ "$available_bytes" -ge "$required_bytes" ]; then
        return 0
    else
        return 1
    fi
}

# Create necessary directories
create_directories() {
    log "INFO" "Creating necessary directories..."
    mkdir -p "$TIMESHIFT_SNAPSHOTS_DIR"
    mkdir -p "$LOCAL_BACKUP_DIR"
    mkdir -p "$GDRIVE_MOUNT_POINT"
    sudo_exec mkdir -p /var/log
    sudo_exec touch "$LOG_FILE" 2>/dev/null || touch "/tmp/backup_manager.log"
    sudo_exec chown $USER:$USER "$LOG_FILE" 2>/dev/null || LOG_FILE="/tmp/backup_manager.log"
}

# Install required packages if not present
install_dependencies() {
    log "INFO" "Checking and installing dependencies..."
    
    local packages_to_install=""
    
    # Check if timeshift is installed
    if ! command -v timeshift &> /dev/null; then
        log "INFO" "Timeshift not found, will install..."
        packages_to_install="$packages_to_install timeshift"
    fi
    
    # Check if google-drive-ocamlfuse is available
    if ! command -v google-drive-ocamlfuse &> /dev/null; then
        log "WARN" "Google Drive FUSE not available - will try to install..."
        # Try to install from PPA
        sudo_exec add-apt-repository -y ppa:alessandro-strada/ppa 2>/dev/null || true
    fi
    
    if [ -n "$packages_to_install" ]; then
        log "INFO" "Installing packages: $packages_to_install"
        sudo_exec apt update 2>/dev/null || log "WARN" "Could not update package list"
        sudo_exec apt install -y $packages_to_install 2>/dev/null || log "WARN" "Some packages failed to install"
    fi
}

# Test Google Drive authentication
test_google_drive_auth() {
    log "INFO" "Testing Google Drive authentication..."
    
    # Check if config exists
    if [ ! -f ~/.gdfuse/default/config ]; then
        log "WARN" "Google Drive not configured. Please run: google-drive-ocamlfuse -label $GOOGLE_ACCOUNT"
        return 1
    fi
    
    # Test if we can list files (this tests auth without mounting)
    if timeout 10 google-drive-ocamlfuse -label "$GOOGLE_ACCOUNT" -debug 2>/dev/null | grep -q "Successfully"; then
        log "INFO" "Google Drive authentication is working"
        return 0
    else
        log "WARN" "Google Drive authentication test failed"
        return 1
    fi
}

# Mount Google Drive with better error handling
mount_google_drive() {
    log "INFO" "Attempting to mount Google Drive..."
    
    # Skip if already mounted and working
    if mountpoint -q "$GDRIVE_MOUNT_POINT" 2>/dev/null; then
        if timeout 5 ls "$GDRIVE_MOUNT_POINT" >/dev/null 2>&1; then
            log "INFO" "Google Drive already mounted and accessible"
            return 0
        else
            log "WARN" "Google Drive mounted but not accessible, unmounting..."
            fusermount -u "$GDRIVE_MOUNT_POINT" 2>/dev/null || umount "$GDRIVE_MOUNT_POINT" 2>/dev/null || true
            sleep 2
        fi
    fi
    
    # Test authentication first
    if ! test_google_drive_auth; then
        log "ERROR" "Google Drive authentication failed - skipping mount"
        return 1
    fi
    
    # Attempt to mount
    if timeout 30 google-drive-ocamlfuse -label "$GOOGLE_ACCOUNT" "$GDRIVE_MOUNT_POINT" 2>/dev/null; then
        # Verify mount worked
        if timeout 10 ls "$GDRIVE_MOUNT_POINT" >/dev/null 2>&1; then
            log "INFO" "Google Drive mounted successfully at $GDRIVE_MOUNT_POINT"
            mkdir -p "$GDRIVE_MOUNT_POINT/TimeShift_Backups" 2>/dev/null || true
            return 0
        else
            log "ERROR" "Google Drive mount failed verification"
            fusermount -u "$GDRIVE_MOUNT_POINT" 2>/dev/null || true
            return 1
        fi
    else
        log "ERROR" "Google Drive mount command failed"
        return 1
    fi
}

# Create local backup copy of important data
create_local_backup() {
    log "INFO" "Creating local backup copy..."
    
    local backup_date=$(date '+%Y%m%d-%H%M%S')
    local backup_path="$LOCAL_BACKUP_DIR/backup_$backup_date"
    
    # Check available space
    if ! check_disk_space "$LOCAL_BACKUP_DIR" "$MAX_BACKUP_SIZE_BYTES"; then
        log "WARN" "Insufficient disk space for local backup"
        return 1
    fi
    
    mkdir -p "$backup_path"
    
    # Copy important user data (up to size limit)
    local total_size=0
    local files_copied=0
    
    # Create list of important directories to backup
    local backup_dirs=(
        "$HOME/Documents"
        "$HOME/Desktop"
        "$HOME/Downloads"
        "$HOME/.config"
        "$HOME/.bashrc"
        "$HOME/.profile"
        "$TIMESHIFT_SNAPSHOTS_DIR"
    )
    
    for dir in "${backup_dirs[@]}"; do
        if [ -e "$dir" ]; then
            local dir_size=$(du -sb "$dir" 2>/dev/null | awk '{print $1}' || echo "0")
            if [ $((total_size + dir_size)) -lt "$MAX_BACKUP_SIZE_BYTES" ]; then
                log "INFO" "Backing up: $dir"
                if [ -d "$dir" ]; then
                    cp -r "$dir" "$backup_path/" 2>/dev/null || log "WARN" "Failed to copy $dir"
                else
                    cp "$dir" "$backup_path/" 2>/dev/null || log "WARN" "Failed to copy $dir"
                fi
                total_size=$((total_size + dir_size))
                files_copied=$((files_copied + 1))
            else
                log "WARN" "Skipping $dir - would exceed size limit"
            fi
        fi
    done
    
    # Create backup info file
    cat > "$backup_path/backup_info.txt" << EOF
Backup Created: $(date)
Backup Type: Local Data Backup
Files Copied: $files_copied directories/files
Total Size: $(du -sh "$backup_path" | awk '{print $1}')
Backup Path: $backup_path
EOF
    
    log "INFO" "Local backup created at: $backup_path"
    echo "$backup_path" > "$LOCAL_BACKUP_DIR/latest_backup.txt"
    
    # Clean up old backups (keep only 5 most recent)
    find "$LOCAL_BACKUP_DIR" -maxdepth 1 -type d -name "backup_*" | sort | head -n -5 | xargs rm -rf 2>/dev/null || true
    
    return 0
}

# Create Timeshift snapshot with better error handling
create_timeshift_snapshot() {
    log "INFO" "Creating Timeshift snapshot..."
    
    # Check if timeshift is configured
    if ! sudo_exec timeshift --list >/dev/null 2>&1; then
        log "WARN" "Timeshift not configured, attempting to set up..."
        sudo_exec timeshift --check 2>/dev/null || {
            log "ERROR" "Timeshift setup failed"
            return 1
        }
    fi
    
    local snapshot_name="startup-$(date '+%Y%m%d-%H%M%S')"
    
    # Create the snapshot with timeout
    if timeout 600 sudo_exec timeshift --create --comments "Automatic startup backup - $snapshot_name" --tags D; then
        log "INFO" "Timeshift snapshot created successfully: $snapshot_name"
        
        # Get snapshot info
        local latest_snapshot=$(sudo_exec timeshift --list | grep -E "^\\s*>" | tail -1 | awk '{print $2}' 2>/dev/null || echo "unknown")
        
        # Create info file
        cat > "$TIMESHIFT_SNAPSHOTS_DIR/latest_snapshot.txt" << EOF
Latest Snapshot: $latest_snapshot
Created: $(date)
Name: $snapshot_name
Type: Timeshift System Snapshot
EOF
        
        # Copy to Google Drive if mounted
        if mountpoint -q "$GDRIVE_MOUNT_POINT" 2>/dev/null && timeout 10 ls "$GDRIVE_MOUNT_POINT" >/dev/null 2>&1; then
            cp "$TIMESHIFT_SNAPSHOTS_DIR/latest_snapshot.txt" "$GDRIVE_MOUNT_POINT/TimeShift_Backups/" 2>/dev/null && \
                log "INFO" "Snapshot info copied to Google Drive" || \
                log "WARN" "Failed to copy snapshot info to Google Drive"
        fi
        
        return 0
    else
        log "ERROR" "Failed to create Timeshift snapshot (may have timed out)"
        return 1
    fi
}

# Main execution with better error handling
main() {
    log "INFO" "Starting Enhanced Backup Manager..."
    
    load_config
    
    # Always try to create directories
    create_directories
    
    # Install dependencies (non-fatal if fails)
    install_dependencies || log "WARN" "Some dependencies failed to install"
    
    # Try Google Drive mount (non-fatal if fails)
    if mount_google_drive; then
        log "INFO" "Google Drive integration available"
    else
        log "WARN" "Google Drive integration not available - continuing with local backup only"
    fi
    
    # Always create local backup
    if create_local_backup; then
        log "INFO" "Local backup completed successfully"
    else
        log "WARN" "Local backup failed"
    fi
    
    # Try Timeshift snapshot
    if create_timeshift_snapshot; then
        log "INFO" "Timeshift snapshot completed successfully"
    else
        log "WARN" "Timeshift snapshot failed - but local backup is available"
    fi
    
    log "INFO" "Backup Manager completed"
    
    # Final status report
    echo "BACKUP_STATUS_REPORT" >> "$LOG_FILE"
    echo "Timestamp: $(date)" >> "$LOG_FILE"
    echo "Google Drive: $(mountpoint -q "$GDRIVE_MOUNT_POINT" && echo "Connected" || echo "Disconnected")" >> "$LOG_FILE"
    echo "Local Backup: $([ -f "$LOCAL_BACKUP_DIR/latest_backup.txt" ] && echo "Available" || echo "Failed")" >> "$LOG_FILE"
    echo "Timeshift: $([ -f "$TIMESHIFT_SNAPSHOTS_DIR/latest_snapshot.txt" ] && echo "Available" || echo "Failed")" >> "$LOG_FILE"
    echo "END_BACKUP_STATUS_REPORT" >> "$LOG_FILE"
}

# Handle script arguments
case "${1:-main}" in
    "test-gdrive")
        test_google_drive_auth && echo "Google Drive auth OK" || echo "Google Drive auth failed"
        ;;
    "mount-gdrive")
        mount_google_drive && echo "Google Drive mounted" || echo "Google Drive mount failed"
        ;;
    "local-backup")
        create_local_backup && echo "Local backup created" || echo "Local backup failed"
        ;;
    "timeshift")
        create_timeshift_snapshot && echo "Timeshift snapshot created" || echo "Timeshift snapshot failed"
        ;;
    *)
        main "$@"
        ;;
esac
