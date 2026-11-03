# Zadania 004: Potok animacji

- **Plan:** [plan.md](plan.md)
- **Utworzono:** 2026-11-03

Każde zadanie mieści się w jednym commicie. `[P]` oznacza zadanie, które można robić równolegle
z innymi `[P]` w tej samej fazie. W nawiasie: wymagania (W) i kryteria (K), które zadanie realizuje.

Plan nie zmienia serializacji i nie dodaje funkcji zewnętrznych dla skryptów, więc nie ma dla nich
osobnych zadań. Silnik budujemy przez `tools/build-engine.ps1`. Każda zmiana w walce kończy się
zestawami `tools/test.ps1 -Spec 001` i `-Spec 002` jako testami regresji (`gothic25/CLAUDE.md`).
Pliki z gry wyciągamy tylko do `gothic25/build/` (konstytucja, zasada 6). Kod z prototypu
(`gothic25/build/prototypes/idle-natural/scripts/`) przenosimy do `tools/` i porządkujemy,
nie kopiujemy w całości.

## Faza 1: Narzędzia bazowe

- [x] **Z1** [P] Przypięty KrxImpExp i ścieżka do Blendera.
      - `tools/get-krx.ps1` (wzór `get-gdc.ps1`):
        - pobiera commit `$KrxCommit` z gitlab.com/Patrix9999/krximpexp przez git, bo archiwa www
          GitLab daje tylko przeglądarce (weryfikacja Cloudflare). Pliki są eksportowane bez zamiany
          końców linii, a SHA-256 liczy się z plików (`Get-TreeSha256`);
        - rozpakowuje do `.tools/blender-scripts/addons/krximpexp/`, z `KRX_COMMIT.txt`;
        - `-Force` pobiera od nowa.
      - `tools/lib/common.ps1`: `$KrxCommit`, `$BlenderScriptsDir`, funkcja `Resolve-Blender`
        (`local.json` `blender`, potem `G25_BLENDER`). Brak ścieżki kończy się komunikatem, co ustawić.
      - `local.example.json`: klucz `blender`.
      - Sprawdzenie: `get-krx.ps1` na czystym `.tools`, drugi przebieg bez pobierania, zepsuta suma
        kończy się błędem.

      (W10)
- [x] **Z2** [P] `tools/anim.py`: MAN, MDH i format `.anim`.
      - Odczyt i zapis MAN oraz odczyt MDH, z prototypu `zen_anim.py`.
      - Format `.anim` według planu: nagłówek, `quant` jako dokładny float32, `source`, klatki ze stałą
        liczbą miejsc po przecinku.
      - Polecenia:
        - `to-text` / `from-text`;
        - `extract <model>` z archiwów gry do `build/anims-work/`, z priorytetem jak w grze
          (dodatek nad podstawą, `Data/ModVDF` nad oboma), przez funkcje z `vdf.py`;
        - `skeleton` (`<MODEL>.skeleton.json`);
        - `roundtrip` (MAN -> `.anim` -> MAN dla wszystkich `HUMANS*-*.MAN`, raport i kod wyjścia).
      - Sprawdzenie: `anim.py roundtrip HUMANS` na kopii gry daje 0 różnic. Wynik zapisany
        w opisie commitu.
      - Wynik (2026-11-03): 1038 animacji ludzi i nakładek, 1038 identycznych bajt w bajt, ok. 3 s.
        Dwa pliki (`HUMANS_ACROBATIC-T_FALL*_2_DIVE`) mają skalę pozycji 0 i kody 0; zapis to
        odwzorowuje. `extract HUMANS` bierze `HUMANS.MSB` i `HUM_BODY_NAKED0.MDM` z `Anims_Addon.vdf`.

      (W2, W3, K1 bez Blendera)
