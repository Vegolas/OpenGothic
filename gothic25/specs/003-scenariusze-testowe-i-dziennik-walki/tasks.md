# Zadania 003: Scenariusze testowe i dziennik walki

- **Plan:** [plan.md](plan.md)
- **Utworzono:** 2026-10-29

Każde zadanie mieści się w jednym commicie. `[P]` oznacza zadanie, które można robić równolegle
z innymi `[P]` w tej samej fazie. W nawiasie: wymagania (W) i kryteria (K), które zadanie realizuje.

Zadania w silniku budujemy przez `tools/build-engine.ps1`. Plan nie zmienia serializacji
i nie dodaje funkcji zewnętrznych dla skryptów, więc nie ma dla nich osobnych zadań. Grupy T1–T6
z planu idą osobnymi commitami, żeby dało się je osobno zgłosić upstreamowi.

Zgoda na uruchamianie gry: dopóki Z20 nie wpisze zasady z W11 do `gothic25/CLAUDE.md`, każde
uruchomienie gry, także w trybie automatycznym, wymaga zgody właściciela projektu.

## Faza 1: Przygotowanie

- [x] **Z1** `gothic25/tests/README.md`: umowa między silnikiem a narzędziami, zanim powstanie kod.
      Spisać:
      - format scenariusza: nagłówki `# criterion:` i `# timeout:`, polecenia konsoli, `wait`
        na czas i na zdarzenie, `quit`, `expect`,
      - pola zdarzeń dziennika walki (`attack`, `result`, `break`, `state`, `marker`),
      - miary dla `expect`,
      - układ katalogów: `tests/NNN/`, profil testowy, katalog wyników.

      Instrukcję uruchamiania uzupełni Z20. (W1, W5, W9)

## Faza 2: Silnik, mechanizmy ogólne

- [x] **Z2** [P] T1: `-game:` przyjmuje ścieżkę bezwzględną.
      - Archiwa z `[FILES] VDF` są wtedy szukane w `<katalog .ini>/../Data/**`, a `.mod` o tej
        samej nazwie w folderze gry jest pomijany.
      - `-save` przyjmuje ścieżkę do pliku.
      - Sprawdzenie: względne `-game:` i `-save <n>` działają jak dotąd (zwykłe `tools/run.ps1`). (W2)
- [x] **Z3** [P] T2: opcja małego okna (`-window small`, okno Tempesta `Normal`, 800×600). Bez opcji
      okno jak dotąd. (W2)
- [x] **Z4** [P] T3: polecenie konsoli `call <funkcja> [argumenty...]`.
      - Własne dzielenie linii, argumenty według typu parametru (liczba, stała, nazwa instancji,
        `hero`, tekst).
      - Wywołanie przez `push_*` i `unsafe_call` z `self` i `other`, w `try/catch`.
      - Odrzucanie funkcji zewnętrznych, wypisanie wyniku albo błędu. (W3, K5)
- [x] **Z5** T3: polecenia `give`, `equip`, `save game <slot>` (z kontrolą dialogu i przerywnika)
      i `quit`. Po Z4, ten sam plik. (W3)
- [x] **Z6** T3 i T5: opcja `-results <katalog>` (zakładany przy pierwszym zapisie) i polecenie
      `screenshot <plik>` (sygnał w `Gothic`, obsługa w `MainWindow` jak `F11`, PNG, ścieżka
      względna do katalogu wyników). Po Z5, ten sam plik konsoli. (W3, W6, K7)

## Faza 3: Silnik, dziennik walki i wykonawca

- [x] **Z7** [P] `Pose::continueCombo` zapamiętuje wynik ostatniego żądania ciosu: nowy cios,
      połączenie do przodu, połączenie w bok, odrzucone, pominięte ms. Dostęp przez `MdlVisual`.
      Bez użycia w logice walki. (W4)
- [x] **Z8** [P] `FightAlgo`: przejściowe pola serii bez zapisu.
      - Rodzaj ruchu, numer serii, długość i pozycja.
      - Ustawiane w `nextFromQueue` przed skasowaniem `queueId`, przesuwane w `consumeAction`.
      - Bez użycia w logice walki. (W4)
- [x] **Z9** T6: dziennik walki (`game/fightlog.*`).
      - Zapis JSON Lines do katalogu wyników (bez `-results` do `fightlog/` w katalogu roboczym).
      - Polecenie `toggle fightlog` i zdarzenia `attack` z `Npc::doAttack`, tylko przy prawdziwym
        ciosie według Z7, z danymi serii z Z8.
      - API zdarzeń `marker` dla innych części silnika.
      - Tylko z `-devmode`. Przy wyłączonym dzienniku jedno sprawdzenie flagi.

      Po Z7 i Z8. (W4, W8, K12)
- [x] **Z10** T6: zdarzenia `result` i `state`.
      - `result`: pudło z przyczyną w `commitDamage`, blok i odskok w `takeDamage(Npc&, Bullet*)`,
        trafienie z obrażeniami i życiem przed i po.
      - `state`: zachwianie, odrzut, nieprzytomność, śmierć. (W4)
- [x] **Z11** T6: zdarzenia `break` z przyczyną w miejscach wywołań `onTakeHit`, `onBreakSeries`,
      `onEnemyPrehit`, `onClearTarget`, `dropForwardAttacks` (tylko przy zmianie kolejki) oraz przy
      braku okna combo. (W4)
