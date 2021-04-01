from dataclasses import fields
from datetime import date
from decimal import Decimal
from typing import List
from typing import Optional
from typing import Union

from movs.model import Row
from PySide2.QtCore import QAbstractTableModel
from PySide2.QtCore import QModelIndex
from PySide2.QtCore import QObject
from PySide2.QtCore import QRegExp
from PySide2.QtCore import QSortFilterProxyModel
from PySide2.QtCore import Qt
from PySide2.QtGui import QBrush, QColor

FIELD_NAMES = [field.name for field in fields(Row)]

T_FIELDS = Union[date, Optional[Decimal], str]

ZERO = Decimal(0)


def _abs(row: Row) -> Decimal:
    if row.addebiti is not None:
        return -row.addebiti
    if row.accrediti is not None:
        return row.accrediti
    return ZERO


class ViewModel(QAbstractTableModel):
    def __init__(self, parent: QObject, data: List[Row]):
        super().__init__(parent)
        self._data = data
        abs_data = [_abs(row) for row in data]
        abs_data.sort()
        self._min = abs_data[0]
        self._max = abs_data[-1]

    def rowCount(self, _parent: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, _parent: QModelIndex = QModelIndex()) -> int:
        return len(FIELD_NAMES)

    def headerData(
            self,
            section: int,
            orientation: Qt.Orientation,
            role: int = Qt.DisplayRole) -> Optional[str]:
        if role != Qt.DisplayRole:
            return None

        if orientation != Qt.Horizontal:
            return None

        return FIELD_NAMES[section]

    def data(self,
             index: QModelIndex,
             role: int = Qt.DisplayRole) -> Optional[T_FIELDS]:
        column = index.column()
        row = index.row()

        if role == Qt.DisplayRole:
            return str(getattr(self._data[row], FIELD_NAMES[column]))

        if role == Qt.BackgroundRole:
            abs_value = _abs(self._data[row])
            perc = float((abs_value - self._min) / (self._max - self._min))

            red = int((1 - perc) * 255)  # 0..1 ->  255..0
            green = int(perc * 255)  # 0..1 -> 0..255
            blue = int((.5 - abs(perc - .5)) * 511)  # 0..0.5..1 -> 0..255..0

            return QBrush(QColor(red, green, blue, 127))

        return None

    def sort(self, index: int, order: Qt.SortOrder = Qt.AscendingOrder) -> None:
        def key(row: Row) -> Union[date, Decimal, str]:  # T_FIELDS - None
            e: T_FIELDS = getattr(row, FIELD_NAMES[index])
            if e is None:
                return ZERO
            return e

        self.layoutAboutToBeChanged.emit()
        try:
            self._data.sort(key=key, reverse=order == Qt.DescendingOrder)
        finally:
            self.layoutChanged.emit()


class SortFilterViewModel(QSortFilterProxyModel):
    def __init__(self, parent: QObject, data: List[Row]) -> None:
        super().__init__(parent)
        self.setSourceModel(ViewModel(self, data))
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.setSortCaseSensitivity(Qt.CaseInsensitive)
        self.setDynamicSortFilter(True)

    def filterAcceptsRow(
            self,
            source_row: int,
            source_parent: QModelIndex) -> bool:
        regex = self.filterRegExp()
        source_model = self.sourceModel()
        column_count = source_model.columnCount(source_parent)
        return any(regex.indexIn(source_model.data(index)) != -1
                   for index in (source_model.index(source_row, i, source_parent)
                                 for i in range(column_count)))

    def filter_changed(self, text: str) -> None:
        self.setFilterRegExp(
            QRegExp(
                text,
                Qt.CaseInsensitive,
                QRegExp.FixedString))

    def sort(self, column: int, order: Qt.SortOrder = Qt.AscendingOrder) -> None:
        self.sourceModel().sort(column, order)
