# Cyclo

![gif pokazujący działanie animacji](https://github.com/Bandae/Cyclo/assets/76438366/384c1b6e-6d84-4db4-86d4-43015b082037)

Program *cyclo* z interfejsem stworzonym dzięki bibliotece Qt wspomaga wykonywanie obliczeń wytrzymałościowych dla przekładni cykloidalnych. Może zostać użyty, aby wykonać pełny projekt przekładni spełniający wszystkie wymogi do danego zastosowania, a także dla ponownego obliczenia już istniejącej przekładni, biorąc pod uwagę potencjalne odchyłki wykonania elementów, również wynikające ze zużycia podczas eksploatacji. Dzięki programowi cały proces jest znacznie uproszczony i przystępny nawet dla początkujących projektantów.

Celem przy projektowaniu jest spełnienie wszystkich wymagań, a więc opisanie możliwego do wykonania zarysu cykloidalnego, spełnienie warunków wytrzymałościowych przy przenoszeniu narzuconego momentu wyjściowego, a także w dalszej kolejności optymalizacja przez np. dobór jak najbardziej opłacalnych materiałów.

![Ogólny widok aplikacji](https://github.com/Bandae/Cyclo/assets/76438366/3d838570-2a47-4721-bbb5-59da7ea3a0ca)

Tworzona przekładnia jest widoczna na ekranie i istnieje możliwość uruchomienia jej animacji. W lewym górnym rogu ekranu wyświetlane są błędy, wraz z informacjami o tym, jak się ich pozbyć. Dostępny jest pasek menu pozwalający na zapisanie i wczytanie stanu aplikacji, a także na wygenerowanie raportu do pliku tekstowego z wszystkimi informacjami o przekładni. Można też stworzyć plik .dxf z rysunkiem koła cykloidalnego. Pliki są tworzone w folderze z plikiem main. Po prawej stronie ekranu widoczne są przyciski do przełączania pomiędzy modułami aplikacji oraz aktywny moduł.

Projekt rozpoczyna się od wprowadzenia wymaganych od przekładni parametrów - momentu wyjściowego, prędkości obrotowej wejściowej, oraz przełożenia. Następnie używa się poszczególnych modułów aby zaprojektować kolejne części przekładni - zarys kół, mechanizm wyjściowy, mechanizm wejściowy.


## Moduł zarysu

![widok zakładki danych modułu zarysu](https://github.com/Bandae/Cyclo/assets/76438366/b4452ca6-78a6-4017-8158-d2448e62164d)

Koła cykloidalne w przekładni wykonują ruch planetarny, będący złożeniem toczenia się po rolkach, oraz obrotu z mimośrodem.
Moduł przyjmuje od użytkownika dane potrzebne do wyznaczenia zarysu, a także liczbę kół cykloidalnych w przekładni, szerokość kół i współczynniki tarcia. Dodatkowo podać należy materiał i obróbkę cieplną kół oraz rolek. Wraz z wprowadzaniem zmian, zaktualizuje się animacja oraz wyniki, w które wliczają się maksymalne wartości sił i nacisków, wykresy, oraz dane geometryczne koła cykloidalnego. Moduł sprawdza kilka warunków poprawnego wykonania zazębienia i informuje o ewentualnych błędach.

## Moduły mechanizmów wyjściowych

W przekładni można użyć jednego z kilku mechanizmów wyjściowych. W każdej z zakładek dostępna jest więc u samej góry opcja zaznaczenia danego mechanizmu, wyłączająca możliwość użycia pozostałych.

### Moduł mechanizmu wyjściowego z tulejami

![Widok zakładki wprowadzania danych modułu mechanizmu z tulejami](https://github.com/Bandae/Cyclo/assets/76438366/70a7e1f1-674c-406e-b353-5d675591f839)

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
