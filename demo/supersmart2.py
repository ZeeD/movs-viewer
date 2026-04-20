"""Reset libretto with supersmart from scratch."""

from datetime import date
from decimal import Decimal
from json import load
from pathlib import Path
from typing import Final
from typing import TypedDict

from movslib.model import KV
from movslib.model import Row
from movslib.movs import write_txt
from movsmerger.movsmerger import merge_files
from movsvalidator.movsvalidator import validate

MOVIMENTI_2: Final = '/home/zed/Desktop/movimenti_libretto_000053361801.xlsx'
MOVIMENTI_1: Final = '/home/zed/Desktop/movimenti_libretto_000053361801-2.xlsx'
SEARCH: Final = Path('/home/zed/Desktop/search.json')
OUTPUT_1: Final = (
    '/home/zed/eclipse-workspace/movs-data/RPOL_accumulator_libretto1.txt'
)
OUTPUT_2: Final = (
    '/home/zed/eclipse-workspace/movs-data/RPOL_accumulator_libretto2.txt'
)


class SearchE(TypedDict):
    progressivo: str
    tipologia: str
    descrizioneCommerciale: str
    dataScadenza: str
    dataAttivazione: str
    dataDisattivazione: str
    importo: str
    interessiAccreditati: str
    numeroPVR: str
    durata: str
    tassoInteresse: str
    interessiLordi: str
    segnoInteressiLordi: str
    interessiNetti: str
    segnoInteressiNetti: str
    tassoAnnuoLordoAScadenza: str
    status: str


def parse_search_e(search_e: SearchE) -> list[Row]:
    descrizione_commerciale = search_e['descrizioneCommerciale']
    data_scadenza = date.fromisoformat(search_e['dataScadenza'])
    data_attivazione = date.fromisoformat(search_e['dataAttivazione'])
    importo = Decimal(search_e['importo'])
    interessi_accreditati = Decimal(search_e['interessiAccreditati'])
    durata = search_e['durata']
    tasso_interesse = f'{float(search_e["tassoInteresse"]):0.2f}'.replace(
        '.', ','
    )
    status = search_e['status']

    msg = f'{descrizione_commerciale},{durata} giorni,{tasso_interesse} %'

    # 2 o 3 rows:
    # se status == 'SCADUTA' allora nell'excel ci devono essere gli interessi
    # se status == 'ATTIVA' allora si inserisce previsione

    if status not in ('SCADUTA', 'ATTIVA'):
        raise ValueError

    ret = [
        # sottoscrizione + rimborso
        Row(
            data_contabile=data_attivazione,
            data_valuta=data_attivazione,
            addebiti=importo,
            accrediti=None,
            descrizione_operazioni=f'sottoscrizione {msg}',
        ),
        Row(
            data_contabile=data_scadenza,
            data_valuta=data_scadenza,
            addebiti=None,
            accrediti=importo,
            descrizione_operazioni=f'rimborso {msg}',
        ),
    ]

    if status == 'ATTIVA':
        # previsione
        ret.append(
            Row(
                data_contabile=data_scadenza,
                data_valuta=data_scadenza,
                addebiti=None,
                accrediti=interessi_accreditati,
                descrizione_operazioni=f'previsione {msg}',
            )
        )

    return ret




def main() -> None:
    kv, csv = merge_files(MOVIMENTI_1, MOVIMENTI_2)

    write_txt(OUTPUT_1, kv, csv)
    messages_1: Final[list[str]] = []
    validate(OUTPUT_1, messages_1)
    print('\n'.join(messages_1))


    with SEARCH.open() as fp:
        search: list[SearchE] = load(fp)

    saldo_contabile = kv.saldo_disponibile
    for search_e in search:
        (_, _, *prevs) = rows = parse_search_e(search_e)
        csv.extend(rows)
        for previsione in prevs:
            saldo_contabile += previsione.accrediti or Decimal(0)

    csv = [ d[2] for d in sorted(((row.date, -row.money, row) for row in csv), reverse=True)]

    write_txt(
        OUTPUT_2,
        KV(
            da=kv.da,
            a=kv.a,
            tipo=kv.tipo,
            conto_bancoposta=kv.conto_bancoposta,
            intestato_a=kv.intestato_a,
            saldo_al=kv.saldo_al,
            saldo_contabile=saldo_contabile,
            saldo_disponibile=kv.saldo_disponibile,
        ),
        csv,
    )
    messages_2: Final[list[str]] = []
    validate(OUTPUT_2, messages_2)
    print('\n'.join(messages_2))


if __name__ == '__main__':
    main()
