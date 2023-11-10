from PySide6.QtWidgets import QTabWidget, QVBoxLayout
from PySide6.QtGui import QPainter
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis

def punkty_wykresu(liczba_zebow, wartosci):
    '''wartosci to albo sily albo naprezenia, dla obu takie samo liczenie'''
    punkty = []
    for i in range(liczba_zebow+1):
        if i==0:
            punkty.append([i+1,0])
        elif liczba_zebow%2==0:
            if liczba_zebow/2>i:
                punkty.append([i+1,wartosci[i-1]])
            else:
                punkty.append([i+1,0])
        else:
            if (liczba_zebow-1)/2>i:
                punkty.append([i+1,wartosci[i-1]])
            else:
                punkty.append([i+1,0])
    return punkty


class Wykres(QChartView):
    def __init__(self, chart_title, x_title, y_title):
        super().__init__()
        self.chart = QChart()
        self.chart.legend().hide()
        self.chart.setTitle(chart_title)
        self.setRenderHint(QPainter.Antialiasing)

        self.series = QLineSeries()
        self.chart.addSeries(self.series)

        self.os_x = QValueAxis()
        self.os_y = QValueAxis()
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


class Wykresy(QTabWidget):
    def __init__(self):
        super().__init__()
        self.wykres_sil = Wykres("Wykres Sił w rolkach", "Numer Rolki [n]", "Wartość Siły [kN]")
        self.wykres_naprezen = Wykres("Wykres Naprężeń w rolkach", "Numer Rolki [n]", "Wartość Nacisku [MPa]")
        self.wykres_strat_mocy = Wykres("Wykres Strat mocy w rolkach", "Numer Rolki [n]", "Wartość Straty [W]")

        tabs = QTabWidget()
        tabs.setMovable(True)
        tabs.setTabPosition(QTabWidget.North)
        tabs.addTab(self.wykres_sil, "Siły")
        tabs.addTab(self.wykres_naprezen, "Naprężenia")
        tabs.addTab(self.wykres_strat_mocy, "Straty Mocy")

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        self.setLayout(layout)

    def update_charts(self, liczba_zebow, data):
        if data.get("sily") and data["sily"] is not None:
            self.wykres_sil.update_data(punkty_wykresu(liczba_zebow, data["sily"]))
        if data.get("naprezenia") and data["naprezenia"] is not None:
            self.wykres_naprezen.update_data(punkty_wykresu(liczba_zebow, data["naprezenia"]))
        if data.get("straty_mocy") and data["straty_mocy"] is not None:
            self.wykres_strat_mocy.update_data(punkty_wykresu(liczba_zebow,data["straty_mocy"]))