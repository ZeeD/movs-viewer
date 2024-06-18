from datetime import UTC
from datetime import date
from datetime import datetime
from datetime import time
from decimal import Decimal
from itertools import accumulate
from itertools import chain
from itertools import groupby
from os import environ
from typing import TYPE_CHECKING
from typing import NamedTuple
from typing import cast
from typing import override

from guilib.chartwidget.chartwidget import ChartWidget
from guilib.chartwidget.modelgui import SeriesModel
from guilib.chartwidget.modelgui import SeriesModelUnit
from guilib.chartwidget.viewmodel import SortFilterViewModel
from guilib.dates.converters import date2days
from guilib.dates.converters import date2QDateTime
from movslib.model import ZERO
from movslib.movs import read_txt

if 'QT_API' not in environ:
    environ['QT_API'] = 'pyside6'

from qtpy.QtCharts import QBarCategoryAxis
from qtpy.QtCharts import QBarSeries
from qtpy.QtCharts import QBarSet
from qtpy.QtCharts import QCategoryAxis
from qtpy.QtCharts import QChart
from qtpy.QtCharts import QLineSeries
from qtpy.QtCharts import QValueAxis
from qtpy.QtCore import Qt

if TYPE_CHECKING:
    from collections.abc import Iterable
    from collections.abc import Sequence

    from guilib.chartwidget.model import Column
    from guilib.chartwidget.model import ColumnHeader
    from guilib.chartwidget.model import Info
    from movslib.model import Row
    from qtpy.QtWidgets import QGraphicsSceneMouseEvent
    from qtpy.QtWidgets import QGraphicsSceneWheelEvent


class Point(NamedTuple):
    data: date
    mov: Decimal


def to_point(row: 'Row') -> Point:
    if row.accrediti is not None:
        mov = row.accrediti
    elif row.addebiti is not None:
        mov = -row.addebiti
    else:
        mov = ZERO
    return Point(row.date, mov)


def build_series(
    data: 'Sequence[Row]', epoch: date = date(2008, 1, 1)
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
    data: 'Sequence[Row]',
) -> tuple[QBarSeries, QBarCategoryAxis]:
    data = sorted(data, key=lambda row: row.date)

    axis_x = QBarCategoryAxis()

    series = QBarSeries()
    barset = QBarSet('group by year')
    series.append(barset)

    def sum_points(points: 'Iterable[Point]') -> Decimal:
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
    data: 'Sequence[Row]',
) -> tuple[QBarSeries, QBarCategoryAxis]:
    data = sorted(data, key=lambda row: row.date)

    axis_x = QBarCategoryAxis()

    series = QBarSeries()
    barset = QBarSet('group by month')
    series.append(barset)

    def sum_points(points: 'Iterable[Point]') -> Decimal:
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
    def __init__(self, data: 'Sequence[Row]') -> None:
        super().__init__()

        def years(data: 'Sequence[Row]') -> list[date]:
            if not data:
                return []
            data = sorted(data, key=lambda row: row.date)
            start = data[0].date.year - 1
            end = data[-1].date.year + 1
            return [date(year, 1, 1) for year in range(start, end + 1)]

        def months(data: 'Sequence[Row]', step: int = 1) -> list[date]:
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
    def wheelEvent(self, event: 'QGraphicsSceneWheelEvent') -> None:
        super().wheelEvent(event)
        y = event.delta()
        if y < 0:
            self.zoom(0.75)  # zoomOut is ~ .5
        elif y > 0:
            self.zoomIn()

    @override
    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        super().mousePressEvent(event)
        event.accept()

    @override
    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        super().mouseMoveEvent(event)

        x_curr, y_curr = cast(tuple[float, float], event.pos().toTuple())
        x_prev, y_prev = cast(tuple[float, float], event.lastPos().toTuple())
        self.scroll(x_prev - x_curr, y_curr - y_prev)


class CH:
    def __init__(self, name: str) -> None:
        self.name = name

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CH):
            return NotImplemented
        return self.name == other.name


class C:
    def __init__(
        self, header: 'ColumnHeader', howmuch: 'Decimal | None'
    ) -> None:
        self.header = header
        self.howmuch = howmuch


class I:  # noqa: E742
    def __init__(self, when: 'date', columns: 'list[Column]') -> None:
        self.when = when
        self.columns = columns

    def howmuch(self, column_header: 'ColumnHeader') -> 'Decimal | None':
        for column in self.columns:
            if column.header == column_header:
                return column.howmuch
        return None


MONEY_HEADER = CH('money')


def series_model_factory(infos: 'list[Info]') -> 'SeriesModel':
    """Extract money from info; accumulate and step; group by month / year."""
    x_min = date.max
    x_max = date.min
    y_min = Decimal('inf')
    y_max = -Decimal('inf')

    money = QLineSeries()
    money.setName('money')
    money_acc = QLineSeries()
    money_acc.setName('money acc')
    money_by_month = QLineSeries()
    money_by_month.setName('money by month')
    money_by_year = QLineSeries()
    money_by_year.setName('money by year')

    acc = 0.0
    acc_by_month = 0.0
    acc_by_year = 0.0
    last_by_month: date | None = None
    last_by_year: date | None = None
    for info in infos:
        when = info.when
        howmuch = info.howmuch(MONEY_HEADER)
        if howmuch is None:
            continue

        if when < x_min:
            x_min = when
        if when > x_max:
            x_max = when

        when_d = date2days(when)
        howmuch_f = float(howmuch)

        # money
        money.append(when_d, 0)
        # TODO: fix hover to deal with a variable number of items in series
        money.append(when_d, howmuch_f)
        if howmuch < y_min:
            y_min = howmuch
        if howmuch > y_max:
            y_max = howmuch

        # money acc
        money_acc.append(when_d, acc)
        acc += howmuch_f
        money_acc.append(when_d, acc)
        if acc < y_min:
            y_min = Decimal(acc)
        if acc > y_max:
            y_max = Decimal(acc)

        # money_by_month
        money_by_month.append(when_d, acc_by_month)
        if last_by_month is None or last_by_month.month != when.month:
            acc_by_month = 0.0
        else:
            acc_by_month += howmuch_f
        money_by_month.append(when_d, acc_by_month)
        last_by_month = when
        if acc_by_month < y_min:
            y_min = Decimal(acc_by_month)
        if acc_by_month > y_max:
            y_max = Decimal(acc_by_month)

        # money_by_year
        money_by_year.append(when_d, acc_by_year)
        if last_by_year is None or last_by_year.year != when.year:
            acc_by_year = 0.0
        else:
            acc_by_year += howmuch_f
        money_by_year.append(when_d, acc_by_year)
        last_by_year = when
        if acc_by_year < y_min:
            y_min = Decimal(acc_by_year)
        if acc_by_year > y_max:
            y_max = Decimal(acc_by_year)

    return SeriesModel(
        [money, money_acc, money_by_month, money_by_year],
        date2QDateTime(x_min),
        date2QDateTime(x_max),
        float(y_min),
        float(y_max),
        SeriesModelUnit.EURO,
    )


class ChartView(ChartWidget):
    def __init__(self, data_path: str) -> None:
        self.data_path = data_path
        # TODO: there are 2 classes same name
        self.model = SortFilterViewModel()
        super().__init__(self.model, None, series_model_factory, '%d/%m/%Y')
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.reload()

    def reload(self) -> None:
        _, data = read_txt(self.data_path)
        # convert data to infos
        infos: 'list[Info]' = []
        for row in sorted(data, key=lambda row: row.date):
            infos.append(I(row.date, [C(MONEY_HEADER, row.money)]))
        self.model.update(infos)
