from collections import deque

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtGui import QTextCursor, QColor, QTextCharFormat


class Console(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setReadOnly(True)
        self.setStyleSheet("background-color: black; color: white; font-family: monospace; font-size: 12px;")
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self._on_timeout)
        self.timer.start()
        self.q = deque()

    def log(self, message, color=None):
        self.q.append((message, color))

    def _on_timeout(self):
        if len(self.q) > 0:
            message, color = self.q.pop()
            self.moveCursor(QTextCursor.End)
            if color is not None:
                text_format = QTextCharFormat()
                text_format.setForeground(QColor(color))
                self.textCursor().setCharFormat(text_format)
            self.insertPlainText(message + '\n')
            self.moveCursor(QTextCursor.End)
