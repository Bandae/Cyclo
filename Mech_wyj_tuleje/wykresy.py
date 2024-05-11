from PySide2.QtWidgets import QTabWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QGridLayout, QAbstractItemView, QHeaderView, QWidget
from PySide2.QtGui import QPainter
from PySide2.QtCharts import QtCharts
from PySide2.QtCore import Qt
# TODO: zrobic tolerance graph points lepiej. nie musze chyba tego robic tylko inna metode 
def graph_points(point_values, smooth_values):
    scatter_points = [[i, point_values[i - 1]] for i in range(1, len(point_values) + 1)]
    scale = len(point_values) / len(smooth_values)
    line_points = [[i * scale + 1, smooth_values[i]] for i in range(0, len(smooth_values))]
    return scatter_points, line_points


class Wykres(QtCharts.QChartView):
    def __init__(self, chart_title, x_title, y_title):
        super().__init__()
        self.chart = QtCharts.QChart()
        self.chart.legend().hide()
        self.chart.setTitle(chart_title)
        self.setRenderHint(QPainter.Antialiasing)

        self.os_x = QtCharts.QValueAxis()
        self.os_x.setTitleText(x_title)
        self.os_x.setLabelFormat('%.0f')
        self.chart.addAxis(self.os_x, Qt.AlignBottom)

        self.os_y = QtCharts.QValueAxis()
        self.os_y.setTitleText(y_title)
        self.os_y.setLabelFormat('%.2f')
        self.chart.addAxis(self.os_y, Qt.AlignLeft)
        
        # self.os_y.setTickCount(1)
        self.line_series = QtCharts.QLineSeries()
        self.point_series = QtCharts.QScatterSeries(name="wartość średnia")
        self.point_series.setColor("#529AB7")
        self.point_series.setMarkerSize(15)
        self.chart.addSeries(self.line_series)
        self.chart.addSeries(self.point_series)
        self.line_series.attachAxis(self.os_x)
        self.line_series.attachAxis(self.os_y)
        self.point_series.attachAxis(self.os_x)
        self.point_series.attachAxis(self.os_y)

        self.tol_series_low = QtCharts.QLineSeries(name="minimalna wartość")
        self.tol_series_high = QtCharts.QLineSeries(name="maksymalna wartość")
        self.chart.addSeries(self.tol_series_low)
        self.chart.addSeries(self.tol_series_high)
        self.tol_series_low.attachAxis(self.os_x)
        self.tol_series_low.attachAxis(self.os_y)
        self.tol_series_high.attachAxis(self.os_x)
        self.tol_series_high.attachAxis(self.os_y)
        
        self.setChart(self.chart)
    
    def update_data_tolerance(self, value_lists):
        self.chart.legend().show()
        self.line_series.clear()
        self.point_series.clear()
        self.tol_series_high.clear()
        self.tol_series_low.clear()
        for i, wart in enumerate(value_lists[0], 1):
            self.line_series.append(i, wart)
        for i, wart in enumerate(value_lists[1], 1):
            self.tol_series_low.append(i, wart)
        for i, wart in enumerate(value_lists[2], 1):
            self.tol_series_high.append(i, wart)
        
        self.os_x.setRange(1, len(value_lists[0]))
        self.os_y.setRange(0, max([i for i in value_lists[2]]))
        self.chart.update()

    def update_data(self, point_values, smooth_values):
        self.chart.legend().hide()
        self.line_series.clear()
        self.point_series.clear()
        self.tol_series_high.clear()
        self.tol_series_low.clear()
        for wart in smooth_values:
            self.line_series.append(wart[0], wart[1])
        for wart in point_values:
            self.point_series.append(wart[0], wart[1])

        self.os_x.setRange(point_values[0][0], point_values[-1][0])
        self.os_y.setRange(0, max([i[1] for i in smooth_values]))
        self.chart.update()


class Table(QTableWidget):
    TABLE_TITLES = ["Siły", "Naciski", "Straty"]
    def __init__(self, parent):
        super().__init__(parent)
        self.data = [[0], [0], [0]]
        self.setHorizontalHeaderLabels((self.TABLE_TITLES[0],))
        # self.verticalHeader().setVisible(False)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # self.setRowCount(6)
        self.setFixedWidth(80)
        self.setColumnCount(1)
        self.setColumnWidth(0, 45)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

    def update(self, new_data, open_tab):
        self.data = new_data
        self.changeTable(open_tab)

    def changeTable(self, open_tab):
        self.setHorizontalHeaderLabels((self.TABLE_TITLES[open_tab],))
        self.setRowCount(len(self.data[open_tab]))
        for i, value in enumerate(self.data[open_tab]):
            self.setItem(i, 0, QTableWidgetItem(str(value)))


class ChartTabs(QTabWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.wykres_sil = Wykres("Siły na sworzniach", "numer sworznia", "Siła [N]")
        self.wykres_naciskow = Wykres("Naciski powierzchniowe na sworzniach", "numer sworznia", "Wartość Nacisku [MPa]")
        self.wykres_strat = Wykres("Straty mocy na sworzniach", "numer sworznia", "Straty mocy [W]")

        self.setTabPosition(QTabWidget.North)
        self.addTab(self.wykres_sil, "Siły")
        self.addTab(self.wykres_naciskow, "Naciski")
        self.addTab(self.wykres_strat, "Straty")

    def update(self, data):
        if data["mode"] == "tolerances":
            if data.get("sily") and data["sily"] is not None:
                self.wykres_sil.update_data_tolerance(data["sily"])
            if data.get("naciski") and data["naciski"] is not None:
                self.wykres_naciskow.update_data_tolerance(data["naciski"])
            if data.get("straty") and data["straty"] is not None:
                self.wykres_strat.update_data_tolerance(data["straty"])
            return

        if data.get("sily") and data["sily"] is not None:
            self.wykres_sil.update_data(*graph_points(data["sily"][0], data["sily"][1]))
        if data.get("naciski") and data["naciski"] is not None:
            self.wykres_naciskow.update_data(*graph_points(data["naciski"][0], data["naciski"][1]))
        if data.get("straty") and data["straty"] is not None:
            self.wykres_strat.update_data(*graph_points(data["straty"][0], data["straty"][1]))


class ResultsTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.wykres_sil = Wykres("Siły na sworzniach", "numer sworznia", "Siła [N]")
        self.wykres_naciskow = Wykres("Naciski powierzchniowe na sworzniach", "numer sworznia", "Wartość Nacisku [MPa]")
        self.wykres_strat = Wykres("Straty mocy na sworzniach", "numer sworznia", "Straty mocy [W]")

        self.table = Table(self)

        self.graphs = ChartTabs(self)
        self.graphs.currentChanged.connect(self.table.changeTable)

        table_layout = QVBoxLayout()
        table_layout.addWidget(self.table)
        chart_layout = QVBoxLayout()
        chart_layout.addWidget(self.graphs)
        grid = QGridLayout()
        grid.addLayout(table_layout, 0, 0)
        grid.addLayout(chart_layout, 0, 1)
        self.setLayout(grid)

    def updateResults(self, data):
        self.table.update((data["sily"][0], data["naciski"][0], data["straty"][0]), self.graphs.currentIndex())
        self.graphs.update(data)
