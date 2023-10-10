from decimal import Decimal
from enum import auto
from enum import Enum

from PyQt6.QtGui import QBrush
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QPen
from PyQt6.QtWidgets import QWidget


class QCP:
    class Interaction(Enum):
        iRangeDrag = auto()
        iRangeZoom = auto()
        iSelectPlottables = auto()


class QCPAxisTickerDateTime:
    ...


class QCPGraph:
    def setPen(self, pen: QPen) -> None:
        ...

    def setBrush(self, brush: QBrush) -> None:
        ...

    def setData(self, x: list[float], y: list[Decimal]) -> None:
        ...


class QCPAxis:
    def setTicker(self, ticker: QCPAxisTickerDateTime) -> None:
        ...


class QCPLegend:
    def setVisible(self, visible: bool) -> None:
        ...

    def setBrush(self, brush: QColor) -> None:
        ...


class QCustomPlot(QWidget):
    def addGraph(self) -> QCPGraph:
        ...

    def rescaleAxes(self) -> None:
        ...

    def setInteraction(self, interaction: QCP.Interaction) -> None:
        ...

    xAxis: QCPAxis
    legend: QCPLegend
