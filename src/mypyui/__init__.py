from sys import argv

from movs import read_txt

from .tabui import main_window


def main() -> None:
    try:
        _, accumulator = argv
    except ValueError:
        raise SystemExit(f'uso: {argv[0]} ACCUMULATOR')

    _, data = read_txt(accumulator)

    with main_window(list(data)) as window:
        window.show()
