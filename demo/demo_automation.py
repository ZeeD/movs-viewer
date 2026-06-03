from logging import INFO
from logging import basicConfig
from logging import getLogger
from sys import argv

from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QWidget

from movsmerger.movsmerger import merge_files
from movsviewer.automation import get_movimenti
from movsviewer.settings import Settings

logger = getLogger(__name__)


def main() -> None:
    basicConfig(level=INFO, format='%(message)s')
    app = QApplication(argv)
    q = QWidget()
    q.show()

    settings = Settings(argv[1:])
    numconto = '000091703983'
    with get_movimenti(numconto) as movimenti:
        logger.info(movimenti)
        merge_files(settings.data_paths[0], str(movimenti))

    raise SystemExit(app.exec())


if __name__ == '__main__':
    main()
