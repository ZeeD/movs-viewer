from dataclasses import dataclass
from itertools import accumulate
# from itertools import tee
from typing import Iterable
from datetime import date


@dataclass(frozen=True)
class DC:
    a: date
    b: int


t = tuple[date, int]

def acc(dcs: Iterable[DC]) -> Iterable[t]:
    def func(l: t, r: DC) -> t:
        return (r.a, l[1]+r.b)
    it = iter(dcs)
    head = next(it)
    return accumulate(it, func, initial=(head.a, head.b))


for e in acc([DC(date(2020, 1, 1), 1),
              DC(date(2020, 1, 2), 3),
              DC(date(2021, 1, 3), 2)]):
    print(e)
