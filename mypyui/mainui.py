from sys import argv
from typing import cast

from qtpy.QtCore import QCoreApplication
from qtpy.QtCore import QItemSelection
from qtpy.QtCore import Qt
from qtpy.QtGui import QAction
from qtpy.QtGui import QKeySequence
from qtpy.QtGui import QShortcut
from qtpy.QtQuick import QQuickWindow
from qtpy.QtQuick import QSGRendererInterface
from qtpy.QtUiTools import QUiLoader
from qtpy.QtWidgets import QApplication
from qtpy.QtWidgets import QDialog
from qtpy.QtWidgets import QDialogButtonBox
from qtpy.QtWidgets import QFileDialog
from qtpy.QtWidgets import QLineEdit
from qtpy.QtWidgets import QMainWindow
from qtpy.QtWidgets import QPlainTextEdit
from qtpy.QtWidgets import QTableView
from qtpy.QtWidgets import QToolButton
from qtpy.QtWidgets import QWidget

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


class Settingsui(QDialog):
    usernameLineEdit: QLineEdit
    passwordLineEdit: QLineEdit
    dataPaths: QPlainTextEdit
    buttonBox: QDialogButtonBox
    openFileChooser: QToolButton


def _setDataPaths(dataPaths: QPlainTextEdit, fileNames: list[str]) -> None:
    dataPaths.setPlainText(_dataPathsSeparator.join(fileNames))


def _getDataPaths(dataPaths: QPlainTextEdit) -> list[str]:
    return dataPaths.toPlainText().split(_dataPathsSeparator)


def new_settingsui(settings: Settings) -> Settingsui:
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

    settingsui.buttonBox.accepted.connect(save_settings)
    settingsui.openFileChooser.clicked.connect(open_data_paths)

    return settingsui


def new_mainui(settings: Settings,
               model: SortFilterViewModel,
               settingsui: Settingsui) -> QWidget:
    def update_helper() -> None:
        model.reload()
        chart_view.reload()

    def update_status_bar(_selected: QItemSelection,
                          _deselected: QItemSelection) -> None:
        model.selectionChanged(selection_model, mainui.statusBar())

    mainui = cast(Mainui, QUiLoader().load(MAINUI_UI_PATH))

    mainui.tableView.setModel(model)
    model.modelReset.connect(mainui.tableView.resizeColumnsToContents)
    selection_model = mainui.tableView.selectionModel()
    selection_model.selectionChanged.connect(update_status_bar)

    mainui.lineEdit.textChanged.connect(model.filterChanged)

    chart_view = ChartView(settings)
    mainui.tab_2.layout().addWidget(chart_view)

    mainui.actionUpdate.triggered.connect(update_helper)
    mainui.actionSettings.triggered.connect(settingsui.show)
    settingsui.accepted.connect(update_helper)

    QShortcut(QKeySequence('Ctrl+F'),
              mainui).activated.connect(mainui.lineEdit.setFocus)
    QShortcut(QKeySequence('Esc'), mainui).activated.connect(
        lambda: mainui.lineEdit.setText(''))

    # on startup load
    update_helper()

    return mainui


def main() -> None:
    QCoreApplication.setAttribute(  # @UndefinedVariable
        Qt.ApplicationAttribute.AA_ShareOpenGLContexts)  # @UndefinedVariable
    QQuickWindow.setGraphicsApi(QSGRendererInterface.GraphicsApi.OpenGLRhi)

    app = QApplication(argv)
    settings = Settings(argv[1:])
    model = SortFilterViewModel(settings)
    settingsui = new_settingsui(settings)
    mainui = new_mainui(settings, model, settingsui)

    mainui.show()

    raise SystemExit(app.exec())
