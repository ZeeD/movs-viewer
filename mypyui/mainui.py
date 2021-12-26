from PySide6.QtCore import QItemSelection
from PySide6.QtGui import QKeySequence
from PySide6.QtGui import QShortcut
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QWidget

from .chartview import ChartView
from .constants import MAINUI_UI_PATH
from .constants import SETTINGSUI_UI_PATH
from .settings import Settings
from .viewmodel import SortFilterViewModel


def new_settingsui(settings: Settings) -> QWidget:
    def save_settings() -> None:
        settings.data_path = settingsui.dataPathLineEdit.text()

    def open_folder() -> None:
        settingsui.dataPathLineEdit.setText(QFileDialog.getExistingDirectory())

    settingsui = QUiLoader().load(SETTINGSUI_UI_PATH)
    settingsui.dataPathLineEdit.setText(settings.data_path)

    settingsui.buttonBox.accepted.connect(save_settings)
    settingsui.toolButton.clicked.connect(open_folder)

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

    mainui = QUiLoader().load(MAINUI_UI_PATH)

    mainui.tableView.setModel(model)
    selection_model = mainui.tableView.selectionModel()
    selection_model.selectionChanged.connect(update_status_bar)

    mainui.lineEdit.textChanged.connect(model.filterChanged)

    chart_view = ChartView(settings)
    mainui.tab_2.layout().addWidget(chart_view)

    mainui.actionUpdate.triggered.connect(update_helper)
    mainui.actionSettings.triggered.connect(settingsui.show)
    settingsui.accepted.connect(update_helper)

    QShortcut(QKeySequence(mainui.tr('Ctrl+F')),
              mainui).activated.connect(mainui.lineEdit.setFocus)
    QShortcut(QKeySequence(mainui.tr('Esc')),
              mainui).activated.connect(lambda: mainui.lineEdit.setText())

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
