from logging import INFO
from logging import basicConfig
from logging import getLogger
from sys import argv

from movsviewer.settings import Settings

logger = getLogger(__name__)


def dump(settings: Settings, prefix: str = '') -> None:
    logger.info('%susername: %s', prefix, settings.username)
    logger.info('%spassword: %s', prefix, settings.password)
    logger.info('%sdata_paths:', prefix)
    for data_path in settings.data_paths:
        logger.info('\t%s', data_path)


def set_password(settings: Settings, password: str) -> None:
    dump(settings, 'orig ')
    settings.password = password
    dump(settings, 'new  ')


def set_data_paths(settings: Settings, data_paths: list[str]) -> None:
    dump(settings, 'orig ')
    settings.data_paths = data_paths
    dump(settings, 'new  ')


def main() -> None:
    basicConfig(level=INFO, format='%(message)s')

    arg, *args = argv

    settings = Settings([])
    if not args or args in (['-d'], ['--dump']):
        dump(settings)
    elif args[0] in ('-P', '--password') and len(args) == 2:  # noqa:PLR2004
        set_password(settings, args[1])
    elif args[0] in ('-p', '--data-paths') and args[1:]:
        set_data_paths(settings, args[1:])
    else:  # usage
        logger.warning('uso: %s [-d] | [-P password] | [-p path,path]', arg)


if __name__ == '__main__':
    main()
