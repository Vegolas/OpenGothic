# 002: Skalowanie obrażeń w kombo

- **Status:** Zrobiona
- **Utworzono:** 2026-10-28
- **Warstwa (wstępnie):** silnik i skrypty <!-- zasoby / skrypty / silnik -->

- **Powiązane:** [001: Combosy NPC w walce wręcz](../001-combosy-npc-w-walce-wrecz/spec.md)
  (NPC dostają mniejszą premię niż bohater, ale ich nowe combosy z 001 też będą zadawać więcej
  obrażeń; balans obu funkcji ustalamy razem).

## Problem

Każdy cios combo zadaje dziś takie same obrażenia. Kolejne ciosy combo mistrza trwają jednak dłużej
niż pierwszy, a ataki boczne są krótkie i można je szybko łączyć. W efekcie pełne combo to najmniej
opłacalny sposób walki dla postaci, która go się nauczyła. Więcej obrażeń na sekundę daje naprzemienne
lewo-prawo albo przerywanie animacji i ponawianie szybkiego ciosu.

Szacunek dla mistrza broni jednoręcznej w obecnej wersji moda, policzony z klatek animacji przy
idealnym wyczuciu czasu (do potwierdzenia pomiarem w K4):

| Sposób walki | Czas na jeden cios |
|---|---|
| pełne combo do przodu (4 ciosy) | ok. 0,63 s |
| naprzemienne ataki lewo-prawo | ok. 0,32 s |

Przy równych obrażeniach na cios lewo-prawo daje więc mniej więcej dwa razy więcej obrażeń na sekundę
niż combo, którego nauka kosztuje najwięcej punktów nauki. Gracz nie ma powodu z niego korzystać.

## Cel

Każdy kolejny cios combo do przodu zadaje więcej obrażeń niż poprzedni, tak że dla mistrza pełne
combo staje się najskuteczniejszym sposobem walki wręcz, a nie najsłabszym.

## Poza zakresem

- Zmiana animacji i tempa combo oraz ataków bocznych.
- Zmiana podstawowego wzoru obrażeń, obrażeń broni i ochrony pancerzy.
- Walka dystansowa i magia.
- Combosy NPC. To jest specyfikacja 001.
- Blokowanie technik przerywania animacji i osłabianie lewo-prawo. Ta specyfikacja tylko sprawia,
  że combo przebija lewo-prawo i powtarzanie pierwszego ciosu.
- Informacja dla gracza (dźwięk, efekt, liczby na ekranie) o mocniejszym ciosie poza trybem
  deweloperskim. Jeśli będzie potrzebna, to jako osobna funkcja.

## Scenariusze gracza

1. **Gdy** bohater z talentem mistrza broni jednoręcznej wyprowadza pełne combo do przodu, **wtedy**
   każdy kolejny cios zabiera przeciwnikowi wyraźnie więcej punktów życia niż poprzedni, a ostatni
   najwięcej.
2. **Gdy** ten sam bohater walczy na zmianę ciosami z lewej i prawej, **wtedy** każdy cios zadaje
   zwykłe obrażenia i w sumie pokonuje przeciwnika wolniej niż pełnymi combo.
3. **Gdy** nowicjusz (talent poniżej 30%) wyprowadza swoje dwuciosowe combo, **wtedy** drugi cios
   też jest mocniejszy, ale nowicjusz zyskuje na combo mniej niż wojownik, a wojownik mniej niż mistrz.
4. **Gdy** bohater uderza combo przeciwnika odpornego na dany typ obrażeń, **wtedy** przeciwnik
   pozostaje odporny, niezależnie od numeru ciosu.
5. **Gdy** gracz uruchomi grę bez moda Gothic 2.5, **wtedy** obrażenia są takie jak dotąd.

## Wymagania

- **W1:** Obrażenia ciosu z combo do przodu zależą od jego numeru w combo. Pierwszy cios zadaje tyle
  co dziś, a każdy kolejny co najmniej tyle co poprzedni.
- **W2:** Premię za każdy kolejny cios da się ustawić w danych moda bez przebudowy silnika, osobno:
  - dla broni jednoręcznej i dwuręcznej na każdym poziomie talentu (nowicjusz, wojownik, mistrz),
  - dla pięści (jedna tabela, bo pięści nie mają talentu),
  - dla bohatera i dla NPC.
- **W3:** Premia nie dotyczy ataków bocznych (także łączonych w serie lewo-prawo), ataku z biegu,
  dobijania, walki dystansowej ani magii. Ataki boczne nie dostają też żadnej kary: zadają takie
  obrażenia jak dziś.
