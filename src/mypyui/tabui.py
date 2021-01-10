import contextlib
import typing

from PySide2 import QtUiTools, QtWidgets

from movs import model

from . import chartview
from . import viewmodel


TABUI_UI_PATH = f'{__file__}/../../../resources/tabui.ui'


@contextlib.contextmanager
def main_window(data: typing.Iterable[model.Row]
                ) -> typing.Iterator[QtWidgets.QMainWindow]:
    app = QtWidgets.QApplication([__file__])
    try:
        main_window = QtUiTools.QUiLoader().load(TABUI_UI_PATH)

        view_model = viewmodel.SortFilterViewModel(main_window, data)
        main_window.tableView.setModel(view_model)
        main_window.lineEdit.textChanged.connect(view_model.filter_changed)

        chart_view = chartview.ChartView(main_window, data)
        grid = QtWidgets.QGridLayout()
        grid.addWidget(chart_view)
        main_window.tab2.setLayout(grid)

        yield main_window
    finally:
        app.exec_()
