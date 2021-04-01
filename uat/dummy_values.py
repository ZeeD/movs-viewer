from datetime import date, timedelta
from movs.model import Row
from decimal import Decimal
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

DATA = [row(day, euro)
        for day, euro in enumerate(range(11), start=1)]


def main() -> None:
    with main_window(DATA) as window:
        window.show()


if __name__ == '__main__':
    main()
