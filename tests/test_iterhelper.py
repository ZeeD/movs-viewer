from unittest import TestCase

from movslib.iterhelper import zip_with_next


class TestIterHelper(TestCase):
    def test_zip_with_next(self) -> None:
        it = 'abc'
        last = 'z'

        expected = [('a', 'b'), ('b', 'c'), ('c', 'z')]
        actual = zip_with_next(it, last)

        self.assertListEqual(expected, list(actual))

    def test_zip_with_next_none(self) -> None:
        it = 1, 2
        last = None

        expected = [(1, 2), (2, None)]
        actual = zip_with_next(it, last)

        self.assertListEqual(expected, list(actual))
