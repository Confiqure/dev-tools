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
    Returns the bounding box (x, y, width, height) of the active (frontmost) window if available.
    """
    try:
        # Get the active application's windows
        active_app = Quartz.CGWindowListCopyWindowInfo(
            Quartz.kCGWindowListOptionOnScreenOnly
            | Quartz.kCGWindowListExcludeDesktopElements,
            Quartz.kCGNullWindowID,
        )

        # Filter for a frontmost, non-desktop window (layer = 0)
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


def get_mouse_position():
    """Returns the current mouse cursor position (x, y)."""
    loc = Quartz.CGEventGetLocation(Quartz.CGEventCreate(None))
    return (loc.x, loc.y)


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

        # Flags for manual pause and idle pause
        self.user_paused = False  # True when user manually clicks "Pause"
        self.idle_detected = False  # True when mouse hasn't moved for 2+ minutes

        # Track the screen that was last active (for retroactive deduction)
        self.last_active_screen = -1

        # Store last mouse position and last move time
        self.last_mouse_pos = get_mouse_position()
        self.last_mouse_move_time = time.time()

        self.setWindowTitle("Screen Usage Tracker")
        main_layout = QVBoxLayout()
        chart_layout = QHBoxLayout()

        # Add pie chart
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        main_layout.addLayout(chart_layout)

        # Add Pause/Resume button
        self.toggle_button = QPushButton("Pause")
        self.toggle_button.clicked.connect(self.toggle_tracking)
        main_layout.addWidget(self.toggle_button)

        # Add label for balance time
        self.balance_label = QLabel("All screens are balanced: 0 sec")
        self.balance_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.balance_label)

        self.setLayout(main_layout)

        # Start the background tracking thread
        self.tracking_thread = threading.Thread(
            target=self.screen_usage_tracker, daemon=True
        )
        self.tracking_thread.start()

        # Start GUI update timer (updates once per second)
        self.update_timer = self.startTimer(1000)

    def timerEvent(self, event):
        """
        Fires once per second to update the GUI (pie chart, label, icon),
        and refresh the button text based on idle/manual pause status.
        """
        # Update the button text first
        if self.user_paused:
            self.toggle_button.setText("Resume")
        elif self.idle_detected:
            self.toggle_button.setText("Idle...")
        else:
            self.toggle_button.setText("Pause")

        # Determine if we are actually tracking or not
        is_tracking = (not self.user_paused) and (not self.idle_detected)

        # Update the window icon to reflect state
        if not is_tracking:
            QApplication.setWindowIcon(create_icon_with_text("| |"))
        else:
            total_usage = sum(self.screen_usage)
            n = len(self.screen_usage)

            # Compute pie chart percentages
            if n == 0 or total_usage == 0:
                normalized_percentages = [0] * n
            else:
                raw_percentages = [count / total_usage for count in self.screen_usage]
                normalization_factor = 100 / sum(raw_percentages)
                normalized_percentages = [
                    p * normalization_factor for p in raw_percentages
                ]

            # Update pie chart
            self.update_pie_chart(normalized_percentages)

            # Compute “time to balance” and update label + icon
            max_x = 0.0
            max_screen_idx = -1

            if n > 1:
                for i, usage_i in enumerate(self.screen_usage):
                    numerator = total_usage - n * usage_i
                    denominator = n - 1
                    x = numerator / denominator  # how many seconds needed
                    if x > max_x:
                        max_x = x
                        max_screen_idx = i

            # If the result is negative (or only 1 screen), set it to zero
            if max_x < 0 or n < 2:
                max_x = 0
                max_screen_idx = -1

            max_time_str = format_time(max_x)
            if max_screen_idx == -1:
                self.balance_label.setText("All screens are balanced: 0 sec")
                QApplication.setWindowIcon(create_icon_with_text(":)"))
            else:
                self.balance_label.setText(
                    f"Screen {max_screen_idx + 1} needs {max_time_str} to reach balance"
                )
                QApplication.setWindowIcon(
                    create_icon_with_text(str(max_screen_idx + 1))
                )

    def screen_usage_tracker(self):
        """
        Continuously checks mouse movement (idle detection) and increments usage
        counters for the active screen when tracking is enabled.
        """
        IDLE_LIMIT = 120  # 2 minutes in seconds

        while True:
            # 1) Check mouse movement unconditionally (so we know when user moves again).
            current_mouse_pos = get_mouse_position()

            if current_mouse_pos != self.last_mouse_pos:
                # Mouse moved
                self.last_mouse_pos = current_mouse_pos
                self.last_mouse_move_time = time.time()

                # If we had been idle-detected, clear it
                if self.idle_detected:
                    self.idle_detected = False
            else:
                # Mouse hasn't moved: check how long
                elapsed_idle = time.time() - self.last_mouse_move_time
                # Only trigger idle if we are not paused or already idle
                if (
                    not self.idle_detected
                    and not self.user_paused  # do not detect idle while paused
                    and elapsed_idle > IDLE_LIMIT
                ):
                    self.idle_detected = True
                    # Retroactively remove 2 minutes from the last active screen
                    if self.last_active_screen != -1:
                        self.screen_usage[self.last_active_screen] = max(
                            0, self.screen_usage[self.last_active_screen] - IDLE_LIMIT
                        )

            # 2) Determine if we are currently tracking (not paused and not idle)
            is_tracking = (not self.user_paused) and (not self.idle_detected)

            if is_tracking:
                # Increment usage on whichever screen is active
                active_window_pos = get_active_window_position()
                if active_window_pos:
                    x, y, width, height = active_window_pos
                    for i, (sx, sy, swidth, sheight) in enumerate(self.screen_bounds):
                        if sx <= x < sx + swidth and sy <= y < sy + sheight:
                            self.screen_usage[i] += 1
                            self.last_active_screen = i
                            break

            # Sleep 1 second between increments
            time.sleep(1)

    def update_pie_chart(self, percentages):
        """
        Updates the matplotlib pie chart with the given percentages (one per screen).
        """
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if not any(percentages) and len(percentages) > 0:
            # If everything is zero, show a dummy chart
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
        """
        Toggle user_paused. If user_paused was False -> True, that means Pause.
        If user_paused was True -> False, that means Resume.
        """
        was_paused = self.user_paused
        self.user_paused = not self.user_paused

        # When resuming from a manual pause, reset the idle timer so
        # that any mouse inactivity during the pause isn’t counted as idle.
        if was_paused and not self.user_paused:
            self.last_mouse_move_time = time.time()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenUsageApp()
    window.show()
    sys.exit(app.exec())
