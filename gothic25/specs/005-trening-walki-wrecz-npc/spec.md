# 005: Trening walki wręcz NPC

- **Status:** Zrobiona
- **Utworzono:** 2026-11-05
- **Zmieniona:** 2026-11-05 przy Z6 (decyzje właściciela, ryzyko R2 planu): W5 i K5, próg odejścia od
  waypointu 3,5 m w trakcie serii i początek serii najwyżej 0,75 m od waypointu.
- **Warstwa (wstępnie):** skrypty, możliwie silnik <!-- zasoby / skrypty / silnik -->

- **Powiązane:** [001: Combosy NPC w walce wręcz](../001-combosy-npc-w-walce-wrecz/spec.md)
  (repertuar ciosów NPC i długość combo według talentu, W1),
  [002: Skalowanie obrażeń w kombo](../002-skalowanie-obrazen-w-kombo/spec.md) (trening nie zadaje
  obrażeń, W6), [003: Scenariusze testowe i dziennik walki](../003-scenariusze-testowe-i-dziennik-walki/spec.md)
  (sprawdzanie kryteriów, W9), [004: Potok animacji](../004-potok-animacji/spec.md) (sierpowe
  pięściami), [ADR 0005](../../decisions/0005-stabilne-numery-symboli.md) (zapisy gry).

## Problem

W Nocy Kruka NPC, którzy w planie dnia ćwiczą walkę, mają jeden trening: w kółko powtarzają tę samą
sekwencję z mieczem (kata), a po każdym powtórzeniu wracają na swoje miejsce. Taki plan dnia ma 26
postaci, m.in. paladyni, strażnicy i najemnicy, z talentem od 30% do 80%.

- Wszyscy ćwiczą tak samo i w tym samym rytmie. Nowicjusza nie da się odróżnić od mistrza, a dwóch
  ćwiczących obok siebie wygląda jak jedna animacja powielona dwa razy.
- Trening nie ma nic wspólnego z tym, jak ci sami NPC walczą. Od 001 NPC w walce wyprowadzają pełne
  combo, ataki z boków i serie mieszane, a od 004 także sierpowe pięściami. Na treningu tego nie widać.
- NPC bez broni białej dostaje do treningu maczugę, choć mógłby ćwiczyć pięściami.

Skutek dla gracza: plac ćwiczeń, który miał pokazywać żołnierzy w formie, wygląda mechanicznie
i nie zdradza, kto na nim jest groźny.

## Cel

Nowy plan dnia `Practice_Melee`: NPC ćwiczy w miejscu ciosy, których używa w walce (ciosy do przodu
i combo, ataki z lewej i z prawej, serie mieszane), w losowej kolejności i ze zmiennymi przerwami.
Ćwiczy swoją bronią białą albo pięściami, zależnie od wariantu wybranego przez autora moda. Po
treningu widać broń i wyszkolenie: mistrz ćwiczy dłuższe combo i szybsze ciosy niż nowicjusz
i krócej odpoczywa.

Na razie żaden NPC w świecie nie dostaje nowego planu dnia (P3). Plan dnia czeka na nową treść moda,
a do tego czasu przypisują go tylko scenariusze testowe.

## Poza zakresem

- Sparing: dwóch NPC walczących ze sobą naprawdę, przez AI walki, bez obrażeń i bez reakcji innych
  NPC, albo trening z bohaterem. To osobny pomysł w `roadmap.md` (decyzja właściciela przy P1).
- Manekin lub inny cel treningowy: nowe obiekty i modele w świecie.
- Nowe animacje. Trening używa animacji walki, które NPC ma już w grze z modem, w tym sierpowych
  z 004.
- Zmiany walki NPC: AI walki (001), obrażenia (002), obrona.
- Wpływ treningu na statystyki lub talent NPC.
- Orkowie, jaszczuroludzie i inne modele niż ludzie.
- Trening bohatera i nowe sterowanie gracza.
- Zmiana planów dnia NPC w świecie, w tym 26 postaci z obecnym treningiem z mieczem (P3). Zrobi to
  przyszła treść moda.
- Walka dystansowa i magia. Trening magii zostaje jak w oryginale. Trening strzelecki to osobny
  pomysł w `roadmap.md`.
- Nowe kwestie i okrzyki treningowe (głosy, konstytucja, zasada 6). Dźwięki zamachu z animacji ciosów
  zostają.

## Scenariusze gracza

