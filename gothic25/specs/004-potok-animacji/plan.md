# Plan 004: Potok animacji

- **Specyfikacja:** [spec.md](spec.md)
- **Status:** Zatwierdzony
- **Utworzono:** 2026-11-03

## Podsumowanie

Potok zbudujemy głównie z narzędzi:
- `tools/anim.py` w czystym Pythonie czyta i zapisuje MAN, MDH, MSB i MDS, buduje animacje
  z tekstowego eksportu, odbija je lustrzanie i porównuje definicje z MDK z grą;
- skrypty Blendera uruchamiane bez okna importują oryginały i eksportują akcje do tekstu.

Definicje modelu ludzi to zmienione źródło `HumanS.mds` z MDK, zapisane w paczce jako `HUMANS.MSB`.
Silnik czyta je bez zmian. Zmiany w silniku są małe, a wszystkie zależą od istnienia animacji
w modelu:
- ataki boczne pięściami bohatera i NPC;
- polecenie konsoli, które odtwarza animację na postaci.

Pierwszą treścią są sierpowe: lewy zrobiony w Blenderze i prawy jako jego odbicie. Zasady wspólne
dla kolejnych funkcji z animacjami wydzielamy do [ADR 0007](../../decisions/0007-zrodla-i-budowanie-animacji-moda.md).

## Warstwa

- **Narzędzia i zasoby (większość pracy).** Formaty gry (MAN, MSB) zapisuje tylko nasze narzędzie,
  bo ani ZenKit, ani KrxImpExp ich nie zapisują. Narzędzie w Pythonie działa bez Blendera, w CI i
  z każdego skryptu (zasada 10). Definicje w tekście MDS nie wymagają zmian w silniku, bo ZenKit
  sam rozpoznaje format tekstowy.
- **Silnik (mała zmiana).** Pięści mają dziś ataki boczne zablokowane w silniku w pięciu miejscach
  (niżej). Treść, czyli animacje i ich zdarzenia, zostaje w danych moda, a silnik tylko przestaje
  zakładać, że pięści nie mają ataków bocznych. Bez animacji działa jak upstream. Zmiana jest ogólna
  i da się ją zgłosić do Try/OpenGothic.
- **Skrypty: bez zmian.** Style walki NPC (`FIGHT.DAT`) już dziś zlecają ciosy boczne pięściami
  (spec. W15).

## Obecny stan

Silnik:

- Definicje modelu: `Resources::implLoadAnimation` w `common/resources.cpp:667-687`. W trybie G2
  nazwa `.MDS` jest zamieniana na `.MSB` (`:672`), a `zenkit::ModelScript::load` (`:681`) sam
  rozpoznaje treść binarną albo tekstową (`lib/ZenKit/src/ModelScript.cc:436-446`). Tekstowy MDS
  zapisany jako `HUMANS.MSB` zadziała więc bez zmian.
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
- Konsola: tabela poleceń w konstruktorze `Marvin::Marvin` (`common/marvin.cpp:73-186`) (wzór obsługi z instancją: `C_Immortal`,
  `:521-531`), enum w `common/marvin.h:71-73`. Animację po nazwie odtwarza `Npc::playAnimByName`
  (`npc.cpp:995-997`). Scenariusze wykonują każde polecenie konsoli (003).
- Zapisy: `Pose::load` (`common/graphics/mesh/pose.cpp:70-90`) zapisuje nazwy animacji warstw,
  a przy wczytaniu pomija te, których model nie ma (`:85`). `common/game/serialize.cpp` bez zmian.
- Funkcje zewnętrzne skryptów (`common/game/gamescript.cpp`): nic nie dochodzi. `Mdl_ApplyOverlayMds`
  i pokrewne ładują nakładki tą samą drogą co model, więc tekstowe nakładki też zadziałają.

Mod i narzędzia:

- `gothic25/content/Anims/` jest pusty (`.gitkeep`). `tools/pack.ps1` pakuje `content/` i
  `build/scripts/` (`pack.ps1:18-29`), `mod.json` wyklucza źródła (`pack.exclude`).
- `tools/get-gdc.ps1` to wzór pobierania przypiętego narzędzia z SHA-256 do `.tools/`.
  `tools/lib/common.ps1` czyta `local.json` (`Get-LocalConfig`, `Get-Prop`).
