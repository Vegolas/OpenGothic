# ADR 0010: Nowe funkcje zewnętrzne silnika dla skryptów moda

- **Status:** Przyjęta <!-- Proponowana / Przyjęta / Zastąpiona przez ADR NNNN / Odrzucona -->
- **Data:** 2026-11-05 (zaproponowana i przyjęta razem z planem 005)

## Kontekst

[Specyfikacja 005](../specs/005-trening-walki-wrecz-npc/spec.md) potrzebuje pierwszych nowych funkcji
zewnętrznych (externals), czyli funkcji silnika wywoływanych ze skryptów. Do tej pory fork zmieniał
zachowanie silnika tylko przez opcjonalne symbole skryptów ([ADR 0003](0003-przelaczniki-silnika-w-skryptach.md))
i dane moda ([ADR 0008](0008-dokladanie-definicji-animacji-moda-przez.md)). Kolejne pomysły z `roadmap.md`
(reżyser zdarzeń, idealne parowanie) też będą potrzebowały nowych funkcji, więc warto ustalić
zasady raz.

Fakty (sprawdzone 2026-11-05):

- Silnik rejestruje funkcje zewnętrzne po nazwie (`bindExternal` w `common/game/gamescript.cpp:111-303`).
- Gdy skrypty wywołają funkcję, której silnik nie zna, ZenKit woła domyślną obsługę
  (`common/gothic.cpp:1012`). Ta raz wypisuje do logu „not implemented call [nazwa]” i nic nie robi
  (`common/gothic.cpp:1057-1064`, `lib/ZenKit/src/DaedalusVm.cc:262-268`). Mod na starszym silniku
  działa więc bez nowej funkcji, zamiast się wysypać.
- Kompilator `gdc` 0.9.5 zna wbudowane funkcje Gothic II z pliku
  `.tools/gdc-0.9.5/DaedalusBuiltins/gothic.d`, zapisanego w postaci `extern func ...;`. Taką samą
  deklarację przyjmuje też w zwykłym pliku skryptów. Sprawdzone na małym `.src`: kompilacja przeszła,
  a `.DAT` powstał.
- Funkcja zewnętrzna to nazwany symbol w `GOTHIC.DAT`, więc obowiązuje ją [ADR 0005](0005-stabilne-numery-symboli.md)
  (stabilne numery symboli).

## Opcje

1. **Deklaracja `extern func` w nowym pliku skryptów funkcji, która jej używa.** Silnik rejestruje
   funkcję w `bindExternal` obok pozostałych.
   - Zalety: działa z obecnym `gdc` bez zmian w narzędziach. Deklaracja leży przy kodzie, który
     jej używa. Spełnia ADR 0005.
   - Wady: deklaracje są rozsiane po plikach funkcji. Listę trzeba prowadzić w README skryptów.
2. **Własny plik funkcji wbudowanych dla `gdc`** (`--runtime`): kopia `gothic.d` z dopisanymi
   funkcjami moda.
   - Zalety: jedna lista, a skrypty wyglądają jak oryginalne.
   - Wady: kopię trzeba utrzymywać przy każdej wersji `gdc`. Funkcje moda nie są wtedy symbolami
     skryptów moda, więc trudniej sprawdzić, które skrypty ich używają.
3. **Bez nowych funkcji: tylko symbole i dane** (ADR 0003, ADR 0008). Silnik sam wykrywa sytuację
   i zachowuje się inaczej.
   - Zalety: brak nowego interfejsu.
   - Wady: nie da się tak zlecić NPC czynności z poziomu planu dnia, np. ruchu treningowego. Logika
     treści przeszłaby do silnika, wbrew zasadzie 2 konstytucji.

## Decyzja

**Opcja 1.**

- **Deklaracja.** Nowa funkcja zewnętrzna jest zadeklarowana jako `extern func` na początku nowego
  pliku skryptów funkcji, która jej używa. Plik jest dopisany na końcu `Content/Gothic.src` (ADR 0005).
  Kolejna funkcja moda nie dopisuje deklaracji do starszego pliku, tylko deklaruje własne we własnym
  nowym pliku.
- **Nazwy.** Nazwy są ogólne, bez przedrostka moda, w konwencji oryginalnych funkcji:
  - `AI_` dla czynności dopisywanych do kolejki AI postaci, np. `AI_ReadyFist`;
  - `Npc_`, `Wld_`, `Hlp_` dla natychmiastowych zapytań i zmian.

  W silniku nazwa jest rejestrowana małymi literami, jak pozostałe.
- **Zachowanie bez moda.** Funkcja, której nie wywołują oryginalne skrypty G1 i G2, nie zmienia
  działania silnika bez moda. Nie potrzebuje więc osobnego przełącznika z ADR 0003, bo przełącznikiem
  jest samo wywołanie. Plan funkcji pokazuje, że oryginalne skrypty nie mają symbolu o tej nazwie.
- **Starszy silnik.** Na silniku bez danej funkcji wywołanie jest ignorowane, a log ma jedną linię
  „not implemented call”. Plan funkcji opisuje, jak wtedy zachowa się mod.
- **Dokumentacja.** Każda nowa funkcja trafia do `content/Scripts/README.md`, do sekcji „Symbole dla
  silnika”, w tabeli funkcji zewnętrznych: nazwa, parametry, działanie i specyfikacja.

## Konsekwencje

- Mod może zlecać NPC nowe czynności i pytać silnik o nowe dane, a treść (kiedy i komu) zostaje
  w skryptach (zasada 2).
- Nowe funkcje nadają się do zgłoszenia upstreamowi: mają ogólne nazwy i nic nie zmieniają, dopóki
  ktoś ich nie wywoła (zasada 3).
- Parametry funkcji są interfejsem. Zmiana ich znaczenia albo liczby wymaga nowej funkcji, bo stare
  zapisy gry mogą mieć w kolejce AI czynności z dawnymi parametrami.
- Gorzej: deklaracje nie są w jednym miejscu, a `gdc` nie sprawdza, czy silnik ma daną funkcję. Literówkę
  w nazwie wykryje dopiero log „not implemented call”. Scenariusz testowy funkcji sprawdza więc, że tej
  linii w logu nie ma (`expect nolog`).
