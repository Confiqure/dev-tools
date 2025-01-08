import sys
import threading
import time

import Quartz
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from screeninfo import get_monitors


def create_icon_with_text(text: str) -> QIcon:
    size = 32
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setPen(QColor("black"))

    font = QFont()
    font.setBold(True)
    font.setPointSize(18)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignCenter, text)
    painter.end()

    return QIcon(pixmap)


def get_screen_bounds():
    """
    Returns the bounding boxes of all available screens.
    """
    screens = get_monitors()  # from the 'screeninfo' library
    return [(s.x, s.y, s.width, s.height) for s in screens]


def get_active_window_position():
    """
    Returns the bounding box of the active (frontmost) window if available.
    """
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
                return x, y, width, height
    except Exception as e:
        print(f"Error getting active window position: {e}")
    return None


def format_time(seconds: float) -> str:
    """
    Return a string representing 'seconds' in sec, min, or hrs,
    depending on the magnitude.
    """
    if seconds < 60:
        return f"{seconds:.1f} sec"
    elif seconds < 3600:
        return f"{seconds / 60:.1f} min"
    else:
        return f"{seconds / 3600:.1f} hrs"


class ScreenUsageApp(QWidget):
    def __init__(self):
        super().__init__()
        self.screen_bounds = get_screen_bounds()
        self.screen_usage = [0] * len(self.screen_bounds)
        self.tracking = True  # Toggle usage tracking

        # Set up the GUI layout
        self.setWindowTitle("Screen Usage Tracker")
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

        # Add label for balance time
        self.balance_label = QLabel("All screens are balanced: 0 sec")
        self.balance_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.balance_label)

        self.setLayout(main_layout)

        # Start tracking thread
        self.tracking_thread = threading.Thread(
            target=self.screen_usage_tracker, daemon=True
        )
        self.tracking_thread.start()

        # Start GUI update timer
        self.update_timer = self.startTimer(1000)

    def timerEvent(self, event):
        if not self.tracking:
            QApplication.setWindowIcon(create_icon_with_text("| |"))  # Pause icon
            return

        total_usage = sum(self.screen_usage)
        n = len(self.screen_usage)

        # Compute pie chart percentages
        if n == 0 or total_usage == 0:
            normalized_percentages = [0] * n
        else:
            raw_percentages = [count / total_usage for count in self.screen_usage]
            normalization_factor = 100 / sum(raw_percentages)
            normalized_percentages = [p * normalization_factor for p in raw_percentages]

        # Update pie chart
        self.update_pie_chart(normalized_percentages)

        max_x = 0.0
        max_screen_idx = -1

        # Only meaningful if there's more than one screen
        if n > 1:
            for i, usage_i in enumerate(self.screen_usage):
                numerator = total_usage - n * usage_i
                denominator = n - 1
                x = numerator / denominator  # how many seconds needed
                if x > max_x:
                    max_x = x
                    max_screen_idx = i

        # If the result is negative (or n < 2), set it to zero
        if max_x < 0 or n < 2:
            max_x = 0
            max_screen_idx = -1

        # Convert to sec, min, or hours
        max_time_str = format_time(max_x)

        # Set the label text
        if max_screen_idx == -1:
            # No meaningful "catch up" time
            self.balance_label.setText("All screens are balanced: 0 sec")
            QApplication.setWindowIcon(create_icon_with_text(":)"))
        else:
            self.balance_label.setText(
                f"Screen {max_screen_idx + 1} needs {max_time_str} to reach balance"
            )
            QApplication.setWindowIcon(create_icon_with_text(str(max_screen_idx + 1)))

    def screen_usage_tracker(self):
        """
        Continuously increments usage counters for the active screen.
        """
        while True:
            if not self.tracking:
                time.sleep(0.1)  # Sleep briefly when paused
                continue

            active_window_pos = get_active_window_position()
            if active_window_pos:
                x, y, width, height = active_window_pos
                for i, (sx, sy, swidth, sheight) in enumerate(self.screen_bounds):
                    if sx <= x < sx + swidth and sy <= y < sy + sheight:
                        self.screen_usage[i] += 1
                        break
            time.sleep(1)

    def update_pie_chart(self, percentages):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Validate percentages to ensure no NaN values
        if not any(percentages):
            percentages = [1] * len(percentages)
            labels = [f"Screen {i + 1} (No Data)" for i in range(len(percentages))]
        else:
            labels = [f"Screen {i + 1}" for i in range(len(percentages))]

        ax.pie(
            percentages, labels=labels, autopct="%1.1f%%", startangle=90, normalize=True
        )
        ax.set_title("Screen Usage Distribution")
        self.canvas.draw()

    def toggle_tracking(self):
        self.tracking = not self.tracking
        self.toggle_button.setText("Resume" if not self.tracking else "Pause")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenUsageApp()
    window.show()
    sys.exit(app.exec())
