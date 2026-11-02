# Plan 003: Scenariusze testowe i dziennik walki

- **Specyfikacja:** [spec.md](spec.md)
- **Status:** Zatwierdzony
- **Utworzono:** 2026-10-29

## Podsumowanie

Silnik dostaje w trybie deweloperskim trzy ogólne mechanizmy:
- wykonawcę scenariuszy, który po wczytaniu świata wykonuje plik poleceń konsoli z czekaniem
  na czas albo na zdarzenie walki,
- nowe polecenia konsoli: wywołanie funkcji skryptu, zapis, zrzut ekranu, wyjście, ekwipunek
  bohatera, przełącznik dziennika,
- dziennik walki wręcz w formacie JSON Lines.

Do tego dwie zmiany przydatne także poza testami: `-game:` przyjmuje ścieżkę bezwzględną, a mod
wczytuje się spoza folderu gry; `-save` przyjmuje ścieżkę pliku.

Po stronie narzędzi:
- `tools/test.ps1` pakuje moda z repozytorium, uruchamia grę w osobnym katalogu roboczym
  (ustawienia, zapisy i log nie mieszają się ze zwykłą grą), pilnuje limitu czasu i robi raport,
- `tools/fightlog.py` zamienia dziennik w raport i sprawdza oczekiwania ze scenariusza,
- scenariusze leżą w `gothic25/tests/<NNN>/`.

Zasady zaliczania kryteriów opisuje [ADR 0004](../../decisions/0004-zaliczanie-kryteriow-przez-scenariusze.md).

## Warstwa

**Silnik i narzędzia.** Skryptów i zasobów moda funkcja nie zmienia.

- **Zasoby nie wystarczą.** Funkcja nie dotyczy treści gry.
- **Skrypty nie wystarczą.**
  - Daedalus nie wczyta pliku scenariusza, nie zapisze gry, nie zrobi zrzutu ekranu i nie zamknie
    gry na żądanie z zewnątrz.
  - Nie widzi okna combo, momentu połączenia ani wyniku bloku. To stan animacji i walki w silniku.
  - Scenariusze w skryptach moda nie zadziałałyby bez moda (spec. W2, K4), a wpychałyby kod
    testowy do paczki dla graczy.
- **Narzędzia (PowerShell, Python)** budują paczkę, przygotowują katalog roboczy, uruchamiają grę
  i liczą raport. To nie musi siedzieć w silniku i łatwiej to zmieniać.

## Obecny stan

Ścieżki względem `common/`, chyba że podano inaczej.

**Start, mod i pliki**

- Opcje wiersza poleceń: `commandline.cpp:55-164`.
  - `-game:<ini>` zawsze daje `<gpath>/system/<ini>` (`commandline.cpp:186-188`), więc ścieżka
    bezwzględna nie działa.
  - `-save <n>` daje względną nazwę `save_slot_<n>.sav` (`commandline.cpp:71-80`).
  - `-nomenu` od razu startuje nową grę (`mainwindow.cpp:81-83`), a `-save` wczytuje zapis przy
    starcie (`mainwindow.cpp:77-80`).
- Paczki moda: `GameModDescriptor` (`gothic.cpp:35-83`) bierze listę z `[FILES] VDF` w `.ini`
  i szuka plików `.mod` tylko w `<gpath>/Data/**` (`gothic.cpp:69-82, 88-109`).
  - `Resources::mountVdfs` przyjmie dowolną ścieżkę bezwzględną (`resources.cpp:124-161`).
  - Przy konflikcie nazw wygrywa archiwum z nowszym znacznikiem czasu w nagłówku.
- Pliki zależne od katalogu roboczego:
  - `log.txt` (`game/main.cpp:85`), `crash.log` (`utils/crashlog.cpp:152`),
  - własny `Gothic.ini` OpenGothica (`gothic.cpp:153`, nakładany na tylko do odczytu
    `<gpath>/system/Gothic.ini`, `gothic.cpp:152`),
  - zapisy `save_slot_<n>.sav` (`ui/gamemenu.cpp:1014-1033, 1083-1115`).

  Silnik nie wymaga, żeby katalog roboczy był katalogiem `.exe`: shadery są wkompilowane, a dane
  gry pochodzą z `-g`.
- Okno: `MainWindow` tworzy okno zmaksymalizowane (`mainwindow.cpp:33`), a bez `-window` przełącza
  na pełny ekran (`mainwindow.cpp:48-50`). Tempest w trybie `Normal` tworzy na Windowsie okno
  800×600 (`lib/Tempest/Engine/system/api/windowsapi.cpp:192-194`). Innego rozmiaru okna nie da się
  ustawić bez zmian w Tempeście, który jest podmodułem.
