# ADR 0002: Przechowywanie dużych zasobów binarnych

- **Status:** Proponowana
- **Data:** 2026-10-27

## Kontekst

Mod będzie zawierał duże pliki binarne: nagrania dialogów (WAV), tekstury, światy `.ZEN`, modele.
Samo `Speech_Addon.vdf` z Nocy Kruka to około 390 MB w 5 369 plikach. Nowe nagrania będą
podobnej skali i będą wielokrotnie generowane od nowa. Zwykły git źle znosi taki rozmiar i historię
zmian binariów, a repozytorium jest forkiem OpenGothic, który klonują też osoby niezainteresowane modem.

## Opcje

1. **Git LFS** dla `content/**` z rozszerzeniami binarnymi (`*.wav`, `*.ogg`, `*.tga`, `*.zen`,
   `*.3ds`, `*.asc`, `*.man`). Wszystko jest w jednym repo, a wersje są powiązane z kodem.
   Wady: limity transferu i miejsca u hostingu, każdy deweloper potrzebuje `git lfs`.
2. **Osobne repozytorium na zasoby** (submoduł albo drugi checkout wskazany w `local.json`).
   Fork silnika zostaje lekki. Wady: dwa repozytoria trzeba wersjonować razem.
3. **Zasoby poza gitem** (dysk sieciowy albo chmura, w repo tylko manifest z sumami SHA-256).
   Najtańsze przy częstym regenerowaniu głosów. Wady: trzeba napisać synchronizację, a historia jest słabsza.

## Decyzja

Do ustalenia przed pierwszym commitem dużych zasobów.

## Konsekwencje

- Do czasu decyzji w `content/` commitujemy tylko małe pliki: skrypty, konfigurację i pojedyncze
  zasoby testowe.
