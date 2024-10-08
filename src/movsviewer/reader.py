from typing import TYPE_CHECKING
from typing import Protocol
from typing import overload

from movslib.libretto import read_libretto
from movslib.movs import read_txt

if TYPE_CHECKING:
    from movslib.model import KV
    from movslib.model import Row
    from movslib.model import Rows


class Reader(Protocol):
    @overload
    def __call__(self, fn: str) -> 'tuple[KV, list[Row]]': ...

    @overload
    def __call__(self, fn: str, name: str) -> 'tuple[KV, Rows]': ...

    def __call__(
        self, fn: str, name: str | None = None
    ) -> 'tuple[KV, list[Row] | Rows]': ...


def _get_reader(fn: str) -> Reader:
    if fn.endswith('.xlsx'):
        return read_libretto
    return read_txt


@overload
def read(fn: str) -> 'tuple[KV, list[Row]]': ...


@overload
def read(fn: str, name: str) -> 'tuple[KV, Rows]': ...


def read(fn: str, name: str | None = None) -> 'tuple[KV, list[Row] | Rows]':
    reader = _get_reader(fn)
    return reader(fn) if name is None else reader(fn, name)