- Filmy:
  - Nowa gra puszcza ze skryptów `INTRO.BIK` i `Addon_Title.BIK`
    (`gothic25/content/Scripts/Content/Story/Startup.d:4710-4711`).
  - `[GAME] scaleVideos=-1` w `Gothic.ini` wyłącza wszystkie filmy (`ui/videowidget.cpp:258-265`).

**Konsola i skrypty**

- Konsola (Marvin):
  - Tabela poleceń: `marvin.cpp:60-153`, wykonanie: `marvin.cpp:257-482`.
  - Najwyżej 4 argumenty, każdy jednym słowem (`marvin.h`, `CmdVal::argv[4]`, `marvin.cpp:156-214`).
  - `save game` to pusta pozycja (`marvin.cpp:110`).
  - `insert` zwraca tylko `bool` i wstawia NPC w miejscu bohatera (`marvin.cpp:432-438, 484-510`).
  - Sygnał `print` używają tylko `p` i `set var`.
  - Marvina posiada `ConsoleWidget` (`ui/consolewidget.h:39`). Działa tylko z `-devmode`
    (`gothic.cpp:145`).
- Wywoływanie funkcji skryptów:
  - `call_function` z ZenKita ma liczbę argumentów ustaloną przy kompilacji.
  - Przy liczbie argumentów znanej dopiero w trakcie działania trzeba wypchnąć argumenty
    (`push_int`, `push_string`, `push_instance`) i wywołać `unsafe_call`
    (`lib/ZenKit/include/zenkit/DaedalusVm.hh:320-332, 640`).
  - Typy parametrów podaje `find_parameters_for_function`.
  - Funkcji zewnętrznych (`CreateInvItems`, `EquipItem`) nie da się tak wywołać: VM obsługuje je
    tylko opkodem `BE` (`lib/ZenKit/src/DaedalusVm.cc:253-275`).
  - Błędy wewnątrz skryptu łapie łagodny handler (`game/gamescript.cpp:97`), ale błędy wywołania
    (zły symbol, liczba lub typ argumentów) lecą wyjątkiem.
  - `self` i `other` ustawia `ScopeVar` (`game/gamescript.cpp:23-36`).
  - NPC po instancji znajduje `World::findNpcByInstance(id, n)` (`world/worldobjects.cpp:469-478`).
    Nowo wstawiony NPC jest ostatnim trafieniem.
- Zapis, wyjście, zrzut ekranu:
  - Zapis idzie przez `Gothic::save` → `onSaveGame` → `MainWindow::saveGame` (`gothic.cpp:655-657`,
    `mainwindow.cpp:1089-1139`).
  - `saveGame` po cichu nic nie robi w dialogu i w przerywniku (`mainwindow.cpp:1090-1093`) i zapisuje
    w osobnym wątku. Po zakończeniu znów wywołuje `onWorldLoaded` (`gothic.cpp:536-550`).
  - Wyjście: `Tempest::SystemApi::exit()` (`ui/gamemenu.cpp:947-950`).
  - Zrzut ekranu: `F11` zapisuje `dbg.png` przez `renderer.screenshoot`, `readPixels` i `Pixmap::save`
    (`mainwindow.cpp:476-480`). Obraz zawiera tylko scenę 3D, bez interfejsu i konsoli
    (`graphics/renderer.cpp:2711-2732`).
- Pętla i czas:
  - `MainWindow::tick` (`mainwindow.cpp:890-951`) woła `Gothic::inst().tick(dt)` (`mainwindow.cpp:940`)
    tylko w grze, bez pauzy i wczytywania.
  - `GameSession::tickCount()` to czas gry w ms z uwzględnieniem `ztimer multiplyer`
    (`game/gamesession.cpp:305-320, 357-359`).
  - `dt` klatki jest przycinane do 50 ms przed pomnożeniem.

**Walka wręcz**

- Początek ciosu NPC i gracza:
  - Wspólny punkt: `Npc::doAttack` (`world/objects/npc.cpp:3877-3896`) → `MdlVisual::continueCombo`
    → `Pose::continueCombo` (`graphics/mesh/pose.cpp:728-787`).
  - `doAttack` zwraca `true` także wtedy, gdy ta sama animacja dalej gra, a nowego ciosu nie ma
    (`pose.cpp:175-178`). Tak jest przy klikaniu gracza.
  - Połączenie do przodu przeskakuje animację (`pose.cpp:783-784`). Połączenie w bok zaczyna nową
    animację (`pose.cpp:777-781`). Brak okna kończy combo (`pose.cpp:763-771`).
  - Etap combo: `Pose::comboInfo` (`pose.cpp:793-815`).
