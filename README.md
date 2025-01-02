# Monitor Usage Tracker

A Python-based GUI application that tracks and visualizes monitor usage in real time. The application displays a pie chart showing the distribution of active window usage across multiple monitors and includes a start/stop button for pausing the tracking during breaks.

## Features

* **Real-Time Monitor Usage Tracking**: Tracks the active window and determines which monitor it’s on.

* **Dynamic Pie Chart**: Visualizes monitor usage distribution with real-time updates.

* **Start/Stop Button**: Allows you to pause and resume tracking when stepping away.

* **Cross-Platform Compatibility**: Works on macOS with Quartz APIs for window detection.

## Installation and Setup

### Prerequisites

1. **Python 3.7 or later**:
Install Python from [python.org](https://www.python.org/) or via a package manager like Homebrew:

    ```sh
    brew install python
    ```

2. **Install Required Libraries**:
Install dependencies using pip:
pip install -r requirements.txt
Ensure the following libraries are installed:

* PyQt5
* matplotlib
* screeninfo
* pyobjc

## Setting Up the Project

1. Clone the repository:

    ```sh
    git clone <repository_url>
    cd <repository_directory>
    ```

2. Install the dependencies:

    ```sh
    pip install -r requirements.txt
    ```

## Running the Application

Run the application using the Python interpreter:

```sh
python monitor_usage_gui.py
```

## Building a Standalone Executable

You can package the application into a standalone executable for macOS using pyinstaller.

## Build Instructions

1. Build the application:

    ```sh
    pyinstaller --onefile --windowed monitor_usage_gui.py
    ```

2. Locate the executable in the dist directory: `dist/monitor_usage_gui`
3. You can now double-click the executable to launch the application.

## How to Use

1. **Start the Application**:
    * Launch the application via Python or the standalone executable.
2. **Track Monitor Usage**:
    * The pie chart dynamically updates to show which monitor is being actively used.

3. **Pause/Resume Tracking**:
    * Use the “Pause” button to stop tracking when stepping away.
    * Click “Resume” to continue tracking.

## Troubleshooting

### macOS Permission Issues

* If macOS blocks the app, allow it under **System Preferences > Security & Privacy > General**.

* Ensure Python has accessibility permissions:

1. Open **System Preferences > Security & Privacy > Privacy**.
2. Add Python to the **Accessibility** section.

### Dependencies Not Found

* Verify that all dependencies are installed:

```sh
pip install -r requirements.txt
```

## Contributing

Contributions are welcome! If you’d like to add features, fix bugs, or improve the documentation:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`
3. Commit your changes and open a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
