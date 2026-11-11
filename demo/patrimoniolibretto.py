"""actuals.

libretto:
supersmart:  160_850.00
disponibili:      26.56

buoni:
Valore nominale: 77_750.00
Valore rimborso: 79_791.32
"""

from decimal import Decimal
from logging import INFO
from logging import basicConfig
from logging import getLogger
from operator import attrgetter
from sys import argv
from typing import TYPE_CHECKING
from typing import Final
from typing import NamedTuple

from openpyxl import Workbook

from movslib.librettotxt import read_libretto_txt

if TYPE_CHECKING:
    from datetime import date

    from movslib.model import Row

logger = getLogger(__name__)

ZERO: Final = Decimal(0)


class Point(NamedTuple):
    date: 'date'
    money: Decimal


def _acc(acc: list[Point], date: 'date', money: Decimal) -> None:
    curr = acc[-1].money if acc else ZERO
    acc.append(Point(date, curr + money))


def get_patrimonio_libretto(
    csv: 'list[Row]',
) -> 'tuple[list[Point], list[Point]]':
    supersmart: list[Point] = []
    disponibili: list[Point] = []

    for row in sorted(csv, key=attrgetter('date')):
        if row.descrizione_operazioni.startswith(
            ('sottoscrizione ', 'rimborso ')
        ):
            _acc(supersmart, row.date, -row.money)
        _acc(disponibili, row.date, row.money)

    return supersmart, disponibili


def save_as_xls(xlsx: str, **pointss: list[Point]) -> None:
    wb = Workbook()
    ws = wb.active
    if ws is None:
        raise ValueError
    for header, points in pointss.items():
        ws.append(['date', header])
        for date, money in points:
            ws.append([date, money])
    wb.save(xlsx)


def main() -> None:
    basicConfig(level=INFO, format='%(message)s')

    fn = argv[1]
    xlsx = argv[2] if len(argv[2:]) else None
    logger.info('fn: %s; xlsx: %s', fn, xlsx)

    supersmart, disponibili = get_patrimonio_libretto(read_libretto_txt(fn)[1])
    actual = (supersmart[-1], disponibili[-1])
    expected = Decimal(160850), Decimal('26.56')

    logger.info('          supersmart; disponibili')
    logger.info('expected: %10.2f; %10.2f', expected[0], expected[1])
    logger.info('actual:   %10.2f; %10.2f', actual[0].money, actual[1].money)

    if xlsx:
        save_as_xls(xlsx, supersmart=supersmart, disponibili=disponibili)


if __name__ == '__main__':
    main()
