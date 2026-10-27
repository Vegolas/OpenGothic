---
description: "Gothic 2.5 SDD: plan techniczny dla zatwierdzonej specyfikacji"
argument-hint: "<numer specyfikacji, np. 003>"
---

Piszesz plan techniczny dla `gothic25/specs/$ARGUMENTS-*/spec.md`.

1. Specyfikacja musi mieć status `Zatwierdzona`. Jeśli nie ma, zatrzymaj się i zaproponuj `/g25-clarify`.
2. Przeczytaj `gothic25/sdd/constitution.md`, ADR-y z `gothic25/decisions/` i szablon
   `gothic25/sdd/templates/plan.md`.
3. Zbadaj obecny stan w kodzie: silnik (`common/`), funkcje zewnętrzne skryptów
   (`common/game/gamescript.cpp`), serializację (`common/game/serialize.cpp`) i skrypty moda
   (`gothic25/content/Scripts`). W sekcji „Obecny stan” podawaj ścieżki z numerami linii.
4. Zapisz `plan.md` obok `spec.md`, z szablonu (podmień `{{NUMBER}}`, `{{TITLE}}`, `{{DATE}}`).
   Uzasadnij wybór warstwy, wypełnij tabelę pokrycia wymagań (każde W musi się w niej znaleźć)
   i bramkę konstytucji. Każde odstępstwo opisz w „Odstępstwa od konstytucji”.
5. Decyzję dotyczącą więcej niż tej jednej funkcji wydziel do ADR
   (`gothic25/tools/new-spec.ps1 -Adr -Title "..."`).
6. Pokaż użytkownikowi podsumowanie, ryzyka i odstępstwa. Nie pisz kodu.
