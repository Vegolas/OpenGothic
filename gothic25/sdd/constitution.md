# Konstytucja projektu Gothic 2.5

Zasady nadrzędne. Specyfikacja, plan albo zadanie, które łamie którąś z nich, musi to wprost
uzasadnić w sekcji „Odstępstwa od konstytucji” albo zostać poprawione. Zmiana konstytucji
wymaga osobnego ADR w `decisions/`.

## 1. Tylko OpenGothic

Mod działa wyłącznie na naszym forku OpenGothic ([ADR 0006](../decisions/0006-mod-tylko-dla-opengothic.md)).
Nie dbamy o zgodność z oryginalnym silnikiem (`Gothic2.exe`), Union, Ninja ani hookami pamięci
Ikarus/LeGo i nie przejmujemy ich ograniczeń.

Funkcję realizujemy w tej warstwie, w której najprościej ją zrobić, przetestować i utrzymać:

- **Zasoby** (dźwięki, tekstury, modele, animacje, światy) w formatach i narzędziach dobranych
  pod nasz silnik i automatyzację.
- **Skrypty Daedalus** (fabuła, dialogi, AI, plany dnia).
- **Silnik C++** (fork OpenGothic): mechanizmy, formaty, nowe funkcje dla skryptów.

Plan każdej funkcji podaje, której warstwy dotyczy i dlaczego ta jest najtańsza w utrzymaniu.
Zmiana w silniku nadal podlega zasadom 2 i 3.

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
Kroki może przejść także automatyczny scenariusz testowy, gdy kryterium da się ocenić z raportu
([ADR 0004](../decisions/0004-zaliczanie-kryteriow-przez-scenariusze.md)).

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

## 9. Licencja GothicMOD: mod jest darmowy i niekomercyjny

Skrypty bazowe pochodzą z materiałów Piranha Bytes udostępnionych na licencji GothicMOD Lizenz 1.0
(`content/Scripts/LICENSE-GothicMOD.txt`). Mod jest na nich zbudowany, więc:

- **Bez pieniędzy.** Gothic 2.5 i każda jego część są darmowe: bez opłat za pobranie, płatnych
  wersji, płatnego wczesnego dostępu ani treści za opłatą. Każdą formę finansowania, także
  darowizny, trzeba przed uruchomieniem zatwierdzić osobnym ADR.
- **Copyleft.** Zmienione skrypty i inne opracowania materiałów objętych licencją rozpowszechniamy
  na tej samej licencji. Nasze samodzielne dzieła (kod silnika na MIT, nowe zasoby) mogą mieć
  własne licencje, ale wydanie musi jasno mówić, które części podlegają GothicMOD (`NOTICE.txt`).
- **Inny tytuł.** Zmienione dzieło nie może nosić tytułu oryginału. Mod nazywa się „Gothic 2.5”,
  nie „Gothic II: Noc Kruka”.
- **Uznanie autorstwa.** Nie przedstawiamy autorów oryginału jako autorów moda. W napisach,
  opisie i `NOTICE.txt` używamy formuły „na podstawie dzieła Piranha Bytes” oraz podajemy źródło
  rekonstrukcji skryptów (VaanaCZ) i polskiego przekładu (CD Projekt).
- **Licencja w paczce.** Każde wydanie zawiera tekst licencji. Dołącza go `tools/publish.ps1`.
  Nie usuwamy ani nie zmieniamy informacji o licencji i prawach autorskich w plikach.

## 10. Automatyzacja

Każdy powtarzalny krok robi skrypt z `tools/`: build silnika i skryptów, przygotowanie zasobów
(np. eksport i konwersja z Blendera), pakowanie, testy, wydanie.

- Narzędzie działa bez interakcji, z tych samych danych daje ten sam wynik i kończy się kodem
  błędu, gdy coś pójdzie źle. Wtedy może je uruchomić agent, CI albo inny skrypt.
- Build i testy nie zmieniają folderu gry gracza (dane gry tylko czytają), więc mogą działać bez
  nadzoru. Folder gry zmienia tylko instalacja (`tools/install.ps1`).
- Kryteria akceptacji sprawdzają scenariusze testowe wszędzie, gdzie się da (zasada 5, ADR 0004).
  Człowiek ocenia tylko to, czego nie da się zmierzyć.
- Plan, który wprowadza ręczny krok, opisuje go w „Odstępstwach od konstytucji” i mówi, czym
  go zautomatyzujemy.
