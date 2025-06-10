from collections import defaultdict
from decimal import Decimal
from logging import INFO
from logging import basicConfig
from logging import getLogger
from sys import stdout
from typing import Final

from movslib.reader import read

FNS: Final = (
    '/home/zed/eclipse-workspace/movs-data/BPOL_accumulator_vitomamma.txt',
    '/home/zed/eclipse-workspace/movs-data/BPOL_accumulator_vitoelena.txt',
)


logger = getLogger(__name__)


def eoystats(fn: str) -> None:
    _, rows = read(fn)

    years = defaultdict[int, Decimal](lambda: Decimal('0'))
    for row in rows:
        years[row.date.year] += row.money

    for year in sorted(years):
        money = years[year]
        logger.info('%s -> %11.2f', year, money)
    logger.info(' SUM -> %11.2f', sum(years.values()))


def main() -> None:
    basicConfig(level=INFO, stream=stdout, format='%(message)s')
    for fn in FNS:
        logger.info('EOY STATS - %s', fn)
        eoystats(fn)


if __name__ == '__main__':
    main()
