# ADR 0009: Zmienione oryginalne animacje w paczce moda

- **Status:** Przyjęta <!-- Proponowana / Przyjęta / Zastąpiona przez ADR NNNN / Odrzucona -->
- **Data:** 2026-11-04, decyzja właściciela projektu (spec. 004, P9 rozstrzygnięte od nowa). Zmienia
  część o animacjach w [ADR 0008](0008-dokladanie-definicji-animacji-moda-przez.md) („Kontekst”
  i „Konsekwencje”). Mechanizm dokładania definicji z ADR 0008 zostaje bez zmian.

## Kontekst

- Zadanie Z4 planu 004 sprawdziło licencję MDK (ADR 0007, „Kontekst”). Na GothicMOD są tylko skrypty
  i dane nowo utworzone przez moderów. Oryginalne animacje z gry podlegają umowie licencyjnej gry,
  która formalnie nie pozwala ich rozpowszechniać, także po zmianach.
- 2026-11-03 właściciel zdecydował (spec. 004, P9), że do paczki trafiają tylko animacje z własnymi
  kluczami.
- Pierwszy sierpowy z własnymi kluczami (zadanie Z15) działał w grze, ale według właściciela
  stylem mocno odstawał od reszty animacji. Żeby nowe ruchy pasowały do gry, muszą zaczynać się od
  oryginalnych póz (np. postawy bojowej z pięściami `S_FISTRUN`) i często są przeróbką oryginału.
- Mody do Gothica zwykle rozpowszechniają zmienione oryginalne animacje. Gothic 2.5 i tak wymaga
  od gracza własnej kopii gry (silnik czyta jej archiwa, ADR 0006).
- Konstytucja (zasada 6) zabrania publikowania plików z gry w niezmienionej postaci. P9 było
  ostrzejsze niż konstytucja.

## Opcje

1. **Zostaje P9: tylko własne klucze.** Zalety: zgodność z literą umowy licencyjnej gry. Wady:
   animacje odstają stylem, przejścia z oryginalnych póz są widoczne, każda animacja od zera.
2. **Tylko pozy wyjściowe z oryginałów.** Animacja moda może zaczynać się i kończyć oryginalną pozą,
   ale całe oryginalne animacje nie trafiają do paczki. Zalety: płynne przejścia. Wady: granica jest
   umowna, nie da się np. przerobić oryginalnego ciosu.
3. **Zmienione oryginalne animacje mogą trafić do paczki.** Niezmienione pliki z gry nie trafiają.
   Zalety: styl spójny z grą, najkrótsza droga do nowych ruchów, tak jak w innych modach. Wady:
   formalny konflikt z umową licencyjną gry. W publicznym repozytorium i w paczce jest materiał
   pochodny od animacji Piranha Bytes.

## Decyzja

**Opcja 3.**

- Animacja moda może powstać z oryginału: import do Blendera (`tools/anim.ps1 import`), zmiany,
  eksport do `anims/` (`.anim` i `.blend` w repozytorium, ADR 0007). Może też zaczynać się od
  oryginalnej pozy na czystym szkielecie (`tools/anim.ps1 new`).
- Niezmienione pliki z gry nie trafiają ani do repozytorium, ani do paczki (zasada 6):
  - eksport odmawia akcji z importu, której klatki są takie same jak w oryginale (także pod nową
    nazwą);
  - `tools/anim.py check-pack` odrzuca MAN o próbkach równych oryginałowi i pełne definicje modelu
    z gry.

  Wyjątkiem są jawne lokalne dane testowe w `gothic25/build` (`-AllowDerived`).
- Definicje nadal są tylko wpisami moda w `<MODEL>.EXT.MDS` (ADR 0008). Wpis może być zmienioną
  kopią oryginalnego wpisu.
- Nowe animacje i wpisy to praca moda na licencji GothicMOD (zasada 9). Animacje zmienione
  z oryginałów są opracowaniem dzieła Piranha Bytes. `NOTICE.txt` wydania mówi o tym formułą
  „na podstawie dzieła Piranha Bytes”.

## Konsekwencje

- W repozytorium (publicznym) i w paczce mogą być animacje pochodne od oryginałów. Ryzyko
  z umowy licencyjnej gry właściciel przyjmuje świadomie. Gdyby właściciel praw zgłosił sprzeciw,
  takie animacje trzeba usunąć z repozytorium i z paczki. Pochodzenie zdradza historia commitów
  i akcja w pliku `.blend` (właściwość `g25_anim`, pochodzenie `game` przy imporcie).
- Blokada eksportu (spec. 004, W16) pilnuje już tylko niezmienionych oryginałów.
- Kolejne animacje (np. sierpowe w Z15-Z17) mogą zaczynać się od oryginalnej postawy
  i przerabiać oryginalne ciosy.
