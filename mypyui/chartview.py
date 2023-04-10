from collections.abc import Iterable
from collections.abc import Sequence
from datetime import date
from datetime import datetime
from datetime import time
from decimal import Decimal
from itertools import accumulate
from itertools import chain
from itertools import groupby
from typing import cast
from typing import NamedTuple

from PySide6.QtCharts import QBarCategoryAxis
from PySide6.QtCharts import QBarSeries
from PySide6.QtCharts import QBarSet
from PySide6.QtCharts import QCategoryAxis
from PySide6.QtCharts import QChart
from PySide6.QtCharts import QChartView
from PySide6.QtCharts import QLineSeries
from PySide6.QtCharts import QValueAxis
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsSceneMouseEvent
from PySide6.QtWidgets import QGraphicsSceneWheelEvent

from movs import read_txt
from movs.model import Row

from .settings import Settings

ZERO = Decimal(0)


class Point(NamedTuple):
    data: date
    mov: Decimal


def toPoint(row: Row) -> Point:
    if row.accrediti is not None:
        mov = row.accrediti
    elif row.addebiti is not None:
        mov = -row.addebiti
    else:
        mov = ZERO
    return Point(row.date, mov)


def build_series(data: Sequence[Row],
                 epoch: date = date(2008, 1, 1)) -> QLineSeries:
    data = sorted(data, key=lambda row: row.date)

    series = QLineSeries()
    series.setName('data')

    # add start and today
    moves = chain((Point(epoch, ZERO),),
                  map(toPoint, data),
                  (Point(date.today(), ZERO),))

    def sumy(a: Point, b: Point) -> Point:
        return Point(b.data, a.mov + b.mov)

    summes = accumulate(moves, func=sumy)

    floats = ((datetime.combine(data, time()).timestamp() * 1000, mov)
              for data, mov in summes)

    # step the movements
    last_mov: Decimal | None = None
    for ts, mov in floats:
        if last_mov is not None:
            series.append(ts, float(last_mov))
        series.append(ts, float(mov))
        last_mov = mov

    return series


def build_group_by_year_series(data: Sequence[Row]) -> tuple[QBarSeries,
                                                             QBarCategoryAxis]:
    data = sorted(data, key=lambda row: row.date)

    axis_x = QBarCategoryAxis()

    series = QBarSeries()
    series.attachAxis(axis_x)
    barset = QBarSet('group by year')
    series.append(barset)

    def sum_points(points: Iterable[Point]) -> Decimal:
        return sum((point.mov for point in points), start=ZERO)

    years = []
    for year, points in groupby(map(toPoint, data),
                                lambda point: point.data.year):
        barset.append(float(sum_points(points)))
        years.append(f'{year}')
    axis_x.setCategories(years)

    return series, axis_x


def build_group_by_month_series(data: Sequence[Row]) -> tuple[QBarSeries,
                                                              QBarCategoryAxis]:
    data = sorted(data, key=lambda row: row.date)

    axis_x = QBarCategoryAxis()

    series = QBarSeries()
    series.attachAxis(axis_x)
    barset = QBarSet('group by month')
    series.append(barset)

    def sum_points(points: Iterable[Point]) -> Decimal:
        return sum((point.mov for point in points), start=ZERO)

    year_months = []
    for (year, month), points in groupby(map(toPoint, data),
                                         lambda point: (point.data.year,
                                                        point.data.month)):
        barset.append(float(sum_points(points)))
        year_months.append(f'{year}-{month}')
    axis_x.setCategories(year_months)

    return series, axis_x


class Chart(QChart):
    def __init__(self, data: Sequence[Row]):
        super().__init__()

        def years(data: Sequence[Row]) -> list[date]:
            if not data:
                return []
            data = sorted(data, key=lambda row: row.date)
            start = data[0].date.year - 1
            end = data[-1].date.year + 1
            return [date(year, 1, 1) for year in range(start, end + 1)]

        def months(data: Sequence[Row], step: int = 1) -> list[date]:
            if not data:
                return []
            data = sorted(data, key=lambda row: row.date)
            start = data[0].date.year - 1
            end = data[-1].date.year + 1
            return [date(year, month, 1)
                    for year in range(start, end + 1)
                    for month in range(1, 13, step)]

        def reset_axis_x_labels() -> None:
            if True:
                pass

        def ts(d: date) -> float:
            return datetime(d.year, d.month, d.day).timestamp() * 1000

        # self.legend().setVisible(False)

        axis_y = QValueAxis()
        axis_y.setTickType(QValueAxis.TickType.TicksDynamic)
        axis_y.setTickAnchor(0.)
        axis_y.setTickInterval(10000.)
        axis_y.setMinorTickCount(9)
        self.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

        axis_x = QCategoryAxis()
        axis_x.setLabelsPosition(QCategoryAxis.AxisLabelsPosition.AxisLabelsPositionOnValue)
        for dt in months(data, 6):
            axis_x.append(f'{dt}', ts(dt))
        self.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)

        series = build_series(data)
        self.addSeries(series)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)

        group_by_year_series, axis_x_years = build_group_by_year_series(data)
        self.addSeries(group_by_year_series)
        group_by_year_series.attachAxis(axis_y)
        self.addAxis(axis_x_years, Qt.AlignmentFlag.AlignBottom)

        group_by_month_series, axis_x_months = build_group_by_month_series(
            data)
        self.addSeries(group_by_month_series)
        group_by_month_series.attachAxis(axis_y)
        self.addAxis(axis_x_months, Qt.AlignmentFlag.AlignBottom)

    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        super().wheelEvent(event)
        y = event.delta()
        if y < 0:
            self.zoom(.75)  # zoomOut is ~ .5
        elif y > 0:
            self.zoomIn()

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mousePressEvent(event)
        event.accept()

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mouseMoveEvent(event)

        x_curr, y_curr = cast(tuple[float, float], event.pos().toTuple())
        x_prev, y_prev = cast(tuple[float, float], event.lastPos().toTuple())
        self.scroll(x_prev - x_curr, y_curr - y_prev)


class ChartView(QChartView):
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.reload()

    def reload(self) -> None:
        if self.settings.data_paths:
            _, data = read_txt(self.settings.data_paths[0])
        else:
            data = []
        self.setChart(Chart(data))
