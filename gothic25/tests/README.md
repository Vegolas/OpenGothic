# Scenariusze testowe

Scenariusz przygotowuje w grze sytuację z kryterium akceptacji, a dziennik walki zapisuje, co się
wydarzyło. Z dziennika powstaje raport, który sprawdza oczekiwania zapisane w scenariuszu.
Specyfikacja: [003](../specs/003-scenariusze-testowe-i-dziennik-walki/spec.md). Kiedy wynik
przebiegu zalicza kryterium, opisuje [ADR 0004](../decisions/0004-zaliczanie-kryteriow-przez-scenariusze.md).

Ten plik opisuje format scenariusza, format dziennika i miary oczekiwań. To umowa między silnikiem
(wykonawca scenariuszy, dziennik) a narzędziami (`tools/test.ps1`, `tools/fightlog.py`). Pola
i polecenia można dopisywać. Zmiana znaczenia istniejących wymaga ponownego porównania raportu
z obserwacją w grze (003 K3).

## Katalogi

| Ścieżka | Co tam jest |
|---|---|
| `tests/NNN/Kn-nazwa.txt` | scenariusze dla kryterium `Kn` specyfikacji `NNN` |
| `build/test/profile/` | katalog roboczy gry przy testach: `Gothic.ini` tworzony od nowa przed każdym przebiegiem, zapisy z testów, `log.txt` ostatniego przebiegu |
| `build/test-runs/<data>-<czas>-NNN-nazwa[-nomod]/` | wyniki jednego przebiegu (niżej) |

`build/` jest poza gitem. Zapisy z testów leżą tylko w profilu testowym i nie mieszają się
z zapisami zwykłej gry.

Pliki w katalogu przebiegu:

| Plik | Kto zapisuje | Zawartość |
|---|---|---|
| `scenario.txt` | `test.ps1` | kopia użytego scenariusza |
| `meta.json` | `test.ps1` | commit, czy drzewo było czyste, z modem czy bez, argumenty gry |
| `scenario.json` | silnik | wynik scenariusza: `ok` albo `error`, numer linii, komunikat, czas gry |
| `fightlog.jsonl` | silnik | dziennik walki |
| `*.png` | silnik | zrzuty ekranu (`screenshot`) |
| `log.txt`, `crash.log` | `test.ps1` | kopie z profilu testowego |
| `report.md` | `fightlog.py` | raport i wynik oczekiwań |

## Format scenariusza

Plik tekstowy UTF-8, jedno polecenie w linii. Linie zaczynające się od `#` to komentarze, puste
linie są pomijane. Nazwy instancji, funkcji i poleceń nie rozróżniają wielkości liter.

Nagłówek w komentarzach na początku pliku:

```
# criterion: 001 K2
# timeout: 300
```

- `criterion`: kryterium, które scenariusz sprawdza. Może wystąpić kilka razy.
- `timeout`: limit czasu rzeczywistego całego przebiegu w sekundach. Domyślnie 600. Po nim
  `test.ps1` zamyka grę i zgłasza niepowodzenie.
- `save`: zapis wczytywany na starcie zamiast nowej gry, ścieżka względem `gothic25/`
  (np. `build/testsaves/001-K9-v0.1.0-pal230.sav` albo `build/test/profile/save_slot_1.sav`,
  zapis zrobiony przez wcześniejszy scenariusz zestawu).
- `mod: off`: scenariusz uruchamia się bez moda (np. „bez moda bez zmian”).

`test.ps1 -Spec NNN` uruchamia scenariusze z `tests/NNN/` w kolejności nazw plików. Scenariusz,
który wczytuje zapis innego scenariusza, musi mieć nazwę dalej w kolejności.

`cheat god`, `ztimer multiplyer` i dziennik walki nie są częścią zapisu gry. Scenariusz, który
wczytuje zapis, włącza je od nowa.

