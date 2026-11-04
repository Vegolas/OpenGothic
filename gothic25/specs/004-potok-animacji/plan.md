# Plan 004: Potok animacji

- **Specyfikacja:** [spec.md](spec.md)
- **Status:** Zatwierdzony (poprawiony i zatwierdzony ponownie 2026-11-03 po zadaniu Z4: licencja MDK, ADR 0008)
- **Utworzono:** 2026-11-03

## Podsumowanie

Potok budujemy głównie z narzędzi:
- `tools/anim.py` w czystym Pythonie czyta i zapisuje MAN, MDH, MSB i MDS, buduje animacje
  z tekstowego eksportu, odbija je lustrzanie i łączy definicje moda z oryginałem tak jak silnik;
- skrypty Blendera uruchamiane bez okna importują oryginały jako wzorzec, zakładają nowe animacje
  na czystym szkielecie i eksportują akcje do tekstu.

Mod dostarcza tylko własne animacje i własny plik definicji `HUMANS.EXT.MDS`. Silnik dokłada go
do oryginalnego `HUMANS.MSB` z kopii gracza ([ADR 0008](../../decisions/0008-dokladanie-definicji-animacji-moda-przez.md)).
Zmiany w silniku zależą od danych moda:
- dokładanie definicji (gdy jest plik rozszerzenia);
- ataki boczne pięściami bohatera i NPC (gdy model ma ich animacje);
- polecenia konsoli, które odtwarzają animację i wypisują jej definicję.

Pierwszą treścią są sierpowe: lewy zrobiony w Blenderze i prawy jako jego odbicie. Od 2026-11-04
mogą zaczynać się od oryginalnej postawy i przerabiać oryginalne ruchy (spec. P9, ADR 0009). Zasady
wspólne dla kolejnych funkcji z animacjami są w [ADR 0007](../../decisions/0007-zrodla-i-budowanie-animacji-moda.md),
ADR 0008 i ADR 0009.

## Warstwa

- **Narzędzia i zasoby (większość pracy).** Formaty gry (MAN) zapisuje tylko nasze narzędzie, bo
  ani ZenKit, ani KrxImpExp go nie zapisują. Narzędzie w Pythonie działa bez Blendera, w CI i
  z każdego skryptu (zasada 10).
- **Silnik (mała zmiana).** Licencja MDK (Z4) wyklucza rozpowszechnianie pełnych definicji
  modelu, więc dokładanie własnych wpisów do oryginału musi zrobić silnik. To ogólny mechanizm
  przy ładowaniu definicji, sterowany plikiem moda. Pięści mają dziś ataki boczne zablokowane
  w pięciu miejscach (niżej). Treść, czyli animacje i ich zdarzenia, zostaje w danych moda. Bez
  danych moda działa jak upstream. Obie zmiany są ogólne i da się je zgłosić do Try/OpenGothic.
- **Skrypty: bez zmian.** Style walki NPC (`FIGHT.DAT`) już dziś zlecają ciosy boczne pięściami
  (spec. W15).

## Obecny stan

Silnik:

- Definicje modelu: `Resources::implLoadAnimation` w `common/resources.cpp:667-687`. W trybie G2
  nazwa `.MDS` jest zamieniana na `.MSB` (`:672`), a `zenkit::ModelScript::load` (`:681`) sam
  rozpoznaje treść binarną albo tekstową (`lib/ZenKit/src/ModelScript.cc:436-446`). Tą samą drogą
  idą nakładki (`Mdl_ApplyOverlayMds`).
- `zenkit::ModelScript` ma osobne listy: `animations`, `aliases`, `blends`, `combinations`,
  `disabled_animations`, `model_tags` oraz `meshes` i `skeleton`
  (`lib/ZenKit/include/zenkit/ModelScript.hh:273-285`). Wyszukiwanie plików w VFS nie rozróżnia
  wielkości liter (`lib/ZenKit/src/Vfs.cc:94`).
