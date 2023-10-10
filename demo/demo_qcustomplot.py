import sys
from datetime import datetime
from datetime import time
from decimal import Decimal

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QPen
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QMainWindow
from QCustomPlot_PyQt6 import QCP
from QCustomPlot_PyQt6 import QCPAxisTickerDateTime
from QCustomPlot_PyQt6 import QCustomPlot

from movs import read_txt

app = QApplication(sys.argv)

BPOLPATH = '../../movs-data/BPOL_accumulator_vitomamma.txt'

_, rows = read_txt(BPOLPATH, 'vitomamma')

customPlot = QCustomPlot()

graphVitomamma = customPlot.addGraph()
graphVitomamma.setPen(QPen(Qt.GlobalColor.darkGreen))
graphVitomamma.setBrush(QBrush(QColor(0, 0, 255, 20)))

v = Decimal(0)
x, y = [], []
for row in sorted(rows, key=lambda row: row.date):
    d = row.date
    v += row.money
    x.append(datetime.combine(d, time()).timestamp())
    y.append(v)
graphVitomamma.setData(x, y)


customPlot.rescaleAxes()
customPlot.setInteraction(QCP.Interaction.iRangeDrag)
customPlot.setInteraction(QCP.Interaction.iRangeZoom)
customPlot.setInteraction(QCP.Interaction.iSelectPlottables)

dateTicker = QCPAxisTickerDateTime()
customPlot.xAxis.setTicker(dateTicker)

customPlot.legend.setVisible(True)
customPlot.legend.setBrush(QColor(255, 255, 255, 150))

window = QMainWindow()
window.resize(800, 600)
window.setCentralWidget(customPlot)
window.show()
sys.exit(app.exec())
