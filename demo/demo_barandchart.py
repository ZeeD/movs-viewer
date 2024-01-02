from datetime import UTC
from datetime import date
from datetime import datetime
from itertools import accumulate
from itertools import groupby
from os import environ
from pathlib import Path
from sys import argv
from typing import NoReturn
from typing import override

if 'QT_API' not in environ:
    environ['QT_API'] = 'pyside6'

from movslib.model import ZERO
from movslib.model import Row
from movslib.model import Rows
from movslib.movs import read_txt
from qtpy.QtCharts import QBarCategoryAxis
from qtpy.QtCharts import QBarSeries
from qtpy.QtCharts import QBarSet
from qtpy.QtCharts import QChart
from qtpy.QtCharts import QChartView
from qtpy.QtCharts import QDateTimeAxis
from qtpy.QtCharts import QLineSeries
from qtpy.QtCharts import QStackedBarSeries
from qtpy.QtCharts import QValueAxis
from qtpy.QtCore import QDateTime
from qtpy.QtCore import QPointF
from qtpy.QtCore import QRectF
from qtpy.QtCore import Qt
from qtpy.QtGui import QPen
from qtpy.QtWidgets import QApplication
from qtpy.QtWidgets import QGraphicsSceneMouseEvent
from qtpy.QtWidgets import QGraphicsSceneWheelEvent
from qtpy.QtWidgets import QMainWindow

from movsviewer.settings import Settings


def year(row: Row) -> int:
    return row.data_valuta.year


def month(row: Row) -> int:
    return row.data_valuta.month


def day(row: Row) -> date:
    return row.data_valuta


def get_rows() -> Rows:
    settings = Settings(argv[1:])
    _, rows = read_txt(
        settings.data_paths[0], Path(settings.data_paths[0]).stem
    )
    return rows


def range_years(rows: Rows) -> range:
    rows_sorted = sorted(rows, key=year)
    return range(year(rows_sorted[0]), year(rows_sorted[-1]) + 1)


def years(rows: Rows) -> list[str]:
    "All years between first and last row."
    return [f'{y: 04}' for y in range_years(rows)]


def sums_years_by_month(rows: Rows) -> dict[str, list[float]]:
    "Return {month: [sum(row) for row in each year]} ."
    ret: dict[str, list[float]] = {}

    tmp = {k: list(v) for k, v in groupby(sorted(rows, key=month), key=month)}
    for i, m in enumerate(
        [
            'GEN',
            'FEB',
            'MAR',
            'APR',
            'MAG',
            'GIU',
            'LUG',
            'AGO',
            'SET',
            'OTT',
            'NOV',
            'DIC',
        ],
        start=1,
    ):
        tmp2 = {
            k: list(v)
            for k, v in groupby(sorted(tmp.get(i, []), key=year), key=year)
        }

        ret[m] = [
            float(sum((row.money for row in tmp2.get(y, [])), start=ZERO))
            for y in range_years(rows)
        ]

    return ret


def sums_by_year(rows: Rows) -> list[float]:
    "Return [sum(row) for row in each year] ."
    tmp = {k: list(v) for k, v in groupby(sorted(rows, key=year), key=year)}
    return [
        float(sum((row.money for row in tmp.get(y, [])), start=ZERO))
        for y in range_years(rows)
    ]


def sums_by_day(rows: Rows) -> list[tuple[float, float]]:
    epoch = datetime.fromtimestamp(0, tz=UTC).date()

    def msec(d: date) -> float:
        return (d - epoch).total_seconds() * 1000

    rows_sorted = sorted(rows, key=day)
    ret = list(
        accumulate(
            rows_sorted,
            lambda acc, row: (msec(day(row)), float(row.money) + acc[1]),
            initial=(msec(date(year(rows_sorted[0]), 1, 1)), 0.0),
        )
    )
    # append a pair (next year-01-01, lastsum)
    ret.append((msec(date(year(rows_sorted[-1]) + 1, 1, 1)), ret[-1][1]))
    return ret


def qdt(data: tuple[float, float]) -> QDateTime:
    return QDateTime.fromMSecsSinceEpoch(int(data[0]))


