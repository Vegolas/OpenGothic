# Gothic 2.5

Modyfikacja Gothic II: Noc Kruka budowana na forku OpenGothic. Cel: bardziej żywy świat
(losowe zdarzenia), spójne polskie głosy i poprawione mechaniki (m.in. skradanie).

Projekt prowadzimy w **Spec-Driven Development (SDD)**: każda zmiana zaczyna się od specyfikacji,
potem plan techniczny, lista zadań i dopiero implementacja. Zasady nadrzędne są w
[sdd/constitution.md](sdd/constitution.md), cykl pracy w [sdd/workflow.md](sdd/workflow.md).

## Układ katalogów

```
gothic25/
├── mod.json              manifest moda (id, wersja, nazwa archiwum, wpisy do .ini)
├── local.example.json    wzór lokalnej konfiguracji (ścieżka do gry, kompilator skryptów)
├── roadmap.md            pomysły czekające na specyfikację
├── sdd/                  konstytucja, opis cyklu SDD, szablony dokumentów
├── specs/                specyfikacje funkcji: specs/NNN-nazwa/{spec,plan,tasks}.md
├── decisions/            decyzje architektoniczne (ADR)
├── content/              zasoby moda w układzie _work/Data (pakowane do Gothic25.mod)
├── system/               szablon pliku Gothic25.ini
└── tools/                skrypty: build, pakowanie, instalacja, uruchamianie, publikacja
```

Zmiany w silniku (C++) robimy w głównym drzewie forka (`common/`, `lib/`), ale każda z nich
musi wynikać ze specyfikacji w `specs/`.

## Pierwsze uruchomienie

1. Skopiuj `local.example.json` jako `local.json` i ustaw `gothicDir` (folder z `System/Gothic2.exe`).
2. Zbuduj silnik: `tools/build-engine.ps1`.
3. Pobierz kompilator skryptów (`gdc`, wymaga środowiska .NET 8): `tools/get-gdc.ps1`.
4. Skompiluj skrypty, spakuj moda i zainstaluj go w grze: `tools/build-scripts.ps1`,
   `tools/pack.ps1`, potem `tools/install.ps1`.
5. Uruchom: `tools/run.ps1` (dodaj `-Dev`, żeby włączyć konsolę deweloperską).

Skrypty działają w Windows PowerShell 5.1 i PowerShell 7. Jeśli zasady wykonywania blokują `.ps1`,
uruchamiaj je przez `powershell -NoProfile -ExecutionPolicy Bypass -File gothic25/tools/<skrypt>.ps1`.
Pakowanie wymaga Pythona 3.10 lub nowszego (tylko biblioteka standardowa).

Ścieżkę do gry można też podać parametrem `-GothicDir` albo zmienną środowiskową `G25_GOTHIC_DIR`.

## CI

Fork ma własne workflow. Upstreamowy `Build` (`.github/workflows/build.yml`) jest w forku wyłączony
poleceniem `gh workflow disable`, a nie edytowany, żeby aktualizacje z Try/OpenGothic nie dawały konfliktów.

- `gothic25-mod.yml`: przy zmianach w `gothic25/` pobiera `gdc`, kompiluje skrypty i buduje
  paczkę moda (`publish.ps1 -SkipEngine`). Paczka trafia do artefaktów.
- `gothic25-engine.yml`: przy zmianach poza `gothic25/` buduje silnik na Windowsie i Linuksie
  (te same kroki co upstream).

Buildy na macOS, Androida i paczkę `.deb` sprawdza CI upstreamu, gdy zgłaszamy tam zmiany.

## Praca z Claude Code

W `.claude/commands/` są komendy prowadzące przez cykl SDD:
`/g25-specify <opis>`, `/g25-clarify NNN`, `/g25-plan NNN`, `/g25-tasks NNN`,
`/g25-implement NNN [Zn]`, `/g25-verify NNN`. Kontekst projektu dla Claude jest w [CLAUDE.md](CLAUDE.md).

## Skrypty

| Skrypt | Co robi |
|---|---|
| `tools/build-engine.ps1` | Buduje OpenGothic (CMake + Ninja + MSVC) do `build/` w katalogu głównym repo |
| `tools/get-gdc.ps1` | Pobiera przypiętą wersję kompilatora `gdc` z `DaedalusBuiltins` i sprawdza sumy SHA-256 |
| `tools/build-scripts.ps1` | Kompiluje skrypty Daedalus z `content/Scripts` do `.DAT` i plików OU (domyślnie przez `gdc`) |
| `tools/pack.ps1` | Składa `content/` i skompilowane skrypty w `gothic25/build/Gothic25.mod` |
| `tools/install.ps1` | Kopiuje `.mod` do `Data/ModVDF` i `.ini` do `System` w folderze gry |
| `tools/run.ps1` | Uruchamia OpenGothic z modem (`-game:Gothic25.ini`) |
| `tools/publish.ps1` | Pełne wydanie: build Release w `build-release/`, paczki zip (mod i silnik) i sumy SHA-256 w `gothic25/dist/<wersja>/`. Wymaga czystego drzewa git i sekcji wersji w `CHANGELOG.md`. `-Tag` zakłada lokalny tag |
| `tools/new-spec.ps1` | Zakłada nowy katalog specyfikacji z szablonów |
| `tools/vdf.py` | Pakowanie, listowanie i rozpakowywanie archiwów VDF/MOD |
| `tools/dat.py` | Podgląd skompilowanych skryptów `.DAT`: statystyki, symbole, deasembler, porównanie dwóch plików |

## Ważne zachowania silnika

- OpenGothic **nie** pozwala luźnym plikom z `_work` nadpisywać zawartości archiwów
  (`Resources::mountWork` montuje je z `VfsOverwriteBehavior::NONE`). Dlatego nawet do testów
  zasoby trzeba spakować do `.mod`.
- Jeśli `.ini` moda ma wpis `[FILES] VDF=`, silnik montuje tylko wymienione tam archiwa `.mod`
  (`GameModDescriptor` w `common/gothic.cpp`).
- Archiwa `.mod` mają pierwszeństwo przed `.vdf`, a między sobą wygrywa nowszy znacznik czasu.
