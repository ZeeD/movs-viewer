import datetime
import decimal
import itertools
import typing

from PySide2.QtCharts import QtCharts


def build_series(data: typing.Sequence[typing.Tuple[datetime.date, decimal.Decimal]],
                 epoch: datetime.date = datetime.date(1990, 1, 1)):
    series = QtCharts.QLineSeries()

    # add start and today
    moves = itertools.chain(
        ((epoch, decimal.Decimal(0)),),
        data,
        ((datetime.date.today(), decimal.Decimal(0)),)
    )

    def sumy(a: typing.Iterable[typing.Any],
             b: typing.Iterable[typing.Any]
             ) -> typing.Tuple[datetime.date, decimal.Decimal]:
        _a0, a1, *_ = a
        b0, b1, *_ = b
        return b0, a1 + b1

    summes = itertools.accumulate(moves, func=sumy)

    floats = ((datetime.datetime.combine(x, datetime.time()).timestamp() * 1000, y)
              for x, y in summes)

    # step the movements
    last_y = None
    for x, y in floats:
        if last_y is not None:
            series.append(x, last_y)
        series.append(x, y)
        last_y = y

    return series
