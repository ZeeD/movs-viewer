from datetime import UTC
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from itertools import accumulate
from itertools import cycle
from math import inf
from operator import attrgetter
from sys import argv
from typing import TYPE_CHECKING
from typing import cast
from typing import override

from movslib.movs import read_txt
from PySide6.QtCore import QSize
from PySide6.QtCore import Qt
from PySide6.QtCore import Slot
from PySide6.QtGui import QBrush
from PySide6.QtGui import QFont
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QWidget

from qwt.legend import QwtLegend
from qwt.plot import QwtPlot
from qwt.plot_curve import QwtPlotCurve
from qwt.plot_grid import QwtPlotGrid
from qwt.plot_marker import QwtPlotMarker
from qwt.scale_div import QwtScaleDiv
from qwt.scale_draw import QwtScaleDraw
from qwt.symbol import QwtSymbol
from qwt.text import QwtText

if TYPE_CHECKING:
    from collections.abc import Iterable
    from decimal import Decimal

    from movslib.model import Row
    from movslib.model import Rows

    from qwt.legend import QwtLegendLabel


def linecolors() -> 'Iterable[Qt.GlobalColor]':
    excluded: set[Qt.GlobalColor] = {
        Qt.GlobalColor.color0,
        Qt.GlobalColor.color1,
        Qt.GlobalColor.black,
        Qt.GlobalColor.white,
        Qt.GlobalColor.lightGray,
        Qt.GlobalColor.cyan,
        Qt.GlobalColor.green,
        Qt.GlobalColor.magenta,
        Qt.GlobalColor.yellow,
        Qt.GlobalColor.transparent,
    }
    return cycle(filter(lambda c: c not in excluded, Qt.GlobalColor))


def acc(rows: 'Rows') -> 'Iterable[tuple[date, Decimal]]':
    def func(a: 'tuple[date, Decimal]', b: 'Row') -> 'tuple[date, Decimal]':
        return (b.date, a[1] + b.money)

    it = iter(sorted(rows, key=attrgetter('date')))
    head = next(it)
    return accumulate(it, func, initial=(head.date, head.money))


def days(min_xdata: float, max_xdata: float) -> list[float]:
    lower = datetime.fromtimestamp(min_xdata, tz=UTC).date()
    upper = datetime.fromtimestamp(max_xdata, tz=UTC).date()

    def it() -> 'Iterable[float]':
        when = lower
        while when < upper:
            yield datetime.combine(when, time()).timestamp()
            when += timedelta(days=1)

    return list(it())


def months(min_xdata: float, max_xdata: float) -> list[float]:
    lower = datetime.fromtimestamp(min_xdata, tz=UTC).date()
    upper = datetime.fromtimestamp(max_xdata, tz=UTC).date()

    ly, lm = (lower.year, lower.month)
    uy, um = (upper.year, upper.month)

    def it() -> 'Iterable[float]':
        wy, wm = ly, lm
        while (wy, wm) < (uy, um):
            yield datetime.combine(date(wy, wm, 1), time()).timestamp()
            ml = 12
            if wm < ml:
                wm += 1
            else:
                wy += 1
                wm = 1

    return list(it())


def years(min_xdata: float, max_xdata: float) -> list[float]:
    lower = datetime.fromtimestamp(min_xdata, tz=UTC).year
    upper = datetime.fromtimestamp(max_xdata, tz=UTC).year

    def it() -> 'Iterable[float]':
        when = lower
        while when < upper:
            yield datetime.combine(date(when, 1, 1), time()).timestamp()
            when += 1

    return list(it())


def float2date(value: float) -> date:
    return datetime.fromtimestamp(value, tz=UTC)


class YearMonthScaleDraw(QwtScaleDraw):
    def label(self, value: float) -> str:
        return float2date(value).strftime('%Y-%m')


class EuroScaleDraw(QwtScaleDraw):
    def label(self, value: float) -> str:
        return f'€ {value:_.2f}'


