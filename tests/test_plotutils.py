from datetime import date
from decimal import Decimal
from typing import Final
from unittest.case import TestCase

from movslib.model import Row
from movslib.model import Rows
from movsviewer.plotutils import _acc_reset_by_year

D_20200101: Final = date(2020, 1, 1)
D_20200102: Final = date(2020, 1, 2)
D_20210101: Final = date(2021, 1, 1)
D_20210102: Final = date(2021, 1, 2)
D_20220101: Final = date(2022, 1, 1)
D_0: Final = Decimal(0)
D_10: Final = Decimal(10)
D_20: Final = Decimal(20)
D_30: Final = Decimal(30)
D_40: Final = Decimal(30)
D_50: Final = Decimal(30)


class TestPlotUtils(TestCase):
    def test_acc_reset_by_year_emtpy(self) -> None:
        rows = Rows('', [])
        expected: list[tuple[date, Decimal]] = []
        actual = list(_acc_reset_by_year(rows))

        self.assertListEqual(expected, actual)

    def test_acc_reset_by_year_one(self) -> None:
        rows = Rows('', [Row(D_20200101, D_20200101, None, D_10, '')])
        expected = [(D_20200101, D_10)]
        actual = list(_acc_reset_by_year(rows))

        self.assertListEqual(expected, actual)

    def test_acc_reset_by_year_two_same_year(self) -> None:
        rows = Rows(
            '',
            [
                Row(D_20200101, D_20200101, None, D_10, ''),
                Row(D_20200102, D_20200102, None, D_20, ''),
            ],
        )
        expected = [(D_20200101, D_10), (D_20200102, D_10 + D_20)]
        actual = list(_acc_reset_by_year(rows))

        self.assertListEqual(expected, actual)

    def test_acc_reset_by_year_two_cross_year(self) -> None:
        rows = Rows(
            '',
            [
                Row(D_20200101, D_20200101, None, D_10, ''),
                Row(D_20210101, D_20210101, None, D_20, ''),
            ],
        )
        expected = [(D_20200101, D_10), (D_20210101, D_20)]
        actual = list(_acc_reset_by_year(rows))

        self.assertListEqual(expected, actual)

    def test_acc_reset_by_year_generic(self) -> None:
        rows = Rows(
            '',
            [
                Row(D_20200101, D_20200101, None, D_10, ''),
                Row(D_20200102, D_20200102, D_20, None, ''),
                Row(D_20210101, D_20210101, None, D_30, ''),
                Row(D_20210102, D_20210102, D_40, None, ''),
                Row(D_20220101, D_20220101, None, D_50, ''),
            ],
        )
        expected = [
            (D_20200101, D_10),
            (D_20200102, D_10 - D_20),
            (D_20210101, D_30),
            (D_20210102, D_30 - D_40),
            (D_20220101, D_50),
        ]
        actual = list(_acc_reset_by_year(rows))

        self.assertListEqual(expected, actual)
