# 001: Combosy NPC w walce wręcz

- **Status:** W realizacji
- **Utworzono:** 2026-10-28
- **Warstwa (wstępnie):** skrypty i silnik <!-- zasoby / skrypty / silnik -->

- **Powiązane:** [002: Skalowanie obrażeń w kombo](../002-skalowanie-obrazen-w-kombo/spec.md)
  (balans obu funkcji trzeba ustalać razem: premia za kolejne ciosy combo dotknie także NPC,
  jeśli 002 tak zdecyduje).

## Problem

Gracz, który nauczy się walki, ma do dyspozycji całe combo do przodu (do czterech ciosów u mistrza),
ataki z lewej i prawej oraz ich łączenie. NPC z tego repertuaru praktycznie nie korzystają:

- Żaden styl walki ludzi (tchórz, normalny, silny, mistrz) nie przewiduje serii wielociosowych.
  Mistrz miesza tylko pojedynczy cios z krótką serią „bok, potem przód”. Serie potrójne, wirujące
  i mistrzowskie zostały przygotowane przez twórców gry, ale ludzie ich nie używają. Korzystają z nich
  tylko orkowie i jaszczuroludzie, którzy walczą tym samym stylem (seria boczna i potrójna).
- Nawet gdyby NPC wybrał serię kilku ciosów do przodu, w obecnym silniku każdy kolejny cios
  zaczyna się od nowa, jako pierwszy cios combo. Mistrz miecza wygląda więc w walce jak nowicjusz,
  który powtarza w kółko to samo uderzenie.

Skutek dla gracza: walka z Ravenem, paladynem czy najemnikiem mistrzem niewiele różni się od walki
z byle bandytą. Wyższy talent przeciwnika widać tylko w liczbach (trafienia krytyczne), a nie w tym,
jak przeciwnik walczy.

## Cel

NPC walczą wręcz tym samym repertuarem co gracz: wyprowadzają pełne combo do przodu (tak długie,
jak pozwala ich talent), ataki boczne i serie mieszane. Częstość i długość serii zależą od stylu
walki NPC, więc mistrza da się rozpoznać po samym sposobie walki.

## Poza zakresem

- Zmiana obrażeń zadawanych przez kolejne ciosy combo. To jest specyfikacja 002.
- Nowe animacje i zmiana tempa istniejących animacji ataku.
- Walka dystansowa i magia.
- Zmiana sterowania i combo gracza.
- Zmiana talentów i statystyk NPC (kto jest mistrzem, a kto nowicjuszem).
- Zmiana obrony NPC (kiedy blokuje, kiedy odskakuje), z wyjątkiem obrony w trakcie serii (W5).
- Zwierzęta i potwory walczące własnymi atakami (wilki, ścierwojady, trolle itd.).

## Scenariusze gracza

1. **Gdy** gracz walczy z paladynem, który jest mistrzem broni jednoręcznej, **i** stoi w jego
   zasięgu, **wtedy** paladyn co jakiś czas wyprowadza pełne czterociosowe combo: każdy kolejny cios
   wychodzi płynnie z poprzedniego, tak jak u gracza z tym samym talentem.
2. **Gdy** gracz walczy z bandytą-wojownikiem (talent 30–59%) z bronią dwuręczną, **wtedy** jego
   combo do przodu kończy się po trzech ciosach, bo na tyle pozwala mu talent, nawet jeśli jego styl
   walki przewiduje dłuższą serię.
3. **Gdy** gracz walczy z tchórzliwym chłopem albo słabym bandytą, **wtedy** ten atakuje głównie
   pojedynczymi ciosami. Różnica między nim a mistrzem jest widoczna od pierwszych sekund walki.
4. **Gdy** gracz zablokuje cios z serii NPC, **wtedy** blok działa tak samo jak na cios gracza,
   a **gdy** trafi NPC w trakcie serii i go zachwieje, **wtedy** seria się urywa.