1. **Gdy** gracz przechodzi obok NPC, któremu autor moda dał nowy trening, **wtedy** widzi, jak NPC
   w miejscu wyprowadza pojedyncze ciosy, combo do przodu i serie z boków, przerywane krótszymi
   i dłuższymi przerwami. Dwóch ćwiczących obok siebie nie porusza się w jednym rytmie.
2. **Gdy** obok siebie ćwiczą mistrz i nowicjusz z tą samą bronią, **wtedy** mistrz wyprowadza
   dłuższe combo i szybsze ciosy, tak jak w walce (001 W1), i krócej odpoczywa między seriami.
3. **Gdy** ćwiczy NPC z bronią dwuręczną, **wtedy** ćwiczy ciosami broni dwuręcznej. **Gdy** autor
   przypisał mu trening pięściami albo NPC nie ma broni białej, **wtedy** ćwiczy pięściami: proste,
   combo i sierpowe z obu stron.
4. **Gdy** gracz stanie tuż przed ćwiczącym albo przebiegnie przez plac, **wtedy** ciosy go nie
   ranią, nie zaczyna się walka i nikt nie reaguje jak na atak.
5. **Gdy** gracz zagada do ćwiczącego, **wtedy** NPC przerywa trening i rozmawia jak dotąd, a po
   rozmowie wraca do ćwiczeń.
6. **Gdy** gracz zaatakuje ćwiczącego albo w pobliżu pojawi się wróg, **wtedy** NPC reaguje jak każdy
   NPC w planie dnia, np. walczy albo ucieka.
7. **Gdy** kończy się pora treningu, **wtedy** NPC chowa broń i przechodzi do następnego punktu planu
   dnia.

## Wymagania

- **W1:** Skrypty mogą przypisać NPC plan dnia `Practice_Melee` tak samo jak inne plany dnia
  (godziny od i do, waypoint). Przy przypisaniu autor wybiera wariant:
  - **bronią**: NPC ćwiczy swoją bronią białą (jednoręczną albo dwuręczną), a gdy jej nie ma,
    pięściami. NPC nie dostaje broni do treningu;
  - **pięściami**: NPC ćwiczy pięściami, także gdy ma broń.

  NPC idzie na swoje miejsce, dobywa broni albo pięści i ćwiczy do końca pory treningu.
- **W2:** Trening składa się z ciosów, których NPC używa w walce tą bronią:
  - cios do przodu i combo do przodu,
  - atak z lewej i atak z prawej,
  - serie mieszane, np. bok i potem przód, albo lewy i prawy.

  Długość combo do przodu i szybkość ciosów wynikają z talentu NPC tak samo jak w walce (001 W1).
  Pięściami ataki z boków to sierpowe z 004, a combo do przodu ma 2 ciosy.

  Między seriami NPC czasem blokuje albo odskakuje, tak jak w walce tą bronią albo pięściami
  (walka z cieniem). To rzadkie przerywniki: wartość startowa to jeden blok albo odskok mniej więcej
  na 5 serii ciosów, do strojenia w grze (W4). Oryginalnych kata z mieczem nowy trening nie używa.
- **W3:** Trening nie ma stałego cyklu:
  - kolejność rodzajów ciosów i długość serii są losowe, w granicach W2;
  - przerwy między seriami są losowe, a ich zakres zależy od talentu NPC w broni, którą ćwiczy;
  - co kilka serii (wartość startowa: co 4 do 8) NPC robi dłuższy odpoczynek z bronią w ręku, taki
    sam dla każdego talentu;
  - dwóch NPC, którzy zaczynają trening w tej samej chwili, nie uderza w tych samych momentach.

  Wartości startowe, do strojenia w grze (W4):

  | Talent | Przerwa między seriami | Dłuższy odpoczynek |
  |---|---|---|
  | nowicjusz (poniżej 30%) | 2–5 s | 6–10 s |
  | wojownik (30–59%) | 1–3,5 s | 6–10 s |
  | mistrz (60% i więcej) | 0,5–2 s | 6–10 s |

  Pięści nie mają talentu, więc w treningu pięściami NPC ma przerwy wojownika.
- **W4:** Proporcje rodzajów ciosów, częstość bloków i odskoków, zakres przerw i długość serii autor
  moda ustawia w skryptach, bez zmian w silniku. Ustawienia mogą się różnić między NPC.
