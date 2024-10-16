from datetime import date
from decimal import Decimal
from typing import Final
from unittest.case import TestCase

from movslib.model import KV
from movslib.model import ZERO
from movslib.model import Row

from _support.tmpapp import tmp_app
from _support.tmptxt import tmp_txt
from movsviewer.mainui import NewMainui
from movsviewer.mainui import Settingsui
from movsviewer.settings import Settings


class TestNewMainui(TestCase):
    r: Final = list(range(1, 10))
    s: Final = sum((Decimal(10 * m) for m in r), ZERO)
    kv: Final = KV(
        da=None,
        a=None,
        tipo='',
        conto_bancoposta='',
        intestato_a='',
        saldo_al=None,
        saldo_contabile=s,
        saldo_disponibile=s,
    )
    csv: Final = [
        Row(
            data_contabile=date(2024, m, 1),
            data_valuta=date(2024, m, 1),
            addebiti=None,
            accrediti=Decimal(10 * m),
            descrizione_operazioni='',
        )
        for m in r
    ]

    def test_new_mainui(self) -> None:
        with tmp_app() as widgets, tmp_txt(self.kv, self.csv) as data_path:
            settings = Settings([data_path])
            settingsui = Settingsui()

            new_mainui = NewMainui()
            mainui = new_mainui(settings, settingsui)
            widgets.append(mainui)
