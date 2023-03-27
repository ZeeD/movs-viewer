from datetime import date
from datetime import datetime
from datetime import time
from decimal import Decimal

from PySide6.QtCharts import QChartView
from PySide6.QtCharts import QDateTimeAxis
from PySide6.QtCharts import QLineSeries
from PySide6.QtCharts import QValueAxis
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication


def chartView(dates: list[date], *valuess: list[Decimal]) -> QChartView:
    chart_view = QChartView()
    chart = chart_view.chart()

    value_axis = QValueAxis(chart)
    date_axis = QDateTimeAxis(chart)
    date_axis.setFormat('yyyy/MM')

    chart.addAxis(value_axis, Qt.AlignmentFlag.AlignLeft)
    chart.addAxis(date_axis, Qt.AlignmentFlag.AlignBottom)

    for values in valuess:
        series = QLineSeries(chart)

        for date, value in zip(dates, values):
            series.append(datetime.combine(date, time()).timestamp() * 1000,
                          float(value))

        chart.addSeries(series)

        series.attachAxis(value_axis)
        series.attachAxis(date_axis)

    all_values = [value for values in valuess for value in values]
    value_axis.setMin(float(min(all_values)))
    value_axis.setMax(float(max(all_values)))

    return chart_view


def main() -> None:
    qapplication = QApplication()
    try:
        dates = [date(2000, 1, 1), date(2020, 1, 1)]
        valuesOrig = [Decimal(1), Decimal(0)]
        valuesAct = [Decimal(2), Decimal(3)]

        chart_view = chartView(dates, valuesOrig, valuesAct)
        chart_view.resize(1000, 1000)
        chart_view.show()
    finally:
        qapplication.exec()


if __name__ == '__main__':
    main()
