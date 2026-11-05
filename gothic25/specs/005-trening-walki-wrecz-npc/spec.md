# 005: Trening walki wręcz NPC

- **Status:** W realizacji
- **Utworzono:** 2026-11-05
- **Zmieniona:** 2026-11-05 przy Z6 (decyzje właściciela, ryzyko R2 planu): W5 i K5, próg odejścia od
  waypointu 3,5 m w trakcie serii i początek serii najwyżej 0,6 m od waypointu.
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
  każdą serię zaczyna najwyżej 0,6 m od waypointu. W trakcie serii ciosy przesuwają go tak jak w walce,
  ale żaden ruch nie zaczyna się dalej niż 3,5 m od waypointu.
  - Zmienione 2026-11-05 przy Z6 (decyzja właściciela): wcześniej NPC nie oddalał się o więcej niż
    1,5 m. Dziennik z Z4 pokazał, że combo 4 ciosów mistrza 1H przesuwa postać o około 2,8 m. Właściciel
    wybrał pełne combo z powrotem po serii zamiast krótszych serii albo odskoku przed combo. Próg początku
    serii najpierw wynosił 0,5 m. Powrót przez `AI_GotoWP` kończy się jednak 20-60 cm od waypointu
    (tolerancja dojścia w silniku), a w przebiegu Z6 seria zaczynała się do 53 cm od niego, więc właściciel
    wybrał próg 0,6 m.
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

- [ ] **K1** (W1, W2, W3, W9): Repertuar i losowość bronią jednoręczną.
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
- [ ] **K2** (W2, W3): Talent i brak synchronizacji.
  - Kroki: scenariusz automatyczny. Dwóch NPC z bronią dwuręczną obok siebie: nowicjusz (talent poniżej
    30%) i mistrz (60% i więcej). Obaj dostają `Practice_Melee` w tej samej chwili, 10 minut czasu
    gry. Potem to samo w `-Manual`, a człowiek patrzy na obu.
  - Oczekiwane: combo nowicjusza ma najwyżej 2 ciosy, a mistrza do 4 (001 W1). Czas od startu ciosu
    do trafienia jest u mistrza krótszy, tak jak w walce. Przerwy między seriami mieszczą się
    w zakresach z W3, a mediana przerw mistrza jest krótsza niż nowicjusza. Mniej niż 20% ciosów obu
    NPC zaczyna się w odstępie poniżej 0,2 s od siebie. Ocena człowieka: obaj nie ruszają się
    w jednym rytmie, a mistrza da się rozpoznać.
- [ ] **K3** (W1, W2): Trening pięściami.
  - Kroki: scenariusz automatyczny jak w K1, w trzech przebiegach: NPC z bronią jednoręczną
    w wariancie pięściami, NPC bez broni białej w wariancie bronią i NPC z bronią w wariancie bronią
    (kontrola).
  - Oczekiwane: w pierwszych dwóch przebiegach NPC ma w rękach tylko pięści, a dziennik ma ciosy do
    przodu, combo dwuciosowe i sierpowe z obu stron (004), także w seriach. NPC bez broni nie ma
    po treningu nowych przedmiotów w ekwipunku. W trzecim przebiegu NPC ćwiczy swoją bronią.
- [ ] **K4** (W4): Ustawienia ze skryptów.
  - Kroki: scenariusz automatyczny jak w K1 z lokalnymi ustawieniami testowymi: tylko ataki z lewej
    i stała przerwa 2 s.
  - Oczekiwane: dziennik ma tylko ataki z lewej, a przerwy wynoszą 2 s ± 0,2 s. Silnik nie był
    przebudowywany.
- [ ] **K5** (W5): Trening w miejscu.
  - Kroki: przebiegi z K1, K2 i K3.
  - Oczekiwane: każda seria zaczyna się najwyżej 0,6 m od waypointu, a NPC jest zwrócony tak jak
    waypoint (odchylenie do 15°). Żaden ruch nie zaczyna się dalej niż 3,5 m od waypointu.
  - Zmienione 2026-11-05 przy Z6 razem z W5 (wcześniej 1,5 m dla każdego ciosu).
- [ ] **K6** (W6): Trening nikogo nie rani.
  - Kroki: scenariusz automatyczny. Bohater bez trybu nieśmiertelności stoi pół metra przed
    ćwiczącym przez 3 minuty czasu gry. Potem w tym samym miejscu staje wstawiony mieszczanin, a na
    koniec owca.
  - Oczekiwane: dziennik nie ma trafień ani obrażeń, życie bohatera, mieszczanina i owcy się nie
    zmienia, nikt nie zaczyna walki ani nie ucieka. Ćwiczący nie obraca się w stronę bohatera.
- [ ] **K7** (W7): Rozmowa i reakcje.
  - Kroki: `-Manual`, scenariusz wstawia ćwiczącego jak w K1. Zagadaj do niego i zakończ rozmowę.
    Potem dobądź broni obok niego, schowaj ją, a na koniec uderz go. Dla porównania to samo przy NPC
    z obecnym treningiem z mieczem.
  - Oczekiwane: przy rozmowie, dobytej broni i ataku NPC zachowuje się jak NPC w obecnym treningu
    z mieczem. Po rozmowie wraca do treningu w ciągu kilku sekund.
- [ ] **K8** (W8): Koniec pory treningu.
  - Kroki: scenariusz automatyczny. NPC z planem dnia: trening, a po nim stanie w innym miejscu.
    `set time` na dwie minuty przed końcem treningu, potem czekanie do 5 minut po końcu.
  - Oczekiwane: dziennik nie ma ciosów treningowych później niż 3 s po końcu pory treningu. NPC
    chowa broń i idzie na miejsce z następnego punktu planu dnia.
- [ ] **K9** (W10): Bez moda bez zmian, regresja walki.
  - Kroki: scenariusz bez moda (`# mod: off`): jeden z NPC z obecnym treningiem z mieczem w porze
    treningu, seria zrzutów. Potem zestawy `tools/test.ps1 -Spec 001` i `-Spec 004`.
  - Oczekiwane: NPC bez moda ćwiczy oryginalne kata. Zestawy 001 i 004 przechodzą bez zmiany
    oczekiwań.
- [ ] **K10** (W11): Zapisy.
  - Kroki: zapis w trakcie serii treningowej, wczytany ponownie. Potem zapis z poprzedniej wersji
    moda wczytany w nowej.
  - Oczekiwane: oba zapisy się wczytują. Po wczytaniu pierwszego NPC dalej ćwiczy na swoim miejscu.
- [ ] **K11** (P3): Świat bez zmian.
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
