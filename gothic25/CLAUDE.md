# Gothic 2.5: kontekst dla Claude

Mod Gothic II: Noc Kruka na forku OpenGothic. Repozytorium główne to silnik (C++, upstream:
Try/OpenGothic), a katalog `gothic25/` zawiera mod i jego proces.

- Zasady nadrzędne: `sdd/constitution.md`. Przed każdym planem i implementacją sprawdź ich zgodność.
- Mod działa tylko na OpenGothic (ADR 0006). Nie sprawdzaj zgodności z oryginalnym `Gothic2.exe`
  i nie proponuj rozwiązań pod niego (Union, Ninja, hooki Ikarus/LeGo, kompilacja zasobów przez grę).
- Powtarzalny krok (build, zasoby, testy) automatyzuj skryptem w `tools/` (zasada 10).
- Cykl pracy: `sdd/workflow.md`. Komendy: `/g25-specify`, `/g25-clarify`, `/g25-plan`, `/g25-tasks`,
  `/g25-implement`, `/g25-verify`.
- Nie implementuj niczego bez specyfikacji w statusie `Zatwierdzona` i planu w `specs/NNN-*/`.
- Dokumenty piszemy po polsku. Kod, komentarze i commity po angielsku, w stylu repozytorium.
- Kod silnika: `common/` (gra: `common/game`, świat i NPC: `common/world`, skrypty i funkcje
  zewnętrzne: `common/game/gamescript.cpp`, zgodność z Ikarus/LeGo: `common/game/compatibility`).
- Zasoby moda: `content/` w układzie `_work/Data`. Pakowanie: `tools/pack.ps1` (używa `tools/vdf.py`).
- Skrypty: `content/Scripts` (baza Unified-PL, cp1250 na dysku). Przed zmianą przeczytaj
  `content/Scripts/README.md`. Kompilator `gdc` nie toleruje form feed ani `slf.` w ciele instancji
  i inaczej niż oryginał traktuje brakujące `;` po `if`. Wpływ zmian na bajtkod sprawdzaj przez
  `tools/dat.py diff`.
- Skrypty w `tools/` muszą działać w Windows PowerShell 5.1. Pliki `.ps1` piszemy w samym ASCII,
  a pliki UTF-8 czytamy i zapisujemy przez `Read-Utf8` / `Write-Utf8` z `tools/lib/common.ps1`.
- Nie uruchamiaj `install.ps1` ani `run.ps1` na folderze gry użytkownika bez jego zgody.
- Scenariusze testowe w trybie automatycznym (`tools/test.ps1 -Scenario ...` albo `-Spec NNN`, bez
  `-Manual`) uruchamiaj bez pytania (spec. 003, W11): nie zmieniają folderu gry, mod biorą
  z repozytorium, kończą się same w małym oknie. Tryb `-Manual`, `run.ps1`, `install.ps1` i każde inne
  uruchomienie gry nadal wymagają zgody użytkownika.
- Testy walki: scenariusze w `tests/NNN/`, format i zasady w `tests/README.md`, zaliczanie kryteriów
  według ADR 0004. Po zmianie w walce uruchom zestawy specyfikacji, których dotyczy, jako testy regresji.
- Nie dodawaj ani nie usuwaj symboli w istniejących plikach skryptów: przesuwa to numery symboli
  w `GOTHIC.DAT` i psuje stare zapisy (ADR 0005). Sprawdzenie: `tools/dat.py prefix`.
