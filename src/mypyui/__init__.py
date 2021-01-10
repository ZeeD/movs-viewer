import sys

from PySide2 import QtWidgets

import movs
from mypyui import tabui


def main() -> None:
    try:
        _, accumulator = sys.argv
    except:
        raise SystemExit(f'uso: {sys.argv[0]} ACCUMULATOR')

    _, data = movs.read_txt(accumulator)

    with tabui.main_window(data) as main_window:
        main_window.show()
