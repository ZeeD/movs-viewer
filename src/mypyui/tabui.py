from contextlib import contextmanager
from typing import List
from typing import Iterator

from movs.model import Row
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QGridLayout
from PySide2.QtWidgets import QMainWindow

from .chartview import ChartView
from .viewmodel import SortFilterViewModel

TABUI_UI_PATH = f'{__file__}/../../../resources/tabui.ui'


@contextmanager
def main_window(data: List[Row]) -> Iterator[QMainWindow]:
    app = QApplication([__file__])

    main_window = QUiLoader().load(TABUI_UI_PATH)

    view_model = SortFilterViewModel(main_window, data)
    main_window.tableView.setModel(view_model)
    main_window.lineEdit.textChanged.connect(view_model.filter_changed)

    # chart_view = ChartView(main_window, data)
    # grid = QGridLayout()
    # grid.addWidget(chart_view)
    # main_window.tab_2.setLayout(grid)

    try:
        yield main_window
    finally:
        app.exec_()