- Klatki: `Animation::Animation` ładuje `<model>-<ani>.MAN` dla każdej animacji z definicji
  (`common/graphics/mesh/animation.cpp:36`). Z nagłówka MAN pochodzą nazwa i warstwa, które nadpisują
  wartości z definicji, oraz fps i liczba klatek (`animation.cpp:228-232`). Zakres klatek z definicji
  służy tylko do zdarzeń (`animation.cpp:22-27`, `frameClamp`). Checksum MAN nie jest sprawdzany.
- Pięści, wybór animacji: `AnimationSolver::implSolveAnim`, gałąź pięści
  (`common/graphics/mesh/animationsolver.cpp:115-124`), obsługuje tylko `Attack`
  (`S_FISTATTACK` / `T_FISTATTACKMOVE`) i `AttackBlock`. Broń ma `T_%sATTACKL/R` (`:129-132`).
- Pięści, gracz: `common/game/playercontrol.cpp:822-828`. Z pięściami lewo i prawo są ignorowane,
  działa tylko blok (`ActBack`). `Npc::swingSwordL/R` (`common/world/objects/npc.cpp:4000-4012`)
  wymagają aktywnej broni.
- Pięści, NPC: pierwszy cios serii (`npc.cpp:1729`) i cios łączony w oknie combo (`npc.cpp:1982`)
  zamieniają cios boczny pięścią na `Anim::Attack`. `FightAlgo::dropForwardAttacks`
  (`common/game/fightalgo.cpp:253-257`, wywołanie w `npc.cpp:1913`) przy limicie talentu wyrzuca
  z kolejki ciosy boczne pięściami jak ciosy do przodu. Komentarz: „fist has no side attacks”.
- Łączenie w serie jest ogólne. `Pose::continueCombo` (`common/graphics/mesh/pose.cpp:730-800`)
  w oknie combo uruchamia inną animację tej samej warstwy jako atak boczny (`CL_Side`, `:799`).
  `Pose::comboInfo` (`pose.cpp:825-846`) uznaje animację za combo do przodu, gdy ma więcej niż jedno
  `DEF_HIT_END` (`:837`).
- Obrażenia: `Npc::comboDamage` (`npc.cpp:1221-1234`) daje premię tylko combo do przodu, więc sierpowy
  z jednym trafieniem dostanie 100% bez zmian w kodzie (002 W3).
- Dziennik walki zapisuje kierunek ataku `left`/`right` z `Anim::AttackL/R`
  (`common/game/fightlog.cpp:228-233`). Wywołuje go `Npc::doAttack` (`npc.cpp:3945-3966`).
- Konsola: tabela poleceń w konstruktorze `Marvin::Marvin` (`common/marvin.cpp:73-186`; wzór
  obsługi z instancją: `C_Immortal`, `:521-531`), enum w `common/marvin.h:71-73`. Animację po
  nazwie odtwarza `Npc::playAnimByName` (`npc.cpp:995-997`). Scenariusze wykonują każde polecenie
  konsoli (003).
- Zapisy: `Pose::load` (`common/graphics/mesh/pose.cpp:70-90`) zapisuje nazwy animacji warstw,
  a przy wczytaniu pomija te, których model nie ma (`:85`). `common/game/serialize.cpp` bez zmian.
- Funkcje zewnętrzne skryptów (`common/game/gamescript.cpp`): nic nie dochodzi.

Mod i narzędzia (stan po Z1-Z3):

- `tools/get-krx.ps1` pobiera przypięty KrxImpExp, `Resolve-Blender` w `tools/lib/common.ps1`.
- `tools/anim.py`: MAN i MDH, format `.anim`, `extract` (kolejność archiwów jak w silniku), `roundtrip`
  (1038 animacji bajt w bajt), `snap`.
- `tools/anim.ps1` i `tools/blender/` (`rig.py`, `export.py`, `check.py`): `import`, `open`, `export`,
  `check`, `roundtrip` przez Blendera (1038 bajt w bajt). Akcja z importu ma właściwość `g25_anim`
  z nagłówkiem i slotami oryginału.
