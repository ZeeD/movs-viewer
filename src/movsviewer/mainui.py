from sys import argv
from typing import TYPE_CHECKING
from typing import cast

from guilib.multitabs.widget import MultiTabs
from guilib.searchsheet.widget import SearchSheet
from PySide6.QtCore import QCoreApplication
from PySide6.QtCore import QItemSelection
from PySide6.QtCore import QItemSelectionModel
from PySide6.QtCore import Qt
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQuick import QSGRendererInterface
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtWidgets import QToolButton
from PySide6.QtWidgets import QWidget

from movsviewer.chartview import ChartView
from movsviewer.constants import MAINUI_UI_PATH
from movsviewer.constants import SETTINGSUI_UI_PATH
from movsviewer.settings import Settings
from movsviewer.validator import Validator
from movsviewer.viewmodel import SortFilterViewModel

if TYPE_CHECKING:
    from PySide6.QtGui import QAction


_DATA_PATHS_SEPARATOR = '; \n'


class Mainui(QMainWindow):
    actionSettings: 'QAction'  # noqa: N815
    actionUpdate: 'QAction'  # noqa: N815
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

    settingsui.accepted.connect(save_settings)
    settingsui.openFileChooser.clicked.connect(open_data_paths)

    return settingsui


def new_mainui(settings: Settings, settingsui: Settingsui) -> QWidget:
    models = [
        SortFilterViewModel(data_path) for data_path in settings.data_paths
    ]
    charts = [ChartView(data_path) for data_path in settings.data_paths]

    def build_helper() -> None:
        multi_tabs.clear()
        for model, chart in zip(models, charts, strict=True):
            sheet = SearchSheet(multi_tabs)
            sheet.set_model(model)

            selection_model = sheet.selection_model()
            selection_model.selectionChanged.connect(
                UpdateStatusBar(model, selection_model)
            )

            idx = multi_tabs.add_double_box(sheet, chart, model.name)
            model.modelReset.connect(
                lambda mt=multi_tabs, i=idx, m=model: mt.setTabText(i, m.name)
            )

    def update_helper() -> None:
        data_paths_models = set(settings.data_paths)
        data_paths_charts = set(settings.data_paths)
        if not validator.validate():
            return
        for model in models[:]:
            if model.data_path in data_paths_models:
                data_paths_models.remove(model.data_path)
                model.reload()
            else:
                models.remove(model)
        models.extend(
            SortFilterViewModel(data_path) for data_path in data_paths_models
        )
        for chart in charts[:]:
            if chart.data_path in data_paths_charts:
                data_paths_charts.remove(chart.data_path)
                chart.reload()
            else:
                charts.remove(chart)
        charts.extend(ChartView(data_path) for data_path in data_paths_charts)
        build_helper()

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

    build_helper()

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
