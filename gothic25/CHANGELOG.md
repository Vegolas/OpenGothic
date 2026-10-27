# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/pl/1.1.0/), wersje według SemVer
(zob. konstytucja, zasada 8). `tools/publish.ps1` ostrzega, jeśli brakuje sekcji dla wydawanej wersji.

## [Unreleased]

### Dodano

- Polskie skrypty Nocy Kruka (Unified-PL od VaanaCZ) jako baza w `content/Scripts`, kompilowane
  przez `gdc` 0.9.5 (`tools/get-gdc.ps1`). Zachowanie gry jak w oryginale.
- Zasada 9 konstytucji: mod jest darmowy i niekomercyjny (licencja GothicMOD). Wydania zawierają
  `NOTICE.txt` i tekst licencji.

## [0.1.0]

### Dodano

- Struktura projektu w SDD: konstytucja, cykl pracy, szablony specyfikacji, planów, zadań i ADR.
- Skrypty: budowanie silnika, kompilacja skryptów, pakowanie `.mod`, instalacja, uruchamianie i publikacja.
