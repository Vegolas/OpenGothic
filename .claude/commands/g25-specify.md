---
description: "Gothic 2.5 SDD: nowa specyfikacja funkcji"
argument-hint: "<opis funkcji>"
---

Tworzysz nową specyfikację funkcji dla moda Gothic 2.5. Opis od użytkownika:

$ARGUMENTS

1. Przeczytaj `gothic25/sdd/constitution.md`, `gothic25/sdd/workflow.md`, `gothic25/roadmap.md`
   i `gothic25/specs/README.md`. Jeśli funkcja ma już specyfikację, powiedz to i zakończ.
2. Wymyśl krótki polski tytuł i załóż katalog:
   `powershell -NoProfile -ExecutionPolicy Bypass -File gothic25/tools/new-spec.ps1 -Title "<tytuł>" -Layer "<warstwa>"`.
   Skrypt wypisze ścieżkę do nowego `spec.md`.
3. Wypełnij `spec.md` według szablonu, z perspektywy gracza, **bez szczegółów implementacji**
   (żadnych klas, plików ani funkcji silnika). Wymagania numeruj W1, W2…, kryteria akceptacji
   K1, K2… i podaj dla nich kroki weryfikacji w grze.
4. Wszystko, czego nie da się rozstrzygnąć z opisu, wpisz do „Pytania otwarte” zamiast zgadywać.
   Jeśli lista nie jest pusta, ustaw status `Do decyzji` także w `specs/README.md`.
5. Jeśli pomysł był w `roadmap.md`, zastąp jego opis linkiem do specyfikacji.
6. Na koniec pokaż ścieżkę i listę pytań otwartych. Nie twórz planu.
