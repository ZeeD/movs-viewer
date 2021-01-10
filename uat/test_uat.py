import datetime
import decimal
import unittest

from movs import model
from mypyui import tabui


class TestUAT(unittest.TestCase):
    def test_simple_data(self) -> None:
        'dummy unit test... need user check'

        with tabui.main_window([
            row(1, 123),
            row(2, 456),
            row(3, -789),
            row(4, 101),
            row(5, -112),
            row(6, 13),
        ]) as main_window:
            main_window.show()


def row(day: int, euro: int) -> model.Row:
    data_contabile = data_valuta = datetime.date(2012, 1, day)
    addebiti = None if euro >= 0 else decimal.Decimal(-euro)
    accrediti = decimal.Decimal(euro) if euro >= 0 else None
    descrizione_operazioni = ''
    return model.Row(data_contabile,
                     data_valuta,
                     addebiti,
                     accrediti,
                     descrizione_operazioni)
