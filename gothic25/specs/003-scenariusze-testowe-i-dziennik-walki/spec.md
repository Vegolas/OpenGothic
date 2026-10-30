# 003: Scenariusze testowe i dziennik walki

- **Status:** W realizacji
- **Utworzono:** 2026-10-29
- **Warstwa (wstępnie):** silnik i narzędzia <!-- zasoby / skrypty / silnik -->

- **Powiązane:** [001: Combosy NPC w walce wręcz](../001-combosy-npc-w-walce-wrecz/spec.md)
  (weryfikacja Z15 czeka na tę funkcję), [002: Skalowanie obrażeń w kombo](../002-skalowanie-obrazen-w-kombo/spec.md)
  (kryteria liczbowe), konstytucja, zasada 5 (zob. P5).

## Problem

Każde kryterium akceptacji trzeba dziś przygotować ręcznie: nowa gra, konsola, `cheat god`,
rozmowa z `ch` po talent i punkty nauki, przedmioty, `insert` przeciwnika, przejście w spokojne
miejsce. Przy specyfikacji 001 to kilkanaście takich przygotowań, więc testy w grze kończą się
ogólnym „działa” zamiast przejścia kroków.

Do tego większość kryteriów walki to liczenie na oko: ile ciosów miało combo, jakie serie wykonał
NPC w ciągu 2 minut, czy seria urwała się po bloku. Takie obserwacje są męczące, łatwo się pomylić,
a kryteria liczbowe (obrażenia kolejnych ciosów combo w 002) są na oko niesprawdzalne.

Claude, który pisze kod, nie widzi gry. Może sprawdzić tylko to, co da się zbudować i odczytać
z plików, więc każde kryterium w grze wraca do właściciela projektu.

## Cel

Przebieg testu opisujemy raz, w pliku w repozytorium. Jedno polecenie uruchamia grę, sama
przygotowuje sytuację z kryterium i zapisuje dziennik walki. Z dziennika powstaje raport, który
czyta człowiek albo Claude. Właściciel projektu ogląda tylko to, czego nie da się odczytać z liczb.

## Poza zakresem

- Sterowanie bohaterem jak przez gracza: symulowanie klawiszy, nagrywanie i odtwarzanie wejścia.
  Bohater w scenariuszu tylko stoi, przenosi się albo działa przez funkcje skryptów.
- Uruchamianie gry bez okna i testy w CI.
- Nagrywanie wideo.
- Osobny świat testowy. Scenariusze korzystają ze światów gry i ich waypointów.
- Automatyczna ocena wyglądu: płynność animacji, przeskoki, kolizje. To zostaje dla człowieka.
- Dziennik systemów innych niż walka wręcz: walki dystansowej, magii, dialogów, planów dnia, handlu.
  Dystans i magię dopiszemy razem z funkcją, która będzie ich potrzebować.
- Jakakolwiek zmiana gry dla gracza, który nie uruchamia jej w trybie deweloperskim.

## Scenariusze gracza

„Gracz” to tutaj osoba, która testuje moda: właściciel projektu albo Claude.

1. **Gdy** właściciel projektu chce zobaczyć combo paladyna z 001 K1, **wtedy** uruchamia jedno
   polecenie ze scenariuszem tego kryterium. Gra startuje od razu w świecie, bez menu. Bohater jest
   nieśmiertelny, ma talent i miecz z kroków kryterium i stoi w spokojnym miejscu, a paladyn stoi
   obok i go atakuje. Właściciel tylko patrzy.
2. **Gdy** Claude sprawdza 001 K2, **wtedy** uruchamia scenariusz w trybie automatycznym. Gra
   przyspiesza czas, po zadanym czasie zamyka się sama, a Claude dostaje raport: jakie serie
   i jak długie combo wykonał każdy NPC.
3. **Gdy** trzeba sprawdzić grę bez moda (001 K8), **wtedy** ten sam scenariusz uruchamia się
   na tej samej kompilacji silnika bez moda, a raporty obu przebiegów da się porównać.
4. **Gdy** trzeba sprawdzić zapis w trakcie walki (001 K9), **wtedy** jeden scenariusz zapisuje grę
   w środku walki, a drugi wczytuje ten zapis i obserwuje dalszą walkę.
5. **Gdy** właściciel projektu gra bohaterem w scenariuszu dla 002, **wtedy** raport pokazuje
   obrażenia każdego jego ciosu razem z etapem combo, więc premie da się sprawdzić z liczb.