- `tools/vdf.py` ma `list`, `extract` i `pack`. Przy wyciąganiu nie rozstrzyga, który plik obowiązuje,
  gdy `Anims_Addon.vdf` nadpisuje `Anims.vdf`: dodatek nadpisuje `HUMANS.MSB` i `HUM_BODY_NAKED0.MDM`.
- `tools/fightlog.py` liczy `bonus.dir.<kierunek>` (premia 002), ale nie liczy ciosów według kierunku.

Dane gry (tylko odczyt):

- `Anims.vdf` i `Anims_Addon.vdf`: `HUMANS.MDH` (34 węzły, checksum `0xC63488C2`), `HUMANS.MSB`
  i 17 plików `HUMANS-*FIST*.MAN`. Nie ma `T_FISTATTACKL/R` w żadnym modelu ludzi.
- Źródła MDK w kopii właściciela: `_work/Data/Anims/HumanS.mds` (cp1252, CRLF, 858 animacji; pięści
  w liniach 1040-1060) i `mds_overlay/*.mds` (np. wzór ataku bocznego `t_1hAttackL`
  w `Humans_1hST1.mds:173-180`: warstwa 1, jedno `DEF_HIT_END`, `DEF_WINDOW`, `DEF_HIT_LIMB`).

Prototyp (lokalnie, poza gitem, `gothic25/build/prototypes/idle-natural/`):

- `zen_anim.py`: odczyt i zapis MAN oraz MDH. Odczyt i ponowny zapis dał pliki bajt w bajt równe
  oryginałom (`S_RUN`, `S_1HATTACK`).
- `s7_apply_man.py`: MAN -> akcja Blendera, ze sprawdzoną konwencją kwaternionów i korzenia.
- `s11_idle.py`: poza Blendera -> MAN, odwrotność s7. `S_RUN` przeszedł MAN -> Blender -> MAN bajt
  w bajt.

## Projekt

### Silnik (C++)

Wszystkie zmiany w stylu OpenGothic. Każda działa tylko wtedy, gdy model ma animację ataku bocznego
pięścią (ADR 0007, punkt 5). Oryginalne modele G1 i G2 jej nie mają (sprawdza K8).

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
5. **Konsola: `play ani <postać> <animacja>`** (W9). Nowa pozycja w `Marvin` (`C_PlayAni`, wzór
   `C_Immortal`) woła `Npc::playAnimByName` (`hero` albo instancja). Błąd, gdy postaci albo animacji
   nie ma, więc scenariusz kończy się z numerem linii. To ogólne polecenie deweloperskie,
   do zgłoszenia upstreamowi razem z pkt 1-4.

Brak nowych funkcji zewnętrznych i nowych symboli skryptów.

### Skrypty (Daedalus)

Brak zmian. Dokumentacja:
- w `specs/001-combosy-npc-w-walce-wrecz/spec.md` (W1) zdanie o ciosach bocznych pięściami dostaje
  odwołanie do 004 W15;
- w `content/Scripts/README.md` w sekcji „Symbole dla silnika” dochodzi zdanie, że ataki boczne
  pięściami włącza animacja, a nie symbol (ADR 0007).

### Zasoby

Układ według ADR 0007:

```
gothic25/anims/
  README.md                  opis kroków dla autora (W11), lista animacji, które włączają zachowania silnika
  anims.json                 modele: plik MDS -> nazwa MSB, odbicia lustrzane, wymagane szkielety
  HUMANS/
    HumanS.mds               definicje z MDK, cp1252 + CRLF, zmiany moda w blokach "// G25 004 ..."
    HUMANS.skeleton.json     węzły, rodzice i checksum z HUMANS.MDH (pochodne, bez siatek)
    T_FISTATTACKL.blend      szkielet + akcja, bez siatek z gry (lekki, rzędu 100-200 kB)
    T_FISTATTACKL.anim       tekstowy eksport, źródło buildu
```

- **Sierpowy z lewej** robimy w Blenderze przez MCP w oknie właściciela, który ogląda i ocenia.
  Punkt wyjścia to `S_FISTATTACK` zaimportowany narzędziem: obrót tułowia, łuk lewej ręki w poziomie
  i powrót do postawy `S_FIST`. Długość ok. 20-30 klatek przy 25 fps, jak `t_1hAttackL`.