- **W5:** NPC ćwiczy w miejscu. Po każdej serii wraca na swój waypoint i zwraca się tak jak on, więc
  każdą serię zaczyna najwyżej 0,75 m od waypointu. W trakcie serii ciosy przesuwają go tak jak w walce,
  ale żaden ruch nie zaczyna się dalej niż 3,5 m od waypointu.
  - Zmienione 2026-11-05 przy Z6 (decyzja właściciela): wcześniej NPC nie oddalał się o więcej niż
    1,5 m. Dziennik z Z4 pokazał, że combo 4 ciosów mistrza 1H przesuwa postać o około 2,8 m. Właściciel
    wybrał pełne combo z powrotem po serii zamiast krótszych serii albo odskoku przed combo. Próg początku
    serii najpierw wynosił 0,5 m. Powrót przez `AI_GotoWP` kończy się jednak 20-60 cm od waypointu
    (tolerancja dojścia w silniku), a w przebiegu Z6 seria zaczynała się do 53 cm od niego, więc właściciel
    wybrał próg 0,6 m. W przebiegu Z7 postacie z mieczem 2H zaczynały serię do 68 cm od waypointu (silnik
    kończy dojście około 60 cm od punktu, a dochodzi obrót), więc właściciel podniósł próg do 0,75 m.
- **W6:** Ciosy treningowe nikogo nie ranią: ani bohatera, ani NPC, ani zwierząt. Nie liczą się jako
  atak, więc nie zaczynają walki i nie wywołują reakcji świadków. Ćwiczący nie celuje w nikogo ani nie
  odwraca się w stronę bohatera.
- **W7:** Ćwiczący reaguje na otoczenie tak jak NPC w obecnym treningu z mieczem: rozmowa z bohaterem,
  dobyta broń, atak, wróg w pobliżu. Po rozmowie i po zakończonym zagrożeniu wraca do treningu.
- **W8:** Na końcu pory treningu NPC chowa broń przed przejściem do następnego punktu planu dnia,
  także gdy pora kończy się w trakcie serii.
- **W9:** Ciosy, bloki i odskoki z treningu trafiają do dziennika walki z 003 z rodzajem ruchu,
  kierunkiem, numerem w serii i czasem, oznaczone jako treningowe. Dzięki temu scenariusz testowy
  policzy repertuar, przerwy, odległość od miejsca i brak obrażeń.
- **W10:** Bez moda Gothic 2.5 NPC ćwiczą jak w oryginale, a silnik zachowuje się jak dotąd.
- **W11:** Zapis zrobiony w trakcie treningu wczytuje się, a NPC dalej ćwiczy. Zapisy z poprzednich
  wersji moda się wczytują.

## Kryteria akceptacji

Wspólne przygotowanie (P0): mod zbudowany z repozytorium, gra uruchamiana przez `tools/test.ps1`
(scenariusze z `tests/005/`), dla kryteriów ręcznych z `-Manual`. Czas gry przyspieszony przez
`ztimer multiplyer`, dziennik walki włączony.

- [x] **K1** (W1, W2, W3, W9): Repertuar i losowość bronią jednoręczną.
  - Kroki: scenariusz automatyczny. `insert` NPC z bronią jednoręczną i talentem mistrza, przypisanie
    mu `Practice_Melee` w miejscu wstawienia, 10 minut czasu gry, raport z dziennika walki.
  - Oczekiwane:
    - każdy rodzaj ciosu z W2 występuje co najmniej 3 razy;
    - combo do przodu mają różne długości, od 1 do 4 ciosów;
    - są bloki i odskoki, a razem jest ich od 1 na 10 do 1 na 3 serie ciosów (wartość startowa
      z W2 to 1 na 5);
    - przerwy między seriami pokrywają zakres mistrza z W3: najkrótsza leży w dolnej, a najdłuższa
      w górnej ćwiartce zakresu;
    - są dłuższe odpoczynki (6–10 s), od 1 na 8 do 1 na 4 serie;
    - kolejność rodzajów serii nie jest stałym cyklem: raport nie znajduje okresu krótszego niż
      10 serii.
