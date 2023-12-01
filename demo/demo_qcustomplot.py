from datetime import date
from decimal import Decimal
from functools import partial
from operator import attrgetter
from sys import argv

from movs import read_txt
from movs.model import Rows
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
from QCustomPlot_PyQt6 import QCPGraph


def timestamp(d: date) -> float:
    return QCPAxisTickerDateTime.dateTimeToKey(d)

b = False
def _add_graph(plot: QCustomPlot, rows: Rows) -> None:
    global b
    graph = plot.addGraph()
    graph.setPen(QPen(Qt.GlobalColor.darkGreen))
    graph.setBrush(QBrush(QColor(255 if b else 0, 0, 0 if b else 255, 20)))
    graph.setName(rows.name)
    graph.setLineStyle(QCPGraph.LineStyle.lsStepLeft)

    value: Decimal | None = None
    for row in sorted(rows, key=attrgetter('date')):
        value = row.money if value is None else (value + row.money)
        graph.addData(timestamp(row.date), value)

    b = not b


def make_plot(rowss: list[Rows], parent: QWidget | None = None) -> QCustomPlot:
    plot = QCustomPlot(parent)

    plot.legend.setVisible(True)
    plot.legend.setBrush(QColor(255, 255, 255, 150))

    plot.xAxis.rangeChanged.connect(lambda _: plot.replot())

    for rows in rowss:
        _add_graph(plot, rows)

    plot.rescaleAxes()
    plot.setInteraction(QCP.Interaction.iRangeDrag)
    plot.setInteraction(QCP.Interaction.iRangeZoom)
    plot.setInteraction(QCP.Interaction.iSelectPlottables)

    dateTicker = QCPAxisTickerDateTime()
    dateTicker.setDateTimeFormat('yyyy\ndd/MM')
    dateTicker.setTickCount(rows[0].date.year-rows[-1].date.year)
    plot.xAxis.setTicker(dateTicker)
    plot.xAxis.setTicks(True)
    plot.xAxis.setSubTicks(True)

    return plot


def plotSetRangeLower(self: QCustomPlot, value: int)-> None:
    d = date.fromordinal(value)
    t = timestamp(d)
    self.xAxis.setRangeLower(t)


def main() -> None:
    _, rows_m = read_txt('../../movs-data/BPOL_accumulator_vitomamma.txt',
                       'vitomamma')
    _, rows_e = read_txt('../../movs-data/BPOL_accumulator_vitoelena.txt',
                       'vitoelena')

    app = QApplication(argv)

    mainapp = QWidget()

    plot = make_plot([rows_m, rows_e], mainapp)
    slider = QSlider(Qt.Orientation.Horizontal, mainapp)

    slider.setMinimum(min(rows[-1].date.toordinal() for rows in (rows_m, rows_e)))
    slider.setMaximum(max(rows[0].date.toordinal() for rows in (rows_m, rows_e)))
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
