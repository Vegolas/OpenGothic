# Konstytucja projektu Gothic 2.5

Zasady nadrzędne. Specyfikacja, plan albo zadanie, które łamie którąś z nich, musi to wprost
uzasadnić w sekcji „Odstępstwa od konstytucji” albo zostać poprawione. Zmiana konstytucji
wymaga osobnego ADR w `decisions/`.

## 1. Warstwa najniższa, która wystarczy

Funkcję realizujemy w najniższej warstwie, która ją uniesie:

1. **Zasoby** (dźwięki, tekstury, modele, światy). Działają też w oryginalnym silniku.
2. **Skrypty Daedalus** (fabuła, dialogi, AI, plany dnia).
3. **Silnik C++** (fork OpenGothic). Tylko gdy dwie pierwsze warstwy nie wystarczą.

Plan każdej funkcji podaje, której warstwy dotyczy i dlaczego nie da się jej zrobić niżej.

## 2. Silnik daje mechanizmy, skrypty decydują o treści

Zmiany w C++ dodają ogólne mechanizmy: nowe funkcje zewnętrzne dla skryptów (`bindExternal`),
parametry, systemy. Konkretna treść (który NPC, jaki event, jakie wartości) żyje w skryptach
albo w plikach danych moda, a nie na sztywno w silniku.

## 3. Fork ma pozostać łatwy do aktualizacji z upstreamu

- Kod silnika piszemy w stylu repozytorium OpenGothic (nazewnictwo, wcięcia, gęstość komentarzy).
- Zachowanie odbiegające od oryginalnego Gothica włączamy flagą albo ustawieniem moda,
  domyślnie wyłączone. Bez moda fork ma działać jak upstream.
- Zmiany grupujemy tak, żeby dało się je zgłosić do Try/OpenGothic, jeśli są ogólnie przydatne.
- Treść moda trzymamy wyłącznie w `gothic25/`.

## 4. Zapisy gry są święte

Każdy nowy stan zapisywany w grze dostaje wersjonowaną serializację (`common/game/serialize.cpp`).
Zapis z poprzedniej wersji moda musi się wczytać albo plan musi jawnie ogłosić niezgodność
i podać numer wersji, od której obowiązuje.

## 5. Każda funkcja ma kryteria akceptacji, które da się sprawdzić w grze

Specyfikacja opisuje zachowanie z perspektywy gracza oraz kroki, którymi da się je zweryfikować
(miejsce w świecie, komenda konsoli, zapis testowy). „Działa” oznacza, że ktoś przeszedł te kroki.

## 6. Prawa do zasobów

- Nie publikujemy plików z oryginalnej gry w niezmienionej postaci. Gracz musi mieć własną kopię
  Gothic II: Noc Kruka.
- Głosy generowane przez AI powstają tylko z głosów, do których mamy zgodę właściciela.
  Specyfikacja takiej funkcji wskazuje, skąd ta zgoda pochodzi.
- Każdy zewnętrzny zasób (model, tekstura, muzyka) ma w specyfikacji źródło i licencję.

## 7. Język

- Dokumenty projektu (specyfikacje, plany, ADR) piszemy po polsku.
- Kod, identyfikatory, komunikaty commitów i komentarze w kodzie piszemy po angielsku,
  tak jak w reszcie repozytorium.
- Teksty widoczne w grze powstają w wersji polskiej. Inne języki to osobna funkcja.

## 8. Wersjonowanie

Mod używa SemVer w `mod.json`:

- **MAJOR**: niezgodność zapisów gry albo wymagana nowa wersja silnika,
- **MINOR**: nowe funkcje,
- **PATCH**: poprawki.

Wydanie zawsze buduje się skryptem `tools/publish.ps1` z czystego drzewa git.
