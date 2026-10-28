# ADR 0003: Włączanie zmian silnika przez symbole skryptów moda

- **Status:** Przyjęta <!-- Proponowana / Przyjęta / Zastąpiona przez ADR NNNN / Odrzucona -->
- **Data:** 2026-10-28 (zaproponowana i przyjęta razem z planem 001)

## Kontekst

Konstytucja (zasada 3) wymaga, żeby zachowanie silnika odbiegające od oryginalnego Gothica
włączać flagą albo ustawieniem moda, domyślnie wyłączonym: bez moda fork ma działać jak upstream.
Zasada 2 każe trzymać treść (które NPC, jakie wartości) w skryptach albo danych moda.

Pierwsze funkcje, które tego potrzebują, to [001: Combosy NPC](../specs/001-combosy-npc-w-walce-wrecz/spec.md)
i [002: Skalowanie obrażeń w kombo](../specs/002-skalowanie-obrazen-w-kombo/spec.md). Kolejne
(skradanie, reżyser zdarzeń z `roadmap.md`) będą miały ten sam problem.

Stan w silniku:

- OpenGothic z pliku `.ini` moda czyta tylko `[FILES]` i `[SETTINGS]` (`common/gothic.cpp:42-55`).
  Sekcji `[OVERRIDES]` z `system/Gothic25.ini` nie czyta wcale.
- Silnik już dziś czyta wiele opcjonalnych symboli skryptów po nazwie i ma dla nich wartości
  domyślne, gdy symbolu brak: `NPC_ATTACK_FINISH_DISTANCE` (`common/game/fightalgo.cpp:263`),
  `DAM_CRITICAL_MULTIPLIER`, `TRADE_VALUE_MULTIPLIER`, `B_RefreshAtInsert`
  (`common/game/gamescript.cpp:343-391`), instancje `FA_*_<N>` stylów walki
  (`common/game/definitions/fightaidefinitions.cpp`).

## Opcje

1. **Opcjonalne symbole w skryptach moda.** Nowe zachowanie silnika włącza się, gdy skrypty
   definiują określony symbol: stałą, instancję albo klasę. Gdy symbolu nie ma (oryginalne skrypty
   G1 i G2, inne mody), silnik działa jak upstream. Zalety: zgodne z istniejącym wzorcem OpenGothic,
   przełącznik i treść są w tym samym miejscu (skryptach moda), nie trzeba nowej infrastruktury,
   inne mody mogą użyć mechanizmu bez zmian w silniku, łatwo zgłosić zmianę do upstreamu.
   Wady: przełącznik jest wkompilowany w `.DAT`, gracz nie wyłączy go bez przebudowy skryptów.
   Nazwy symboli stają się interfejsem, który trzeba dokumentować.
2. **Klucze w `.ini` moda** (np. sekcja `[OPENGOTHIC]` w `Gothic25.ini`). Zalety: przełącznik widać
   bez czytania skryptów, można go zmienić bez kompilacji. Wady: trzeba dopisać do silnika czytanie
   ustawień z `.ini` moda, a treść (wartości) i tak zostaje w skryptach, więc konfiguracja jednej
   funkcji leży w dwóch miejscach.
3. **Jedna globalna stała „tryb Gothic 2.5”** włączająca wszystkie zmiany naraz. Zalety: prostota.
   Wady: brak ziarnistości (np. 001 zmienia tylko część stylów walki), wszystko albo nic,
   trudne do zgłoszenia upstreamowi.

## Decyzja

**Opcja 1.**

- Każda zmiana zachowania silnika ma własny, opcjonalny symbol w skryptach, który ją włącza.
  Symbol może być jednocześnie nośnikiem treści (np. instancja z parametrami).
- Brak symbolu oznacza dokładnie zachowanie upstreamu. Plan funkcji wskazuje, które symbole
  ją włączają, i dowodzi, że oryginalne skrypty G1 i G2 ich nie definiują.
- Nazwy symboli są ogólne, bez przedrostka moda (np. `FA_COMBO_<N>`, a nie `G25_...`), bo mechanizmy
  mają nadawać się do zgłoszenia do Try/OpenGothic. Nazwy trzymają się konwencji z otoczenia
  (stylów walki `FA_*_<N>`, stałych wielkimi literami).
- Lista symboli rozpoznawanych przez silnik trafia do `content/Scripts/README.md` (sekcja
  „Symbole dla silnika”), z odnośnikiem do specyfikacji.

## Konsekwencje

- Bez skryptów moda (zwykły Gothic I i II) fork zachowuje się jak upstream, co łatwo sprawdzić
  w kryteriach „bez moda bez zmian”.
- Mod uruchomiony na starszym silniku działa, tylko bez nowych zachowań. Silnik ignoruje nieznane
  mu symbole.
- Gracz nie wyłączy pojedynczej zmiany w opcjach. Jeśli kiedyś będzie to potrzebne, przełącznik
  w menu będzie osobną funkcją.
- Ta decyzja nie dotyczy zapisów gry. Nowy stan w zapisie nadal wymaga wersjonowania (zasada 4).
  Jak pogodzić własne wersje z numeracją upstreamu, rozstrzygnie osobny ADR przy pierwszej funkcji,
  która tego potrzebuje.