class C(QChart):
    def __init__(
        self,
        seriess: tuple[QBarSeries, QStackedBarSeries, QLineSeries],
        data_by_year: list[float],
        data_by_day: list[tuple[float, float]],
        rows: Rows,
    ) -> None:
        super().__init__()

        series_year, series_month, series_day = seriess

        self.setTheme(QChart.ChartTheme.ChartThemeQt)
        self.addSeries(series_year)
        self.addSeries(series_month)
        self.addSeries(series_day)

        # axis
        axis_y = QValueAxis()
        axis_y.setTickType(QValueAxis.TickType.TicksDynamic)
        axis_y.setTickAnchor(0.0)
        axis_y.setTickInterval(10_000.0)
        axis_y.setRange(-40_000, 120_000)

        axis_x_line = QDateTimeAxis()
        axis_x_line.setFormat('dd/MM/yyyy')
        axis_x_line.setRange(qdt(data_by_day[0]), qdt(data_by_day[-1]))
        axis_x_line.setTickCount(len(data_by_year) + 1)

        axis_x_bar = QBarCategoryAxis()
        axis_x_bar.append(years(rows))

        self.addAxis(axis_x_bar, Qt.AlignmentFlag.AlignBottom)
        self.addAxis(axis_x_line, Qt.AlignmentFlag.AlignBottom)
        self.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

        # for some reason I need to link the axis to the series after the chart
        series_year.attachAxis(axis_x_bar)
        series_year.attachAxis(axis_y)
        series_month.attachAxis(axis_x_bar)
        series_month.attachAxis(axis_y)
        series_day.attachAxis(axis_x_line)
        series_day.attachAxis(axis_y)

    @override
    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        super().wheelEvent(event)

        area = self.plotArea()
        w = area.width() * (1.25 if event.delta() > 0 else (1 / 1.25))
        x = area.x() - (w - area.width()) / 2
        self.zoomIn(QRectF(x, area.y(), w, area.height()))

    @override
    def mousePressEvent(self, _event: QGraphicsSceneMouseEvent) -> None:
        "Reimplemented to capture the mouse move."

    @override
    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mouseMoveEvent(event)

        self.scroll(event.lastPos().x() - event.pos().x(), 0)


def main() -> NoReturn:
    rows = get_rows()

    data_by_year = sums_by_year(rows)
    data_by_day = sums_by_day(rows)

    a = QApplication(argv)

    # line
    def series_day_hovered(_point: QPointF, state: bool) -> None:  # noqa: FBT001
        pen = QPen(series_day.pen())
        pen.setWidth(pen.width() * 2 if state else pen.width() // 2)
        series_day.setPen(pen)

    series_day = QLineSeries()
    series_day.replace([QPointF(x, y) for x, y in data_by_day])
    # series_day.setPointLabelsVisible(True)
    series_day.hovered.connect(series_day_hovered)

    # bar series - by month
    def series_month_hovered(
        status: bool,  # noqa: FBT001
        _index: int,
        _barset: QBarSet,
    ) -> None:
        series_month.setLabelsVisible(status)

    series_month = QStackedBarSeries()
    series_month.hovered.connect(series_month_hovered)
    for month, sums_years in sums_years_by_month(rows).items():
        set_ = QBarSet(month)
        set_.append(sums_years)
        series_month.append(set_)

    # bar series - by year
    def series_year_hovered(
        status: bool,  # noqa: FBT001
        _index: int,
        _barset: QBarSet,
    ) -> None:
        series_year.setLabelsVisible(status)

    series_year = QBarSeries()
    series_year.hovered.connect(series_year_hovered)
    set_ = QBarSet('year')
    set_.append(data_by_year)
    series_year.append(set_)

    chart = C(
        (series_year, series_month, series_day), data_by_year, data_by_day, rows
    )

    chart_view = QChartView(chart)
    chart_view.setCursor(Qt.CursorShape.CrossCursor)

    # main
    main_window = QMainWindow()
    main_window.setCentralWidget(chart_view)
    main_window.resize(1920, 1080)
    main_window.show()

    raise SystemExit(a.exec())


if __name__ == '__main__':
    main()
