from typing import overload

Ticks = list[float]


class QwtScaleDiv:
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self,
                 lowerBound: float,
                 upperBound: float,
                 ticks: list[Ticks]) -> None: ...

    @overload
    def __init__(self,
                 lowerBound: float,
                 upperBound: float,
                 minorTicks: Ticks,
                 mediumTicks: Ticks,
                 majorTicks: Ticks) -> None: ...
