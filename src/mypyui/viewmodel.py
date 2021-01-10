import dataclasses
import datetime
import decimal
import math
import typing

from PySide2 import QtCore

from movs import model
import movs


FIELD_NAMES = [field.name for field in dataclasses.fields(movs.model.Row)]

T_FIELDS = typing.Union[datetime.date, decimal.Decimal, str]


class ViewModel(QtCore.QAbstractTableModel):
    def __init__(self,
                 parent: QtCore.QObject,
                 data: typing.Iterable[movs.model.Row]):
        super().__init__(parent)
        self._data = [tuple(getattr(row, name) for name in FIELD_NAMES)
                      for row in data]

    def rowCount(self, _parent: QtCore.QModelIndex=QtCore.QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, _parent: QtCore.QModelIndex=QtCore.QModelIndex()) -> int:
        return len(FIELD_NAMES)

    def headerData(self,
                   section: int,
                   orientation: QtCore.Qt.Orientation,
                   role: int=QtCore.Qt.DisplayRole
                   ) -> typing.Optional[str]:
        if role != QtCore.Qt.DisplayRole:
            return None

        if orientation != QtCore.Qt.Horizontal:
            return None

        return FIELD_NAMES[section]

    def data(self,
             index: QtCore.QModelIndex,
             role: int= QtCore.Qt.DisplayRole
             ) -> typing.Optional[str]:
        column = index.column()
        row = index.row()

        if role == QtCore.Qt.DisplayRole:
            return f'{self._data[row][column]}'

        return None

    def sort(self, index: int, order: QtCore.Qt.SortOrder=QtCore.Qt.AscendingOrder)->None:
        def key(row: typing.Tuple[typing.Union[T_FIELDS, None], ...]
                ) -> typing.Union[T_FIELDS, float]:
            e = row[index]
            if e is None:
                return math.inf
            return e

        self.layoutAboutToBeChanged.emit()
        try:
            self._data.sort(key=key,
                            reverse=order == QtCore.Qt.DescendingOrder)
        finally:
            self.layoutChanged.emit()


class SortFilterViewModel(QtCore.QSortFilterProxyModel):
    def __init__(self,
                 parent: QtCore.QObject,
                 data: typing.Iterable[model.Row]
                 ) -> None:
        super().__init__(parent)
        self.setSourceModel(ViewModel(self, data))
        self.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setSortCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setDynamicSortFilter(True)

    def filterAcceptsRow(self,
                         source_row: int,
                         source_parent: QtCore.QModelIndex
                         ) -> bool:
        regex = self.filterRegExp()
        source_model = self.sourceModel()
        column_count = source_model.columnCount(source_parent)
        return any(regex.indexIn(source_model.data(index)) != -1
                   for index in (source_model.index(source_row, i, source_parent)
                                 for i in range(column_count)))

    def filter_changed(self, text: str) -> None:
        self.setFilterRegExp(QtCore.QRegExp(text,
                                            QtCore.Qt.CaseInsensitive,
                                            QtCore.QRegExp.FixedString))
