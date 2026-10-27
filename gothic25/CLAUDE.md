# Gothic 2.5: kontekst dla Claude

Mod Gothic II: Noc Kruka na forku OpenGothic. Repozytorium główne to silnik (C++, upstream:
Try/OpenGothic), a katalog `gothic25/` zawiera mod i jego proces.

- Zasady nadrzędne: `sdd/constitution.md`. Przed każdym planem i implementacją sprawdź ich zgodność.
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
