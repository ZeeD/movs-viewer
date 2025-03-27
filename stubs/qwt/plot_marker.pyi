from typing import Final
from typing import Self
from typing import overload

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from qwt.plot import QwtPlot
from qwt.plot import QwtPlotItem
from qwt.symbol import QwtSymbol
from qwt.text import QwtText

class QwtPlotMarker(QwtPlotItem):
    NoLine: Final[int]
    HLine: Final[int]
    VLine: Final[int]
    Cross: Final[int]

    def setXValue(self, x: float) -> None: ...
    def setYValue(self, y: float) -> None: ...
    @overload
    def setLabel(self, label: str) -> None: ...
    @overload
    def setLabel(self, label: QwtText) -> None: ...
    @classmethod
    def make(
        cls,
        xvalue: float | None = ...,
        yvalue: float | None = ...,
        title: str | None = ...,
        label: str | QwtText | None = ...,
        symbol: QwtSymbol | None = ...,
        plot: QwtPlot | None = ...,
        z: float | None = ...,
        x_axis: int | None = ...,
        y_axis: int | None = ...,
        align: Qt.AlignmentFlag | None = ...,
        orientation: Qt.Orientation | None = ...,
        spacing: int | None = ...,
        linestyle: int | None = ...,
        color: QColor | str | Qt.GlobalColor | None = ...,
        width: float | None = ...,
        style: Qt.PenStyle | None = ...,
        antialiased: bool = False,
    ) -> Self: ...
