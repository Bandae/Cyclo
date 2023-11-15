from PySide2.QtWidgets import QTabWidget, QVBoxLayout
from PySide2.QtGui import QPainter
from PySide2.QtCharts import QtCharts

def punkty_wykresu(wartosci):
    return [[i, wartosci[i - 1]] for i in range(1, len(wartosci) + 1)]
    # punkty = []
    # for i in range(1, len(wartosci) + 1):
    #     if wartosci[i - 1] < 0:
    #         punkty.append([i, 0])
    #     else:
    #         punkty.append([i, wartosci[i - 1]])
    # return punkty


class Wykres(QtCharts.QChartView):
    def __init__(self, chart_title, x_title, y_title):
        super().__init__()
        self.chart = QtCharts.QChart()
        self.chart.legend().hide()
        self.chart.setTitle(chart_title)
        self.setRenderHint(QPainter.Antialiasing)

        self.series = QtCharts.QLineSeries()
        self.chart.addSeries(self.series)

        self.os_x = QtCharts.QValueAxis()
        self.os_y = QtCharts.QValueAxis()
        self.os_x.setTitleText(x_title)
        self.os_x.setLabelFormat('%.0f')
        self.chart.setAxisX(self.os_x, self.series)
        
        self.os_y.setTitleText(y_title)
        # self.os_y.setTickCount(1)
        self.os_y.setLabelFormat('%.2f')
        self.setChart(self.chart)
        self.chart.setAxisY(self.os_y, self.series)
    
    def update_data(self, wartosci):
        self.series.clear()
        
        for wart in wartosci:
            self.series.append(wart[0], wart[1])
        
        self.os_x.setRange(wartosci[0][0], wartosci[len(wartosci)-1][0])
        self.os_y.setRange(min([i[1] for i in wartosci]), max([i[1] for i in wartosci]))
        self.chart.update()
         

class ChartTab(QTabWidget):
    def __init__(self):
        super().__init__()
        self.wykres_sil = Wykres("Siły na sworzniach", "numer sworznia", "Siła [N]")
        self.wykres_naciskow = Wykres("Naciski powierzchniowe na sworzniach", "numer sworznia", "Wartość Nacisku [MPa]")
        self.wykres_strat = Wykres("Straty mocy na sworzniach", "numer sworznia", "Straty mocy [W]")

        tabs = QTabWidget()
        tabs.setMovable(True)
        tabs.setTabPosition(QTabWidget.North)
        tabs.addTab(self.wykres_sil, "Siły")
        tabs.addTab(self.wykres_naciskow, "Naciski")
        tabs.addTab(self.wykres_strat, "Straty")

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        self.setLayout(layout)

    def update_charts(self, data):
        if data.get("sily") and data["sily"] is not None:
            self.wykres_sil.update_data(punkty_wykresu(data["sily"]))
        if data.get("naciski") and data["naciski"] is not None:
            self.wykres_naciskow.update_data(punkty_wykresu(data["naciski"]))
        if data.get("straty") and data["straty"] is not None:
            self.wykres_strat.update_data(punkty_wykresu(data["straty"]))
