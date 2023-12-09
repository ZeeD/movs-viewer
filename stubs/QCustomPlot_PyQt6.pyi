from datetime import date
from datetime import datetime
from decimal import Decimal
from enum import Enum
from enum import auto
from typing import ClassVar

from PyQt6.QtCore import pyqtBoundSignal
from PyQt6.QtGui import QBrush
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QPen
from PyQt6.QtWidgets import QWidget

class QCP:
    class Interaction(Enum):
        iRangeDrag = auto()  # noqa: N815
        iRangeZoom = auto()  # noqa: N815
        iSelectPlottables = auto()  # noqa: N815

class QCPAxisTickerDateTime:
    def setDateTimeFormat(self, fmt: str) -> None: ...  # noqa: N802
    def setTickCount(self, tickCount: int) -> None: ...  # noqa: N802, N803
    @staticmethod
    def dateTimeToKey(dateTime: date | datetime) -> float: ...  # noqa: N802, N803

class QCPGraph:
    class LineStyle(Enum):
        lsStepLeft = auto()  # noqa: N815

    def setPen(self, pen: QPen) -> None: ...  # noqa: N802
    def setBrush(self, brush: QBrush) -> None: ...  # noqa: N802
    def setData(  # noqa: N802
        self,
        keys: list[float],
        values: list[Decimal],
        alreadySorted: bool = False,  # noqa: N803, FBT001, FBT002
    ) -> None: ...
    def setName(self, name: str) -> None: ...  # noqa: N802
    def addData(self, key: float, value: Decimal) -> None: ...  # noqa: N802
    def setLineStyle(self, ls: LineStyle) -> None: ...  # noqa: N802

class QCPAxis:
    def setTicker(self, ticker: QCPAxisTickerDateTime) -> None: ...  # noqa: N802
    def setTicks(self, ticks: bool) -> None: ...  # noqa: N802, FBT001
    def setSubTicks(self, subTicks: bool) -> None: ...  # noqa: N802, N803, FBT001
    def setRangeLower(self, rangeLower: float) -> None: ...  # noqa: N802, N803

    rangeChanged: ClassVar[pyqtBoundSignal]  # noqa: N815

class QCPLegend:
    def setVisible(self, visible: bool) -> None: ...  # noqa: N802, FBT001
    def setBrush(self, brush: QColor) -> None: ...  # noqa: N802

class QCustomPlot(QWidget):
    def addGraph(self) -> QCPGraph: ...  # noqa: N802
    def rescaleAxes(self) -> None: ...  # noqa: N802
    def setInteraction(self, interaction: QCP.Interaction) -> None: ...  # noqa: N802
    def replot(self) -> None: ...

    xAxis: QCPAxis  # noqa: N815
    legend: QCPLegend