Polecenia wykonują się po kolei, gdy świat jest już wczytany (nowa gra albo zapis wskazany przy
starcie). Błąd w linii (nieznane polecenie, instancja, funkcja, waypoint, zły argument) kończy
scenariusz z numerem linii w `scenario.json` i w `log.txt`. W trybie automatycznym kończy też grę.

### Polecenia konsoli

Każde polecenie konsoli deweloperskiej (`F2`) działa w scenariuszu tak samo, np. `cheat god`,
`goto waypoint <WP>`, `goto pos <x> <y> <z>`, `insert <instancja>`, `set time <h> <min>`,
`ztimer multiplyer <mnożnik>`.

Nowe polecenia konsoli (działają też ręcznie po `F2`):

| Polecenie | Działanie |
|---|---|
| `call <funkcja> [argumenty...]` | wywołuje funkcję ze skryptów i wypisuje wynik (niżej) |
| `give <przedmiot> [ile]` | dodaje przedmiot do ekwipunku bohatera, domyślnie 1 sztukę |
| `equip <przedmiot>` | zakłada przedmiot na bohatera; gdy go nie ma, najpierw dodaje |
| `save game <slot>` | zapisuje grę do slotu jak z menu; w dialogu albo przerywniku zgłasza błąd |
| `screenshot <plik>` | zapisuje zrzut sceny 3D do PNG; ścieżka względna trafia do katalogu wyników |
| `toggle fightlog` | włącza albo wyłącza dziennik walki (w scenariuszu jest włączony od startu) |
| `immortal <instancja>` | postać nie traci życia (flaga `NPC_FLAG_IMMORTAL`); walka NPC z NPC trwa wtedy do końca scenariusza |
| `info told <kwestia>` | kwestia dialogowa (instancja `C_INFO`) liczy się jako przegadana z bohaterem; `info told DIA_Xardas_Hello` na początku scenariusza zatrzymuje powitanie Xardasa w nowej grze |
| `quit` | kończy grę |

Argumenty `call` dobierane są według typu parametru funkcji:

- `int`: liczba, nazwa stałej ze skryptów (`NPC_TALENT_1H`) albo nazwa instancji (wtedy numer
  jej symbolu, jak w `Hlp_GetNpc`),
- `float`: liczba,
- `string`: jedno słowo,
- `C_NPC`: `hero` albo nazwa instancji postaci.

Postać wskazana nazwą instancji to ostatnio dodana do świata postać tej instancji, więc po `insert`
to właśnie wstawiona. Liczba argumentów musi się zgadzać z funkcją. Na czas wywołania `self` to
bohater, a `other` to jego cel (bez celu też bohater). Funkcji zewnętrznych silnika
(np. `CreateInvItems`) nie da się wywołać. Do ekwipunku służą `give` i `equip`.

### Polecenia sterujące

| Polecenie | Działanie |
|---|---|
| `wait <sekundy>` | czeka podany czas gry; przy `ztimer multiplyer 2` trwa o połowę krócej |
| `wait <kto> <zdarzenie> [n] timeout <sekundy>` | czeka na zdarzenie walki postaci; po limicie czasu gry błąd |
| `expect <kto> <miara> <op> <wartość>` | oczekiwanie dla raportu; silnik je pomija |

`<kto>` to `hero` albo nazwa instancji. Przy czekaniu na zdarzenie liczy się każda postać tej
instancji. Zdarzenia pochodzą z dziennika walki, więc czekanie nie działa, gdy scenariusz go wyłączy
(`toggle fightlog`).

Zdarzenia do czekania liczą się od chwili rozpoczęcia czekania:

| Zdarzenie | Kiedy |
|---|---|
| `series` | postać zaczyna serię (pierwszy cios ruchu FAI z więcej niż jednym ciosem) |
| `series-hit n` | postać wyprowadza `n`-ty cios serii |
| `combo n` | postać wyprowadza `n`-ty cios combo do przodu (`combo 2` to pierwsze połączenie) |
| `down` | postać leży: upadek po odrzucie, nieprzytomność albo śmierć |
| `unconscious` | postać traci przytomność |
| `dead` | postać ginie |

