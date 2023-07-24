from datetime import date
from datetime import datetime
from decimal import Decimal

from qtpy import QtCharts
from qtpy.QtCore import QPointF
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication
from qtpy.QtWidgets import QGraphicsSceneMouseEvent
from qtpy.QtWidgets import QGraphicsSceneWheelEvent

app = QApplication([__file__])


rows: list[tuple[date, Decimal]] = [
    (date(2000, 1, 1), Decimal(0)),
    (date(2001, 3, 13), Decimal(1000)),
    (date(2002, 2, 2), Decimal(2000)),
    (date(2005, 7, 4), Decimal(1500)),
    (date(2005, 11, 9), Decimal(500)),
    (date(2010, 4, 27), Decimal(2500))
]


def ts(d: date) -> float:
    return datetime(d.year, d.month, d.day).timestamp() * 1000


series = QtCharts.QLineSeries()
for dt, d in rows:
    series.append(ts(dt), float(d))


def years(rows: list[tuple[date, Decimal]]) -> list[date]:
    start_year = rows[0][0].year - 1
    end_year = rows[-1][0].year + 1
    return [date(year, 1, 1)
            for year in range(start_year, end_year + 1)]


# axis_x = QtCharts.QDateTimeAxis()
axis_x = QtCharts.QCategoryAxis()
axis_x.setLabelsPosition(QtCharts.QCategoryAxis.AxisLabelsPosition.AxisLabelsPositionOnValue)
for dt in years(rows):
    axis_x.append(f'{dt}', ts(dt))

axis_y = QtCharts.QValueAxis()
axis_y.setTickType(QtCharts.QValueAxis.TickType.TicksDynamic)
axis_y.setTickAnchor(0.)
axis_y.setTickInterval(100.)
axis_y.setMinorTickCount(9)


class Chart(QtCharts.QChart):
    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        y = event.delta()
        if y < 0:
            self.zoomOut()
        elif y > 0:
            self.zoomIn()
        super().wheelEvent(event)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        event.accept()

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        def t(pos: QPointF) -> tuple[float, float]:
            return pos.x(), pos.y()

        x_curr, y_curr = t(event.pos())
        x_prev, y_prev = t(event.lastPos())
        self.scroll(x_prev - x_curr, y_curr - y_prev)


chart = Chart()
chart.legend().setVisible(False)

chart.addSeries(series)
chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
series.attachAxis(axis_x)
chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
series.attachAxis(axis_y)


chart_view = QtCharts.QChartView(chart)
chart_view.showMaximized()

app.exec_()
