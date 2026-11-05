# 004: Potok animacji

- **Status:** Zrobiona
- **Utworzono:** 2026-11-03
- **Zmieniona:** 2026-11-03 po sprawdzeniu licencji MDK (zadanie Z4): P2 rozstrzygnięte od nowa,
  doszło P9, zmienione W2, W5-W7, W9, W13, W16, K4, K7, K11 i K14. Ponownie 2026-11-04: P9
  rozstrzygnięte od nowa (zmienione oryginalne animacje mogą trafić do paczki, ADR 0009), zmienione
  „Problem”, „Cel”, scenariusz 1, W2, W7, W16, K7, K14 i „Zasoby i prawa”. 2026-11-05: dopisek
  do W14 (odbicie wpięte w niesymetryczną postawę, decyzja właściciela przy Z17) i K9 bez kroku
  „bez moda” (decyzja właściciela przy Z18).
- **Warstwa (wstępnie):** narzędzia, zasoby i silnik <!-- zasoby / skrypty / silnik -->

- **Powiązane:** [001: Combosy NPC w walce wręcz](../001-combosy-npc-w-walce-wrecz/spec.md)
  (combo na pięści; W15 zmienia zdanie z 001 W1 o ciosach bocznych pięściami),
  [002: Skalowanie obrażeń w kombo](../002-skalowanie-obrazen-w-kombo/spec.md) (ataki boczne bez
  premii), [003: Scenariusze testowe i dziennik walki](../003-scenariusze-testowe-i-dziennik-walki/spec.md)
  (sprawdzanie animacji w grze), [ADR 0002](../../decisions/0002-duze-zasoby-w-repo.md) (duże
  zasoby w repozytorium, zob. W1), [ADR 0006](../../decisions/0006-mod-tylko-dla-opengothic.md),
  [ADR 0007](../../decisions/0007-zrodla-i-budowanie-animacji-moda.md) (źródła i narzędzia),
  [ADR 0008](../../decisions/0008-dokladanie-definicji-animacji-moda-przez.md) (definicje moda
  dokładane przez silnik), konstytucja, zasady 6, 9 i 10.

## Problem

Mod nie ma dziś jak dodać nowej animacji postaci ani zmienić istniejącej. Każdy pomysł, który
potrzebuje nowych ruchów, stoi przez to w miejscu, np. styl walki bez broni z atakami bocznymi,
nowe animacje stania NPC czy losowe animacje bezczynności.

- Silnik w trybie Gothic II czyta klatki każdej animacji tylko w postaci skompilowanej, a definicje
  modelu (nazwy animacji, flagi, przejścia, zdarzenia, np. klatka trafienia i okno combo) tylko pod
  nazwą wersji skompilowanej. Treść definicji może być tekstowa, w składni Gothica.
- Oryginalna droga, czyli kompilacja zasobów przez grę, odpada (ADR 0006). Biblioteka, na której
  stoi silnik, czyta formaty skompilowane, ale ich nie zapisuje. Dodatek do Blendera (KrxImpExp)
  importuje i eksportuje animacje w formacie źródłowym Gothica (ASC), ale nie zapisuje formatów,
  które czyta gra.
- Walka pięściami nie ma ataków bocznych: przyciski ataku z lewej i z prawej nic nie robią, a ciosy
  boczne ze stylu walki NPC silnik zamienia na ciosy do przodu.

Test stosu z 2026-11-02 i prototyp z 2026-11-03 pokazały, że droga istnieje:

- Blender 5.2 z KrxImpExp poprawnie wczytuje szkielet i ciało HUMANS.
- Animację z gry da się przenieść do Blendera i z powrotem do pliku gry bez straty: wynik jest bajt
  w bajt równy oryginałowi.
- Testowa animacja stania, zrobiona w Blenderze i podmieniona w miejsce oryginalnej, zadziałała
  w grze.

Brakuje powtarzalnego narzędzia od Blendera do paczki moda, definicji moda dla nowych animacji
i obsługi ataków bocznych pięściami. Podmiana istniejącej animacji działa, bo jej definicja już
jest w grze. Nowej animacji, np. sierpowego z lewej, gra bez definicji nie użyje.

Umowa licencyjna MDK obejmuje licencją GothicMOD tylko skrypty i nowe dane moderów, a resztę
zostawia na licencji gry (zadanie Z4, ADR 0007). Mod ma więc własne wpisy definicji, które gra łączy
z oryginałem z kopii gracza. Animacje moda mogą powstawać z oryginałów i trafiać do paczki po
zmianach, tak jak w innych modach do Gothica, bo gracz i tak musi mieć własną kopię gry (decyzja
właściciela z 2026-11-04, ADR 0009). Niezmienionych plików z gry nie publikujemy (konstytucja,
zasada 6).

## Cel

Autor moda tworzy albo zmienia animację człowieka w Blenderze i jednym poleceniem, bez okien
i bez ręcznych kroków, dostaje ją w grze. Dotyczy to zarówno podmiany istniejącej animacji, jak
i nowej animacji razem z jej definicją. Paczka zawiera animacje moda (nowe albo zmienione
oryginalne) i wpisy definicji moda, a gra łączy je z oryginałem z kopii gracza. Pierwszym prawdziwym przypadkiem są sierpowe z lewej i z prawej
(prawy jako lustrzane odbicie lewego): bohater i NPC walczący pięściami zadają nimi ciosy w grze.

## Poza zakresem

- Szkielety inne niż ludzki (potwory, orkowie, zwierzęta) oraz zmiany samego szkieletu i ciała:
  nowe kości, nowe siatki, nowe sloty na broń.
