from sys import argv

from guilib.chartwidget.viewmodel import SortFilterViewModel
from PySide6.QtWidgets import QApplication

from movsviewer.plotutils import PlotAndSliderWidget
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
    widget = PlotAndSliderWidget(model, None)

    widget.show()

    by_year = '--by-year' in app.arguments()
    multi_years = '--multi-years' in app.arguments()

    model.update(
        load_infos(*fn_names, by_year=by_year, multi_years=multi_years)
    )

    app.exec()


if __name__ == '__main__':
    main()
