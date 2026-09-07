from itertools import islice
from pathlib import Path
from typing import TYPE_CHECKING
from typing import overload

from movslib.model import KV
from movslib.model import Row
from movslib.model import Rows
from movslib.movs import read_csv
from movslib.movs import read_kv

if TYPE_CHECKING:
    from collections.abc import Iterable


def read_kv_libretto_txt(kv_raw: KV, rows: 'Iterable[Row]') -> KV:
    """Filtra righe attive, ritorna valore originale"""
    # TODO: actually do it
    return kv_raw


@overload
def read_libretto_txt(fn: str) -> tuple[KV, list[Row]]: ...


@overload
def read_libretto_txt(fn: str, name: str) -> tuple[KV, Rows]: ...


def read_libretto_txt(
    fn: str, name: str | None = None
) -> tuple[KV, list[Row] | Rows]:
    with Path(fn).open(encoding='UTF-8') as f:
        kv_file = islice(f, 8)
        csv_file = f
        kv_raw = read_kv(kv_file)
        csv = read_csv(csv_file)
        kv = read_kv_libretto_txt(kv_raw, csv)
        return kv, (list(csv) if name is None else Rows(name, csv))
