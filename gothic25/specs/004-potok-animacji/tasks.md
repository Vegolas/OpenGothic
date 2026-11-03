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
- [ ] **Z3** Skrypty Blendera i `tools/anim.ps1`.
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

      Po Z1 i Z2. (W1, W2, W3, W10, K1)

## Faza 2: Definicje i build

- [ ] **Z4** [P] Licencja MDK (ryzyko R1).
      - Odszukać tekst licencji MDK Gothic II: Noc Kruka (instalator MDK, dokumentacja, strona
        wydawcy) i sprawdzić, czy obejmuje definicje animacji (`_work/Data/Anims/*.mds`).
      - Wynik ze źródłem wpisać do ADR 0007 (sekcja „Kontekst”).
      - Jeśli licencja ich nie obejmuje: zatrzymać fazę 2 i zaproponować zmianę planu
        (dokładanie definicji przez silnik, nowy ADR).

      (W7)
- [ ] **Z5** [P] `anim.py mdk-diff`: parsery MSB i MDS oraz porównanie.
      - Parser binarnego MSB (układ chunków jak w ZenKit `ModelScriptBinary`) i tekstowego MDS
        (składnia jak w ZenKit `ModelScriptDsl`). Oba dają ten sam model danych: animacje, aliasy,
        blendy, połączenia, blokady, tagi modelu, zdarzenia z klatkami.
      - `mdk-diff <MDS> <MSB>` porównuje model danych i wypisuje różnice z nazwą animacji i polem.
        Kod wyjścia 1 przy różnicach.
      - Sprawdzenie: `HumanS.mds` i wszystkie `mds_overlay/Humans*.mds` z kopii właściciela kontra MSB
        z gry (z priorytetem dodatku). Raport do opisu commitu, a różnice do Z7.

      (W13, K11)
- [ ] **Z6** `anim.py build`: walidacja i zapis.
      - Wejście: `anims/anims.json`, definicje MDS z `anims/<MODEL>/`, pliki `.anim` i opcjonalny
        katalog `--extra`. Wyjście: `build/anims/_COMPILED/` z MAN i `<MODEL>.MSB` (tekst definicji,
        cp1252, CRLF).
      - Nagłówek MAN (nazwa, warstwa, `next`) z definicji. Kwantyzacja z `quant` albo dopasowana do
        danych. Bez chunka źródła, gdy `.anim` go nie ma.
      - Walidacja z W4:
        - szkielet zgodny ze `skeleton.json`;
        - liczba klatek równa zakresowi z definicji;
        - zdarzenia i okna combo w zakresie;
        - każda animacja z definicji ma MAN z buildu albo z gry (gdy dane gry są dostępne);
        - komunikat z nazwą animacji i powodem, kod wyjścia 1.
      - Wynik deterministyczny: posortowane wejścia, stały format, bez dat i ścieżek bezwzględnych.
      - Trzy zepsute źródła w `tests/004/fixtures/broken/` (brak kości, zdarzenie poza zakresem,
        brakująca animacja).
      - Sprawdzenie: dwa buildy z tego samego stanu dają identyczne pliki, każdy zepsuty przypadek
        kończy się błędem, a build działa bez Blendera.

      Po Z2 i Z5. (W4, W6, K3)
- [ ] **Z7** Definicje z MDK w modzie i build w pakowaniu.
      - `anims/HUMANS/`:
        - `HumanS.mds` z MDK w oryginalnym kodowaniu i końcach linii, z poprawkami różnic z Z5
          w blokach `// G25 004`;
        - `HUMANS.skeleton.json`.
      - `anims/anims.json`: model `HUMANS`, plik `HumanS.mds` -> `HUMANS.MSB`. Nowe
        `anims/.gitattributes`: `*.mds text working-tree-encoding=cp1252 eol=crlf`. Tak jak skrypty
        w `content/Scripts/.gitattributes`: na dysku kodowanie oryginału, w gicie UTF-8 z czytelnym
        diffem.
      - `tools/pack.ps1`: `anim.py build` przed pakowaniem i `--map build/anims=_WORK/DATA/ANIMS`.
        `tools/test.ps1`: `-AnimExtra <katalog>` przekazywany do `build --extra`.
      - Sprawdzenie:
        - `anim.py mdk-diff` dla `anims/HUMANS/HumanS.mds` kontra gra daje 0 różnic poza blokami
          `G25`;
        - log gry z modem bez ostrzeżeń parsera MDS;
        - `test.ps1 -Spec 001`, `-Spec 002` i `-Spec 003` przechodzą na definicjach tekstowych
          (ryzyko R3).

      Po Z4, Z5 i Z6. (W5, W6, W7, W13, K11)