- Animacje twarzy (mimika, ruch ust).
- Pełny styl walki bez broni: inne nowe ciosy niż sierpowe (kopnięcia, podbródkowy, dłuższe combo
  do przodu), warianty parady i uniki, zmiany stylów walki NPC (AI), balans i talent. To osobna
  specyfikacja, która skorzysta z tej. Tutaj sierpowe są pierwszym przypadkiem, który sprawdza potok.
  NPC używają ich tylko tam, gdzie ich obecny styl już przewiduje cios boczny (W15).
- Jakość artystyczna animacji. Sierpowy może być zgrubny, byle czytelny jako cios.
- Zgodność z oryginalnym silnikiem `Gothic2.exe` i jego narzędziami (ADR 0006).
- Automatyczna ocena wyglądu animacji (płynność, poślizg stóp, przenikanie). To ocenia człowiek.
- Zewnętrzne źródła animacji (mocap, biblioteki animacji, generowanie przez AI). Każde takie źródło
  wymaga osobnej decyzji o licencji (konstytucja, zasada 6).
- Podgląd na żywo w Blenderze (połączenie przez MCP) jako część budowania. Podgląd pomaga autorowi
  i Claude'owi, ale build go nie wymaga.

## Scenariusze gracza

„Gracz” to tutaj głównie autor moda (właściciel projektu albo Claude), a w scenariuszach 5, 6 i 8
ktoś, kto gra w moda.

1. **Gdy** autor chce zobaczyć oryginalną animację jako wzorzec, np. cios pięścią, **wtedy** jednym
   poleceniem wczytuje ją z własnej kopii gry do Blendera, razem ze szkieletem i ciałem, i widzi ją
   tak jak w grze. Nową animację zaczyna od czystego szkieletu albo od oryginału, np. od jego pozy,
   i zmienia ją.
2. **Gdy** autor zrobił w Blenderze własną animację o nazwie istniejącej, np. nowe stanie, **wtedy**
   po zbudowaniu moda zastępuje ona oryginalną w grze, a pozostałe animacje zostają bez zmian.
3. **Gdy** autor dodaje nową animację, np. sierpowy z lewej, **wtedy** dopisuje jej definicję
   do tekstowych definicji moda (nazwa, warstwa, przejścia, flagi, klatki, zdarzenia, takie jak
   klatka trafienia i okno combo). Po zbudowaniu moda gra używa jej tak samo jak oryginalnych animacji.
4. **Gdy** Claude buduje animacje bez okna Blendera i bez udziału człowieka, **wtedy** polecenie
   kończy się sukcesem albo błędem z nazwą animacji i powodem, np. zły szkielet, brak klatek,
   zdarzenie poza zakresem klatek. Ten sam stan repozytorium daje te same pliki.
5. **Gdy** gracz walczy pięściami i atakuje z lewej albo z prawej, także w oknie combo po ciosie
   do przodu, **wtedy** bohater wyprowadza sierpowy z tej strony i trafia przeciwnika jak zwykłym
   ciosem pięścią.
6. **Gdy** ktoś uruchomi grę bez moda Gothic 2.5, **wtedy** walka pięściami i wszystkie animacje
   wyglądają jak dotąd, a atak z lewej pięściami niczego nie robi, tak jak w oryginale.
7. **Gdy** autor albo Claude chce obejrzeć animację w grze bez grania, **wtedy** scenariusz testowy
   odtwarza ją na postaci i robi serię zrzutów ekranu.
8. **Gdy** bohater bije się na pięści z kopaczem albo bandytą, którego styl walki przewiduje ciosy
   boczne, **wtedy** przeciwnik w seriach wyprowadza sierpowe zamiast samych prostych.

## Wymagania

- **W1:** Każda animacja moda ma w repozytorium dwie postacie:
  - plik Blendera, czyli plik roboczy do edycji (rozmiar i sposób przechowywania według ADR 0002);
  - tekstowy eksport z Blendera, który jest źródłem buildu: bezstratny, klatka po klatce, czytelny
    w diffie.

  Definicje animacji są w plikach tekstowych (W7). Pliki w formatach gry powstają z eksportu
  i definicji narzędziem i nie są wersjonowane jako źródło. Narzędzie zgłasza błąd, gdy eksport
  tekstowy nie zgadza się z plikiem Blendera.
- **W2:** Narzędzie wczytuje do Blendera dowolną oryginalną animację ludzi z kopii gry autora
  (także z modeli nakładek, np. stylów walki), razem ze szkieletem i ciałem, w pozie zgodnej z grą.
  Oryginał służy jako wzorzec, jako punkt wyjścia nowej animacji i do testów. Pliki z gry i robocze
  pliki z oryginałami trafiają do lokalnego katalogu roboczego. Do repozytorium animacja trafia
  dopiero po zmianach, przez eksport (W16). Nową animację narzędzie zakłada też na czystym
  szkielecie.
- **W3:** Konwersja nie traci danych. Oryginalna animacja wczytana do Blendera i zapisana z powrotem
  bez zmian daje plik bajt w bajt równy oryginałowi.
- **W4:** Budowanie animacji to jedno polecenie z narzędzi moda, wykonywane także przy zwykłym
  budowaniu moda.
  - Działa bez okien i bez interakcji, a z tych samych źródeł daje identyczne pliki.
  - Nie wymaga Blendera: buduje z eksportu tekstowego (W1). Blendera potrzebują tylko import
    oryginałów (W2), eksport i sprawdzenie zgodności eksportu z plikiem Blendera.
  - Kończy się kodem błędu i komunikatem z nazwą animacji, gdy: szkielet nie pasuje do modelu
    (brak albo nadmiar kości), animacja nie ma klatek, definicja wskazuje nieistniejącą animację,
    zdarzenie wypada poza zakresem klatek.
- **W5:** Animacja moda o nazwie oryginalnej animacji zastępuje ją w grze. Pozostałe animacje
  modelu zostają oryginalne.
