from typing import List
from pathlib import Path

from movs import read_txt
from movs.model import Row

from .tabui import main_window

MOVS_DATA_ROOT = Path(__file__).parent.parent.parent / 'movs-data'


def loader(path: str) -> List[Row]:
    _, data = read_txt(path)
    return list(data)


def main() -> None:
    preload_path = str(MOVS_DATA_ROOT / 'BPOL_accumulator_vitomamma.txt')
    with main_window(loader, preload_path) as window:
        window.show()
