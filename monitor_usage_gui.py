import sys
import time
import threading
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from screeninfo import get_monitors
import Quartz


def get_monitor_bounds():
    monitors = get_monitors()
    return [(m.x, m.y, m.width, m.height) for m in monitors]


def get_active_window_position():
    try:
        # Get the active application
        active_app = Quartz.CGWindowListCopyWindowInfo(
            Quartz.kCGWindowListOptionOnScreenOnly
            | Quartz.kCGWindowListExcludeDesktopElements,
            Quartz.kCGNullWindowID,
        )

        # Filter for the frontmost application window
        active_window = next(
            (w for w in active_app if w.get("kCGWindowLayer") == 0), None
        )

        if active_window:
            bounds = active_window.get("kCGWindowBounds")
            if bounds:
                x = bounds.get("X", 0)
                y = bounds.get("Y", 0)
                width = bounds.get("Width", 0)
                height = bounds.get("Height", 0)
                # print(f"Active Window Position: ({x}, {y}), Size: ({width}x{height})")
                return x, y, width, height
    except Exception as e:
        print(f"Error getting active window position: {e}")
    return None


class MonitorUsageApp(QWidget):
    def __init__(self):
        super().__init__()
        self.monitor_bounds = get_monitor_bounds()
        self.monitor_usage = [0] * len(self.monitor_bounds)
        self.start_time = time.time()
        self.tracking = True  # To toggle tracking

        # Set up the GUI layout
        self.setWindowTitle("Monitor Usage Tracker")
        main_layout = QVBoxLayout()
        chart_layout = QHBoxLayout()

        # Add pie chart
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        main_layout.addLayout(chart_layout)

        # Add Start/Stop button
        self.toggle_button = QPushButton("Pause")
        self.toggle_button.clicked.connect(self.toggle_tracking)
        main_layout.addWidget(self.toggle_button)

        self.setLayout(main_layout)

        # Start monitoring thread
        self.monitoring_thread = threading.Thread(
            target=self.monitor_usage_tracker, daemon=True
        )
        self.monitoring_thread.start()

        # Start GUI update timer
        self.update_timer = self.startTimer(1000)

    def timerEvent(self, event):
        if not self.tracking:
            return  # Do nothing if tracking is paused

        total_usage = sum(self.monitor_usage)

        if total_usage == 0:
            normalized_percentages = [0] * len(self.monitor_usage)
        else:
            raw_percentages = [count / total_usage for count in self.monitor_usage]
            normalization_factor = 100 / sum(raw_percentages)
            normalized_percentages = [p * normalization_factor for p in raw_percentages]

        # Update pie chart
        self.update_pie_chart(normalized_percentages)

    def monitor_usage_tracker(self):
        while True:
            if not self.tracking:
                time.sleep(0.1)  # Sleep for a short while when paused
                continue

            active_window_pos = get_active_window_position()
            if active_window_pos:
                x, y, width, height = active_window_pos
                for i, (mx, my, mwidth, mheight) in enumerate(self.monitor_bounds):
                    if mx <= x < mx + mwidth and my <= y < mheight:
                        self.monitor_usage[i] += 1
                        break
            time.sleep(1)

    def update_pie_chart(self, percentages):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Validate percentages to ensure no NaN values
        if not any(percentages):
            percentages = [1] * len(percentages)
            labels = [f"Monitor {i + 1} (No Data)" for i in range(len(percentages))]
        else:
            labels = [f"Monitor {i + 1}" for i in range(len(percentages))]

        ax.pie(
            percentages, labels=labels, autopct="%1.1f%%", startangle=90, normalize=True
        )
        ax.set_title("Monitor Usage Distribution")
        self.canvas.draw()

    def toggle_tracking(self):
        self.tracking = not self.tracking
        self.toggle_button.setText("Resume" if not self.tracking else "Pause")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MonitorUsageApp()
    window.show()
    sys.exit(app.exec())
