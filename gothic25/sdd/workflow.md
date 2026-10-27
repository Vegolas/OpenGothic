# Cykl pracy SDD

Każda funkcja przechodzi przez te same etapy. Każdy etap kończy się dokumentem w katalogu
`specs/NNN-nazwa/`, a kolejny etap startuje dopiero po jego akceptacji.

| Etap | Dokument | Komenda Claude Code | Pytanie, na które odpowiada |
|---|---|---|---|
| 1. Specyfikacja | `spec.md` | `/g25-specify <opis>` | Co i po co, z perspektywy gracza? |
| 2. Doprecyzowanie | `spec.md` (sekcja pytań) | `/g25-clarify NNN` | Czego jeszcze nie wiemy? |
| 3. Plan | `plan.md` | `/g25-plan NNN` | Jak, w której warstwie, jakie ryzyka? |
| 4. Zadania | `tasks.md` | `/g25-tasks NNN` | W jakiej kolejności i małych krokach? |
| 5. Implementacja | kod, zasoby, odhaczone `tasks.md` | `/g25-implement NNN` | — |
| 6. Weryfikacja | sekcja „Weryfikacja” w `spec.md` | `/g25-verify NNN` | Czy kryteria akceptacji są spełnione? |

## Numeracja i nazwy

- Katalog: `specs/NNN-krotka-nazwa`, np. `specs/003-skradanie-widocznosc`.
- `NNN` to kolejny wolny numer, trzy cyfry. Nowy katalog zakłada `tools/new-spec.ps1`.
- Indeks wszystkich specyfikacji jest w `specs/README.md`. Aktualizuj go przy każdej zmianie statusu.

## Statusy specyfikacji

`Szkic` → `Do decyzji` → `Zatwierdzona` → `W realizacji` → `Zrobiona`
(albo `Porzucona`, z jednym zdaniem dlaczego).

- `Do decyzji`: specyfikacja ma otwarte pytania w sekcji „Pytania otwarte”.
- `Zatwierdzona`: nie ma otwartych pytań, właściciel projektu ją zaakceptował.
- Plan wolno pisać dopiero dla specyfikacji `Zatwierdzona`.

## Zasady

- Specyfikacja nie mówi **jak**: żadnych nazw klas, plików ani funkcji silnika.
  To jest miejsce na plan.
- Plan musi przejść „Bramkę konstytucji”: każdą zasadę z `sdd/constitution.md` odhaczamy
  albo opisujemy odstępstwo.
- Zadanie w `tasks.md` jest na tyle małe, żeby zmieścić się w jednym commicie. Zadania, które
  można robić równolegle, oznaczamy `[P]`.
- Decyzje, które dotyczą więcej niż jednej funkcji (narzędzia, formaty, konwencje), trafiają
  do `decisions/` jako ADR, a specyfikacje i plany się do nich odwołują.
- Pomysły, które nie są jeszcze gotowe na specyfikację, zapisujemy w `roadmap.md`.
