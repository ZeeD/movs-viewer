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

import charts
import model


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
        self.model = model.CustomTableModel(data, t_headers)

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

        self.series = charts.build_series(data)
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
