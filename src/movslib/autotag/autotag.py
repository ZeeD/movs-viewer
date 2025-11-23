from typing import TYPE_CHECKING

from movslib.autotag.model import TagRow
from movslib.autotag.model import TagRows
from movslib.autotag.model import Tags

if TYPE_CHECKING:
    from movslib.model import Row
    from movslib.model import Rows


def autotag(rows: 'Rows') -> TagRows:
    return TagRows(rows.name, map(_autotag_row, rows))


def _autotag_row(row: 'Row') -> TagRow:
    """Add zero, one, or more tags to a row, based on patterns."""
    accrediti = row.accrediti
    descrizione_operazioni = row.descrizione_operazioni

    ret = TagRow(
        row.data_contabile,
        row.data_valuta,
        row.addebiti,
        accrediti,
        descrizione_operazioni,
    )

    if accrediti is not None:
        ret.tags.add(Tags.ENTRATE)

    for pattern, tags in [('BONIFICO SEPA', [Tags.BONIFICO])]:
        if pattern in descrizione_operazioni and accrediti is not None:
            ret.tags.update(tags)

    for pattern, tags in [
        (p, [Tags.COMMISSIONI])
        for p in ['COMMISSIONI', 'CANONE', 'IMPOSTA DI BOLLO']
    ]:
        if descrizione_operazioni.startswith(pattern):
            ret.tags.update(tags)

    for pattern, tags in {
        'AUTOSTRADA': [Tags.AUTOSTRADA],
        'ENEL ENERGIA': [Tags.BOLLETTE, Tags.LUCE],
        'Wind Tre S.p.A.': [Tags.BOLLETTE, Tags.TELEFONO],
        'WIND TRE S P A': [Tags.BOLLETTE, Tags.TELEFONO],
        'SORGENIA S P A': [Tags.BOLLETTE, Tags.GAS],
        'FASTWEB': [Tags.BOLLETTE, Tags.TELEFONO],
        **{
            p: [Tags.SPESA]
            for p in (
                'ESSELUNGA',
                'EUROSPIN',
                'IPERCOOP',
                'SUPERMERCATO',
                'IL GIGANTE',
                'ALDI',
            )
        },
        'RICARICA POSTEPAY': [Tags.RICARICA_POSTEPAY],
        **{
            p: [Tags.CONDOMINIO]
            for p in (
                'STUDIO RAG. ANDREA IANNUZZI',
                'Gestione ordinaria',
                '-CMAV-',
                'ORDINARIA',
                'anticipata',
                'RIFACIMENTO IMPIANTO VIDEOCITOF',
                'ANTICIPATA',
                'TINTEGGIATURA SCALE',
                'BENEF BANCA DI CREDITO COOPERATIVO PER CAUSALE',
                'per Ordinaria',
                'PER Ordinaria',
                'PER gestione ordinaria',
                'ordinaria',
                'BENEF Banca di credito cooperativo PER',
            )
        },
        '1 H CLEAN DI ROZZA GIU': [Tags.LAVANDERIA],
        '000053361801': [Tags.RISPARMIO, Tags.LIBRETTO],
        'COFFEE CAPP': [Tags.MACCHINETTA_CAFFE],
        **{
            p: [Tags.TRASPORTI]
            for p in ['ATM MILAN', 'TRENORD', 'TRENITALIA', 'AZIENDATRAS']
        },
        **{p: [Tags.DELIVERY] for p in ['DELIVEROO']},
    }.items():
        if pattern in descrizione_operazioni:
            ret.tags.update(tags)

    # and
    for patterns, tags in [
        *[
            (ps, [Tags.PRANZO_VIMERCATE])
            for ps in [
                ["MCDONALD'S VIMERCATE", 'VIMERCATE'],
                ['PELLEGRINI SPA C/O ALC', 'VIMERCATE'],
                ["UAGLIO'-V.TORRIBIANCH", 'VIMERCATE'],
                ['CIOCCOLATI ITALIANI', 'VIMERCATE'],
                ['CLAVERA VIMERCATE', 'VIMERCATE'],
                ['PAN B SRL', 'VIMERCATE'],
                ['GRUPPO NEGOZI SRL', 'VIMERCATE'],
                ['HAMBU VIMERCATE', 'VIMERCATE'],
                ["PAGAMENTO POS MAMMA' ROSA", 'VIMERCATE'],
                ['PAGAMENTO POS OLD WILD WEST', 'VIMERCATE'],
            ]
        ],
        *[
            (ps, [Tags.BENZINA])
            for ps in [['PAGAMENTO POS 45592 CASTELNUOVO DEL']]
        ],
    ]:
        if all(pattern in descrizione_operazioni for pattern in patterns):
            ret.tags.update(tags)

    return ret
