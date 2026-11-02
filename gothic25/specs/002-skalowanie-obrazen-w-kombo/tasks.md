# Zadania 002: Skalowanie obrażeń w kombo

- **Plan:** [plan.md](plan.md)
- **Utworzono:** 2026-11-01

Każde zadanie mieści się w jednym commicie. `[P]` oznacza zadanie, które można robić równolegle
z innymi `[P]` w tej samej fazie. W nawiasie: wymagania (W) i kryteria (K), które zadanie realizuje.

Plan nie zmienia serializacji i nie dodaje funkcji zewnętrznych dla skryptów, więc nie ma dla nich
osobnych zadań. Silnik budujemy przez `tools/build-engine.ps1`, skrypty przez
`tools/build-scripts.ps1`. Każda zmiana w walce kończy się zestawem `tools/test.ps1 -Spec 001`
jako testem regresji (`gothic25/CLAUDE.md`).

## Faza 1: Skrypty

- [x] **Z1** Tablice premii w nowym pliku `Content/AI/AI_Intern/ComboDamage.d`, dopisanym na końcu
      `Gothic.src` za `STORY\Startup.d`.
      - Tablice: `COMBO_DAMAGE_1H_PLAYER`, `COMBO_DAMAGE_2H_PLAYER` (3 × 4), `COMBO_DAMAGE_FIST_PLAYER`
        (4) i to samo z `_NPC`. Wartości startowe z planu.
      - Komentarz w pliku: układ tablic i zasada dla NPC (połowa nadwyżki ponad 100%).
      - Wiersz w tabeli „Symbole dla silnika” w `content/Scripts/README.md`.
      - Sprawdzenie: `tools/build-scripts.ps1`, `tools/dat.py prefix` na `GOTHIC.DAT` z 0.1.0
        (nazwane symbole z 0.1.0 mają te same numery, ADR 0005 z uzupełnieniem) i scenariusz
        `tests/001/K09c` z zapisem z 0.1.0. Bez silnika z Z3 i Z4 nic się w grze nie zmienia.

      (W1, W2, W5, W6, W7, W10)
- [x] **Z2** Cel testowy w nowym pliku `Content/AI/AI_Intern/ComboDamageTest.d`, na końcu
      `Gothic.src` za `ComboDamage.d`.
      - Postać `TST_ComboDummy`: człowiek bez broni, ochrona 0, dużo punktów życia.
      - Stan startowy `ZS_ComboDummy`: wyłączone percepcje, postać stoi.
      - Sprawdzenie: `tools/dat.py prefix` jak w Z1. Scenariusz próbny: `insert TST_ComboDummy`,
        bandyta atakuje cel przez 60 s, a cel nie blokuje, nie oddaje i nie ucieka (dziennik: brak
        ciosów i obron celu). Po Z1, ten sam plik `Gothic.src`.
      - Wynik próby (2026-11-01): paladyn 58 ciosów w 60 s, cel bez ciosów, bloków i odskoków.
        Każde trafienie zachwiewa cel i odpycha go o kawałek, więc para przesuwa się o kilkanaście
        metrów na minutę. Scenariusze z Z8 i Z9: krótkie obserwacje albo zapas miejsca.

      (P0 dla K1–K7, W10)

## Faza 2: Silnik

- [x] **Z3** `GameScript` czyta tablice `COMBO_DAMAGE_*` przy starcie (`initCommon`, obok
      `DAM_CRITICAL_MULTIPLIER`).
      - Metoda `comboDamage(player, talent, poziom, cios)` zwraca procent; ciosy dalsze niż długość
        wiersza biorą ostatnią kolumnę.
      - Brak tablicy: 100%. Zły rozmiar (nie 3 × n albo n dla pięści): ostrzeżenie w logu, tablica
        pominięta.
      - Bez użycia w obliczeniu obrażeń. Sprawdzenie: build, log gry z modem bez ostrzeżeń.

      (W2, W9)
- [x] **Z4** Premia w obliczeniu obrażeń.
      - `Npc::comboDamage()`: przy `Pose::comboInfo().forward` procent dla ciosu `comboLength()+1`,
        broni z `activeWeapon` (pięści, gdy brak) i `talentSkill`, tablica bohatera albo NPC
        według `isPlayer()`. W każdym innym wypadku 100%, także dla potworów bez broni.
      - `DamageCalculator::swordDamage`: `value * premia / 100` po filtrze odporności, przed
        `MinDamage` w `damageValue`.
      - Strzały i czary bez zmian (inna ścieżka).
      - Sprawdzenie: build, zestaw `tests/001` (regresja).

      Po Z3. (W1, W3, W4, W7, W9)
- [x] **Z5** Dziennik walki: pole `bonus` (procent premii, 100 bez premii) w zdarzeniu `result`
      przy `hit`. Wartość z tego samego obliczenia co `dmg` (`Npc::takeDamage`). Opis pola
      w `tests/README.md`. Po Z4. (W8)

## Faza 3: Narzędzia

