# content/

Zasoby moda w takim samym układzie jak `_work/Data` w Gothicu. `tools/pack.ps1` pakuje ten katalog
do `Gothic25.mod` pod ścieżką `_WORK/DATA/`. Nazwy w archiwum są zamieniane na wielkie litery.

| Katalog | Co trzymamy | Ścieżka w grze |
|---|---|---|
| `Anims/` | animacje, `.MDS` | `_work/Data/Anims` |
| `Meshes/` | modele | `_work/Data/Meshes` |
| `Music/` | muzyka DirectMusic | `_work/Data/Music` |
| `Presets/` | presety obiektów | `_work/Data/Presets` |
| `Scripts/Content/` | źródła Daedalus: fabuła, dialogi, AI (`Gothic.src`, `Fight.src`) | `_work/Data/Scripts/Content` |
| `Scripts/System/` | źródła Daedalus: menu, kamera, efekty, dźwięki | `_work/Data/Scripts/System` |
| `Sound/SFX/` | efekty dźwiękowe | `_work/Data/Sound/SFX` |
| `Sound/Speech/` | kwestie dialogowe, `<nazwa_kwestii>.WAV` | `_work/Data/Sound/Speech` |
| `Textures/` | tekstury | `_work/Data/Textures` |
| `Worlds/` | światy `.ZEN` | `_work/Data/Worlds` |

Zasady:

- Pliki o tej samej nazwie co w oryginalnej grze nadpisują oryginał. Kwestię dialogową podmieniasz,
  wrzucając do `Sound/Speech/` plik WAV o tej samej nazwie, np. `DIA_ADDON_10008_BANDIT_HI_01_00.WAV`.
- Dźwięki: OpenGothic czyta WAV PCM 8/16-bit, WAV IMA ADPCM 4-bit (format oryginalnych nagrań,
  44,1 kHz mono) oraz OGG. Plik bez nagłówka `RIFF` albo `OggS` jest po cichu pomijany, bez wpisu w logu.
- Źródła skryptów (`*.d`, `*.src`) nie trafiają do archiwum. Do archiwum idą skompilowane `.DAT`
  z `gothic25/build/scripts/` (zob. `tools/build-scripts.ps1` i ADR 0001).
- Oryginalne pliki do podglądu wyciągniesz poleceniem
  `python tools/vdf.py extract "<gra>/Data/Speech_Addon.vdf" <folder> --include "*/DIA_ADDON_*"`.
  Nie commituj ich do repozytorium (konstytucja, zasada 6).
- Duże pliki binarne: zob. ADR 0002.