- **Definicja w `HumanS.mds`** obok pięści (linie 1040-1060 źródła), według wzoru `t_1hAttackL`:
  `ani ("t_FistAttackL" 1 "" 0.0 0.2 M. "<źródło>" F 1 N)`, z `DEF_HIT_LIMB "BIP01 L HAND"`,
  `DEF_OPT_FRAME`, `DEF_HIT_END`, `DEF_WINDOW` i `*eventSFX (… "WHOOSH" EMPTY_SLOT)`. Warstwa 1, tak
  jak `s_FistAttack`, bo `continueCombo` łączy tylko animacje tej samej warstwy.
- **Sierpowy z prawej** nie ma źródła. Reguła `"T_FISTATTACKR": {"mirror": "T_FISTATTACKL"}`
  w `anims.json` sprawia, że build tworzy MAN i blok definicji z zamienionymi stronami (W14).
- **Format `.anim`** (ADR 0007, pkt 2):
  - nagłówek `g25-anim 1`, `model`, `fps`, `checksum`, lista węzłów;
  - opcjonalnie `quant <min> <scale>` (float32 zapisany dokładnie) i `source` (metadane chunka
    źródła z oryginału), dzięki którym oryginały wracają bajt w bajt;
  - potem `frame N` i jedna linia na węzeł: `w x y z` z 7 miejscami i pozycja w cm z 5 miejscami.
    To o rząd wielkości dokładniej niż kwant MAN (rotacja ok. 3·10⁻⁵, pozycja ok. 2·10⁻³ cm),
    więc zapis i odczyt odtwarzają te same kody.
- **Wynik buildu** (`build/anims/_COMPILED/`, poza gitem):
  - `HUMANS-T_FISTATTACKL.MAN` i `HUMANS-T_FISTATTACKR.MAN`, z nagłówkiem MAN (nazwa, warstwa,
    `next`) z definicji, bo silnik bierze je z MAN (`animation.cpp:228`);
  - `HUMANS.MSB` z tekstem `HumanS.mds` i wstawionymi blokami odbić.

### Narzędzia

- **`tools/anim.py`** (biblioteka standardowa, jak `vdf.py`, `dat.py` i `fightlog.py`). Kod z prototypu
  przenosimy i porządkujemy. Polecenia:
  - `extract`: oryginały modelu z archiwów gry do `build/anims-work/`, z priorytetem jak w grze
    (dodatek nad podstawą, mod nad oboma);
  - `skeleton`: `HUMANS.skeleton.json` z MDH;
  - `to-text` / `from-text`: MAN <-> `.anim`;
  - `roundtrip`: K1 bez Blendera, MAN -> `.anim` -> MAN dla wszystkich animacji modelu i nakładek,
    z raportem;
  - `build`: `.anim` + definicje + `anims.json` -> `build/anims/`. Walidacja z W4:
    - szkielet zgodny ze `skeleton.json`;
    - liczba klatek równa zakresowi z definicji;
    - zdarzenia w zakresie;
    - każda animacja z definicji ma MAN z buildu albo z gry;
    - wynik deterministyczny (posortowane wejścia, stały format liczb, bez dat);
  - `mirror`: odbicie W14, także samodzielnie dla K12. Odbicie liczy się w przestrzeni modelu:
    `W'_i = S·W_m(i)·S·C_i`, gdzie `S = diag(-1, 1, 1)`, `m` zamienia węzły L/R, a stała korekta
    `C_i` jest liczona z pozy spoczynkowej. Dzięki niej działa także przy niesymetrycznych osiach
    kości Biped. Korzeń odbija się tak samo, więc ruch postaci zmienia stronę;
  - `mdk-diff` (K11): parser binarnego MSB i tekstowego MDS, porównanie animacji, flag, przejść,
    zakresów, zdarzeń, aliasów, połączeń i blokad. Raport różnic z nazwą animacji i pola;
  - `check-pack` (K7): zawartość paczki moda kontra archiwa gry (nazwy i SHA-256).
- **`tools/blender/`**, skrypty `bpy` uruchamiane z `anim.ps1`:
  - `rig.py`: import MDH+MDM przez KrxImpExp i MAN -> akcja (z s7). Sloty `ZS_*` jako obiekty
    z kluczami transformacji lokalnej, żeby oryginały wracały w całości;
  - `export.py`: akcje -> `.anim` (z s11);
  - `check.py`: ponowny eksport do katalogu tymczasowego i porównanie z `.anim` w repozytorium
    (W1, niezgodność to błąd);
  - zapis `.blend` bez siatek z gry; przy otwieraniu do podglądu `rig.py` dokłada ciało z kopii gry.
