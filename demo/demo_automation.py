from logging import INFO
from logging import basicConfig
from logging import info
from sys import argv

from movsmerger.movsmerger import merge_files
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QInputDialog
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QWidget

from movsviewer.automation import get_movimenti
from movsviewer.settings import Settings


# TODO @me: capire dove metterla
# TOD000
class AskOtp:
    def __init__(self, parent: QWidget) -> None:
        self.parent = parent

    def __call__(self) -> str:
        self.parent.setFocus()
        response, ok = QInputDialog.getText(
            self.parent, 'OTP', 'homeBanking', QLineEdit.EchoMode.Normal
        )
        if not ok:
            raise ValueError
        return response


def main() -> None:
    basicConfig(level=INFO, format='%(message)s')
    app = QApplication(argv)
    q = QWidget()
    q.show()

    settings = Settings(argv[1:])
    numconto = '000091703983'  # TODO @me: move in settings
    # TOD000
    with get_movimenti(
        settings.username, settings.password, numconto, AskOtp(q)
    ) as movimenti:
        info(movimenti)
        merge_files(settings.data_paths[0], str(movimenti))
    raise SystemExit(app.exec())


if __name__ == '__main__':
    main()
