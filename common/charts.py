from PySide2.QtWidgets import QTabWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QGridLayout, QAbstractItemView, QHeaderView, QWidget
from PySide2.QtGui import QPainter
from PySide2.QtCharts import QtCharts
from PySide2.QtCore import Qt


def graph_points(point_values, smooth_values):
    scatter_points = [[i, point_values[i - 1]] for i in range(1, len(point_values) + 1)]
    scale = len(point_values) / len(smooth_values)
    line_points = [[i * scale + 1, smooth_values[i]] for i in range(0, len(smooth_values))]
    return scatter_points, line_points


class Wykres(QtCharts.QChartView):
    def __init__(self, chart_title: str, x_title: str, y_title: str) -> None:
        super().__init__()
        self.chart = QtCharts.QChart()
        self.chart.setTitle(chart_title)
        self.setRenderHint(QPainter.Antialiasing)

        self.os_x = QtCharts.QValueAxis()
        self.os_x.setTitleText(x_title)
        self.os_x.setLabelFormat('%.0f')
        self.chart.addAxis(self.os_x, Qt.AlignBottom)

        self.os_y = QtCharts.QValueAxis()
        self.os_y.setTitleText(y_title)
        # TODO: moze zmieniac precyzje zaleznie czy sa tolerancje, albo zaleznie od tego co wyswietla wykres np luzy
        self.os_y.setLabelFormat('%.3f')
        self.chart.addAxis(self.os_y, Qt.AlignLeft)
        
        # self.os_y.setTickCount(1)
        self.series = {
            "line_series": QtCharts.QLineSeries(name="wartość średnia"),
            "point_series": QtCharts.QScatterSeries(),
            "tol_series_low": QtCharts.QLineSeries(name="minimalna wartość"),
            "tol_series_high": QtCharts.QLineSeries(name="maksymalna wartość"),
        }

        for series in self.series.values():
            self.chart.addSeries(series)
            series.attachAxis(self.os_x)
            series.attachAxis(self.os_y)
        
        self.series["point_series"].setColor("#529AB7")
        self.series["point_series"].setMarkerSize(15)
        self.chart.legend().markers(self.series["point_series"])[0].setVisible(False)
        self.chart.legend().hide()
        self.setChart(self.chart)
    
    def update_data_tolerance(self, value_lists):
        self.chart.legend().show()
        for series in self.series.values():
            series.clear()

        for i, wart in enumerate(value_lists[0], 1):
            self.series["line_series"].append(i, wart)
        for i, wart in enumerate(value_lists[1], 1):
            self.series["tol_series_low"].append(i, wart)
        for i, wart in enumerate(value_lists[2], 1):
            self.series["tol_series_high"].append(i, wart)
        
        self.os_x.setRange(1, len(value_lists[0]))
        self.os_y.setRange(min([i for i in value_lists[1]]), max([i for i in value_lists[2]]) * 1.05)
        self.chart.update()

    def update_data(self, point_values, smooth_values):
        self.chart.legend().hide()
        for series in self.series.values():
            series.clear()
        
        for value in smooth_values:
            self.series["line_series"].append(value[0], value[1])
        for value in point_values:
            self.series["point_series"].append(value[0], value[1])

        self.os_x.setRange(point_values[0][0], point_values[-1][0])
        self.os_y.setRange(min([i[1] for i in smooth_values]), max([i[1] for i in smooth_values]) * 1.05)
        self.chart.update()


class Table(QTableWidget):
    def __init__(self, parent, table_titles):
        super().__init__(parent)
        self.data = [[0] for _ in table_titles]
        self.table_titles = table_titles
        self.setHorizontalHeaderLabels((self.table_titles[0],))
        # self.verticalHeader().setVisible(False)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # self.setRowCount(6)
        self.setFixedWidth(90)
        self.setColumnCount(1)
        self.setColumnWidth(0, 70)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

    def update(self, new_data, open_tab):
        self.data = new_data
        self.changeTable(open_tab)

    def changeTable(self, open_tab):
        self.setHorizontalHeaderLabels((self.table_titles[open_tab],))
        self.setRowCount(len(self.data[open_tab]))
        for i, value in enumerate(self.data[open_tab]):
            # TODO: tutaj moze zmieniac tę precyzję
            self.setItem(i, 0, QTableWidgetItem("{:.4f}".format(value)))


class ChartTabs(QTabWidget):
    def __init__(self, parent, x_axis_title, chart_descriptions):
        super().__init__(parent)
        self.charts = {
            key: Wykres(value["chart_title"], x_axis_title, value["y_axis_title"]) for key, value in chart_descriptions.items()
        }

        self.setTabPosition(QTabWidget.North)
        for key, name in zip(self.charts, (chart_descriptions[key]["repr_name"] for key in chart_descriptions)):
            self.addTab(self.charts[key], name)

    def update(self, data):
        for key in self.charts:
            if len(data[key]) == 3:
                self.charts[key].update_data_tolerance(data[key])
            else:
                self.charts[key].update_data(*graph_points(*data[key]))
            # if data.get(key) and data[key] is not None:


class ResultsTab(QWidget):
    def __init__(self, parent, x_axis_title, chart_descriptions):
        super().__init__(parent)
        self.table = Table(self, [chart_descriptions[key]["repr_name"] for key in chart_descriptions])

        self.graphs = ChartTabs(self, x_axis_title, chart_descriptions)
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
        self.table.update([data[key][0] for key in data], self.graphs.currentIndex())
        self.graphs.update(data)
