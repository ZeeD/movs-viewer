from decimal import Decimal
from enum import auto
from enum import Enum

from PyQt6.QtGui import QBrush
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QPen
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtBoundSignal
from typing import ClassVar
from datetime import date, datetime


class QCP:
    class Interaction(Enum):
        iRangeDrag = auto()
        iRangeZoom = auto()
        iSelectPlottables = auto()


class QCPAxisTickerDateTime:
    def setDateTimeFormat(self, fmt: str) -> None:
        ...

    def setTickCount(self, tickCount: int) -> None:
        ...

    @staticmethod
    def dateTimeToKey(dateTime: date | datetime) -> float:
        ...


class QCPGraph:
    class LineStyle(Enum):
        lsStepLeft = auto()

    def setPen(self, pen: QPen) -> None:
        ...

    def setBrush(self, brush: QBrush) -> None:
        ...

    def setData(self,
                keys: list[float],
                values: list[Decimal],
                alreadySorted: bool=False) -> None:
        ...

    def setName(self, name: str) -> None:
        ...

    def addData(self,
                key: float,
                value: Decimal) -> None:
        ...

    def setLineStyle(self, ls: LineStyle) -> None:...


class QCPAxis:
    def setTicker(self, ticker: QCPAxisTickerDateTime) -> None:
        ...

    def setTicks(self, ticks: bool) -> None:
        ...

    def setSubTicks(self, subTicks: bool) -> None:
        ...

    def setRangeLower(self, rangeLower: float) -> None:
        ...

    rangeChanged: ClassVar[pyqtBoundSignal]


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

    def replot(self) -> None:
        ...

    xAxis: QCPAxis
    legend: QCPLegend
