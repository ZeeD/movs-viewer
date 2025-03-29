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


def acc(rows: 'Rows') -> 'Iterable[tuple[date, Decimal]]':
    def func(a: 'tuple[date, Decimal]', b: 'Row') -> 'tuple[date, Decimal]':
        return (b.date, a[1] + b.money)

    it = iter(sorted(rows, key=attrgetter('date')))
    head = next(it)
    return accumulate(it, func, initial=(head.date, head.money))


def rowss2sort_filter_view_model(*rowss: 'Rows') -> SortFilterViewModel:
    tmp = defaultdict[date, list[ColumnProto]](list)
    for rows in rowss:
        ch = ColumnHeader(rows.name)
        for d, m in acc(rows):
            tmp[d].append(Column(ch, m))
    model = SortFilterViewModel()
    model.update([Info(d, tmp[d]) for d in sorted(tmp)])
    return model


def main() -> None:
    _, rows_vm = read_txt(
        '/home/zed/eclipse-workspace/movs-data/BPOL_accumulator_vitomamma.txt',
        'vitomamma',
    )
    _, rows_ve = read_txt(
        '/home/zed/eclipse-workspace/movs-data/BPOL_accumulator_vitoelena.txt',
        'vitoelena',
    )

    model = rowss2sort_filter_view_model(rows_vm, rows_ve)

    app = QApplication(argv)

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

    plot.model_reset()

    app.exec()


if __name__ == '__main__':
    main()