- [ ] **Z8** `anim.py check-pack`.
      - Porównuje pliki animacji i definicji w `Gothic25.mod` z archiwami gry (nazwy i SHA-256).
      - Błąd przy pliku identycznym z oryginałem. Raport z listą plików animacji w paczce.
      - Sprawdzenie: paczka z Z7 (definicje bez sierpowych są jeszcze bajtowo różne od MSB, bo to
        tekst) i sztuczny przypadek z oryginalnym MAN w `--extra`, który musi dać błąd.

      Po Z7. (W7, K7)

## Faza 3: Silnik

- [ ] **Z9** [P] Polecenie konsoli `play ani <postać> <animacja>`.
      - `C_PlayAni` w `common/marvin.h` i tabeli `Marvin::Marvin`, obsługa wzorem `C_Immortal`:
        `hero` albo instancja, `Npc::playAnimByName`.
      - Błąd (`print` i `false`), gdy nie ma postaci albo animacji.
      - Opis w `tests/README.md` (polecenia konsoli).
      - Sprawdzenie: scenariusz `play ani hero S_FISTATTACK` i seria zrzutów pokazują cios. Nieznana
        nazwa kończy scenariusz błędem z numerem linii.

      (W9)
- [ ] **Z10** [P] Ataki boczne pięściami bohatera.
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
- [ ] **Z11** Ataki boczne pięściami NPC.
      - `npc.cpp:1729` i `npc.cpp:1982`: cios boczny pięścią zostaje `AttackL/R`, gdy model ma taką
        animację, a w przeciwnym razie `Attack` jak dotąd.
      - `dropForwardAttacks(fist && !sideAttacks)` w `implComboLink`. Komentarz w `fightalgo.cpp:254`
        poprawiony.
      - Sprawdzenie: build, `-Spec 001` i `-Spec 002` bez sierpowych w modzie przechodzą bez zmian.

      Po Z10 (wspólna metoda). (W15, W12)
- [ ] **Z12** [P] Miara kierunku ciosów w raporcie walki.
      - `tools/fightlog.py`: `attacks.dir.<fwd|left|right|run|finish>` dla oczekiwań. Opis w
        `tests/README.md` (oczekiwania).
      - Sprawdzenie: raport z istniejącego przebiegu 002 (ataki boczne paladyna) pokazuje
        `attacks.dir.left` > 0.

      (K13)

## Faza 4: Sierpowe

- [ ] **Z13** Sierpowy z lewej.
      - Punkt wyjścia: `anim.ps1 import HUMANS S_FISTATTACK`. Animację robimy w Blenderze przez MCP
        w oknie właściciela, który ogląda podgląd i ją akceptuje.
      - Ok. 20-30 klatek przy 25 fps: obrót tułowia, łuk lewej ręki w poziomie, powrót do `S_FIST`.
        Stopy na ziemi, korzeń bez dryfu.
      - `anims/HUMANS/T_FISTATTACKL.blend` (bez siatek z gry) i `T_FISTATTACKL.anim`.
      - Blok `// G25 004` w `HumanS.mds` obok pięści: `t_FistAttackL` na warstwie 1 z
        `DEF_HIT_LIMB "BIP01 L HAND"`, `DEF_OPT_FRAME`, `DEF_HIT_END`, `DEF_WINDOW` i `WHOOSH`.
      - Sprawdzenie:
        - `anim.ps1 check` bez różnic;
        - `anim.py build` i `check-pack` przechodzą;
        - scenariusz z `play ani hero T_FISTATTACKL` i zrzutami;
        - w trybie ręcznym (za zgodą właściciela) atak z lewej pięściami.

      Po Z3, Z7, Z9 i Z10. (W1, W6, W8)
