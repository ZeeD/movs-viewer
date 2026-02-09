from logging import INFO
from logging import basicConfig
from logging import getLogger
from sys import argv

from movslib.buoni import read_buoni

logger = getLogger(__name__)


def main() -> None:
    basicConfig(level=INFO)

    for fn in argv[1:]:
        _, csv = read_buoni(fn)
        for row in csv:
            logger.info(
                '%s, %s, %s, %s, %s',
                f'{row.data_contabile:%m/%d/%Y}',
                f'{row.data_valuta:%m/%d/%Y}',
                row.addebiti,
                row.accrediti,
                row.descrizione_operazioni,
            )


if __name__ == '__main__':
    main()