### Przykład

```
# criterion: 001 K1
# timeout: 400
# Paladyn-mistrz atakuje nieśmiertelnego bohatera, przyspieszenie 2.
info told DIA_Xardas_Hello
cheat god
set time 12 0
goto waypoint NW_CITY_TO_FOREST_01
call B_RaiseFightTalent hero NPC_TALENT_1H 70
equip ItMw_1h_Pal_Sword
insert Pal_230_Ritter
call B_Attack Pal_230_Ritter hero 0 0
screenshot start.png
ztimer multiplyer 2
wait Pal_230_Ritter series timeout 60
wait 120
quit

expect Pal_230_Ritter combo.max == 4
expect Pal_230_Ritter series.master >= 1
```

(Waypoint jest tylko przykładem. Właściwe miejsca wybiera zadanie Z19 planu 003.)

Miejsce: scenariusze 001 walczą we wnętrzu wieży Xardasa, gdzie zaczyna się nowa gra. Xardas
atakuje wstawionych bandytów (w próbie zabił strażnika bramy zamiast pozwolić mu walczyć
z bohaterem), więc scenariusze usuwają go na początku: `call B_RemoveNpc NONE_100_Xardas`.
To samo z bandytą ze schodów: `call B_RemoveNpc BDT_1013_Bandit_L`.

Przyspieszenie: przy `ztimer multiplyer 2` NPC atakują częściej w przeliczeniu na minutę czasu gry
(w próbie K1: 58 zamiast 33 ciosów na minutę), ale udział rodzajów serii, długości combo i moment
łączenia się nie zmieniają. Scenariusze używają przyspieszenia 2. Liczb na minutę nie porównuj
między przebiegami z różnym przyspieszeniem.

Pora dnia: nowa gra zaczyna się rano. W próbie z 2026-10-30 paladyn wstawiony bez `set time 12 0`
nie zaatakował bohatera przez 60 s mimo `B_Attack`, a z tą linią zaatakował po pół sekundy.
Ustawiaj porę dnia na początku scenariusza, zanim wstawisz postacie.

## Dziennik walki

Plik `fightlog.jsonl`: JSON Lines, jedno zdarzenie w linii. Pierwsza linia to `meta`. Plik powstaje
w katalogu wyników (`-results`), a bez tej opcji w katalogu roboczym gry, i jest zakładany od nowa
przy pierwszym włączeniu dziennika w danym uruchomieniu gry. Dziennik obejmuje walkę wręcz (broń
biała i pięści) wszystkich postaci, także bohatera.

Teksty ze skryptów (np. imię) są w stronie kodowej gry, więc silnik zapisuje ich bajty spoza ASCII
jako `\u00XX`. `fightlog.py` odkodowuje je jako cp1250.

### Pola wspólne

| Pole | Typ | Znaczenie |
|---|---|---|
| `t` | int | czas gry w ms (`ztimer multiplyer` go skaluje) |
| `ev` | string | rodzaj zdarzenia: `meta`, `attack`, `result`, `break`, `state`, `marker` |
| `who` | string | instancja postaci, której dotyczy zdarzenie (np. `PAL_230_RITTER`) |
| `who_id` | int | numer postaci w tym dzienniku, od 1 w kolejności pojawienia się; odróżnia postacie tej samej instancji |
| `player` | bool | czy to bohater |

`marker` i `meta` nie mają pól `who`, `who_id` ani `player`.

### `meta`

| Pole | Znaczenie |
|---|---|
| `format` | wersja formatu dziennika, obecnie `1` |
| `world` | nazwa świata |
| `mod` | plik `.ini` moda albo `null` bez moda |

### `attack`: początek prawdziwego ciosu