5. **Gdy** paladyni walczą z orkami w Górniczej Dolinie albo strażnik miejski z bandytą,
   **wtedy** obie strony korzystają z combosów także w walce NPC z NPC.
6. **Gdy** gracz uruchomi grę bez moda Gothic 2.5, **wtedy** NPC walczą tak jak dotąd.

## Wymagania

- **W1:** NPC walczący bronią jednoręczną, dwuręczną albo pięściami potrafi wyprowadzić combo do przodu
  o pełnej długości, na jaką pozwala jego talent. Każdy kolejny cios combo wychodzi z poprzedniego
  (NPC nie wraca do postawy i nie powtarza pierwszego ciosu). Długości combo do przodu wynikają
  z animacji gry i są takie same jak u gracza:

  | Broń | Nowicjusz (< 30%) | Wojownik (30–59%) | Mistrz (60%+) |
  |---|---|---|---|
  | jednoręczna | 2 ciosy | 4 ciosy | 4 ciosy |
  | dwuręczna | 2 ciosy | 3 ciosy | 4 ciosy |
  | orkowie i jaszczuroludzie (broń orkowa) | 2 ciosy | 2 ciosy | 2 ciosy |
  | pięści (ludzie i orkowie) | 2 ciosy | 2 ciosy | 2 ciosy |

  Walka na pięści podlega tym samym zasadom co walka bronią. Pięści nie mają ataków bocznych,
  więc ciosy boczne z serii są zwykłymi ciosami do przodu, jak dotąd.

- **W2:** NPC używa wszystkich rodzajów serii przewidzianych w grze: boczna (lewo, prawo),
  frontalna (bok, potem przód), potrójna (przód, prawo, lewo albo lewo, prawo, przód),
  wirująca (lewo, prawo, lewo, prawo) i mistrzowska (lewo, prawo i cztery ciosy do przodu).
  Do tego dochodzi kontynuacja combo do przodu: NPC, który wyprowadził cios do przodu, może go
  przedłużyć kolejnymi ciosami combo, tak jak opisali to twórcy gry w skryptach walki.
- **W3:** Repertuar serii i ich częstość zależą od stylu walki NPC:

  | Styl | Repertuar |
  |---|---|
  | tchórz | bez zmian: pojedyncze ciosy |
  | normalny | pojedynczy cios, seria boczna, seria frontalna |
  | silny | jak normalny oraz seria potrójna i kontynuacja combo do przodu |
  | mistrz | wszystkie serie, w tym wirująca i mistrzowska, oraz kontynuacja combo do przodu; mniej więcej co drugi atak to seria |
  | orkowie (wojownik, szaman, nieumarły ork) i jaszczuroludzie | dotychczasowy zestaw (pojedynczy cios, seria boczna, potrójna) oraz kontynuacja combo do przodu; ciosy serii łączą się płynnie |
  | elita orków (w tym pułkownicy) | wszystkie serie, jak mistrz u ludzi |

  Szkielety walczą stylami ludzi, więc dostają repertuar swojego stylu z tej tabeli.
  Combo do przodu orków i jaszczuroludzi ma 2 ciosy, więc ich serie kończą się najpóźniej
  na drugim ciosie do przodu (W4).
- **W4:** Talent ogranicza serię: NPC nigdy nie wykona więcej ciosów do przodu z rzędu, niż wynosi
  długość jego combo (W1). Jeśli seria przewiduje ich więcej, kończy się na ostatnim ciosie combo.
- **W5:** Ciosy z serii NPC podlegają tym samym zasadom obrony co ciosy gracza: każdy da się
  zablokować albo uniknąć odskokiem. Trafienie, które zachwieje NPC, przerywa jego serię.
  W trakcie własnej serii NPC się nie broni, z wyjątkiem stylów mistrzowskich (mistrz u ludzi,
  elita orków): gdy przeciwnik zaczyna cios, mogą przerwać serię i zareagować tak samo jak poza
  serią (blok, odskok).
