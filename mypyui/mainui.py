from typing import cast

from PySide6.QtCore import QItemSelection
from PySide6.QtGui import QAction
from PySide6.QtGui import QKeySequence
from PySide6.QtGui import QShortcut
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtWidgets import QTableView
from PySide6.QtWidgets import QToolButton
from PySide6.QtWidgets import QWidget

from .chartview import ChartView
from .constants import MAINUI_UI_PATH
from .constants import SETTINGSUI_UI_PATH
from .settings import Settings
from .viewmodel import SortFilterViewModel

_dataPathsSeparator = '; \n'


class Mainui(QMainWindow):
    lineEdit: QLineEdit
    tableView: QTableView
    tab_2: QWidget
    actionSettings: QAction
    actionUpdate: QAction


class Settingsui(QWidget):
    usernameLineEdit: QLineEdit
    passwordLineEdit: QLineEdit
    dataPaths: QPlainTextEdit
    buttonBox: QDialogButtonBox
    openFileChooser: QToolButton


def _setDataPaths(dataPaths: QPlainTextEdit, fileNames: list[str]) -> None:
    dataPaths.setPlainText(_dataPathsSeparator.join(fileNames))


def _getDataPaths(dataPaths: QPlainTextEdit) -> list[str]:
    return dataPaths.toPlainText().split(_dataPathsSeparator)


def new_settingsui(settings: Settings) -> QWidget:
    def save_settings() -> None:
        settings.data_paths = _getDataPaths(settingsui.dataPaths)
        settings.username = settingsui.usernameLineEdit.text()
        settings.password = settingsui.passwordLineEdit.text()

    def open_data_paths() -> None:
        fileNames, _ = QFileDialog.getOpenFileNames(settingsui)
        _setDataPaths(settingsui.dataPaths, fileNames)

    settingsui = cast(Settingsui, QUiLoader().load(SETTINGSUI_UI_PATH))
    settingsui.usernameLineEdit.setText(settings.username)
    settingsui.passwordLineEdit.setText(settings.password)
    _setDataPaths(settingsui.dataPaths, settings.data_paths)

    settingsui.buttonBox.accepted.connect(save_settings)  # type: ignore
    settingsui.openFileChooser.clicked.connect(open_data_paths)  # type: ignore

    return settingsui


def new_mainui(settings: Settings,
               model: SortFilterViewModel,
               settingsui: QWidget) -> QWidget:
    def update_helper() -> None:
        model.reload()
        chart_view.reload()

    def update_status_bar(_selected: QItemSelection,
                          _deselected: QItemSelection) -> None:
        model.selectionChanged(selection_model, mainui.statusBar())

    mainui = cast(Mainui, QUiLoader().load(MAINUI_UI_PATH))

    mainui.tableView.setModel(model)
    selection_model = mainui.tableView.selectionModel()
    selection_model.selectionChanged.connect(update_status_bar)  # type: ignore

    mainui.lineEdit.textChanged.connect(model.filterChanged)  # type: ignore

    chart_view = ChartView(settings)
    mainui.tab_2.layout().addWidget(chart_view)

    mainui.actionUpdate.triggered.connect(update_helper)  # type: ignore
    mainui.actionSettings.triggered.connect(settingsui.show)  # type: ignore
    settingsui.accepted.connect(update_helper)  # type: ignore

    QShortcut(QKeySequence('Ctrl+F'),  # type: ignore
              mainui).activated.connect(mainui.lineEdit.setFocus)
    QShortcut(QKeySequence('Esc'), mainui).activated.connect(  # type: ignore
        lambda: mainui.lineEdit.setText(''))

    # on startup load
    update_helper()

    return mainui


def main() -> None:
    app = QApplication([__file__])
    settings = Settings()
    model = SortFilterViewModel(settings)
    settingsui = new_settingsui(settings)
    mainui = new_mainui(settings, model, settingsui)

    mainui.show()

    raise SystemExit(app.exec())
