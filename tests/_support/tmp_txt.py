from contextlib import contextmanager
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

from movslib.movs import write_txt

if TYPE_CHECKING:
    from collections.abc import Iterable
    from collections.abc import Iterator

    from movslib.model import KV
    from movslib.model import Row


@contextmanager
def tmp_txt(kv: 'KV', csv: 'Iterable[Row]') -> 'Iterator[str]':
    with NamedTemporaryFile(suffix='.txt') as ntf:
        fn = ntf.name
        write_txt(fn, kv, csv)

        yield fn
