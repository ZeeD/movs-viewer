from datetime import date
from datetime import timedelta
from decimal import Decimal
from pprint import pprint

from movs.model import Row

from mypyui.tabui import main_window


def row(day: int, euro: int) -> Row:
    data = date(2012, 1, 1) + timedelta(days=day)
    return Row(data, data,
               None if euro >= 0 else Decimal(-euro),
               Decimal(euro) if euro >= 0 else None,
               '')


DATA = [row(1, 123),
        row(2, 456),
        row(3, -789),
        row(4, 101),
        row(5, -112),
        row(6, 13)]

# DATA = [row(day, euro) for day, euro in enumerate(range(11))]


def main() -> None:
    pprint(DATA)
    with main_window(DATA) as window:
        window.show()


if __name__ == '__main__':
    main()
