# ruff: noqa: E501

from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest import TestCase

from movslib.libretto import read_libretto
from movslib.model import KV
from movslib.model import Row

PATH = f'{Path(__file__).parent}/test_libretto.xlsx'


class TestLibretto(TestCase):
    maxDiff = None

    def test_base(self) -> None:
        kv, rows = read_libretto(PATH)

        # kv
        self.assertEqual(
            KV(
                date(1990, 1, 1),
                date(2024, 9, 30),
                '',
                '000053361801',
                '',
                date(2024, 9, 30),
                Decimal('118384.98'),
                Decimal('118384.98'),
            ),
            kv,
        )

        # rows
        self.assertEqual(
            [
                Row(
                    data_contabile=date(2024, 9, 28),
                    data_valuta=date(2024, 9, 28),
                    addebiti=None,
                    accrediti=Decimal('910.45'),
                    descrizione_operazioni='INTERESSI DA SOMME ACCANTONATE PORTATE A SCADENZA',
                ),
                Row(
                    data_contabile=date(2024, 9, 6),
                    data_valuta=date(2024, 9, 6),
                    addebiti=None,
                    accrediti=Decimal('163.90'),
                    descrizione_operazioni='INTERESSI DA SOMME ACCANTONATE PORTATE A SCADENZA',
                ),
                Row(
                    data_contabile=date(2024, 9, 5),
                    data_valuta=date(2024, 9, 5),
                    addebiti=None,
                    accrediti=Decimal('91.06'),
                    descrizione_operazioni='INTERESSI DA SOMME ACCANTONATE PORTATE A SCADENZA',
                ),
                Row(
                    data_contabile=date(2024, 9, 3),
                    data_valuta=date(2024, 9, 3),
                    addebiti=None,
                    accrediti=Decimal('546.38'),
                    descrizione_operazioni='INTERESSI DA SOMME ACCANTONATE PORTATE A SCADENZA',
                ),
                Row(
                    data_contabile=date(2024, 9, 2),
                    data_valuta=date(2024, 9, 1),
                    addebiti=None,
                    accrediti=Decimal('273.19'),
                    descrizione_operazioni='INTERESSI DA SOMME ACCANTONATE PORTATE A SCADENZA',
                ),
                Row(
                    data_contabile=date(2024, 6, 3),
                    data_valuta=date(2024, 6, 3),
                    addebiti=None,
                    accrediti=Decimal('2400.00'),
                    descrizione_operazioni='GIROFONDO DA WEB DA CONTO BP CC 000091703983',
                ),
                Row(
                    data_contabile=date(2024, 4, 2),
                    data_valuta=date(2023, 12, 31),
                    addebiti=Decimal('61.20'),
                    accrediti=None,
                    descrizione_operazioni='IMPOSTA DI BOLLO PRODOTTI FINANZIARI',
                ),
                Row(
                    data_contabile=date(2024, 3, 30),
                    data_valuta=date(2024, 3, 30),
                    addebiti=None,
                    accrediti=Decimal('43.96'),
                    descrizione_operazioni='GIROFONDO DA WEB DA CONTO BP CC 000091703983',
                ),
                Row(
                    data_contabile=date(2024, 3, 30),
                    data_valuta=date(2024, 3, 30),
                    addebiti=None,
                    accrediti=Decimal('4978.02'),
                    descrizione_operazioni='GIROFONDO DA WEB DA CONTO BP CC 000091703983',
                ),
                Row(
                    data_contabile=date(2024, 1, 16),
                    data_valuta=date(2023, 12, 31),
                    addebiti=None,
                    accrediti=None,
                    descrizione_operazioni='COMPETENZE',
                ),
                Row(
                    data_contabile=date(2023, 10, 4),
                    data_valuta=date(2023, 10, 4),
                    addebiti=None,
                    accrediti=Decimal('20000.00'),
                    descrizione_operazioni='GIROFONDO DA WEB DA CONTO BP CC 000091703983',
                ),
                Row(
                    data_contabile=date(2023, 10, 4),
                    data_valuta=date(2023, 10, 4),
                    addebiti=None,
                    accrediti=Decimal('15000.00'),
                    descrizione_operazioni='GIROFONDO DA WEB DA CONTO BP CC 000091703983',
                ),
                Row(
                    data_contabile=date(2023, 10, 4),
                    data_valuta=date(2023, 10, 4),
                    addebiti=None,
                    accrediti=Decimal('15000.00'),
                    descrizione_operazioni='GIROFONDO DA WEB DA CONTO BP CC 000091703983',
                ),
                Row(
                    data_contabile=date(2023, 9, 12),
                    data_valuta=date(2023, 9, 12),
                    addebiti=None,
                    accrediti=Decimal('9039.22'),
                    descrizione_operazioni='ACCREDITO GIRO CONTO STESSO INTERMEDIARIO',
                ),
                Row(
                    data_contabile=date(2023, 9, 11),
                    data_valuta=date(2023, 9, 11),
                    addebiti=None,
                    accrediti=Decimal('5000.00'),
                    descrizione_operazioni='GIROFONDO DA APP DA CONTO BP CC 000091703983',
                ),
                Row(
                    data_contabile=date(2023, 9, 9),
                    data_valuta=date(2023, 9, 9),
                    addebiti=None,
                    accrediti=Decimal('15000.00'),
                    descrizione_operazioni='GIROFONDO DA WEB DA CONTO BP CC 000091703983',
                ),
                Row(
                    data_contabile=date(2023, 9, 8),
                    data_valuta=date(2023, 9, 8),
                    addebiti=None,
                    accrediti=Decimal('15000.00'),
                    descrizione_operazioni='GIROFONDO DA WEB DA CONTO BP CC 000091703983',
                ),
                Row(
                    data_contabile=date(2023, 9, 7),
                    data_valuta=date(2023, 9, 7),
                    addebiti=None,
                    accrediti=Decimal('15000.00'),
                    descrizione_operazioni='GIROFONDO DA WEB DA CONTO BP CC 000091703983',
                ),
            ],
            rows,
        )
