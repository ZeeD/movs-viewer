from datetime import date
from itertools import accumulate
from itertools import groupby
from sys import argv
from typing import NoReturn

from movs import read_txt
from movs.model import Row
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
        axis_y.setTickType(QValueAxis.TickType.TicksDynamic)
        axis_y.setTickAnchor(0.)
        axis_y.setTickInterval(10_000.)
        axis_y.setRange(-40_000, 120_000)

        axis_x_line = QDateTimeAxis()
        axis_x_line.setFormat('dd/MM/yyyy')
        axis_x_line.setRange(qdt(data_by_day[0]), qdt(data_by_day[-1]))
        axis_x_line.setTickCount(len(data_by_year) + 1)

        axis_x_bar = QBarCategoryAxis()
        axis_x_bar.append(categories)

        # line
        def series_day_hovered(_point: QPointF, state: bool) -> None:
            pen = QPen(series_day.pen())
            pen.setWidth(pen.width() * 2 if state else pen.width() // 2)
            series_day.setPen(pen)

        series_day = QLineSeries()
        series_day.replace([QPointF(x, y) for x, y in data_by_day])
        # series_day.setPointLabelsVisible(True)
        series_day.hovered.connect(series_day_hovered)

        # bar series - by month
        def series_month_hovered(status: bool,
                                 _index: int,
                                 _barset: QBarSet) -> None:
            series_month.setLabelsVisible(status)

        series_month = QStackedBarSeries()
        series_month.hovered.connect(series_month_hovered)
        for month, sums_years in data_by_month.items():
            set_ = QBarSet(month)
            set_.append(sums_years)
            series_month.append(set_)

        # bar series - by year
        def series_year_hovered(status: bool,
                                _index: int,
                                _barset: QBarSet) -> None:
            series_year.setLabelsVisible(status)

        series_year = QBarSeries()
        series_year.hovered.connect(series_year_hovered)
        set_ = QBarSet('year')
        set_.append(data_by_year)
        series_year.append(set_)

        class C(QChart):
            def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
                super().wheelEvent(event)

                area = self.plotArea()
                w = area.width() * (1.25 if event.delta() > 0 else (1 / 1.25))
                x = area.x() - (w - area.width()) / 2
                self.zoomIn(QRectF(x, area.y(), w, area.height()))

            def mousePressEvent(self, _event: QGraphicsSceneMouseEvent) -> None:
                'reimplemented to capture the mouse move'

            def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
                super().mouseMoveEvent(event)

                self.scroll(event.lastPos().x() - event.pos().x(), 0)

        chart = C()
        chart.setTheme(QChart.ChartTheme.ChartThemeQt)
        chart.addSeries(series_year)
        chart.addSeries(series_month)
        chart.addSeries(series_day)
        chart.addAxis(axis_x_bar, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(axis_x_line, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

        # for some reason I need to link the axis to the series after the chart
        series_year.attachAxis(axis_x_bar)
        series_year.attachAxis(axis_y)
        series_month.attachAxis(axis_x_bar)
        series_month.attachAxis(axis_y)
        series_day.attachAxis(axis_x_line)
        series_day.attachAxis(axis_y)

        chart_view = QChartView(chart)
        chart_view.setCursor(Qt.CursorShape.CrossCursor)

        # main
        main_window = QMainWindow()
        main_window.setCentralWidget(chart_view)
        main_window.resize(1920, 1080)
        main_window.show()
    finally:
        raise SystemExit(a.exec())


if __name__ == '__main__':
    main()
