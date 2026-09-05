from movslib.model import Row
from movslib.movs import read_txt
from movslib.movs import write_txt

SRC = '/home/zed/eclipse-workspace/movs-data/RPOL_accumulator_libretto.txt'
DST = f'{SRC}~'

kv, csv = read_txt(SRC)
write_txt(
    DST,
    kv,
    sorted(
        [
            Row(
                data_contabile=row.data_valuta,
                data_valuta=row.data_contabile,
                addebiti=row.addebiti,
                accrediti=row.accrediti,
                descrizione_operazioni=row.descrizione_operazioni,
            )
            for row in csv
        ],
        key=lambda row: (row.data_contabile, row.data_valuta),
        reverse=True,
    ),
)