- [x] **Z3** Skrypty Blendera i `tools/anim.ps1`.
      - `tools/blender/rig.py`:
        - import MDH+MDM przez KrxImpExp (jawne `addon_utils.enable(..., default_set=True)`);
        - MAN -> akcja, ze wzoru `s7_apply_man.py`; sloty `ZS_*` z kluczami transformacji lokalnej;
        - zapis `.blend` bez siatek z gry, a w trybie `open` z doczepionym ciałem z kopii gry.
      - `tools/blender/export.py`: akcje -> `.anim`, ze wzoru `s11_idle.py`. `tools/blender/check.py`:
        ponowny eksport do katalogu tymczasowego i porównanie z `.anim`.
      - `tools/anim.ps1` (`import`, `export`, `check`, `open`, `roundtrip-blender`):
        - `BLENDER_USER_SCRIPTS=.tools/blender-scripts`,
          `--background --factory-startup --python-exit-code 1`;
        - sprawdzenie wersji 5.2.x i commitu KrxImpExp przed pracą.
      - Sprawdzenie:
        - `anim.ps1 roundtrip-blender HUMANS` (wszystkie animacje ludzi i nakładek przez Blendera,
          w jednym procesie) daje 0 różnic;
        - `anim.ps1 import HUMANS S_FISTATTACK` daje `.blend` bez siatek z gry, a `open` dokłada ciało;
        - zła ścieżka do Blendera i inny commit KrxImpExp kończą się komunikatem (K10, część
          o ustawieniach).

      - Wynik (2026-11-03):
        - `roundtrip-blender`: 1038 animacji, 1038 identycznych bajt w bajt (także 199 jednoklatkowych,
          skala pozycji 0, w ≈ 0);
        - eksport niezmienionego `S_FISTATTACK` daje ten sam tekst co `anim.py to-text`, bo eksport
          przyciąga próbki do siatki kwantyzacji MAN (`anim.snap`). Zmieniony oryginał, który wychodzi
          poza zakres kwantyzacji, dostaje nowy zakres;
        - lekki `.blend`: szkielet i sloty KrxImpExp, bez `ZM_SKIN`, `DUMMY_HEAD` i tekstur z gry;
        - `check` wykrywa rozjechany `.anim`;
        - kopia akcji pod nową nazwą eksportuje się jako nowa animacja (bez `raw`, `layout`, `quant`
          oryginału);
        - błędy: zła ścieżka do Blendera, Blender 3.6 („Blender 5.2.x is required”) i inny commit
          KrxImpExp kończą się komunikatem.

      Po Z1 i Z2. (W1, W2, W3, W10, K1)

## Faza 2: Definicje i build

- [x] **Z4** [P] Licencja MDK (ryzyko R1).
      - Odszukać tekst licencji MDK Gothic II: Noc Kruka (instalator MDK, dokumentacja, strona
        wydawcy) i sprawdzić, czy obejmuje definicje animacji (`_work/Data/Anims/*.mds`).
      - Wynik ze źródłem wpisać do ADR 0007 (sekcja „Kontekst”).
      - Jeśli licencja ich nie obejmuje: zatrzymać fazę 2 i zaproponować zmianę planu
        (dokładanie definicji przez silnik, nowy ADR).
      - Wynik (2026-11-03): **licencja ich nie obejmuje.** EULA MDK obejmuje GothicMOD tylko nowe dane
        i skrypty z `/_work/data/Scripts`. Reszta danych z instalatora, w tym `_work/Data/Anims/*.mds`,
        podlega umowie licencyjnej gry (bez rozpowszechniania). Szczegóły i źródło: ADR 0007,
        „Kontekst”. Faza 2 wstrzymana do decyzji o zmianie planu.

      (W7)
