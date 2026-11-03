# ADR 0008: Dokładanie definicji animacji moda przez silnik

- **Status:** Przyjęta <!-- Proponowana / Przyjęta / Zastąpiona przez ADR NNNN / Odrzucona -->
- **Data:** 2026-11-03, przyjęta razem z poprawionym planem 004 (zastępuje punkt 3 decyzji
  [ADR 0007](0007-zrodla-i-budowanie-animacji-moda.md))

## Kontekst

ADR 0007 zakładał, że mod rozpowszechnia pełne tekstowe definicje modelu ludzi z MDK, zmienione
o animacje moda. Zadanie Z4 planu 004 sprawdziło licencję MDK (ADR 0007, „Kontekst”):
- na GothicMOD są tylko dane nowo utworzone przez moderów i skrypty z `/_work/data/Scripts`;
- definicje animacji z MDK i oryginalne animacje z gry podlegają umowie licencyjnej gry, która
  nie pozwala ich rozpowszechniać, także w zmienionej postaci.

Właściciel projektu zdecydował 2026-11-03 (spec. 004, P2 i P9):
- definicje moda łączy z oryginałem silnik;
- w paczce są tylko animacje z własnymi kluczami, a oryginały służą lokalnie jako wzorzec i do
  testów.

Fakty z kodu:

- `Resources::implLoadAnimation` (`common/resources.cpp:667-687`) ładuje definicje modelu
  i nakładek pod nazwą `<MODEL>.MSB` (w trybie G2 `.MDS` zamienia na `.MSB`, `:672`), a ZenKit
  rozpoznaje treść tekstową i binarną (`lib/ZenKit/src/ModelScript.cc:436-446`).
- Z definicji powstaje `Animation` (`common/graphics/mesh/animation.cpp:32`), które dla każdej
  animacji ładuje `<MODEL>-<ANI>.MAN`. Pliki z paczki moda mają pierwszeństwo przed archiwami gry.

## Opcje

1. **Plik rozszerzenia czytany przez silnik.** Mod dostarcza obok oryginału tekstowy plik
   `<MODEL>.EXT.MDS` (np. `HUMANS.EXT.MDS`, `HUMANS_1HST1.EXT.MDS`) w składni Gothica, tylko
   z własnymi wpisami. Silnik po wczytaniu definicji modelu albo nakładki szuka tego pliku i dokłada
   jego wpisy:
   - animacja o nowej nazwie dochodzi;
   - wpis o nazwie oryginalnej animacji ją zastępuje;
   - aliasy, blendy, połączenia i blokady łączy się tak samo, według nazwy.

   Bez pliku silnik działa jak upstream. Zalety: w paczce jest tylko praca moda, nakładki stylów
   walki i stare zapisy działają bez zmian, mechanizm jest ogólny (może go użyć każdy mod).
   Wady: zmiana w ładowaniu animacji i własna reguła łączenia do opisania.
2. **Własna nakładka nakładana przez skrypty** (`Mdl_ApplyOverlayMds`). Zalety: bez zmian
   w ładowaniu. Wady: nakładkę musi dostać każdy człowiek, także w starych zapisach, a kolejność
   względem nakładek stylów walki decyduje, która definicja wygrywa.
3. **Pełne definicje w paczce** (ADR 0007, pkt 3, i zapis binarnego MSB). Odpada przez licencję.

## Decyzja

**Opcja 1.**

- Nazwa pliku: `<MODEL>.EXT.MDS`, gdzie `<MODEL>` to nazwa definicji modelu albo nakładki bez
  rozszerzenia. Treść w składni MDS, z blokiem `Model` i `aniEnum`. Siatki i szkielet w pliku
  rozszerzenia są ignorowane.
- Łączenie według nazwy, bez rozróżniania wielkości liter. Wpis z rozszerzenia wygrywa z oryginałem,
  także z wpisem innego rodzaju o tej samej nazwie (np. `ani` zastępuje `aniAlias`), bo w grze nazwa
  wskazuje jedną animację.
- Zachowanie włącza obecność pliku (dane moda), tak jak animacje w ADR 0007, pkt 5. Plan dowodzi,
  że oryginalne gry takich plików nie mają.
- Narzędzia moda (`tools/anim.py`) łączą definicje tak samo, żeby walidować build bez silnika.
  Polecenie konsoli pokazuje połączoną definicję animacji postaci, więc zgodność da się sprawdzić
  w grze.

## Konsekwencje

- W repozytorium i w paczce są tylko nasze definicje (zasada 6). Definicje z MDK i oryginalne
  animacje służą lokalnie jako wzorzec i do testów.
- Silnik zyskuje ogólny mechanizm, który da się zgłosić do Try/OpenGothic.
- Podmiana oryginalnej animacji to wpis w rozszerzeniu (opcjonalnie) i MAN z kluczami moda.
- Reguła „wpis wygrywa według nazwy” nie pozwala usunąć oryginalnej animacji. Jeśli kiedyś będzie
  potrzebne, dojdzie jawna składnia usuwania.
