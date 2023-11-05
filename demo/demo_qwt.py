from collections.abc import Iterable
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from decimal import Decimal
from itertools import accumulate
from itertools import cycle
from operator import attrgetter
from sys import argv

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication
from qwt import QwtPlot
from qwt import QwtPlotCurve
from qwt import QwtPlotGrid
from qwt.scale_div import QwtScaleDiv
from qwt.scale_draw import QwtScaleDraw

from movs import read_txt
from movs.model import Row
from movs.model import Rows


def linecolors() -> Iterable[Qt.GlobalColor]:
    return cycle(filter(lambda c: c not in set([Qt.GlobalColor.color0,
                                                Qt.GlobalColor.color1,
                                                Qt.GlobalColor.black,
                                                Qt.GlobalColor.white,
                                                Qt.GlobalColor.darkGray,
                                                Qt.GlobalColor.gray,
                                                Qt.GlobalColor.lightGray,
                                                Qt.GlobalColor.transparent]),
                        Qt.GlobalColor))


T = tuple[date, Decimal]


def acc(rows: Rows) -> Iterable[T]:
    def func(a: T, b: Row) -> T:
        return (b.date, a[1] + b.money)

    it = iter(sorted(rows, key=attrgetter('date')))
    head: Row = next(it)
    return accumulate(it, func, initial=(head.date, head.money))


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


class SD(QwtScaleDraw):
    def label(self, value: float) -> str:
        return date.fromtimestamp(value).strftime('%Y-%m')


def qwtmain(*rowss: Rows) -> QwtPlot:
    plot = QwtPlot()

    min_xdata: float | None = None
    max_xdata: float | None = None
    for (rows, linecolor) in zip(rowss, linecolors()):
        xdata: list[float] = []
        ydata: list[float] = []
        for when, howmuch in acc(rows):
            xdata.append(datetime.combine(when, time()).timestamp())
            ydata.append(float(howmuch))

        tmp = min(xdata)
        if min_xdata is None or tmp < min_xdata:
            min_xdata = tmp
        tmp = max(xdata)
        if max_xdata is None or tmp > max_xdata:
            max_xdata = tmp

        QwtPlotCurve.make(xdata, ydata, rows.name, plot,
                          style=QwtPlotCurve.Steps,
                          linecolor=linecolor,
                          linewidth=3,
                          antialiased=True)

    if min_xdata is None or max_xdata is None:
        raise Exception('...')

    plot.setAxisScaleDiv(QwtPlot.xBottom,
                         QwtScaleDiv(min_xdata, max_xdata,
                                     days(min_xdata, max_xdata),
                                     months(min_xdata, max_xdata),
                                     years(min_xdata, max_xdata)))

    plot.setAxisScaleDraw(QwtPlot.xBottom, SD())

    QwtPlotGrid.make(plot)

    plot.resize(1_000, 1_000)
    return plot


PATH = '/home/zed/eclipse-workspace/movs-data/BPOL_accumulator_vitomamma.txt'


def main() -> None:
    _, rows = read_txt(PATH, 'BPOL')

    app = QApplication(argv)

    plot = qwtmain(rows)
    plot.show()

    app.exec_()


if __name__ == '__main__':
    main()
