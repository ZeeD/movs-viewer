# ruff: noqa: E501

from datetime import date
from decimal import Decimal
from os import environ
from pathlib import Path
from typing import ClassVar
from typing import override
from unittest import TestCase

from jdk4py import JAVA_HOME

from movslib.estrattoconto import read_estrattoconto
from movslib.model import Row

PATH_1 = f'{Path(__file__).parent}/test_estrattoconto_1.pdf'
PATH_2 = f'{Path(__file__).parent}/test_estrattoconto_2.pdf'
PATH_3 = f'{Path(__file__).parent}/test_estrattoconto_3.pdf'


class TestEstrattoconto(TestCase):
    maxDiff = None
    _orig: ClassVar[str | None] = None

    @override
    @classmethod
    def setUpClass(cls) -> None:
        cls._orig = environ.get('JAVA_HOME', default=None)
        environ['JAVA_HOME'] = str(JAVA_HOME)
        super().setUpClass()

    @override
    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        if cls._orig is None:
            del environ['JAVA_HOME']
        else:
            environ['JAVA_HOME'] = cls._orig

    def test_base_path_1(self) -> None:
        kv, rows = read_estrattoconto(PATH_1)

        # kv
        self.assertEqual(date(2022, 8, 31), kv.da)
        self.assertEqual(date(2022, 8, 31), kv.a)
        self.assertEqual('Tutte', kv.tipo)
        self.assertEqual('001030700957', kv.conto_bancoposta)
        self.assertEqual('CHREIM ELENA DE TULLIO VITO', kv.intestato_a)
        self.assertEqual(date(2022, 8, 31), kv.saldo_al)
        self.assertEqual(Decimal('350.85'), kv.saldo_contabile)
        self.assertEqual(Decimal('350.85'), kv.saldo_disponibile)

        # rows
        expected_rows = [
            Row(
                date(2022, 8, 30),
                date(2022, 8, 26),
                Decimal('64.50'),
                None,
                'PAGAMENTO POS 26/08/2022 21.02 MU DELIVERY SRL MILANO ITA OPERAZIONE 663773 CARTA 92051516',
            ),
            Row(
                date(2022, 8, 30),
                date(2022, 8, 28),
                Decimal('8.46'),
                None,
                'PAGAMENTO POS 28/08/2022 11.42 COOP LOMBARDIA S.C. SESTO SAN GIO ITA OPERAZIONE 669857 CARTA 92051516',
            ),
            Row(
                date(2022, 8, 27),
                date(2022, 8, 25),
                Decimal('2.00'),
                None,
                'PAGAMENTO POS 25/08/2022 12.44 BESTIA BEER E STREET F VIMERCATE ITA OPERAZIONE 661849 CARTA 92051516',
            ),
            Row(
                date(2022, 8, 26),
                date(2022, 8, 23),
                Decimal('101.63'),
                None,
                'PAGAMENTO POS 23/08/2022 19.10 FOREXCHANGE-STAZ.C.GAL MILANO ITA OPERAZIONE 667748 CARTA 92051516',
            ),
            Row(
                date(2022, 8, 26),
                date(2022, 8, 23),
                Decimal('100.12'),
                None,
                'PAGAMENTO POS 23/08/2022 19.16 FOREXCHANGE-STAZ.C.GAL MILANO ITA OPERAZIONE 663939 CARTA 92051516',
            ),
            Row(
                date(2022, 8, 23),
                date(2022, 8, 20),
                Decimal('26.47'),
                None,
                'PAGAMENTO POS 20/08/2022 18.57 COOP LOMBARDIA S.C. SESTO SAN GIO ITA OPERAZIONE 663495 CARTA 92051516',
            ),
            Row(
                date(2022, 8, 22),
                date(2022, 8, 21),
                Decimal('3.87'),
                None,
                'PAGAMENTO POS 21/08/2022 11.50 3584 MARKET MILANO MILANO ITA OPERAZIONE 669376 CARTA 92051516',
            ),
            Row(
                date(2022, 8, 22),
                date(2022, 8, 22),
                Decimal('30.22'),
                None,
                'ADDEBITO DIRETTO SDD Wind Tre S.p. CID.IT960020000013378520152 210822 MAN.O66791531390614',
            ),
            Row(
                date(2022, 8, 20),
                date(2022, 8, 18),
                Decimal('11.00'),
                None,
                'PAGAMENTO POS 18/08/2022 13.22 CASAVIETNAM DI NGUYEN. MILANO ITA OPERAZIONE 668501 CARTA 35438808',
            ),
            Row(
                date(2022, 8, 18),
                date(2022, 8, 15),
                Decimal('3.90'),
                None,
                'PAGAMENTO POS 15/08/2022 13.21 ROSSOPOMODORO MONZA ITA OPERAZIONE 665159 CARTA 92051516',
            ),
            Row(
                date(2022, 8, 17),
                date(2022, 8, 13),
                Decimal('30.10'),
                None,
                'PAGAMENTO POS 13/08/2022 17.31 COOP LOMBARDIA S.C. SESTO SAN GIO ITA OPERAZIONE 661180 CARTA 92051516',
            ),
            Row(
                date(2022, 8, 17),
                date(2022, 8, 13),
                Decimal('7.00'),
                None,
                'PAGAMENTO POS 13/08/2022 09.22 SumUp *Sun Strac Map Milano ITA OPERAZIONE 669406 CARTA 92051516',
            ),
            Row(
                date(2022, 8, 11),
                date(2022, 8, 10),
                Decimal('6.45'),
                None,
                'PAGAMENTO POS 10/08/2022 10.51 3584 MARKET MILANO MILANO ITA OPERAZIONE 669267 CARTA 92051516',
            ),
            Row(
                date(2022, 8, 10),
                date(2022, 8, 10),
                None,
                Decimal('400.00'),
                'BONIFICO TRN BAPPIT22 5034000470672221480160001753IT DA CHREIM ELENA PER Settembre Ele',
            ),
            Row(
                date(2022, 8, 10),
                date(2022, 8, 7),
                Decimal('18.10'),
                None,
                'PAGAMENTO POS 07/08/2022 11.44 1 H CLEAN DI ROZZA GIU SESTO SAN GIO ITA OPERAZIONE 656532 CARTA 92051516',
            ),
            Row(
                date(2022, 8, 9),
                date(2022, 8, 9),
                Decimal('626.92'),
                None,
                "BONIFICO TRN EA22080931258833480160020400IT BENEF BANCA DI CREDITO COOPERATIVO PER Gestione ordinaria 2022/2023 unita': 07, 31 1",
            ),
            Row(
                date(2022, 8, 9),
                date(2022, 8, 9),
                None,
                Decimal('400.00'),
                'BONIFICO TRN BAPPIT22 5034000457292220480160001753IT DA CHREIM ELENA PER Agosto ele',
            ),
            Row(
                date(2022, 8, 9),
                date(2022, 8, 9),
                None,
                Decimal('400.00'),
                'POSTAGIRO TRN BPPIITRR EA22080929158352PO0400004000IT DA DE TULLIO VITO GELAO MARIA PER Agosto 2022',
            ),
            Row(
                date(2022, 8, 9),
                date(2022, 8, 7),
                Decimal('39.89'),
                None,
                'PAGAMENTO POS 07/08/2022 12.37 COOP LOMBARDIA S.C. SESTO SAN GIO ITA OPERAZIONE 652851 CARTA 92051516',
            ),
            Row(
                date(2022, 8, 9),
                date(2022, 8, 7),
                Decimal('7.50'),
                None,
                'PAGAMENTO POS 07/08/2022 09.43 LLOA BE NATURAL MILANO ITA OPERAZIONE 650894 CARTA 92051516',
            ),
            Row(
                date(2022, 8, 8),
                date(2022, 7, 31),
                Decimal('1.00'),
                None,
                'CANONE MENSILE CARTA DI DEBITO MESE DI RIFERIMENTO 2022/07',
            ),
            Row(
                date(2022, 8, 8),
                date(2022, 7, 31),
                Decimal('1.00'),
                None,
                'CANONE MENSILE CARTA DI DEBITO MESE DI RIFERIMENTO 2022/07',
            ),
            Row(
                date(2022, 8, 7),
                date(2022, 8, 7),
                Decimal('250.00'),
                None,
                'POSTAGIRO TRN EA22080727951725PO0160020400IT BENEF Elena Cavagnis PER Regalo da Vito e Elena per i neo sposi. Vi auguriamo ogni be',
            ),
            Row(
                date(2022, 8, 7),
                date(2022, 8, 7),
                None,
                Decimal('400.00'),
                'POSTAGIRO TRN BPPIITRR EA22080727947325PO0400004000IT DA DE TULLIO VITO GELAO MARIA PER Agosto 2022',
            ),
            Row(
                date(2022, 8, 5),
                date(2022, 8, 3),
                Decimal('69.50'),
                None,
                'PAGAMENTO POS 03/08/2022 20.49 YAMAMOTO SRL MILANO ITA OPERAZIONE 654684 CARTA 92051516',
            ),
            Row(
                date(2022, 8, 4),
                date(2022, 8, 4),
                Decimal('201.00'),
                None,
                'ADDEBITO DIRETTO SDD A2A SPA CID.IT17ENE0000011957540153 040822 MAN.00000000000000000000007020761594001',
            ),
            Row(
                date(2022, 8, 3),
                date(2022, 7, 31),
                Decimal('29.00'),
                None,
                'PAGAMENTO POS 31/07/2022 22.11 FANCYTOAST MILANO ITA OPERAZIONE 659917 CARTA 92051516',
            ),
            Row(
                date(2022, 8, 2),
                date(2022, 7, 29),
                Decimal('36.50'),
                None,
                'PAGAMENTO POS 29/07/2022 20.35 BESTIA BEER E STREET F VIMERCATE ITA OPERAZIONE 659080 CARTA 92051516',
            ),
            Row(
                date(2022, 8, 2),
                date(2022, 7, 29),
                Decimal('22.00'),
                None,
                'PAGAMENTO POS 29/07/2022 21.08 HAMBU VIMERCATE VIMERCATE ITA OPERAZIONE 657526 CARTA 92051516',
            ),
            Row(
                date(2022, 8, 2),
                date(2022, 7, 30),
                Decimal('16.82'),
                None,
                'PAGAMENTO POS 30/07/2022 11.39 COOP LOMBARDIA S.C. SESTO SAN GIO ITA OPERAZIONE 652381 CARTA 92051516',
            ),
            Row(
                date(2022, 8, 2),
                date(2022, 7, 31),
                Decimal('2.00'),
                None,
                'CANONE CONTO CLICK ADDEBITO RELATIVO AL PERIODO DI LUGLIO 2022',
            ),
            Row(
                date(2022, 8, 1),
                date(2022, 8, 1),
                Decimal('1.00'),
                None,
                'COMMISSIONE RICARICA POSTEPAY Ricarica Postepay',
            ),
            Row(
                date(2022, 8, 1),
                date(2022, 8, 1),
                Decimal(1500),
                None,
                'RICARICA POSTEPAY DA WEB/APP Ricarica Postepay',
            ),
            Row(
                date(2022, 8, 1),
                date(2022, 8, 1),
                None,
                Decimal(1500),
                'BONIFICO TRN BAPPIT22 5034004217772210480160001753IT DA CHREIM ELENA PER Viaggio America',
            ),
        ]

        self.assertEqual(expected_rows, rows)

    def test_path_2(self) -> None:
        _ = read_estrattoconto(PATH_2)

    def test_path_3(self) -> None:
        _, rows = read_estrattoconto(PATH_3)

        descrizione_operazioni = {row.descrizione_operazioni for row in rows}
        self.assertNotIn('TOTALE USCITE', descrizione_operazioni)
        self.assertNotIn('TOTALE ENTRATE', descrizione_operazioni)
