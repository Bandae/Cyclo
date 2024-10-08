from typing import Union, Dict

DaneZakladek = Dict[str, Dict[str, Union[int, float, str, dict, list]]]
DaneZapis = Dict[str, Union[int, float, str, dict, list]]

# Typ danych przekazywanych miedzy zakladkami
# {
#     "GearTab": {"nazwa_danej": dana, "nazwa_danej": dana, ...},
#     "PinOutTab": {...},
#     ...
# }

class ITabController:    
    def sendData(self) -> None:
        '''
        Wysyła potrzebne innym zakładkom dane w momencie zmiany zakładki z tej na inną.
        '''
        ...
    
    def receiveData(self, new_data: DaneZakladek) -> None:
        '''
        Przyjmuje i zapisuje dane przysłane przez inne zakładki przy zmianie zakładki.
        Powinna wywołać obliczenia jeśli konieczne.
        '''
        ...
    
    def saveData(self) -> DaneZapis:
        '''
        Wywoływana przed zapisem danych do pliku JSON. Powinna wykonać wszystkie wasze obliczenia,
        następnie ułożyć wszystkie wasze dane w słownik i zwrócić. Taki sam słownik dostaniecie po wczytaniu danych z pliku.
        '''
        ...
    
    def loadData(self, new_data: DaneZapis) -> None:
        '''
        Wywoływana po wczytaniu danych z pliku JSON.
        Powinna wczytać dane, wpisać je do waszych struktur danych i wywołać ewentualne obliczenia.
        '''
        ...

    def csvData(self) -> str:
        '''
        Zwraca dane zakładki konieczne do eksportu, sformatowane już do zapisu w CSV.
        '''
        return ''

    def reportData(self) -> str:
        '''
        Zwraca dane zakładki konieczne do raportu, sformatowane już do zapisu w rtf.
        '''
        return ''
    