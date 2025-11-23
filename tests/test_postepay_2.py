from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest import TestCase

from movslib.model import KV
from movslib.model import Row
from movslib.postepay import read_postepay

PATH = f'{Path(__file__).parent}/test_postepay_2.pdf'


class TestPostepay2(TestCase):
    maxDiff = None

    def test_base(self) -> None:
        expected_kv = KV(
            None,
            None,
            '',
            '535574******7907',
            'DE TULLIO VITO',
            date(2025, 9, 14),
            Decimal(0),
            Decimal(0),
        )
        expected_rows_0 = Row(
            date(2025, 9, 10),
            date(2025, 9, 8),
            Decimal('20.10'),
            None,
            "PAGAMENTO POS MIVA'LA'  MILANO              ITA",
        )

        actual_kv, actual_rows = read_postepay(PATH)

        # kv
        self.assertEqual(expected_kv.da, actual_kv.da)
        self.assertEqual(expected_kv.a, actual_kv.a)
        self.assertEqual(expected_kv.tipo, actual_kv.tipo)
        self.assertEqual(
            expected_kv.conto_bancoposta, actual_kv.conto_bancoposta
        )
        self.assertEqual(expected_kv.intestato_a, actual_kv.intestato_a)
        self.assertEqual(expected_kv.saldo_al, actual_kv.saldo_al)
        self.assertEqual(expected_kv.saldo_contabile, actual_kv.saldo_contabile)
        self.assertEqual(
            expected_kv.saldo_disponibile, actual_kv.saldo_disponibile
        )

        # rows
        actual_rows_0 = actual_rows[0]

        self.assertEqual(
            expected_rows_0.data_contabile, actual_rows_0.data_contabile
        )
        self.assertEqual(expected_rows_0.data_valuta, actual_rows_0.data_valuta)
        self.assertEqual(expected_rows_0.addebiti, actual_rows_0.addebiti)
        self.assertEqual(expected_rows_0.accrediti, actual_rows_0.accrediti)
        self.assertEqual(
            expected_rows_0.descrizione_operazioni,
            actual_rows_0.descrizione_operazioni,
        )
