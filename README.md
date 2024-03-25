# Cyclo

![gif pokazujący działanie animacji](https://private-user-images.githubusercontent.com/76438366/316500340-1c12c842-4398-4455-b590-cd9cd250bb05.gif?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MTEzNzAzODUsIm5iZiI6MTcxMTM3MDA4NSwicGF0aCI6Ii83NjQzODM2Ni8zMTY1MDAzNDAtMWMxMmM4NDItNDM5OC00NDU1LWI1OTAtY2Q5Y2QyNTBiYjA1LmdpZj9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDAzMjUlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQwMzI1VDEyMzQ0NVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTQwYTI3ZDgwYTM4NjAyYWVkMGJjYmY5NTM2MDc0Mzk3MTgyYmMzYjA5YmQyZmI5NTE2MGY4NjQ2NmEyMWU1NDEmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JmFjdG9yX2lkPTAma2V5X2lkPTAmcmVwb19pZD0wIn0.qb2YxnLeexI-WxIQ6htdN7FxVLWwxsSgExhIWYksqxg)

Program *cyclo* z interfejsem stworzonym dzięki bibliotece Qt wspomaga wykonywanie obliczeń wytrzymałościowych dla przekładni cykloidalnych. Może zostać użyty, aby wykonać pełny projekt przekładni spełniający wszystkie wymogi do danego zastosowania, a także dla ponownego obliczenia już istniejącej przekładni, biorąc pod uwagę potencjalne odchyłki wykonania elementów, również wynikające ze zużycia podczas eksploatacji. Dzięki programowi cały proces jest znacznie uproszczony i przystępny nawet dla początkujących projektantów.

Celem przy projektowaniu jest spełnienie wszystkich wymagań, a więc opisanie możliwego do wykonania zarysu cykloidalnego, spełnienie warunków wytrzymałościowych przy przenoszeniu narzuconego momentu wyjściowego, a także w dalszej kolejności optymalizacja przez np. dobór jak najbardziej opłacalnych materiałów.

![Ogólny widok aplikacji](https://private-user-images.githubusercontent.com/76438366/316500794-f4fb6f5d-b331-4722-b89e-da3c7e48436d.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MTEzNzA0NzIsIm5iZiI6MTcxMTM3MDE3MiwicGF0aCI6Ii83NjQzODM2Ni8zMTY1MDA3OTQtZjRmYjZmNWQtYjMzMS00NzIyLWI4OWUtZGEzYzdlNDg0MzZkLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDAzMjUlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQwMzI1VDEyMzYxMlomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTYxZGJkZmFlNWE2NmQ1OTA2ODE0OTEyOTBkMDhkYTcwNjc4YWVlODk2MTliNTkzNTIxMjQ2YmVhMjRjMmRkMTAmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JmFjdG9yX2lkPTAma2V5X2lkPTAmcmVwb19pZD0wIn0.eIpp_GKU-F5idw9OwBNVXDrnc_4iXKWa60Bb7ZUuyJk)

Tworzona przekładnia jest widoczna na ekranie i istnieje możliwość uruchomienia jej animacji. W lewym górnym rogu ekranu wyświetlane są błędy, wraz z informacjami o tym, jak się ich pozbyć. Dostępny jest pasek menu pozwalający na zapisanie i wczytanie stanu aplikacji, a także na wygenerowanie raportu do pliku tekstowego z wszystkimi informacjami o przekładni. Można też stworzyć plik .dxf z rysunkiem koła cykloidalnego. Pliki są tworzone w folderze z plikiem main. Po prawej stronie ekranu widoczne są przyciski do przełączania pomiędzy modułami aplikacji oraz aktywny moduł.

Projekt rozpoczyna się od wprowadzenia wymaganych od przekładni parametrów - momentu wyjściowego, prędkości obrotowej wejściowej, oraz przełożenia. Następnie używa się poszczególnych modułów aby zaprojektować kolejne części przekładni - zarys kół, mechanizm wyjściowy, mechanizm wejściowy.


## Moduł zarysu

![widok zakładki danych modułu zarysu](https://private-user-images.githubusercontent.com/76438366/316500762-fac454ee-ce6f-4548-b4dd-ee78f40ac52c.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MTEzNzA0NzIsIm5iZiI6MTcxMTM3MDE3MiwicGF0aCI6Ii83NjQzODM2Ni8zMTY1MDA3NjItZmFjNDU0ZWUtY2U2Zi00NTQ4LWI0ZGQtZWU3OGY0MGFjNTJjLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDAzMjUlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQwMzI1VDEyMzYxMlomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTdmMjc2ZmJjZWMxNzQ3ODRlNjNmYTI1ZjkwNDFkNDM5MzU0MDkxYTQ5ZDE2ODAzMzlmYjRiMTgyYTg2YWMzMGYmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JmFjdG9yX2lkPTAma2V5X2lkPTAmcmVwb19pZD0wIn0.O5rDxp-vcj6Ol0z5PWqoHoBlPhDSScAtMj-U7nWmfhI)

Koła cykloidalne w przekładni wykonują ruch planetarny, będący złożeniem toczenia się po rolkach, oraz obrotu z mimośrodem.
Moduł przyjmuje od użytkownika dane potrzebne do wyznaczenia zarysu, a także liczbę kół cykloidalnych w przekładni, szerokość kół i współczynniki tarcia. Dodatkowo podać należy materiał i obróbkę cieplną kół oraz rolek. Wraz z wprowadzaniem zmian, zaktualizuje się animacja oraz wyniki, w które wliczają się maksymalne wartości sił i nacisków, wykresy, oraz dane geometryczne koła cykloidalnego. Moduł sprawdza kilka warunków poprawnego wykonania zazębienia i informuje o ewentualnych błędach.

## Moduły mechanizmów wyjściowych

W przekładni można użyć jednego z kilku mechanizmów wyjściowych. W każdej z zakładek dostępna jest więc u samej góry opcja zaznaczenia danego mechanizmu, wyłączająca możliwość użycia pozostałych.

### Moduł mechanizmu wyjściowego z tulejami

![Widok zakładki wprowadzania danych modułu mechanizmu z tulejami](https://private-user-images.githubusercontent.com/76438366/316500775-78045581-eb88-432d-9a65-232695822516.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MTEzNzA0NzIsIm5iZiI6MTcxMTM3MDE3MiwicGF0aCI6Ii83NjQzODM2Ni8zMTY1MDA3NzUtNzgwNDU1ODEtZWI4OC00MzJkLTlhNjUtMjMyNjk1ODIyNTE2LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDAzMjUlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQwMzI1VDEyMzYxMlomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTE0M2NjY2FkNjQ4YWMzZWQ4YTBlYjYyYWM4NTBkZjgwY2QzOGUzMzRlZGE4NjUxYzM2ZDNlY2YyOGE2YzUyYjYmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JmFjdG9yX2lkPTAma2V5X2lkPTAmcmVwb19pZD0wIn0.kTRWvV3nBLhUn_EahZ1khYK4Lx4TywvGyYer0mBu0Yw)

Zadaniem mechanizmu wyjściowego jest zamiana ruchu planetarnego koła cykloidalnego na ruch obrotowy elementu wyjściowego. W mechanizmie z tulejami koło cykloidalne ma otwory przez które oddziałuje na tuleje, które są osadzone na sworzniach będąch częścią elementu wyjściowego.
Moduł przyjmuje od użytkownika kilka parametrów mechanizmu i oblicza średnicę sworzni wymaganą by przenieść obciążenie.

- Liczba sworzni - Obciążenie rozkłada się na poszczególne sworznie, więc większa ich ilość pozwala przenieść ten sam moment z mniejszymi średnicami sworzni lub mniej wytrzymałym na zginanie materiałem. Otwory dla zbyt dużej ilości sworzni przetną się jednak ze sobą uniemożliwiając wykonanie.

- Promień rozmieszczenia sworzni - Im większy, tym mniejsze mogą być średnice sworzni. Zbyt duży spowoduje jednak, że otwory nie zmieszczą się na kole.

- Sposób mocowania sworzni - wybierany w oddzielnym oknie wyskakującym po wciśnięciu przycisku. Sposoby wykorzystujące śruby znacznie zmniejszają obciążenie sworzni, ale wymagają bardziej skomplikowanej konstrukcji przekładni, większej dokładności wykonania itd.

- Odstępy pomiędzy kołami oraz kołem a tarczą - ustawiane zależnie od wymagań konstrukcyjnych danej przekładni. Większe oznaczają nieznacznie większe obciążenie sworzni.

- Wybór materiałów - dla sworznia wybiera się materiał oraz współczynnik bezpieczeństwa konieczne do wyznaczenia średnicy. Dla tulei wybiera się materiał oraz ewentualnie obróbkę cieplną, które wraz z materiałem koła wprowadzonym w zakładce zarysu pozwalają określić naciski dopuszczalne.

- Współczynniki tarcia - wpływają na straty mocy.

Po wprowadzeniu powyższych danych należy wcisnąć przycisk "oblicz". Animacja oraz wykresy zostaną zaktualizowane. Poniżej wyświetlane są obliczone średnice sworzni, tulei oraz otworów w mechanizmie. Można je ręcznie zwiększyć, aby np. osiągnąć pełne wartości. Wyświetlane obok wyniki zawierają maksymalną siłę oraz nacisk powierzchniowy w mechanizmie, a także sumę strat mocy. Dodatkowo w podzakładce wyniki można zobaczyć wykresy obrazujące rozkład sił, nacisków oraz strat na poszczególnych sworzniach.

## Moduł mechanizmu wejściowego

*W trakcie tworzenia...*

## Dodatkowe

Więcej informacji o poszczególnych modułach można znaleźć w plikach .pdf w folderze **help**
