from datetime import date
from decimal import Decimal
from unittest import TestCase

from movslib.model import ZERO
from movslib.model import Row
from movslib.model import Rows

DATA_CONTABILE = date(2022, 11, 5)
DATA_VALUTA = date(2022, 11, 6)
ADDEBITI = Decimal(123)
ACCREDITI: None = None
DESCRIZIONE_OPERAZIONI = 'DESCRIZIONE_OPERAZIONI'


class TestRow(TestCase):
    def test_money(self) -> None:
        money = Decimal(123)
        for expected, addebiti, accrediti in (
            (-money, money, None),
            (money, None, money),
            (ZERO, None, None),
        ):
            with self.subTest(
                expected=expected, accrediti=accrediti, addebiti=addebiti
            ):
                self.assertEqual(
                    expected,
                    Row(
                        DATA_CONTABILE,
                        DATA_VALUTA,
                        addebiti,
                        accrediti,
                        DESCRIZIONE_OPERAZIONI,
                    ).money,
                )

    def test_date_is_data_valuta(self) -> None:
        self.assertEqual(
            DATA_VALUTA,
            Row(
                DATA_CONTABILE,
                DATA_VALUTA,
                ADDEBITI,
                ACCREDITI,
                DESCRIZIONE_OPERAZIONI,
            ).date,
        )


NAME = 'name'


class TestRows(TestCase):
    def test_ctor(self) -> None:
        self.assertEqual(NAME, Rows(NAME).name)
