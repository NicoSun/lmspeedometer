# multi_button_busy_all_disabled.py
import sys
import random
import time
from functools import partial
from PySide6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QPushButton, QLabel, QDialog, QHBoxLayout, QVBoxLayout
)
from PySide6.QtCore import QThread, Signal, Slot

class Worker(QThread):
    finished_signal = Signal(float)  # emit elapsed seconds

    def __init__(self, duration_seconds: float):
        super().__init__()
        self.duration = duration_seconds
        self._running = True

    def run(self):
        start = time.perf_counter()
        end_time = time.time() + self.duration
        while self._running and time.time() < end_time:
            time.sleep(0.05)
        elapsed = time.perf_counter() - start
        self.finished_signal.emit(elapsed)

    def stop(self):
        self._running = False

class ResultDialog(QDialog):
    def __init__(self, button_label: str, elapsed_seconds: float, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Task Result")
        self.setModal(True)
        layout = QVBoxLayout(self)
        label = QLabel(f"Button: {button_label}\nExecution time: {elapsed_seconds:.3f} seconds", self)
        layout.addWidget(label)
        btn_close = QPushButton("Close", self)
        btn_close.clicked.connect(self.accept)
        h = QHBoxLayout()
        h.addStretch()
        h.addWidget(btn_close)
        layout.addLayout(h)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Button — All Disabled While Busy")
        self.resize(420, 160)

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.workers = {}  # per-button worker references
        self.buttons = []  # list of buttons for easy enable/disable

        labels = ["Task A", "Task B", "Task C"]  # at least 3
        for i, lbl in enumerate(labels):
            btn = QPushButton(lbl, self)
            btn.clicked.connect(partial(self.on_button_clicked, btn))
            self.buttons.append(btn)
            row = i // 3
            col = i % 3
            self.layout.addWidget(btn, row, col)

    @Slot()
    def on_button_clicked(self, button: QPushButton):
        # If any worker is running, ignore (shouldn't happen if we disabled)
        if any(w.isRunning() for w in self.workers.values()):
            return

        # Set all buttons to busy/disabled
        self.set_all_buttons_busy(True, active_button=button)

        duration = random.uniform(1.0, 5.0)
        worker = Worker(duration)
        worker.finished_signal.connect(partial(self.on_task_finished, button))
        self.workers[button] = worker
        worker.start()

    @Slot(object, float)
    def on_task_finished(self, button: QPushButton, elapsed_seconds: float):
        # Clean up worker
        worker = self.workers.get(button)
        if worker:
            worker.quit()
            worker.wait()
            del self.workers[button]

        # Re-enable all buttons and restore texts/styles
        self.set_all_buttons_busy(False)

        # Show result dialog (non-blocking)
        dlg = ResultDialog(button.text(), elapsed_seconds, parent=self)
        dlg.show()

    def set_all_buttons_busy(self, busy: bool, active_button: QPushButton | None = None):
        if busy:
            for btn in self.buttons:
                # show which one started the work
                if btn is active_button:
                    btn.setText(f"{btn.text()} (Working...)")
                else:
                    btn.setText(btn.text())  # keep label; could add suffix if desired
                btn.setStyleSheet("background-color: #d9534f; color: white;")
                btn.setEnabled(False)
        else:
            for btn in self.buttons:
                # remove suffix if present
                btn.setText(btn.text().replace(" (Working...)", ""))
                btn.setStyleSheet("")
                btn.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
