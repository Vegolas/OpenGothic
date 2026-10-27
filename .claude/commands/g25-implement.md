---
description: "Gothic 2.5 SDD: realizacja kolejnych zadań z tasks.md"
argument-hint: "<numer specyfikacji> [numer zadania, np. Z3]"
---

Realizujesz zadania ze specyfikacji Gothic 2.5. Argumenty: $ARGUMENTS

1. Przeczytaj `spec.md`, `plan.md` i `tasks.md` z `gothic25/specs/<numer>-*/` oraz
   `gothic25/sdd/constitution.md`.
2. Weź wskazane zadanie albo pierwsze nieodhaczone. Trzymaj się planu. Jeśli plan okazuje się
   błędny, zatrzymaj się, opisz problem i zaproponuj poprawkę planu zamiast improwizować.
3. Kod silnika pisz w stylu otaczającego kodu OpenGothic. Zachowanie odbiegające od oryginału
   ma być za flagą albo ustawieniem moda (konstytucja, zasada 3).
4. Po zmianie zbuduj to, czego dotyczy zadanie: `gothic25/tools/build-engine.ps1` dla C++,
   `gothic25/tools/build-scripts.ps1` i `gothic25/tools/pack.ps1` dla treści.
   Nie instaluj moda w folderze gry ani nie uruchamiaj gry bez zgody użytkownika.
5. Odhacz zadanie w `tasks.md` i zaproponuj komunikat commita po angielsku. Bez commitowania,
   chyba że użytkownik o to poprosi.