- **W6:** Mod może dodać nowe animacje do modelu ludzi i do każdej jego nakładki (style walki,
  postawy, chód) oraz zastąpić definicję oryginalnej animacji.
  - Każda definicja ma nazwę, warstwę, następną animację, czas wejścia i wyjścia, flagi (ruch,
    obrót, kolejka, bezczynność), zakres klatek oraz zdarzenia, których używa gra: okno combo,
    optymalną klatkę trafienia, kończynę trafiającą, dźwięki i efekty.
  - Definicje moda są w tekstowym pliku w składni Gothica, osobnym dla modelu albo nakładki. Plik
    zawiera tylko wpisy moda.
  - W grze nowa animacja działa tak samo jak oryginalna o tych samych ustawieniach.
- **W7:** Paczka moda zawiera animacje moda (nowe albo zmienione oryginalne) i wpisy definicji moda.
  Nie ma w niej niezmienionych plików z gry: oryginalnych animacji bez zmian ani pełnych definicji
  modelu (konstytucja, zasada 6, ADR 0009).
  - Gra łączy definicje moda z oryginalnymi z kopii gracza: animacja o nowej nazwie dochodzi, a wpis
    o nazwie oryginalnej animacji zastępuje oryginał (W13).
  - Nowe animacje i wpisy definicji to praca moda na licencji GothicMOD (konstytucja, zasada 9).
    Zmienione oryginalne animacje są opracowaniem dzieła Piranha Bytes (ADR 0009).
- **W8:** Bohater walczący pięściami wyprowadza atak z lewej i z prawej, jeśli model ma dla niego
  animację. Pierwsze takie animacje to sierpowy z lewej i jego lustrzane odbicie, sierpowy z prawej
  (W14).
  - Cios trafia jak zwykły cios pięścią i zadaje obrażenia jak atak boczny w 002 (bez premii combo,
    także gdy jest częścią serii).
  - Sierpowe łączą się w serie tak jak ataki boczne bronią. W oknie combo ciosu pięścią do przodu
    atak z lewej albo z prawej przechodzi w sierpowy z tej strony. W oknie combo sierpowego można
    wyprowadzić kolejny sierpowy albo cios do przodu. Okna combo i klatki trafienia pochodzą
    z definicji animacji (W6).
  - Bez takiej animacji, w tym bez moda, atak boczny pięściami działa jak dotąd, czyli nic nie robi.
- **W9:** W trybie deweloperskim da się poleceniami konsoli, także w scenariuszu testowym (003):
  - odtworzyć wskazaną animację na wskazanej postaci, a potem obejrzeć ją na serii zrzutów bez
    sterowania bohaterem;
  - wypisać definicję animacji z modelu postaci, tak jak widzi ją gra: skąd pochodzi (oryginał albo
    mod), warstwę, zakres klatek i zdarzenia.
- **W10:** Narzędzia sprawdzają wersję Blendera i dodatku importu. Brak programu albo zła wersja
  kończy się jasnym komunikatem, co i gdzie ustawić, a nie błędem w trakcie konwersji.
  - Ścieżka do Blendera jest ustawieniem dewelopera, nie ścieżką wpisaną w narzędzia.
  - Dodatek importu w przypiętym commicie pobiera narzędzie moda, bez instalacji w profilu Blendera
    dewelopera. Zmiana wersji dodatku to zmiana commitu zapisanego w repozytorium.
- **W11:** W repozytorium jest opis kroków dla autora: jak wczytać oryginał, jak dodać i zbudować
  nową animację, jak ją obejrzeć w grze.
- **W12:** Bez moda Gothic 2.5 silnik zachowuje się jak dotąd. Zapisy gry z poprzednich wersji moda
  się wczytują.
- **W13:** Łączenie definicji moda z oryginałem:
  - bez pliku definicji moda model działa dokładnie jak oryginał;
  - z plikiem model ma wszystkie oryginalne animacje, a do tego animacje moda;
  - wpis moda o nazwie oryginalnej animacji zastępuje tylko ją;
  - to samo dotyczy nakładek, a nakładki stylów walki i stare zapisy działają bez zmian.
- **W14:** Narzędzie tworzy lustrzane odbicie animacji (lewo i prawo): zamienia kości lewej i prawej
  strony, odbija ruch względem płaszczyzny symetrii postaci i zamienia strony w zdarzeniach
  (np. kończyna trafiająca). Odbicie jest częścią buildu, więc odbita animacja nie ma osobnego źródła.
  Podwójne odbicie daje animację wyjściową.
  - Dopisane 2026-11-05 (decyzja właściciela przy Z17): animację, która zaczyna się i kończy
    w niesymetrycznej postawie, odbicie wpina w tę postawę. Sierpowe startują z postawy `S_FISTRUN`
    z lewą nogą z przodu. Odbity sierpowy wchodzi z tej postawy i do niej wraca, a stopy zostają tam,
    gdzie ma je postawa. Bez tego przy każdym prawym sierpowym nogi zamieniałyby się miejscami.
    Podwójne odbicie dotyczy wtedy samego odbicia, przed wpięciem w postawę.
- **W15:** NPC walczący pięściami wyprowadza sierpowy tam, gdzie jego styl walki zleca cios boczny
  (pojedynczy albo w serii).
  - Dziś silnik zamienia taki cios na cios do przodu (001 W1). Bez animacji sierpowych, w tym bez
    moda, tak zostaje.
  - Styl walki NPC (AI) się nie zmienia. Obrażenia sierpowych NPC są takie jak ataku bocznego (002,
    bez premii).
  - Po wdrożeniu zdanie z 001 W1 o ciosach bocznych pięściami trzeba zaktualizować odwołaniem do tej
    specyfikacji.