- [x] **Z5** [P] Parsery definicji i `anim.py defs`.
      - Parser binarnego MSB (układ chunków jak w ZenKit `ModelScriptBinary`) i tekstowego MDS
        (składnia jak w ZenKit `ModelScriptDsl`). Oba dają ten sam model danych: animacje, aliasy,
        blendy, połączenia, blokady, tagi modelu, zdarzenia z klatkami.
      - Łączenie według ADR 0008 (wpis według nazwy, bez wielkości liter, z pochodzeniem).
      - `defs <MODEL> [<ANI>...] [--ext PLIK]`: połączone definicje oryginału z kopii gry i rozszerzenia,
        w tej samej postaci, w jakiej wypisuje je `ani info` (Z11).
      - Sprawdzenie:
        - parser MSB czyta `HUMANS.MSB` i wszystkie `HUMANS_*.MSB` z gry bez błędów, z tą samą liczbą
          animacji co tekstowe MDS z MDK w kopii właściciela (MDK tylko jako lokalna kontrola parsera
          MDS, nic z niego nie trafia do repozytorium);
        - porównanie obu parserów dla tych plików: różnice tylko tam, gdzie MDK różni się od gry
          (raport do opisu commitu).
      - Wynik (2026-11-03), `anim.py mds-check <gra>/_work/Data/Anims`:
        - 117 plików definicji (3949 animacji), 0 błędów parsera, `HUMANS` 784 = 784 animacje;
        - znane różnice ZenKit między formatami są liczone osobno: zasięg i slot dźwięku (668),
          floaty czytane jako int (`pfx`/`pfx_stop`/`tremor`, 108), spacje w cudzysłowie (2);
        - 60 pozostałych to różnice danych MDK i gry, np. `T_1HPARADE_0` w MDK ma `DEF_WINDOW`,
          a w grze nie, i dodatkowe kroki w `T_1HWALKL_2_1HWALK` w grze.
        - `defs HUMANS S_FISTATTACK` wypisuje definicję z gry. Z testowym rozszerzeniem: 1 dołożona,
          1 zastąpiona, pochodzenie `mod`.
        - Tokenizer naprawiony przy EOF (cofanie zostaje na końcu tekstu, jak w ZenKit, który przed
          `maybe` sprawdza `eof()`).

      (W13, K11)
- [ ] **Z6** `anim.py build`: walidacja i zapis.
      - Wejście: `anims/anims.json`, `anims/<MODEL>/*.EXT.MDS`, pliki `.anim` i opcjonalny katalog
        `--extra`. Wyjście: `build/anims/_COMPILED/` z MAN i `<MODEL>.EXT.MDS` (wpisy moda i bloki
        odbić z Z16).
      - Nagłówek MAN (nazwa, warstwa, `next`) z definicji moda. Kwantyzacja z `quant` albo dopasowana
        do danych.
      - Walidacja z W4:
        - szkielet zgodny ze `skeleton.json`;
        - liczba klatek równa zakresowi z definicji;
        - zdarzenia i okna combo w zakresie;
        - każda animacja z rozszerzenia ma MAN z buildu albo z gry (gdy dane gry są dostępne);
        - komunikat z nazwą animacji i powodem, kod wyjścia 1.
      - Wynik deterministyczny: posortowane wejścia, stały format, bez dat i ścieżek bezwzględnych.
      - Trzy zepsute źródła w `tests/004/fixtures/broken/` (brak kości, zdarzenie poza zakresem,
        brakująca animacja), zrobione jako nasze pliki (czysty szkielet, własne wpisy MDS).
      - Sprawdzenie: dwa buildy z tego samego stanu dają identyczne pliki, każdy zepsuty przypadek
        kończy się błędem, a build działa bez Blendera.

      Po Z5. (W4, W6, K3)
- [ ] **Z7** Build w pakowaniu i układ `anims/`.
      - `anims/anims.json` (model `HUMANS`, rozszerzenie `HUMANS.EXT.MDS`),
        `anims/HUMANS/HUMANS.skeleton.json` (`anim.py skeleton`) i `anims/HUMANS/HUMANS.EXT.MDS`
        z samym nagłówkiem, na razie bez wpisów.
      - `tools/pack.ps1`: `anim.py build` przed pakowaniem i `--map build/anims=_WORK/DATA/ANIMS`.
        `tools/test.ps1`: `-AnimExtra <katalog>` przekazywany do `build --extra`.
      - Sprawdzenie: `pack.ps1` i `test.ps1 -Spec 001` przechodzą (rozszerzenie bez wpisów niczego nie
        zmienia, a silnik jeszcze go nie czyta).

      Po Z6. (W4, W5, W6)
- [ ] **Z8** [P] `anim.py check-pack`.
      - Porównuje paczkę moda z archiwami gry. Błąd przy:
        - pliku definicji modelu z gry (`*.MSB`, pełne `*.MDS`);
        - pliku identycznym z oryginałem (SHA-256);
        - MAN, którego próbki są równe oryginałowi o tej samej nazwie.
      - Raport z listą plików animacji w paczce.
      - Sprawdzenie: paczka z Z7 przechodzi. Sztuczne przypadki w `--extra` (oryginalny MAN
        i oryginalny MSB z `build/anims-work`) dają błąd.

      Po Z7. (W7, K7)
