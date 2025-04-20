# GAMING Parking System

A desktop application for managing parking tickets at GAMING. This application allows users to:
- Create parking tickets
- Print tickets
- Manage parking records
- Export data to CSV

## Features
- Simple and intuitive user interface
- Instant ticket printing
- Data export functionality
- Database management
- Ticket preview before printing

## Installation

1. Clone the repository:
```bash
git clone https://github.com/kohaku1907/gui_xe_app.git
cd gui_xe_app
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python src/main.py
```

2. Enter the vehicle number in the input field
3. Click "In" to print the ticket
4. Use the ">>>" button to export data to CSV

## Building for Windows Deployment

To create a standalone Windows executable that can be run without Python installation:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the application:
```bash
pyinstaller --onefile --windowed --name "Gaming Parking" --icon=resources/icon.ico src/main.py
```

This will create a single executable file in the `dist` directory.

### Build Options Explained:
- `--onefile`: Creates a single executable file
- `--windowed`: Prevents console window from showing
- `--name`: Sets the output filename
- `--icon`: Adds a custom icon to the executable

### Additional Build Options:
- To include additional data files (like the database):
```bash
pyinstaller --onefile --windowed --name "Gaming Parking" --add-data "resources/gui_xe.db;resources" --icon=resources/icon.ico src/main.py
```

- To create a build with debug information:
```bash
pyinstaller --onefile --windowed --name "Gaming Parking" --debug=all src/main.py
```

### Post-Build Steps:
1. Test the executable in the `dist` directory
2. Create a shortcut to the executable
3. Copy the executable and shortcut to the target computer
4. Ensure the target computer has the required printer drivers installed

### Troubleshooting:
- If the application fails to start, check if all required DLLs are included
- Ensure the database file is in the correct location
- Check printer connectivity and drivers
- For debugging, run without `--windowed` to see console output

## Project Structure
```
gui_xe_app/
├── src/                # Source code
├── resources/          # UI files and resources
├── docs/              # Documentation
├── requirements.txt   # Project dependencies
└── README.md         # This file
```

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request. 