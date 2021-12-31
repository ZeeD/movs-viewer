from typing import cast

from PySide6.QtCore import QSettings

from .constants import SETTINGS_DATA_PATHS


class Settings:
    def __init__(self) -> None:
        self.settings = QSettings('ZeeD', 'mypyui')

    @property
    def data_paths(self) -> list[str]:
        return cast(list[str], self.settings.value(SETTINGS_DATA_PATHS))

    @data_paths.setter
    def data_paths(self, data_paths: list[str]) -> None:
        self.settings.setValue(SETTINGS_DATA_PATHS, data_paths)