class Plot(QwtPlot):
    def __init__(self, rowss: 'list[Rows]', parent: QWidget | None) -> None:
        super().__init__(parent)
        self._rowss = rowss

        self.setCanvasBackground(Qt.GlobalColor.white)
        QwtPlotGrid.make(self, enableminor=(False, True))
        self.setAxisScaleDraw(QwtPlot.xBottom, YearMonthScaleDraw())
        # https://github.com/PlotPyStack/PythonQwt/issues/88
        self.canvas().setMouseTracking(True)
        self.setMouseTracking(True)
        self.insertLegend(QwtLegend(), QwtPlot.TopLegend)
        self.curves: dict[str, QwtPlotCurve] = {}
        self.markers: dict[str, QwtPlotMarker] = {}

        self.model_reset()

    @Slot()
    def model_reset(self) -> None:
        self.setAxisScaleDraw(QwtPlot.yLeft, EuroScaleDraw())

        min_xdata: float | None = None
        max_xdata: float | None = None
        for rows, linecolor in zip(self._rowss, linecolors(), strict=False):
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

            name = rows.name
            self.curves[name] = QwtPlotCurve.make(
                xdata=xdata,
                ydata=ydata,
                title=QwtText.make(
                    f'{name} - ...', weight=QFont.Weight.Bold, color=linecolor
                ),
                plot=self,
                style=QwtPlotCurve.Steps,
                linecolor=linecolor,
                linewidth=2,
                antialiased=True,
            )
            self.markers[name] = QwtPlotMarker.make(
                symbol=QwtSymbol.make(
                    style=QwtSymbol.Diamond,
                    brush=QBrush(linecolor),
                    size=QSize(9, 9),
                ),
                plot=self,
                align=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                linestyle=QwtPlotMarker.Cross,
                color=Qt.GlobalColor.gray,
                width=1,
                style=Qt.PenStyle.DashLine,
                antialiased=True,
            )

        if min_xdata is None or max_xdata is None:
            raise ValueError

        self._date_changed(min_xdata, max_xdata)

    def _date_changed(self, lower_bound: float, upper_bound: float) -> None:
        ds = days(lower_bound, upper_bound)
        ms = months(lower_bound, upper_bound)
        ys = years(lower_bound, upper_bound)

        # ticks cannot be of len==1
        if len(ds) == 1:
            ds = []
        if len(ms) == 1:
            ms = []
        if len(ys) == 1:
            ys = []

        self.setAxisScaleDiv(
            QwtPlot.xBottom, QwtScaleDiv(lower_bound, upper_bound, ds, ms, ys)
        )

        y_min, y_max = inf, -inf
        for curve in self.curves.values():
            data = curve.data()
            if data is None:
                raise ValueError
            ys = data.yData()
            ys2 = [
                ys[idx]
                for idx, x in enumerate(data.xData())
                if lower_bound <= x <= upper_bound
            ]
            y_min = min(y_min, *ys2)
            y_max = max(y_max, *ys2)

        self.setAxisScale(QwtPlot.yLeft, y_min, y_max)

        self.replot()

    @override
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        event_pos = event.position()

        scale_map = self.canvasMap(QwtPlot.xBottom)
        event_pos_x = event_pos.x()

        magic_offset = 75  # minimum event_pos_x - TODO: find origin

        dt_hover = float2date(
            scale_map.invTransform(event_pos_x - magic_offset)
        )

        for name, curve in self.curves.items():
            legend = cast(
                'QwtLegendLabel',
                cast('QwtLegend', self.legend()).legendWidget(curve),
            )

            data = curve.data()
            if data is None:
                raise ValueError

            x_closest = None
            y_closest = None
            td_min = timedelta.max
            for x_data, y_data in zip(data.xData(), data.yData(), strict=True):
                dt_x = float2date(x_data)
                td = dt_hover - dt_x if dt_hover > dt_x else dt_x - dt_hover
                if td < td_min:
                    x_closest = x_data
                    y_closest = y_data
                    td_min = td

            text = QwtText.make(
                f'{name} - € {y_closest:_.2f}',
                weight=QFont.Weight.Bold,
                color=curve.pen().color(),
            )
            legend.setText(text)
            if x_closest is not None:
                self.markers[name].setXValue(x_closest)
            if y_closest is not None:
                self.markers[name].setYValue(y_closest)
            self.markers[name].setLabel(text)

        self.replot()


def main() -> None:
    _, rows_vm = read_txt(
        '/home/zed/eclipse-workspace/movs-data/BPOL_accumulator_vitomamma.txt',
        'vitomamma',
    )
    _, rows_ve = read_txt(
        '/home/zed/eclipse-workspace/movs-data/BPOL_accumulator_vitoelena.txt',
        'vitoelena',
    )

    app = QApplication(argv)
    plot = Plot([rows_vm, rows_ve], None)
    plot.show()
    app.exec()


if __name__ == '__main__':
    main()