Zapisywany tylko wtedy, gdy zaczyna się nowy cios (nowa animacja albo połączenie w oknie combo),
a nie przy każdym żądaniu ataku.

| Pole | Typ | Znaczenie |
|---|---|---|
| `n` | int | numer ciosu tej postaci w dzienniku, od 1 |
| `name` | string | imię postaci |
| `tgt`, `tgt_id` | string, int | cel; `null`, gdy brak |
| `tgt_down` | bool | czy cel leżał w chwili ciosu |
| `tactic` | int | styl walki (`fight_tactic`); raport podaje nazwę stałej `FAI_*` |
| `weapon` | string | `fist`, `1h`, `2h` |
| `talent` | int | poziom talentu tej broni: 0, 1, 2 |
| `talent_pct` | int | procent talentu tej broni |
| `dir` | string | `fwd`, `left`, `right`, `run` (atak w biegu), `finish` (dobicie leżącego) |
| `combo` | int | etap combo do przodu tego ciosu, od 1 |
| `link` | string | `new` (cios od postawy), `fwd` (połączenie do przodu), `side` (połączenie w bok) |
| `win_pct` | int | przy połączeniu: chwila w oknie combo poprzedniego ciosu, 0–100; inaczej `null` |
| `skip_ms` | int | przy połączeniu do przodu: ile ms animacji poprzedniego ciosu pominięto; inaczej `0` |
| `src` | string | `queue` (z serii FAI), `continue` (kontynuacja combo z `FA_MY_W_COMBO_<N>`), `player`, `other` (np. dobicie) |
| `series` | string | rodzaj ruchu FAI: `attack`, `side`, `front`, `triple`, `whirl`, `master`; `combo` przy `src: continue`; `null` dla gracza i `other` |
| `series_id` | int | numer serii tej postaci, od 1; `null` poza `src: queue` |
| `series_pos` | int | który to cios serii, od 1; pozycja przeskakuje, gdy silnik pominie cios (np. cel poza zasięgiem), a wychodzi poza `series_len`, gdy w kolejce została reszta przerwanej serii |
| `series_len` | int | ile ciosów ma ruch FAI |

### `result`: wynik ciosu

Zapisywany w chwili, w której cios mógł trafić (ramka trafienia animacji).

| Pole | Typ | Znaczenie |
|---|---|---|
| `n` | int | numer ciosu atakującego (pole `n` z `attack`) |
| `tgt`, `tgt_id` | string, int | cel; `null` przy pudle bez celu |
| `res` | string | `hit`, `block`, `jumpback`, `miss` |
| `why` | string | przy `miss`: `no_target`, `range`, `angle`, `down` (cel już leżał); inaczej `null` |
| `combo` | int | etap combo do przodu ciosu, od 1 |
| `dmg` | int | przy `hit`: obrażenia wyliczone przez grę; inaczej `0` |
| `hp_before`, `hp_after` | int | przy `hit`: życie celu przed i po (różni się od `dmg` np. przy `cheat god`); inaczej `0` |
| `stagger` | bool | czy cel się zachwiał |

Gdy cios powala cel, zdarzenie `state` z `unconscious` albo `dead` trafia do dziennika przed
`result` tego ciosu. Zachwianie i odrzut (`stumble`, `fly`) są zapisywane po nim.

### `break`: przerwanie serii albo combo

| Pole | Typ | Znaczenie |
|---|---|---|
| `what` | string | `series` albo `combo` |
| `why` | string | przyczyna (niżej) |
| `series`, `series_id`, `series_pos` | | przy `series`: rodzaj i numer serii oraz ile jej ciosów padło (`combo` i `null` dla kontynuacji combo); przy `combo`: `null`, `null` i etap combo, na którym się urwało |

Przyczyny:

