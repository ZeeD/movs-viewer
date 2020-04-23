import dataclasses
import pathlib
import sys

from PySide2.QtWidgets import QApplication

from movs import model
from mypyui import window, view
import movs


def main() -> None:
    'main'

    if not sys.argv[1:]:
        raise SystemExit(f'uso: {sys.argv[0]} ACCUMULATOR')

    _, csv = movs.read_txt(str(sys.argv[1]))

    data = csv[::-1]
    headers = tuple(f.name for f in dataclasses.fields(model.Row))

    app = QApplication(sys.argv)
    main_window = window.MainWindow(view.Widget(data, headers))
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
