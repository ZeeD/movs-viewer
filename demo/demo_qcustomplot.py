from datetime import date
from datetime import datetime, timedelta
from datetime import time
from decimal import Decimal
from operator import attrgetter

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QPen
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QSlider
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget
from QCustomPlot_PyQt6 import QCP
from QCustomPlot_PyQt6 import QCPAxisTickerDateTime
from QCustomPlot_PyQt6 import QCustomPlot

from movs import read_txt
from movs.model import Rows

from functools import partial


def timestamp(d: date) -> float:
    return datetime.combine(d, time()).timestamp()


def make_plot(rows: Rows, parent: QWidget | None = None) -> QCustomPlot:
    plot = QCustomPlot(parent)

    graph = plot.addGraph()
    graph.setPen(QPen(Qt.GlobalColor.darkGreen))
    graph.setBrush(QBrush(QColor(0, 0, 255, 20)))
    graph.setName(rows.name)

    value: Decimal | None = None
    for row in sorted(rows, key=attrgetter('date')):
        value = row.money if value is None else (value + row.money)
        graph.addData(timestamp(row.date), value)

    plot.rescaleAxes()
    plot.setInteraction(QCP.Interaction.iRangeDrag)
    plot.setInteraction(QCP.Interaction.iRangeZoom)
    plot.setInteraction(QCP.Interaction.iSelectPlottables)

    dateTicker = QCPAxisTickerDateTime()
    dateTicker.setDateTimeFormat('yyyy')
    dateTicker.setTickCount(rows[0].date.year-rows[-1].date.year)
    plot.xAxis.setTicker(dateTicker)
    # plot.xAxis.setRange(lower, upper)
    # setRangeLower
    # setRangeUpper
    # rescale
    plot.xAxis.setTicks(True)
    plot.xAxis.setSubTicks(True)

    plot.legend.setVisible(True)
    plot.legend.setBrush(QColor(255, 255, 255, 150))
    return plot


def plotSetRangeLower(self: QCustomPlot, value: int)-> None:
    d = date.fromordinal(value)
    t = timestamp(d)
    self.xAxis.setRangeLower(t)


def main() -> None:
    _, rows = read_txt('../../movs-data/BPOL_accumulator_vitomamma.txt',
                       'vitomamma')

    app = QApplication([__file__])

    mainapp = QWidget()

    plot = make_plot(rows, mainapp)
    slider = QSlider(Qt.Orientation.Horizontal, mainapp)

    slider.setMinimum(rows[-1].date.toordinal())
    slider.setMaximum(rows[0].date.toordinal())
    slider.setSingleStep(1)
    slider.setPageStep(365)
    slider.valueChanged.connect(partial(plotSetRangeLower, plot))

    layout = QVBoxLayout(mainapp)
    layout.addWidget(plot)
    layout.addWidget(slider)
    mainapp.setLayout(layout)

    mainapp.resize(800, 600)
    mainapp.show()

    app.exec()


if __name__ == '__main__':
    main()
