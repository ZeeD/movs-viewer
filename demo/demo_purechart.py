from datetime import UTC
from datetime import date
from datetime import datetime
from decimal import Decimal
from sys import argv
from typing import override

from PySide6.QtCharts import QChart
from PySide6.QtCharts import QChartView
from PySide6.QtCharts import QDateTimeAxis
from PySide6.QtCharts import QLineSeries
from PySide6.QtCharts import QValueAxis
from PySide6.QtCore import QDateTime
from PySide6.QtCore import QPointF
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QGraphicsSceneMouseEvent
from PySide6.QtWidgets import QGraphicsSceneWheelEvent


def dt(year: int) -> QDateTime:
    return QDateTime(year, 1, 1, 0, 0, 0)


def ts(d: date) -> float:
    return datetime(d.year, d.month, d.day, tzinfo=UTC).timestamp() * 1000


def years(rows: list[tuple[date, Decimal]]) -> list[date]:
    start_year = rows[0][0].year - 1
    end_year = rows[-1][0].year + 1
    return [date(year, 1, 1) for year in range(start_year, end_year + 1)]


class Chart(QChart):
    @override
    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        y = event.delta()
        if y < 0:
            self.zoomOut()
        elif y > 0:
            self.zoomIn()
        super().wheelEvent(event)

    @override
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        event.accept()

    @override
    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        def t(pos: QPointF) -> tuple[float, float]:
            return pos.x(), pos.y()

        x_curr, y_curr = t(event.pos())
        x_prev, y_prev = t(event.lastPos())
        self.scroll(x_prev - x_curr, y_curr - y_prev)


def demo_purechart(rows: list[tuple[date, Decimal]]) -> QChartView:
    chart = Chart()
    chart.legend().setVisible(False)

    #    axis_x = QCategoryAxis()
    #    axis_x.setLabelsPosition(
    #        QCategoryAxis.AxisLabelsPosition.AxisLabelsPositionOnValue
    #    )
    #    for dt in years(rows):
    #        axis_x.append(f'{dt}', ts(dt))
    #    chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
    axis_x = QDateTimeAxis()
    axis_x.setFormat('dd/MM/yyyy')
    axis_x.setTickCount(13)
    axis_x.setRange(dt(1999), dt(2011))
    chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)

    axis_y = QValueAxis()
    axis_y.setTickType(QValueAxis.TickType.TicksDynamic)
    axis_y.setTickAnchor(0.0)
    axis_y.setTickInterval(100.0)
    axis_y.setMinorTickCount(9)
    chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

    series = QLineSeries()
    for when, howmuch in rows:
        series.append(ts(when), float(howmuch))
    chart.addSeries(series)
    series.attachAxis(axis_x)
    series.attachAxis(axis_y)

    return QChartView(chart)


def main() -> None:
    rows = [
        (date(2000, 1, 1), Decimal(0)),
        (date(2001, 3, 13), Decimal(1000)),
        (date(2002, 2, 2), Decimal(2000)),
        (date(2005, 7, 4), Decimal(1500)),
        (date(2005, 11, 9), Decimal(500)),
        (date(2010, 4, 27), Decimal(2500)),
    ]

    a = QApplication(argv)

    chart_view = demo_purechart(rows)
    chart_view.showMaximized()

    raise SystemExit(a.exec())


if __name__ == '__main__':
    main()
