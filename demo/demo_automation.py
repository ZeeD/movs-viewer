from logging import INFO
from logging import basicConfig
from logging import info
from sys import argv

from movsmerger.movsmerger import merge_files
from qtpy.QtWidgets import QApplication
from qtpy.QtWidgets import QInputDialog
from qtpy.QtWidgets import QLineEdit
from qtpy.QtWidgets import QWidget

from movsviewer.automation import get_movimenti
from movsviewer.settings import Settings


# TODO: capire dove metterla
class AskOtp:
    def __init__(self, parent: QWidget) -> None:
        self.parent = parent

    def __call__(self) -> str:
        self.parent.setFocus()
        response, ok = QInputDialog.getText(
            self.parent, 'OTP', 'homeBanking', QLineEdit.EchoMode.Normal
        )
        assert ok
        return response


def main() -> None:
    basicConfig(level=INFO, format='%(message)s')
    app = QApplication(argv)
    q = QWidget()
    q.show()

    settings = Settings(argv[1:])
    numconto = '000091703983'  # TODO: move in settings
    with get_movimenti(
        settings.username, settings.password, numconto, AskOtp(q)
    ) as movimenti:
        info(movimenti)
        merge_files(settings.data_paths[0], str(movimenti))
    raise SystemExit(app.exec())


if __name__ == '__main__':
    main()