- `gothic25/content/Anims/` jest pusty (`.gitkeep`). `tools/pack.ps1` pakuje `content/`
  i `build/scripts/` (`pack.ps1:18-29`).
- `tools/fightlog.py` liczy `bonus.dir.<kierunek>`, ale nie liczy ciosów według kierunku. Raport
  dzieli przez zero, gdy przebieg nie ma ciosów bohatera (`fightlog.py:418`).

Dane gry (tylko odczyt, umowa licencyjna gry):

- `Anims.vdf` i `Anims_Addon.vdf`: `HUMANS.MDH` (34 węzły, checksum `0xC63488C2`), `HUMANS.MSB`
  (z dodatku) i 17 plików `HUMANS-*FIST*.MAN`. Nie ma `T_FISTATTACKL/R` w żadnym modelu ludzi ani
  pliku `*.EXT.MDS` w żadnym archiwum.
- Źródła MDK w kopii właściciela (`_work/Data/Anims/*.mds`, np. wzór ataku bocznego `t_1hAttackL`
  w `mds_overlay/Humans_1hST1.mds:173-180`) służą tylko jako wzorzec składni i zdarzeń. Nie
  kopiujemy ich do repozytorium (Z4).

## Projekt

### Silnik (C++)

Wszystkie zmiany w stylu OpenGothic. Każda działa tylko wtedy, gdy mod dostarcza dane: plik
rozszerzenia definicji albo animację ataku bocznego pięścią (ADR 0007, pkt 5, ADR 0008). Oryginalne
gry G1 i G2 nie mają ani jednego, ani drugiego (sprawdza K8 i K11).

0. **Dokładanie definicji** (ADR 0008).
   - `Resources::implLoadAnimation` po wczytaniu definicji modelu albo nakładki szuka pliku
     `<nazwa bez rozszerzenia>.EXT.MDS`, a gdy go znajdzie, ładuje go przez `zenkit::ModelScript::load`.
   - Wpisy łączy według nazwy, bez rozróżniania wielkości liter:
     - `animations`, `aliases` i `combinations`: wpis z rozszerzenia zastępuje każdy wpis oryginału
       o tej samej nazwie, także innego rodzaju (`ani` zamiast `aniAlias`), albo dochodzi;
     - `blends` według pary nazw;
     - `disabled_animations` i `model_tags` dochodzą.
   - `meshes` i `skeleton` z rozszerzenia są pomijane.
   - Animacje z rozszerzenia dostają znacznik pochodzenia (dla polecenia z pkt 5).
   - Log: jedna linia z nazwą pliku i liczbą dołożonych i zastąpionych wpisów.
1. **Wybór animacji.** W gałęzi pięści `AnimationSolver::implSolveAnim` `AttackL`/`AttackR` dają
   `T_FISTATTACKL`/`T_FISTATTACKR` (`solveFrm`). Gdy animacji nie ma, wynik to `nullptr`, jak dziś.
2. **Pytanie o animację.** Nowa metoda `Npc::hasFistSideAttack(Anim)` (albo w `MdlVisual`) sprawdza
   przez solver, czy model ma atak boczny pięścią w danym kierunku.
3. **Gracz.** W `PlayerControl` gałąź pięści obsługuje `ActLeft`/`ActRight` tak jak broń
   (`swingSwordL/R`, reset strafe), a `ActBack` zostaje blokiem. `Npc::swingSwordL/R` przy
   `WeaponState::Fist` nie wymagają broni. Bez animacji `doAttack` zwraca `false`, więc nic się nie
   dzieje, tak jak dziś.
4. **NPC.** `npc.cpp:1729` i `npc.cpp:1982` zamieniają cios boczny pięścią na `Anim::Attack`, tylko gdy
   model nie ma ataku w tym kierunku. `dropForwardAttacks(fist)` dostaje `fist && !sideAttacks`, więc
   przy limicie talentu sierpowe zostają w kolejce jak ataki boczne bronią. Okna combo, łączenie
   `CL_Side` i obrażenia bez premii działają bez zmian (Obecny stan).