- [ ] **Z9** [P] Nowa animacja na czystym szkielecie i blokada pochodnych.
      - `rig.py new` i `anim.ps1 new -Anim <NAZWA>`: szkielet z MDH i pusta akcja z `g25_anim`
        bez danych oryginału: pochodzenie `mod`, węzły = kości modelu, nagłówek z MDH, bez slotów
        i `raw`.
      - Import zapisuje pochodzenie `game`. `export` do katalogu poza `build/` odmawia akcji
        z pochodzeniem `game`, także po zmianie nazwy, i podpowiada `anim.ps1 new`.
        `-AllowDerived` pozwala na taki eksport tylko do `build/`.
      - `anim.py fixtures`: lokalne dane testowe w `build/anims-fixtures/` z kopii gry:
        - podmiana `S_RUN` z obrotem głowy (wzór prototypu);
        - testowy `HUMANS.EXT.MDS` (nowa animacja, podmieniona definicja jednej oryginalnej, wpis dla
          nakładki `HUMANS_1HST1`).
      - Sprawdzenie (K14):
        - eksport kopii importu do `anims/` kończy się błędem;
        - z `-AllowDerived` zapisuje dane tylko w `build/`;
        - `new` + `export` daje `.anim` bez `raw`, `quant` i slotów oryginału;
        - `check` dla nowej animacji przechodzi.

      Po Z3. (W2, W16, K14)

## Faza 3: Silnik

- [ ] **Z10** [P] Dokładanie definicji moda (ADR 0008).
      - `Resources::implLoadAnimation`:
        - po wczytaniu definicji modelu albo nakładki szuka `<nazwa>.EXT.MDS` i ładuje go przez
          `zenkit::ModelScript::load`;
        - łączy wpisy według nazwy (bez wielkości liter): `animations`, `aliases`, `blends`,
          `combinations`, `disabled_animations`, `model_tags`. Pomija `meshes` i `skeleton`;
        - oznacza pochodzenie animacji z rozszerzenia;
        - zapisuje w logu jedną linię z liczbą dołożonych i zastąpionych wpisów.
      - Bez pliku nic się nie zmienia.
      - Sprawdzenie:
        - build;
        - z danymi testowymi z Z9 log pokazuje dołożone i zastąpione wpisy, a nowa animacja ma MAN
          z paczki;
        - `-Spec 001` i `-Spec 002` z pustym rozszerzeniem przechodzą.

      Po Z7 i Z9 (dane testowe). (W6, W7, W12, W13)
- [ ] **Z11** [P] Polecenia konsoli `play ani` i `ani info`.
      - `C_PlayAni` i `C_AniInfo` w `common/marvin.h` i tabeli `Marvin::Marvin`, obsługa wzorem
        `C_Immortal` (`hero` albo instancja):
        - `play ani <postać> <animacja>`: `Npc::playAnimByName`;
        - `ani info <postać> <animacja>`: pochodzenie (oryginał albo rozszerzenie), warstwa, flagi,
          zakres klatek, liczba klatek MAN, `next`, zdarzenia z klatkami.
      - Błąd (`print` i `false`), gdy nie ma postaci albo animacji.
      - Opis w `tests/README.md` (polecenia konsoli).
      - Sprawdzenie:
        - scenariusz z `play ani hero S_FISTATTACK` i serią zrzutów pokazuje cios;
        - `ani info hero S_FISTATTACK` wypisuje to samo co `anim.py defs HUMANS S_FISTATTACK`;
        - nieznana nazwa kończy scenariusz błędem z numerem linii.

      (W9)
- [ ] **Z12** [P] Ataki boczne pięściami bohatera.
      - `AnimationSolver::implSolveAnim`: w gałęzi pięści `AttackL/R` -> `T_FISTATTACKL/R`.
      - Metoda sprawdzająca, czy model ma atak boczny pięścią w danym kierunku (np.
        `Npc::hasFistSideAttack(Anim)` przez solver).
      - `Npc::swingSwordL/R` przy `WeaponState::Fist` bez wymogu broni.
      - `PlayerControl`: z pięściami `ActLeft`/`ActRight` jak przy broni, `ActBack` dalej blok.
      - Sprawdzenie:
        - build;
        - bez animacji (mod bez sierpowych i bez moda) atak z lewej pięściami nic nie robi;
        - `-Spec 001` i `-Spec 002` przechodzą.

      (W8, W12)
