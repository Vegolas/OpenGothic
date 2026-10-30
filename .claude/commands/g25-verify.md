---
description: "Gothic 2.5 SDD: weryfikacja kryteriów akceptacji"
argument-hint: "<numer specyfikacji, np. 003>"
---

Weryfikujesz specyfikację `gothic25/specs/$ARGUMENTS-*/spec.md`.

1. Sprawdź, czy wszystkie zadania w `tasks.md` są odhaczone.
2. Jeśli specyfikacja ma scenariusze w `gothic25/tests/$ARGUMENTS/`, uruchom zestaw:
   `gothic25/tools/test.ps1 -Spec $ARGUMENTS` (tryb automatyczny, bez pytania o zgodę, zob.
   `gothic25/CLAUDE.md`). Uruchamiaj na zacommitowanym kodzie: przebieg z `dirty: true`
   w `meta.json` nie zalicza kryterium (ADR 0004).
   - Kryterium, które scenariusz w całości sprawdza oczekiwaniami, zalicza przebieg z wynikiem
     „zaliczony”. Do tabeli wpisz scenariusz, commit, „Claude, automatycznie” i liczby z `report.md`,
     które rozstrzygają kryterium.
   - Niezaliczony przebieg wyjaśnij (błąd w kodzie albo źle dobrany próg). Nie powtarzaj go do skutku.
3. Dla pozostałych kryteriów i dla części wizualnych (płynność, wygląd) przygotuj dla użytkownika
   listę kroków do wykonania w grze (komendy `tools/run.ps1` albo `tools/test.ps1 -Manual`, zapis,
   miejsce, komendy konsoli w trybie `-Dev`). Kryteria, które da się sprawdzić bez gry (build, testy,
   zawartość archiwum przez `python gothic25/tools/vdf.py list`), sprawdź sam.
4. Wyniki wpisz do sekcji „Weryfikacja”: kryterium, wynik, wersja albo commit, kto sprawdzał.
   Nie wpisuj „spełnione” za kryterium, którego nikt nie sprawdził.
5. Gdy wszystkie K są spełnione, ustaw status `Zrobiona` w `spec.md` i w `gothic25/specs/README.md`
   oraz dopisz zmianę do sekcji `[Unreleased]` w `gothic25/CHANGELOG.md`.
