# Backup Manager Pro

A comprehensive backup management system with a modern graphical interface, designed for Linux systems. This application provides automated system backups using Timeshift, local backup storage, and optional Google Drive integration.

## Features

- **Modern GUI Interface**: Built with Python Tkinter featuring a clean, professional design
- **Multiple Backup Types**: 
  - Timeshift system snapshots
  - Local user data backups
  - Google Drive cloud storage integration
- **Real-time Monitoring**: Live status updates and activity logging
- **Configurable Settings**: Customizable backup paths, size limits, and scheduling
- **Smart Storage Management**: Automatic cleanup of old backups to manage disk space
- **Cross-platform Compatibility**: Works on major Linux distributions

## Screenshots

The application features a modern, intuitive interface with:
- Real-time system status monitoring
- Progress indicators for backup operations
- Comprehensive activity logging
- Easy-to-use control panel

## Installation

### Prerequisites

- Python 3.6 or higher
- Linux operating system (tested on Ubuntu/Linux Mint)
- Root privileges for system-level operations

### Required Dependencies

The application will automatically attempt to install these if missing:
- `timeshift` - For system snapshots
- `google-drive-ocamlfuse` - For Google Drive integration (optional)

### Quick Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/backup-manager-pro.git
cd backup-manager-pro
```

2. Run the installation script:
```bash
chmod +x install.sh
./install.sh
```

3. Launch the application:
```bash
python3 backup_manager_gui.py
```

## Usage

### First Run

1. Launch the application using the desktop shortcut or command line
2. The application will automatically check system dependencies
3. Configure your backup preferences in Settings
4. Set up Google Drive authentication if desired (optional)
5. Click "Create Backup Now" to start your first backup

### Google Drive Setup (Optional)

To enable Google Drive integration:

1. Click "Mount Google Drive" in the application
2. Follow the authentication prompts in your web browser
3. Grant the necessary permissions
4. The application will automatically mount your Google Drive

### Configuration

Access settings through the Settings button to configure:
- **Local backup directory**: Choose where to store local backups
- **Maximum backup size**: Set size limits (default: 4GB)
- **Auto-start**: Enable automatic backup on application launch
- **Refresh interval**: Set how often status updates occur

## Technical Details

### Architecture

- **Frontend**: Python Tkinter with modern styling
- **Backend**: Bash scripts for system operations
- **Storage**: JSON configuration files
- **Logging**: Comprehensive activity logging with timestamps

### File Structure

```
backup-manager-pro/
├── backup_manager_gui.py      # Main GUI application
├── backup_manager_script.sh   # Core backup operations
├── install.sh                 # Installation script
├── requirements.txt           # Python dependencies
├── config/                    # Configuration templates
├── icons/                     # Application icons
└── desktop/                   # Desktop integration files
```

### Backup Process

1. **System Check**: Verifies available disk space and dependencies
2. **Local Backup**: Creates compressed archives of user data
3. **Timeshift Snapshot**: Creates system-level snapshots
4. **Cloud Sync**: Optionally syncs to Google Drive
5. **Cleanup**: Removes old backups based on retention policy

## Configuration

The application stores its configuration in `~/.backup_manager_config.json`:

```json
{
  "auto_start": true,
  "local_backup_path": "/home/user/Local_Backups",
  "max_backup_size_gb": 4,
  "max_snapshots": 10,
  "refresh_interval": 30,
  "theme": "modern"
}
```

## Troubleshooting

### Common Issues

**Google Drive won't mount:**
- Ensure `google-drive-ocamlfuse` is installed
- Check internet connection
- Re-authenticate if necessary

**Timeshift fails:**
- Verify you have sufficient disk space
- Ensure Timeshift is properly configured
- Check system permissions

**Application won't start:**
- Verify Python 3 is installed
- Check all dependencies are met
- Review log files in `/var/log/backup_manager.log`

### Logging

Application logs are stored in:
- System log: `/var/log/backup_manager.log`
- Fallback log: `/tmp/backup_manager.log`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue on GitHub or contact the maintainers.

## Changelog

### Version 2.0
- Complete UI redesign with modern styling
- Enhanced Google Drive integration
- Improved error handling and logging
- Configurable settings system
- Better progress tracking

### Version 1.0
- Initial release
- Basic backup functionality
- Timeshift integration
- Simple GUI interface

## Acknowledgments

- Built with Python Tkinter
- Uses Timeshift for system snapshots
- Google Drive integration via ocamlfuse
- Inspired by modern backup solutions