6. **Gdy** Claude chce sprawdzić, czy przygotowanie się udało, **wtedy** ogląda zrzuty ekranu
   zrobione przez scenariusz w zadanych chwilach.

## Wymagania

- **W1:** Scenariusz to plik tekstowy w repozytorium moda z listą poleceń wykonywanych po kolei,
  gdy świat jest już wczytany (nowa gra albo wczytany zapis). Polecenia to komendy konsoli
  deweloperskiej (te same, które wpisuje się po `F2`). Dochodzą do tego polecenia sterujące
  przebiegiem:
  - czekanie przez zadany czas gry (przyspieszenie czasu skraca scenariusz),
  - czekanie na zdarzenie z walki wskazanej postaci: początek serii, n-ty cios serii albo combo
    do przodu, upadek, utrata przytomności, śmierć. Każde takie czekanie ma limit czasu gry,
    po którym scenariusz zgłasza błąd (W7),
  - zakończenie gry.

  Plik może zawierać komentarze i puste linie.
- **W2:** Scenariusz uruchamia się jednym poleceniem z narzędzi moda. Można w nim wybrać:
  - z modem albo bez moda (oryginalna gra na tej samej kompilacji silnika),
  - nową grę albo wczytanie wskazanego zapisu,
  - tryb automatyczny (gra kończy się po scenariuszu, polecenie wypisuje raport) albo ręczny
    (po scenariuszu gra zostaje otwarta i można grać dalej).

  Gra startuje od razu w świecie, bez menu i bez filmów. Polecenie czeka na zamknięcie gry
  i podaje, gdzie leżą wyniki.

  Przed uruchomieniem z modem polecenie samo pakuje moda z bieżących plików repozytorium, także
  niezacommitowanych. Gra wczytuje go z katalogu roboczego repozytorium, bez instalacji. Folder gry
  pozostaje nietknięty, a zainstalowany tam mod (jeśli jest) nie bierze udziału w teście.

  W trybie automatycznym gra działa w małym oknie (800×600) z dźwiękiem, żeby dało się dalej
  pracować przy komputerze. Tryb ręczny używa zwykłych ustawień gry. Ustawienia z testu nie
  przechodzą do zwykłej gry: po teście gra uruchamia się z takimi ustawieniami jak przed nim.

  Zapisy gry z przebiegów scenariuszy leżą osobno i nigdy nie nadpisują zapisów ze zwykłej gry.
  Do wczytania przy starcie można wskazać dowolny plik zapisu: zapis z testu, zapis ze zwykłej gry
  albo zapis odłożony do testów (np. zapis z 0.1.0 do 001 K9).
- **W3:** Konsola deweloperska dostaje nowe polecenia, dostępne ręcznie i w scenariuszach:
  - wywołanie funkcji ze skryptów gry z argumentami: liczbami, nazwami stałych ze skryptów,
    tekstami i postaciami. Postać wskazuje się jako bohatera albo nazwą instancji. Gdy scenariusz
    wstawił kilka postaci tej samej instancji, chodzi o ostatnio wstawioną. Wynik albo błąd widać
    w konsoli. Przykład: podniesienie talentu bohatera albo rozkaz ataku NPC na bohatera.
    Funkcji zewnętrznych silnika (np. tworzenie przedmiotów) nie da się tak wywołać, więc:
  - dodanie przedmiotu do ekwipunku bohatera i założenie go (broń, pancerz),
  - oznaczenie kwestii dialogowej jako już przegadanej z bohaterem, żeby ważny dialog
    (np. powitanie Xardasa na początku nowej gry) nie zaczepiał bohatera w teście,
  - nieśmiertelność wskazanej postaci, żeby walka NPC z NPC trwała tyle, ile potrzebuje test,
  - usunięcie ze świata postaci wskazanej instancji w pobliżu bohatera, żeby potwory z okolicy
    miejsca testu nie dołączały do walki (dopisane 2026-10-30),
  - zapis gry do wskazanego slotu, tak samo jak z menu,
  - zrzut ekranu do pliku PNG, bez okna konsoli na obrazie,
  - zakończenie gry.
