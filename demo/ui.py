from datetime import date
from datetime import datetime
from datetime import time
from decimal import Decimal
from typing import NamedTuple

from PySide6.QtCharts import QChartView
from PySide6.QtCharts import QDateTimeAxis
from PySide6.QtCharts import QLineSeries
from PySide6.QtCharts import QValueAxis
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication


class Point(NamedTuple):
    when: date
    howmuch: Decimal


class Data(NamedTuple):
    name: str
    values: list[Point]


def chartView(*datas: Data) -> QChartView:
    chart_view = QChartView()
    chart = chart_view.chart()

    value_axis = QValueAxis(chart)
    date_axis = QDateTimeAxis(chart)
    date_axis.setFormat('yyyy/MM')

    chart.addAxis(value_axis, Qt.AlignmentFlag.AlignLeft)
    chart.addAxis(date_axis, Qt.AlignmentFlag.AlignBottom)

    for data in datas:
        series = QLineSeries(chart)
        series.setName(data.name)

        for when, howmuch in data.values:
            series.append(datetime.combine(when, time()).timestamp() * 1000,
                          float(howmuch))

        chart.addSeries(series)

        series.attachAxis(value_axis)
        series.attachAxis(date_axis)

    howmuchs = [howmuch for data in datas for (when, howmuch) in data.values]
    value_axis.setMin(float(min(howmuchs)))
    value_axis.setMax(float(max(howmuchs)))

    return chart_view


def main() -> None:
    qapplication = QApplication()
    try:
        dates = [date(2000, 1, 1), date(2020, 1, 1)]
        valuesOrig = Data('valuesOrig', [Point(*p)
                          for p in zip(dates, [Decimal(1), Decimal(0)])])
        valuesAct = Data('valuesAct', [Point(*p)
                         for p in zip(dates, [Decimal(2), Decimal(3)])])

        chart_view = chartView(valuesOrig, valuesAct)
        chart_view.resize(1000, 1000)
        chart_view.show()
    finally:
        qapplication.exec()


if __name__ == '__main__':
    main()
