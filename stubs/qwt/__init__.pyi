from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame

from .scale_div import QwtScaleDiv
from .scale_draw import QwtScaleDraw


class QwtPlot(QFrame):
    xBottom: int

    def setAxisScaleDiv(self,
                        axisId: int,
                        scaleDiv: QwtScaleDiv) -> None: ...

    def setAxisScaleDraw(self,
                         axisId: int,
                         scaleDraw: QwtScaleDraw) -> None: ...


class QwtPlotCurve:
    Steps: int

    @classmethod
    def make(cls,
             xdata: list[float] | None =None,
             ydata: list[float] | None=None,
             title: str | None=None,
             plot: QwtPlot | None=None,
             z: None=None,
             x_axis: None=None,
             y_axis: None=None,
             style: int | None=None,
             symbol: None=None,
             linecolor: Qt.GlobalColor | None=None,
             linewidth: float | None=None,
             linestyle: None=None,
             antialiased: bool=False,
             size: None=None,
             finite: None=None) -> QwtPlotCurve: ...


class QwtPlotGrid:
    @classmethod
    def make(cls,
             plot: QwtPlot | None=None,
             z: None=None,
             enablemajor: None=None,
             enableminor: None=None,
             color: None=None,
             width: None=None,
             style: None=None,
             mincolor: None=None,
             minwidth: None=None,
             minstyle: None=None) -> QwtPlotGrid: ...
