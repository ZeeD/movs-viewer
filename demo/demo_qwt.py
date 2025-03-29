from collections import defaultdict
from datetime import date
from itertools import accumulate
from operator import attrgetter
from sys import argv
from typing import TYPE_CHECKING

from guilib.chartslider.chartslider import ChartSlider
from guilib.chartwidget.model import Column
from guilib.chartwidget.model import ColumnHeader
from guilib.chartwidget.model import ColumnProto
from guilib.chartwidget.model import Info
from guilib.chartwidget.model import InfoProto
from guilib.chartwidget.viewmodel import SortFilterViewModel
from guilib.qwtplot.plot import Plot
from movslib.movs import read_txt
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from collections.abc import Iterable
    from decimal import Decimal

    from movslib.model import Row
    from movslib.model import Rows


def load_infos(*fn_names: tuple[str, str]) -> list[InfoProto]:
    def acc(rows: 'Rows') -> 'Iterable[tuple[date, Decimal]]':
        def func(a: 'tuple[date, Decimal]', b: 'Row') -> 'tuple[date, Decimal]':
            return (b.date, a[1] + b.money)

        it = iter(sorted(rows, key=attrgetter('date')))
        head = next(it)
        return accumulate(it, func, initial=(head.date, head.money))

    tmp = defaultdict[date, list[ColumnProto]](list)
    for fn, name in fn_names:
        _, rows = read_txt(fn, name)
        ch = ColumnHeader(rows.name)
        for d, m in acc(rows):
            tmp[d].append(Column(ch, m))
    return [Info(d, tmp[d]) for d in sorted(tmp)]


def main() -> None:
    fn_names = [
        (
            '/home/zed/eclipse-workspace/movs-data/BPOL_accumulator_vitomamma.txt',
            'vitomamma',
        ),
        (
            '/home/zed/eclipse-workspace/movs-data/BPOL_accumulator_vitoelena.txt',
            'vitoelena',
        ),
    ]

    app = QApplication(argv)

    model = SortFilterViewModel()
    widget = QWidget()
    plot = Plot(model, None)
    chart_slider = ChartSlider(model, widget, dates_column=0)
    layout = QVBoxLayout(widget)
    layout.addWidget(plot)
    layout.addWidget(chart_slider)
    widget.setLayout(layout)

    chart_slider.start_date_changed.connect(plot.start_date_changed)
    chart_slider.end_date_changed.connect(plot.end_date_changed)

    widget.show()

    model.update(load_infos(*fn_names))

    app.exec()


if __name__ == '__main__':
    main()