- **W4:** Premia to procent od obrażeń końcowych: liczonych jak dziś (po odjęciu ochrony pancerza
  i po osłabieniu słabego ciosu przy niskim talencie), a przed zasadą obrażeń minimalnych.
  Odporny cel nadal nie traci życia. Przykład: siła z bronią 100, ochrona 80, premia 350%:
  20 obrażeń bez premii, 70 z premią.
- **W5:** Dla postaci z talentem mistrza (60%+) pełne combo do przodu zadaje na sekundę więcej obrażeń
  niż naprzemienne ataki boczne (lewo-prawo) i powtarzanie pierwszego ciosu, tą samą bronią przeciw
  temu samemu celowi, i to co najmniej o 20%. Przerywanie ciosu blokiem albo odskokiem nie jest
  częścią tego porównania. Wartości startowe premii bohatera-mistrza dla kolejnych ciosów combo to
  100%, 175%, 275%, 400% (średnio ok. 240% na cios). Ostateczne wartości ustala pomiar z K4.
- **W6:** Nowicjusz i wojownik dostają premię z własnych tabel (W2). Zysk z pełnego combo w porównaniu
  z lepszą z technik z W5 rośnie z talentem: u nowicjusza jest najmniejszy, u wojownika większy,
  u mistrza największy. Dotyczy to także wojownika z bronią jednoręczną, który ma combo z 4 ciosów
  jak mistrz.
- **W7:** Premia dotyczy bohatera i NPC, ale NPC mają mniejszą premię niż bohater. Wartość startowa
  dla NPC to połowa nadwyżki premii bohatera ponad 100%: przy wartościach startowych z W5 daje to
  ok. 100%, 140%, 190%, 250%.
- **W8:** W trybie deweloperskim da się odczytać, ile obrażeń zadał każdy cios wręcz, który to był cios
  combo i jaką premię dostał. Gracz bez trybu deweloperskiego tego nie widzi.
- **W9:** Bez moda Gothic 2.5 obrażenia są takie same jak w obecnej wersji silnika.
- **W10:** Zapisy gry z poprzednich wersji moda się wczytują. Po wczytaniu zapisu zrobionego w trakcie
  combo premia pierwszego ciosu zgadza się z tym, który to faktycznie cios combo (widać to po animacji):
  gra nie daje np. premii ostatniego ciosu ciosowi, który zaczyna nowe combo.

## Kryteria akceptacji

Wspólne przygotowanie (P0): mod zbudowany i zainstalowany, gra uruchomiona przez `tools/run.ps1 -Dev`,
nowa gra. Konsola: `F2`. W konsoli `cheat god`, potem `insert ch` i w rozmowie z nim: punkty nauki,
siła potrzebna do broni, „Umiejętności bojowe” → broń jednoręczna i dwuręczna do 80%. Bronie:
`insert ItMw_1h_Pal_Sword`, `insert ItMw_2h_Pal_Sword`. Cel testowy: NPC, który nie blokuje i nie
oddaje, z dużą liczbą punktów życia (przygotowany w planie i wstawiany przez `insert`).

- [x] **K1** (W1, W8): Kolejne ciosy combo zadają rosnące obrażenia.
  - Kroki: P0, miecz jednoręczny, trzy pełne combo do przodu w cel testowy, odczyt z W8.
  - Oczekiwane: obrażenia każdego ciosu odpowiadają premii z danych moda dla jego numeru,
    a pierwszy cios zadaje tyle samo, co przed zmianą (porównanie z K8).
- [x] **K2** (W2): Premię zmienia się bez przebudowy silnika.
  - Kroki: zmień w danych moda premię za trzeci cios broni jednoręcznej, przebuduj i zainstaluj
    tylko moda, powtórz K1.
  - Oczekiwane: zmienia się tylko obrażenie trzeciego ciosu, zgodnie z nową wartością.
- [x] **K3** (W3): Ataki spoza combo nie dostają premii.
  - Kroki: P0, w cel testowy: seria ataków bocznych, atak z biegu, strzał z łuku, zaklęcie,
    a na końcu dobicie powalonego człowieka (`insert BDT_1013_Bandit_L`, powal go i dobij).
  - Oczekiwane: odczyt z W8 nie pokazuje premii ani kary dla żadnego z tych ataków, także dla
    kolejnych ataków bocznych w długiej serii lewo-prawo.