- **`tools/anim.ps1`** (Windows PowerShell 5.1, ASCII): `import`, `export`, `check`, `open`, `roundtrip-blender`.
  - Bierze `blender` z `local.json` i ustawia `BLENDER_USER_SCRIPTS=.tools/blender-scripts`.
  - Uruchamia `--background --factory-startup --python-exit-code 1`.
  - Przed konwersją sprawdza wersję Blendera (5.2.x) i commit KrxImpExp (`KRX_COMMIT.txt`) i kończy
    się komunikatem z poprawką (W10).
- **`tools/get-krx.ps1`**: przypięty commit (`$KrxCommit` w `common.ps1`, dziś `5be176c4…`)
  z gitlab.com/Patrix9999/krximpexp do `.tools/blender-scripts/addons/krximpexp/`. Pobiera przez git,
  bo archiwa www GitLab są za weryfikacją przeglądarki. SHA-256 liczy z plików bez zamiany końców
  linii.
- **`tools/pack.ps1`**: przed pakowaniem woła `anim.py build`, a potem dokłada
  `--map build/anims=_WORK/DATA/ANIMS`. `test.ps1` pakuje moda, więc testy zawsze mają świeże
  animacje.
- **`tools/test.ps1`**: opcja `-AnimExtra <katalog>` przekazywana do `anim.py build`. Dokłada źródła
  testowe tylko na czas przebiegu (K4: podmiana stania z `tests/004/fixtures/`, bez zmian w `anims/`).
- **`tools/fightlog.py`**: miara `attacks.dir.<fwd|left|right|run|finish>` do oczekiwań (K13).
- **`local.example.json`**: klucz `blender`.

### Testy

- `tests/004/`:
  - K4: `play ani` i seria zrzutów z `-AnimExtra`;
  - K6: kopacz i dziennik, porównanie czasu trafień z klatkami definicji;
  - K8: wersje bez moda, `# mod: off`;
  - K12: zrzuty obu sierpowych;
  - K13: kopacz przez 2 min, `expect BDT_10027_Addon_Buddler attacks.dir.left >= 1` i to samo
    dla `right`;
  - `reczne/K05-sierpowe.txt`: bohater z pięściami i cel, który nie oddaje.
- Testy narzędzi (K1, K3, K7, K11, K12): polecenia `anim.py` z kodem wyjścia i raportem.
  Do K3 trzy zepsute źródła w `tests/004/fixtures/broken/`.
- Regresja: `test.ps1 -Spec 001`, `-Spec 002`, `-Spec 003`:
  - po przejściu na definicje z MDK (jeszcze bez sierpowych): pokazuje, czy ZenKit czyta tekst tak
    samo jak binarny MSB;
  - po zmianach w silniku: sprawdza walkę z sierpowymi.

### Zapisy gry

Brak nowego stanu i zmian w `common/game/serialize.cpp`. Zapisy przechowują nazwy animacji warstw,
a `Pose::load` pomija nieznane (`pose.cpp:85`). Zapis z sierpowym wczytany bez moda nie zatrzyma
postaci (K9). Definicje z MDK są równoważne oryginałowi (W13), więc stare zapisy wskazują te same
animacje.

### Kolejność

1. `get-krx.ps1`, klucz `blender`, `anim.py` (MAN, MDH, `.anim`) i K1 bez Blendera.
2. Skrypty Blendera i `anim.ps1`, K1 przez Blendera i K2.
3. `mdk-diff` i K11. Potem `anims/HUMANS/HumanS.mds` bez zmian, `build` i `pack`, a na koniec
   regresja 001-003 na definicjach tekstowych.
4. Silnik: pkt 5 (`play ani`), potem pkt 1-4.
5. Sierpowy z lewej w Blenderze, definicja, `mirror`, K3-K13.
6. Dokumentacja: `anims/README.md`, `content/README.md`, `tests/README.md`, `NOTICE.txt`, 001 W1,
   `content/Scripts/README.md`.

## Pokrycie wymagań