- **W4:** W trybie deweloperskim gra może prowadzić dziennik walki wręcz. W przebiegach scenariuszy
  dziennik jest zawsze włączony. W zwykłej grze deweloperskiej jest domyślnie wyłączony, a włącza
  go i wyłącza polecenie konsoli. Taki dziennik trafia do katalogu wyników jak przebieg scenariusza
  (W6), a raport z niego robi to samo narzędzie (W5). Dziennik zapisuje każdy cios bronią białą
  albo pięścią każdej postaci, NPC i bohatera:
  - czas, kto atakuje i kogo (instancja i imię), styl walki, broń i talent,
  - rodzaj ciosu (do przodu, w lewo, w prawo) i który to cios combo do przodu,
  - czy cios należy do serii, jakiej i który to jej cios,
  - moment połączenia z poprzednim ciosem: kiedy w oknie combo i ile animacji poprzedniego ciosu
    pominięto,
  - wynik: trafienie, blok, unik albo pudło, oraz zadane obrażenia,
  - przerwanie serii albo combo z przyczyną: blok, zachwianie, przeciwnik leży, przeciwnik poza
    zasięgiem, obrona w trakcie serii, koniec talentu.

  Dziennik zapisuje też upadki, utratę przytomności i śmierć uczestników walki.
- **W5:** Raport z dziennika podsumowuje każdą postać: liczbę ciosów, serie według rodzaju,
  rozkład długości combo do przodu i najdłuższe combo, moment połączenia (najwcześniejszy,
  średni, najpóźniejszy), przerwania według przyczyny i obrażenia według etapu combo. Raport jest
  tekstem czytelnym dla człowieka. Dziennik ma postać, z której raport i inne narzędzia
  odczytują dane bez zgadywania (jedno zdarzenie w linii, stałe pola).
- **W6:** Każdy przebieg zapisuje wyniki (dziennik, raport, zrzuty ekranu, log gry, użyty scenariusz)
  w osobnym katalogu z nazwą scenariusza i czasem. Katalog leży poza folderem gry i poza gitem,
  a kolejne przebiegi nie nadpisują poprzednich.
- **W7:** Błąd w scenariuszu (nieznane polecenie, instancja, funkcja, waypoint, zły argument) trafia
  do wyników z numerem linii. W trybie automatycznym przerywa scenariusz i kończy grę, a polecenie
  zgłasza niepowodzenie. Tryb automatyczny ma limit czasu: gdy gra się nie zakończy, polecenie ją
  zamyka i zgłasza niepowodzenie.
- **W8:** Bez trybu deweloperskiego gra działa tak jak dotąd: nie ma nowych poleceń, dziennika
  ani scenariuszy. Narzędzia działają także bez moda Gothic 2.5. Włączony dziennik nie zmienia
  przebiegu gry.
- **W9:** Repozytorium zawiera scenariusze dla tych kryteriów 001, które da się przygotować
  automatycznie, oraz krótką instrukcję: jak napisać scenariusz, jak go uruchomić i jak czytać
  raport. Proces weryfikacji (`/g25-verify`) mówi, kiedy z nich korzystać.
- **W10:** Kryterium akceptacji, które da się ocenić z raportu (serie, długości combo, przerwania,
  obrażenia), może zaliczyć automatyczny przebieg scenariusza, także uruchomiony przez Claude.
  Wpis w sekcji „Weryfikacja” podaje wtedy scenariusz, wersję albo commit i liczby z raportu, które
  rozstrzygają kryterium, bo katalog wyników nie trafia do gita. Kryteria wizualne (płynność
  animacji, wygląd) zalicza tylko człowiek. Zasadę 5 konstytucji doprecyzowuje w tym duchu
  osobny ADR.
- **W11:** Claude może uruchamiać scenariusze w trybie automatycznym bez pytania o zgodę za każdym
  razem, bo nie zmieniają one folderu gry i same się kończą. Tryb ręczny, instalacja moda w folderze
  gry i zwykłe uruchomienie gry nadal wymagają zgody właściciela projektu. Zasada trafia
  do instrukcji dla Claude razem z tą funkcją, nie wcześniej.
- **W12:** Scenariusz może zawierać oczekiwane wyniki dotyczące danych z raportu, np. „najdłuższe
  combo do przodu `BDT_1071_Addon_Ramon` ≤ 3” albo „`Pal_230_Ritter`: seria mistrzowska ≥ 1”.
  Raport podaje dla każdego oczekiwania „zaliczone” albo „niezaliczone” z wartością faktyczną
  oraz wynik całego przebiegu, a polecenie zgłasza niepowodzenie, gdy któreś oczekiwanie nie jest
  spełnione. Wszystkie scenariusze jednej specyfikacji da się uruchomić jednym poleceniem
  z podsumowaniem wyników, żeby powtarzać je po każdej zmianie. Scenariusze dla 001 (W9) mają
  oczekiwania dobrane tak, żeby przy poprawnym działaniu nie zawodziły przypadkiem.