- [x] **K4** (W5): Pełne combo mistrza daje najwięcej obrażeń na sekundę.
  - Kroki: P0, dla każdej broni (jednoręczna, dwuręczna) po 20 sekund nieprzerwanego ataku w cel testowy
    każdą techniką: pełne combo, powtarzanie pierwszego ciosu, lewo-prawo.
    Z odczytu W8 policz obrażenia na sekundę.
  - Oczekiwane: pełne combo ma wynik co najmniej o 20% wyższy od lepszej z dwóch pozostałych technik.
    Jeśli tak nie jest, wartości premii poprawiamy w danych moda i powtarzamy pomiar.
- [x] **K5** (W4): Odporność i ochrona działają jak dotąd.
  - Kroki: P0, pełne combo w `insert MagicGolem` (odporny na ostrze i obuch), potem w cel z wysoką
    ochroną przed ostrzem `insert StoneGolem`.
  - Oczekiwane: MagicGolem nie traci punktów życia żadnym ciosem. Na StoneGolemie każdy kolejny cios
    zadaje obrażenia, jakie zadałby bez premii, pomnożone przez premię (W4). Jeśli wynik jest mniejszy
    niż minimum obrażeń, cios zadaje minimum, tak jak dziś.
- [x] **K6** (W6): Zysk z combo rośnie z talentem.
  - Kroki: P0, ale w rozmowie z `ch` „Całkowity reset postaci” i broń jednoręczna do 10%.
    Zmierz obrażenia na sekundę jak w K4 dla pełnego combo, lewo-prawo i powtarzania pierwszego ciosu.
    Potem podnieś broń jednoręczną do 40% i powtórz pomiar.
  - Oczekiwane: względny zysk z pełnego combo nad lepszą z dwóch pozostałych technik jest u nowicjusza
    (10%) mniejszy niż u wojownika (40%), a u wojownika mniejszy niż u mistrza w K4.
- [x] **K7** (W7): Premia dotyczy właściwych postaci.
  - Kroki: P0, `insert Pal_230_Ritter`, pozwól mu wyprowadzić combo w bohatera (`cheat god` chroni
    przed śmiercią) i sprawdź odczyt W8 dla jego ciosów.
  - Oczekiwane: kolejne ciosy combo paladyna dostają premię z tabeli dla NPC, mniejszą niż premia
    bohatera za ten sam cios w K1.
- [x] **K8** (W9): Bez moda bez zmian.
  - Kroki: uruchom silnik z tej samej kompilacji bez moda (zwykły Gothic II: Noc Kruka), powtórz K1
    na dowolnym przeciwniku.
  - Oczekiwane: wszystkie ciosy combo zadają takie same obrażenia jak przed zmianą.
- [x] **K9** (W10): Zapisy.
  - Kroki: wczytaj zapis z wersji 0.1.0. Potem zapisz grę z menu w środku combo (w trybie
    deweloperskim `F5` zamraża kamerę zamiast szybkiego zapisu), wczytaj ją i od razu uderz.
  - Oczekiwane: oba zapisy się wczytują. Odczyt W8 dla pierwszego ciosu po wczytaniu pokazuje numer
    ciosu zgodny z animacją i premię zgodną z tym numerem.

## Wpływ na zapisy gry

Funkcja nie powinna dodawać nowego stanu zapisywanego w grze: numer ciosu w combo wynika z bieżącej
animacji, a ta jest już zapisywana. Zapisy z wersji 0.1.0 muszą się wczytać (K9). Jeśli plan wykaże,
że potrzebny jest nowy stan, dostanie on wersjonowany zapis zgodnie z konstytucją, zasada 4.

## Zasoby i prawa

Brak. Zmieniają się tylko zasady obrażeń i wartości w skryptach moda.

## Pytania otwarte

- [x] **P1:** Czy premia dotyczy też NPC? **Rozstrzygnięcie (2026-10-28):** tak, ale NPC mają osobno
  ustawianą, mniejszą premię. Opis w W2 i W7, kryterium K7.
- [x] **P2:** Co z atakami bocznymi? **Rozstrzygnięcie (2026-10-28):** bez premii i bez kary.
  Combo wygrywa wyłącznie premią, więc premie muszą być wysokie. Opis w W3, kryterium K3.
- [x] **P3:** W którym miejscu obliczenia działa premia? **Rozstrzygnięcie (2026-10-28):** po odjęciu
  ochrony i po osłabieniu słabego ciosu, przed zasadą obrażeń minimalnych. Opis w W4, kryterium K5.
- [x] **P4:** Jak duża ma być przewaga pełnego combo z W5? **Rozstrzygnięcie (2026-10-28):** co najmniej
  20%, wartości startowe premii bohatera 100/175/275/400%, korekta pomiarem. Opis w W5, kryterium K4.
