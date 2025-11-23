from datetime import date
from datetime import timedelta
from unittest import TestCase

from movslib.model import Row

from movsmerger.movsmerger import merge_rows


def d(days: int = 0) -> date:
    return date(2020, 1, 1) + timedelta(days=days)


ROW0 = Row(d(0), d(0), None, None, '')
ROW1 = Row(d(1), d(1), None, None, '')
ROW2 = Row(d(2), d(2), None, None, '')
ROW3 = Row(d(3), d(3), None, None, '')
ROW4 = Row(d(4), d(4), None, None, '')


class MergeRowsTest(TestCase):
    maxDiff = None

    def test_empty_empty(self) -> None:
        self.assertEqual([], merge_rows([], []))

    def test_empty_full(self) -> None:
        self.assertEqual([ROW0], merge_rows([], [ROW0]))

    def test_full_full_equals(self) -> None:
        self.assertEqual([ROW0], merge_rows([ROW0], [ROW0]))

    def test_full_full_new_data(self) -> None:
        self.assertEqual([ROW1, ROW0], merge_rows([ROW0], [ROW1]))

    def test_old_data_overlap(self) -> None:
        expected = [ROW4, ROW3, ROW2, ROW1, ROW0]

        acc = [ROW4, ROW3, ROW0]
        new = [ROW3, ROW2, ROW1, ROW0]

        self.assertEqual(expected, merge_rows(acc, new))

    def test_old_data(self) -> None:
        expected = [ROW4, ROW3, ROW2, ROW1, ROW0]

        acc = [ROW4, ROW3, ROW0]
        new = [ROW2, ROW1]

        self.assertEqual(expected, merge_rows(acc, new))
