from movsmerger import merge_files
from qtpy.QtWidgets import QApplication
from qtpy.QtWidgets import QInputDialog
from qtpy.QtWidgets import QLineEdit
from qtpy.QtWidgets import QWidget

from mypyui.automation import get_movimenti
from mypyui.settings import Settings
from sys import argv


# TODO: capire dove metterla
class ask_otp:
    def __init__(self, parent: QWidget) -> None:
        self.parent = parent

    def __call__(self) -> str:
        self.parent.setFocus()
        response, ok = QInputDialog.getText(self.parent,
                                            'OTP', 'homeBanking',
                                            QLineEdit.EchoMode.Normal)
        assert ok
        return response


def main() -> None:
    app = QApplication(argv)
    q = QWidget()
    q.show()

    settings = Settings(argv[1:])
    numconto = '000091703983'  # TODO move in settings
    with get_movimenti(settings.username,
                       settings.password,
                       numconto,
                       ask_otp(q)) as movimenti:
        print(movimenti)
        merge_files(settings.data_paths[0], movimenti)
    raise SystemExit(app.exec())


if __name__ == '__main__':
    main()