| Wymaganie | Gdzie realizowane |
|---|---|
| W1 | `anims/<MODEL>/<ANI>.blend` + `.anim` (ADR 0007), `tools/blender/check.py`, `anim.ps1 check` |
| W2 | `anim.py extract`, `tools/blender/rig.py`, `anim.ps1 import` do `build/anims-work/` |
| W3 | format `.anim` z `quant`/`source`, `anim.py roundtrip`, `anim.ps1 roundtrip-blender` |
| W4 | `anim.py build` (walidacja, determinizm), wywołanie z `pack.ps1` |
| W5 | MAN z buildu o nazwie oryginału, pakowany nad `Anims.vdf` (paczka moda ma priorytet) |
| W6 | definicje w `anims/HUMANS/HumanS.mds` i nakładkach, build -> `HUMANS.MSB` (tekst) |
| W7 | definicje z MDK tylko zmienione, `NOTICE.txt`, `.blend` bez siatek, `anim.py check-pack` |
| W8 | silnik pkt 1-3, definicje sierpowych (warstwa 1, okna combo) |
| W9 | silnik pkt 5 (`play ani`), scenariusze w `tests/004/` |
| W10 | `local.json` `blender`, `get-krx.ps1`, `$KrxCommit`, kontrole w `anim.ps1` |
| W11 | `anims/README.md`, `content/README.md`, `tests/README.md` |
| W12 | warunek „model ma animację” w pkt 1-4, `Pose::load` bez zmian, K8, K9 |
| W13 | `anim.py mdk-diff`, regresja 001-003 na definicjach tekstowych |
| W14 | `anim.py mirror`, reguła w `anims.json`, blok definicji generowany w buildzie |
| W15 | silnik pkt 2 i 4, poprawka 001 W1, K13 i regresja 001 |

## Bramka konstytucji

- [x] 1. **Tylko OpenGothic, warstwa najtańsza.** Formaty dobrane pod nasz silnik (tekstowe definicje
  działają tylko dzięki ZenKit, nie w `Gothic2.exe`). Narzędzia w Pythonie, silnik tylko tam, gdzie
  pięści są zablokowane na sztywno.
- [x] 2. **Mechanizmy w silniku, treść w modzie.** Silnik zyskuje ogólną zdolność „ataki boczne
  pięściami, jeśli model je ma” i polecenie `play ani`. Animacje, ich zdarzenia i okna combo są
  w danych moda.
- [x] 3. **Fork łatwy do aktualizacji.** Zmiana w kilku miejscach, w stylu repozytorium. Bez
  animacji `T_FISTATTACKL/R` zachowanie jest jak w upstreamie. Oryginalne modele ich nie mają (K8).
  Włączanie przez animację zamiast symbolu skryptu opisuje ADR 0007, pkt 5. Treść moda jest tylko
  w `gothic25/`.
- [x] 4. **Zapisy.** Brak nowego stanu. Nieznane animacje w zapisie są pomijane (`pose.cpp:85`, K9).
- [x] 5. **Kryteria sprawdzalne w grze.** K4, K6, K8, K12 i K13 to scenariusze automatyczne. K5 to
  scenariusz ręczny. K1, K3, K7 i K11 sprawdzają narzędzia z kodem wyjścia.
- [x] 6. **Prawa do zasobów.** W repozytorium i paczce nie ma oryginalnych plików gry:
  - MAN z gry zostają w `build/anims-work/`;
  - `.blend` nie zawiera siatek z gry;
  - `skeleton.json` to dane pochodne (nazwy węzłów, checksum);
  - definicje z MDK są zmienione i na licencji GothicMOD;
  - narzędzia (Blender, KrxImpExp, GPL) nie trafiają do paczki.

  Warunek: licencja MDK (ryzyko R1).
- [x] 7. **Język.** Plan, ADR i README po polsku. Kod, komentarze i commity po angielsku. `.ps1`
  w ASCII.
- [x] 8. **Wersja.** MINOR (0.2.0 -> 0.3.0): nowa funkcja, zapisy zgodne. Mod działa na starszym
  silniku, tylko bez ataków bocznych pięściami.
- [x] 9. **GothicMOD.** Zmienione definicje z MDK i animacje na bazie oryginałów rozpowszechniamy na
  GothicMOD. W `NOTICE.txt` dochodzi wpis o definicjach animacji. Bez opłat.
- [x] 10. **Automatyzacja.** Build, walidacja, odbicie, porównanie z MDK, kontrola paczki i testy
  działają bez interakcji, a build także bez Blendera. Blender działa bez okna z przypiętym
  dodatkiem.

  Ręczne zostaje tworzenie animacji w Blenderze (praca twórcza, nie powtarzalny krok) i ocena wyglądu
  w K2, K5 i K12, którą konstytucja zostawia człowiekowi.

