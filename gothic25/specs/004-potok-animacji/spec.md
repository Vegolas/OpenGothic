# 004: Potok animacji

- **Status:** W realizacji
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

- [ ] **K1** (W2, W3): Oryginalne animacje przechodzą konwersję bez straty.
  - Kroki: polecenie konwersji w obie strony dla wszystkich animacji modelu ludzi i jego nakładek
    z kopii gry (podstawa i dodatek), bez otwierania Blendera.
  - Oczekiwane: każdy plik wynikowy jest bajt w bajt równy oryginałowi. Raport podaje liczbę
    sprawdzonych animacji i listę różnic (pustą).
- [ ] **K2** (W2): Oryginał wczytany do Blendera wygląda jak w grze.
  - Kroki: wczytaj do Blendera oryginalny cios pięścią i atak mieczem jednoręcznym ze stylu
    mistrza. Porównaj klatki z optymalną klatką trafienia z tymi samymi chwilami w grze
    (scenariusz z W9).
  - Oczekiwane: pozy się zgadzają (ocena człowieka): stopy na ziemi, ten sam kierunek ciosu
    i ruch postaci w tę samą stronę.
- [ ] **K3** (W1, W4): Budowanie jest powtarzalne i zgłasza błędy.
  - Kroki: zbuduj animacje dwa razy z tego samego stanu repozytorium i porównaj wyniki. Potem
    zbuduj kolejno z trzema zepsutymi źródłami testowymi: animacja bez jednej kości, zdarzenie poza
    zakresem klatek, definicja wskazująca brakującą animację. Na koniec zmień plik Blendera bez
    ponownego eksportu i uruchom sprawdzenie zgodności.
  - Oczekiwane: oba wyniki są identyczne, a budowanie działa na komputerze bez Blendera. Każdy
    zepsuty przypadek i niezgodny eksport kończą się kodem błędu i komunikatem z nazwą animacji
    i powodem.
- [ ] **K4** (W5, W9): Podmiana istniejącej animacji.
  - Kroki: testowa podmiana animacji stania ludzi (np. spojrzenie w bok) jako lokalne dane testowe
    (W16), zbudowanie moda z nimi, scenariusz z W9 z serią zrzutów bohatera.
  - Oczekiwane: na zrzutach widać zmienioną animację. Bohater stoi w miejscu, a inne animacje
    (bieg, walka) są oryginalne. Dane testowe powstają lokalnie z kopii gry, nie trafiają do
    repozytorium ani do wydania.
- [ ] **K5** (W6, W8): Sierpowe bohatera w grze.
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
- [ ] **K6** (W6): Zdarzenia z definicji działają.
  - Kroki: scenariusz z W9 odtwarza sierpowy na bohaterze stojącym przy przeciwniku. Dziennik walki
    i log gry.
  - Oczekiwane: trafienie, dźwięk zamachu i okno combo pojawiają się w klatkach z definicji.
- [ ] **K7** (W7): Paczka nie zawiera niezmienionych oryginałów.
  - Kroki: zbuduj paczkę moda i porównaj jej zawartość z archiwami oryginalnej gry (nazwy i sumy
    kontrolne).
  - Oczekiwane: w paczce nie ma niezmienionego pliku animacji ani definicji modelu z gry, w tym
    pełnych definicji modelu. Są tylko MAN zbudowane z `.anim` moda i pliki definicji moda (W1, W6).
    Żaden MAN z paczki nie ma tych samych próbek co oryginał.
- [ ] **K8** (W8, W12, W15): Bez moda bez zmian.
  - Kroki: ta sama kompilacja silnika bez moda, bohater z pięściami: atak z lewej, zwykły atak,
    combo. Potem scenariusz z K13 bez moda.
  - Oczekiwane: atak z lewej niczego nie robi, zwykły atak i combo są jak w oryginale. Kopacz nie
    wyprowadza sierpowych, a jego ciosy boczne ze stylu są ciosami do przodu.
