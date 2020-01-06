import datetime
import decimal
import itertools
import logging
import sys
import typing

from PySide2.QtCharts import QtCharts
from PySide2.QtCore import QAbstractTableModel
from PySide2.QtCore import QModelIndex
from PySide2.QtCore import Qt
from PySide2.QtGui import QKeyEvent
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QAction, QVBoxLayout
from PySide2.QtWidgets import QApplication
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
        self.file_menu = self.menu.addMenu('File')

        # Exit QAction
        exit_action = QAction('Exit', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)

        self.file_menu.addAction(exit_action)

        # Status Bar
        self.status = self.statusBar()
        self.status.showMessage('Data loaded and plotted')


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


def build_series(data: typing.Sequence[typing.Tuple[datetime.date, decimal.Decimal]]):
    series = QtCharts.QLineSeries()

    # add start and today
    moves = itertools.chain(
        ((datetime.date(1990, 1, 1), decimal.Decimal(0)),),
        data,
        ((datetime.date.today(), decimal.Decimal(0)),)
    )

    def sumy(a: typing.Iterable[typing.Any],
             b: typing.Iterable[typing.Any]
             ) -> typing.Tuple[datetime.date, decimal.Decimal]:
        _a0, a1, *_ = a
        b0, b1, *_ = b
        return b0, a1 + b1

    summes = itertools.accumulate(moves, func=sumy)

    floats = ((datetime.datetime.combine(x, datetime.time()).timestamp() * 1000, y)
              for x, y in summes)

    # step the movements
    last_y = None
    for x, y in floats:
        if last_y is not None:
            series.append(x, last_y)
        series.append(x, y)
        last_y = y

    return series


class ChartView(QtCharts.QChartView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setRubberBand(QtCharts.QChartView.HorizontalRubberBand)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.modifiers() & Qt.ControlModifier:
            key = event.key()
            if key == Qt.Key_0:
                self.chart().zoomReset()
            elif key == Qt.Key_Plus:
                self.chart().zoomIn()
            elif key == Qt.Key_Minus:
                self.chart().zoomOut()
        super().keyPressEvent(event)


class Widget(QWidget):
    def __init__(self, data, t_headers):
        QWidget.__init__(self)

        # Getting the Model
        self.model = CustomTableModel(data, t_headers)

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

        self.series = build_series(data)
        self.chart = QtCharts.QChart()
        self.chart.addSeries(self.series)
        self.chart.legend().setVisible(False)
        self.chart_view = ChartView(self.chart)

        self.axis_x = QtCharts.QDateTimeAxis()
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.series.attachAxis(self.axis_x)
        self.axis_y = QtCharts.QValueAxis()
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_y)

        # QWidget Layout
        self.main_layout = QVBoxLayout()
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # Left layout
        size.setHorizontalStretch(1)
        self.table_view.setSizePolicy(size)
        self.main_layout.addWidget(self.table_view)
        self.main_layout.addWidget(self.chart_view)

        # Set the layout to the QWidget
        self.setLayout(self.main_layout)


def main():
    app = QApplication(sys.argv)
    window = MainWindow(Widget(
        (
            (datetime.date(2000, 1, 1), decimal.Decimal(5000)),
            (datetime.date(2000, 3, 1), decimal.Decimal(-2000)),
            (datetime.date(2001, 1, 1), decimal.Decimal(1000)),
            (datetime.date(2001, 2, 1), decimal.Decimal(-3000)),
            (datetime.date(2001, 3, 1), decimal.Decimal(10000)),
        ),
        ('...', 'movimenti', )
    ))
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
