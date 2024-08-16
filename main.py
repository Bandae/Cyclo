from PySide2.QtWidgets import QApplication
from main_window.main_window import MainWindow
import sys

# TODO: sprawdzic obliczenia tolerancje: T_ze: (0, 0,004), T_fi-ri: (-0,003, 0)
# TODO: dodać obrazki dwa nowe bmp do wyswietlania
# TODO: potestować zapisywanie i wczytywanie
# TODO: pozamieniać miejsca gdzie jest wybór z kilku stałych wartości na ENUM (jak np. typ obliczeń - tolerancja/odchylka/bez luzu)
# TODO: przenieść obliczenia z luzami do wątku i dodać jakieś powiadomienie, że są w trakcie

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