- NPC:
  - Pierwszy cios kroku FAI: `Npc::implAttack` (`npc.cpp:1710-1718`).
  - Połączenie w oknie: `Npc::implComboLink` (`npc.cpp:1884-1956`, cios w 1945-1954).
  - Gracz: `PlayerControl::implMove` (`game/playercontrol.cpp:783-838`).
- Seria:
  - `FightAlgo::fillQueue` losuje ruch FAI (`game/fightalgo.cpp:33-110`).
  - `nextFromQueue` rozwija go w kolejkę `tr[]` (`fightalgo.cpp:112-210`), po czym kasuje rodzaj ruchu
    (`fightalgo.cpp:207`). Nigdzie nie zostaje informacja, że to np. 2. cios serii potrójnej.
  - Czyszczenie kolejki: `onClearTarget`, `onTakeHit`, `onBreakSeries`, `dropForwardAttacks`
    (`fightalgo.cpp:230-252`).
- Wynik ciosu:
  - Pudło: `Npc::commitDamage` (`npc.cpp:2083-2091`): brak celu, poza zasięgiem, poza kątem.
  - Blok i odskok: `Npc::takeDamage(Npc&, const Bullet*)` (`npc.cpp:2093-2115`).
  - Trafienie: `Npc::takeDamage(...)` (`npc.cpp:2132-2209`). Kolejno: percepcja `ASSESSDAMAGE`,
    `onTakeHit`, obrażenia z `DamageCalculator::damageValue` (`game/damagecalculator.cpp:127-187`),
    zachwianie (`npc.cpp:2169-2183`), punkty życia (`npc.cpp:2192`).
  - `DamageCalculator::Val` niesie tylko wartość i flagi trafienia.
  - Rzeczywista utrata życia może być inna niż wartość obrażeń: tryb `cheat god`, nieśmiertelni NPC
    (`npc.cpp:1241-1270`).
- Upadek, nieprzytomność, śmierć: `Npc::onNoHealth` (`npc.cpp:595-631`), odrzut `FLY`
  (`npc.cpp:2186-2188`).
- Dane postaci:
  - instancja: `Npc::instanceSymbol()`, imię: `displayName()`,
  - styl walki: `handle().fight_tactic`,
  - poziom talentu: `talentSkill`, procent: `hitChance`,
  - broń: `activeWeapon()`.

**Znalezisko poza zakresem 003.** `FightAlgo::onClearTarget` czyści tylko `tr[0]`
(`fightalgo.cpp:236-239`), a rozwinięcie nowego ruchu nadpisuje tylko jego własne pozycje. Po
utracie celu w środku serii resztka starej serii zostaje więc za nowym ruchem. Pojedynczy cios
może wtedy urosnąć w kilkuciosową serię. Dotyczy to upstreamu, ale przy dłuższych seriach z 001
występuje częściej. Dziennik walki to pokaże. Poprawka należy do 001 i nie wchodzi w ten plan.

## Projekt

### Silnik (C++)

Wszystko poza grupą T1 działa tylko z `-devmode`. Nowy kod trafia do nowych plików tam, gdzie
się da. Zmiany w istniejących plikach to krótkie zaczepienia. Grupy są pomyślane jako osobne
commity, które da się osobno zgłosić do upstreamu.

**T1. Mod spoza folderu gry i zapis spod ścieżki** (W2). Ogólne opcje, bez `-devmode`.

- `-game:` przyjmuje ścieżkę bezwzględną do `.ini`. Wtedy archiwa z `[FILES] VDF` są szukane
  najpierw w `<katalog .ini>/../Data/**`. To układ `gothic25/build/game` z `tools/pack.ps1`.
- Archiwum `.mod` o tej samej nazwie w folderze gry jest wtedy pomijane, więc zainstalowany tam mod
  nie bierze udziału w teście.
- Ścieżka względna działa jak dotąd.
- `-save` przyjmuje też ścieżkę do pliku (gdy argument zawiera separator albo kończy się na `.sav`).
  Liczba i `q` działają jak dotąd.

**T2. Małe okno** (W2). Nowa opcja wiersza poleceń, np. `-window small`, tworzy okno w trybie
Tempesta `Normal` (800×600 na Windowsie) zamiast zmaksymalizowanego. Zob. „Różnice względem
specyfikacji”.

