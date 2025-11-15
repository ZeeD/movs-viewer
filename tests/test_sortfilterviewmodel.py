from datetime import date
from decimal import Decimal
from typing import Final
from unittest.case import TestCase

from guilib.chartwidget.model import Column
from guilib.chartwidget.model import ColumnHeader
from guilib.chartwidget.model import Info
from guilib.chartwidget.viewmodel import SortFilterViewModel as SFVMguilib
from movslib.model import KV
from movslib.model import ZERO
from movslib.model import Row
from PySide6.QtWidgets import QTableView

from _support.tmpapp import tmp_app
from _support.tmptxt import tmp_txt
from movsviewer.viewmodel import SortFilterViewModel as SFVMmovsviewer


class TestSortFilterViewModel(TestCase):
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
            accrediti=Decimal(100 - (10 * m)),
            descrizione_operazioni='',
        )
        for m in range(1, 10)
    ]

    def test_sort_filter_view_model(self) -> None:
        with tmp_app() as widgets, tmp_txt(self.kv, self.csv) as data_path:
            m_movsviewer = SFVMmovsviewer(data_path)
            v_movsviewer = QTableView()
            v_movsviewer.setWindowTitle('movsviewer')
            v_movsviewer.setModel(m_movsviewer)
            widgets.append(v_movsviewer)

            m_guilib = SFVMguilib()
            m_guilib.update(
                [
                    Info(
                        row.date,
                        [
                            Column(ColumnHeader('addebiti', '€'), row.addebiti),
                            Column(
                                ColumnHeader('accrediti', '€'), row.accrediti
                            ),
                            Column(
                                ColumnHeader('descrizione_operazioni', '€'),
                                row.descrizione_operazioni,  # type: ignore[arg-type]
                            ),
                        ],
                    )
                    for row in self.csv
                ]
            )
            v_guilib = QTableView()
            v_guilib.setWindowTitle('guilib')
            v_guilib.setModel(m_guilib)
            widgets.append(v_guilib)
