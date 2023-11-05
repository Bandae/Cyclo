from PySide6.QtWidgets import QWidget, QMainWindow
from typing import Union, Dict

# Typ danych przekazywanych miedzy zakladkami
# {
#     "pawel": {"nazwa_danej": dana, "nazwa_danej": dana, ...},
#     "wiktor": {...},
#     ...
# }
DaneZakladek = Dict[str, Dict[str, Union[int, float, str, dict, list]]]
DaneZapis = Dict[str, Union[int, float, str, dict, list]]

class AbstractTab(QWidget):
    '''Abstrakcyjna klasa do dziedziczenia przez każdą z naszych zakładek.'''
    def __init__(self, parent: QMainWindow) -> None:
        super().__init__(parent)
    
    def send_data(self) -> DaneZakladek:
        '''Wysyła potrzebne innym zakładkom dane w momencie zmiany zakładki z tej na inną.'''
        ...
    
    def receive_data(self, new_data: DaneZakladek) -> None:
        '''Przyjmuje i zapisuje dane przysłane przez inne zakładki przy zmianie zakładki.
        Powinna wywołać obliczenia jeśli konieczne.'''
        ...
    
    def save_data(self) -> DaneZapis:
        '''Wywoływana przed zapisem danych do pliku JSON. Powinna wykonać wszystkie wasze obliczenia,
        następnie ułożyć wszystkie wasze dane w słownik i zwrócić. Taki sam słownik dostaniecie po wczytaniu danych z pliku.'''
        ...
    
    def load_data(self, new_data: DaneZapis) -> None:
        '''Wywoływana po wczytaniu danych z pliku JSON.
        Powinna wczytać dane, wpisać je do waszych struktur danych i wywołać ewentualne obliczenia.'''
        ...
