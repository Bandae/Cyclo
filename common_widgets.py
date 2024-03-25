from typing import Callable

from PySide2.QtGui import QFont, QResizeEvent
from PySide2.QtWidgets import QDoubleSpinBox, QLabel, QFrame, QSpinBox, QScrollArea, QWidget, QGridLayout

class DoubleSpinBox(QDoubleSpinBox):
    def __init__(self, value, minimum, maximum, step, decimal_places=2):
        super().__init__()
        self.setRange(minimum, maximum)
        self.setValue(value)
        # self.lineEdit().setReadOnly(False)
        self.setSingleStep(step)
        self.setDecimals(decimal_places)
    
    def modify(self, value=None, minimum=None, maximum=None):
        if minimum is not None:
            self.setMinimum(minimum)
        if maximum is not None:
            self.setMaximum(maximum)
        if value is not None:
            self.setValue(value)


class IntSpinBox(QSpinBox):
    def __init__(self, value, minimum, maximum, step):
        super().__init__()
        self.setRange(minimum, maximum)
        self.setValue(value)
        # self.lineEdit().setReadOnly(False)
        self.setSingleStep(step)


class QLabelD(QLabel):
    def __init__(self, text='', font_size=9, style=True):
        super().__init__()
        self.setText(str(text))
        if style:
            self.setFrameStyle(QFrame.Box | QFrame.Raised)
        # self.setLineWidth(1)
        self.setWordWrap(True)
        self.setFont(QFont('Sans Serif', font_size))
        self.setStyleSheet("padding: 4px")


class ResponsiveContainer(QScrollArea):
    # TODO: teorytycznie by mógł być dowolny QLayout tutaj, ale jakoś nie widzę jak mogą być użyte żeby tworzyć kilka kolumn itd.
    def __init__(
            self, parent: QWidget, widget: QWidget,
            fn_below: Callable[[QGridLayout], None],
            fn_above: Callable[[QGridLayout], None],
            break_point: int, ver_space: int,
        ) -> None:
        """
        widget wypełni ScrollArea. Musi mieć ustawiony na sobie QGridLayout.
        fn_below to metoda tego widget'u, która umieszcza w jego układzie elementy w sposób czytelny dla mniejszych szerokości okna.
        fn_above umieszcza elementy tak, aby wykorzystać przestrzeń dostępną na większych ekranach.
        break_point: szerokość widgetu przy której następuje zmiana rozłożenia elementów
        ver_space: wysokość potrzebna na zmieszczenie wszystkich elementów na mniejszym ekranie
        """
        super().__init__(parent)
        self.setFrameStyle(QFrame.NoFrame)

        self.break_point = break_point
        self.ver_space = ver_space
        self.fn_below = fn_below
        self.fn_above = fn_above
        self.main_widget = widget
        self.setWidget(widget)

    def resizeEvent(self, arg__1: QResizeEvent) -> None:
        def clearLayout(layout: QGridLayout) -> None:
            while layout.itemAt(0):
                child = layout.takeAt(0)
                child.widget().hide()
        
        def showWidgets(layout: QGridLayout) -> None:
            for i in range(layout.count()):
                layout.itemAt(i).widget().show()

        def setSmallScreen():
            clearLayout(self.main_widget.layout())
            self.fn_below(self.main_widget.layout())
            showWidgets(self.main_widget.layout())
        
        def setBigScreen():
            clearLayout(self.main_widget.layout())
            self.fn_above(self.main_widget.layout())
            showWidgets(self.main_widget.layout())
        
        old_width = arg__1.oldSize().width()
        new_width = arg__1.size().width()
        new_height = arg__1.size().height()
        self.main_widget.setFixedWidth(new_width)
        if new_width > self.break_point and old_width < self.break_point:
            self.main_widget.setFixedHeight(new_height)
            setBigScreen()
        elif new_width < self.break_point and old_width > self.break_point:
            self.main_widget.setFixedHeight(self.ver_space)
            setSmallScreen()
        return super().resizeEvent(arg__1)