from sys import argv

from qtpy.QtCore import QAbstractTableModel
from qtpy.QtCore import QModelIndex
from qtpy.QtCore import QPersistentModelIndex
from qtpy.QtCore import Qt
from qtpy.QtGui import QBrush
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QApplication
from qtpy.QtWidgets import QTableView

T_INDEX = QModelIndex | QPersistentModelIndex


class Model(QAbstractTableModel):
    _data = list(range(101))

    def rowCount(self, _parent: T_INDEX = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, _parent: T_INDEX = QModelIndex()) -> int:
        return 1

    def data(
        self, index: T_INDEX, role: int = Qt.ItemDataRole.DisplayRole
    ) -> str | QBrush | None:
        row = index.row()

        if role == Qt.ItemDataRole.DisplayRole:
            max_, min_, val = max(self._data), min(self._data), self._data[row]

            perc = (val - min_) / (max_ - min_) if max_ != min_ else 0.5

            hue = int(perc * 120)  # 0..359 ; red=0, green=120

            return f'{self._data[row]} - {hue=}'

        if role == Qt.ItemDataRole.BackgroundRole:
            max_, min_, val = max(self._data), min(self._data), self._data[row]

            perc = (val - min_) / (max_ - min_) if max_ != min_ else 0.5

            hue = int(perc * 120)  # 0..359 ; red=0, green=120
            saturation = 223  # 0..255
            lightness = 159  # 0..255

            return QBrush(QColor.fromHsl(hue, saturation, lightness))

        return None


def main() -> None:
    app = QApplication(argv)

    model = Model()

    view = QTableView()
    view.setModel(model)
    view.show()

    app.exec()


if __name__ == '__main__':
    main()
