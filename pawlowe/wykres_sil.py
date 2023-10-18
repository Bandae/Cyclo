from PySide6.QtWidgets import QTabWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QPushButton, QMainWindow, QWidget, QMainWindow
from PySide6.QtGui import QIcon, QPainter
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
import math

class WykresSil(QChartView):
    def __init__(self,dane,sily):
        super().__init__()

        self.seria = QLineSeries()

        for i in range(dane[0]):

            if i==0:
                self.seria.append(i,0)
            elif dane[0]%2==0:
                if dane[0]/2>i:
                    self.seria.append(i,sily[i-1])
                else:
                    self.seria.append(i,0)
            else:
                if (dane[0]-1)/2>i:
                    self.seria.append(i,sily[i-1])
                else:
                    self.seria.append(i,0)

        self.chart = QChart()
        self.chart.legend().hide()
        self.chart.addSeries(self.seria)
        self.chart.setTitle("Wyres Sił w rolkach")
        self.setRenderHint(QPainter.Antialiasing)

        os_x = QValueAxis()
        os_y = QValueAxis()




        self.setChart(self.chart)





