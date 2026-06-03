from datetime import timedelta
from sys import argv

from guilib.chartwidget.model import Column
from guilib.chartwidget.model import ColumnHeader
from guilib.chartwidget.model import Info
from guilib.chartwidget.viewmodel import SortFilterViewModel
from guilib.qwtplot.plot import Plot
from PySide6.QtWidgets import QApplication

from movslib.model import ZERO
from movslib.model import Row
from movslib.reader import read
from qwt.plot_curve import QwtPlotCurve


def convert(rows: list[Row]) -> list[Info]:
    # find all chs
    hs = {}
    for row in rows:
        if 'sottoscrizione' in row.descrizione_operazioni:
            do = row.descrizione_operazioni[15:]
            k = f'{row.date} - {do}'
            days = int(do.split(',')[1].split(' ')[0])
            v = {
                's': row.date,
                'r': row.date+timedelta(days=days),
                'm': row.money
            }
            hs[k] = v
        elif  'rimborso' in row.descrizione_operazioni:
            do = row.descrizione_operazioni[9:]
            for k in hs:
                if not k.endswith(do):
                    continue
                v = hs[k]
                if v['r'] != row.date:
                    continue
                v['m2'] = row.money
                break
            else:
                print(f'!!!! NOT FOUND !!! [{do=}]')
                print(f'{hs=}')

    converted = []
    for row in rows:
        if 'sottoscrizione' in row.descrizione_operazioni:
            ch = ColumnHeader(row.descrizione_operazioni[15:], '€')
            # add 0
            converted.append(Info(row.date, [Column(ch, ZERO)]))
            converted.append(Info(row.date, [Column(ch, -row.money)]))
        elif 'rimborso' in row.descrizione_operazioni:
            ch = ColumnHeader(row.descrizione_operazioni[9:], '€')
            converted.append(Info(row.date, [Column(ch, row.money)]))
    return converted

def read_and_convert(fns: list[str]) -> list[Info]:
    ret = []
    for fn in fns:
        _, rows = read(fn)
        ret.extend(convert(rows))
    return ret


def draw(fns: list[str]) -> Plot:
    model = SortFilterViewModel()
    plot = Plot(model, None, curve_style=QwtPlotCurve.Lines)
    infos = read_and_convert(fns)
    model.update(infos)
    return plot


def main() -> None:
    app = QApplication(argv)

    plot = draw(app.arguments()[1:])
    plot.show()

    raise SystemExit(app.exec())


if __name__ == '__main__':
    main()
