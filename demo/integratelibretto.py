from datetime import datetime
from decimal import Decimal
from json import load
from operator import attrgetter
from pathlib import Path

from movslib.model import Row
from movslib.movs import write_txt
from movslib.reader import read

ACC_PATH = '/home/zed/eclipse-workspace/movs-data/RPOL_accumulator_libretto.txt'
JSON_PATH = '/home/zed/Desktop/librettoattive.json'
# JSON_PATH = '/home/zed/Desktop/librettoscadute.json'


def main() -> None:
    kv, csv = read(ACC_PATH)
    with Path(JSON_PATH).open() as fp:
        j = load(fp)

    csv.reverse()

    assert isinstance(j, list)
    for el in j:
        assert isinstance(el, dict)
        row = Row(
            data_contabile=datetime.fromisoformat(el['data_contabile']).date(),
            data_valuta=datetime.fromisoformat(el['data_valuta']).date(),
            addebiti=None
            if el['addebiti'] is None
            else Decimal(el['addebiti']),
            accrediti=None
            if el['accrediti'] is None
            else Decimal(el['accrediti']),
            descrizione_operazioni=el['descrizione operazioni'],
        )
        csv.append(row)

    csv.sort(key=attrgetter('data_contabile'))
    csv.reverse()

    write_txt(f'{ACC_PATH}~', kv, csv)


if __name__ == '__main__':
    main()
