from sys import argv

from guilib.chartslider.xchartslider import XChartSlider
from guilib.chartslider.ychartslider import YChartSlider
from guilib.chartwidget.viewmodel import SortFilterViewModel
from guilib.qwtplot.plot import Plot
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QWidget

from movsviewer.plotutils import load_infos


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
    x_chart_slider = XChartSlider(model, widget, dates_column=0)
    y_chart_slider = YChartSlider(model, widget, dates_column=0)

    layout = QGridLayout(widget)
    layout.addWidget(plot, 0, 0)
    layout.addWidget(x_chart_slider, 1, 0)
    layout.addWidget(y_chart_slider, 0, 1)
    widget.setLayout(layout)

    x_chart_slider.start_date_changed.connect(plot.start_date_changed)
    x_chart_slider.end_date_changed.connect(plot.end_date_changed)

    y_chart_slider.min_money_changed.connect(plot.min_money_changed)
    y_chart_slider.max_money_changed.connect(plot.max_money_changed)

    widget.show()

    model.update(load_infos(*fn_names))

    app.exec()


if __name__ == '__main__':
    main()
