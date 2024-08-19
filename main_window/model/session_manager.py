
import json
from PySide2.QtWidgets import QFileDialog, QMessageBox

from common.utils import open_save_dialog
from main_window.view.main_window import MainWindow

class SessionManager:
    def __init__(self, main_window: MainWindow):
        self._parent = main_window
        self._loaded_file = None

    def loadJSON(self):
        '''
        Wczytuje dane z pliku .json, wywołuje metodę loadData() każdej z zakładek, podając im słownik jej danych.
        Może być None, każdy musi z osobna sprawdzić przed odczytywaniem pojedynczych pozycji.
        '''
        data = None
        file_path = None
        file_dialog = QFileDialog(self._parent)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setWindowTitle("Wczytywanie danych")
        file_dialog.setNameFilter('JSON Files (*.json)')

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                QMessageBox.information(self._parent, 'Dane wczytane', 'Dane zostały wczytane.')

                self._loaded_file = file_path

            except Exception as e:
                QMessageBox.critical(self._parent, 'Błąd', f'Wystąpił błąd przy wczytywaniu pliku: {str(e)}')
        
        return data
        
    def saveToJSON(self, data, mode="save"):
        '''
        Zapis do pliku JSON. Wywołuje na każdej zakładce metodę saveData(), zbiera zwrócone przez nie dane i zapisuje jako obiekty,
        których klucze są takie same, jak self.tab_titles.
        Wywołuje activateTab(), żeby upewnić się, że przekazane są między nami dane, i wykonane obliczenia przed zapisem.

        Użycie tej metody, albo loadJSON(), zapisuje podaną przez użytkownika ścieżkę, i kolejne wywołania tej metody automatycznie zapisują do tego pliku.
        '''
        def save_ess(f_path, dane):
            try:
                with open(f_path, 'w') as f:
                    json.dump(dane, f)
                QMessageBox.information(self._parent, 'Plik zapisany', 'Dane zostały zapisane do pliku JSON.')
                self._loaded_file = f_path
            except Exception as e:
                QMessageBox.critical(self._parent, 'Błąd', f'Wystąpił błąd podczas zapisu do pliku: {str(e)}')

        if self._loaded_file is not None and mode != "save as":
            save_ess(self._loaded_file, data)
            return
            
        file_path = open_save_dialog(".json")
        if file_path:
            save_ess(file_path, data)