**T3. Nowe polecenia konsoli** (W3, W4). Każde polecenie wypisuje wynik albo błąd przez `print`:

- `call <funkcja> [argumenty...]`:
  - Własne dzielenie linii, bo limit 4 argumentów konsoli nie wystarcza. Liczba argumentów musi się
    zgadzać z funkcją.
  - Argument dobierany jest według typu parametru:
    - `int`: liczba, stała `int` ze skryptów albo nazwa instancji (wtedy jej numer symbolu, jak
      w `Hlp_GetNpc`),
    - `float`: liczba,
    - `string`: słowo,
    - `C_NPC`: `hero` albo nazwa instancji (ostatnio wstawiony NPC tej instancji, przez
      `findNpcByInstance`).
  - Wywołanie przez `push_*` i `unsafe_call`, z `self = hero` i `other = cel bohatera`
    (`ScopeVar`), w `try/catch`. Zwracana wartość jest wypisywana.
  - Funkcje zewnętrzne są odrzucane z czytelnym komunikatem.
- `give <instancja przedmiotu> [ile]` i `equip <instancja przedmiotu>`: ekwipunek bohatera
  (`Npc::addItem`, `Npc::useItem`). Potrzebne, bo `CreateInvItems` i `EquipItem` są zewnętrzne.
- `info told <instancja C_INFO>` (dopisane 2026-10-30): kwestia liczy się jako przegadana
  z bohaterem (`GameScript::setNpcInfoKnown`), więc ważny dialog, np. `DIA_Xardas_Hello` na starcie
  nowej gry, nie zaczepia bohatera. Bez tego K1 (tryb ręczny bez wejścia od gracza) nie przejdzie.
- `insert` (zmiana z 2026-10-30): postać albo przedmiot pojawia się 2 m przed bohaterem, a przy
  ścianie tuż przed nią (promień fizyki), zamiast w miejscu bohatera. Duże postacie utykały w nim.
- `immortal <instancja>` (dopisane 2026-10-30): flaga `NPC_FLAG_IMMORTAL` postaci, którą
  `Npc::changeAttribute` już respektuje. Paladyn zabija bandytę w kilku ciosach, więc bez tego walki
  NPC z NPC z 001 K5 i K7 trwałyby za krótko na obserwację serii, obrony i przerwań.
- `remove npc <instancja> <promień w m>` (dopisane 2026-10-30): postacie tej instancji w promieniu
  od bohatera opuszczają świat (`World::removeNpc`). Scenariusze 001 przeniesione spod wieży Xardasa
  na `NW_PASS_05` (Z27) muszą usunąć młode wilki z `NW_PASS_06`, które dołączają do walki,
  a `B_RemoveNpc` trafia tylko w ostatnio utworzoną postać instancji `YWolf` w całym świecie. Brak
  takich postaci w promieniu to błąd, żeby scenariusz w złym miejscu nie przeszedł po cichu.
  Usuwanie wilków w `Startup.d` odpada: zmieniłoby grę dla graczy i nie działa bez moda.
- `save game <slot>`:
  - zastępuje pustą pozycję,
  - przed zapisem sprawdza warunki z `MainWindow::saveGame` (dialog, przerywnik) i zgłasza błąd,
    zamiast milczeć.
- `screenshot <plik>`: nowy sygnał w `Gothic`, obsługa w `MainWindow` jak `F11`, zapis PNG.
  Ścieżka względna trafia do katalogu wyników (T5).
- `quit`: `SystemApi::exit()`.
- `toggle fightlog`: włącza i wyłącza dziennik walki (T6).

**T4. Wykonawca scenariuszy** (W1, W2, W7). Nowe pliki `game/scenariorunner.*`. Obiekt należy do
`MainWindow`, ma własną instancję Marvina i wiąże jej `print` z logiem.

- `-scenario <plik>`: plik jest wczytywany i sprawdzany przy starcie. Każda linia pamięta swój
  numer. Linie `#` i `expect ...` silnik pomija, bo oczekiwania sprawdza raport.
- Start po pierwszym `onWorldLoaded` (nowa gra albo `-save`). Kolejne `onWorldLoaded` po zapisie
  nie restartują scenariusza.
- Krok wykonywany jest w `MainWindow::tick` po `Gothic::inst().tick(dt)`, więc nie w pauzie,
  wczytywaniu ani filmie. Po `save game` scenariusz czeka, aż zapis się skończy, i sprawdza, czy
  plik powstał.
