from datetime import UTC
from datetime import date
from datetime import datetime
from logging import INFO
from logging import basicConfig
from logging import getLogger
from pathlib import Path
from sys import argv
from typing import TYPE_CHECKING

from movslib.reader import read

if TYPE_CHECKING:
    from movslib.model import KV
    from movslib.model import Rows

logger = getLogger(__name__)


def validate_saldo(kv: 'KV', csv: 'Rows', messages: list[str]) -> bool:
    s = sum(item.money for item in csv)
    d = abs(kv.saldo_contabile - s)

    today = datetime.now(tz=UTC).date()
    saldo_al = kv.saldo_al if kv.saldo_al is not None else today
    messages.append(
        f'{csv.name} @ {saldo_al} ({(today - saldo_al).days} giorni fa)'
    )
    messages.append(
        f'saldo_contabile: {float(kv.saldo_contabile):_} - '
        f'saldo_disponibile: {float(kv.saldo_disponibile):_}'
    )
    messages.append(f'Σ:               {float(s):_}')
    messages.append(f'Δ:               {float(d):_}')
    return kv.saldo_contabile == s


def validate_dates(csv: 'Rows', messages: list[str]) -> bool:
    data_contabile: date | None = None
    for row in csv:
        if data_contabile is not None and data_contabile < row.data_contabile:
            messages.append(f'{data_contabile} < {row.data_contabile}!')
            return False
    return True


def validate(fn: str, messages: list[str]) -> bool:
    kv, csv = read(fn, Path(fn).stem)
    return all(
        [validate_saldo(kv, csv, messages), validate_dates(csv, messages)]
    )


def validate_fn(fn: str, *, prefix: str = '') -> bool:
    messages: list[str] = []
    ok = validate(fn, messages)
    for message in messages:
        logger.info('%s%s', prefix, message)
    if not ok:
        logger.error('%s%s seems has some problems!', prefix, fn)
    return ok


def main() -> None:
    basicConfig(level=INFO, format='%(message)s')

    if not argv[1:]:
        logger.error('uso: %s ACCUMULATOR...', argv[0])
        raise SystemExit

    for fn in argv[1:]:
        ok = validate_fn(fn)
        if not ok:
            raise SystemExit
