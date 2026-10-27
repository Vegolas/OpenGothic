---
description: "Gothic 2.5 SDD: weryfikacja kryteriów akceptacji"
argument-hint: "<numer specyfikacji, np. 003>"
---

Weryfikujesz specyfikację `gothic25/specs/$ARGUMENTS-*/spec.md`.

1. Sprawdź, czy wszystkie zadania w `tasks.md` są odhaczone.
2. Dla każdego kryterium K przygotuj dla użytkownika listę kroków do wykonania w grze
   (komendy `tools/run.ps1`, zapis, miejsce, komendy konsoli w trybie `-Dev`).
   Kryteria, które da się sprawdzić bez gry (build, testy, zawartość archiwum przez
   `python gothic25/tools/vdf.py list`), sprawdź sam.
3. Wyniki wpisz do sekcji „Weryfikacja”: kryterium, wynik, wersja albo commit, kto sprawdzał.
   Nie wpisuj „spełnione” za kryterium, którego nikt nie sprawdził.
4. Gdy wszystkie K są spełnione, ustaw status `Zrobiona` w `spec.md` i w `gothic25/specs/README.md`
   oraz dopisz zmianę do sekcji `[Unreleased]` w `gothic25/CHANGELOG.md`.
