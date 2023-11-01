from PySide6.QtWidgets import QWidget, QMainWindow
from typing import Union, Dict

# Typ danych przekazywanych miedzy zakladkami.
# {
#     "pawel": {"nazwa_danej": dana, "nazwa_danej": dana, ...},
#     "wiktor": {...},
#     ...
# }
DaneZakladek = Dict[str, Dict[str, Union[int, float, str, dict]]]

class AbstractTab(QWidget):
    '''Abstrakcyjna klasa do dziedziczenia przez każdą z naszych zakładek.'''
    def __init__(self, parent: QMainWindow) -> None:
        super().__init__(parent)
    
    def send_data(self) -> DaneZakladek:
        '''Metoda wysyłająca potrzebne innym zakładkom dane w momencie zmiany zakładki z tej na inną.'''
        ...
    
    def receive_data(self, new_data: DaneZakladek) -> None:
        '''Metoda przyjmująca i zapisująca dane przysłane przez inne zakładki przy zmianie zakładki.'''
        ...
