from pathlib import Path
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
    from collections.abc import Callable

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
        file_names, _ = QFileDialog.getOpenFileNames(
            settingsui, dir=str(Path.home())
        )
        _set_data_paths(settingsui.dataPaths, file_names)

    settingsui = cast(Settingsui, QUiLoader().load(SETTINGSUI_UI_PATH))
    settingsui.usernameLineEdit.setText(settings.username)
    settingsui.passwordLineEdit.setText(settings.password)
    _set_data_paths(settingsui.dataPaths, settings.data_paths)

    settingsui.accepted.connect(save_settings)
    settingsui.openFileChooser.clicked.connect(open_data_paths)

    return settingsui


class NewMainui:
    models: list[SortFilterViewModel]
    charts: list[ChartView]
    multi_tabs: MultiTabs
    settings: Settings
    validator: Validator

    def __call__(self, settings: Settings, settingsui: Settingsui) -> QWidget:
        self.models = [
            SortFilterViewModel(data_path) for data_path in settings.data_paths
        ]
        self.charts = [
            ChartView(data_path) for data_path in settings.data_paths
        ]
        self.settings = settings
        self.mainui = cast(Mainui, QUiLoader().load(MAINUI_UI_PATH))

        self.validator = Validator(self.mainui, settings)

        self.multi_tabs = MultiTabs(self.mainui.centralwidget)
        self.mainui.gridLayout.addWidget(self.multi_tabs, 0, 0, 1, 1)

        self.mainui.actionUpdate.triggered.connect(self.update_helper)
        self.mainui.actionSettings.triggered.connect(settingsui.show)
        settingsui.accepted.connect(self.update_helper)

        # on startup load
        self.update_helper()

        return self.mainui

    def update_helper(self) -> None:
        data_paths_models = set(self.settings.data_paths)
        data_paths_charts = set(self.settings.data_paths)
        if not self.validator.validate():
            return
        for model in self.models[:]:
            if model.data_path in data_paths_models:
                data_paths_models.remove(model.data_path)
                model.reload()
            else:
                self.models.remove(model)
        self.models.extend(
            SortFilterViewModel(data_path) for data_path in data_paths_models
        )
        for chart in self.charts[:]:
            if chart.data_path in data_paths_charts:
                data_paths_charts.remove(chart.data_path)
                chart.reload()
            else:
                self.charts.remove(chart)
        self.charts.extend(
            ChartView(data_path) for data_path in data_paths_charts
        )
        self.multi_tabs.clear()
        for model, chart in zip(self.models, self.charts, strict=True):
            sheet = SearchSheet(self.multi_tabs)
            sheet.set_model(model)

            selection_model = sheet.selection_model()
            selection_model.selectionChanged.connect(
                self.update_status_bar(model, selection_model)
            )

            idx = self.multi_tabs.add_double_box(sheet, chart, model.name)

            def on_model_reset(
                mt: MultiTabs = self.multi_tabs,
                i: int = idx,
                m: SortFilterViewModel = model,
            ) -> None:
                return mt.setTabText(i, m.name)

            model.modelReset.connect(on_model_reset)

    def update_status_bar(
        self, model: SortFilterViewModel, selection_model: QItemSelectionModel
    ) -> 'Callable[[QItemSelection, QItemSelection], None]':
        return lambda _selected, _deselected: model.selection_changed(
            selection_model, self.mainui.statusBar()
        )


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
    new_mainui = NewMainui()
    mainui = new_mainui(settings, settingsui)

    mainui.show()

    raise SystemExit(app.exec())
