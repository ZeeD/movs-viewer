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
        value = self.settings.value(SETTINGS_USERNAME)
        return cast(str, value) if value is not None else ''

    @username.setter
    def username(self, username: str) -> None:
        self.settings.setValue(SETTINGS_USERNAME, username)

    @property
    def password(self) -> str:
        value = self.settings.value(SETTINGS_PASSWORD)
        return cast(str, value) if value is not None else ''

    @password.setter
    def password(self, password: str) -> None:
        self.settings.setValue(SETTINGS_PASSWORD, password)

    @property
    def data_paths(self) -> list[str]:
        value = self.settings.value(SETTINGS_DATA_PATHS)

        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            return value

        raise ValueError(value)

    @data_paths.setter
    def data_paths(self, data_paths: list[str]) -> None:
        self.settings.setValue(SETTINGS_DATA_PATHS, data_paths)
