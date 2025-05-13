from csv import DictReader
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING
from typing import TypedDict
from typing import overload

if TYPE_CHECKING:
    from collections.abc import Iterator


Base = TypedDict(
    'Base',
    {
        'data scadenza': date,
        'importo': Decimal,
        'tasso': Decimal,
        'data adesione': date,
        'durata': int,
        'interessi netti': Decimal,
    },
)


class Deposito(Base):
    interessi: Decimal


class Offerta(Base):
    interessi: Decimal


class Scadute(Base): ...


@overload
def read(path: Path, cls: type[Deposito]|type[Offerta]) -> 'Iterator[Deposito]|Iterator[Offerta]': ...
@overload
def read(path: Path, cls: type[Scadute]) -> 'Iterator[Scadute]': ...


def read(
    path: Path, cls: type[Deposito] | type[Offerta] | type[Scadute]
) -> 'Iterator[Deposito] | Iterator[Offerta] | Iterator[Scadute]':
    with path.open(newline='') as csv:
        reader = DictReader(csv)
        for row in reader:
            # base
            obj = cls([
                ('importo',Decimal(row['importo'])),
                ('tasso',Decimal(row['tasso'])),
                ('durata',int(row['durata'])),
                ('data scadenza',date.fromisoformat(row['data scadenza'])),
                ('data adesione', date.fromisoformat(row['data adesione'])),
                ('interessi netti', Decimal(row['interessi netti'])),
            ])
            # Deposito/Offerta
            if 'interessi' in row:
                obj['interessi'] = Decimal(row['interessi'])
            yield obj


ROOT = Path(__file__).parent / 'supersmart'


def main() -> None:
    deposito = read(ROOT / 'deposito.csv', Deposito)
    offerta = read(ROOT / 'offerta.csv', Offerta)
    scadute = read(ROOT / 'scadute.csv', Scadute)


if __name__ == '__main__':
    main()