- [ ] **K9** (W12): Zapisy.
  - Kroki: zapis z poprzedniej wersji moda wczytany w nowej. Potem zapis zrobiony w trakcie
    sierpowego, wczytany ponownie z modem.
  - Oczekiwane: wszystkie zapisy się wczytują. Z modem bohater po wczytaniu może walczyć pięściami
    i wyprowadzić sierpowy.
  - Zmienione 2026-11-05 (decyzja właściciela przy Z18): krok „wczytany bez moda” usunięty. Zapis
    zrobiony z modem nie wczytuje się bez moda niezależnie od animacji („Cannot init RTN_TOT_3”),
    bo skrypty moda mają inne numery symboli niż skrypty gry (ADR 0005). Animację, której nie zna,
    silnik pomija przy wczytaniu zapisu: `Pose::load` usuwa jej warstwę, a postać wraca do zwykłej
    pozy.
- [ ] **K10** (W10, W11): Złe ustawienia i opis kroków.
  - Kroki: na czystym checkoucie pobierz dodatek importu narzędziem moda i wykonaj import oryginału.
    Potem uruchom import ze złą ścieżką do Blendera, a potem z innym commitem dodatku importu.
    Osoba spoza implementacji (albo nowa sesja Claude'a) dodaje według opisu z W11 testową animację
    i ogląda ją w grze.
  - Oczekiwane: oba złe ustawienia kończą się komunikatem, co poprawić. Według opisu da się przejść
    całą drogę bez dodatkowych pytań.
- [ ] **K11** (W9, W13): Definicje moda łączą się z oryginałem.
  - Kroki: scenariusz z lokalnym plikiem testowym definicji moda (W16), który dodaje nową animację
    do modelu ludzi, zastępuje definicję jednej oryginalnej animacji (np. zmienia jej zdarzenie)
    i dodaje animację do nakładki stylu walki. Poleceniem z W9 wypisuje definicje tych animacji
    i jednej niezmienionej. Potem to samo bez pliku testowego i bez moda.
  - Oczekiwane:
    - z plikiem testowym nowa animacja i podmieniona definicja pochodzą z moda, a niezmieniona
      z oryginału;
    - animacja dodana do nakładki działa po nałożeniu nakładki;
    - bez pliku i bez moda wszystkie trzy wypisują się jak w oryginale, a nowej nie ma.
- [ ] **K12** (W14): Odbicie lustrzane.
  - Kroki: odbij w narzędziu sierpowy z lewej, a wynik odbij jeszcze raz. Odbij też oryginalny atak
    boczny mieczem z lewej i porównaj z oryginalnym atakiem z prawej. Scenariusz z W9 ze zrzutami
    obu sierpowych.
  - Oczekiwane: podwójne odbicie jest równe animacji wyjściowej w granicach dokładności formatu.
    Odbity atak mieczem z lewej jest ruchem w drugą stronę, a kończyna trafiająca w zdarzeniach jest
    po drugiej stronie. Na zrzutach sierpowy z prawej jest lustrzanym odbiciem lewego: stopy na
    ziemi, ta sama wysokość ciosu (ocena człowieka).
- [ ] **K13** (W15): NPC wyprowadzają sierpowe.
  - Kroki: scenariusz automatyczny jak 001 K12: `insert BDT_10027_Addon_Buddler` (styl silny, bez broni
    białej) atakuje nieśmiertelnego bohatera przez 2 minuty. Potem zestaw `tools/test.ps1 -Spec 001`
    jako test regresji.
  - Oczekiwane: dziennik pokazuje ciosy boczne kopacza (sierpowe), także w seriach, z obrażeniami
    bez premii. Combo do przodu pięściami ma nadal 2 ciosy. Zestaw 001 przechodzi. Jeśli jakieś
    kryterium 001 zakładało ciosy boczne pięściami jako ciosy do przodu, poprawiamy jego oczekiwania
    (W15).
- [ ] **K14** (W16): Eksport nie przepuszcza niezmienionych oryginałów.
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
