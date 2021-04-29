from datetime import datetime
from decimal import Decimal

from PySide2.QtCharts import QtCharts
from PySide2.QtCore import QPointF
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QGraphicsSceneMouseEvent
from PySide2.QtWidgets import QGraphicsSceneWheelEvent

app = QApplication([__file__])


series = QtCharts.QLineSeries()
series.append(datetime(2000, 1, 1).timestamp() * 1000, Decimal(0))
series.append(datetime(2001, 1, 1).timestamp() * 1000, Decimal(100))
series.append(datetime(2001, 2, 1).timestamp() * 1000, Decimal(200))
series.append(datetime(2001, 2, 2).timestamp() * 1000, Decimal(150))
series.append(datetime(2001, 3, 1).timestamp() * 1000, Decimal(50))
series.append(datetime(2002, 1, 3).timestamp() * 1000, Decimal(250))


axis_x = QtCharts.QDateTimeAxis()

axis_y = QtCharts.QValueAxis()
axis_y.setTickType(QtCharts.QValueAxis.TicksDynamic)
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
chart.addAxis(axis_x, Qt.AlignBottom)
series.attachAxis(axis_x)
chart.addAxis(axis_y, Qt.AlignLeft)
series.attachAxis(axis_y)


chart_view = QtCharts.QChartView(chart)
chart_view.showMaximized()

app.exec_()
