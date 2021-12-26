from typing import cast

from PySide6.QtCore import QSettings

from .constants import SETTINGS_DATA_PATH


class Settings:
    def __init__(self) -> None:
        self.settings = QSettings('ZeeD', 'mypyui')

    @property
    def data_path(self) -> str:
        return cast(str, self.settings.value(SETTINGS_DATA_PATH))

    @data_path.setter
    def data_path(self, data_path: str) -> None:
        self.settings.setValue(SETTINGS_DATA_PATH, data_path)
