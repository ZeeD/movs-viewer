from datetime import date
from datetime import datetime
from datetime import time
from decimal import Decimal
from itertools import accumulate
from itertools import chain
from typing import List
from typing import Optional
from typing import Tuple

from movs.model import Row
from PySide2.QtCharts import QtCharts
from PySide2.QtCore import Qt
from PySide2.QtGui import QKeyEvent
from PySide2.QtGui import QWheelEvent
from PySide2.QtWidgets import QWidget

ZERO = Decimal(0)


def build_series(
        data: List[Row],
        epoch: date = date(2008, 1, 1)) -> QtCharts.QLineSeries:
    data = sorted(data, key=lambda row: row.data_valuta)

    series = QtCharts.QLineSeries()

    def toTuple(row: Row) -> Tuple[date, Decimal]:
        if row.accrediti is not None:
            mov = row.accrediti
        elif row.addebiti is not None:
            mov = - row.addebiti
        else:
            mov = ZERO
        return (row.data_valuta, mov)

    # add start and today
    moves = chain(
        ((epoch, ZERO),),
        map(toTuple, data),
        ((date.today(), ZERO),))

    def sumy(a: Tuple[date, Decimal], b: Tuple[date, Decimal]
             ) -> Tuple[date, Decimal]:
        _a0, a1 = a
        b0, b1 = b
        return b0, a1 + b1

    summes = accumulate(moves, func=sumy)

    floats = ((datetime.combine(x, time()).timestamp() * 1000, y)
              for x, y in summes)

    # step the movements
    last_y: Optional[Decimal] = None
    for x, y in floats:
        if last_y is not None:
            series.append(x, last_y)
        series.append(x, y)
        last_y = y

    return series


class Chart(QtCharts.QChart):
    def __init__(self, data: List[Row]):
        super().__init__()
        self.legend().setVisible(False)

        series = build_series(data)
        self.addSeries(series)

        axis_x = QtCharts.QDateTimeAxis()
        self.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QtCharts.QValueAxis()
        axis_y.setTickType(QtCharts.QValueAxis.TicksDynamic)
        axis_y.setTickAnchor(0.)
        axis_y.setTickInterval(10000.)
        axis_y.setMinorTickCount(9)
        self.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)


class ChartView(QtCharts.QChartView):
    def __init__(self, parent: QWidget, data: List[Row]):
        super().__init__(Chart(data), parent)
        self.setRubberBand(QtCharts.QChartView.HorizontalRubberBand)
        self.setCursor(Qt.CrossCursor)

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

    def wheelEvent(self, event: QWheelEvent) -> None:
        y = event.angleDelta().y()
        if y < 0:
            self.chart().zoomOut()
        elif y > 0:
            self.chart().zoomIn()
        super().wheelEvent(event)

    def load(self, data: List[Row]) -> None:
        self.setChart(Chart(data))
