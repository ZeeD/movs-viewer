from datetime import date
from decimal import Decimal
from io import StringIO
from unittest import TestCase

from movslib.model import KV
from movslib.model import Row
from movslib.movs import conv_date
from movslib.movs import conv_date_inv
from movslib.movs import fmt_value
from movslib.movs import read_csv
from movslib.movs import read_kv
from movslib.movs import write_kv


class TestMovs(TestCase):
    def test_conv_date(self) -> None:
        expected = date(1982, 5, 11)
        actual = conv_date('11/05/1982')

        self.assertEqual(expected, actual)

    def test_conv_date_invalid(self) -> None:
        expected = None
        actual = conv_date('invalid')

        self.assertEqual(expected, actual)

    def test_conv_date_inv(self) -> None:
        expected = '11/05/1982'
        actual = conv_date_inv(date(1982, 5, 11))

        self.assertEqual(expected, actual)

    def test_read_kv(self) -> None:
        expected = KV(
            None,
            None,
            'tipo',
            'conto_bancoposta',
            'intestato_a',
            None,
            Decimal(0),
            Decimal(0),
        )
        actual = read_kv(
            iter(
                (
                    '',
                    '',
                    ': tipo',
                    ': conto_bancoposta',
                    ': intestato_a',
                    '',
                    ': 0_____',
                    ': 0_____',
                )
            )
        )

        self.assertEqual(expected, actual)

    def test_fmt_value_none(self) -> None:
        expected = ''
        actual = fmt_value(None, lambda _: '')

        self.assertEqual(expected, actual)

    def test_fmt_value_date(self) -> None:
        expected = '11/05/1982'
        actual = fmt_value(date(1982, 5, 11), lambda _: '')

        self.assertEqual(expected, actual)

    def test_fmt_value_decimal(self) -> None:
        expected = '_1_'
        actual = fmt_value(Decimal(1), lambda d: f'_{d}_')

        self.assertEqual(expected, actual)

    def test_fmt_value_str(self) -> None:
        expected = 'foo'
        actual = fmt_value('foo', lambda _: '')

        self.assertEqual(expected, actual)

    def test_write_kv(self) -> None:
        expected = (
            ' da: (gg/mm/aaaa): \n'
            ' a: (gg/mm/aaaa): \n'
            ' Tipo(operazioni): tipo\n'
            ' Conto BancoPosta n.: conto_bancoposta\n'
            ' Intestato a: intestato_a\n'
            ' Saldo al: \n'
            ' Saldo contabile: +0 Euro\n'
            ' Saldo disponibile: +0 Euro\n'
        )
        with StringIO() as stringio:
            write_kv(
                stringio,
                KV(
                    None,
                    None,
                    'tipo',
                    'conto_bancoposta',
                    'intestato_a',
                    None,
                    Decimal(0),
                    Decimal(0),
                ),
            )
            actual = stringio.getvalue()

        self.assertEqual(expected, actual)

    def test_read_csv(self) -> None:
        expected = [
            Row(date(1982, 5, 11), date(2022, 5, 11), Decimal(12), None, '')
        ]
        actual = read_csv(('', ' 11/05/1982       11/05/2022    12'))

        self.assertListEqual(expected, list(actual))

        with self.assertRaises(ValueError):
            list(read_csv(('', '')))

        with self.assertRaises(ValueError):
            list(read_csv(('', ' 11/05/1982')))

    def test_write_csv(self) -> None:
        expected = [
            Row(date(1982, 5, 11), date(2022, 5, 11), Decimal(12), None, '')
        ]
        actual = read_csv(('', ' 11/05/1982       11/05/2022    12'))

        self.assertListEqual(expected, list(actual))

        with self.assertRaises(ValueError):
            list(read_csv(('', '')))

        with self.assertRaises(ValueError):
            list(read_csv(('', ' 11/05/1982')))