- [x] **K2** (W2, W3): Talent i brak synchronizacji.
  - Kroki: scenariusz automatyczny. Dwóch NPC z bronią dwuręczną obok siebie: nowicjusz (talent poniżej
    30%) i mistrz (60% i więcej). Obaj dostają `Practice_Melee` w tej samej chwili, 10 minut czasu
    gry. Potem to samo w `-Manual`, a człowiek patrzy na obu.
  - Oczekiwane: combo nowicjusza ma najwyżej 2 ciosy, a mistrza do 4 (001 W1). Czas od startu ciosu
    do trafienia jest u mistrza krótszy, tak jak w walce. Przerwy między seriami mieszczą się
    w zakresach z W3, a mediana przerw mistrza jest krótsza niż nowicjusza. Mniej niż 20% ciosów obu
    NPC zaczyna się w odstępie poniżej 0,2 s od siebie. Ocena człowieka: obaj nie ruszają się
    w jednym rytmie, a mistrza da się rozpoznać.
- [x] **K3** (W1, W2): Trening pięściami.
  - Kroki: scenariusz automatyczny jak w K1, w trzech przebiegach: NPC z bronią jednoręczną
    w wariancie pięściami, NPC bez broni białej w wariancie bronią i NPC z bronią w wariancie bronią
    (kontrola).
  - Oczekiwane: w pierwszych dwóch przebiegach NPC ma w rękach tylko pięści, a dziennik ma ciosy do
    przodu, combo dwuciosowe i sierpowe z obu stron (004), także w seriach. NPC bez broni nie ma
    po treningu nowych przedmiotów w ekwipunku. W trzecim przebiegu NPC ćwiczy swoją bronią.
- [x] **K4** (W4): Ustawienia ze skryptów.
  - Kroki: scenariusz automatyczny jak w K1 z lokalnymi ustawieniami testowymi: tylko ataki z lewej
    i stała przerwa 2 s.
  - Oczekiwane: dziennik ma tylko ataki z lewej, a przerwy wynoszą 2 s ± 0,2 s. Silnik nie był
    przebudowywany.
- [x] **K5** (W5): Trening w miejscu.
  - Kroki: przebiegi z K1, K2 i K3.
  - Oczekiwane: każda seria zaczyna się najwyżej 0,75 m od waypointu, a NPC jest zwrócony tak jak
    waypoint (odchylenie do 15°). Żaden ruch nie zaczyna się dalej niż 3,5 m od waypointu.
  - Zmienione 2026-11-05 przy Z6 razem z W5 (wcześniej 1,5 m dla każdego ciosu).
- [x] **K6** (W6): Trening nikogo nie rani.
  - Kroki: scenariusz automatyczny. Bohater bez trybu nieśmiertelności stoi pół metra przed
    ćwiczącym przez 3 minuty czasu gry. Potem w tym samym miejscu staje wstawiony mieszczanin, a na
    koniec owca.
  - Oczekiwane: dziennik nie ma trafień ani obrażeń, życie bohatera, mieszczanina i owcy się nie
    zmienia, nikt nie zaczyna walki ani nie ucieka. Ćwiczący nie obraca się w stronę bohatera.
  - Zmienione 2026-11-06 przy Z9 (decyzja właściciela): mieszczanin i owca stają obok ćwiczącego,
    1-3 m od niego, a nie dokładnie w miejscu bohatera. Polecenie `insert` stawia postać 2 m przed
    bohaterem, a obrotu bohatera scenariusz nie ustawia. Obrażenia wręcz trafiają w grze tylko cel
    atakującego, a trening czyści cel i kończy klatkę trafienia przed sprawdzeniem celu, więc
    dokładne miejsce postronnych nic nie zmienia. Bohater stoi dokładnie pół metra przed
    ćwiczącym (`goto pos` z pozycji i kierunku waypointu, polecenie `wp info`).
- [x] **K7** (W7): Rozmowa i reakcje.
  - Kroki: `-Manual`, scenariusz wstawia ćwiczącego jak w K1. Zagadaj do niego i zakończ rozmowę.
    Potem dobądź broni obok niego, schowaj ją, a na koniec uderz go. Dla porównania to samo przy NPC
    z obecnym treningiem z mieczem.
  - Oczekiwane: przy rozmowie, dobytej broni i ataku NPC zachowuje się jak NPC w obecnym treningu
    z mieczem. Po rozmowie wraca do treningu w ciągu kilku sekund.
- [x] **K8** (W8): Koniec pory treningu.
  - Kroki: scenariusz automatyczny. NPC z planem dnia: trening, a po nim stanie w innym miejscu.
    `set time` na dwie minuty przed końcem treningu, potem czekanie do 5 minut po końcu.
  - Oczekiwane: dziennik nie ma ciosów treningowych później niż 3 s po końcu pory treningu. NPC
    chowa broń i idzie na miejsce z następnego punktu planu dnia.
