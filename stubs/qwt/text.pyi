from typing import Self

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame

class QwtTextLabel(QFrame): ...

class QwtText:
    def __init__(
        self,
        text: str | None = ...,
        textFormat: int | None = None,
        other: QwtText | None = None,
    ) -> None: ...
    @classmethod
    def make(
        cls,
        text: str | None = None,
        textformat: None = None,
        renderflags: None = None,
        font: None = None,
        family: None = None,
        pointsize: None = None,
        weight: QFont.Weight | None = None,
        color: QColor | Qt.GlobalColor | None = None,
        borderradius: None = None,
        borderpen: None = None,
        brush: None = None,
    ) -> Self: ...