- **W6:** NPC nie zaczyna kolejnego ciosu serii, gdy przeciwnik leży (nieprzytomny albo martwy).
  Gdy przeciwnik w trakcie serii wyjdzie z zasięgu albo zajdzie NPC od tyłu, zachowanie zależy
  od stylu walki:
  - mistrz (ludzie) i elita orków kończą bieżący cios i przerywają serię, a potem podchodzą
    albo się obracają,
  - pozostałe style dokańczają serię do końca, także w powietrze. Odskok gracza daje wtedy okno
    na kontrę.
- **W7:** Kolejny cios serii NPC wypada w czasie, w którym gracz też mógłby go połączyć z poprzednim.
  NPC nie łączy ciosów szybciej, niż pozwala na to gra graczowi, i nigdy tak późno, żeby combo się
  urwało. Animacja ciosu gra prawie w całości, bo wcześniejsze połączenie pomija jej część i wygląda
  jak przyspieszenie. Style mistrzowskie (mistrz, elita orków) łączą ciosy losowo pod koniec okna,
  więc ich combo jest odrobinę szybsze (pomijają najwyżej ok. 0,2 s ciosu). Pozostałe style łączą
  ciosy na samym końcu okna.
- **W8:** Combosy działają także w walce NPC z NPC, w pojedynkach na arenie i w walkach
  „do nieprzytomności”.
- **W9:** Bez moda Gothic 2.5 NPC walczą tak samo jak w obecnej wersji silnika.
- **W10:** Zapis zrobiony w trakcie walki, także w środku serii NPC, wczytuje się, a NPC po wczytaniu
  walczy dalej (dokończy serię albo zacznie nową, ale nie zawiesza się).

## Kryteria akceptacji

Wspólne przygotowanie (P0): mod zbudowany i zainstalowany, gra uruchomiona przez `tools/run.ps1 -Dev`,
nowa gra. Konsola: `F2`. W konsoli `cheat god`, żeby bohater nie zginął. Do obserwacji pomaga
zwolnione tempo: `ztimer multiplyer 0.3`, powrót: `ztimer multiplyer 1`.

- [ ] **K1** (W1, W2): Mistrz jednoręczny wyprowadza pełne combo.
  - Kroki: P0, potem `insert Pal_230_Ritter` (paladyn, styl mistrza, talent 80%, miecz jednoręczny).
    Uderz go raz, żeby zaczął walczyć. Stój w jego zasięgu bez atakowania przez 2 minuty.
  - Oczekiwane: co najmniej raz pełne combo do przodu z czterech różnych ciosów bez powrotu do postawy
    między nimi (porównaj z combo bohatera z talentem 60%+ z K3) oraz co najmniej raz każda seria
    przydzielona stylowi mistrza w W3.
- [ ] **K2** (W1, W4): Mistrz dwuręczny ma combo z czterech ciosów, a wojownik dwuręczny z trzech.
  - Kroki: P0, `insert BDT_1088_Addon_Torwache` (styl mistrza, talent 85%, broń dwuręczna), 2 minuty
    jak w K1. Potem to samo z `insert BDT_1071_Addon_Ramon` (styl mistrza, talent 55%, broń dwuręczna).
  - Oczekiwane: pierwszy wykonuje combo do przodu z czterech ciosów, drugi nigdy więcej niż z trzech.
    Seria mistrzowska drugiego kończy się na trzecim ciosie do przodu.
- [ ] **K3** (W7): NPC nie łączy ciosów szybciej niż gracz.
  - Kroki: P0, `insert ch`, w rozmowie „Poziom, Punkty nauki i Gildia” daj sobie punkty nauki,
    potem „Umiejętności bojowe” → „Bronie jednoręczne” do 80%. Weź miecz paladyna (albo inny
    jednoręczny), wykonaj kilka razy pełne combo możliwie szybko i porównaj tempo z combo
    `Pal_230_Ritter` z K1 przy `ztimer multiplyer 0.3`.
  - Oczekiwane: kolejne ciosy NPC nie wychodzą wcześniej niż najszybsze połączenie, jakie udaje się
    wykonać graczowi. Combo paladyna i `BDT_1006_Bandit_H` (styl silny, K4) nie wyglądają na
    przyspieszone: w zwolnionym tempie każdy cios jest widoczny w całości, bez wyraźnego przeskoku.
    Combo paladyna jest najwyżej nieznacznie szybsze niż bandyty.
