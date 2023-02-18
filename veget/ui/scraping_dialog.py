# -*- coding: utf-8 -*-

import csv

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QWidget

from ..linkedin import LinkedIn, ProfileLink
from .console import Console


class ScrapingThread(QThread):
    finished = Signal()

    def __init__(self, username: str, password: str, sleep_: int, timeout: int, company_search: list[(str, str)],
                 ofile: str, label: QLabel, console: Console, progress_bar: QProgressBar):
        super().__init__()
        self.username: str = username
        self.password: str = password
        self.sleep_: int = sleep_
        self.timeout: int = timeout
        self.company_search: list[(str, str)] = company_search
        self.ofile: str = ofile
        self.label = label
        self.console = console
        self.progress_bar = progress_bar

    def run(self):
        with LinkedIn(self.username, self.password, sleep_time=self.sleep_, timeout=self.timeout) as li, \
                open(self.ofile, "w") as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow([
                "Company",
                "Employee Name",
                "Role",
                "Based On",
                "Start Date",
                "End Date"
            ])
            f.flush()

            for i, (company, search_url) in enumerate(self.company_search):
                self.label.setText(f"Scraping {company} profiles")
                profile_links: list[ProfileLink] = li.search(search_url)
                step = 100 / len(profile_links)
                self.console.log(f"{company} profiles ({len(profile_links)}) scraped")
                for profile_link in profile_links:
                    self.label.setText(f"Working on company {company}. Scraping profile '{profile_link.name}'")
                    profile = li.get_profile(profile_link)
                    self.console.log(f"Profile '{profile}')")
                    for experience in profile.experiences:
                        if company.lower() == experience.company.lower():
                            csv_writer.writerow([
                                company,
                                profile_link.name,
                                experience.position,
                                experience.location,
                                experience.start_date,
                                experience.end_date
                            ])
                            f.flush()
                    self.progress_bar.setValue(self.progress_bar.value() + step)
                self.progress_bar.setValue((i + 1) * 100)

        self.progress_bar.setValue(self.progress_bar.maximum())
        self.console.log("Scraping process finished")
        self.finished.emit()


class ScrapingDialog(QDialog):
    def __init__(self, username: str, password: str, sleep_: int, timeout: int, company_search: list[(str, str)],
                 ofile: str, parent: QWidget = None):
        super().__init__(parent)
        self.setWindowTitle("Scraping LinkedIn Profiles")
        self.username: str = username
        self.password: str = password
        self.sleep_: int = sleep_
        self.timeout: int = timeout
        self.company_search: list[(str, str)] = company_search
        self.ofile: str = ofile
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)

        action_label = QLabel("Starting scraping process", self)
        progress_bar = QProgressBar(self)
        console = Console(self)
        progress_bar.setMaximum(len(self.company_search) * 100)
        progress_bar.setMinimum(0)
        layout.addWidget(action_label)
        layout.addWidget(progress_bar)
        layout.addWidget(console)

        self.thread = ScrapingThread(self.username, self.password, self.sleep_, self.timeout, self.company_search,
                                     self.ofile, action_label, console, progress_bar)
        self.thread.start()