- [x] **K9** (W10): Bez moda bez zmian, regresja walki.
  - Kroki: scenariusz bez moda (`# mod: off`): jeden z NPC z obecnym treningiem z mieczem w porze
    treningu, seria zrzutów. Potem zestawy `tools/test.ps1 -Spec 001` i `-Spec 004`.
  - Oczekiwane: NPC bez moda ćwiczy oryginalne kata. Zestawy 001 i 004 przechodzą bez zmiany
    oczekiwań.
- [x] **K10** (W11): Zapisy.
  - Kroki: zapis w trakcie serii treningowej, wczytany ponownie. Potem zapis z poprzedniej wersji
    moda wczytany w nowej.
  - Oczekiwane: oba zapisy się wczytują. Po wczytaniu pierwszego NPC dalej ćwiczy na swoim miejscu.
- [x] **K11** (P3): Świat bez zmian.
  - Kroki: scenariusz automatyczny z modem, nowa gra. `goto waypoint` do jednego z NPC z obecnym
    treningiem z mieczem w jego porze treningu, seria zrzutów i dziennik walki.
  - Oczekiwane: NPC ćwiczy oryginalne kata, a dziennik nie ma ciosów treningowych.

## Wpływ na zapisy gry

Funkcja nie powinna dodawać nowego stanu do zapisu. Nowy plan dnia to nowe symbole skryptów, więc
trafia do nowych plików i nie przesuwa numerów istniejących symboli (ADR 0005). Zapisy z poprzednich
wersji moda się wczytają.

Plany dnia NPC w świecie się nie zmieniają (P3). Plan dnia jest jednak częścią zapisu, więc gdy
przyszła treść da nowy trening istniejącym NPC, zmiana zadziała dopiero od nowej gry albo od chwili,
w której skrypty wymienią tym NPC plan dnia. Ta treść musi to uwzględnić (konstytucja, zasada 4).

## Zasoby i prawa

Brak nowych zasobów. Trening używa animacji z gry i animacji moda z 004. Nowy plan dnia to praca
moda na licencji GothicMOD (konstytucja, zasada 9).

## Pytania otwarte

- [x] **P1:** Czym ćwiczy NPC? Fakt ze skryptów: wszyscy 26 obecnych ćwiczących ma broń białą,
  21 jednoręczną i 5 dwuręczną. **Odpowiedź (2026-11-05):** autor wybiera wariant przy przypisaniu
  planu dnia: swoją bronią albo pięściami. NPC bez broni w wariancie bronią ćwiczy pięściami i nie
  dostaje maczugi. Właściciel rozważał zamiast tego sparing przez AI walki (prawdziwa walka bez
  obrażeń i bez reakcji innych NPC), ale to osobna funkcja. Najpierw statyczne ćwiczenia, różne dla
  broni i pięści, a potem może trening strzelecki. Oba pomysły są w `roadmap.md`. Zapisane w celu,
  „Poza zakresem”, scenariuszu 3, W1, W2 i K3.
- [x] **P2:** Czy trening to same ciosy, czy także inne ruchy walki: blok, odskok i oryginalne kata
  z mieczem jako rzadki przerywnik między seriami? **Odpowiedź (2026-11-05):** ciosy, a blok
  i odskok jako rzadkie przerywniki (walka z cieniem). Kata z oryginału zostają tylko w starym
  treningu. Zapisane w W2, W4, W9 i K1.
- [x] **P3:** Którzy NPC ćwiczą w nowy sposób? Fakt ze skryptów: obecny trening z mieczem ma 26
  postaci (16 paladynów, Wulfgar i 4 strażników, 2 najemników, Rethon, Bones i Babo).
  **Odpowiedź (2026-11-05):** na razie nikt. Nowy plan dnia jest dostępny dla skryptów i czeka na
  nową treść moda, a w grze przypisują go tylko scenariusze testowe. Zapisane w celu, „Poza
  zakresem”, scenariuszu 1, K10, K11 i „Wpływie na zapisy gry”.
- [x] **P4:** Jakie przerwy między seriami? **Odpowiedź (2026-11-05):** przerwy skracają się
  z talentem (mistrz odpoczywa krócej), a co kilka serii jest dłuższy odpoczynek, taki sam dla
  każdego. Wartości startowe są do strojenia w grze. Zapisane w W3, K1 i K2.