5. **Konsola** (W9), dwie nowe pozycje w `Marvin` (wzór `C_Immortal`), `hero` albo instancja:
   - `play ani <postać> <animacja>`: `Npc::playAnimByName`;
   - `ani info <postać> <animacja>`: wypisuje definicję z modelu postaci, tak jak ją widzi gra:
     pochodzenie (oryginał albo rozszerzenie), warstwę, flagi, zakres klatek, liczbę klatek MAN,
     `next` i zdarzenia z klatkami.

   Gdy nie ma postaci albo animacji, polecenie zgłasza błąd, więc scenariusz kończy się z numerem
   linii.

Brak nowych funkcji zewnętrznych i nowych symboli skryptów.

### Skrypty (Daedalus)

Brak zmian. Dokumentacja:
- w `specs/001-combosy-npc-w-walce-wrecz/spec.md` (W1) zdanie o ciosach bocznych pięściami dostaje
  odwołanie do 004 W15;
- w `content/Scripts/README.md` w sekcji „Symbole dla silnika” dochodzi zdanie, że ataki boczne
  pięściami włącza animacja, a definicje moda plik `*.EXT.MDS` (ADR 0007, ADR 0008).

### Zasoby

Układ według ADR 0007 i ADR 0008:

```
gothic25/anims/
  README.md                  opis kroków dla autora (W11), lista animacji i plików, które włączają zachowania silnika
  anims.json                 modele: plik definicji moda -> nazwa w paczce, odbicia lustrzane
  HUMANS/
    HUMANS.EXT.MDS           definicje moda dla modelu ludzi (tylko własne wpisy, ASCII)
    HUMANS.skeleton.json     węzły, rodzice i checksum z HUMANS.MDH (opis budowy modelu)
    T_FISTATTACKL.blend      szkielet + akcja, bez siatek z gry (lekki, rzędu 100-200 kB)
    T_FISTATTACKL.anim       tekstowy eksport, źródło buildu
```

- **Sierpowy z lewej** zakładamy poleceniem `anim.ps1 new` na czystym szkielecie i kluczujemy sami
  w Blenderze przez MCP w oknie właściciela, który ogląda i ocenia.
  - Oryginalny `S_FISTATTACK` można obejrzeć obok (`anim.ps1 import`) jako wzorzec. Od 2026-11-04
    sierpowy może zaczynać się od oryginalnej postawy i przerabiać oryginalny ruch (spec. P9,
    ADR 0009).
  - Ok. 20-30 klatek przy 25 fps: postawa bojowa, obrót tułowia, łuk lewej ręki w poziomie, powrót.
- **Definicja w `HUMANS.EXT.MDS`**, wzorem budowy ataku bocznego broni:
  - `ani ("t_FistAttackL" 1 "" 0.0 0.2 M. "t_FistAttackL.anim" F 1 N)` z `DEF_HIT_LIMB "BIP01 L HAND"`,
    `DEF_OPT_FRAME`, `DEF_HIT_END`, `DEF_WINDOW` i `*eventSFX (… "WHOOSH" EMPTY_SLOT)`;
  - warstwa 1, tak jak `s_FistAttack`, bo `continueCombo` łączy tylko animacje tej samej warstwy;
  - wartości klatek z naszej animacji.
- **Sierpowy z prawej** nie ma źródła. Reguła `"T_FISTATTACKR": {"mirror": "T_FISTATTACKL"}`
  w `anims.json` sprawia, że build tworzy MAN i blok definicji z zamienionymi stronami (W14).
- **Format `.anim`** (ADR 0007, pkt 2, bez zmian od Z2):
  - nagłówek `g25-anim 1`, `model`, `fps`, `checksum`, lista węzłów;
  - opcjonalnie `quant` i `raw`/`layout`, tylko dla oryginałów w lokalnych testach;
  - klatki ze stałą liczbą miejsc po przecinku, przyciągnięte do siatki kwantyzacji MAN.
