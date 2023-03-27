from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from decimal import Decimal
from typing import Iterable
from typing import NamedTuple

from PySide6.QtCharts import QChartView
from PySide6.QtCharts import QDateTimeAxis
from PySide6.QtCharts import QLineSeries
from PySide6.QtCharts import QValueAxis
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from qwt import QwtPlot
from qwt import QwtPlotCurve
from qwt import QwtPlotGrid
from qwt.scale_div import QwtScaleDiv
from qwt.scale_draw import QwtScaleDraw


class Point(NamedTuple):
    when: date
    howmuch: Decimal


class Data(NamedTuple):
    name: str
    values: list[Point]


def pysidemain(*datas: Data) -> QChartView:
    chart_view = QChartView()
    chart = chart_view.chart()

    value_axis = QValueAxis(chart)
    date_axis = QDateTimeAxis(chart)
    date_axis.setFormat('yyyy/MM')

    chart.addAxis(value_axis, Qt.AlignmentFlag.AlignLeft)
    chart.addAxis(date_axis, Qt.AlignmentFlag.AlignBottom)

    for data in datas:
        series = QLineSeries(chart)
        series.setName(data.name)

        for when, howmuch in data.values:
            series.append(datetime.combine(when, time()).timestamp() * 1000,
                          float(howmuch))

        chart.addSeries(series)

        series.attachAxis(value_axis)
        series.attachAxis(date_axis)

    howmuchs = [howmuch for data in datas for (
        when, howmuch) in data.values]
    value_axis.setMin(float(min(howmuchs)))
    value_axis.setMax(float(max(howmuchs)))

    chart_view.resize(1000, 1000)
    return chart_view


def qwtmain(*datas: Data) -> QwtPlot:
    plot = QwtPlot()

    min_xdata: float | None = None
    max_xdata: float | None = None
    for (name, values) in datas:
        xdata: list[float] = []
        ydata: list[float] = []
        for when, howmuch in values:
            xdata.append(datetime.combine(when, time()).timestamp())
            ydata.append(float(howmuch))

        tmp = min(xdata)
        if min_xdata is None or tmp < min_xdata:
            min_xdata = tmp
        tmp = max(xdata)
        if max_xdata is None or tmp > max_xdata:
            max_xdata = tmp

        QwtPlotCurve.make(xdata, ydata, name, plot,
                          # style=QwtPlotCurve.Steps,
                          antialiased=True)

    if min_xdata is None or max_xdata is None:
        raise Exception('...')

    def days(min_xdata: float, max_xdata: float) -> list[float]:
        lower = date.fromtimestamp(min_xdata)
        upper = date.fromtimestamp(max_xdata)

        def it() -> Iterable[float]:
            when = lower
            while when < upper:
                yield datetime.combine(when, time()).timestamp()
                when += timedelta(days=1)
        return list(it())

    def months(min_xdata: float, max_xdata: float) -> list[float]:
        lower = date.fromtimestamp(min_xdata)
        upper = date.fromtimestamp(max_xdata)

        ly, lm = (lower.year, lower.month)
        uy, um = (upper.year, upper.month)

        def it() -> Iterable[float]:
            wy, wm = ly, lm
            while (wy, wm) < (uy, um):
                yield datetime.combine(date(wy, wm, 1), time()).timestamp()
                if wm < 12:
                    wm += 1
                else:
                    wy += 1
                    wm = 1
        return list(it())

    def years(min_xdata: float, max_xdata: float) -> list[float]:
        lower = date.fromtimestamp(min_xdata).year
        upper = date.fromtimestamp(max_xdata).year

        def it() -> Iterable[float]:
            when = lower
            while when < upper:
                yield datetime.combine(date(when, 1, 1), time()).timestamp()
                when += 1
        return list(it())

    plot.setAxisScaleDiv(QwtPlot.xBottom,
                         QwtScaleDiv(min_xdata, max_xdata,
                                     days(min_xdata, max_xdata),
                                     months(min_xdata, max_xdata),
                                     years(min_xdata, max_xdata)))

    class SD(QwtScaleDraw):
        def __init__(self) -> None:
            super().__init__()

        def label(self, value: float) -> str:
            return date.fromtimestamp(value).strftime('%Y-%m')
    plot.setAxisScaleDraw(QwtPlot.xBottom, SD())

    QwtPlotGrid.make(plot)

    plot.resize(1_000, 1_000)
    return plot


def main() -> None:
    dates = [date(2000, 1, 1), date(2010, 1, 1), date(2020, 1, 1)]
    valuesOrig = Data('valuesOrig', [Point(*p)
                      for p in zip(dates, [Decimal(5), Decimal(0), Decimal(4)])])
    valuesAct = Data('valuesAct', [Point(*p)
                     for p in zip(dates, [Decimal(2), Decimal(3), Decimal(1)])])

    app = QApplication()
    try:
        chart_view = pysidemain(valuesOrig, valuesAct)
        chart_view.show()

        plot = qwtmain(valuesOrig, valuesAct)
        plot.show()
    finally:
        app.exec_()


if __name__ == '__main__':
    main()
