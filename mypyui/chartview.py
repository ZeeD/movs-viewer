from datetime import date
from datetime import datetime
from datetime import time
from decimal import Decimal
from itertools import accumulate
from itertools import chain
from typing import cast
from typing import Optional
from typing import Sequence
from typing import Tuple

from PySide6.QtCharts import QCategoryAxis
from PySide6.QtCharts import QChart
from PySide6.QtCharts import QChartView
from PySide6.QtCharts import QLineSeries
from PySide6.QtCharts import QValueAxis
from PySide6.QtCore import QPointF
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsSceneMouseEvent
from PySide6.QtWidgets import QGraphicsSceneWheelEvent

from movs import read_txt
from movs.model import Row

from .settings import Settings

ZERO = Decimal(0)


def build_series(data: Sequence[Row],
                 epoch: date = date(2008, 1, 1)) -> QLineSeries:
    data = sorted(data, key=lambda row: row.data_valuta)

    series = QLineSeries()

    def toTuple(row: Row) -> Tuple[date, Decimal]:
        if row.accrediti is not None:
            mov = row.accrediti
        elif row.addebiti is not None:
            mov = - row.addebiti
        else:
            mov = ZERO
        return (row.data_valuta, mov)

    # add start and today
    moves = chain(
        ((epoch, ZERO),),
        map(toTuple, data),
        ((date.today(), ZERO),))

    def sumy(a: Tuple[date, Decimal],
             b: Tuple[date, Decimal]) -> Tuple[date, Decimal]:
        _a0, a1 = a
        b0, b1 = b
        return b0, a1 + b1

    summes = accumulate(moves, func=sumy)

    floats = ((datetime.combine(x, time()).timestamp() * 1000, y)
              for x, y in summes)

    # step the movements
    last_y: Optional[Decimal] = None
    for x, y in floats:
        if last_y is not None:
            series.append(x, float(last_y))
        series.append(x, float(y))
        last_y = y

    return series


class Chart(QChart):
    def __init__(self, data: Sequence[Row]):
        super().__init__()

        def years(data: list[Row]) -> list[date]:
            if not data:
                return []
            data = sorted(data, key=lambda row: row.data_valuta)
            start = data[0].data_contabile.year - 1
            end = data[-1].data_contabile.year + 1
            return [date(year, 1, 1) for year in range(start, end + 1)]

        def months(data: Sequence[Row], step: int = 1) -> list[date]:
            if not data:
                return []
            data = sorted(data, key=lambda row: row.data_valuta)
            start = data[0].data_contabile.year - 1
            end = data[-1].data_contabile.year + 1
            return [date(year, month, 1)
                    for year in range(start, end + 1)
                    for month in range(1, 13, step)]

        def reset_axis_x_labels() -> None:
            if True:
                pass

        def ts(d: date) -> float:
            return datetime(d.year, d.month, d.day).timestamp() * 1000

        self.legend().setVisible(False)

        series = build_series(data)
        self.addSeries(series)

        axis_x = QCategoryAxis()
        axis_x.setLabelsPosition(
            QCategoryAxis.AxisLabelsPositionOnValue)
        for dt in months(data, 6):
            axis_x.append(f'{dt}', ts(dt))

        self.addAxis(axis_x, cast(Qt.Alignment, Qt.AlignBottom))
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setTickType(QValueAxis.TicksDynamic)
        axis_y.setTickAnchor(0.)
        axis_y.setTickInterval(10000.)
        axis_y.setMinorTickCount(9)
        self.addAxis(axis_y, cast(Qt.Alignment, Qt.AlignLeft))
        series.attachAxis(axis_y)

    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        super().wheelEvent(event)
        y = event.delta()
        if y < 0:
            self.zoomOut()
        elif y > 0:
            self.zoomIn()

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mousePressEvent(event)
        event.accept()

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mouseMoveEvent(event)

        def t(pos: QPointF) -> tuple[float, float]:
            return pos.x(), pos.y()

        x_curr, y_curr = t(event.pos())
        x_prev, y_prev = t(event.lastPos())
        self.scroll(x_prev - x_curr, y_curr - y_prev)


class ChartView(QChartView):
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.setCursor(Qt.CrossCursor)
        self.reload()

    def reload(self) -> None:
        if self.settings.data_paths:
            _, data = read_txt(self.settings.data_paths[0])
        else:
            data = []
        self.setChart(Chart(data))
