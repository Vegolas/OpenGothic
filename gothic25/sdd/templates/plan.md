# Plan {{NUMBER}}: {{TITLE}}

- **Specyfikacja:** [spec.md](spec.md)
- **Status:** Szkic
- **Utworzono:** {{DATE}}

## Podsumowanie

<!-- Dwa, trzy zdania: jak zrealizujemy specyfikację. -->

## Warstwa

<!-- Zasoby / skrypty / silnik. Dlaczego ta warstwa jest najtańsza w utrzymaniu, testach
     i aktualizacji z upstreamu (zasada 1). -->

## Obecny stan

<!-- Co już istnieje w silniku i skryptach, z linkami do plików i linii.
     Np. wykrywanie gracza: common/world/objects/npc.cpp (Npc::canSenseNpc). -->

## Projekt

### Silnik (C++)

<!-- Nowe klasy, funkcje zewnętrzne dla skryptów, flagi, ustawienia. Wpisz „brak zmian”, jeśli nie dotyczy. -->

### Skrypty (Daedalus)

<!-- Nowe i zmienione pliki, instancje, funkcje. -->

### Zasoby

<!-- Pliki w content/, ich nazwy i źródło. -->

### Zapisy gry

<!-- Co dochodzi do serializacji, jak wersjonujemy, co ze starymi zapisami. -->

## Pokrycie wymagań

| Wymaganie | Gdzie realizowane |
|---|---|
| W1 | … |

## Bramka konstytucji

- [ ] 1. Tylko OpenGothic, warstwa najtańsza w utrzymaniu
- [ ] 2. Silnik daje mechanizmy, skrypty decydują o treści
- [ ] 3. Fork łatwy do aktualizacji z upstreamu (flagi, styl, brak treści moda w silniku)
- [ ] 4. Zapisy gry wersjonowane
- [ ] 5. Kryteria akceptacji sprawdzalne w grze
- [ ] 6. Prawa do zasobów
- [ ] 7. Język dokumentów i kodu
- [ ] 8. Wpływ na wersję (MAJOR / MINOR / PATCH)
- [ ] 9. Licencja GothicMOD (bez opłat, copyleft dla opracowań, uznanie autorstwa)
- [ ] 10. Automatyzacja (build, zasoby i weryfikacja bez ręcznych kroków)

## Odstępstwa od konstytucji

<!-- Każde odstępstwo z uzasadnieniem. Wpisz „brak”, jeśli nie ma. -->

## Ryzyka

<!-- Co może pójść źle i jak to wcześnie wykryć. -->

## Alternatywy odrzucone

<!-- Inne podejścia i dlaczego nie. -->
