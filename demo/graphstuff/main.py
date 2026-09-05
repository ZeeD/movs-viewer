from pathlib import Path
from sys import argv

from PySide6.QtGui import QGuiApplication
from PySide6.QtGui import QWindow
from PySide6.QtQuick import QQuickView


def graphstuff() -> QWindow:
    viewer = QQuickView()
    viewer.engine().addImportPath(Path(__file__).parent)
    viewer.setColor('black')
    viewer.loadFromModule('qml', 'main')
    return viewer


def main() -> None:
    app = QGuiApplication(argv)

    viewer = graphstuff()

    viewer.show()
    raise SystemExit(app.exec())


if __name__ == '__main__':
    main()