## Kryteria akceptacji

Wspólne przygotowanie (P0): silnik zbudowany z bieżącej wersji repozytorium. Moda nie trzeba
budować ani instalować (W2).

- [ ] **K1** (W1, W2, W3): Tryb ręczny przygotowuje sytuację bez dotykania klawiatury.
  - Kroki: P0, uruchom scenariusz dla 001 K1 w trybie ręcznym.
  - Oczekiwane: gra startuje bez menu i bez filmów. Bez żadnego wejścia od gracza bohater stoi
    w miejscu ze scenariusza, jest nieśmiertelny (`cheat god`), ma talent jednoręczny 80% i miecz
    paladyna w ręku (sprawdź w ekranie postaci i ekwipunku), a obok stoi `Pal_230_Ritter`
    i go atakuje. Gra zostaje otwarta.
- [ ] **K2** (W1, W2, W4, W5, W6): Tryb automatyczny daje raport.
  - Kroki: P0, zanotuj daty modyfikacji plików w folderach `Data\ModVDF` i `System` gry. Zmień
    w repozytorium dowolny komentarz w skryptach walki bez commita. Uruchom w trybie automatycznym
    scenariusz dla 001 K2 (dwaj NPC z bronią dwuręczną, przyspieszony czas).
  - Oczekiwane: polecenie spakowało moda ze zmienionych plików. Gra działa w małym oknie
    z dźwiękiem i zamyka się sama po czasie ze scenariusza. W nowym katalogu wyników są dziennik,
    raport, log gry i kopia scenariusza. Raport podaje dla obu NPC liczbę ciosów, serie według
    rodzaju i rozkład długości combo do przodu. Daty modyfikacji plików w folderze gry się
    nie zmieniły, a gra uruchomiona potem zwykłym `tools/run.ps1` ma rozdzielczość i tryb okna
    sprzed testu.
- [ ] **K3** (W4, W5): Raport zgadza się z tym, co widać na ekranie.
  - Kroki: P0, uruchom scenariusz dla 001 K1 w trybie ręcznym, wpisz `ztimer multiplyer 0.3`
    i przez ok. 3 minuty czasu gry notuj każdą serię i każde combo paladyna oraz każdy własny blok
    i trafienie. Zamknij grę i otwórz raport z tego przebiegu.
  - Oczekiwane: liczba serii każdego rodzaju, długości combo, bloki i trafienia z raportu zgadzają się
    z notatkami (dopuszczalna różnica: jedna seria na samym początku albo końcu obserwacji).
- [ ] **K4** (W2, W8): Ten sam scenariusz działa bez moda.
  - Kroki: P0, uruchom scenariusz dla 001 K1 w trybie automatycznym bez moda.
  - Oczekiwane: scenariusz przechodzi bez błędów, a raport opisuje walkę paladyna (jego ciosy,
    bloki i trafienia). Wyniki leżą w osobnym katalogu i nie mieszają się z przebiegiem z modem.
- [ ] **K5** (W3): Wywołanie funkcji skryptu z konsoli.
  - Kroki: P0, nowa gra w trybie deweloperskim, `F2`. Wywołaj funkcję podnoszącą talent bohatera
    w broni jednoręcznej o 50 punktów, podając talent nazwą stałej ze skryptów. Potem wstaw
    `Pal_230_Ritter` i wywołaj funkcję ataku z paladynem jako atakującym i bohaterem jako celem.
    Na koniec wywołaj funkcję z błędną nazwą i z brakującym argumentem.
  - Oczekiwane: talent w ekranie postaci rośnie o 50 punktów, paladyn atakuje bohatera. Błędna
    nazwa i brakujący argument dają czytelny komunikat w konsoli, a gra działa dalej.
- [ ] **K6** (W1, W2, W3): Zapis w środku serii i jego wczytanie.
  - Kroki: P0, zanotuj daty modyfikacji zapisów ze zwykłej gry. Uruchom scenariusz, który czeka,
    aż paladyn wyprowadzi drugi cios serii, wtedy zapisuje grę do slotu 1 i kończy grę. Potem
    uruchom scenariusz, który wczytuje ten zapis, czeka 30 s czasu gry i kończy grę. Na koniec
    uruchom dowolny scenariusz w trybie ręcznym i wczytaj ten zapis z menu gry.
  - Oczekiwane: dziennik pierwszego przebiegu pokazuje zapis po drugim ciosie serii, przed jej
    końcem. Zapis widać w menu z miniaturą jak każdy inny. Raport drugiego przebiegu pokazuje dalszą
    walkę paladyna. Ręczne wczytanie z menu działa. Zapisy ze zwykłej gry, także slot 1, mają
    te same daty modyfikacji co przed testem.
