from typing import Final

from pkg_resources import resource_filename


def _resource(filename: str) -> str:
    return resource_filename('mypyui', f'resources/{filename}')


MAINUI_UI_PATH: Final = _resource('mainui.ui')
SETTINGSUI_UI_PATH: Final = _resource('settingsui.ui')

SETTINGS_DATA_PATH: Final = 'dataPath'
SETTINGS_DATA_PATHS: Final = 'dataPaths'