- **Wynik buildu** (`build/anims/_COMPILED/`, poza gitem):
  - `HUMANS-T_FISTATTACKL.MAN` i `HUMANS-T_FISTATTACKR.MAN`, z nagłówkiem MAN (nazwa, warstwa,
    `next`) z definicji moda, bo silnik bierze je z MAN (`animation.cpp:228`);
  - `HUMANS.EXT.MDS` z wpisami moda i wygenerowanymi blokami odbić.

### Narzędzia

- **`tools/anim.py`**, nowe polecenia:
  - parser binarnego MSB (układ chunków jak w ZenKit `ModelScriptBinary`) i tekstowego MDS
    (składnia jak w ZenKit `ModelScriptDsl`), dające wspólny model danych;
  - `defs <MODEL> [<ANI>...]`: połączone definicje oryginału z kopii gry i rozszerzenia moda,
    według reguł ADR 0008, z pochodzeniem każdego wpisu. Ten sam kod waliduje build;
  - `build`: `.anim` + `*.EXT.MDS` + `anims.json` -> `build/anims/`. Walidacja z W4:
    - szkielet zgodny ze `skeleton.json`;
    - liczba klatek równa zakresowi z definicji;
    - zdarzenia i okna combo w zakresie;
    - każda animacja z rozszerzenia ma MAN z buildu albo z gry, gdy dane gry są dostępne
      (podmiana samej definicji oryginału);
    - wynik deterministyczny (posortowane wejścia, stały format liczb, bez dat).

    Opcja `--extra <katalog>` dokłada lokalne dane testowe;
  - `mirror`: odbicie W14 (`W'_i = S·W_m(i)·S·C_i`, `S = diag(-1, 1, 1)`, `m` zamienia węzły L/R,
    stała korekta `C_i` z pozy spoczynkowej), także samodzielnie dla K12. Odbija też blok definicji
    (strony w `DEF_HIT_LIMB` i nazwach węzłów);
  - `check-pack` (K7): paczka moda kontra archiwa gry. Błąd przy pliku o nazwie definicji modelu z gry
    (`*.MSB`, pełne `*.MDS`), przy pliku identycznym z oryginałem i przy MAN, którego próbki są równe
    oryginałowi o tej samej nazwie;
  - `fixtures`: lokalne dane testowe do K4 i K11 w `build/anims-fixtures/`, z kopii gry gracza:
    - podmiana stania: oryginalny `S_RUN` z obrotem głowy, jak prototyp;
    - testowy `HUMANS.EXT.MDS` z nową animacją, podmienioną definicją i wpisem dla nakładki.

    Nic z tego nie trafia do repozytorium.
- **`tools/blender/rig.py` i `tools/anim.ps1`** (W16):
  - `anim.ps1 new -Anim <NAZWA>`: szkielet z MDH i pusta akcja z właściwością `g25_anim` bez danych
    oryginału: pochodzenie `mod`, węzły = kości modelu, nagłówek z MDH, bez slotów, bez `raw`;
  - import oznacza akcję jako pochodzenie `game`;
  - `export` do `anims/` odmawia akcji z pochodzeniem `game` (także po zmianie nazwy) i kieruje do
    `new`;
  - `-AllowDerived` pozwala na taki eksport tylko do katalogu w `build/` (dane testowe).
- **`tools/pack.ps1`**: przed pakowaniem woła `anim.py build`, a potem dokłada
  `--map build/anims=_WORK/DATA/ANIMS`. `test.ps1` pakuje moda, więc testy zawsze mają świeże
  animacje.
- **`tools/test.ps1`**: opcja `-AnimExtra <katalog>` przekazywana do `anim.py build --extra`, dla
  danych testowych z `anim.py fixtures`.
- **`tools/fightlog.py`**: miara `attacks.dir.<fwd|left|right|run|finish>` do oczekiwań (K13)
  i poprawka dzielenia przez zero w `techniques_section`.

### Testy