- Polecenia sterujące:
  - `wait <sekundy>`: czas gry z `GameSession::tickCount()`, więc skraca się przy przyspieszeniu,
  - `wait <instancja|hero> <zdarzenie> [n] timeout <sekundy>`: zdarzenia z dziennika walki T6,
    takie jak `series` (początek serii), `series-hit n`, `combo n`, `down`, `unconscious`, `dead`,
  - `quit` (zmiana z 2026-10-30): kończy scenariusz. W trybie automatycznym gra kończy się razem
    z nim, a w ręcznym zostaje otwarta (W2, K1). Wcześniej `quit` zamykał grę także w trybie
    ręcznym, więc scenariusze 001 nie nadawały się do K1. Polecenie konsoli `quit` (T3) nadal
    zamyka grę.
- `-scenario-exit` (tryb automatyczny): po ostatniej linii i przy pierwszym błędzie gra się kończy.
  Bez tej opcji (tryb ręczny) błąd trafia do konsoli i logu, a gra działa dalej.
- Plik statusu `scenario.json` w katalogu wyników: wynik, numer linii, komunikat, czas gry.
  Polecenie testu czyta ten plik, bo kod wyjścia gry nie niesie wyniku.

**T5. Katalog wyników** (W4, W6). Opcja `-results <katalog>`. Silnik zapisuje tam dziennik walki,
zrzuty ekranu i `scenario.json`, a katalog zakłada dopiero przy pierwszym zapisie. Bez tej opcji
pliki trafiają do katalogu roboczego.

**T6. Dziennik walki** (W4, W5, W8). Nowe pliki `game/fightlog.*`. Format JSON Lines: jedno
zdarzenie w linii, stałe pola, `t` w ms czasu gry.

- Zdarzenia:
  - `attack`: kto, kogo, styl, broń, talent, kierunek, etap combo, seria (rodzaj, numer serii,
    pozycja), źródło (kolejka, kontynuacja combo, gracz), połączenie (rodzaj: nowy, do przodu,
    w bok; część okna w %; pominięte ms animacji),
  - `result`: pudło z przyczyną, blok, odskok, trafienie z obrażeniami i życiem przed i po,
  - `break`: przerwanie serii lub combo z przyczyną: blok, zachwianie, cel leży, cel poza zasięgiem,
    obrona w serii, limit talentu, brak okna,
  - `state`: zachwianie, odrzut, nieprzytomność, śmierć,
  - `marker`: zapis, zrzut ekranu, linie scenariusza (do K6 i do czytania raportu).
- Zaczepienia:
  - `Npc::doAttack`. `Pose::continueCombo` zapamiętuje wynik ostatniego żądania: nowy cios,
    połączenie do przodu, połączenie w bok, odrzucone, pominięte ms. Dzięki temu dziennik nie liczy
    ciosów, których nie było.
  - `FightAlgo` dostaje pola przejściowe bez zapisu: rodzaj ruchu, numer serii, długość i pozycja.
    Ustawia je `nextFromQueue` przed skasowaniem `queueId`, przesuwa `consumeAction`.
  - `commitDamage` (pudło), oba `takeDamage` (blok, odskok, trafienie), `onNoHealth`, zachwianie.
  - Miejsca wywołań `onTakeHit`, `onBreakSeries`, `onClearTarget`, `dropForwardAttacks` w `Npc`
    (przyczyny przerwań). `dropForwardAttacks` loguje tylko wtedy, gdy kolejka faktycznie się zmieni.
- Dziennik tylko czyta stan:
  - nie losuje (nie rusza generatora liczb losowych),
  - nie zmienia kolejności zdarzeń,
  - przy wyłączonym dzienniku każde zaczepienie kończy się na jednym sprawdzeniu flagi (W8).
- Wykonawca scenariuszy subskrybuje zdarzenia dziennika, żeby obsłużyć czekanie na zdarzenie.

### Narzędzia

**`tools/test.ps1`** (W2, W6, W7, W12). Windows PowerShell 5.1, sam ASCII.

- Parametry:
  - `-Scenario <ścieżka albo NNN/nazwa>` albo `-Spec <NNN>` (wszystkie scenariusze z `tests/NNN/`
    po kolei, z podsumowaniem),
  - `-NoMod`, `-Save <plik>`, `-Manual`, `-TimeoutSec`, `-GothicDir`, `-BuildDir`.
