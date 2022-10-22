from typing import Final

from pkg_resources import resource_filename


def _resource(filename: str) -> str:
    return resource_filename('mypyui', f'resources/{filename}')


MAINUI_UI_PATH: Final = _resource('mainui.ui')
SETTINGSUI_UI_PATH: Final = _resource('settingsui.ui')

GECKODRIVER_PATH: Final = _resource('geckodriver.exe')

SETTINGS_USERNAME: Final = 'username'
SETTINGS_PASSWORD: Final = 'password'
SETTINGS_DATA_PATHS: Final = 'dataPaths'