- **W16:** Narzędzia pilnują, żeby do źródeł moda nie trafił niezmieniony oryginał:
  - eksport do źródeł moda przepuszcza animację z importu oryginału po zmianach, a odmawia, gdy jej
    klatki są takie same jak w oryginale (także pod nową nazwą), z komunikatem, że trzeba ją zmienić;
  - wyjątek, jawnie włączany, mają tylko lokalne dane testowe, które nie trafiają do repozytorium.

## Kryteria akceptacji

Wspólne przygotowanie (P0): mod zbudowany z repozytorium, gra uruchamiana przez `tools/test.ps1`
(scenariusze z `tests/004/`), dla kryteriów ręcznych z `-Manual`. Blender i dodatek importu
w wersjach z W10 (Blender 5.2 LTS, KrxImpExp z przypiętego commitu gałęzi `dev`).

- [x] **K1** (W2, W3): Oryginalne animacje przechodzą konwersję bez straty.
  - Kroki: polecenie konwersji w obie strony dla wszystkich animacji modelu ludzi i jego nakładek
    z kopii gry (podstawa i dodatek), bez otwierania Blendera.
  - Oczekiwane: każdy plik wynikowy jest bajt w bajt równy oryginałowi. Raport podaje liczbę
    sprawdzonych animacji i listę różnic (pustą).
- [x] **K2** (W2): Oryginał wczytany do Blendera wygląda jak w grze.
  - Kroki: wczytaj do Blendera oryginalny cios pięścią i atak mieczem jednoręcznym ze stylu
    mistrza. Porównaj klatki z optymalną klatką trafienia z tymi samymi chwilami w grze
    (scenariusz z W9).
  - Oczekiwane: pozy się zgadzają (ocena człowieka): stopy na ziemi, ten sam kierunek ciosu
    i ruch postaci w tę samą stronę.
- [x] **K3** (W1, W4): Budowanie jest powtarzalne i zgłasza błędy.
  - Kroki: zbuduj animacje dwa razy z tego samego stanu repozytorium i porównaj wyniki. Potem
    zbuduj kolejno z trzema zepsutymi źródłami testowymi: animacja bez jednej kości, zdarzenie poza
    zakresem klatek, definicja wskazująca brakującą animację. Na koniec zmień plik Blendera bez
    ponownego eksportu i uruchom sprawdzenie zgodności.
  - Oczekiwane: oba wyniki są identyczne, a budowanie działa na komputerze bez Blendera. Każdy
    zepsuty przypadek i niezgodny eksport kończą się kodem błędu i komunikatem z nazwą animacji
    i powodem.
- [x] **K4** (W5, W9): Podmiana istniejącej animacji.
  - Kroki: testowa podmiana animacji stania ludzi (np. spojrzenie w bok) jako lokalne dane testowe
    (W16), zbudowanie moda z nimi, scenariusz z W9 z serią zrzutów bohatera.
  - Oczekiwane: na zrzutach widać zmienioną animację. Bohater stoi w miejscu, a inne animacje
    (bieg, walka) są oryginalne. Dane testowe powstają lokalnie z kopii gry, nie trafiają do
    repozytorium ani do wydania.
- [x] **K5** (W6, W8): Sierpowe bohatera w grze.
  - Kroki: P0 z `-Manual`, bohater z pięściami, `insert` przeciwnika, który nie oddaje. Kilka razy
    atak z lewej i z prawej z miejsca. Potem serie: cios do przodu i w jego oknie combo atak z lewej,
    w oknie sierpowego atak z prawej, a na koniec cios do przodu. Na koniec samo zwykłe combo
    pięściami. Dziennik walki z 003.
  - Oczekiwane:
    - atak z lewej i z prawej odtwarza sierpowy z tej strony (ocena człowieka: czytelny jako cios
      z tej strony);
    - serie płynnie przechodzą z ciosu w cios, a dziennik pokazuje je jako jedną serię;
    - trafienia wypadają w klatkach trafienia z definicji, a sierpowe mają obrażenia ataku bocznego
      bez premii (002 W3);
    - zwykłe combo pięściami działa jak dotąd.
- [x] **K6** (W6): Zdarzenia z definicji działają.
  - Kroki: scenariusz z W9 odtwarza sierpowy na bohaterze stojącym przy przeciwniku. Dziennik walki
    i log gry.
  - Oczekiwane: trafienie, dźwięk zamachu i okno combo pojawiają się w klatkach z definicji.
- [x] **K7** (W7): Paczka nie zawiera niezmienionych oryginałów.
  - Kroki: zbuduj paczkę moda i porównaj jej zawartość z archiwami oryginalnej gry (nazwy i sumy
    kontrolne).
  - Oczekiwane: w paczce nie ma niezmienionego pliku animacji ani definicji modelu z gry, w tym
    pełnych definicji modelu. Są tylko MAN zbudowane z `.anim` moda i pliki definicji moda (W1, W6).
    Żaden MAN z paczki nie ma tych samych próbek co oryginał.
- [x] **K8** (W8, W12, W15): Bez moda bez zmian.
  - Kroki: ta sama kompilacja silnika bez moda, bohater z pięściami: atak z lewej, zwykły atak,
    combo. Potem scenariusz z K13 bez moda.
  - Oczekiwane: atak z lewej niczego nie robi, zwykły atak i combo są jak w oryginale. Kopacz nie
    wyprowadza sierpowych, a jego ciosy boczne ze stylu są ciosami do przodu.