- Kroki:
  1. Z modem: `tools/build-scripts.ps1` i `tools/pack.ps1`. Paczka powstaje w
     `gothic25/build/game` z bieżących plików, także niezacommitowanych. Folder gry nie jest ruszany.
  2. Profil testowy `gothic25/build/test/profile` jako katalog roboczy gry:
     - `Gothic.ini` to kopia `build/opengothic/Gothic.ini` użytkownika (zwykłe ustawienia,
       z dźwiękiem) z dopisanym `[GAME] scaleVideos=-1`,
     - plik powstaje od nowa przed każdym przebiegiem, więc ustawienia z testu nie wracają do zwykłej
       gry,
     - zapisy testów zostają w profilu, osobno od zapisów zwykłej gry, i są widoczne w menu
       kolejnych przebiegów (K6).
  3. Katalog wyników `gothic25/build/test-runs/<data-czas>-<NNN>-<nazwa>[-nomod]` z kopią
     scenariusza i `meta.json`: commit, czy drzewo czyste, z modem czy bez, argumenty.
  4. Start `Gothic2Notr.exe` z katalogiem roboczym w profilu i argumentami:
     - `-g`, `-devmode`, `-nomenu` albo `-save`, `-scenario`, `-results`,
     - z modem: `-game:<ścieżka bezwzględna do .ini>`,
     - w trybie automatycznym: `-window small` i `-scenario-exit`.
  5. Czekanie z limitem czasu rzeczywistego. Domyślny limit pochodzi z nagłówka scenariusza
     (`# timeout:`), a bez nagłówka wynosi 600 s. Po przekroczeniu gra jest zamykana siłą.
  6. Kopia `log.txt` i `crash.log` do wyników, raport przez `fightlog.py`, podsumowanie na ekranie,
     kod wyjścia 0 albo 1.
- `tools/run.ps1 -Dev` dostaje `-results` z nowym katalogiem wyników, żeby dziennik włączony
  w zwykłej grze deweloperskiej trafiał tam samo (W4, K12).

**`tools/fightlog.py`** (W5, W12). Python 3, sama biblioteka standardowa.

- `report <katalog>` tworzy `report.md`. Dla każdej postaci:
  - ciosy, serie według rodzaju, rozkład długości combo do przodu i najdłuższe combo,
  - moment połączenia (najwcześniejszy, średni, najpóźniejszy) i pominięte ms,
  - przerwania według przyczyny, bloki, odskoki, trafienia, obrażenia według etapu combo.
- Nazwy stylów walki raport bierze ze stałych `FAI_*` w `AI_Constants.d`.
- `check` liczy oczekiwania `expect <kto> <miara> <op> <wartość>` ze scenariusza.
  - Przykładowe miary: `hits`, `combo.max`, `combo.count.N`, `series.<RODZAJ>`, `break.<przyczyna>`,
    `blocks`, `skip.max_ms`, `damage.stage.N.avg`.
  - Wynik: zaliczone albo niezaliczone, z wartością faktyczną. Kod wyjścia 1 przy niezaliczonym.

**Scenariusze** (W9, W12):
- `gothic25/tests/<NNN>/<Kn>-<nazwa>.txt` z nagłówkiem `# criterion: NNN Kn` i `# timeout:`.
- `gothic25/tests/README.md` to instrukcja: format, polecenia, oczekiwania, uruchamianie, czytanie
  raportu.
- Scenariusze dla 001:
  - K1, K2, K4, K7, K10, K12: obserwacja z `ztimer multiplyer` najwyżej 2, zob. ryzyka,
  - K3: część liczbowa, czyli pominięte ms,
  - K5 i K7: NPC kontra NPC,
  - K6: bohater bez `cheat god`,
  - K8: K1 z `-NoMod`,
  - K9: zapis w środku serii, wczytanie zapisu z Z1 i nowego zapisu,
  - K11: odsunięcie bohatera po pierwszym ciosie serii.
- Atak NPC na bohatera: `call B_Attack <NPC> hero 0 0` (`AR_NONE = 0`). Miejsce: spokojny waypoint
  w Khorinis, wybrany przy implementacji i potwierdzony zrzutem ekranu.

### Proces

- [ADR 0004](../../decisions/0004-zaliczanie-kryteriow-przez-scenariusze.md): zaliczanie kryteriów
  raportem, wpisy do „Weryfikacji”, zgoda na tryb automatyczny. Przyjmowany razem z tym planem.
- Gdy narzędzie będzie gotowe:
  - zdanie w zasadzie 5 konstytucji,
  - opis weryfikacji w `sdd/workflow.md` i w `.claude/commands/g25-verify.md`,
  - zgoda na tryb automatyczny i opis uruchamiania w `gothic25/CLAUDE.md` (W11),
  - wpis w `CHANGELOG.md`.

