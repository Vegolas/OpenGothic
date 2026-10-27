---
description: "Gothic 2.5 SDD: doprecyzowanie pytań otwartych w specyfikacji"
argument-hint: "<numer specyfikacji, np. 003>"
---

Doprecyzowujesz specyfikację `gothic25/specs/$ARGUMENTS-*/spec.md`.

1. Przeczytaj specyfikację i `gothic25/sdd/constitution.md`.
2. Sprawdź, czy nie brakuje pytań: niejasne wymagania, kryteria bez kroków weryfikacji,
   niejasny wpływ na zapisy gry, brak źródła zasobów lub zgody na głos. Dopisz brakujące.
3. Zadawaj użytkownikowi pytania otwarte po jednym, z propozycją odpowiedzi do wyboru.
   Fakty, które da się ustalić z kodu silnika albo skryptów, sprawdź sam zamiast pytać.
4. Po każdej odpowiedzi zaktualizuj wymagania, kryteria i odhacz pytanie.
5. Gdy lista pytań jest pusta, zapytaj użytkownika, czy zatwierdza specyfikację. Dopiero po jego
   „tak” ustaw status `Zatwierdzona` w `spec.md` i w `gothic25/specs/README.md`.