- `tests/004/`:
  - K4: `-AnimExtra build/anims-fixtures`, `play ani` i seria zrzutów;
  - K6: kopacz i dziennik, porównanie czasu trafień z klatkami definicji (`ani info`);
  - K8: wersje bez moda, `# mod: off`;
  - K11: `ani info` dla nowej, podmienionej, niezmienionej i nakładkowej animacji, z danymi
    testowymi, bez nich i bez moda. Oczekiwania z logu;
  - K12: zrzuty obu sierpowych;
  - K13: kopacz przez 2 min, `expect BDT_10027_Addon_Buddler attacks.dir.left >= 1` i to samo
    dla `right`;
  - `reczne/K05-sierpowe.txt`: bohater z pięściami i cel, który nie oddaje.
- Testy narzędzi (K1, K3, K7, K12, K14): polecenia `anim.py` i `anim.ps1` z kodem wyjścia i raportem.
  Do K3 trzy zepsute źródła w `tests/004/fixtures/broken/`. To nasze pliki: tekst `.anim`
  z czystego szkieletu i wpisy MDS.
- Regresja: `test.ps1 -Spec 001` i `-Spec 002` po zmianach w silniku (pkt 0 i pkt 1-4).

### Zapisy gry

Brak nowego stanu i zmian w `common/game/serialize.cpp`. Zapisy przechowują nazwy animacji warstw,
a `Pose::load` pomija nieznane (`pose.cpp:85`). Zapis z sierpowym wczytany bez moda nie zatrzyma
postaci (K9). Oryginalne definicje się nie zmieniają, więc stare zapisy wskazują te same animacje.

### Kolejność

1. Gotowe: Z1-Z4 (narzędzia bazowe, Blender, licencja).
2. Parsery MSB i MDS, `anim.py defs`, `build`, `pack`, `check-pack`, `new` i blokada eksportu
   pochodnych.
3. Silnik: pkt 0 (dokładanie), pkt 5 (`play ani`, `ani info`), pkt 1-4 (pięści), miara w raporcie.
4. Sierpowy z lewej w Blenderze, `mirror`, prawy, dane testowe i scenariusze K3-K14.
5. Dokumentacja: `anims/README.md`, `content/README.md`, `tests/README.md`, `NOTICE.txt`, 001 W1,
   `content/Scripts/README.md`, `gothic25/CLAUDE.md`.

## Pokrycie wymagań

| Wymaganie | Gdzie realizowane |
|---|---|
| W1 | `anims/<MODEL>/<ANI>.blend` + `.anim` (ADR 0007), `tools/blender/check.py`, `anim.ps1 check` |
| W2 | `anim.py extract`, `rig.py`, `anim.ps1 import` (wzorzec w `build/anims-work/`), `anim.ps1 new` |
| W3 | format `.anim`, `anim.py roundtrip`, `anim.ps1 roundtrip` (gotowe, Z2-Z3) |
| W4 | `anim.py build` (walidacja, determinizm), wywołanie z `pack.ps1` |
| W5 | MAN moda o nazwie oryginału, pakowany nad `Anims.vdf` (paczka moda ma priorytet) |
| W6 | `anims/HUMANS/HUMANS.EXT.MDS` i pliki nakładek, silnik pkt 0 |
| W7 | tylko pliki moda w paczce, silnik pkt 0, `anim.py check-pack`, `NOTICE.txt` |
| W8 | silnik pkt 1-3, definicje sierpowych (warstwa 1, okna combo) |
| W9 | silnik pkt 5 (`play ani`, `ani info`), scenariusze w `tests/004/` |
| W10 | `local.json` `blender`, `get-krx.ps1`, `$KrxCommit`, kontrole w `anim.ps1` (gotowe, Z1 i Z3) |
| W11 | `anims/README.md`, `content/README.md`, `tests/README.md` |
| W12 | warunek „są dane moda” w pkt 0-4, `Pose::load` bez zmian, K8, K9 |
| W13 | silnik pkt 0, `anim.py defs` (te same reguły), K11 |
| W14 | `anim.py mirror`, reguła w `anims.json`, blok definicji generowany w buildzie |
| W15 | silnik pkt 2 i 4, poprawka 001 W1, K13 i regresja 001 |
| W16 | `anim.ps1 new`, pochodzenie w `g25_anim`, blokada w `export`, `-AllowDerived` tylko do `build/`, `anim.py fixtures` |

