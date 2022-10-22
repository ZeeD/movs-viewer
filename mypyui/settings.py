from typing import cast

from PySide6.QtCore import QSettings

from .constants import SETTINGS_DATA_PATHS
from .constants import SETTINGS_PASSWORD
from .constants import SETTINGS_USERNAME


class Settings:
    def __init__(self) -> None:
        self.settings = QSettings('ZeeD', 'mypyui')

    @property
    def username(self) -> str:
        return cast(str, self.settings.value(SETTINGS_USERNAME))

    @username.setter
    def username(self, username: str) -> None:
        self.settings.setValue(SETTINGS_USERNAME, username)

    @property
    def password(self) -> str:
        return cast(str, self.settings.value(SETTINGS_PASSWORD))

    @password.setter
    def password(self, password: str) -> None:
        self.settings.setValue(SETTINGS_PASSWORD, password)

    @property
    def data_paths(self) -> list[str]:
        return cast(list[str], self.settings.value(SETTINGS_DATA_PATHS))

    @data_paths.setter
    def data_paths(self, data_paths: list[str]) -> None:
        self.settings.setValue(SETTINGS_DATA_PATHS, data_paths)
