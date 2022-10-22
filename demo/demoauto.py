from PySide6.QtWidgets import QApplication, QLineEdit
from PySide6.QtWidgets import QInputDialog
from PySide6.QtWidgets import QWidget

from movsmerger import merge_files
from mypyui.automation import get_movimenti
from mypyui.settings import Settings


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
    app = QApplication([__file__])
    q = QWidget()
    q.show()

    settings = Settings()
    numconto = '000091703983'  # TODO move in settings
    with get_movimenti(settings.username,
                       settings.password,
                       numconto,
                       ask_otp(q)) as movimenti:
        print(movimenti)
        merge_files(settings.data_paths[0], movimenti)
    raise SystemExit(app.exec())


main()
