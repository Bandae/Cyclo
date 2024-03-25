from PySide2.QtWidgets import QApplication
from mainwindow import MainWindow
import sys
# TODO: responsywność - kiedy zmniejsze okno z otwartą zakładką jakąś, to nie odpala się mały ekran na innych, ale jak duży to już tak
# TODO: potestować zapisywanie i wczytywanie

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
