from typing import Callable, Tuple
from enum import Enum
from PySide2.QtGui import QFont, QResizeEvent
from PySide2.QtWidgets import QDoubleSpinBox, QLabel, QFrame, QSpinBox, QScrollArea, QWidget, QGridLayout, QPushButton

class DoubleSpinBox(QDoubleSpinBox):
    def __init__(self, value, minimum=None, maximum=None, step=0.01, decimal_places=2):
        super().__init__()
        self.modify(value, minimum, maximum)
        self.setSingleStep(step)
        self.setDecimals(decimal_places)
        if value is None:
            self.lineEdit().setText("")
    
    def wheelEvent(self, event):
        '''
        Overrides the default behaviour of changing the value on scrolling.
        Allows the event to instead be handled by the parent, resulting in scrolling the container.
        '''
        return False
    
    def hideEvent(self, event):
        value = self.value()
        super().hideEvent(event)
        if value is None:
            self.lineEdit().setText("")
    
    def showEvent(self, event):
        value = self.value()
        super().showEvent(event)
        if value is None:
            self.lineEdit().setText("")
    
    def focusOutEvent(self, event):
        value = self.value()
        super().focusOutEvent(event)
        if value is None:
            self.lineEdit().setText("")

    def value(self):
        return super().value() if self.lineEdit().text() != "" else None
    
    def modify(self, value=None, minimum=None, maximum=None):
        if minimum is not None:
            self.setMinimum(minimum)
        if maximum is not None:
            self.setMaximum(maximum)
        if value is not None:
            self.setValue(value)


class IntSpinBox(QSpinBox):
    def __init__(self, value, minimum=None, maximum=None, step=1):
        super().__init__()
        self.modify(value, minimum, maximum)
        self.setSingleStep(step)
        if value is None:
            self.lineEdit().setText("")
    
    def wheelEvent(self, event):
        '''
        Overrides the default behaviour of changing the value on scrolling.
        Allows the event to instead be handled by the parent, resulting in scrolling the container.
        '''
        return False
    
    def hideEvent(self, event):
        value = self.value()
        super().hideEvent(event)
        if value is None:
            self.lineEdit().setText("")
    
    def showEvent(self, event):
        value = self.value()
        super().showEvent(event)
        if value is None:
            self.lineEdit().setText("")
    
    def focusOutEvent(self, event):
        value = self.value()
        super().focusOutEvent(event)
        if value is None:
            self.lineEdit().setText("")

    def value(self):
        return super().value() if self.lineEdit().text() != "" else None
    
    def modify(self, value=None, minimum=None, maximum=None):
        if minimum is not None:
            self.setMinimum(minimum)
        if maximum is not None:
            self.setMaximum(maximum)
        if value is not None:
            self.setValue(value)


class PushButton(QPushButton):
    def __init__(self, *args, **kwargs):
        """
        Custom QPushButton that applies a custom font to the button text.

        This constructor allows flexible initialization by passing any combination
        of text and parent, while ensuring the custom font is applied.
        """
        super().__init__(*args, **kwargs)

        # Set a custom font for the button text
        custom_font = QFont('Arial', 9, QFont.Normal)
        self.setFont(custom_font)


class Label(QLabel):
    def __init__(self, *args, **kwargs):
        """
        Custom QLabel that applies a custom font to the label text.

        This constructor allows flexible initialization by passing any combination
        of text and parent, while ensuring the custom font is applied.
        """
        super().__init__(*args, **kwargs)

        # Set a custom font for the label text
        font = QFont('Arial', 10, QFont.Normal)
        self.setFont(font)


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


class StatusDiodes(QWidget):
    class Status(Enum):
        ERROR = 0
        WARNING = 1
        OK = 2
        DISABLED = 3
    
    def __init__(self, parent: QWidget, descriptions: Tuple[str, str, str, str]) -> None:
        super().__init__(parent)
        self.setFixedHeight(16)
        self.diodes = [QLabel(self), QLabel(self), QLabel(self)]
        self.descriptions = descriptions
        self.current_status = self.Status.DISABLED
        self.label = QLabel(descriptions[3])
        self.label.setFixedHeight(16)
        
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)
        for i, diode in enumerate(self.diodes):
            diode.setFixedSize(16, 16)
            diode.setStyleSheet(self.createDiodeStyle(self.Status.DISABLED))
            layout.addWidget(diode, 0, i)
        layout.addWidget(self.label, 0, 3, 1, 7)
    
    def createDiodeStyle(self, status):
        if status == self.Status.ERROR:
            color1, color2 = "#ff0000", "#a14646"
        elif status == self.Status.WARNING:
            color1, color2 = "#fff000", "#c3bb37"
        elif status == self.Status.OK:
            color1, color2 = "#3dec55", "#48b056"
        elif status == self.Status.DISABLED:
            color1, color2 = "#b1b1b1", "#b1b1b1"
        return f"border-radius: 8;background-color: qlineargradient(spread:pad, x1:0.145, y1:0.16, x2:1, y2:1, stop:0 {color1}, stop:1 {color2});"
    
    def enableDiode(self, status):
        # TODO: https://wiki.qt.io/Dynamic_Properties_and_Stylesheets
        for diode in self.diodes:
            diode.setStyleSheet(self.createDiodeStyle(self.Status.DISABLED))
        if status != self.Status.DISABLED:
            self.diodes[status.value].setStyleSheet(self.createDiodeStyle(status))
        self.label.setText(self.descriptions[status.value])
        self.current_status = status


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
        self.current_layout_style = "small"

        self.break_point = break_point
        self.ver_space = ver_space
        self.fn_below = fn_below
        self.fn_above = fn_above
        self.main_widget = widget
        self.setWidget(widget)

    def resizeEvent(self, arg__1: QResizeEvent) -> None:
        def clearLayout(layout: QGridLayout) -> None:
            # TODO: Nie moge usuwać wszystkich widżetów, bo mam je w modułach stworzone jako atrybuty i tylko zmieniam layout.
            # Ale usuwanie i ponowne tworzenie prostych widżetów których nie potrzebuje mieć zapisanych (jakieś label np.)
            # powoduje błędne umieszczenie ich w layoucie. Wygląda jakby w zasadzie wszystkie były na sobie ułożone. w innym layoucie.
            # Na ten moment po prostu zapisze te etykiety jak atrybuty klasy dataedit.
            # To się dzieje tylko jeśli jest aktywowany moduł.


            # attrs = list(self.main_widget.__dict__.values())
            # additional_attrs = []
            # for attr in attrs:
            #     if type(attr) == list:
            #         for el in attr: additional_attrs.append(el)
            #     elif type(attr) == dict:
            #         for el in attr.values(): additional_attrs.append(el)
            # for el in additional_attrs: attrs.append(el)
            
            while layout.itemAt(0):
                child = layout.takeAt(0)
                child.widget().hide()
                # if widget in attrs:
                #     widget.hide()
                # else:
                #     widget.deleteLater()                
        
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
        
        new_width = arg__1.size().width()
        new_height = arg__1.size().height()
        self.main_widget.setFixedWidth(new_width)
        
        if new_width > self.break_point and self.current_layout_style == "small":
            self.main_widget.setFixedHeight(new_height)
            self.current_layout_style = "big"
            setBigScreen()
        elif new_width < self.break_point and self.current_layout_style == "big":
            self.main_widget.setFixedHeight(self.ver_space)
            self.current_layout_style = "small"
            setSmallScreen()
        return super().resizeEvent(arg__1)