| `why` | Kiedy |
|---|---|
| `hit` | postać dostała trafienie (kolejka czyszczona przy każdym niezablokowanym ciosie) |
| `target_down` | cel leży |
| `target_lost` | cel poza zasięgiem albo kątem przy `break_on_lost` (001 W6) |
| `defend` | mistrz przerywa serię, żeby się bronić (001 W5) |
| `block` | postać zaczyna blok w trakcie combo |
| `talent` | ostatni etap combo do przodu, dalsze ciosy do przodu usunięte (001 W4) |
| `no_window` | kolejny cios poza oknem combo albo animacja nie ma dalszego okna |

### `state`: stan postaci

| Pole | Znaczenie |
|---|---|
| `state` | `stumble` (zachwianie), `fly` (odrzut), `lie` (upadek po odrzucie), `unconscious`, `dead` |
| `by`, `by_id` | kto spowodował, jeśli wiadomo; inaczej `null` |

### `marker`: znacznik

| Pole | Znaczenie |
|---|---|
| `what` | `scenario_start`, `line`, `wait_done` (spełnione czekanie na zdarzenie), `save`, `screenshot`, `fightlog_on`, `fightlog_off`, `scenario_end` |
| `line` | numer linii scenariusza; `null` poza scenariuszem |
| `text` | treść polecenia albo komunikat |
| `file` | przy `save` i `screenshot`: plik |

## Oczekiwania

```
expect <kto> <miara> <op> <wartość>
```

- `<kto>`: `hero` albo nazwa instancji. Miara sumuje wszystkie postacie tej instancji.
- `<op>`: `==`, `!=`, `<`, `<=`, `>`, `>=`.
- `<wartość>`: liczba.

Miary liczą się z całego dziennika przebiegu:

| Miara | Znaczenie |
|---|---|
| `attacks` | liczba ciosów (`attack`) |
| `attacks.tgt_down` | ciosy w leżący cel |
| `res.<hit\|block\|jumpback\|miss>` | wyniki ciosów postaci |
| `res.miss.<why>` | pudła z daną przyczyną (`no_target`, `range`, `angle`, `down`) |
| `taken.<hit\|block\|jumpback>` | wyniki ciosów wymierzonych w postać |
| `combo.max` | najdłuższe combo do przodu (najwyższe `combo`) |
| `combo.count.<N>` | liczba combo do przodu, które skończyły się dokładnie na `N` ciosach |
| `series.<rodzaj>` | liczba serii danego rodzaju (`attack`, `side`, `front`, `triple`, `whirl`, `master`), liczona po różnych `series_id`; `series.combo` to liczba ciosów z kontynuacji combo |
| `series.multi` | liczba rozpoczętych serii z więcej niż jednym ciosem |
| `break.<why>` | liczba przerwań z daną przyczyną |
| `skip.max_ms`, `skip.avg_ms` | pominięte ms animacji przy połączeniach do przodu |
| `link.min_pct`, `link.avg_pct` | chwila połączenia w oknie combo, w % |
| `damage.stage.<N>.avg`, `damage.stage.<N>.count` | średnie obrażenia i liczba trafień na etapie combo `N` |
| `state.<stan>` | liczba zdarzeń `state` postaci |

Gdy miara nie ma danych (np. `skip.avg_ms` bez połączeń), oczekiwanie jest niezaliczone
z wartością „brak danych”. Liczniki (np. `series.triple`, `break.hit`) mają wtedy wartość 0.
Oczekiwanie wobec postaci, której nie ma w dzienniku, jest niezaliczone, tak samo jak nieznana
miara albo operator. Wychwytuje to literówki w scenariuszu.

Oczekiwania sprawdza `tools/fightlog.py check <katalog przebiegu>`. Dopisuje je do `report.md`
i kończy się kodem 1, gdy któreś jest niezaliczone albo scenariusz nie zakończył się wynikiem `ok`.
Cały przebieg jest zaliczony tylko wtedy, gdy oba warunki są spełnione.

## Uruchamianie

Uzupełni to zadanie Z20 planu 003, gdy `tools/test.ps1` będzie gotowe.
