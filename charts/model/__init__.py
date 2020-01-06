import datetime
import decimal
import itertools
import typing

from PySide2.QtCharts import QtCharts
from PySide2.QtCore import QAbstractTableModel
from PySide2.QtCore import QModelIndex
from PySide2.QtCore import Qt
from PySide2.QtGui import QKeyEvent
from PySide2.QtWidgets import QHeaderView
from PySide2.QtWidgets import QSizePolicy
from PySide2.QtWidgets import QTableView
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QWidget


class CustomTableModel(QAbstractTableModel):
    def __init__(self,
                 data: typing.Iterable[typing.Sequence[typing.Any]],
                 headers: typing.Iterable[str]):
        QAbstractTableModel.__init__(self)
        self._data = data
        self._headers = headers

    def rowCount(self, _parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, _parent=QModelIndex()):
        return len(self._headers)

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None

        if orientation != Qt.Horizontal:
            return None

        return self._headers[section]

    def data(self, index, role=Qt.DisplayRole):
        column = index.column()
        row = index.row()

        if role == Qt.DisplayRole:
            return f'{self._data[row][column]}'

        return None
