from datetime import date
from decimal import Decimal
from typing import Final

from movslib.model import KV
from movslib.model import ZERO
from movslib.model import Row

from _support.basetest import BaseTest
from _support.tmp_txt import tmp_txt
from movsviewer.chartview import ChartView


class TestChartView(BaseTest):
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
        with tmp_txt(self.kv, self.csv) as data_path:
            chart_view = ChartView(data_path)
        self.widgets.append(chart_view)
