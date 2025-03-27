from collections.abc import Sequence
from typing import overload

from qwt.interval import QwtInterval

class QwtScaleDiv:
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, lowerBound: float, upperBound: float) -> None: ...
    @overload
    def __init__(
        self, lowerBound: float, upperBound: float, ticks: list[Sequence[float]]
    ) -> None: ...
    @overload
    def __init__(
        self,
        lowerBound: float,
        upperBound: float,
        minorTicks: Sequence[float],
        mediumTicks: Sequence[float],
        majorTicks: Sequence[float],
    ) -> None: ...
    def setLowerBound(self, lowerBound: float) -> None: ...
    def setUpperBound(self, upperBound: float) -> None: ...
    def interval(self) -> QwtInterval: ...