- [x] **Z6** `tools/fightlog.py`: premia w raporcie i oczekiwaniach.
      - Kolumna premii w tabeli „Etap combo”.
      - Miary `bonus.stage.<N>.min`, `bonus.stage.<N>.max` i `bonus.dir.<dir>.max` (atak `n`
        łączony z jego `result`).
      - Opis miar w `tests/README.md`.

      Po Z5. (W8, K1, K3, K7)
- [x] **Z7** `tools/fightlog.py`: sekcja „Techniki” dla bohatera i opcja `--bonus`.
      - Odcinki ciosów bohatera według `dir` i `link`: pełne combo (łączenia do przodu), lewo-prawo
        (naprzemienne `left`/`right`), powtarzanie pierwszego ciosu (`fwd`, `link: new`, `combo: 1`).
      - Dla odcinka: mediana i rozrzut czasu na cios, obrażenia na cios, obrażenia na sekundę,
        przewaga pełnego combo nad lepszą z pozostałych technik w procentach.
      - `--bonus <tablica>`: te same liczby dla innych premii, z obrażeń bez premii (`dmg` / `bonus`)
        i zmierzonego czasu na cios.
      - Sprawdzenie na dzienniku z próbnej gry bohaterem i na dzienniku bez ciosów bohatera.

      Po Z6, ten sam plik. (W5, W6, K4, K6)

## Faza 4: Scenariusze

- [x] **Z8** [P] Scenariusze `tests/002/` dla ciosów NPC, z progami uzasadnionymi w komentarzach:
      - K1/K7: paladyn-mistrz i Torwache atakują `TST_ComboDummy` (`immortal`). Premie według etapu
        równe tablicy NPC, etap 1 = 100.
      - K3: bandyta ze stylem normalnym i paladyn: `bonus.dir.left.max` i `bonus.dir.right.max` = 100;
        atak z biegu i dobijanie, jeśli wystąpią, bez premii.
      - K8: K1 bez moda (`# mod: off`), premia 100 na każdym etapie.

      (W1, W3, W7, W9, K1, K3, K7, K8)
- [x] **Z9** [P] Scenariusze `tests/002/` dla odporności i zapisów:
      - K5: paladyn kontra `MagicGolem` (bez utraty życia) i `StoneGolem` (obrażenia każdego ciosu =
        obrażenia bez premii × premia, nie mniej niż 5).
      - K9: zapis w środku combo paladyna (`wait ... combo 2`), wczytanie i porównanie etapu i premii
        pierwszego ciosu po wczytaniu z animacją. Wczytanie zapisu z 0.1.0 jak 001 K09c.

      Dopisane przy realizacji (2026-11-02): golemy oddają i przerywają combo, więc paladyn trafia je
      tylko pierwszym ciosem. Dalsze etapy sprawdzają cele testowe z ochroną 200 i odporne
      (`TST_ComboDummyArmored`, `TST_ComboDummyImmune` na końcu `ComboDamageTest.d`), a raport ma
      miary `damage.stage.<N>.max`, `damage.min` i `damage.max`.

      (W4, W10, K5, K9)
- [x] **Z10** [P] Scenariusze do trybu ręcznego dla ciosów bohatera:
      - mistrz z bronią jednoręczną i dwuręczną (K1, K4);
      - nowicjusz 10% i wojownik 40% z bronią jednoręczną (K6).

      Każdy ustawia talent (`call B_RaiseFightTalent`), broń (`equip`) i cel testowy, a w komentarzu
      opisuje, co grać: po 20 s pełnego combo, lewo-prawo i powtarzania pierwszego ciosu.
      Zrealizowane jako dwie sesje w `tests/002/reczne/` (poza `-Spec`): `K04-mistrz` (obie bronie,
      zmiana w ekwipunku) i `K06-nowicjusz-wojownik` (talent 10%, potem 40% poleceniem `call`).
      (W5, W6, K1, K4, K6)

## Faza 5: Proces

- [x] **Z11** Wpis w `CHANGELOG.md` w `[Unreleased]`: premia za kolejne ciosy combo dla bohatera
      i NPC, wymaga silnika z tego wydania. Numer wersji ustalamy przy wydaniu (MINOR). (W1, W7)

## Faza 6: Weryfikacja

- [x] **Z12** Przejść kroki K1–K9 i uzupełnić sekcję „Weryfikacja” w spec.md.
      - Automatycznie (ADR 0004): `tools/test.ps1 -Spec 002`, K2 przez zmianę premii trzeciego ciosu
        w `ComboDamage.d` bez commita i powtórkę K1, zestaw `tests/001` jako regresja.
      - Ręcznie: gra bohaterem w scenariuszach z Z10 z dziennikiem. Liczby dla K1 (bohater), K4 i K6
        wylicza sekcja „Techniki”.
      - Strojenie: gdy K4 albo K6 nie przechodzi, nowe wartości z `--bonus`, osobny commit z tabelą
        przed i po w komentarzu `ComboDamage.d`, potem ponowny pomiar.
      - Wynik (2026-11-02): wszystkie K spełnione bez strojenia. K4 i K6 rozstrzyga przeliczenie bez
        losowania słabego ciosu, bo sama sekcja „Techniki” daje przy kilkunastu combo duży rozrzut
        (opis w sekcji „Weryfikacja” w spec.md).

      (K1–K9)
