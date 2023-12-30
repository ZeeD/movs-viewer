from collections.abc import Iterable
from collections.abc import Sequence
from datetime import UTC
from datetime import date
from datetime import datetime
from datetime import time
from decimal import Decimal
from itertools import accumulate
from itertools import chain
from itertools import groupby
from os import environ
from typing import NamedTuple
from typing import cast
from typing import override

from movslib.model import Row
from movslib.movs import read_txt

if 'QT_API' not in environ:
    environ['QT_API'] = 'pyside6'


from qtpy.QtCharts import QBarCategoryAxis
from qtpy.QtCharts import QBarSeries
from qtpy.QtCharts import QBarSet
from qtpy.QtCharts import QCategoryAxis
from qtpy.QtCharts import QChart
from qtpy.QtCharts import QChartView
from qtpy.QtCharts import QLineSeries
from qtpy.QtCharts import QValueAxis
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGraphicsSceneMouseEvent
from qtpy.QtWidgets import QGraphicsSceneWheelEvent

ZERO = Decimal(0)


class Point(NamedTuple):
    data: date
    mov: Decimal


def to_point(row: Row) -> Point:
    if row.accrediti is not None:
        mov = row.accrediti
    elif row.addebiti is not None:
        mov = -row.addebiti
    else:
        mov = ZERO
    return Point(row.date, mov)


def build_series(
    data: Sequence[Row], epoch: date = date(2008, 1, 1)
) -> QLineSeries:
    data = sorted(data, key=lambda row: row.date)

    series = QLineSeries()
    series.setName('data')

    # add start and today
    moves = chain(
        (Point(epoch, ZERO),),
        map(to_point, data),
        (Point(datetime.now(tz=UTC).date(), ZERO),),
    )

    def sumy(a: Point, b: Point) -> Point:
        return Point(b.data, a.mov + b.mov)

    summes = accumulate(moves, func=sumy)

    floats = (
        (datetime.combine(data, time()).timestamp() * 1000, mov)
        for data, mov in summes
    )

    # step the movements
    last_mov: Decimal | None = None
    for ts, mov in floats:
        if last_mov is not None:
            series.append(ts, float(last_mov))
        series.append(ts, float(mov))
        last_mov = mov

    return series


def build_group_by_year_series(
    data: Sequence[Row],
) -> tuple[QBarSeries, QBarCategoryAxis]:
    data = sorted(data, key=lambda row: row.date)

    axis_x = QBarCategoryAxis()

    series = QBarSeries()
    # series.attachAxis(axis_x)
    barset = QBarSet('group by year')
    series.append(barset)

    def sum_points(points: Iterable[Point]) -> Decimal:
        return sum((point.mov for point in points), start=ZERO)

    years = []
    for year, points in groupby(
        map(to_point, data), lambda point: point.data.year
    ):
        barset.append(float(sum_points(points)))
        years.append(f'{year}')
    axis_x.setCategories(years)

    return series, axis_x


def build_group_by_month_series(
    data: Sequence[Row],
) -> tuple[QBarSeries, QBarCategoryAxis]:
    data = sorted(data, key=lambda row: row.date)

    axis_x = QBarCategoryAxis()

    series = QBarSeries()
    # series.attachAxis(axis_x)
    barset = QBarSet('group by month')
    series.append(barset)

    def sum_points(points: Iterable[Point]) -> Decimal:
        return sum((point.mov for point in points), start=ZERO)

    year_months = []
    for (year, month), points in groupby(
        map(to_point, data), lambda point: (point.data.year, point.data.month)
    ):
        barset.append(float(sum_points(points)))
        year_months.append(f'{year}-{month}')
    axis_x.setCategories(year_months)

    return series, axis_x


class Chart(QChart):
    def __init__(self, data: Sequence[Row]) -> None:
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
            return [
                date(year, month, 1)
                for year in range(start, end + 1)
                for month in range(1, 13, step)
            ]

        def reset_axis_x_labels() -> None:
            if True:
                pass

        def ts(d: date) -> float:
            return (
                datetime(d.year, d.month, d.day, tzinfo=UTC).timestamp() * 1000
            )

        # self.legend().setVisible(False)

        axis_y = QValueAxis()
        axis_y.setTickType(QValueAxis.TickType.TicksDynamic)
        axis_y.setTickAnchor(0.0)
        axis_y.setTickInterval(10000.0)
        axis_y.setMinorTickCount(9)
        self.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

        axis_x = QCategoryAxis()
        axis_x.setLabelsPosition(
            QCategoryAxis.AxisLabelsPosition.AxisLabelsPositionOnValue
        )
        for dt in months(data, 6):
            axis_x.append(f'{dt}', ts(dt))
        self.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)

        series = build_series(data)
        self.addSeries(series)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)

        group_by_year_series, axis_x_years = build_group_by_year_series(data)
        self.addSeries(group_by_year_series)
        self.addAxis(axis_x_years, Qt.AlignmentFlag.AlignBottom)
        group_by_year_series.attachAxis(axis_y)

        group_by_month_series, axis_x_months = build_group_by_month_series(data)
        self.addSeries(group_by_month_series)
        self.addAxis(axis_x_months, Qt.AlignmentFlag.AlignBottom)
        group_by_month_series.attachAxis(axis_y)

    @override
    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        super().wheelEvent(event)
        y = event.delta()
        if y < 0:
            self.zoom(0.75)  # zoomOut is ~ .5
        elif y > 0:
            self.zoomIn()

    @override
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mousePressEvent(event)
        event.accept()

    @override
    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mouseMoveEvent(event)

        x_curr, y_curr = cast(tuple[float, float], event.pos().toTuple())
        x_prev, y_prev = cast(tuple[float, float], event.lastPos().toTuple())
        self.scroll(x_prev - x_curr, y_curr - y_prev)


class ChartView(QChartView):
    def __init__(self, data_path: str) -> None:
        super().__init__()
        self.data_path = data_path
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.reload()

    def reload(self) -> None:
        _, data = read_txt(self.data_path)
        self.setChart(Chart(data))