- [x] **P5:** Czy premia zależy od talentu, czy tylko od numeru ciosu i rodzaju broni?
  **Rozstrzygnięcie (2026-10-28):** zależy od talentu: osobne tabele dla nowicjusza, wojownika
  i mistrza (pięści jedna tabela). Opis w W2 i W6, kryterium K6.
- [x] **P6:** Jakie techniki przerywania animacji gracze dziś stosują i które porównujemy w K4?
  **Rozstrzygnięcie (2026-10-28):** naprzemienne lewo-prawo i powtarzanie pierwszego ciosu.
  Przerywania blokiem i odskokiem nie porównujemy. Opis w W5, kryterium K4.
- [x] **P7:** Czy gracz ma dostać sygnał, że cios był mocniejszy (inny dźwięk, efekt trafienia)?
  **Rozstrzygnięcie (2026-10-28):** nie w tej specyfikacji. Jeśli tak, to jako osobna funkcja.

## Weryfikacja

<!-- Wypełniane po implementacji: kto, kiedy, na jakiej wersji, wynik dla każdego K. -->

**Przebiegi automatyczne (Claude, 2026-11-02, commit `75742e4c`, czyste drzewo).**
- **Zestawy:** `tools/test.ps1 -Spec 002` przeszło 12 z 12 scenariuszy, a zestaw `tests/001` jako regresja
  17 z 17.
- **Katalogi wyników:** leżą w `gothic25/build/test-runs/` poza gitem, więc liczby, które rozstrzygają
  kryteria, są wpisane w tabeli.
- **Cele testowe:** stoją, nie blokują i nie oddają: `TST_ComboDummy` (ochrona 0), `TST_ComboDummyArmored`
  (ochrona 200) i `TST_ComboDummyImmune` (odporny).
- **Siła ciosu paladyna:** bez premii mocny cios zadaje 235, słaby 23.

**Sesje ręczne (Mateusz Tomanek, 2026-11-02, commit `75742e4c`, drzewo zmienione tylko w tym pliku).**
- **Scenariusze:** `002/reczne/K04-mistrz` i `002/reczne/K06-nowicjusz-wojownik` z dziennikiem walki.
  Do tego dobicie, atak z biegu, combo bohatera bez moda i animacja po wczytaniu zapisu, ocenione w grze.
- **Broń dwuręczna:** grana postacią `PC_Rockefeller` (talent 100%), bo bohater ze scenariusza miał
  10 siły, a dwuręczny miecz paladyna wymaga 80. Scenariusz `K04-mistrz` podnosi teraz siłę bohatera.
- **Losowanie słabego ciosu:** bohater z mieczem paladyna zadaje mocnym ciosem 70, a słabym 7, i mocny
  cios wypada z szansą równą talentowi. Przy kilkunastu combo to losowanie przeważa nad różnicą między
  technikami: sekcja „Techniki bohatera” dała wojownikowi +77% i +255% w dwóch sesjach.
- **Przeliczenie bez losowania (Claude, poza raportem):** każdy zamach odcinka techniki, także chybiony,
  dostaje średnią siłę ciosu bohatera dla tej broni i talentu razy premię swojego etapu combo. Sumę
  dzielimy przez czas odcinków z raportu. Pudła liczą się jak trafienia, bo czas zamachu jest prawdziwy,
  a chybienie zależy od ustawienia. Przykład: w lewo-prawo nowicjusza cel po 3 trafieniach odsunął się
  po zatoczeniu i 15 z 18 zamachów chybiło z powodu zasięgu, a prawdziwy przeciwnik podchodzi z powrotem.
- **Decyzja właściciela (2026-11-02):** wyniki wystarczają, premii ani pomiaru dalej nie stroimy.
  Balans sprawdzą playtesty.

