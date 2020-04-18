import datetime
import decimal
import itertools
import typing

from PySide2.QtCharts import QtCharts
import movs

ZERO = decimal.Decimal(0)


def build_series(data: typing.Iterable[movs.model.Row],
                 epoch: datetime.date = datetime.date(1990, 1, 1)):
    series = QtCharts.QLineSeries()

    def toTuple(
            row: movs.model.Row) -> typing.Tuple[datetime.date, decimal.Decimal]:
        if row.accrediti is not None:
            mov = row.accrediti
        elif row.addebiti is not None:
            mov = - row.addebiti
        else:
            mov = ZERO
        return (row.data_contabile, mov)

    # add start and today
    moves = itertools.chain(
        ((epoch, ZERO),),
        map(toTuple, data),
        ((datetime.date.today(), ZERO),)
    )

    def sumy(a: typing.Iterable[typing.Any],
             b: typing.Iterable[typing.Any]
             ) -> typing.Tuple[datetime.date, decimal.Decimal]:
        _a0, a1, *_ = a
        b0, b1, *_ = b
        return b0, a1 + b1

    summes = itertools.accumulate(moves, func=sumy)

    floats = (
        (datetime.datetime.combine(
            x,
            datetime.time()).timestamp() *
            1000,
            y) for x,
        y in summes)

    # step the movements
    last_y = None
    for x, y in floats:
        if last_y is not None:
            series.append(x, last_y)
        series.append(x, y)
        last_y = y

    return series