## Odstępstwa od konstytucji

Brak. Odstępstwo od ADR 0003 (włączanie animacją zamiast symbolem skryptu) opisuje i uzasadnia
ADR 0007, który przyjmujemy razem z tym planem.

## Ryzyka

- **R1: licencja MDK.** Plan zakłada, że tekstowe definicje z MDK są objęte GothicMOD, tak jak
  skrypty. Na początku etapu 3 sprawdzamy tekst licencji MDK i zapisujemy wynik w ADR 0007. Jeśli
  MDK jest wyłączone, ADR każe przejść na dokładanie definicji przez silnik (nowy ADR, zmiana planu).
- **R2: MDK różni się od danych Nocy Kruka.** Dodatek nadpisuje `HUMANS.MSB`, a MDK może być
  starsze. Wykrywa to `mdk-diff` (K11) przed użyciem w modzie. Różnice poprawiamy w definicjach
  i opisujemy w raporcie.
- **R3: ZenKit czyta tekst inaczej niż binarny MSB** (flagi, zdarzenia, aliasy). Wykrywają to regresja
  001-003 na definicjach tekstowych przed sierpowymi i log gry (ostrzeżenia parsera).
- **R4: precyzja Blendera.** Krzywe Blendera trzymają float32. Prototyp dał bajt w bajt dla `S_RUN`,
  ale duże przesunięcia korzenia albo długie animacje mogą trafić na granicę kwantu. K1 przez
  Blendera obejmuje wszystkie animacje ludzi. Gdyby coś odstawało, `rig.py` zapisuje próbki wprost
  we właściwościach akcji.
- **R5: odbicie przy niesymetrycznych osiach Biped.** Korekta `C_i` z pozy spoczynkowej powinna to
  pokryć. K12 porównuje odbity `t_1hAttackL` z `t_1hAttackR`, a test podwójnego odbicia wykryje błąd
  wzoru.
- **R6: NPC zmieniają walkę na pięści** (W15). Kryteria 001 mogły zakładać ciosy boczne jako proste
  (001 K12). Regresja 001 po zmianach w silniku, a oczekiwania poprawiamy jawnie (K13).
- **R7: jakość sierpowego.** Pierwsza animacja robiona przez Claude'a w Blenderze może być sztywna.
  Spec. dopuszcza zgrubną, a właściciel ocenia ją na podglądzie MCP przed buildem i w K5.
- **R8: `play ani` a AI postaci.** AI NPC może od razu przerwać odtwarzanie. Do zrzutów używamy
  bohatera albo NPC bez planu dnia, a w razie potrzeby polecenie ustawia stan bezczynności tylko
  na czas animacji.
- **R9: dostępność GitLab.** `get-krx.ps1` wymaga sieci i istnienia commitu. SHA-256 wykryje zmianę,
  a brak sieci kończy się komunikatem. Kopia z `.tools` wystarcza, dopóki commit się nie zmienia.
- **R10: konflikty w `HumanS.mds`.** Jeden duży plik definicji, który zmieniają kolejne funkcje.
  Zmiany oznaczamy blokami `// G25 NNN`, a `mdk-diff` umie pokazać różnice moda względem MDK.

## Alternatywy odrzucone

- **ASC z KrxImpExp jako źródło:** stratny (do 0,5°) i bez sceny Blendera (spec. P1).
- **Tylko `.blend`:** bez diffu, a build wymagałby Blendera, więc nie zadziała w CI (spec. P1).
- **Własna nakładka, dokładanie definicji przez silnik, zapis binarnego MSB:** odrzucone w spec. P2
  (ADR 0007). Pierwsza wymaga nakładania na każdą postać i stare zapisy. Druga to zmiana w silniku,
  której nie potrzebujemy. Trzecia to nowy format i oryginalne definicje w paczce.
- **Symbol skryptu włączający ataki boczne pięściami (ADR 0003):** konfiguracja w dwóch miejscach,
  bez korzyści, bo animacja i tak jest warunkiem (ADR 0007, pkt 5).
- **Instalacja KrxImpExp w profilu Blendera użytkownika:** niepowtarzalna i miesza się z ręczną pracą
  właściciela (spec. P6).
- **Parser definicji w C++ (narzędzie na ZenKit):** wierniejszy silnikowi, ale wymaga budowania
  silnika do zwykłego buildu moda. Zostajemy przy Pythonie, a wierność sprawdzają regresja 001-003
  i K6.
