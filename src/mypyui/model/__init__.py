import dataclasses
import datetime
import decimal
import itertools
import math
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

import movs


FIELD_NAMES = [field.name for field in dataclasses.fields(movs.model.Row)]

T_FIELDS = typing.Union[datetime.date, decimal.Decimal, str]


class CustomTableModel(QAbstractTableModel):

    def __init__(self,
                 data: typing.Iterable[movs.model.Row]):
        QAbstractTableModel.__init__(self)
        self._data = [tuple(getattr(row, name) for name in FIELD_NAMES)
                      for row in data]

    def rowCount(self, _parent: QModelIndex=QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, _parent: QModelIndex=QModelIndex()) -> int:
        return len(FIELD_NAMES)

    def headerData(self,
                   section: int,
                   orientation: Qt.Orientation,
                   role: int=Qt.DisplayRole
                   ) -> typing.Optional[str]:
        if role != Qt.DisplayRole:
            return None

        if orientation != Qt.Horizontal:
            return None

        return FIELD_NAMES[section]

    def data(self,
             index: QModelIndex,
             role: int= Qt.DisplayRole
             ) -> typing.Optional[str]:
        column = index.column()
        row = index.row()

        if role == Qt.DisplayRole:
            return f'{self._data[row][column]}'

        return None

    def sort(self, index: int, order: Qt.SortOrder=Qt.AscendingOrder)->None:
        def key(row: typing.Tuple[typing.Union[T_FIELDS, None], ...]
                ) -> typing.Union[T_FIELDS, float]:
            e = row[index]
            if e is None:
                return math.inf
            return e

        self.layoutAboutToBeChanged.emit()
        try:
            self._data.sort(key=key,
                            reverse=order == Qt.DescendingOrder)
        finally:
            self.layoutChanged.emit()
