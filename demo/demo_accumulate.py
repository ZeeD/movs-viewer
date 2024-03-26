from dataclasses import dataclass
from datetime import date
from itertools import accumulate
from logging import INFO
from logging import basicConfig
from logging import info
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


@dataclass(frozen=True)
class DC:
    a: date
    b: int


def acc(dcs: 'Iterable[DC]') -> 'Iterable[tuple[date, int]]':
    it = iter(dcs)
    h = next(it)
    return accumulate(it, lambda t, dc: (dc.a, t[1] + dc.b), initial=(h.a, h.b))


def main() -> None:
    basicConfig(level=INFO, format='%(message)s')

    for e in acc(
        [
            DC(date(2020, 1, 1), 1),
            DC(date(2020, 1, 2), 3),
            DC(date(2021, 1, 3), 2),
        ]
    ):
        info(e)


if __name__ == '__main__':
    main()
