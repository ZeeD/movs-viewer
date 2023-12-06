from datetime import date
from sys import argv

from movs.model import KV
from movs import read_txt
from movs.model import Row
from .settings import Settings
from qtpy.QtWidgets import QMessageBox
from qtpy.QtWidgets import QWidget


def validate_saldo(kv: KV, csv: list[Row], messages: list[str]) -> bool:
    messages.append(f'bpol.saldo_al:                      {kv.saldo_al}')
    if kv.saldo_al:
        ultimo_update = (date.today() - kv.saldo_al).days
        messages.append(f'ultimo update:                      {ultimo_update} giorni fa')
    messages.append(f'bpol.saldo_contabile:               {float(kv.saldo_contabile):_}')
    messages.append(
        f'bpol.saldo_disponibile:             {float(kv.saldo_disponibile):_}')

    s = sum(item.money for item in csv)
    messages.append(f'Σ (item.accredito - item.addebito): {float(s):_}')
    ret = kv.saldo_contabile == s == kv.saldo_disponibile
    if not ret:
        delta = max([abs(kv.saldo_contabile-s), abs(s-kv.saldo_disponibile)])
        messages.append(f'Δ:                                  {float(delta):_}')
    return ret


def validate_dates(csv: list[Row], messages: list[str]) -> bool:
    data_contabile: date | None = None
    for row in csv:
        if data_contabile is not None and data_contabile < row.data_contabile:
            messages.append(f'{data_contabile} < {row.data_contabile}!')
            return False
    return True


def validate(fn: str, messages: list[str]) -> bool:
    messages.append(fn)
    kv, csv = read_txt(fn)
    return all([validate_saldo(kv, csv, messages), validate_dates(csv, messages)])


class Validator:
    def __init__(self, parent: QWidget, settings: Settings) -> None:
        self.parent = parent
        self.settings = settings

    def validate(self) -> bool:
        for fn in self.settings.data_paths:
            messages: list[str] = []
            if not validate(fn, messages):
                button = QMessageBox.warning(self.parent, f'{fn} seems has some problems!', '\n'.join(messages))
                print(f'{button=}') # TODO use button to check for continue/skip
                return False
        return True

def main() -> None:
    if not argv[1:]:
        raise SystemExit(f'uso: {argv[0]} ACCUMULATOR...')

    for fn in argv[1:]:
        messages: list[str] = []
        if not validate(fn, messages):
            print('\n'.join(messages))
            raise SystemExit(f'{fn} seems has some problems!')
