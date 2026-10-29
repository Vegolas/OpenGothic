# ADR 0004: Zaliczanie kryteriów przez scenariusze testowe

- **Status:** Przyjęta <!-- Proponowana / Przyjęta / Zastąpiona przez ADR NNNN / Odrzucona -->
- **Data:** 2026-10-29 (zaproponowana i przyjęta razem z planem 003)

## Kontekst

Zasada 5 konstytucji mówi, że „Działa” oznacza, że ktoś przeszedł kroki kryterium akceptacji.
Dotąd tym „kimś” był zawsze człowiek w grze. W praktyce przy 001 skończyło się to ogólnym
„działa” zamiast przejścia kroków K1–K12, a kryteria liczbowe (002) są na oko niesprawdzalne.

[Specyfikacja 003](../specs/003-scenariusze-testowe-i-dziennik-walki/spec.md) wprowadza scenariusze
testowe: gra sama przygotowuje sytuację z kryterium, prowadzi dziennik walki, a raport sprawdza
oczekiwania zapisane w scenariuszu. Scenariusz w trybie automatycznym może uruchomić Claude.
Trzeba ustalić, kiedy taki przebieg zalicza kryterium, co wpisujemy do sekcji „Weryfikacja”
i kto może uruchamiać testy bez pytania. Decyzja dotyczy każdej kolejnej specyfikacji.

## Opcje

1. **Raport tylko pomaga, kryterium zalicza człowiek.** Zalety: bez zmiany konstytucji, ocena
   zawsze należy do właściciela projektu. Wady: każde powtórzenie testu po zmianie wymaga
   człowieka, więc testy regresji nie będą robione. Claude nie domknie żadnego kryterium.
2. **Automatyczny przebieg zalicza kryteria, które da się ocenić z raportu. Kryteria wizualne
   zalicza człowiek.** Zalety: liczby (serie, długości combo, obrażenia) sprawdza maszyna
   powtarzalnie i dokładniej niż oko, człowiek ogląda tylko wygląd. Wady: trzeba ufać dziennikowi,
   więc dziennik sam musi przejść porównanie z obserwacją (003 K3). Trzeba pilnować, żeby progi
   oczekiwań nie były dobierane pod wynik.
3. **Wszystko automatycznie, także wygląd na podstawie zrzutów ekranu.** Zalety: człowiek
   niepotrzebny. Wady: pojedyncze klatki nie pokazują płynności animacji, przeskoków ani tempa,
   więc zaliczenie byłoby pozorne.

## Decyzja

**Opcja 2**, z zasadami:

- **Co zalicza.** Przebieg scenariusza w trybie automatycznym zalicza kryterium, gdy:
  - scenariusz w nagłówku wskazuje to kryterium,
  - oczekiwania scenariusza obejmują wszystko, co kryterium każe sprawdzić,
  - przebieg ma wynik „zaliczone”,
  - przebieg poszedł na zacommitowanym kodzie (raport podaje commit i czy drzewo było czyste).

  Kryterium z częścią wizualną (płynność, wygląd, „nie wygląda na przyspieszone”) automat zalicza
  najwyżej częściowo. Część wizualną zalicza człowiek.
- **Co wpisujemy.** Wiersz tabeli „Weryfikacja” podaje: wynik, scenariusz, commit, kto uruchomił
  („Claude, automatycznie” albo imię) i liczby z raportu, które rozstrzygają kryterium. Katalog
  wyników nie trafia do gita, więc wpis musi się bronić bez niego.
- **Niepowodzeń nie powtarzamy do skutku.** Niezaliczony przebieg trzeba wyjaśnić: błąd w kodzie
  albo źle dobrany próg. Poprawka progu to osobny commit z uzasadnieniem w scenariuszu, a nie ciche
  ponowne uruchomienie.
- **Kto uruchamia.** Claude uruchamia scenariusze w trybie automatycznym bez pytania o zgodę.
  Tryb ręczny, instalacja moda w folderze gry i zwykłe uruchomienie gry nadal wymagają zgody
  właściciela projektu. Zasada trafia do `gothic25/CLAUDE.md` razem z narzędziem z 003.
- **Zaufanie do dziennika.** Zmiana w zapisie dziennika walki wymaga ponownego porównania raportu
  z obserwacją w grze (jak 003 K3), zanim jego wyniki znów zaliczą kryteria.
- **Konstytucja.** Zasada 5 dostaje zdanie: „Kroki może przejść także automatyczny scenariusz
  testowy, gdy kryterium da się ocenić z raportu (ADR 0004)”. Tekst zmieniamy razem z narzędziem
  z 003, nie wcześniej.

## Konsekwencje

- Nowe specyfikacje mogą pisać kryteria liczbowe tak, żeby dało się je ocenić z raportu,
  a kryteria wizualne osobno. Kroki dla człowieka nadal są obowiązkowe dla części wizualnej.
- Każda specyfikacja ze scenariuszami ma zestaw testów regresji. Po zmianie w walce uruchamiamy
  zestawy wcześniejszych specyfikacji (np. 001 po 002).
- `/g25-verify` i `sdd/workflow.md` opisują, kiedy uruchamiać scenariusze i jak wpisywać ich wyniki.
- Dziennik walki staje się interfejsem, od którego zależą zaliczenia. Jego format zmieniamy
  ostrożnie, z ponownym porównaniem z obserwacją.
- Gorzej: gra w trybie automatycznym pojawia się na ekranie bez pytania (małe okno z dźwiękiem).