### Skrypty (Daedalus)

Brak zmian. Scenariusze wywołują istniejące funkcje (`B_RaiseFightTalent`, `B_Attack`).

### Zasoby

Brak.

### Zapisy gry

Brak nowego stanu. Nowe pola `FightAlgo` (rodzaj i pozycja serii) są przejściowe i nie trafiają
do zapisu, tak jak pola łączenia z 001. Po wczytaniu dziennik zaczyna serię od nowa. `save game`
używa tej samej ścieżki co menu. Wersja zapisu bez zmian.

## Pokrycie wymagań

| Wymaganie | Gdzie realizowane |
|---|---|
| W1 | T4 (plik, czekanie na czas i zdarzenie, `quit`, komentarze), T6 (zdarzenia do czekania) |
| W2 | `test.ps1` (z modem albo bez, zapis, tryby, pakowanie), T1 (mod spoza gry, `-save` ze ścieżki), T2 (małe okno), profil testowy (ustawienia, zapisy osobno, `scaleVideos=-1`) |
| W3 | T3 (`call`, `save game`, `screenshot`, `quit`, do tego `give` i `equip`) |
| W4 | T6 (zdarzenia i zaczepienia), T3 `toggle fightlog`, T5 i `run.ps1 -Dev -results` |
| W5 | `fightlog.py report`, format JSON Lines z T6 |
| W6 | T5 i katalog przebiegu w `test.ps1` (`gothic25/build/` jest w `.gitignore`) |
| W7 | T4 (błędy z numerem linii, `scenario.json`, wyjście w trybie automatycznym), limit czasu w `test.ps1` |
| W8 | wszystko poza T1 i T2 tylko z `-devmode`; dziennik tylko czyta stan; T1 i T2 nie zmieniają zachowania bez nowych argumentów |
| W9 | `gothic25/tests/001/*`, `gothic25/tests/README.md`, `g25-verify` i `sdd/workflow.md` |
| W10 | ADR 0004, zasada 5, `meta.json` (commit, czyste drzewo) |
| W11 | ADR 0004, `gothic25/CLAUDE.md` po dostarczeniu narzędzia |
| W12 | `fightlog.py check`, `test.ps1 -Spec`, oczekiwania w scenariuszach 001 |

## Bramka konstytucji

- [x] 1. **Najniższa wystarczająca warstwa.** Skrypty nie uruchomią pliku scenariusza, nie zapiszą
  gry, nie zrobią zrzutu i nie widzą okna combo (zob. „Warstwa”). Logikę, której silnik nie
  potrzebuje, robią narzędzia.
- [x] 2. **Silnik daje mechanizmy, skrypty decydują o treści.** Silnik daje ogólne mechanizmy
  (wykonawca, polecenia, dziennik). Treść testów, czyli kto, gdzie i czego oczekujemy, leży
  w scenariuszach w `gothic25/tests`.
- [x] 3. **Fork łatwy do aktualizacji.**
  - T3–T6 działają tylko z `-devmode`, a T1 i T2 tylko po podaniu nowych argumentów.
  - Nowy kod jest w nowych plikach, Tempest i ZenKit są nietknięte.
  - Grupy T1–T6 da się zgłosić upstreamowi osobno.
  - W silniku nie ma treści moda.
- [x] 4. **Zapisy gry.** Brak nowego stanu, wersja zapisu bez zmian.
- [x] 5. **Kryteria sprawdzalne w grze.** K1–K12 mają kroki w grze. Funkcja doprecyzowuje zasadę 5
  przez ADR 0004.
- [x] 6. **Prawa do zasobów.** Brak nowych zasobów.
- [x] 7. **Język.** Dokumenty, instrukcja i scenariusze po polsku (komentarze w scenariuszach też).
  Kod, polecenia konsoli, pola dziennika i commity po angielsku.
- [x] 8. **Wersja.** Paczka moda się nie zmienia, więc wersja moda zostaje 0.2.0. Wpis do
  `CHANGELOG.md` opisuje narzędzia i zmiany w silniku.
- [x] 9. **Licencja GothicMOD.** Kod silnika na MIT, narzędzia i scenariusze to nasze dzieło.
  Scenariusze nie zawierają materiałów objętych licencją, tylko nazwy symboli.

## Odstępstwa od konstytucji

Brak.

## Różnice względem specyfikacji

Przyjęte razem z planem (2026-10-29) i przeniesione do specyfikacji:

