from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QWidget

from qwt.text import QwtText
from qwt.text import QwtTextLabel

class QwtAbstractLegend(QFrame): ...

class QwtLegend(QwtAbstractLegend):
    def setDefaultItemMode(self, mode: int) -> None: ...
    def legendWidget(self, itemInfo: object) -> QWidget: ...

class QwtLegendData:
    ReadOnly: int
    Clickable: int
    Checkable: int

class QwtLegendLabel(QwtTextLabel):
    def setText(self, text: QwtText) -> None: ...
