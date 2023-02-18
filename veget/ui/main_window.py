from PySide6.QtWidgets import QWidget, QMainWindow, QLabel, QLineEdit, QPushButton, QFileDialog, \
    QSpinBox, QTableWidget, QHBoxLayout, QTableWidgetItem, QDialog, QVBoxLayout, QDialogButtonBox, QFrame, QSpacerItem, \
    QSizePolicy

from veget.ui.scraping_dialog import ScrapingDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VeGet0n")
        self.setGeometry(100, 100, 600, 800)
        self._init_ui()

    def _init_ui(self):
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.username = QLineEdit(widget)
        self.username.setPlaceholderText("LinkedIn username")
        layout.addWidget(self.username)

        self.password = QLineEdit(widget, echoMode=QLineEdit.Password)
        self.password.setPlaceholderText("LinkedIn password")
        layout.addWidget(self.password)

        sleep_label = QLabel("Sleep", widget)
        self.sleep = QSpinBox(widget)
        self.sleep.setMinimum(0)
        self.sleep.setMaximum(60)
        self.sleep.setValue(5)
        sleep_layout = QHBoxLayout(widget)
        sleep_layout.addWidget(sleep_label)
        sleep_layout.addWidget(self.sleep, stretch=1)
        layout.addLayout(sleep_layout)

        timeout_label = QLabel("Timeout", widget)
        self.timeout = QSpinBox(widget)
        self.timeout.setMinimum(0)
        self.timeout.setMaximum(60)
        self.timeout.setValue(10)
        timeout_layout = QHBoxLayout(widget)
        timeout_layout.addWidget(timeout_label)
        timeout_layout.addWidget(self.timeout, stretch=1)
        layout.addLayout(timeout_layout)

        search_frame = QFrame(widget)
        search_frame.setFrameShadow(QFrame.Raised)
        search_frame.setFrameShape(QFrame.StyledPanel)
        search_frame_layout = QVBoxLayout(search_frame)
        search_frame.setLayout(search_frame_layout)

        self.search_table = QTableWidget(self)
        self.search_table.setColumnCount(2)
        self.search_table.setHorizontalHeaderLabels(["Company Name", "Search URL"])
        search_frame_layout.addWidget(self.search_table, stretch=1)

        table_buttons_layout = QHBoxLayout(widget)
        self.company_name = QLineEdit(widget)
        self.company_name.setPlaceholderText("Company name")
        self.search_url = QLineEdit(widget)
        self.search_url.setPlaceholderText("Search URL")
        self.add_button = QPushButton("+", widget)
        self.add_button.clicked.connect(self._add_table_entry)
        self.clear_button = QPushButton("Clear all", widget)
        self.clear_button.clicked.connect(self._clear_table)
        table_buttons_layout.addWidget(self.company_name, stretch=1)
        table_buttons_layout.addWidget(self.search_url, stretch=2)
        table_buttons_layout.addWidget(self.add_button)
        search_frame_layout.addLayout(table_buttons_layout)
        search_frame_layout.addWidget(self.clear_button)

        layout.addWidget(search_frame, stretch=1)

        start_button_layout = QHBoxLayout(widget)
        start_button_spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.start_button = QPushButton("Start", widget)
        self.start_button.clicked.connect(self._start_clicked)
        start_button_layout.addItem(start_button_spacer)
        start_button_layout.addWidget(self.start_button)
        layout.addLayout(start_button_layout)

    def _start_clicked(self):
        user = self.username.text()
        password = self.password.text()
        sleep_time = self.sleep.value()
        timeout = self.timeout.value()
        company_search: list[(str, str)] = []
        for row in range(self.search_table.rowCount()):
            row_data = []
            for column in range(self.search_table.columnCount()):
                item = self.search_table.item(row, column)
                row_data.append(item.text())
            company_search.append(tuple(row_data))

        output_filename, _ = QFileDialog.getSaveFileName(self, "Destination CSV", "", "CSV files (*.csv)")
        scraping_dialog = ScrapingDialog(user, password, sleep_time, timeout, company_search, output_filename, self)
        scraping_dialog.exec()

    def _add_table_entry(self):
        if not self.company_name.text() or not self.search_url.text():
            return
        row_count = self.search_table.rowCount()
        self.search_table.insertRow(row_count)
        self.search_table.setItem(row_count, 0, QTableWidgetItem(self.company_name.text()))
        self.search_table.setItem(row_count, 1, QTableWidgetItem(self.search_url.text()))
        self.company_name.clear()
        self.search_url.clear()

    def _clear_table(self):
        self.search_table.clearContents()
        self.search_table.setRowCount(0)

    def delete_entries(self):
        selected_rows = set(index.row() for index in self.table.selectedIndexes())
        for row in reversed(sorted(selected_rows)):
            self.table.removeRow(row)
