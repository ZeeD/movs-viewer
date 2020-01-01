import datetime
import logging
import random
import sys
import typing

from PySide2.QtCharts import QtCharts
from PySide2.QtCore import QAbstractTableModel
from PySide2.QtCore import QModelIndex
from PySide2.QtCore import Qt
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QAction
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QHeaderView
from PySide2.QtWidgets import QMainWindow
from PySide2.QtWidgets import QSizePolicy
from PySide2.QtWidgets import QTableView
from PySide2.QtWidgets import QWidget


class MainWindow(QMainWindow):
    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.setCentralWidget(widget)

        # Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        # Exit QAction
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)

        self.file_menu.addAction(exit_action)

        # Status Bar
        self.status = self.statusBar()
        self.status.showMessage("Data loaded and plotted")


class CustomTableModel(QAbstractTableModel):
    def __init__(self,
                 data: typing.Iterable[typing.Iterable[typing.Any]],
                 t_headers: typing.Iterable[str],
                 l_headers: typing.Iterable[str]):
        QAbstractTableModel.__init__(self)
        self._data = data
        self._t_headers = t_headers
        self._l_headers = l_headers

    def rowCount(self, _parent=QModelIndex()):
        return len(self._l_headers)

    def columnCount(self, _parent=QModelIndex()):
        return len(self._t_headers)

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            try:
                return self._t_headers[section]
            except IndexError:
                logging.exception("%r[%r]", self._t_headers, section)

        try:
            return self._l_headers[section]
        except IndexError:
            logging.exception("%r[%r]", self._l_headers, section)

    def data(self, index, role=Qt.DisplayRole):
        column = index.column()
        row = index.row()

        if role == Qt.DisplayRole:
            try:
                return f"{self._data[row][column]}"
            except IndexError:
                logging.exception("%r[%r][%r]", self._data, row, column)

        return None


def build_series():
    series = QtCharts.QLineSeries()
    series.setName('name')

    # Filling QLineSeries
    def data():
        for i in range(10):
            x = (datetime.datetime.now() +
                 datetime.timedelta(hours=i)).timestamp() * 1000
            y = i * random.random()
            yield x, y

    # step the data

    last_y = None
    for x, y in data():
        if last_y is not None:
            series.append(x, last_y)
        series.append(x, y)
        last_y = y

    return series


class Widget(QWidget):
    def __init__(self, data, t_headers, l_headers):
        QWidget.__init__(self)

        # Getting the Model
        self.model = CustomTableModel(data, t_headers, l_headers)

        # Creating a QTableView
        self.table_view = QTableView()
        self.table_view.setModel(self.model)

        # QTableView Headers
        self.horizontal_header = self.table_view.horizontalHeader()
        self.vertical_header = self.table_view.verticalHeader()
        self.horizontal_header.setSectionResizeMode(
            QHeaderView.ResizeToContents)
        self.vertical_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontal_header.setStretchLastSection(True)

        self.series = build_series()
        self.chart = QtCharts.QChart()
        self.chart.addSeries(self.series)
        self.chart_view = QtCharts.QChartView(self.chart)

        self.axis_x = QtCharts.QDateTimeAxis()
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.series.attachAxis(self.axis_x)
        self.axis_y = QtCharts.QValueAxis()
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_y)

        # QWidget Layout
        self.main_layout = QHBoxLayout()
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # Left layout
        size.setHorizontalStretch(1)
        self.table_view.setSizePolicy(size)
#        self.main_layout.addWidget(self.table_view)
        self.main_layout.addWidget(self.chart_view)

        # Set the layout to the QWidget
        self.setLayout(self.main_layout)


def main():
    app = QApplication(sys.argv)
    window = MainWindow(Widget(((1, 2, 3), (4, 5, 6), (7, 8, 9), (10, 11, 12)),
                               ("nomi", "cose", "città"),
                               ("gen", "feb", "mar", "apr")))
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
