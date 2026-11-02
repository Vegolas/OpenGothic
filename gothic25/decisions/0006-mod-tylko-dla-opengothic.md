# ADR 0006: Mod tylko dla OpenGothic

- **Status:** Przyjęta <!-- Proponowana / Przyjęta / Zastąpiona przez ADR NNNN / Odrzucona -->
- **Data:** 2026-10-30

## Kontekst

Zasada 1 konstytucji kazała realizować funkcję w najniższej warstwie, która wystarczy, i stawiała
zasoby na pierwszym miejscu, bo „działają też w oryginalnym silniku”. Mod i tak wymaga forka
OpenGothic: combosy NPC z [001](../specs/001-combosy-npc-w-walce-wrecz/spec.md), scenariusze testowe
z [003](../specs/003-scenariusze-testowe-i-dziennik-walki/spec.md) i przełączniki z
[ADR 0003](0003-przelaczniki-silnika-w-skryptach.md) działają tylko w naszym silniku. Zgodność
zasobów z oryginałem nic więc graczowi nie daje, a kosztuje.

Research narzędzi do animacji (2026-10-30) pokazał ten koszt na przykładzie:

- Jedyny kompilator `.ASC` + `.MDS` do `.MAN` i `.MSB` to sam `Gothic2.exe` (`-zconvertall`).
  Wymaga Windowsa i uruchomienia gry, więc nie nadaje się do CI ani do pracy bez nadzoru.
- OpenGothic w trybie G2 czyta tylko skompilowany `.MSB` (`common/resources.cpp:672`), choć ZenKit
  umie też parsować tekstowy `.MDS`. Zasoby pod oryginał wymuszają więc jego potok kompilacji.

Właściciel projektu zrobił wiele modów do oryginalnego silnika i nie chce przenosić jego ograniczeń
do Gothic 2.5. Priorytetem jest jak największa automatyzacja buildów, zasobów i testów.

## Opcje

1. **Bez zmian.** Zasoby i skrypty mają działać także w oryginalnym silniku, a silnik zmieniamy
   tylko wtedy, gdy niższa warstwa nie wystarczy. Zalety: część moda dałoby się przenieść na
   oryginał. Wady: narzędzia oryginału (kompilacja przez uruchomienie gry) w potoku, brak pełnej
   automatyzacji, rezygnacja z możliwości własnego silnika.
2. **Tylko OpenGothic.** Mod działa wyłącznie na forku. Zgodnością z `Gothic2.exe`, Union, Ninja
   i hookami pamięci Ikarus/LeGo się nie zajmujemy. Warstwę wybieramy według kosztu: prostoty,
   testowalności, automatyzacji i aktualizacji z upstreamu. Zalety: własne formaty i narzędzia,
   silnik może czytać formaty źródłowe, cały potok da się zautomatyzować. Wady: mod nie zadziała
   w oryginale, a w forku przybywa kodu do utrzymania przy aktualizacjach z upstreamu.

## Decyzja

**Opcja 2.** Konstytucja dostaje nową zasadę 1 („Tylko OpenGothic”) i zasadę 10 („Automatyzacja”).

Bez zmian zostają:

- **Zasada 3.** Dotyczy upstreamu OpenGothic, a nie oryginalnego silnika. Bez moda fork dalej działa
  jak upstream (ADR 0003), na czym opierają się m.in. przebiegi `nomod` w scenariuszach testowych.
- **Zasady 4, 6 i 9** (zapisy, prawa do zasobów, licencja GothicMOD). Nie zależą od silnika.
  Gracz nadal potrzebuje własnej kopii Nocy Kruka, bo mod korzysta z jej danych.

## Konsekwencje

- Plan funkcji uzasadnia wybór warstwy kosztem, a nie kolejnością „zasoby, skrypty, silnik”. Zmiana
  w silniku nie jest już ostatecznością, ale nadal musi być ogólnym mechanizmem (zasada 2) i dać się
  utrzymać przy aktualizacjach z upstreamu (zasada 3).
- Zasobów nie sprawdzamy w oryginalnym silniku. Silnik może czytać formaty źródłowe (np. tekstowy
  `.MDS`), a narzędzia moda mogą same zapisywać formaty binarne (`.MAN`, `.MSB`) bez uruchamiania
  `Gothic2.exe`. Konkretny potok animacji rozstrzygnie osobna specyfikacja.
- OpenGothic sprawdza mniej niż oryginał, np. nie porównuje sumy kontrolnej szkieletu zapisanej
  w `.MAN`. Takie kontrole przenosimy do naszych narzędzi i testów, bo nikt inny ich już nie zrobi.
- Gdy skryptom brakuje mechanizmu, dodajemy funkcję zewnętrzną w silniku (`bindExternal`) zamiast
  obchodzić go hookami pamięci w stylu Ikarus/LeGo. Warstwa zgodności `common/game/compatibility`
  zostaje, bo to kod upstreamu.
- Każdy ręczny krok w procesie to dług. Plan, który go wprowadza, nazywa go i mówi, czym go
  zautomatyzujemy (zasada 10).