- [x] **K9** (W12): Zapisy.
  - Kroki: zapis z poprzedniej wersji moda wczytany w nowej. Potem zapis zrobiony w trakcie
    sierpowego, wczytany ponownie z modem.
  - Oczekiwane: wszystkie zapisy się wczytują. Z modem bohater po wczytaniu może walczyć pięściami
    i wyprowadzić sierpowy.
  - Zmienione 2026-11-05 (decyzja właściciela przy Z18): krok „wczytany bez moda” usunięty. Zapis
    zrobiony z modem nie wczytuje się bez moda niezależnie od animacji („Cannot init RTN_TOT_3”),
    bo skrypty moda mają inne numery symboli niż skrypty gry (ADR 0005). Animację, której nie zna,
    silnik pomija przy wczytaniu zapisu: `Pose::load` usuwa jej warstwę, a postać wraca do zwykłej
    pozy.
- [x] **K10** (W10, W11): Złe ustawienia i opis kroków.
  - Kroki: na czystym checkoucie pobierz dodatek importu narzędziem moda i wykonaj import oryginału.
    Potem uruchom import ze złą ścieżką do Blendera, a potem z innym commitem dodatku importu.
    Osoba spoza implementacji (albo nowa sesja Claude'a) dodaje według opisu z W11 testową animację
    i ogląda ją w grze.
  - Oczekiwane: oba złe ustawienia kończą się komunikatem, co poprawić. Według opisu da się przejść
    całą drogę bez dodatkowych pytań.
- [x] **K11** (W9, W13): Definicje moda łączą się z oryginałem.
  - Kroki: scenariusz z lokalnym plikiem testowym definicji moda (W16), który dodaje nową animację
    do modelu ludzi, zastępuje definicję jednej oryginalnej animacji (np. zmienia jej zdarzenie)
    i dodaje animację do nakładki stylu walki. Poleceniem z W9 wypisuje definicje tych animacji
    i jednej niezmienionej. Potem to samo bez pliku testowego i bez moda.
  - Oczekiwane:
    - z plikiem testowym nowa animacja i podmieniona definicja pochodzą z moda, a niezmieniona
      z oryginału;
    - animacja dodana do nakładki działa po nałożeniu nakładki;
    - bez pliku i bez moda wszystkie trzy wypisują się jak w oryginale, a nowej nie ma.
- [x] **K12** (W14): Odbicie lustrzane.
  - Kroki: odbij w narzędziu sierpowy z lewej, a wynik odbij jeszcze raz. Odbij też oryginalny atak
    boczny mieczem z lewej i porównaj z oryginalnym atakiem z prawej. Scenariusz z W9 ze zrzutami
    obu sierpowych.
  - Oczekiwane: podwójne odbicie jest równe animacji wyjściowej w granicach dokładności formatu.
    Odbity atak mieczem z lewej jest ruchem w drugą stronę, a kończyna trafiająca w zdarzeniach jest
    po drugiej stronie. Na zrzutach sierpowy z prawej jest lustrzanym odbiciem lewego: stopy na
    ziemi, ta sama wysokość ciosu (ocena człowieka).
- [x] **K13** (W15): NPC wyprowadzają sierpowe.
  - Kroki: scenariusz automatyczny jak 001 K12: `insert BDT_10027_Addon_Buddler` (styl silny, bez broni
    białej) atakuje nieśmiertelnego bohatera przez 2 minuty. Potem zestaw `tools/test.ps1 -Spec 001`
    jako test regresji.
  - Oczekiwane: dziennik pokazuje ciosy boczne kopacza (sierpowe), także w seriach, z obrażeniami
    bez premii. Combo do przodu pięściami ma nadal 2 ciosy. Zestaw 001 przechodzi. Jeśli jakieś
    kryterium 001 zakładało ciosy boczne pięściami jako ciosy do przodu, poprawiamy jego oczekiwania
    (W15).
- [x] **K14** (W16): Eksport nie przepuszcza niezmienionych oryginałów.
  - Kroki: zaimportuj oryginał, skopiuj jego akcję pod nową nazwą i spróbuj ją wyeksportować do
    źródeł moda. Potem to samo z jawnym wyjątkiem dla danych testowych do katalogu lokalnego. Potem
    zmień kopię (np. obróć jedną kość w jednej klatce) i wyeksportuj ją do źródeł moda. Na koniec
    załóż nową animację na czystym szkielecie i ją wyeksportuj.
  - Oczekiwane: pierwszy eksport kończy się błędem z komunikatem, że animację trzeba zmienić.
    Wyjątek zapisuje dane tylko poza repozytorium. Zmieniona kopia się eksportuje. Animacja z czystego szkieletu eksportuje się bez
    danych z oryginału (bez metadanych źródła i bez próbek slotów z oryginału).

## Wpływ na zapisy gry

Funkcja nie dodaje nowego stanu do zapisu. Zapis zawiera jednak nazwy animacji, które postać
właśnie odtwarza. Silnik już dziś przy wczytaniu pomija animacje, których model nie ma, więc zapis
zrobiony w trakcie sierpowego wczytany bez moda nie zatrzyma postaci. Sprawdza to K9.

## Zasoby i prawa

- Licencja (zadanie Z4, ADR 0007): umowa licencyjna MDK (`G2MDK-EULA.rtf`, © 2004 Pluto 13 GmbH /
  Piranha Bytes) obejmuje licencją GothicMOD tylko skrypty z `/_work/data/Scripts` i dane nowo
  utworzone przez moderów. Pozostałe dane, w tym definicje animacji z MDK i oryginalne animacje
  z gry, podlegają umowie licencyjnej gry, która formalnie nie pozwala ich rozpowszechniać, także
  po zmianach.
- Decyzja właściciela z 2026-11-04 (P9, ADR 0009): animacje moda mogą powstawać z oryginałów, np.
  od postawy bojowej, i trafiać do repozytorium i paczki po zmianach, jak w innych modach do Gothica.
  Gracz musi mieć własną kopię gry. Ryzyko z umowy licencyjnej gry właściciel przyjmuje świadomie.
- Niezmienione oryginalne animacje, definicje i szkielet służą tylko lokalnie: jako wzorzec, do
  testów narzędzi (K1, K2) i jako lokalne dane testowe (K4, K11). Nie trafiają do repozytorium ani do
  paczki (W2, W7, W16). Szkielet w lekkim pliku Blendera i lista węzłów w eksporcie opisują budowę
  modelu ludzi, do której animacja moda musi pasować.
- Nowe animacje bez zewnętrznych źródeł to nowe dane moda na licencji GothicMOD (konstytucja,
  zasada 9). Animacje zmienione z oryginałów są opracowaniem dzieła Piranha Bytes, co opisuje
  `NOTICE.txt` („na podstawie dzieła Piranha Bytes”).
- Definicje moda to własne wpisy w składni Gothica (W6), bez kopii definicji z MDK.
- Narzędzia: Blender 5.2 (GPL) i KrxImpExp, gałąź `dev` z gitlab.com/Patrix9999/krximpexp
  (GPL-3.0 według nagłówka w kodzie). Oba działają tylko u dewelopera i nie trafiają do paczki moda.
  Dodatek MCP Blender Lab (GPL) służy tylko do podglądu.

## Pytania otwarte

- [x] **P1:** Co jest źródłem animacji w repozytorium: plik Blendera, tekstowy eksport czy oba?
  **Odpowiedź (2026-11-03):** oba. Plik Blendera jest plikiem roboczym, a bezstratny eksport
  tekstowy (klatka po klatce) jest źródłem buildu. ASC z KrxImpExp odpadł jako źródło, bo w teście
  tracił do 0,5° w pojedynczych klatkach. Zapisane w W1, W4 i K3.
- [x] **P2:** Jak definicje moda mają się łączyć z oryginalnymi? Do wyboru były: pełne tekstowe
  definicje z MDK zmienione przez moda, własna nakładka nakładana przez skrypty, dokładanie definicji
  przez silnik albo pełne skompilowane definicje z buildu. Fakty: silnik już dziś czyta tekstowe
  definicje pod nazwą wersji skompilowanej, a w kopii gry właściciela są tekstowe źródła z MDK.
  **Pierwsza odpowiedź (2026-11-03):** pełne tekstowe definicje z MDK, zmienione o animacje moda, pod
  warunkiem, że MDK jest na GothicMOD. **Warunek się nie spełnił** (zadanie Z4, „Zasoby i prawa”).
  **Odpowiedź po sprawdzeniu licencji (2026-11-03):** silnik dokłada definicje moda do oryginalnych
  ([ADR 0008](../../decisions/0008-dokladanie-definicji-animacji-moda-przez.md)). Mod ma tekstowy plik
  tylko z własnymi wpisami dla modelu albo nakładki. Zapisane w W6, W7, W9, W13, K7, K11
  i „Zasobach i prawach”.
- [x] **P3:** Składnia definicji: oryginalna składnia Gothica czy własny format? **Rozstrzygnięte
  przez P2:** oryginalna składnia Gothica (MDS), którą biblioteka silnika już czyta.
- [x] **P4:** Czy w tej specyfikacji robimy też sierpowy z prawej? **Odpowiedź (2026-11-03):** tak,
  przez odbicie lustrzane w narzędziu. Zapisane w celu, scenariuszu 5, W8, W14, K5 i K12.
- [x] **P5:** Zakres modeli: tylko podstawowy model ludzi czy także nakładki? **Odpowiedź
  (2026-11-03):** model ludzi i wszystkie jego nakładki, bez innych szkieletów. Zapisane w W6, W7,
  W13, K1 i K11.
- [x] **P6:** Jak deweloper dostaje KrxImpExp w przypiętej wersji? **Odpowiedź (2026-11-03):**
  narzędzie moda pobiera przypięty commit. Zapisane w W10 i K10.
- [x] **P7:** Czy sierpowy ma od razu wchodzić w serie, czy wystarczy pojedynczy atak boczny?
  **Odpowiedź (2026-11-03):** od razu w serie, tak jak ataki boczne bronią (po ciosie do przodu
  i po sierpowym). Obrażenia zgodnie z 002, bez premii. Zapisane w W8 i K5.
- [x] **P8:** Czy NPC walczący pięściami mają używać sierpowych? Fakt z kodu: style walki NPC już
  dziś zlecają ciosy boczne pięściami, a silnik zamienia je na ciosy do przodu (001 W1).
  **Odpowiedź (2026-11-03):** tak, tam gdzie ich styl zleca cios boczny, bez zmian w AI. Zapisane
  w celu, scenariuszu 8, W15, K8, K13 i „Poza zakresem”.
- [x] **P9:** Oryginalne animacje też podlegają umowie licencyjnej gry. Jakie animacje mogą trafić
  do paczki moda: tylko z własnymi kluczami, czy także przeróbki oryginałów? **Odpowiedź
  (2026-11-03):** tylko z własnymi kluczami. Oryginały służą lokalnie jako wzorzec i do testów.
  **Odpowiedź po pierwszym sierpowym (2026-11-04):** pełne odejście od tej zasady. Sierpowy
  z własnymi kluczami od zera odstawał stylem od reszty animacji, a mody do Gothica zwykle
  rozpowszechniają zmienione oryginalne animacje, przy grze wymaganej od gracza. Animacje moda mogą
  więc powstawać z oryginałów i trafiać do paczki po zmianach. Niezmienionych plików z gry nie
  publikujemy (zasada 6). Zapisane w
  [ADR 0009](../../decisions/0009-zmienione-oryginalne-animacje-w-paczce.md), „Problemie”, „Celu”,
  scenariuszu 1, W2, W7, W16, K7, K14 i „Zasobach i prawach”.

## Weryfikacja

<!-- Wypełniane po implementacji: kto, kiedy, na jakiej wersji, wynik dla każdego K. -->

**Przebiegi automatyczne (Claude, 2026-11-05, commit `04f4b5c3`, czyste drzewo).**
- **Zestawy:** `tools/test.ps1 -Spec 004` przeszło 11 z 11 scenariuszy (przebiegi
  `20261105-1819*` do `-1823*`). Regresja: `-Spec 001` 17 z 17, `-Spec 002` 12 z 12, `-Spec 003`
  2 z 2.
- **Narzędzia:** `anim.py` i `anim.ps1` uruchomione jednym skryptem z sesji (Z20). Wyniki i kody
  wyjścia są w tabeli.
- **Katalogi wyników:** leżą w `gothic25/build/test-runs/` poza gitem, więc liczby, które
  rozstrzygają kryteria, są wpisane w tabeli.
- **Wersja kryteriów:** W14 ma dopisek o odbiciu wpiętym w postawę, a K9 nie ma już kroku „bez moda”
  (decyzje właściciela z 2026-11-05).

**Sesje ręczne (Mateusz Tomanek, 2026-11-05, commit `04f4b5c3`).**
- **Stan drzewa:** zmienione tylko dokumenty i komunikaty błędów w `common.ps1` i `test.ps1`, bez
  zmian w grze i animacjach.
- **Przebiegi:** `test.ps1 -Manual` z katalogami w `build/test-runs/`. Liczby z dziennika walki
  policzył Claude.

| K | Wynik | Wersja | Kto |
|---|---|---|---|
| K1 | spełnione. `anim.py roundtrip HUMANS`: 1038 animacji ludzi i nakładek z gry, MAN -> `.anim` -> MAN, 1038 identycznych bajt w bajt, 0 różnic. Dodatkowo przez Blendera (`anim.ps1 roundtrip`): też 1038 z 1038 | `04f4b5c3` | Claude, automatycznie |
| K2 | spełnione. Materiał: oryginalny `S_FISTATTACK` i mistrzowski `T_1HATTACKL` (nakładka `HUMANS_1HST2`) w grze (przebieg `20261105-190828-K02-oryginaly`, klatki 0, 9, 15, 24 i 0, 3, 8, 14) i te same klatki w Blenderze od tyłu i od przodu. Wstępnie (Claude): kierunek ciosu i skręt tułowia się zgadzają; po `DEF_HIT_END` gra kończy cios i wraca do postawy, więc klatka 24 ciosu pięścią w grze to już postawa. Ocena właściciela: pozy w Blenderze zgadzają się z grą (stopy na ziemi, kierunek ciosu i ruch postaci) | `04f4b5c3` | Mateusz Tomanek (ocena), Claude (zrzuty z gry i Blendera) |
| K3 | spełnione. Dwa buildy repozytorium identyczne (3 pliki, te same SHA-256). Build to sam Python, bez Blendera; źródło testowe `valid` buduje się z danymi gry i bez nich. Zepsute źródła kończą się kodem 1 z nazwą animacji i powodem: „bones without samples: BIP01 L HAND”, „DEF_OPT_FRAME [12] outside frames 1-10”, „the definition points to a missing animation HUMANS-T_G25MISSING.MAN”. Kopia `T_FISTATTACKL.blend` zmieniona w klatce 5 bez eksportu: `anim.ps1 check` kod 1, „differs from T_FISTATTACKL.anim” | `04f4b5c3` | Claude, automatycznie |
| K4 | spełnione. `004/K04`: stanie `S_RUN` z obrotem głowy z lokalnych danych `anim.py fixtures` (`# anim-extra:`), definicja z gry; na zrzutach głowa obraca się w obie strony, a bohater stoi w miejscu. Dane testowe leżą w `build/` (poza gitem), a paczka po zestawie ma tylko 3 pliki animacji moda (K7) | `04f4b5c3` | Claude, automatycznie (zrzuty: Claude) |
| K5 | spełnione. Sesja ręczna `004/reczne/K05-sierpowe` (przebieg `20261105-202145-004-reczne-K05-sierpowe`). Bohater: 72 ciosy, 24 z lewej i 28 z prawej (39 podpiętych bokiem), 20 do przodu. Serie mieszają kierunki w jednej serii dziennika, np. prawy, do przodu, lewy, prawy, do przodu. Wynik sierpowych po 440-447 ms (`DEF_OPT_FRAME 11`), ciosu do przodu po 360-367 ms (`DEF_OPT_FRAME 9`). Wszystkie 29 trafień sierpowych ma premię 100, drugi cios combo do przodu 150 (002). Zwykłe combo: 2 ciosy z wynikiem; trzecie naciśnięcie daje w dzienniku combo 3 bez wyniku, tak samo jak przed 004 (przebieg `20261103-184235-idle-khorinis`, `5dec302e`). Ocena w grze: oba sierpowe czytelne jako cios z tej strony, serie płynne, zwykłe combo jak dawniej | `04f4b5c3` | Mateusz Tomanek (gra), Claude (dziennik) |
| K6 | spełnione. `004/K06` (kopacz, 120 s, ×2): wynik sierpowych po 440-452 ms, czyli 11 klatek (`DEF_OPT_FRAME 11`), tak jak oryginalny cios do przodu po 360 ms przy `DEF_OPT_FRAME 9`. Ciosy podpięte po sierpowych po 592-602 ms, w oknie `DEF_WINDOW 11 16` (440-640 ms). Dźwięk zamachu nie trafia do dziennika; w sesji K5 słychać go przy sierpowych z obu stron | `04f4b5c3` | Claude, automatycznie; dźwięk: Mateusz Tomanek (gra) |
| K7 | spełnione. `anim.py check-pack` na paczce z zestawów: 3 pliki animacji (`HUMANS-T_FISTATTACKL.MAN` i `-R.MAN` po 7091 B, `HUMANS.EXT.MDS` 745 B), wszystkie „ok”: żaden nie jest równy plikowi gry, nie ma `.MSB` ani pełnego `.MDS`, a MAN nie ma próbek oryginału | `04f4b5c3` | Claude, automatycznie |
| K8 | spełnione. Bez moda (`# mod: off`): `004/K08a` nie ma linii „model script extension”, cios pięścią, stanie i `T_1HATTACKL` mają definicje z gry (`DEF_OPT_FRAME` 9 i 24); `004/K08b` kopacz 79 ciosów do przodu, 0 z lewej i 0 z prawej. Bohater bez moda (sesja ręczna `004/reczne/K08-bohater-bez-moda`, przebieg `20261105-204350-…-nomod`, gra bez pliku `.ini` moda): atak z lewej i z prawej nic nie robi, w dzienniku tylko ciosy do przodu, combo łączy się jak przed 004 (etap 2, a trzecie naciśnięcie bez wyniku, jak w K5) | `04f4b5c3` | Claude, automatycznie; bohater: Mateusz Tomanek (gra), Claude (dziennik) |
| K9 | spełnione (kryterium zmienione 2026-11-05). `004/K09a`: zapis w trakcie sierpowego; `K09b`: po wczytaniu z modem bohater wyprowadza prawy sierpowy (`ani info` pochodzenie `mod`); `K09c`: zapis z 0.1.0 wczytuje się, rozszerzenie „2 added, 0 replaced”, sierpowe działają | `04f4b5c3` | Claude, automatycznie |
| K10 | spełnione, z lukami opisu poprawionymi po przebiegu. Nowy agent Claude'a bez kontekstu sesji na czystym worktree: `local.json`, `get-gdc.ps1`, `get-krx.ps1` i import oryginału działają. Zła ścieżka Blendera: kod 1, „Blender not found: … Fix blender in gothic25/local.json (or G25_BLENDER)”. Inny commit dodatku: kod 1, „KrxImpExp 0123… is installed, the tools need 5be176c4…. Run tools/get-krx.ps1”, a zmieniony plik dodatku: „… was modified. Run tools/get-krx.ps1 -Force”. Według `anims/README.md` dodał `T_G25PROBA` (prawe ramię w górę) i zobaczył ją w grze (`ani info` pochodzenie `mod`, zrzuty z uniesionym ramieniem), a `check` i `check-pack` przeszły. Werdykt: „tak, z lukami”. Luki: brak katalogu, z którego uruchamiać polecenia, nieopisany `engineBuildDir`, przy definicji brak miejsca wpisu, numeru `NNN`, objaśnienia pól i uwagi o zdarzeniach ciosu, brak informacji, że `install.ps1` i `run.ps1` nie są potrzebne, kolejność źródeł ścieżki Blendera, wymaganie `git` przy `get-krx.ps1`. Wszystkie poprawione w `README.md`, `anims/README.md`, komunikacie o Blenderze (podaje teraz źródło ścieżki) i o braku silnika; nowa sesja nie przechodziła drogi drugi raz | `04f4b5c3` (przejście), poprawki w commicie weryfikacji | agent Claude'a bez kontekstu, automatycznie |
| K11 | spełnione. `004/K11a` (dane `k11`): „HUMANS.EXT.MDS: 3 added, 1 replaced” i „HUMANS_1HST1.EXT.MDS: 1 added”, `T_G25TEST` i podmieniony `S_FISTATTACK` (`DEF_OPT_FRAME` 10 i 25) z moda, `S_RUN` z gry, `T_G25OVERLAYTEST` działa na szkielecie z nakładką. `K11b` (bez danych): „2 added, 0 replaced”, bez rozszerzenia nakładki, wszystkie trzy z gry. Bez moda: `K08a` | `04f4b5c3` | Claude, automatycznie |
| K12 | spełnione. `anim.py mirror` `t_1hAttackL` podwójne odbicie 0,0000° i 0,0016 cm (0,29 granicy formatu); ręka z mieczem wejścia -112 cm w bok, odbicia +102 cm, oryginalnego `t_1hAttackR` +93 cm (ta sama strona co odbicie), korzeń 0; `DEF_HIT_LIMB` odbicia `ZS_LEFTHAND`. Sierpowy: podwójne odbicie 0,0048° i 0,0024 cm (0,90 granicy). `004/K12`: `ani info` obu sierpowych i zrzuty. Ocena właściciela na zrzutach `hookL-1..7` i `hookR-1..7` (przebieg `20261105-182320-004-K12-sierpowe-zrzuty`): prawy sierpowy jest lustrzanym odbiciem lewego, stopy na ziemi, ta sama wysokość ciosu | `04f4b5c3` | Claude, automatycznie; wygląd: Mateusz Tomanek |
| K13 | spełnione. `004/K13` (kopacz, 120 s, ×2): 35 sierpowych z lewej (7 podpiętych bokiem w seriach), 36 z prawej (29 bokiem), premia ciosów bocznych 100, combo do przodu 2. Regresja `-Spec 001` 17 z 17 bez zmiany oczekiwań | `04f4b5c3` | Claude, automatycznie |
| K14 | spełnione. Import `S_FISTATTACK`, kopia akcji `T_G25COPY`: eksport do źródeł kod 1 („unchanged copy of the original HUMANS-S_FISTATTACK.MAN”); `-AllowDerived` poza `build/` kod 1, do `build/anims-derived-test` kod 0. Kopia z obróconą głową w klatce 10 eksportuje się do źródeł. Nowa animacja na czystym szkielecie: `.anim` bez `raw` i `layout`, 25 kości, 0 slotów `ZS_`; `anim.ps1 check` zgodny | `04f4b5c3` | Claude, automatycznie |
