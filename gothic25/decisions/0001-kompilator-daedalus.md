# ADR 0001: Kompilator skryptów Daedalus i baza skryptów

- **Status:** Proponowana (rekomendacja poniżej, czeka na test akceptacyjny)
- **Data:** 2026-10-27

## Kontekst

OpenGothic wczytuje skompilowane skrypty (`GOTHIC.DAT`, `MENU.DAT` itd.) oraz napisy dialogów
(`OU.BIN` / `OU.CSL`), najpierw z archiwów, potem z dysku (`GameScript::loadDialogOU`). Nie umie
kompilować źródeł `.d`. Biblioteka ZenKit też nie ma kompilatora, ma tylko loader.

Potrzebujemy:

1. **Bazy skryptów**: źródeł Gothic II: Noc Kruka **w polskiej wersji**, bo teksty dialogów, nazwy
   przedmiotów i opisy siedzą w skryptach.
2. **Kompilatora** uruchamianego z wiersza poleceń, w skrypcie i w CI. Musi generować `.DAT` zgodne
   z oryginałem oraz `OU.CSL` / `OU.BIN` z wywołań `AI_Output`, w kodowaniu cp1250.

`tools/build-scripts.ps1` wywołuje polecenie z `local.json` (`scriptCompiler.command` i `args`
z symbolami `{src}`, `{dat}`, `{out}`, `{gothic}`) dla każdej pozycji z `mod.json` → `scripts`.

## Rozpoznanie (stan na 2026-10-27)

### Kompilatory