- [ ] **K4** (W3): Style walki są rozróżnialne.
  - Kroki: P0, po kolei `insert BDT_1013_Bandit_L` (tchórz), `insert BDT_1003_Bandit_M` (normalny),
    `insert BDT_1006_Bandit_H` (silny), każdego obserwuj 2 minuty jak w K1 i zanotuj, jakie serie
    wykonał.
  - Oczekiwane: każdy używa wyłącznie serii przydzielonych jego stylowi w W3. Tchórz nie wykonuje
    żadnej serii, normalny nie wykonuje serii potrójnej ani combo dłuższego niż jeden cios do przodu.
- [ ] **K5** (W5): Blok i trafienie przerywają serię jak u gracza.
  - Kroki: jak K1, ale blokuj ciosy z serii, a potem w trakcie serii zaatakuj paladyna. Powtórz
    z `insert BDT_1006_Bandit_H` (styl silny).
  - Oczekiwane: każdy cios z serii obu przeciwników da się zablokować. Paladyn na atak w trakcie
    swojej serii przynajmniej czasem odpowiada blokiem albo odskokiem. Bandyta się nie broni
    i da się go trafić. Trafienie, które zachwiało NPC, kończy jego serię (nie dokańcza jej
    po odzyskaniu równowagi).
- [ ] **K6** (W6): NPC nie bije leżącego przeciwnika.
  - Kroki: P0 bez `cheat god`, ustaw bohaterowi mało punktów życia (rozmowa z `ch` → „Całkowity reset
    postaci”), `insert Pal_230_Ritter`, uderz go i daj się powalić.
  - Oczekiwane: po upadku bohatera paladyn nie wyprowadza kolejnych ciosów serii.
- [ ] **K7** (W8): Combosy w walce NPC z NPC.
  - Kroki: P0, przy wejściu do miasta (przy strażnikach bramy) `insert BDT_1006_Bandit_H`
    i `insert Pal_230_Ritter` obok siebie. Obserwuj ich walkę.
  - Oczekiwane: paladyn wykonuje combo i serie tak jak w K1.
- [ ] **K8** (W9): Bez moda bez zmian.
  - Kroki: uruchom silnik z tej samej kompilacji bez moda (zwykły Gothic II: Noc Kruka, tryb
    deweloperski), powtórz K1.
  - Oczekiwane: paladyn walczy jak w poprzedniej wersji: nie ma serii potrójnych, wirujących
    ani mistrzowskich, a jego combo do przodu nie przekracza pierwszego ciosu.
- [ ] **K9** (W10): Zapis w trakcie serii.
  - Kroki: jak K1, zapisz grę z menu (w trybie deweloperskim `F5` zamraża kamerę zamiast szybkiego
    zapisu) w chwili, gdy paladyn jest w środku serii, i wczytaj ją.
    Wczytaj też zapis zrobiony w poprzedniej wersji moda.
  - Oczekiwane: oba zapisy się wczytują, a paladyn walczy dalej bez zawieszenia.
- [ ] **K10** (W3, W4): Orkowie i elita orków.
  - Kroki: P0, `insert OrcWarrior_Roam`, obserwuj 2 minuty jak w K1. Potem to samo
    z `insert OrcElite_Roam`.
  - Oczekiwane: wojownik używa pojedynczego ciosu, serii bocznej, potrójnej i combo do przodu z dwóch
    ciosów, a kolejne ciosy serii wychodzą płynnie, bez powrotu do postawy. Elita dodatkowo wykonuje
    serię wirującą i mistrzowską, która kończy się na drugim ciosie do przodu.
