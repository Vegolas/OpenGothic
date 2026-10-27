---
description: "Gothic 2.5 SDD: rozbicie planu na zadania"
argument-hint: "<numer specyfikacji, np. 003>"
---

Rozbijasz plan `gothic25/specs/$ARGUMENTS-*/plan.md` na zadania.

1. Przeczytaj `spec.md`, `plan.md` i szablon `gothic25/sdd/templates/tasks.md`.
2. Zapisz `tasks.md` obok planu. Zasady:
   - jedno zadanie to jeden commit, numeracja Z1, Z2…,
   - każde zadanie wskazuje wymagania (W) albo kryteria (K), które realizuje,
   - zadania niezależne od siebie w tej samej fazie oznacz `[P]`,
   - zmiany serializacji i nowe funkcje zewnętrzne dla skryptów to osobne zadania,
   - ostatnia faza to weryfikacja wszystkich kryteriów K w grze.
3. Sprawdź, czy każde W z planu jest pokryte przynajmniej jednym zadaniem. Braki zgłoś.
4. Ustaw status specyfikacji na `W realizacji` w `spec.md` i w `gothic25/specs/README.md`.