| K | Wynik | Wersja | Kto |
|---|---|---|---|
| K1 | spełnione. NPC: premie według etapu dokładnie z tablic NPC: paladyn (1H, mistrz) 100/140/190/250 (`002/K01a`), strażnik bramy (2H, mistrz) 100/140/190/250 (`K01b`), Ramon (2H, talent 55%, wojownik) 100/125/155 (`K01c`). Obrażenia paladyna 235/329/446/587. Bohater (`002/reczne`): mistrz 1H i 2H 100/175/275/400, wojownik 1H 100/150/200/260, nowicjusz 1H 100/130 (combo nowicjusza ma 2 ciosy). Rockefeller zadaje 1200/2100/3300/4800, czyli 1200 × premia. Pierwszy cios ma premię 100 jak bez moda (K8) | `75742e4c` | Claude, automatycznie; bohater: Mateusz Tomanek (gra), Claude (raport) |
| K2 | spełnione. W `ComboDamage.d` bez commita premia NPC-mistrza za trzeci cios broni jednoręcznej zmieniona ze 190 na 210, a `002/K01a` powtórzony. Mod skompilował i spakował `test.ps1`, silnika nie przebudowano (`Gothic2Notr.exe` z datą sprzed zmiany). Zmieniła się tylko premia trzeciego ciosu: 210, obrażenia 493 i 48 zamiast 446 i 43. Pozostałe etapy bez zmian: 100/140/250, 235/329/587. Zmiana cofnięta. Sprawdzone na tablicy NPC, bo ciosy bohatera wymagają gry; mechanizm odczytu jest wspólny | `75742e4c` ze zmianą w `ComboDamage.d` | Claude, automatycznie |
| K3 | spełnione. Ataki boczne bez premii i bez kary: bandyta ze stylem normalnym (`002/K03`, ciosy z lewej i prawej z premią 100) oraz ataki boczne paladyna łączone po ciosach combo (`002/K01a`, `bonus.dir.left` i `right` = 100). Ciosy boczne bohatera na każdym talencie z premią 100 (`002/reczne`). Dobicie: bohater dobił powalonego człowieka, dziennik nie ma dla dobicia wyniku z premią. Atak z biegu: ocena w grze. Strzał i zaklęcie sprawdzone w kodzie: premia działa tylko w gałęzi walki wręcz `DamageCalculator::damageValue`, a `Npc::comboDamage` daje 100 każdemu ciosowi poza combo do przodu | `75742e4c` | Claude, automatycznie; dobicie i atak z biegu: Mateusz Tomanek |
| K4 | spełnione. Przewaga pełnego combo mistrza nad lepszą z pozostałych technik (lewo-prawo) w przeliczeniu bez losowania: 1H +50%, 2H +72%. Raport bez przeliczenia: 1H +19,8% (2 z 5 czwartych ciosów wypadły słabe, 28 zamiast 280), 2H +56% (Rockefeller nie losuje, różnicę robią 3 pudła). Czas na cios 1H i 2H: combo 0,76 i 0,87 s, lewo-prawo 0,51 i 0,65 s, pierwszy cios 1,29 i 1,61 s. Premie bez zmian: 100/175/275/400 | `75742e4c` | Mateusz Tomanek (gra), Claude (przeliczenie) |
| K5 | spełnione. `MagicGolem`: 0 obrażeń przy każdym trafieniu (`002/K05a`). `StoneGolem`: mocny cios 135, słaby 13 (`K05b`); golemy oddają i przerywają combo, więc trafia je tylko pierwszy cios. Cel z ochroną 200 (`K05c`): mocny cios 35/49/66/87 na etapach 1–4 (35 × premia), słaby 3 z premią to 3/4/5/7, więc minimum podnosi pierwsze dwa do 5. Cel odporny (`K05d`): 0 obrażeń na każdym etapie przy premii do 250% | `75742e4c` | Claude, automatycznie |
| K6 | spełnione. Przewaga pełnego combo w przeliczeniu bez losowania (1H): nowicjusz +7%, wojownik +29% i +31% w dwóch sesjach, mistrz +50% (K4). U nowicjusza lepszą techniką jest lewo-prawo, liczone ze wszystkimi zamachami (opis wyżej). Raport bez przeliczenia: nowicjusz +27%, wojownik +77% i +255% | `75742e4c` | Mateusz Tomanek (gra), Claude (przeliczenie) |
| K7 | spełnione: premie NPC z tablicy NPC (K1) mniejsze niż premie bohatera za ten sam cios: 140/190/250 wobec 175/275/400 | `75742e4c` | Claude, automatycznie; bohater: Mateusz Tomanek (gra) |
| K8 | spełnione: bez moda (`002/K08`, `# mod: off`) każdy cios paladyna ma premię 100. Bez moda NPC nie łączą ciosów (001 W9), więc to sprawdza tylko pierwszy cios. Combo bohatera bez moda: ocena w grze | `75742e4c` | Claude, automatycznie; bohater: Mateusz Tomanek |
| K9 | spełnione. Zapis w chwili drugiego ciosu combo paladyna (`002/K09a`). Po wczytaniu (`K09b`) pierwsze trafienie to ten cios: etap 2, premia 140, 329 obrażeń, a potem łączenie dalej na etap 3 (190) i 4 (250). Zapis z 0.1.0 wczytuje się, a premie zgadzają się z tablicą (`K09c`). Animacja po wczytaniu: ocena w grze; zrzut `po-wczytaniu.png` jej nie rozstrzyga, bo paladyna zasłania bohater | `75742e4c` | Claude, automatycznie; animacja: Mateusz Tomanek |
