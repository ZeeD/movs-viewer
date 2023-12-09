from dataclasses import fields
from datetime import date
from decimal import Decimal
from operator import iadd
from operator import isub
from typing import cast

from movs.movs import read_txt
from movs.model import ZERO
from movs.model import Row
from qtpy.QtCore import QAbstractTableModel
from qtpy.QtCore import QItemSelectionModel
from qtpy.QtCore import QModelIndex
from qtpy.QtCore import QObject
from qtpy.QtCore import QPersistentModelIndex
from qtpy.QtCore import QRegularExpression
from qtpy.QtCore import QSortFilterProxyModel
from qtpy.QtCore import Qt
from qtpy.QtGui import QBrush
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QStatusBar

from settings import Settings

FIELD_NAMES = [field.name for field in fields(Row)]

T_FIELDS = date | Decimal | None | str


def _abs(row: Row) -> Decimal:
    if row.addebiti is not None:
        return -row.addebiti
    if row.accrediti is not None:
        return row.accrediti
    return ZERO


T_INDEX = QModelIndex | QPersistentModelIndex


class ViewModel(QAbstractTableModel):
    def __init__(self, parent: QObject, data: list[Row]):
        super().__init__(parent)
        self._set_data(data)

    def _set_data(self, data: list[Row]) -> None:
        self._data = data
        abs_data = sorted([_abs(row) for row in data])
        self._min = abs_data[0] if abs_data else ZERO
        self._max = abs_data[-1] if abs_data else ZERO

    def rowCount(self, _parent: T_INDEX = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, _parent: T_INDEX = QModelIndex()) -> int:
        return len(FIELD_NAMES)

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> str | None:
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation != Qt.Orientation.Horizontal:
            return None

        return FIELD_NAMES[section]

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> T_FIELDS | QBrush | None:
        column = index.column()
        row = index.row()

        if role == Qt.ItemDataRole.DisplayRole:
            return str(getattr(self._data[row], FIELD_NAMES[column]))

        if role == Qt.ItemDataRole.BackgroundRole:
            max_, min_, val = self._max, self._min, _abs(self._data[row])
            perc = (
                (val - min_) / (max_ - min_) if max_ != min_ else Decimal(0.5)
            )

            hue = int(perc * 120)  # 0..359 ; red=0, green=120
            saturation = 223  # 0..255
            lightness = 159  # 0..255

            return QBrush(QColor.fromHsl(hue, saturation, lightness))

        if role == Qt.ItemDataRole.UserRole:
            return cast(T_FIELDS, getattr(self._data[row], FIELD_NAMES[column]))

        return None

    def sort(
        self, index: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder
    ) -> None:
        def key(row: Row) -> date | Decimal | str:  # T_FIELDS - None
            e: T_FIELDS = getattr(row, FIELD_NAMES[index])
            if e is None:
                return ZERO
            return e

        self.layoutAboutToBeChanged.emit()
        try:
            self._data.sort(
                key=key, reverse=order == Qt.SortOrder.DescendingOrder
            )
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

    def filterAcceptsRow(
        self,
        source_row: int,
        source_parent: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        regex = self.filterRegularExpression()
        source_model = self.sourceModel()
        column_count = source_model.columnCount(source_parent)

        return any(
            regex.match(source_model.data(index)).hasMatch()
            for index in (
                source_model.index(source_row, i, source_parent)
                for i in range(column_count)
            )
        )

    def filterChanged(self, text: str) -> None:
        text = QRegularExpression.escape(text)
        options = QRegularExpression.PatternOption.CaseInsensitiveOption
        self.setFilterRegularExpression(QRegularExpression(text, options))

    def sort(
        self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder
    ) -> None:
        self.sourceModel().sort(column, order)

    def selectionChanged(
        self, selection_model: QItemSelectionModel, statusbar: QStatusBar
    ) -> None:
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