from typing import overload

from PySide6.QtCore import QPointF
from PySide6.QtCore import QRectF

class QwtScaleMap:
    @overload
    def transform(self, scalar: float, /) -> float: ...
    @overload
    def transform(
        self, xMap: QwtScaleMap, yMap: QwtScaleMap, pos: QPointF, /
    ) -> QPointF: ...
    @overload
    def transform(
        self, xMap: QwtScaleMap, yMap: QwtScaleMap, rect: QRectF, /
    ) -> QRectF: ...
    @overload
    def invTransform(self, scalar: float, /) -> float: ...
    @overload
    def invTransform(
        self, xMap: QwtScaleMap, yMap: QwtScaleMap, pos: QPointF, /
    ) -> QPointF: ...
    @overload
    def invTransform(
        self, xMap: QwtScaleMap, yMap: QwtScaleMap, rect: QRectF, /
    ) -> QRectF: ...
