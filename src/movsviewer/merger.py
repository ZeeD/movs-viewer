from operator import attrgetter
from pathlib import Path

from movslib.model import Rows
from movslib.reader import read


def read_and_merge(data_paths: list[str]) -> 'Rows':
    name = '&'.join(Path(data_path).stem for data_path in data_paths)

    data = Rows(name, [])
    for data_path in data_paths:
        data.extend(read(data_path)[1])
    data.sort(key=attrgetter('date'), reverse=True)

    return data