- [ ] **Z14** [P] `anim.py mirror`.
      - Odbicie według planu: `W'_i = S·W_m(i)·S·C_i`, z korektą `C_i` z pozy spoczynkowej.
        Zamiana węzłów L/R według nazw (`L`/`R`, `LEFT`/`RIGHT`).
      - Tekstowe odbicie bloku definicji: zamiana stron w `DEF_HIT_LIMB` i innych nazwach węzłów oraz
        nowa nazwa animacji.
      - Sprawdzenie (K12, część narzędziowa):
        - podwójne odbicie `t_1hAttackL` (oryginał z `Humans_1hST1`) równe wejściu w granicach kwantu;
        - odbity `t_1hAttackL` ma ruch w drugą stronę niż wejście i stronę zgodną z `t_1hAttackR`
          (kierunek ruchu ręki i korzenia w raporcie).

      Po Z2 i Z6, równolegle z Z13. (W14, K12)
- [ ] **Z15** Sierpowy z prawej przez odbicie.
      - Reguła `"T_FISTATTACKR": {"mirror": "T_FISTATTACKL"}` w `anims.json`.
      - Build dokłada `HUMANS-T_FISTATTACKR.MAN` i wygenerowany blok `t_FistAttackR` za blokiem lewego
        w `HUMANS.MSB`.
      - Sprawdzenie: build, `check-pack`, zrzuty obu sierpowych przez `play ani`, podwójne odbicie
        sierpowego równe źródłu.

      Po Z13 i Z14. (W8, W14)
- [ ] **Z16** [P] Scenariusze `tests/004/`.
      - K04: podmiana stania z `tests/004/fixtures/idle/` (eksport testowego idle, opracowanie
        oryginału na GothicMOD) przez `-AnimExtra`, `play ani hero S_RUN` i seria zrzutów.
      - K06: kopacz atakuje nieśmiertelnego bohatera. W raporcie czasy trafień sierpowych kontra
        `DEF_OPT_FRAME`, a link w oknie combo kontra `DEF_WINDOW`.
      - K08: wersje bez moda (`# mod: off`) scenariuszy K12 i K13.
      - K09a i K09b: `play ani hero T_FISTATTACKL`, `save game`, potem wczytanie z modem i bez moda.
      - K12: zrzuty obu sierpowych.
      - K13: `BDT_10027_Addon_Buddler` przez 2 minuty, `expect ... attacks.dir.left >= 1` i to samo
        dla `right`, combo do przodu nadal 2 ciosy.
      - `reczne/K05-sierpowe.txt`: bohater z pięściami, `cheat god`, cel, który nie oddaje.
      - Sprawdzenie: każdy scenariusz uruchomiony raz. Raport z liczbami do opisu commitu.

      Po Z9, Z11, Z12 i Z15. (K4, K6, K8, K9, K12, K13)
- [ ] **Z17** [P] Dokumentacja.
      - `anims/README.md` (W11):
        - kroki od importu oryginału przez edycję, eksport i build do podglądu w grze;
        - format `.anim`, bloki `// G25 NNN` i reguły odbić;
        - lista animacji, które włączają zachowania silnika (ADR 0007, pkt 5): `T_FISTATTACKL/R`.
      - `content/README.md`: wiersz `Anims/` wskazuje na `anims/` i build.
      - `content/Scripts/README.md`: zdanie w sekcji „Symbole dla silnika” o atakach bocznych
        pięściami włączanych animacją.
      - `NOTICE.txt`: definicje animacji z MDK i animacje na bazie oryginałów na licencji GothicMOD.
      - `gothic25/CLAUDE.md`: zasoby animacji i narzędzia `anim.py` / `anim.ps1`.
      - `specs/001-combosy-npc-w-walce-wrecz/spec.md` (W1): odwołanie do 004 W15 przy ciosach
        bocznych pięściami.

      Po Z15. (W7, W11, W15)

## Faza 5: Weryfikacja

- [ ] **Z18** Przejść kroki kryteriów akceptacji i uzupełnić sekcję „Weryfikacja” w spec.md
      (K1-K13).
      - Automatycznie, na zacommitowanym kodzie (ADR 0004):
        - narzędzia K1, K3, K7, K11 i K12 (część narzędziowa);
        - scenariusze K4, K6, K8, K9, K12 i K13;
        - regresja `-Spec 001`, `-Spec 002` i `-Spec 003`.
      - Z właścicielem: K2 (pozy w Blenderze i w grze), K5 (`reczne/K05`, ocena sierpowych i serii),
        wygląd w K12.
      - K10: czysty checkout, `get-krx.ps1`, nowa sesja Claude'a przechodzi `anims/README.md`.
      - Wpis dla każdego K: scenariusz albo polecenie, commit, kto uruchomił, rozstrzygające liczby.

      (K1-K13)