- [ ] **Z13** Ataki boczne pięściami NPC.
      - `npc.cpp:1729` i `npc.cpp:1982`: cios boczny pięścią zostaje `AttackL/R`, gdy model ma taką
        animację, a w przeciwnym razie `Attack` jak dotąd.
      - `dropForwardAttacks(fist && !sideAttacks)` w `implComboLink`. Komentarz w `fightalgo.cpp:254`
        poprawiony.
      - Sprawdzenie: build, `-Spec 001` i `-Spec 002` bez sierpowych w modzie przechodzą bez zmian.

      Po Z12 (wspólna metoda). (W15, W12)
- [ ] **Z14** [P] Miara kierunku ciosów w raporcie walki.
      - `tools/fightlog.py`: `attacks.dir.<fwd|left|right|run|finish>` dla oczekiwań. Opis w
        `tests/README.md` (oczekiwania).
      - Poprawka: `techniques_section` dzieli przez zero, gdy przebieg nie ma ciosów bohatera
        (`ZeroDivisionError` po ręcznym przebiegu w Khorinis 2026-11-03, `fightlog.py:418`).
      - Sprawdzenie: raport z istniejącego przebiegu 002 (ataki boczne paladyna) pokazuje
        `attacks.dir.left` > 0. Raport przebiegu bez ciosów bohatera nie kończy się błędem.

      (K13)

## Faza 4: Sierpowe

- [ ] **Z15** Sierpowy z lewej.
      - Start: `anim.ps1 new -Anim T_FISTATTACKL`. Animację kluczujemy sami w Blenderze przez MCP
        w oknie właściciela, który ogląda podgląd i ją akceptuje. Oryginalny `S_FISTATTACK` można
        obejrzeć obok (`anim.ps1 import`), bez kopiowania kluczy (spec. P9).
      - Ok. 20-30 klatek przy 25 fps: postawa bojowa, obrót tułowia, łuk lewej ręki w poziomie,
        powrót. Stopy na ziemi, korzeń bez dryfu.
      - `anims/HUMANS/T_FISTATTACKL.blend` (bez siatek z gry) i `T_FISTATTACKL.anim`.
      - Blok `// G25 004` w `HUMANS.EXT.MDS`: `t_FistAttackL` na warstwie 1 z
        `DEF_HIT_LIMB "BIP01 L HAND"`, `DEF_OPT_FRAME`, `DEF_HIT_END`, `DEF_WINDOW` i `WHOOSH`.
        Dźwięk jak w oryginałach: `*eventSFX (N "WHOOSH" R:2500)` bez `EMPTY_SLOT`. ZenKit czyta
        oryginalne MSB jako zasięg 2500 i `empty_slot` = false, a tekst bez `R:` daje 1000 (Z5), a silnik
        używa obu pól (`animation.cpp:361`).
      - Sprawdzenie:
        - `anim.ps1 check` bez różnic;
        - `anim.py build` i `check-pack` przechodzą;
        - `ani info hero T_FISTATTACKL` pokazuje pochodzenie z moda;
        - scenariusz z `play ani hero T_FISTATTACKL` i zrzutami;
        - w trybie ręcznym (za zgodą właściciela) atak z lewej pięściami.

      Po Z9, Z10, Z11 i Z12. (W1, W6, W8)
- [ ] **Z16** [P] `anim.py mirror`.
      - Odbicie według planu: `W'_i = S·W_m(i)·S·C_i`, z korektą `C_i` z pozy spoczynkowej.
        Zamiana węzłów L/R według nazw (`L`/`R`, `LEFT`/`RIGHT`).
      - Tekstowe odbicie bloku definicji: zamiana stron w `DEF_HIT_LIMB` i innych nazwach węzłów oraz
        nowa nazwa animacji.
      - Sprawdzenie (K12, część narzędziowa, lokalnie na oryginałach):
        - podwójne odbicie `t_1hAttackL` (z `Humans_1hST1`) równe wejściu w granicach kwantu;
        - odbity `t_1hAttackL` ma ruch w drugą stronę niż wejście i stronę zgodną z `t_1hAttackR`
          (kierunek ruchu ręki i korzenia w raporcie).

      Po Z2 i Z6, równolegle z Z15. (W14, K12)
