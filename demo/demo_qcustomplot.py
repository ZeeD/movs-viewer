from datetime import date
from datetime import datetime
from datetime import time
from decimal import Decimal
from operator import attrgetter

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QPen
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWidgets import QSlider
from PyQt6.QtWidgets import QVBoxLayout
from QCustomPlot_PyQt6 import QCP
from QCustomPlot_PyQt6 import QCPAxisTickerDateTime
from QCustomPlot_PyQt6 import QCustomPlot

from movs import read_txt
from movs.model import Rows


def timestamp(d: date) -> float:
    return datetime.combine(d, time()).timestamp()


def make_plot(rows: Rows) -> QCustomPlot:
    customPlot = QCustomPlot()

    graph = customPlot.addGraph()
    graph.setPen(QPen(Qt.GlobalColor.darkGreen))
    graph.setBrush(QBrush(QColor(0, 0, 255, 20)))
    graph.setName(rows.name)

    value: Decimal | None = None
    for row in sorted(rows, key=attrgetter('date')):
        value = row.money if value is None else (value + row.money)
        graph.addData(timestamp(row.date), value)

    customPlot.rescaleAxes()
    customPlot.setInteraction(QCP.Interaction.iRangeDrag)
    customPlot.setInteraction(QCP.Interaction.iRangeZoom)
    customPlot.setInteraction(QCP.Interaction.iSelectPlottables)

    dateTicker = QCPAxisTickerDateTime()
    dateTicker.setDateTimeFormat('yyyy')
    dateTicker.setTickCount(rows[0].date.year-rows[-1].date.year)
    customPlot.xAxis.setTicker(dateTicker)
    # customPlot.xAxis.setRange(lower, upper)
    # setRangeLower
    # setRangeUpper
    # rescale
    customPlot.xAxis.setTicks(True)
    customPlot.xAxis.setSubTicks(True)

    customPlot.legend.setVisible(True)
    customPlot.legend.setBrush(QColor(255, 255, 255, 150))
    return customPlot


def main() -> None:
    _, rows = read_txt('../../movs-data/BPOL_accumulator_vitomamma.txt',
                       'vitomamma')

    app = QApplication([__file__])

    mainapp = QMainWindow()

    plot = make_plot(rows)
    slider = QSlider()

    layout = QVBoxLayout()
    layout.addWidget(plot)
    layout.addWidget(slider)
    mainapp.setLayout(layout)

    mainapp.resize(800, 600)
    mainapp.show()

    app.exec()


if __name__ == '__main__':
    main()
