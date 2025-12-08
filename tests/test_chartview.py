from datetime import date
from decimal import Decimal
from typing import Final
from unittest.case import TestCase

from _support.tmpapp import tmp_app
from _support.tmptxt import tmp_txt
from movslib.model import KV
from movslib.model import ZERO
from movslib.model import Row
from movsviewer.chartview import ChartWidgetWrapper


class TestChartView(TestCase):
    kv: Final = KV(
        da=None,
        a=None,
        tipo='',
        conto_bancoposta='',
        intestato_a='',
        saldo_al=None,
        saldo_contabile=ZERO,
        saldo_disponibile=ZERO,
    )
    csv: Final = [
        Row(
            data_contabile=date(2024, m, 1),
            data_valuta=date(2024, m, 1),
            addebiti=None,
            accrediti=Decimal(10 * m),
            descrizione_operazioni='',
        )
        for m in range(1, 10)
    ]

    def test_chart_view(self) -> None:
        with tmp_app() as widgets, tmp_txt(self.kv, self.csv) as data_path:
            widgets.append(ChartWidgetWrapper(data_path))
