#!/usr/bin/env python

from datetime import UTC
from datetime import date
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from html.parser import HTMLParser
from locale import LC_NUMERIC
from locale import delocalize
from locale import getlocale
from locale import setlocale
from logging import INFO
from logging import basicConfig
from logging import getLogger
from typing import TYPE_CHECKING
from typing import NamedTuple
from typing import Self
from urllib.parse import urlencode
from urllib.request import urlopen

from movslib.model import ZERO
from movslib.model import Row
from movslib.movs import read_txt

if TYPE_CHECKING:
    from collections.abc import Iterator

logger = getLogger(__name__)

fn = '/home/zed/eclipse-workspace/movs-data/BPOL_accumulator_vitomamma.txt'


class Parser(HTMLParser):
    i = 0
    raw: str | None = None

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag != 'input':
            return
        if self.i == 1:
            self.raw = dict(attrs)['value']
        self.i += 1


class Period(NamedTuple):
    year: int
    month: str
    month_orig: int

    @classmethod
    def from_year(cls, year: int) -> Self:
        return cls(year, 'Media Annua', 0)

    @classmethod
    def from_date(cls, dt: date) -> Self:
        return cls.from_year_month(dt.year, dt.month)

    @classmethod
    def from_year_month(cls, year: int, month: int) -> Self:
        return cls(
            year,
            [
                '',
                'Gennaio',
                'Febbraio',
                'Marzo',
                'Aprile',
                'Maggio',
                'Giugno',
                'Luglio',
                'Agosto',
                'Settembre',
                'Ottobre',
                'Novembre',
                'Dicembre',
                'Media Annua',
            ][month],
            month,
        )


class RawNotFoundError(Exception): ...


def rivaluta(from_: Period, to: Period, value: Decimal) -> Decimal:
    response = urlopen(
        'https://rivaluta.istat.it/Rivaluta/CalcolatoreCoefficientiAction.action',
        urlencode(
            {
                'meseDa': from_.month,
                'annoDa': from_.year,
                'meseA': to.month,
                'annoA': to.year,
                'SOMMA': value,
                'PERIODO': 1,
                'EUROLIRE': 'true',
                '': '',
            }
        ).encode('utf-8'),
    )
    body = response.read().decode('utf-8')
    parser = Parser()
    try:
        parser.feed(body)
    finally:
        parser.close()

    raw = parser.raw
    if raw is None:
        logger.error('no raw - body: %s', body)
        raise RawNotFoundError

    locale = getlocale(LC_NUMERIC)
    setlocale(LC_NUMERIC, ('it_IT', 'UTF-8'))
    try:
        return Decimal(delocalize(raw))
    finally:
        setlocale(LC_NUMERIC, locale)


def acc_by_year(rows: list[Row]) -> 'Iterator[tuple[int, Decimal]]':
    year_orig = None
    acc = ZERO
    for row in sorted(rows, key=lambda row: row.date):
        year = row.date.year

        if year_orig is None:
            year_orig = year
        elif year_orig != year:
            yield (year_orig, acc)
            year_orig = year

        acc += row.money

    if year_orig is not None:
        yield (year_orig, acc)


def acc_by_month(rows: list[Row]) -> 'Iterator[tuple[Decimal, int, int]]':
    year_orig = None
    month_orig = 1
    acc = ZERO
    for row in sorted(rows, key=lambda row: row.date):
        year = row.date.year
        month = row.date.month

        if year_orig is None:
            year_orig = year
            month_orig = month
        elif year_orig != year or month_orig != month:
            yield (acc, year_orig, month_orig)
            year_orig = year
            month_orig = month

        acc += row.money

    if year_orig is not None:
        yield (acc, year_orig, month_orig)


def main() -> None:
    basicConfig(format='%(message)s', level=INFO)

    today = datetime.now(tz=UTC).date()
    to = Period.from_date(today - timedelta(days=45))

    _, rows = read_txt(fn)
    for acc, year, month in acc_by_month(rows):
        if year >= to.year and month >= to.month_orig:
            reval = acc
        else:
            reval = rivaluta(Period.from_year_month(year, month), to, acc)

        logger.info('%s-%02d-01,%s,%s', year, month, acc, reval)


if __name__ == '__main__':
    main()
