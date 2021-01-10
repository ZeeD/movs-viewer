import typing

from PySide2 import QtCharts
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

import movs

from . import util


class Chart(QtCharts.QtCharts.QChart):
    def __init__(self,
                 parent: QtWidgets.QGraphicsItem,
                 data: typing.Iterable[movs.model.Row]
                 ) -> None:
        super().__init__(parent)
        self.legend().setVisible(False)

        series = util.build_series(data)
        self.addSeries(series)

        axis_x = QtCharts.QtCharts.QDateTimeAxis()
        self.addAxis(axis_x, QtCore.Qt.AlignBottom)
        series.attachAxis(self.axis_x)

        axis_y = QtCharts.QtCharts.QValueAxis()
        self.addAxis(axis_y, QtCore.Qt.AlignLeft)
        series.attachAxis(axis_y)


class ChartView(QtCharts.QtCharts.QChartView):
    def __init__(self,
                 parent: QtWidgets.QWidget,
                 data: typing.Iterable[movs.model.Row]
                 ) -> None:
        super().__init__(Chart(self, data), parent)
        self.setRubberBand(QtCharts.QtCharts.QChartView.HorizontalRubberBand)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.modifiers() & QtCore.Qt.ControlModifier:
            key = event.key()
            if key == QtCore.Qt.Key_0:
                self.chart().zoomReset()
            elif key == QtCore.Qt.Key_Plus:
                self.chart().zoomIn()
            elif key == QtCore.Qt.Key_Minus:
                self.chart().zoomOut()
        super().keyPressEvent(event)