- [ ] **K7** (W3, W6): Zrzuty ekranu.
  - Kroki: P0, uruchom scenariusz, który robi zrzut ekranu tuż po wstawieniu paladyna i drugi
    10 s później, z otwartą wcześniej konsolą.
  - Oczekiwane: w katalogu wyników są dwa pliki PNG w rozdzielczości gry. Widać na nich bohatera
    i paladyna, a nie widać konsoli.
- [ ] **K8** (W7): Błędy i limit czasu.
  - Kroki: P0, uruchom w trybie automatycznym scenariusz z literówką w nazwie instancji w trzeciej
    linii. Potem scenariusz, który czeka na serię tchórza `BDT_1013_Bandit_L` (tchórz nie wykonuje
    serii) z limitem 30 s. Na koniec scenariusz, który czeka dłużej niż limit czasu całego przebiegu.
  - Oczekiwane: pierwszy przebieg kończy się zaraz po błędzie, a wyniki i polecenie wskazują
    trzecią linię i nieznaną nazwę. Drugi kończy się po 30 s czasu gry z błędem czekania
    na zdarzenie. Trzeci kończy się po limicie czasu przebiegu. W każdym przypadku polecenie
    zgłasza niepowodzenie zamiast czekać bez końca.
- [ ] **K9** (W8): Gra bez trybu deweloperskiego bez zmian.
  - Kroki: uruchom grę z modem zwykłym poleceniem (bez trybu deweloperskiego), nowa gra,
    powalcz chwilę z dowolnym przeciwnikiem i zamknij grę.
  - Oczekiwane: konsola deweloperska się nie otwiera, nie powstaje dziennik walki ani katalog wyników,
    gra wygląda i działa jak przed zmianą.
- [ ] **K10** (W9, W10, W11): Scenariusze dla 001, instrukcja i zasady zaliczania.
  - Kroki: przeczytaj instrukcję i uruchom według niej wszystkie scenariusze dla 001 w trybie
    automatycznym. Przeczytaj ADR do zasady 5, opis weryfikacji w procesie i instrukcję dla Claude.
  - Oczekiwane: każdy scenariusz przechodzi bez błędów i daje raport, z którego da się ocenić
    swoje kryterium. Instrukcja wystarcza, żeby napisać nowy scenariusz bez czytania kodu.
    ADR i proces mówią, które kryteria może zaliczyć raport i co wpisać do tabeli „Weryfikacja”.
    Instrukcja dla Claude pozwala uruchamiać bez pytania tylko tryb automatyczny.
- [ ] **K11** (W12): Oczekiwania w scenariuszu.
  - Kroki: P0, uruchom w trybie automatycznym kopię scenariusza dla 001 K2 z dwoma dopisanymi
    oczekiwaniami: jednym prawdziwym („najdłuższe combo `BDT_1071_Addon_Ramon` ≤ 3”) i jednym
    fałszywym („najdłuższe combo `BDT_1071_Addon_Ramon` ≥ 5”). Potem uruchom jednym poleceniem
    wszystkie scenariusze dla 001 trzy razy z rzędu.
  - Oczekiwane: raport kopii oznacza pierwsze oczekiwanie jako zaliczone, drugie jako niezaliczone
    z wartością faktyczną, a polecenie zgłasza niepowodzenie. Wszystkie trzy przebiegi zestawu 001
    kończą się podsumowaniem bez żadnego niezaliczonego oczekiwania.
- [ ] **K12** (W4, W5): Dziennik na żądanie w zwykłej grze deweloperskiej.
  - Kroki: uruchom grę z modem w trybie deweloperskim zwykłym poleceniem (bez scenariusza), nowa
    gra, `cheat god`, `insert BDT_1006_Bandit_H` i walcz z nim minutę. Potem włącz dziennik
    poleceniem konsoli, walcz kolejną minutę, wyłącz dziennik i zamknij grę. Zrób raport z tego
    dziennika narzędziem raportu.
  - Oczekiwane: przed włączeniem dziennika nie powstaje żaden plik dziennika. Raport obejmuje tylko
    minutę z włączonym dziennikiem i pokazuje ciosy bohatera z obrażeniami i ciosy bandyty.