## Bramka konstytucji

- [x] 1. **Tylko OpenGothic, warstwa najtańsza.** Narzędzia w Pythonie. Silnik tylko tam, gdzie
  licencja wymaga łączenia u gracza albo gdzie pięści są zablokowane na sztywno.
- [x] 2. **Mechanizmy w silniku, treść w modzie.** Silnik zyskuje ogólne mechanizmy: plik
  rozszerzenia definicji, ataki boczne pięściami, jeśli model je ma, polecenia konsoli. Animacje,
  definicje, zdarzenia i okna combo są w danych moda.
- [x] 3. **Fork łatwy do aktualizacji.** Zmiany w kilku miejscach, w stylu repozytorium. Bez pliku
  `*.EXT.MDS` i bez animacji `T_FISTATTACKL/R` zachowanie jest jak w upstreamie, a oryginalne gry
  tego nie mają (K8, K11). Włączanie przez dane zamiast symbolu skryptu opisują ADR 0007, pkt 5,
  i ADR 0008. Treść moda jest tylko w `gothic25/`.
- [x] 4. **Zapisy.** Brak nowego stanu. Nieznane animacje w zapisie są pomijane (`pose.cpp:85`, K9).
- [x] 5. **Kryteria sprawdzalne w grze.** K4, K6, K8, K11, K12 i K13 to scenariusze automatyczne. K5
  to scenariusz ręczny. K1, K3, K7 i K14 sprawdzają narzędzia z kodem wyjścia.
- [x] 6. **Prawa do zasobów.** Z4 ustaliło, że definicje z MDK i animacje z gry są na licencji gry.
  - W repozytorium i paczce są animacje moda (nowe albo zmienione oryginały, ADR 0009) i własne
    wpisy definicji. Niezmienione pliki z gry nie trafiają tam (W7, W16, K7, K14).
  - Niezmienione oryginały i dane testowe z nich zostają w `build/`.
  - `.blend` nie zawiera siatek z gry. Szkielet i `skeleton.json` opisują budowę modelu, do której
    animacja musi pasować.
  - Narzędzia (Blender, KrxImpExp, GPL) nie trafiają do paczki.
- [x] 7. **Język.** Plan, ADR i README po polsku. Kod, komentarze i commity po angielsku. `.ps1`
  w ASCII.
- [x] 8. **Wersja.** MINOR (0.2.0 -> 0.3.0): nowa funkcja, zapisy zgodne. Mod na starszym silniku
  się uruchomi, ale bez definicji moda (nowe animacje nie zadziałają) i bez ataków bocznych pięściami.
- [x] 9. **GothicMOD.** Animacje i definicje moda to nowe dane, które według EULA MDK są na GothicMOD.
  W `NOTICE.txt` dochodzi wpis o nich. Bez opłat.
- [x] 10. **Automatyzacja.** Build, walidacja, odbicie, łączenie definicji, kontrola paczki, dane
  testowe i testy działają bez interakcji, a build także bez Blendera. Blender działa bez okna
  z przypiętym dodatkiem.

  Ręczne zostaje tworzenie animacji w Blenderze (praca twórcza, nie powtarzalny krok) i ocena wyglądu
  w K2, K5 i K12, którą konstytucja zostawia człowiekowi.

## Odstępstwa od konstytucji

Brak. Włączanie zachowań danymi moda zamiast symbolem skryptu (odstępstwo od ADR 0003) opisują
i uzasadniają ADR 0007, pkt 5, i ADR 0008.

## Ryzyka

- **R1: licencja MDK. Rozstrzygnięte w Z4.** Wynik negatywny, plan przeszedł na ADR 0008 (pliki moda
  dokładane przez silnik, tylko własne animacje).
