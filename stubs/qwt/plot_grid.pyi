from qwt.plot import QwtPlot

class QwtPlotGrid:
    @classmethod
    def make(
        cls,
        plot: QwtPlot | None = None,
        z: None = None,
        enablemajor: tuple[bool, bool] | None = None,
        enableminor: tuple[bool, bool] | None = None,
        color: None = None,
        width: None = None,
        style: None = None,
        mincolor: None = None,
        minwidth: None = None,
        minstyle: None = None,
    ) -> QwtPlotGrid: ...
