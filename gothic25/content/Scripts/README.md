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

## Symbole dla silnika

Fork OpenGothic czyta część symboli skryptów po nazwie. Symbole z tej tabeli włączają zachowania
odbiegające od oryginalnego Gothica ([ADR 0003](../../decisions/0003-przelaczniki-silnika-w-skryptach.md)).
Gdy ich nie ma, silnik działa jak upstream. Starszy silnik i oryginalna gra ignorują je bez błędów.

| Symbol | Gdzie | Co robi | Spec. |
|---|---|---|---|
| `MAX_MOVE` | `Content/_intern/Fight.d` | Długość listy `move` w `C_FightAI`. Oryginał: 6. Fork czyta do 16 ruchów na stan FAI, starszy silnik tylko 6 pierwszych. | [001](../../specs/001-combosy-npc-w-walce-wrecz/spec.md) |
| `C_FightAI_Combo`, `FA_COMBO_<N>` | klasa w `Content/_intern/Fight.d`, instancje w `Content/FAI/*.d` | Włącza łączenie ciosów NPC w oknie combo dla stylu walki `<N>` i ustawia jego parametry (niżej). Styl bez tej instancji walczy jak w oryginale. | [001](../../specs/001-combosy-npc-w-walce-wrecz/spec.md) |
| `FA_MY_W_COMBO_<N>` | `Content/FAI/*.d` | Instancja z oryginału, dotąd pusta i nieużywana. Dla stylów z `FA_COMBO_<N>` silnik losuje z niej ruch raz na okno combo po ciosie do przodu, gdy NPC nie ma już zaplanowanej serii. `MOVE_ATTACK` przedłuża combo, każdy inny ruch je kończy. | [001](../../specs/001-combosy-npc-w-walce-wrecz/spec.md) |

Składowe `C_FightAI_Combo`:

- `link_min`, `link_max`: kiedy NPC łączy kolejny cios serii albo combo, w procentach użytecznej
  części okna combo (od początku okna do końca trafienia). Moment jest losowany między tymi
  wartościami. Przy połączeniu silnik przeskakuje animację do końca trafienia, więc niższe
  wartości skracają cios: 100 gra go prawie w całości, a 0 pomija nawet ponad połowę ciosu.
- `defend_in_series`: `TRUE`, gdy NPC może przerwać własną serię, żeby zareagować na nadchodzący
  cios przeciwnika według `FA_ENEMY_PREHIT_<N>` (blok, odskok).
- `break_on_lost`: `TRUE`, gdy NPC przerywa serię, kiedy przeciwnik wyjdzie z zasięgu broni albo
  z pola widzenia z przodu. Przy `FALSE` NPC dokańcza serię, także w powietrze.

## Numery symboli a zapisy gry

OpenGothic zapisuje NPC i przedmioty numerem symbolu w `GOTHIC.DAT`. Zmiana w istniejącym pliku nie
może więc dodać ani usunąć symbolu, bo przesunęłaby numery wszystkich dalszych symboli i zapisy
poprzedniej wersji przestałyby się wczytywać ([ADR 0005](../../decisions/0005-stabilne-numery-symboli.md)).

- Nowe stałe, instancje i funkcje trafiają do nowych plików dopisanych na końcu `Content/Gothic.src`.
- W starym pliku nową wartość wpisujemy liczbą z komentarzem, np. `fight_tactic = 13` w `MST_OrcElite.d`.
- Sprawdzenie: `python tools/dat.py prefix <GOTHIC.DAT poprzedniej wersji> build/scripts/_compiled/GOTHIC.DAT`
  kończy się kodem 0, gdy żaden symbol się nie przesunął.

## Kodowanie

Pliki są w Windows-1250. Edytor musi zapisywać je w tym kodowaniu. Przy zapisie w UTF-8
`git add` zgłosi błąd konwersji albo polskie znaki w grze się zepsują.
