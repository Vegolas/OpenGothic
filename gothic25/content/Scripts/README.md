# Skrypty Daedalus

Bazą są skrypty Gothic II: Noc Kruka w wersji polskiej, odtworzone i ujednolicone przez VaanaCZ.

| | |
|---|---|
| Źródło | [VaanaCZ/gothic-2-addon-scripts](https://github.com/VaanaCZ/gothic-2-addon-scripts), gałąź `Unified-PL` |
| Commit | `9e9be52e648016083e77a729d90465fd5eba17c1` (2022-11-01) |
| Licencja | GothicMOD Lizenz 1.0 (Piranha Bytes), zob. [LICENSE-GothicMOD.txt](LICENSE-GothicMOD.txt) i konstytucja, zasada 9 |
| Oryginał | na podstawie dzieła Piranha Bytes; polski przekład: CD Projekt |
| Kompilator | `gdc` 0.9.5 (zob. [ADR 0001](../../decisions/0001-kompilator-daedalus.md), `tools/get-gdc.ps1`) |

## Co zmieniono względem źródła

Historia gita pokazuje każdą zmianę osobno: pierwszy commit importu zawiera skrypty bez zmian
w treści, kolejne commity wprowadzają poprawki.

- **Pominięte przy imporcie:** `_compiled/*.DAT` i `Content/Cutscene/Ou.bin`. Generuje je
  `tools/build-scripts.ps1`.
- **Końce linii:** CRLF w plikach `.d` i `.src` (w źródle LF). Pliki są w cp1250 na dysku,
  a w gicie w UTF-8 (`.gitattributes`).
- **Zgodność z `gdc`:**
  - znak form feed w `DIA_VLK_439_Vatras.d` zamieniony na spację,
  - usunięty prefiks `slf.` w ciałach instancji NPC. Oryginalny kompilator go ignorował,
    więc bajtkod jest taki sam.
- **`DIA_Addon_Snaf_Abrechnung_Info`:** dodany brakujący `;` w taki sposób, żeby zachowanie
  było identyczne z oryginalną grą.

## Kodowanie

Pliki są w Windows-1250. Edytor musi zapisywać je w tym kodowaniu. Przy zapisie w UTF-8
`git add` zgłosi błąd konwersji albo polskie znaki w grze się zepsują.