1. **Okno 800×600 zamiast ok. 1280×720 (W2).** Tempest w trybie `Normal` tworzy okno 800×600.
   Inny rozmiar wymagałby zmiany w podmodule Tempest albo wywołań WinAPI w `MainWindow`.
2. **Dodatkowe polecenia `give` i `equip` (W3).** Funkcji zewnętrznych skryptów nie da się wywołać
   przez `call`. Bez tych dwóch poleceń scenariusz nie da bohaterowi miecza paladyna (K1).

## Ryzyka

- **Przyspieszenie czasu zmienia walkę.**
  - `dt` jest przycinane do 50 ms i mnożone, więc przy dużym `ztimer multiplyer` krok symulacji
    może przeskoczyć krótkie okno combo i walka wyjdzie inna niż w normalnym tempie.
  - Zapobieganie: w scenariuszach przyspieszenie najwyżej 2.
  - Wczesne wykrycie: porównanie raportu tego samego scenariusza przy 1 i 2 przy pierwszych
    scenariuszach.
- **Dziennik liczy ciosy, których nie było.**
  - `doAttack` zwraca `true` także bez nowego ciosu.
  - Zapobieganie: wynik z `Pose::continueCombo`.
  - Wczesne wykrycie: porównanie z obserwacją (K3) przy pierwszej wersji dziennika i po każdej
    zmianie jego zapisu (ADR 0004).
- **Dziennik zmienia przebieg gry.** Zaczepienia tylko czytają stan i nie losują. Wczesne wykrycie:
  ten sam scenariusz z włączonym i wyłączonym dziennikiem daje podobny rozkład serii.
- **Oczekiwania zawodzą przypadkiem.**
  - Walka jest losowa.
  - Zapobieganie:
    - ograniczenia „nigdy więcej niż” są pewne,
    - „co najmniej raz” wymaga długiej obserwacji,
    - K11 z 003 każe przejść zestaw 001 trzy razy,
    - niepowodzeń nie powtarzamy do skutku (ADR 0004).
- **Zakłócenia w świecie.**
  - Na waypoincie mogą pojawić się inne postacie, potwory albo pora dnia może przeszkadzać.
  - Zapobieganie: odludne miejsce, `set time` w scenariuszu, zrzut ekranu na początku.
  - Wczesne wykrycie: dziennik pokazuje walki z nieznanymi uczestnikami.
- **Zapis, którego nie było.** Zapis w dialogu albo przerywniku po cichu nic nie robi. `save game`
  sprawdza warunki, a wykonawca sprawdza, czy plik powstał.
- **Mod z gry zamiast z repozytorium.** Wygrywa nowszy znacznik czasu archiwum. Dlatego archiwum
  z folderu gry o tej samej nazwie jest pomijane (T1). `meta.json` i log podają, która paczka się
  wczytała.
- **Gra zajmuje ekran i fokus.** Okno 800×600 z dźwiękiem pojawia się przy każdym przebiegu
  automatycznym. Użytkownik to zaakceptował (P4, P6).
- **Znaleziony błąd kolejki (`onClearTarget`).** Wpłynie na wyniki 001 (dłuższe serie po utracie
  celu). Opisany w „Obecnym stanie”, do poprawki w 001.

## Alternatywy odrzucone

- **Testowy świat (`.zen`).** Wymaga budowania świata bez Spacera i różni się od warunków gry.
  Odludny waypoint i teleport dają to samo.
- **Sterowanie bohaterem przez symulację klawiszy.** Kruche, wymaga fokusu okna i nie powtarza się.
  Poza zakresem specyfikacji.
- **Scenariusze w skryptach moda.** Nie działają bez moda (K4), nie zapiszą gry ani nie zrobią
  zrzutu, wpychają kod testowy do paczki dla graczy.
- **Dziennik w `log.txt`.** Miesza się z logami silnika, które zmieniają się z upstreamem. Osobny
  plik JSON Lines daje stałe pola.
- **Sprawdzanie oczekiwań w silniku.** Python jest prostszy do zmiany i nie wymaga przebudowy silnika.
  Silnik tylko pomija linie `expect`.
- **Instalacja moda w folderze gry przed testem.** Odrzucone w P1.
- **Kody wyjścia gry jako wynik scenariusza.** `SystemApi::exit()` nie przenosi kodu. Plik statusu
  jest prostszy i niezależny od systemu.
- **Własny język skryptowy (np. Lua) w silniku.** Za duży koszt jak na listę poleceń konsoli
  z czekaniem.
