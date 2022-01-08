from datetime import date
from itertools import accumulate
from itertools import groupby
from sys import argv
from typing import cast
from typing import NoReturn

from PySide6.QtCharts import QBarCategoryAxis
from PySide6.QtCharts import QBarSeries
from PySide6.QtCharts import QBarSet
from PySide6.QtCharts import QChart
from PySide6.QtCharts import QChartView
from PySide6.QtCharts import QDateTimeAxis
from PySide6.QtCharts import QLineSeries
from PySide6.QtCharts import QStackedBarSeries
from PySide6.QtCharts import QValueAxis
from PySide6.QtCore import QPointF, QDateTime
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QMainWindow

from movs import read_txt
from movs.model import Row
from mypyui.settings import Settings


def year(row: Row) -> int:
    return row.data_valuta.year


def month(row: Row) -> int:
    return row.data_valuta.month


def day(row: Row) -> date:
    return row.data_valuta


def get_rows() -> list[Row]:
    settings = Settings()
    _, rows = read_txt(settings.data_paths[0])
    return rows


def range_years(ROWS: list[Row]) -> range:
    rows = sorted(ROWS, key=year)
    return range(year(rows[0]), year(rows[-1]) + 1)


def years(ROWS: list[Row]) -> list[str]:
    'all years between first and last row'

    return [f'{y:04}' for y in range_years(ROWS)]


def sums_years_by_month(ROWS: list[Row]) -> dict[str, list[float]]:
    '{month: [sum(row) for row in each year]}'

    ret: dict[str, list[float]] = {}

    tmp = {k: list(v) for k, v in groupby(sorted(ROWS, key=month), key=month)}
    for i, m in enumerate(['GEN', 'FEB', 'MAR', 'APR', 'MAG', 'GIU',
                           'LUG', 'AGO', 'SET', 'OTT', 'NOV', 'DIC'], start=1):
        tmp2 = {k: list(v)
                for k, v in groupby(sorted(tmp.get(i, []), key=year), key=year)}

        ret[m] = [float(sum((row.money for row in tmp2.get(y, [])),
                            start=Row.zero))
                  for y in range_years(ROWS)]

    return ret


def sums_by_year(ROWS: list[Row]) -> list[float]:
    '[sum(row) for row in each year]'

    tmp = {k: list(v) for k, v in groupby(sorted(ROWS, key=year), key=year)}
    return [float(sum((row.money for row in tmp.get(y, [])),
                      start=Row.zero))
            for y in range_years(ROWS)]


def sums_by_day(ROWS: list[Row]) -> list[tuple[float, float]]:
    epoch = date.fromtimestamp(0)

    def msec(d: date) -> float:
        return (d - epoch).total_seconds() * 1000

    rows = list(sorted(ROWS, key=day))
    ret = list(accumulate(rows,
                          lambda acc, row: (msec(day(row)),
                                            float(row.money) + acc[1]),
                          initial=(msec(date(year(rows[0]), 1, 1)), 0.)))
    # append a pair (next year-01-01, lastsum)
    ret.append((msec(date(year(rows[-1]) + 1, 1, 1)),
                ret[-1][1]))
    return ret


def main() -> NoReturn:
    ROWS = get_rows()

    categories = years(ROWS)
    data_by_month = sums_years_by_month(ROWS)
    data_by_year = sums_by_year(ROWS)
    data_by_day = sums_by_day(ROWS)

    def qdt(data: tuple[float, float]) -> QDateTime:
        return QDateTime.fromMSecsSinceEpoch(int(data[0]))

    a = QApplication(argv)
    try:
        # axis
        axis_y = QValueAxis()
        axis_y.setTickType(QValueAxis.TicksDynamic)
        axis_y.setTickAnchor(0.)
        axis_y.setTickInterval(10_000.)
        axis_y.setRange(-40_000, 120_000)

        axis_x_line = QDateTimeAxis()
        axis_x_line.setFormat('MM/yyyy')
        axis_x_line.setRange(qdt(data_by_day[0]), qdt(data_by_day[-1]))
        axis_x_line.setTickCount(len(data_by_year) + 1)

        axis_x_bar = QBarCategoryAxis()
        axis_x_bar.append(categories)

        # line
        series_day = QLineSeries()
        series_day.replace([QPointF(x, y) for x, y in data_by_day])

        # bar series - by month
        series_month = QStackedBarSeries()
        for month, sums_years in data_by_month.items():
            set_ = QBarSet(month)
            set_.append(sums_years)
            series_month.append(set_)

        # bar series - by year
        series_year = QBarSeries()
        set_ = QBarSet('year')
        set_.append(data_by_year)
        series_year.append(set_)

        chart = QChart()
        chart.addSeries(series_year)
        chart.addSeries(series_month)
        chart.addSeries(series_day)
        chart.addAxis(axis_x_bar, cast(Qt.Alignment, Qt.AlignBottom))
        chart.addAxis(axis_x_line, cast(Qt.Alignment, Qt.AlignBottom))
        chart.addAxis(axis_y, cast(Qt.Alignment, Qt.AlignLeft))

        # for some reason I need to link the axis to the series after the chart
        series_year.attachAxis(axis_x_bar)
        series_year.attachAxis(axis_y)
        series_month.attachAxis(axis_x_bar)
        series_month.attachAxis(axis_y)
        series_day.attachAxis(axis_x_line)
        series_day.attachAxis(axis_y)

        # main
        main_window = QMainWindow()
        main_window.setCentralWidget(QChartView(chart))
        main_window.resize(1920, 1080)
        main_window.show()
    finally:
        raise SystemExit(a.exec())


if __name__ == '__main__':
    main()
