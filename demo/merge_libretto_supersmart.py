from dataclasses import dataclass
from datetime import date
from datetime import datetime
from decimal import Decimal
from functools import reduce
from json import load
from locale import LC_TIME
from locale import setlocale
from logging import INFO
from logging import basicConfig
from logging import getLogger
from operator import add
from pathlib import Path
from shlex import quote
from sys import argv
from typing import TYPE_CHECKING
from typing import Final
from typing import TypedDict
from zoneinfo import ZoneInfo

from movslib.model import KV
from movslib.model import Row
from movslib.movs import write_txt
from movslib.reader import read

if TYPE_CHECKING:
    from collections.abc import Iterator

logger = getLogger(__name__)

ACC_FN: Final = (
    '/home/zed/eclipse-workspace/movs-data/RPOL_accumulator_libretto.txt'
)
ATTIVE_FN: Final = '/home/zed/Desktop/attive.json'
SCADUTE_FN: Final = '/home/zed/Desktop/scadute.json'


class Attive(TypedDict):
    tipologia: str
    scadenza: str
    importo: str
    tasso: str
    attivazione: str
    durata: str
    lordi: str
    netti: str


class Scadute(TypedDict):
    tipologia: str
    scadenza: str
    importo: str
    accreditati: str
    attivazione: str
    durata: str
    tasso: str


def dt(raw: str) -> date:
    setlocale(LC_TIME, 'it_IT.UTF-8')
    return (
        datetime.strptime(raw.lower(), '%d %b %Y')
        .replace(tzinfo=ZoneInfo('Europe/Rome'))
        .date()
    )


def d(raw: str) -> Decimal:
    return Decimal(raw.split(None, 1)[0].replace('.', '').replace(',', '.'))


def extend(csv: list[Row], *rows: Row) -> 'Iterator[Decimal]':
    for row in rows:
        for i, e in enumerate(csv):
            if row.date < e.date:
                continue
            csv.insert(i, row)
            yield row.money
            break


@dataclass
class C:
    i: int
    b: bool

    def __index__(self) -> int:
        return self.i

    def __bool__(self) -> bool:
        return self.b


def contains(
    csv: list[Row],
    date_: date,
    addebiti: Decimal | None,
    accrediti: Decimal | None,
    descrizione_operazioni: str,
) -> C:
    for i, e in enumerate(csv):
        if (
            e.date == date_
            and e.addebiti == addebiti
            and e.accrediti == accrediti
            and e.descrizione_operazioni == descrizione_operazioni
        ):
            return C(i, b=True)
    return C(-1, b=False)


def merge_libretto_supersmart(
    acc_fn: str, attive_fn: str, scadute_fn: str
) -> None:
    # load data
    kv, csv = read(acc_fn)
    with Path(attive_fn).open() as fp:
        attive: list[Attive] = load(fp)
    with Path(scadute_fn).open() as fp:
        scadute: list[Scadute] = load(fp)

    saldo = kv.saldo_contabile

    # convert and maybe insert new attive
    for attiva in attive:
        a = dt(attiva['attivazione'])
        msg = f'{attiva["tipologia"]},{attiva["durata"]},{attiva["tasso"]}'
        do_s = f'sottoscrizione {msg}'
        do_r = f'rimborso {msg}'
        do_p = f'previsione {msg}'
        i = d(attiva['importo'])
        s = dt(attiva['scadenza'])
        n = d(attiva['netti'])

        # add up to 3 rows:
        # sottoscrizione w/ importo @ attivazione
        # rimborso w/ importo @ scadenza
        # previsione w/ netti @ scadenza
        if not contains(csv, a, i, None, do_s):
            saldo = reduce(
                add,
                extend(
                    csv,
                    Row(
                        data_contabile=a,
                        data_valuta=a,
                        addebiti=i,
                        accrediti=None,
                        descrizione_operazioni=do_s,
                    ),
                ),
                saldo,
            )
        if not contains(csv, s, None, i, do_r):
            saldo = reduce(
                add,
                extend(
                    csv,
                    Row(
                        data_contabile=s,
                        data_valuta=s,
                        addebiti=None,
                        accrediti=i,
                        descrizione_operazioni=do_r,
                    ),
                ),
                saldo,
            )
        if not contains(csv, s, None, n, do_p):  # TODO: or
            saldo = reduce(
                add,
                extend(
                    csv,
                    Row(
                        data_contabile=s,
                        data_valuta=s,
                        addebiti=None,
                        accrediti=n,
                        descrizione_operazioni=do_p,
                    ),
                ),
                saldo,
            )

    # convert and maybe delete new scadute
    for scaduta in scadute:
        s = dt(scaduta['scadenza'])
        a = dt(scaduta['attivazione'])
        i = d(scaduta['importo'])
        msg = f'{scaduta["tipologia"]},{scaduta["durata"]},{scaduta["tasso"]}'
        do_s = f'sottoscrizione {msg}'
        do_r = f'rimborso {msg}'

        # add up to 2 rows:
        # sottoscrizione w/ importo @ attivazione
        # rimborso w/ importo @ scadenza
        if not contains(csv, a, i, None, do_s):
            saldo = reduce(
                add,
                extend(
                    csv,
                    Row(
                        data_contabile=a,
                        data_valuta=a,
                        addebiti=i,
                        accrediti=None,
                        descrizione_operazioni=do_s,
                    ),
                ),
                saldo,
            )
        if not contains(csv, a, None, i, do_r):
            row = Row(
                data_contabile=s,
                data_valuta=s,
                addebiti=None,
                accrediti=i,
                descrizione_operazioni=do_r,
            )
            if c := contains(csv, s, None, round(i, 2), do_r):
                csv[c] = row
            else:
                saldo = reduce(add, extend(csv, row), saldo)

        if False:  # TODO: check if previsione has been removed
            pass

    # allow retries
    dst_fn = f'{acc_fn}~'
    write_txt(
        dst_fn,
        KV(
            da=kv.da,
            a=kv.a,
            tipo=kv.tipo,
            conto_bancoposta=kv.conto_bancoposta,
            intestato_a=kv.intestato_a,
            saldo_al=kv.saldo_al,
            saldo_contabile=saldo,
            saldo_disponibile=saldo,
        ),
        csv,
    )
    logger.info('kdiff3 %s %s', quote(acc_fn), quote(dst_fn))


def main() -> None:
    basicConfig(format='%(message)s', level=INFO)

    if not argv[1:]:
        logger.warning(
            'Usage: %s ACCUMULATOR.txt ATTIVE.json SCADUTE.json', argv[0]
        )
        acc_fn, attive_fn, scadute_fn = ACC_FN, ATTIVE_FN, SCADUTE_FN
    else:
        acc_fn, attive_fn, scadute_fn = argv[1:]

    merge_libretto_supersmart(acc_fn, attive_fn, scadute_fn)


if __name__ == '__main__':
    main()
