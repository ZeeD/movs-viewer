from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame

from .scale_div import QwtScaleDiv
from .scale_draw import QwtScaleDraw

class QwtPlot(QFrame):
    xBottom: int  # noqa: N815

    def setAxisScaleDiv(  # noqa: N802
        self,
        axisId: int,  # noqa: N803
        scaleDiv: QwtScaleDiv,  # noqa: N803
    ) -> None: ...
    def setAxisScaleDraw(  # noqa: N802
        self,
        axisId: int,  # noqa: N803
        scaleDraw: QwtScaleDraw,  # noqa: N803
    ) -> None: ...

class QwtPlotCurve:
    Steps: int

    @classmethod
    def make(  # noqa: PLR0913
        cls,
        xdata: list[float] | None = None,
        ydata: list[float] | None = None,
        title: str | None = None,
        plot: QwtPlot | None = None,
        z: None = None,
        x_axis: None = None,
        y_axis: None = None,
        style: int | None = None,
        symbol: None = None,
        linecolor: Qt.GlobalColor | None = None,
        linewidth: float | None = None,
        linestyle: None = None,
        antialiased: bool = False,  # noqa: FBT001, FBT002
        size: None = None,
        finite: None = None,
    ) -> QwtPlotCurve: ...

class QwtPlotGrid:
    @classmethod
    def make(  # noqa: PLR0913
        cls,
        plot: QwtPlot | None = None,
        z: None = None,
        enablemajor: None = None,
        enableminor: None = None,
        color: None = None,
        width: None = None,
        style: None = None,
        mincolor: None = None,
        minwidth: None = None,
        minstyle: None = None,
    ) -> QwtPlotGrid: ...