- [x] **Z12** T4: wykonawca scenariuszy (`game/scenariorunner.*`), własna instancja Marvina.
      - `-scenario <plik>` sprawdzany przy starcie, z numerami linii. Linie `#` i `expect`
        są pomijane.
      - Start po pierwszym `onWorldLoaded`, krok w `MainWindow::tick` po `Gothic::tick`.
      - `wait <sekundy>` w czasie gry i `quit`.
      - Czekanie na koniec zapisu i sprawdzenie, czy plik powstał.
      - Znaczniki `marker` w dzienniku. Dziennik zawsze włączony.
      - `scenario.json` z wynikiem. `-scenario-exit` kończy grę po ostatniej linii i przy błędzie.

      Po Z6 i Z9. (W1, W2, W7, K1, K8)
- [x] **Z22** T3 (dopisane 2026-10-30): polecenie konsoli `info told <instancja C_INFO>`, żeby
      powitanie Xardasa nie zaczepiało bohatera w testach. Sprawdzenie: scenariusz z modem, który
      oznacza `DIA_Xardas_Hello`, a po 60 s gry zapisuje grę (zapis w dialogu by się nie udał).
      (W3, K1)
- [x] **Z23** T3 (dopisane 2026-10-30): polecenie konsoli `immortal <instancja>` (flaga
      `NPC_FLAG_IMMORTAL`), żeby walki NPC z NPC w scenariuszach 001 K5 i K7 trwały do końca
      obserwacji. Sprawdzenie w scenariuszach Z19. (W3, K10)
- [x] **Z13** T4: `wait <instancja|hero> <zdarzenie> [n] timeout <s>` na zdarzeniach z dziennika
      (`series`, `series-hit`, `combo`, `down`, `unconscious`, `dead`). Po upływie limitu
      scenariusz zgłasza błąd. (W1, W7, K6, K8)

## Faza 4: Narzędzia

- [x] **Z14** [P] `tools/fightlog.py report <katalog>`: `report.md` z podsumowaniem każdej postaci
      i nazwami stylów walki z `AI_Constants.d`. Python 3, biblioteka standardowa.
      - ciosy, serie według rodzaju, rozkład i najdłuższe combo do przodu,
      - moment połączenia i pominięte ms,
      - przerwania według przyczyny, bloki, odskoki, trafienia, obrażenia według etapu combo.

      (W5, K2, K3)
- [x] **Z15** `tools/fightlog.py check`: oczekiwania `expect` ze scenariusza.
      - Wynik każdego oczekiwania (zaliczone albo niezaliczone) z wartością faktyczną, w raporcie.
      - Kod wyjścia 1 przy niezaliczonym.

      Po Z14, ten sam plik. (W12, K11)
- [x] **Z16** [P] `tools/test.ps1` dla jednego scenariusza. PowerShell 5.1, sam ASCII.
      - Budowa skryptów i paczka (bez `-NoMod`).
      - Profil testowy `gothic25/build/test/profile`: `Gothic.ini` od nowa z kopii ustawień
        użytkownika plus `scaleVideos=-1`, zapisy osobno.
      - Katalog przebiegu z kopią scenariusza i `meta.json` (commit, czyste drzewo, z modem czy bez).
      - Start gry z argumentami z planu, w trybie automatycznym i ręcznym (`-Manual`).
      - Limit czasu i zamknięcie siłą, kopia `log.txt` i `crash.log`.
      - Raport i oczekiwania przez `fightlog.py`, kod wyjścia.

      (W2, W6, W7, W10, K2, K4, K8)
- [x] **Z17** `tools/test.ps1 -Spec <NNN>`: wszystkie scenariusze z `tests/NNN/` po kolei
      z podsumowaniem i kodem wyjścia. Po Z16, ten sam plik. (W12, K10, K11)
- [x] **Z18** [P] `tools/run.ps1 -Dev` przekazuje `-results` z nowym katalogiem wyników, żeby dziennik
      włączony w zwykłej grze deweloperskiej trafiał tam samo. (W4, K12)

## Faza 5: Scenariusze i proces

- [x] **Z19** Scenariusze dla 001 w `gothic25/tests/001/` z oczekiwaniami.
      - Wybór spokojnego waypointu, potwierdzony zrzutem ekranu.
      - Porównanie przyspieszenia 1 i 2 na scenariuszu K1 (ryzyko z planu).
      - Scenariusze:
        - obserwacja: K1, K2, K3 (część liczbowa), K4, K7, K10, K12,
        - interakcja: K5, K6, K8 (K1 bez moda), K9 (zapis w środku serii, wczytanie zapisu z Z1
          w 001 i nowego zapisu), K11.
      - Progi dobrane tak, żeby zestaw nie zawodził przypadkiem. Uzasadnienie progów w komentarzach.

      (W9, W12, K10)
- [ ] **Z20** [P] Proces.
      - Zdanie w zasadzie 5 konstytucji (ADR 0004).
      - Opis weryfikacji przez scenariusze w `sdd/workflow.md` i `.claude/commands/g25-verify.md`.
      - `gothic25/CLAUDE.md`: zgoda na tryb automatyczny (W11) i jak uruchamiać testy.
      - Instrukcja uruchamiania w `tests/README.md`.
      - Wpis w `CHANGELOG.md`.

      (W9, W10, W11, K10)

## Faza 6: Weryfikacja

- [ ] **Z21** Przejść kroki K1–K12 i uzupełnić sekcję „Weryfikacja” w spec.md.
      - Kryteria wymagające człowieka:
        - K1 (tryb ręczny, ekran postaci),
        - K3 (porównanie raportu z obserwacją; bez tego raport nie zalicza kryteriów, ADR 0004),
        - K5 (konsola ręcznie),
        - K9 (gra bez trybu deweloperskiego),
        - K12 (gra bohaterem).
      - Pozostałe może przejść Claude w trybie automatycznym według ADR 0004.

      Potem wracamy do Z15 w 001 z zestawem `tests/001`. (K1–K12)