- **R2: reguła łączenia różni się od zachowania nakładek ZenGin.** Rozszerzenie działa jak „wpis
  według nazwy wygrywa”. Nakładki stylów walki nadal wygrywają z rozszerzeniem modelu, bo silnik
  szuka animacji najpierw w nakładkach, od ostatniej (`AnimationSolver::solveFrm`,
  `common/graphics/mesh/animationsolver.cpp:515-527`). Przypadek animacji dodanej do modelu
  i nakładki sprawdza K11. Kolejność opisuje `anims/README.md`.
- **R3: ZenKit czyta częściowy MDS** (bez `meshAndTree`) albo zgłasza ostrzeżenia. Sprawdzamy na
  pierwszym pliku rozszerzenia w pkt 0. W razie potrzeby rozszerzenie dostaje minimalny nagłówek
  `Model`, który silnik pomija.
- **R4: precyzja Blendera.** Sprawdzone w Z3: 1038 animacji bajt w bajt.
- **R5: odbicie przy niesymetrycznych osiach Biped.** Korekta `C_i` z pozy spoczynkowej powinna to
  pokryć. K12 porównuje odbity `t_1hAttackL` z `t_1hAttackR` (lokalnie, na oryginałach), a test
  podwójnego odbicia wykryje błąd wzoru.
- **R6: NPC zmieniają walkę na pięści** (W15). Kryteria 001 mogły zakładać ciosy boczne jako proste
  (001 K12). Regresja 001 po zmianach w silniku, a oczekiwania poprawiamy jawnie (K13).
- **R7: sierpowy od zera.** Bez kopiowania kluczy oryginału pierwsza animacja zajmie więcej czasu
  i może wyjść sztywna. Spec. dopuszcza zgrubną. Właściciel ocenia ją na podglądzie MCP przed
  buildem i w K5. **Zaszło 2026-11-04:** sierpowy od zera odstawał stylem, więc P9 zmieniono
  (ADR 0009) i kolejne wersje zaczynają się od oryginalnej postawy `S_FISTRUN`.
- **R8: `play ani` a AI postaci.** AI NPC może od razu przerwać odtwarzanie. Do zrzutów używamy
  bohatera albo NPC bez planu dnia.
- **R9: dostępność GitLab.** `get-krx.ps1` pobiera przez git. Archiwa www są za weryfikacją
  przeglądarki (Z1). Brak sieci kończy się komunikatem, a kopia z `.tools` wystarcza, dopóki commit
  się nie zmienia.
- **R10: nazwa `*.EXT.MDS`.** Gdyby inny mod albo przyszły upstream użył tej nazwy inaczej,
  mechanizm byłby niejednoznaczny. Przed zgłoszeniem do upstreamu konwencję trzeba uzgodnić.

## Alternatywy odrzucone

- **ASC z KrxImpExp jako źródło:** stratny (do 0,5°) i bez sceny Blendera (spec. P1).
- **Tylko `.blend`:** bez diffu, a build wymagałby Blendera, więc nie zadziała w CI (spec. P1).
- **Pełne definicje z MDK w paczce (pierwotny ADR 0007, pkt 3) i zapis binarnego MSB:** umowa
  licencyjna MDK na to nie pozwala (Z4, ADR 0008).
- **Własna nakładka nakładana przez skrypty:** musiałaby trafić do każdej postaci i starych zapisów,
  a o wyniku decydowałaby kolejność względem nakładek stylów walki (ADR 0008, spec. P2).
- **Przeróbki oryginalnych animacji w paczce:** odrzucone 2026-11-03 przez umowę licencyjną gry
  (spec. P9), przyjęte 2026-11-04 (ADR 0009).
- **Symbol skryptu włączający ataki boczne pięściami (ADR 0003):** konfiguracja w dwóch miejscach,
  bez korzyści, bo animacja i tak jest warunkiem (ADR 0007, pkt 5).
- **Instalacja KrxImpExp w profilu Blendera użytkownika:** niepowtarzalna i miesza się z ręczną pracą
  właściciela (spec. P6).
