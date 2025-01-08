# Screen Usage Tracker

A **Python-based GUI application** that tracks and visualizes *screen usage* in real time. It shows a dynamic pie chart displaying which *physical screen* is actively in use (based on the active window’s position) and includes a pause/resume feature for when you step away. This project primarily supports macOS by leveraging *Quartz* APIs to detect active windows, but its foundation allows for potential cross-platform expansion in the future.

## Features

- **Real-Time Screen Usage Tracking**  
  Continuously identifies which screen is hosting the active (frontmost) window.

- **Dynamic Pie Chart**  
  Visualizes per-screen usage distribution with live updates and labels.

- **Balance Indicator**  
  Informs you which screen would need more “catch-up” time to balance usage across all screens.

- **Pause/Resume Button**  
  Pauses tracking while you’re away from the computer and resumes with a single click.

- **Dock Icon Indicators**  
  Displays an icon in the dock or taskbar that mirrors the state of the application (e.g., screen index or pause symbol).

- **macOS Compatibility**  
  Utilizes Quartz for window detection. (Other platforms might require additional APIs.)

## Table of Contents

1. [Installation and Setup](#installation-and-setup)  
2. [Setting Up the Project](#setting-up-the-project)  
3. [Running the Application](#running-the-application)  
4. [Building a Standalone Executable](#building-a-standalone-executable)  
5. [How to Use](#how-to-use)  
6. [Troubleshooting](#troubleshooting)  
7. [Contributing](#contributing)  
8. [License](#license)

## Installation and Setup

### Prerequisites

1. **Python 3.7 or Later**  
   Install Python from [python.org](https://www.python.org/) or via a package manager (e.g., Homebrew on macOS):

   ```sh
   brew install python
   ```

2. **Required Libraries**  
   Make sure you have the following packages:
   - PyQt5
   - matplotlib
   - screeninfo
   - pyobjc

   You can install them all via:

   ```sh
   pip install -r requirements.txt
   ```

## Setting Up the Project

1. **Clone the Repository**  

   ```sh
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Install Dependencies**  

   ```sh
   pip install -r requirements.txt
   ```

## Running the Application

Run the application using the Python interpreter:

```sh
python screen_usage_gui.py
```

## Building a Standalone Executable

You can bundle this application into a standalone macOS executable with [PyInstaller](https://pyinstaller.org/en/stable/).

### Build Instructions

1. **Build the Application**  

   ```sh
   pyinstaller --onefile --windowed screen_usage_gui.py
   ```

2. **Locate the Executable**  
   Find the compiled file in the `dist` directory:  
   `dist/screen_usage_gui`
3. **Launch**  
   Double-click on the executable to run the application.

## How to Use

1. **Start the Application**  
   - Either run `python screen_usage_gui.py` or use the standalone executable on macOS.

2. **Real-Time Screen Usage Visualization**  
   - A pie chart dynamically indicates which screen is actively used based on where the topmost window resides.

3. **Balance Indicator**  
   - The application calculates and shows if one screen needs additional “catch-up” time to balance usage across multiple screens.

4. **Pause/Resume Tracking**  
   - Click “Pause” to stop updating usage data when you take a break.  
   - Click “Resume” to continue tracking after your break.

## Troubleshooting

### macOS Permission Issues

- **App Blocked**: If macOS flags the app, allow it under **System Preferences > Security & Privacy > General**.  
- **Accessibility Permissions**: Quartz needs accessibility permissions to get window info:
  1. Open **System Preferences > Security & Privacy > Privacy**.
  2. Add **Python** (or your chosen Python environment) under **Accessibility**.

### Dependencies Not Found

- Make sure you have installed all dependencies:

  ```sh
  pip install -r requirements.txt
  ```

- If issues persist, verify that you’re using the correct Python environment (e.g., virtualenv or conda environment).

## Contributing

**Contributions are always welcome!** If you’d like to add new features, fix bugs, or improve the documentation:

1. **Fork the repository**  
2. **Create a new branch**:  

   ```sh
   git checkout -b feature/your-feature-name
   ```

3. **Commit your changes**  
4. **Open a Pull Request** on GitHub

Feel free to open issues if you encounter any bugs or have feature requests.

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

Thank you for using **Screen Usage Tracker**! If you find it useful or have any feedback, please let us know by creating an issue or opening a pull request.
