from collections import defaultdict
from datetime import date
from datetime import timedelta
from decimal import Decimal
from itertools import accumulate
from operator import attrgetter
from typing import TYPE_CHECKING

from guilib.chartslider.chartslider import ChartSlider
from guilib.chartwidget.model import Column
from guilib.chartwidget.model import ColumnHeader
from guilib.chartwidget.model import ColumnProto
from guilib.chartwidget.model import Info
from guilib.chartwidget.model import InfoProto
from guilib.qwtplot.plot import Plot
from movslib.reader import read
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from movsviewer.merger import read_and_merge

if TYPE_CHECKING:
    from collections.abc import Iterable

    from guilib.chartwidget.viewmodel import SortFilterViewModel
    from movslib.model import Row
    from movslib.model import Rows


def _acc_reset_by_year(rows: 'Rows') -> 'Iterable[tuple[date, Decimal]]':
    if not rows:
        return []

    def func(a: tuple[date, 'Decimal'], b: 'Row') -> tuple[date, 'Decimal']:
        if b.date.year != a[0].year:
            return b.date, b.money

        return b.date, a[1] + b.money

    it = iter(sorted(rows, key=attrgetter('date')))
    head = next(it)
    return accumulate(it, func, initial=(head.date, head.money))


def _acc(rows: 'Rows') -> 'Iterable[tuple[date, Decimal]]':
    def func(a: tuple[date, 'Decimal'], b: 'Row') -> tuple[date, 'Decimal']:
        return b.date, a[1] + b.money

    it = iter(sorted(rows, key=attrgetter('date')))
    head = next(it)
    return accumulate(it, func, initial=(head.date, head.money))


def _acc_multi_years(
    rows: 'Rows',
) -> 'Iterable[tuple[int, Iterable[tuple[date, Decimal]]]]':
    """Yield (year, acc in that year)."""
    if not rows:
        return

    previous_year: int | None = None
    previous_year_acc: list[tuple[date, Decimal]] = []

    for row in sorted(rows, key=attrgetter('date')):
        if row.date.year != previous_year:
            if previous_year is not None:
                yield previous_year, previous_year_acc
            previous_year = row.date.year
            previous_year_acc = [(date(row.date.year, 1, 1), Decimal(0))]
        previous_year_acc.append(
            (row.date, previous_year_acc[-1][1] + row.money)
        )

    if previous_year is not None:
        yield previous_year, previous_year_acc


def load_infos(*fn_names: tuple[str, str] | list[str]) -> list[InfoProto]:
    tmp = defaultdict[date, list[ColumnProto]](list)
    for fn_name in fn_names:
        if isinstance(fn_name, list):
            data_paths = fn_name
            rows = read_and_merge(data_paths)
        else:
            fn, name = fn_name
            _, rows = read(fn, name)

        ch = ColumnHeader(rows.name, '€')
        for d, m in _acc(rows):
            tmp[d].append(Column(ch, m))

        ch_year = ColumnHeader(f'{rows.name} (by year)', '€')
        for d, m in _acc_reset_by_year(rows):
            tmp[d].append(Column(ch_year, m))

        for y, it in _acc_multi_years(rows):
            ch_y = ColumnHeader(f'{rows.name} ({y})', '€')
            for d, m in it:
                tmp[d].append(Column(ch_y, m))

    sorted_days = sorted(tmp)

    # add +/- 1 months of padding
    ret: list[InfoProto] = []
    ret.append(Info(sorted_days[0] - timedelta(days=30), []))
    ret.extend(Info(d, tmp[d]) for d in sorted_days)
    ret.append(Info(sorted_days[-1] + timedelta(days=30), []))

    return ret


class PlotAndSliderWidget(QWidget):
    """Composition of a Plot and a (Chart)Slider."""

    def __init__(
        self, model: 'SortFilterViewModel', parent: QWidget | None
    ) -> None:
        super().__init__(parent)

        plot = Plot(model, self)
        chart_slider = ChartSlider(model, self, dates_column=0)

        layout = QVBoxLayout(self)
        layout.addWidget(plot)
        layout.addWidget(chart_slider)
        self.setLayout(layout)

        chart_slider.start_date_changed.connect(plot.start_date_changed)
        chart_slider.end_date_changed.connect(plot.end_date_changed)
