from csv import DictReader
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING
from typing import NamedTuple
from typing import TypedDict
from typing import cast
from typing import overload

from guilib.chartwidget.viewmodel import SortFilterViewModel
from guilib.qwtplot.plot import Plot
from PySide6.QtWidgets import QApplication

from qwt.plot_curve import QwtPlotCurve

if TYPE_CHECKING:
    from collections.abc import Iterator
    from collections.abc import Sequence

    from guilib.chartwidget.model import InfoProto


Scadute = TypedDict(
    'Scadute',
    {
        'data scadenza': date,
        'importo': Decimal,
        'tasso': Decimal,
        'data adesione': date,
        'durata': int,
        'interessi netti': Decimal,
    },
)


class Deposito(Scadute):
    interessi: Decimal


@overload
def read(path: Path, _cls: type[Deposito], /) -> 'Iterator[Deposito]': ...
@overload
def read(path: Path, _cls: type[Scadute], /) -> 'Iterator[Scadute]': ...


def read(
    path: Path, _cls: type[Deposito] | type[Scadute], /
) -> 'Iterator[Deposito] | Iterator[Scadute]':
    with path.open(newline='') as csv:
        reader = DictReader(csv)
        for row in reader:
            # Scadute
            obj: Scadute = {
                'importo': Decimal(row['importo']),
                'tasso': Decimal(row['tasso']),
                'durata': int(row['durata']),
                'data scadenza': date.fromisoformat(row['data scadenza']),
                'data adesione': date.fromisoformat(row['data adesione']),
                'interessi netti': Decimal(row['interessi netti']),
            }
            # Deposito/Offerta
            if 'interessi' in row:
                cast('Deposito', obj)['interessi'] = Decimal(row['interessi'])
            yield obj


class ColumnHeader(NamedTuple):
    name: str


class Column(NamedTuple):
    header: ColumnHeader
    howmuch: 'Decimal | None'


class Info(NamedTuple):
    when: 'date'
    columns: 'Sequence[Column]'

    def howmuch(self, column_header: ColumnHeader) -> 'Decimal | None':
        for column in self.columns:
            if column.header is column_header:
                return column.howmuch
        return None


ZERO = Decimal(0)


class ToInfos:
    def __init__(self) -> None:
        self.idx = 0

    def __call__(self, row: Scadute) -> list[Info]:
        ch = ColumnHeader(f'{row["importo"]} - {row["tasso"]}')
        self.idx += 1

        return [
            Info(row['data adesione'], [Column(ch, row['importo'])]),
            Info(
                row['data scadenza'],
                [Column(ch, row['importo'] + row['interessi netti'])],
            ),
        ]


to_infos = ToInfos()


def draw(*scadutes: 'Iterator[Scadute]') -> None:
    app = QApplication()

    model = SortFilterViewModel()
    plot = Plot(model, None, curve_style=QwtPlotCurve.Lines)

    infos = []
    for scadute in scadutes:
        for row in scadute:
            infos.extend(to_infos(row))

    model.update(cast('Sequence[InfoProto]', infos))

    plot.show()
    app.exec()


def main() -> None:
    root = Path(__file__).parent / 'supersmart'

    deposito = read(root / 'deposito.csv', Deposito)
    offerta = read(root / 'offerta.csv', Deposito)
    scadute = read(root / 'scadute.csv', Scadute)

    draw(deposito, offerta, scadute)


if __name__ == '__main__':
    main()
