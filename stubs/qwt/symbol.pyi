from typing import Final
from typing import Self

from PySide6.QtCore import QPointF
from PySide6.QtCore import QSize
from PySide6.QtGui import QBrush
from PySide6.QtGui import QPainterPath
from PySide6.QtGui import QPen
from PySide6.QtGui import QPixmap

from qwt.graphic import QwtGraphic

class QwtSymbol:
    NoSymbol: Final[int]
    Ellipse: Final[int]
    Rect: Final[int]
    Diamond: Final[int]

    @classmethod
    def make(
        cls,
        style: int | None = None,
        brush: QBrush | None = None,
        pen: QPen | None = None,
        size: QSize | None = None,
        path: QPainterPath | None = None,
        pixmap: QPixmap | None = None,
        graphic: QwtGraphic | None = None,
        svgdocument: str | None = None,
        pinpoint: QPointF | None = None,
    ) -> Self: ...