## Weryfikacja

<!-- Wypełniane po implementacji: kto, kiedy, na jakiej wersji, wynik dla każdego K. -->

**Przebiegi automatyczne (Claude, 2026-11-11, commit `d27d4c0b`, czyste drzewo).**
- **Zestawy:** `tools/test.ps1 -Spec 005`: 13 z 14 scenariuszy (przebiegi `20261111-1738*` do
  `-1803*`). Niezaliczony `K10b` to błąd miary: pierwszy ruch po wczytaniu zapisu z połowy combo był
  trzecim ciosem tej serii (113 cm od waypointu), a `fightlog.py` liczył go jako początek serii.
  Poprawka miary `ec993ac4` nie zmienia wyników pozostałych przebiegów, a po niej `K10a` i `K10b`
  przeszły (`20261111-1839*`, `-1840*`, commit `ec993ac4`).
- **Regresja (K9):** `-Spec 001` 17 z 17 i `-Spec 004` 11 z 11 (`20261111-1803*` do `-1836*`).
- **Zapisy:** `tools/dat.py prefix` względem `GOTHIC.DAT` sprzed 005 (`02ddcb93`): kod 0. Doszło
  180 nazwanych symboli na końcu, a nazwane symbole z wersji poprzedniej zachowały numery.
- **Katalogi wyników:** leżą w `gothic25/build/test-runs/` poza gitem, więc liczby, które
  rozstrzygają kryteria, są wpisane w tabeli.
- **Wersja kryteriów:** W5 i K5 (3,5 m w serii, początek serii do 0,75 m, decyzje właściciela przy
  Z6 i Z7) i K6 (postronni obok ćwiczącego, decyzja przy Z9).

**Sesje ręczne (Mateusz Tomanek, 2026-11-11, commit `ec993ac4`).**
- **Przebiegi:** `tools/test.ps1 -Manual` dla `reczne/K02-talent-2h`, `reczne/K07-rozmowa`
  i `reczne/K09-kata-bez-moda` (`20261111-205159`, `-205257`, `-205405`), katalogi
  w `build/test-runs/`.
- **Stan drzewa:** zmieniona tylko sekcja „Weryfikacja” w `spec.md` i nowy scenariusz ręczny
  `reczne/K09-kata-bez-moda`, bez zmian w silniku i skryptach.
- **Ocena właściciela:** według kroków K2, K7 i K9 wszystko wygląda w porządku. Obok oceny
  w tabeli są liczby z dziennika walki tych sesji.

