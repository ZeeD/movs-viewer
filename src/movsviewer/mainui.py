from os import environ
from sys import argv
from typing import cast

from guilib.multitabs.widget import MultiTabs
from guilib.searchsheet.widget import SearchSheet

from movsviewer.chartview import ChartView
from movsviewer.constants import MAINUI_UI_PATH
from movsviewer.constants import SETTINGSUI_UI_PATH
from movsviewer.settings import Settings
from movsviewer.validator import Validator
from movsviewer.viewmodel import SortFilterViewModel

if 'QT_API' not in environ:
    environ['QT_API'] = 'pyside6'

from qtpy.QtCore import QCoreApplication
from qtpy.QtCore import QItemSelection
from qtpy.QtCore import QItemSelectionModel
from qtpy.QtCore import Qt
from qtpy.QtGui import QAction
from qtpy.QtQuick import QQuickWindow
from qtpy.QtQuick import QSGRendererInterface
from qtpy.QtUiTools import QUiLoader
from qtpy.QtWidgets import QApplication
from qtpy.QtWidgets import QDialog
from qtpy.QtWidgets import QDialogButtonBox
from qtpy.QtWidgets import QFileDialog
from qtpy.QtWidgets import QGridLayout
from qtpy.QtWidgets import QLineEdit
from qtpy.QtWidgets import QMainWindow
from qtpy.QtWidgets import QPlainTextEdit
from qtpy.QtWidgets import QToolButton
from qtpy.QtWidgets import QWidget

_DATA_PATHS_SEPARATOR = '; \n'


class Mainui(QMainWindow):
    # lineEdit: QLineEdit
    # tableView: QTableView
    # tab_2: QWidget
    actionSettings: QAction  # noqa: N815
    actionUpdate: QAction  # noqa: N815
    gridLayout: QGridLayout  # noqa: N815
    centralwidget: QWidget


class Settingsui(QDialog):
    usernameLineEdit: QLineEdit  # noqa: N815
    passwordLineEdit: QLineEdit  # noqa: N815
    dataPaths: QPlainTextEdit  # noqa: N815
    buttonBox: QDialogButtonBox  # noqa: N815
    openFileChooser: QToolButton  # noqa: N815


def _set_data_paths(data_paths: QPlainTextEdit, file_names: list[str]) -> None:
    data_paths.setPlainText(_DATA_PATHS_SEPARATOR.join(file_names))


def _get_data_paths(data_paths: QPlainTextEdit) -> list[str]:
    return data_paths.toPlainText().split(_DATA_PATHS_SEPARATOR)


def new_settingsui(settings: Settings) -> Settingsui:
    def save_settings() -> None:
        settings.data_paths = _get_data_paths(settingsui.dataPaths)
        settings.username = settingsui.usernameLineEdit.text()
        settings.password = settingsui.passwordLineEdit.text()

    def open_data_paths() -> None:
        file_names, _ = QFileDialog.getOpenFileNames(settingsui)
        _set_data_paths(settingsui.dataPaths, file_names)

    settingsui = cast(Settingsui, QUiLoader().load(SETTINGSUI_UI_PATH))
    settingsui.usernameLineEdit.setText(settings.username)
    settingsui.passwordLineEdit.setText(settings.password)
    _set_data_paths(settingsui.dataPaths, settings.data_paths)

    settingsui.buttonBox.accepted.connect(save_settings)
    settingsui.openFileChooser.clicked.connect(open_data_paths)

    return settingsui


def new_mainui(settings: Settings, settingsui: Settingsui) -> QWidget:
    models = [
        SortFilterViewModel(data_path) for data_path in settings.data_paths
    ]
    charts = [ChartView(data_path) for data_path in settings.data_paths]

    def update_helper() -> None:
        if validator.validate():
            for model in models:
                model.reload()
            for chart in charts:
                chart.reload()

    class UpdateStatusBar:
        def __init__(
            self,
            model: SortFilterViewModel,
            selection_model: QItemSelectionModel,
        ) -> None:
            self.model = model
            self.selection_model = selection_model

        def __call__(
            self, _selected: QItemSelection, _deselected: QItemSelection
        ) -> None:
            self.model.selection_changed(
                self.selection_model, mainui.statusBar()
            )

    mainui = cast(Mainui, QUiLoader().load(MAINUI_UI_PATH))

    validator = Validator(mainui, settings)

    multi_tabs = MultiTabs(mainui.centralwidget)
    mainui.gridLayout.addWidget(multi_tabs, 0, 0, 1, 1)

    for model, chart in zip(models, charts, strict=True):
        sheet = SearchSheet(multi_tabs)
        sheet.set_model(model)

        selection_model = sheet.selection_model()
        selection_model.selectionChanged.connect(
            UpdateStatusBar(model, selection_model)
        )

        multi_tabs.add_double_box(sheet, chart, 'todo')

    mainui.actionUpdate.triggered.connect(update_helper)
    mainui.actionSettings.triggered.connect(settingsui.show)
    settingsui.accepted.connect(update_helper)

    # on startup load
    update_helper()

    return mainui


def main() -> None:
    QCoreApplication.setAttribute(
        Qt.ApplicationAttribute.AA_ShareOpenGLContexts
    )
    QQuickWindow.setGraphicsApi(
        QSGRendererInterface.GraphicsApi.OpenGLRhi  # @UndefinedVariable
    )

    app = QApplication(argv)
    settings = Settings(argv[1:])
    settingsui = new_settingsui(settings)
    mainui = new_mainui(settings, settingsui)

    mainui.show()

    raise SystemExit(app.exec())