| Narzędzie | Co umie | Uwagi |
|---|---|---|
| **DaedalusCompiler (`gdc`)**, [dzieje-khorinis/DaedalusCompiler](https://github.com/dzieje-khorinis/DaedalusCompiler) | `.DAT`, `OU.CSL`/`OU.BIN` (`--gen-ou`), Ikarus/LeGo, wbudowane funkcje zewnętrzne G2 NK, ostrzeżenia o nieużywanych symbolach | C#, MIT. Kodowanie cp1250 zaszyte w kodzie (czytanie źródeł, `.DAT`, OU). Wydanie v0.9.5 (2025-08-22) to pojedyncze pliki wykonywalne dla Windows, Linuksa i macOS, bez instalacji .NET. Funkcje języka bez zmian od 2020 r.; w 2025 r. odnowiono tylko build, CI i testy e2e. Używany produkcyjnie przez Dzieje Khorinis. |
| Oryginalny silnik (`Gothic2.exe -zreparse`, zParserExtender w Union) | pełna zgodność, OU | Wymaga gry i Windowsa, uruchamia grę, nie nadaje się do CI. |
| Gothic Sourcer 3.15 | edytor z kompilatorem | Stary program z GUI, bez Ikarus/LeGo. |
| Parsiphae (Rust) | tylko sprawdzanie składni | Nie generuje `.DAT`. |
| `dacode` (w repo auronen/Gothic-2-localization) | kompilacja i podstawianie tłumaczeń | Binarka bez publicznego kodu i dokumentacji. |

### Bazy skryptów

| Źródło | Zawartość | Uwagi |
|---|---|---|
| **[VaanaCZ/gothic-2-addon-scripts](https://github.com/VaanaCZ/gothic-2-addon-scripts)** | gałęzie `2.6-PL` (odtworzona oryginalna wersja polska) i `Unified-PL` (ujednolicona baza do modowania) | Według autora skrypty z gałęzi wersji oryginalnych kompilują się do `.DAT` identycznego rozmiarem i kolejnością symboli z oryginałem. Kodowanie cp1250. Licencja: **GothicMOD Lizenz** (Piranha Bytes, 2004), czyli wyłącznie niekomercyjne modyfikacje z podaniem autorów. |
| [auronen/Gothic-2-localization](https://github.com/auronen/Gothic-2-localization) | niemieckie źródła plus tłumaczenia w CSV (polskie z przekładu CD Projekt), aktywnie rozwijane | Polskie źródła powstają dopiero przez podstawienie tłumaczeń zamkniętym narzędziem `dacode`. Archiwa `.mod` z wydań zawierają tylko skompilowane `.DAT` i `OU.BIN`. |

## Rekomendacja

1. Kompilator: **`gdc` v0.9.5** (`gdc-windows-x64.exe`), wpisany w `local.json`:
   `"args": ["{src}", "--output-dat", "{dat}"]`, a dla `Gothic.src` dodatkowo
   `--gen-ou --output-ou {out}/Content/Cutscene` (wymaga drobnej zmiany w `build-scripts.ps1`:
   argumenty OU tylko dla pozycji oznaczonej w `mod.json`).
2. Baza skryptów: **`Unified-PL`** z VaanaCZ, wciągnięta do `content/Scripts` z zachowaniem
   informacji o źródle i licencji.

## Test akceptacyjny (2026-10-27): zaliczony z zastrzeżeniami

Narzędzie porównujące: `tools/dat.py diff` (symbole, wartości, bajtkod) i `tools/dat.py disasm`.

**`2.6-PL` przez `gdc` vs oryginalny polski `GOTHIC.DAT` z gry (7 553 627 B):**

- Wynik: 7 553 668 B, 74 651 symboli, tablica sortowania identyczna.
- Bajtkod: 21 328 z 21 333 funkcji i instancji identyczny (po normalizacji adresów). Pięć różnic:
  - `BAU_983_Dragomir`, `PAL_251_Oric`: odwołanie do `Face_N_Tough_Lee_Ähnlich`. Oryginalny
    kompilator zapisywał `Ä` w nazwie jako bajt 0xE5, `gdc` jako 0xC4. W pliku jest spójnie, bez wpływu.
  - `PIR_1300_Addon_Greg_NW`, `PIR_1320_Addon_Greg`: `self.aivar[...]` w ciele instancji. `gdc` dodaje
    jawne ustawienie instancji. ZenKit przypina obiekt do symbolu przed wywołaniem
    (`DaedalusVm::allocate_instance`), więc działanie jest takie samo.
  - `DIA_Addon_Snaf_Abrechnung_Info`: w źródle brakuje `;` po łańcuchu `if … else if …`. Oryginał
    wchłonął następny `if` do łańcucha, a `gdc` traktuje go jako osobną instrukcję. **Realna różnica**:
    Snaf może powiedzieć jedną kwestię więcej.
- Pozostałe różnice bez wpływu na OpenGothic: 3 napisy (VaanaCZ zamienił `"` na `'` w źródłach),
  adresy funkcji zewnętrznych (oryginał wpisuje adresy z `Gothic2.exe`, `gdc` wpisuje -1), pole
  `parent` 55 parametrów funkcji, pozycje w plikach źródłowych.

**`MENU.DAT` z `2.6-PL`:** bajtkod i symbole identyczne z oryginałem.

**`Unified-PL` vs `.DAT` skompilowane przez VaanaCZ:**
- 7 plików systemowych (Camera, Fight, Menu, Music, SFX, ParticleFX, VisualFX): bajtkod i symbole identyczne.
- `GOTHIC.DAT`: te same 5 różnic co wyżej, po skompilowaniu z listą funkcji zewnętrznych bez
  `Game_InitEnglish` i `Game_InitEngIntl`. Referencję zbudowano na innej rewizji silnika. Z domyślną
  listą `gdc` są 2 symbole więcej, co przesuwa numery symboli zapisane w kodzie, ale silnik wiąże
  funkcje po nazwie, więc to bez znaczenia.

**W grze (OpenGothic, `-nomenu`):** `Unified-PL` skompilowane przez `build-scripts.ps1` i spakowane
do `.mod`. Testowy `PrintDebug` w `INIT_GLOBAL` pojawił się w logu, więc gra wykonała nasz
`GOTHIC.DAT`. Brak nowych błędów względem oryginalnych skryptów.

**Niezgodności `gdc` wymagające obejścia:**

1. Znak form feed (0x0C) w kodzie powoduje błąd składni. Występuje raz:
   `DIA_VLK_439_Vatras.d`, linia 566. Do zamiany na spację.
2. `slf.` jako prefiks w ciele instancji (`slf.attribute[...] = ...`) daje błąd „undeclared”.
   Oryginał ignorował prefiks (bajtkod taki sam jak bez niego). Występuje w 131 miejscach w 21 plikach
   (zwłoki, `PC_Hero` itd.). Do usunięcia `slf.` w tych liniach.
3. Wydanie jednoplikowe nie zawiera wbudowanej listy funkcji silnika. Obok `.exe` musi leżeć katalog
   `DaedalusBuiltins/` z `gothic.d` i `menu.d` z tagu v0.9.5. Bez niego każda funkcja silnika jest
   „undeclared”. Wymagane też środowisko .NET 8 (wydanie nie jest self-contained).
4. Brakujące `;` po `if`: `gdc` nie ostrzega, a interpretuje inaczej niż oryginał (przypadek Snafa).

## Decyzja

Do zatwierdzenia przez właściciela projektu. Rekomendacja: przyjąć `gdc` v0.9.5 i `Unified-PL`, przy czym:

- poprawki 1 i 2 wprowadzamy raz, przy imporcie skryptów do `content/Scripts`, z opisem w commicie,
- `DIA_Addon_Snaf_Abrechnung_Info` poprawiamy jawnie (dodajemy `;` i decydujemy, które zachowanie zostaje),
- pobieranie `gdc` razem z `DaedalusBuiltins` i sumą SHA-256 zamykamy w skrypcie w `tools/`.

## Konsekwencje

- **Licencja GothicMOD obowiązuje cały mod**: Gothic 2.5 musi pozostać darmowy i niekomercyjny,
  z podaniem Piranha Bytes oraz autorów rekonstrukcji skryptów. Trzeba to dopisać do konstytucji.
- `gdc` nie jest aktywnie rozwijany. Jeśli zabraknie jakiejś funkcji języka, możemy go sforkować
  (MIT, C#, .NET 8).
- Dopóki decyzja nie zapadnie, funkcje wymagające zmian w skryptach nie mogą przejść do implementacji.
