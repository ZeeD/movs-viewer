import datetime
import decimal
import sys

from PySide2.QtWidgets import QApplication

import view
import window


def main():
    data = (
        (datetime.date(2000, 1, 1), decimal.Decimal(5000)),
        (datetime.date(2000, 3, 1), decimal.Decimal(-2000)),
        (datetime.date(2001, 1, 1), decimal.Decimal(1000)),
        (datetime.date(2001, 2, 1), decimal.Decimal(-3000)),
        (datetime.date(2001, 3, 1), decimal.Decimal(10000)),
    )
    headers = ('...', 'movimenti', )

    app = QApplication(sys.argv)
    main_window = window.MainWindow(view.Widget(data, headers))
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
