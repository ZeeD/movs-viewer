from sys import argv

from guilib.chartslider.chartslider import ChartSlider
from guilib.chartwidget.viewmodel import SortFilterViewModel
from guilib.qwtplot.plot import Plot
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QVBoxLayout
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
