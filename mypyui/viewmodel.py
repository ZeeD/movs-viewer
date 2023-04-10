from dataclasses import fields
from datetime import date
from decimal import Decimal
from operator import iadd
from operator import isub
from typing import cast

from PySide6.QtCore import QAbstractTableModel
from PySide6.QtCore import QItemSelectionModel
from PySide6.QtCore import QModelIndex
from PySide6.QtCore import QObject
from PySide6.QtCore import QPersistentModelIndex
from PySide6.QtCore import QRegularExpression
from PySide6.QtCore import QSortFilterProxyModel
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QStatusBar

from movs import read_txt
from movs.model import Row

from .settings import Settings

FIELD_NAMES = [field.name for field in fields(Row)]

T_FIELDS = date | Decimal | None | str

ZERO = Decimal(0)


def _abs(row: Row) -> Decimal:
    if row.addebiti is not None:
        return -row.addebiti
    if row.accrediti is not None:
        return row.accrediti
    return ZERO


class ViewModel(QAbstractTableModel):
    def __init__(self, parent: QObject, data: list[Row]):
        super().__init__(parent)
        self._set_data(data)

    def _set_data(self, data: list[Row]) -> None:
        self._data = data
        abs_data = sorted([_abs(row) for row in data])
        self._min = abs_data[0] if abs_data else ZERO
        self._max = abs_data[-1] if abs_data else ZERO

    def rowCount(self, _parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, _parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        return len(FIELD_NAMES)

    def headerData(
            self,
            section: int,
            orientation: Qt.Orientation,
            role: int = Qt.ItemDataRole.DisplayRole) -> str | None:
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation != Qt.Orientation.Horizontal:
            return None

        return FIELD_NAMES[section]

    def data(self,
             index: QModelIndex | QPersistentModelIndex,
             role: int = Qt.ItemDataRole.DisplayRole) -> T_FIELDS | QBrush | None:
        column = index.column()
        row = index.row()

        if role == Qt.ItemDataRole.DisplayRole:
            return str(getattr(self._data[row], FIELD_NAMES[column]))

        if role == Qt.ItemDataRole.BackgroundRole:
            abs_value = _abs(self._data[row])
            perc = float((abs_value - self._min) / (self._max - self._min))

            red = int((1 - perc) * 255)  # 0..1 ->  255..0
            green = int(perc * 255)  # 0..1 -> 0..255
            blue = int((.5 - abs(perc - .5)) * 511)  # 0..0.5..1 -> 0..255..0

            return QBrush(QColor(red, green, blue, 127))

        if role == Qt.ItemDataRole.UserRole:
            return cast(T_FIELDS, getattr(self._data[row],
                                          FIELD_NAMES[column]))

        return None

    def sort(
            self,
            index: int,
            order: Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None:
        def key(row: Row) -> date | Decimal | str:  # T_FIELDS - None
            e: T_FIELDS = getattr(row, FIELD_NAMES[index])
            if e is None:
                return ZERO
            return e

        self.layoutAboutToBeChanged.emit()
        try:
            self._data.sort(key=key, reverse=order ==
                            Qt.SortOrder.DescendingOrder)
        finally:
            self.layoutChanged.emit()

    def load(self, data: list[Row]) -> None:
        self.beginResetModel()
        try:
            self._set_data(data)
        finally:
            self.endResetModel()


class SortFilterViewModel(QSortFilterProxyModel):
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self.settings = settings
        self.setSourceModel(ViewModel(self, []))
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setDynamicSortFilter(True)

    def filterAcceptsRow(self,
                         source_row: int,
                         source_parent: QModelIndex | QPersistentModelIndex) -> bool:
        regex = self.filterRegularExpression()
        source_model = self.sourceModel()
        column_count = source_model.columnCount(source_parent)

        return any(regex.match(source_model.data(index)).hasMatch()
                   for index in (source_model.index(source_row,
                                                    i,
                                                    source_parent)
                                 for i in range(column_count)))

    def filterChanged(self, text: str) -> None:
        text = QRegularExpression.escape(text)
        options = QRegularExpression.PatternOption.CaseInsensitiveOption
        self.setFilterRegularExpression(QRegularExpression(text, options))

    def sort(self,
             column: int,
             order: Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None:
        self.sourceModel().sort(column, order)

    def selectionChanged(self,
                         selection_model: QItemSelectionModel,
                         statusbar: QStatusBar) -> None:

        addebiti_index = FIELD_NAMES.index('addebiti')
        accrediti_index = FIELD_NAMES.index('accrediti')

        bigsum = 0
        for column, iop in ((addebiti_index, isub), (accrediti_index, iadd)):
            for index in selection_model.selectedRows(column):
                data = index.data(Qt.ItemDataRole.UserRole)
                if data is not None:
                    bigsum = iop(bigsum, data)

        statusbar.showMessage(f'⅀ = {bigsum}')

    def reload(self) -> None:
        if self.settings.data_paths:
            _, data = read_txt(self.settings.data_paths[0])
        else:
            data = []
        cast(ViewModel, self.sourceModel()).load(data)