| K | Wynik | Wersja | Kto |
|---|---|---|---|
| K1 | spełnione. `005/K01-mistrz-1h` (`20261111-173851`, 24 z 24), mistrz 1H przez 10 minut gry. Serie: prosty 26, combo 35, z lewej 19, z prawej 14, mieszane 19; combo 2, 3 i 4 (13, 10 i 12 razy). Blok albo odskok co 5,7 serii, przerwy 534-1986 ms (zakres mistrza 0,5-2 s), odpoczynek co 7,1 serii, najkrótszy okres ciągu serii 113 (bez cyklu) | `d27d4c0b` | Claude, automatycznie |
| K2 | spełnione. `005/K02-talent-2h` (`20261111-174403`, 17 z 17): combo nowicjusza 2, mistrza 4; trafienie ciosu do przodu u nowicjusza po 324 ms i więcej, u mistrza najwyżej po 216 ms; przerwy nowicjusza 2162-4984 ms, mistrza 512-1982 ms; ciosy razem z drugim 15,2% i 11,0% (próg 20%). Ocena właściciela w sesji `reczne/K02-talent-2h` (`20261111-205159`): obaj nie ruszają się w jednym rytmie, a mistrza da się rozpoznać. Dziennik tej sesji (24 s): nowicjusz same pojedyncze ciosy i przerwy 3,2-4,1 s, mistrz combo do 3 i przerwy 1,4-1,7 s, 0% ciosów razem | `d27d4c0b`, sesja `ec993ac4` | Claude, automatycznie; wygląd: Mateusz Tomanek |
| K3 | spełnione. `K03a` (`20261111-174914`, 10 z 10): z mieczem w wariancie pięściami tryb pięści, combo 2, sierpowe z lewej 10 i z prawej 19, 9 serii mieszanych. `K03b` (`-175054`, 10 z 10): bez broni pięści, combo 2, bez założonej broni i bez nowej maczugi (tę od `B_RefreshAtInsert` przy wstawieniu odliczamy). `K03c` (`-175236`, 6 z 6): kontrola z bronią, tryb broni, combo 4 | `d27d4c0b` | Claude, automatycznie |
| K4 | spełnione. `K04-profil-testowy` (`20261111-175419`, 9 z 9): profil 99 daje 53 ciosy z lewej, 0 innych ruchów, przerwy dokładnie 2000 ms, 0 odpoczynków. Silnik ten sam co w pozostałych przebiegach | `d27d4c0b` | Claude, automatycznie |
| K5 | spełnione (kryterium zmienione przy Z6 i Z7). Z `K01`-`K03c`: początek serii najdalej 53 cm (1H), 66 i 69 cm (2H), 39 i 35 cm (pięści); odchylenie od kierunku waypointu na początku serii 0°; najdalszy ruch 292 cm (1H) i 226 cm (2H) | `d27d4c0b` | Claude, automatycznie |
| K6 | spełnione (kryterium zmienione przy Z9). `K06-bez-obrazen` (`20261111-175602`, 8 z 8): bohater bez nieśmiertelności 70 cm przed waypointem ćwiczącego przez 3 minuty gry, potem mieszczanin i owca obok. 144 pudła `practice`, 0 trafień, życie bohatera, mieszczanina i owcy bez zmian, mieszczanin w swoim stanie, owca nie atakuje i nie ucieka, ćwiczący dalej ćwiczy, odchylenie do 12° | `d27d4c0b` | Claude, automatycznie |
| K7 | spełnione. Sesja `reczne/K07-rozmowa` (`20261111-205257`): strażnik 329 z nowym treningiem przy rozmowie, dobytej broni i ataku zachowuje się jak strażnik 330 ze starym, a po rozmowie wraca do treningu (ocena właściciela). Dziennik: 329 ćwiczy (9 ruchów, w tym blok, 8 pudeł `practice`, 0 trafień treningowych, początek serii do 37 cm). Po ciosie bohatera w strażnika 330 (t=47,6 s) 330 i 329 przechodzą w `ZS_ATTACK` (329 po 12 ms) i razem z 331 i Wulfgarem atakują bohatera. Dziennik śledzi 329 dopiero od jego pierwszego ruchu (t=29,9 s), więc rozmowy i dobytej broni w nim nie widać | `ec993ac4` | Mateusz Tomanek (gra), Claude (dziennik) |
| K8 | spełnione. `K08-koniec-pory` (`20261111-175935`, 6 z 6): 11 serii przed końcem pory, po zmianie stanu o 9:00 (`ZS_STAND_ARMSCROSSED`) 0 ruchów treningowych, broń schowana, postać przy `CENTRE_03` | `d27d4c0b` | Claude, automatycznie |
| K9 | spełnione. `K09-bez-moda` (`20261111-180027`): bez moda 0 ruchów treningowych. Regresja `-Spec 001` 17 z 17 i `-Spec 004` 11 z 11 bez zmiany oczekiwań. Zrzuty K09 nie pokazują strażników (kamera patrzy tam, gdzie bohater), więc kata ocenił właściciel w sesji `reczne/K09-kata-bez-moda` (`20261111-205405`, bez moda): strażnicy ćwiczą oryginalne kata z mieczem | `d27d4c0b`, sesja `ec993ac4` | Claude, automatycznie; wygląd: Mateusz Tomanek |
| K10 | spełnione. `K10a` (`20261111-183958`): zapis zaraz po drugim ciosie combo. `K10b` (`-184030`, 4 z 4): po wczytaniu postać dalej ćwiczy, 17 serii, początek serii do 53 cm, 0 trafień. `K10c` (`-180211`, 5 z 5, `d27d4c0b`): zapis z 0.1.0 się wczytuje, nowa postać ćwiczy (15 serii), strażnik 329 w tym zapisie ma stary trening | `ec993ac4` (K10a, K10b), `d27d4c0b` (K10c) | Claude, automatycznie |
| K11 | spełnione. `K11-swiat-bez-zmian` (`20261111-180310`, 4 z 4): z modem strażnicy 329, 330 i 331 są w `ZS_Practice_Sword`, dziennik nie ma ruchów treningowych | `d27d4c0b` | Claude, automatycznie |
