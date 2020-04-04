import dataclasses
import sys

from PySide2.QtWidgets import QApplication

from movs import model
from mypyui import window, view
import movs
import pathlib


def main() -> None:
    fn = pathlib.Path(movs.__file__).parent.parent.parent / 'resources' / 'BPOL_Lista_Movimenti.txt'
    _, csv = movs.read_txt(fn)

    data = csv
    headers = tuple(f.name for f in dataclasses.fields(model.Row))

    app = QApplication(sys.argv)
    main_window = window.MainWindow(view.Widget(data, headers))
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
