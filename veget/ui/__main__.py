from PySide6.QtWidgets import QApplication

from veget.ui.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication()
    window = MainWindow()
    window.show()
    app.exec()