- [ ] **K11** (W6): Mistrz przerywa serię, gdy przeciwnik odskoczy, a niższe style nie.
  - Kroki: P0, `insert Pal_230_Ritter`, uderz go, a gdy zacznie serię, odskocz do tyłu poza zasięg
    po pierwszym ciosie. Powtórz kilka razy. Potem to samo z `insert BDT_1006_Bandit_H` (styl silny)
    i jego serią potrójną.
  - Oczekiwane: paladyn po odskoku nie wyprowadza kolejnych ciosów serii, tylko podchodzi. Bandyta
    dokańcza serię w powietrze, a w tym czasie da się go trafić.
- [ ] **K12** (W1): Combo na pięści.
  - Kroki: P0, `insert BDT_10027_Addon_Buddler` (styl silny, bez broni białej), obserwuj 2 minuty
    jak w K1.
  - Oczekiwane: kopacz co jakiś czas wyprowadza dwa różne ciosy pięścią połączone w combo,
    bez powrotu do postawy między nimi.

## Wpływ na zapisy gry

Funkcja nie powinna dodawać nowego stanu zapisywanego w grze. Stan walki NPC (bieżąca seria,
pozycja w combo) jest już zapisywany. Zapisy z wersji 0.1.0 muszą się wczytać (K9). Jeśli plan
wykaże, że potrzebny jest nowy stan, dostanie on wersjonowany zapis zgodnie z konstytucją, zasada 4.

## Zasoby i prawa

Brak. Funkcja korzysta wyłącznie z animacji i skryptów walki z oryginalnej gry, których gracz
używa we własnej kopii.

## Pytania otwarte

- [x] **P1:** Które serie dostaje który styl walki i jak często NPC wybiera serię zamiast pojedynczego
  ciosu? **Rozstrzygnięcie (2026-10-28):** stopniowanie według stylu, tabela w W3.
- [x] **P2:** Kogo obejmuje zmiana poza ludźmi? **Rozstrzygnięcie (2026-10-28):** szkielety
  automatycznie (walczą stylami ludzi). Orkowie i jaszczuroludzie walczą płynniej i dostają
  kontynuację combo do przodu, a elita orków dostaje pełny repertuar jak mistrz. Tabela w W3,
  kryterium K10.
- [x] **P3:** Co robi NPC, gdy w trakcie serii przeciwnik wyjdzie z zasięgu albo zajdzie go od tyłu?
  **Rozstrzygnięcie (2026-10-28):** zależy od stylu. Style mistrzowskie (mistrz u ludzi, elita orków)
  przerywają serię, pozostałe dokańczają ją w powietrze. Opis w W6, kryterium K11.
- [x] **P4:** Czy NPC może w trakcie własnej serii przerwać ją, żeby zablokować albo odskoczyć?
  **Rozstrzygnięcie (2026-10-28):** tylko style mistrzowskie (mistrz u ludzi, elita orków).
  Opis w W5, kryterium K5.
- [x] **P5:** Czy walka na pięści (bójki, pojedynki bez broni) też ma używać combo z dwóch ciosów?
  **Rozstrzygnięcie (2026-10-28):** tak, na tych samych zasadach. Opis w W1, kryterium K12.
- [x] **P6:** Jak szybko NPC łączy ciosy w granicach z W7? **Rozstrzygnięcie (2026-10-28):** losowo
  w obrębie okna, wyższe style średnio wcześniej. **Zmiana (2026-10-29, po pierwszym teście w grze):**
  silnik przy połączeniu przeskakuje animację do końca trafienia, więc wczesne łączenie mistrzów
  pomijało 40–60% każdego ciosu i wyglądało jak przyspieszone animacje. Teraz style mistrzowskie
  łączą ciosy losowo pod koniec okna, a pozostałe na samym końcu. Opis w W7, kryterium K3.