## Wpływ na zapisy gry

Brak nowego stanu w zapisach. Zapis z polecenia konsoli jest zwykłym zapisem gry, takim samym
jak zapis z menu. Dziennik i wyniki przebiegów leżą poza zapisami.

## Zasoby i prawa

Brak.

## Pytania otwarte

- [x] **P1:** Skąd gra bierze moda podczas testu? Dziś mod trzeba zainstalować w folderze gry,
  a uruchomienie scenariusza z modem zmieniałoby instalację gracza. **Rozstrzygnięcie (2026-10-29):**
  polecenie testu samo pakuje moda z bieżących plików, a gra wczytuje go z katalogu roboczego
  repozytorium. Folder gry pozostaje nietknięty. Opis w W2, kryterium K2.
- [x] **P2:** Czy scenariusz ma umieć czekać na zdarzenie z walki, np. „gdy paladyn zacznie serię”
  albo „po pierwszym ciosie serii”, z limitem czasu? **Rozstrzygnięcie (2026-10-29):** tak, każde
  czekanie z limitem czasu gry. Opis w W1, kryteria K6 i K8.
- [x] **P3:** Jaki zakres dziennika: tylko walka wręcz NPC i bohatera, czy od razu także walka
  dystansowa i magia? **Rozstrzygnięcie (2026-10-29):** tylko walka wręcz, NPC i bohatera.
  Opis w W4 i w „Poza zakresem”.
- [x] **P4:** Jak ma wyglądać okno gry w trybie automatycznym (zwykłe okno, małe okno bez przejmowania
  fokusu, pełny ekran) i czy gra ma grać dźwięk? Test zajmuje komputer na czas przebiegu.
  **Rozstrzygnięcie (2026-10-29):** tryb automatyczny w małym oknie z dźwiękiem, tryb ręczny
  na zwykłych ustawieniach. Ustawienia z testu nie przechodzą do zwykłej gry. Opis w W2,
  kryterium K2.
- [x] **P5:** Czy wynik automatycznego przebiegu może zaliczyć kryterium akceptacji? Zasada 5
  konstytucji mówi, że „Działa” oznacza przejście kroków przez kogoś. **Rozstrzygnięcie
  (2026-10-29):** tak, dla kryteriów, które da się ocenić z raportu. Kryteria wizualne zalicza
  człowiek, a zasadę 5 doprecyzowuje osobny ADR. Opis w W10, kryterium K10.
- [x] **P6:** Czy Claude może uruchamiać scenariusze testowe bez pytania o zgodę za każdym razem?
  Dziś każde uruchomienie gry i instalacja moda wymagają zgody właściciela projektu.
  **Rozstrzygnięcie (2026-10-29):** tak, w trybie automatycznym. Tryb ręczny, instalacja w folderze
  gry i zwykłe uruchomienie gry nadal wymagają zgody. Opis w W11, kryterium K10.
- [x] **P7:** Czy scenariusz zawiera oczekiwane wyniki, które raport sprawdza sam (np. „najdłuższe
  combo paladyna = 4”, wynik: zaliczone albo nie), czy raport tylko opisuje przebieg, a ocenia
  człowiek albo Claude? Oczekiwania pozwalają powtarzać testy po każdej zmianie, ale walka jest
  losowa, więc źle dobrane progi będą dawać przypadkowe niepowodzenia. **Rozstrzygnięcie
  (2026-10-29):** tak, oczekiwania w scenariuszu, a zestaw scenariuszy specyfikacji uruchamia się
  jednym poleceniem. Opis w W12, kryterium K11.
- [x] **P8:** Kiedy dziennik walki jest włączony: zawsze w trybie deweloperskim, tylko w przebiegach
  scenariuszy, czy także na żądanie poleceniem konsoli w zwykłej grze deweloperskiej (np. gdy
  właściciel projektu sprawdza obrażenia z 002 w swojej grze)? **Rozstrzygnięcie (2026-10-29):**
  w scenariuszach zawsze, w zwykłej grze deweloperskiej na żądanie poleceniem konsoli. Opis w W4,
  kryterium K12.

## Weryfikacja

<!-- Wypełniane po implementacji: kto, kiedy, na jakiej wersji, wynik dla każdego K. -->
