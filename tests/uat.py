from datetime import date
from datetime import timedelta
from decimal import Decimal
from pprint import pprint
from typing import List

from movs.model import Row
from mypyui.tabui import main_window


def row(day: int, euro: int) -> Row:
    data = date(2012, 1, 1) + timedelta(days=day)
    return Row(data, data,
               None if euro >= 0 else Decimal(-euro),
               Decimal(euro) if euro >= 0 else None,
               '')


DATAS: List[List[Row]] = [
    [row(1, 123),
        row(2, 456),
        row(3, -789),
        row(4, 101),
        row(5, -112),
        row(6, 13)],
    [],
    [row(1, 1),
     row(2, 2),
     row(3, 3),
     row(4, 4),
     row(5, 5),
     row(6, 6)]
]


# DATA = [row(day, euro) for day, euro in enumerate(range(11))]


def main() -> None:
    i = 0

    def loader(path: str) -> List[Row]:
        nonlocal i

        print(path)
        data = DATAS[i]
        pprint(data)
        i = (i + 1) % len(DATAS)
        return data

    with main_window(loader, '') as window:
        window.show()


if __name__ == '__main__':
    main()