- [x] **P7:** Czy akceptujemy wyraźny wzrost trudności walk z mistrzami (Raven, paladyni, najemnicy
  Lee, łowcy smoków)? **Rozstrzygnięcie (2026-10-28):** akceptujemy. Po implementacji przechodzimy
  kluczowe walki fabularne, a ewentualne złagodzenia opisujemy w osobnej specyfikacji.

## Weryfikacja

<!-- Wypełniane po implementacji: kto, kiedy, na jakiej wersji, wynik dla każdego K. -->

**Zapis testowy do K9 (Z1, 2026-10-28):** mod 0.1.0 (commit `eda5289a`), nowa gra, walka
z `Pal_230_Ritter`, zapis z menu. Plik lokalny, poza gitem:
`gothic25/build/testsaves/001-K9-v0.1.0-pal230.sav`
(SHA-256 `a764cbba9a7a359bcc2774bf04c21657a36e23d9982ddea7ce578306ad3e1423`).

**Wstępne testy w grze (Mateusz Tomanek, 2026-10-29):** to nie jest przejście kroków K, tylko
pierwsze wrażenie. Na commicie `59b5222a` combosy działały, ale animacje wyglądały na przyspieszone
(zob. P6). Po zmianie tempa (commit `f4342807`) tempo wyglądało naturalnie, a log był czysty.

**Sprawdzenia bez gry (Claude, 2026-10-29, commit `834d85ae`, mod 0.2.0):**

- Silnik buduje się bez nowych ostrzeżeń, a skrypty kompilują się przez `gdc` 0.9.5.
- `Gothic25.mod` (`vdf.py list`) zawiera `FIGHT.DAT` i `GOTHIC.DAT`. Spakowany `FIGHT.DAT` ma
  `C_FIGHTAI.MOVE` jako `int[12]`, klasę `C_FIGHTAI_COMBO` i instancje `FA_COMBO_` dla stylów 4, 42,
  3, 12 i 13. Dla tchórza (2) instancji nie ma (W3).
- Oryginalny `FIGHT.DAT` z gry (`_work/Data/Scripts/_compiled`), z którego silnik korzysta bez moda,
  nie ma żadnej instancji `FA_COMBO_`, ma `C_FIGHTAI.MOVE` jako `int[6]`, a `FA_MY_W_COMBO_*` są
  puste. Nowy kod jest więc bez moda wyłączony. To wsparcie dla W9, ale nie zastępuje K8 w grze.
- Porównanie skompilowanych skryptów z wersją sprzed zmian: w `GOTHIC.DAT` jedyna zmiana kodu poza
  przesuniętymi numerami symboli to styl walki elity orków. W `FIGHT.DAT` zmieniły się tylko
  style 3, 4, 12, 13 i 42.

**Test ogólny w grze (Mateusz Tomanek, 2026-10-29, mod 0.2.0):** nowa gra, kilku wstawionych
przeciwników, ich combosy działały. Nie było to przejście kroków K, więc kryteria są oznaczone
najwyżej jako częściowo sprawdzone. Kod silnika i skryptów w 0.2.0 (`834d85ae`) jest taki sam jak
w `f4342807`, a zmieniły się tylko `mod.json`, `CHANGELOG.md` i `tasks.md`.

| K | Wynik | Wersja | Kto |
|---|---|---|---|
| K1, K2, K4, K10, K12 | częściowo: combosy kilku przeciwników działały, bez obserwacji według kroków (które serie, długość combo, który NPC) | 0.2.0 (`834d85ae`) | Mateusz Tomanek |
| K3 | częściowo: tempo combo oceniane w grze jako naturalne po zmianie z P6, bez porównania z combo bohatera przy `ztimer multiplyer 0.3` | `f4342807` | Mateusz Tomanek |
| K5, K6, K7, K11 | nie sprawdzone | | |
| K8 | nie sprawdzone w grze (dane bez moda sprawdzone wyżej) | | |
| K9 | nie sprawdzone: brak nowego zapisu z 0.2.0, zapis z 0.1.0 nie był wczytywany | | |
