from collections import defaultdict
from datetime import date
from itertools import accumulate
from operator import attrgetter
from typing import TYPE_CHECKING

from guilib.chartwidget.model import Column
from guilib.chartwidget.model import ColumnHeader
from guilib.chartwidget.model import ColumnProto
from guilib.chartwidget.model import Info
from guilib.chartwidget.model import InfoProto
from movslib.movs import read_txt

if TYPE_CHECKING:
    from collections.abc import Iterable
    from decimal import Decimal

    from movslib.model import Row
    from movslib.model import Rows


def _acc(rows: 'Rows') -> 'Iterable[tuple[date, Decimal]]':
    def func(a: 'tuple[date, Decimal]', b: 'Row') -> 'tuple[date, Decimal]':
        return (b.date, a[1] + b.money)

    it = iter(sorted(rows, key=attrgetter('date')))
    head = next(it)
    return accumulate(it, func, initial=(head.date, head.money))


def load_infos(*fn_names: tuple[str, str]) -> list[InfoProto]:
    tmp = defaultdict[date, list[ColumnProto]](list)
    for fn, name in fn_names:
        _, rows = read_txt(fn, name)
        ch = ColumnHeader(rows.name)
        for d, m in _acc(rows):
            tmp[d].append(Column(ch, m))
    return [Info(d, tmp[d]) for d in sorted(tmp)]
