from unittest import TestCase

from movslib.libretto import read_libretto
from movslib.reader import _get_reader


class TestReader(TestCase):
    def test_get_reader(self) -> None:
        for fn, expected in [
            ('~/Desktop/movimenti_libretto_000053361801.xlsx', read_libretto)
        ]:
            with self.subTest(fn=fn, expected=expected):
                actual = _get_reader(fn)
                self.assertIs(expected, actual)
