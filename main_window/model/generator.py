from PySide2.QtWidgets import QMessageBox

from common.utils import open_save_dialog
from main_window.view.main_window import MainWindow

class Generator:
    def __init__(self, main_window: MainWindow):
        self._parent = main_window

    def generateRaport(self, data):        
        file_path = open_save_dialog(".rtf")
        if not file_path:
            return
        # file_name = "CycloRaport_" + datetime.datetime.today().strftime('%d-%m-%Y_%H-%M-%S') + ".rtf"
        try:
            with open(file_path, 'w') as f:
                f.write("{\\rtf1\\ansi\\deff0 {\\fonttbl {\\f0 Times New Roman;}}\\f0\\fs20")
                f.write("{\\pard\\qc\\b Raport \\line\\par}")
                f.write(data)
                f.write("}")
            QMessageBox.information(self._parent, 'Raport zapisany', 'Raport został utworzony.')
        except Exception as e:
            QMessageBox.critical(self._parent, 'Błąd', f'Wystąpił błąd podczas tworzenia raportu: {str(e)}')

    def generateCSV(self, data):
        file_path = open_save_dialog(".csv")
        if not file_path:
            return
        # file_name = "CycloWykresy_" + datetime.datetime.today().strftime('%d-%m-%Y_%H-%M-%S') + ".csv"
        try:
            with open(file_path, "w") as f:
                f.write(data)
            QMessageBox.information(self._parent, 'Tabele zapisane', 'Utworzono plik CSV z danymi.')
        except Exception as e:
            QMessageBox.critical(self._parent, 'Błąd', f'Wystąpił błąd podczas tworzenia pliku csv: {str(e)}')

    def generateDXF(self, data):
        file_path = open_save_dialog(".dxf")
        if not file_path:
            return
        # file_name = "CycloRysunek_" + datetime.datetime.today().strftime('%d-%m-%Y_%H-%M-%S') + ".dxf"
        try:
            with open(file_path, "w") as f:
                f.write("0\nSECTION\n2\nENTITIES\n0\nLWPOLYLINE\n39\n0.5\n")
                f.write(data)
                f.write("0\nENDSEC\n0\nEOF\r")
            QMessageBox.information(self._parent, 'Rysunek zapisany', 'Utworzono rysunek zarysu.')
        except Exception as e:
            QMessageBox.critical(self._parent, 'Błąd', f'Wystąpił błąd podczas tworzenia rysunku: {str(e)}')
