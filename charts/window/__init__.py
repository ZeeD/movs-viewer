import datetime
import decimal
import itertools
import typing

from PySide2.QtWidgets import QMainWindow
from PySide2.QtWidgets import QWidget


class MainWindow(QMainWindow):
    def __init__(self, widget: QWidget):
        super().__init__()
        self.setCentralWidget(widget)