- [ ] **Z17** Sierpowy z prawej przez odbicie.
      - Reguła `"T_FISTATTACKR": {"mirror": "T_FISTATTACKL"}` w `anims.json`.
      - Build dokłada `HUMANS-T_FISTATTACKR.MAN` i wygenerowany blok `t_FistAttackR` za blokiem lewego
        w `HUMANS.EXT.MDS`.
      - Sprawdzenie: build, `check-pack`, zrzuty obu sierpowych przez `play ani`, podwójne odbicie
        sierpowego równe źródłu.

      Po Z15 i Z16. (W8, W14)
- [ ] **Z18** [P] Scenariusze `tests/004/`.
      - K04: podmiana stania z `anim.py fixtures` przez `-AnimExtra build/anims-fixtures`,
        `play ani hero S_RUN` i seria zrzutów.
      - K06: kopacz atakuje nieśmiertelnego bohatera. W raporcie czasy trafień sierpowych kontra
        `DEF_OPT_FRAME`, a link w oknie combo kontra `DEF_WINDOW`.
      - K08: wersje bez moda (`# mod: off`) scenariuszy K11, K12 i K13.
      - K09a i K09b: `play ani hero T_FISTATTACKL`, `save game`, potem wczytanie z modem i bez moda.
      - K11: `ani info` dla nowej, podmienionej, niezmienionej i nakładkowej animacji z danymi
        testowymi, bez nich i bez moda.
      - K12: zrzuty obu sierpowych.
      - K13: `BDT_10027_Addon_Buddler` przez 2 minuty, `expect ... attacks.dir.left >= 1` i to samo
        dla `right`, combo do przodu nadal 2 ciosy.
      - `reczne/K05-sierpowe.txt`: bohater z pięściami, `cheat god`, cel, który nie oddaje.
      - Sprawdzenie: każdy scenariusz uruchomiony raz. Raport z liczbami do opisu commitu.

      Po Z11, Z13, Z14 i Z17. (K4, K6, K8, K9, K11, K12, K13)
- [ ] **Z19** [P] Dokumentacja.
      - `anims/README.md` (W11):
        - kroki od `new` przez edycję, eksport i build do podglądu w grze, a także import oryginału
          jako wzorca;
        - zasada: tylko własne klucze (spec. P9);
        - format `.anim`, plik `*.EXT.MDS` i reguły łączenia (ADR 0008), bloki `// G25 NNN`,
          reguły odbić;
        - lista danych, które włączają zachowania silnika: `T_FISTATTACKL/R`, `*.EXT.MDS`.
      - `content/README.md`: wiersz `Anims/` wskazuje na `anims/` i build.
      - `content/Scripts/README.md`: zdanie w sekcji „Symbole dla silnika” o atakach bocznych pięściami
        i plikach `*.EXT.MDS`.
      - `NOTICE.txt`: animacje i definicje moda jako nowe dane na licencji GothicMOD. Mod nie zawiera
        animacji ani definicji z gry.
      - `gothic25/CLAUDE.md`: zasoby animacji i narzędzia `anim.py` / `anim.ps1`.
      - `specs/001-combosy-npc-w-walce-wrecz/spec.md` (W1): odwołanie do 004 W15 przy ciosach
        bocznych pięściami.

      Po Z17. (W7, W11, W15)

## Faza 5: Weryfikacja

- [ ] **Z20** Przejść kroki kryteriów akceptacji i uzupełnić sekcję „Weryfikacja” w spec.md
      (K1-K14).
      - Automatycznie, na zacommitowanym kodzie (ADR 0004):
        - narzędzia K1, K3, K7, K12 (część narzędziowa) i K14;
        - scenariusze K4, K6, K8, K9, K11, K12 i K13;
        - regresja `-Spec 001`, `-Spec 002` i `-Spec 003`.
      - Z właścicielem: K2 (pozy w Blenderze i w grze), K5 (`reczne/K05`, ocena sierpowych i serii),
        wygląd w K12.
      - K10: czysty checkout, `get-krx.ps1`, nowa sesja Claude'a przechodzi `anims/README.md`.
      - Wpis dla każdego K: scenariusz albo polecenie, commit, kto uruchomił, rozstrzygające liczby.

      (K1-K14)
