import logging
from logging import INFO
from logging import basicConfig
from logging import getLogger
from sys import stdout
from typing import TYPE_CHECKING

from movslib.autotag.autotag import autotag
from movslib.reader import read

if TYPE_CHECKING:
    from movslib.model import Rows

logger = getLogger(__name__)


def demo_autotag(rows: 'Rows') -> None:
    tag_rows = autotag(rows)

    # basic stats
    tagged_rows = len([row for row in tag_rows if row.tags])

    logger.info(
        '%s/%s tagged rows (~%s%%)',
        tagged_rows,
        len(tag_rows),
        tagged_rows * 100 / len(tag_rows),
    )

    for tag_row in tag_rows:
        logger.info(
            '%s [%s]', tag_row.descrizione_operazioni, ','.join(tag_row.tags)
        )


def main() -> None:
    basicConfig(format='%(message)s', level=INFO, stream=stdout)
    logging.raiseExceptions = False

    _, rows = read(
        '/home/zed/eclipse-workspace/movs-data/BPOL_accumulator_vitoelena.txt',
        'vitoelena',
    )

    demo_autotag(rows)


if __name__ == '__main__':
    main()
