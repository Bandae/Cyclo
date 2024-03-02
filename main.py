from PySide2.QtWidgets import QApplication
from mainwindow import MainWindow
import sys
# TODO: responsywność
# TODO: potestować zapisywanie i wczytywanie

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
