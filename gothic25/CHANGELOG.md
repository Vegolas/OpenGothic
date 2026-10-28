# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/pl/1.1.0/), wersje według SemVer
(zob. konstytucja, zasada 8). `tools/publish.ps1` ostrzega, jeśli brakuje sekcji dla wydawanej wersji.

## [Unreleased]

### Dodano

- Polskie skrypty Nocy Kruka (Unified-PL od VaanaCZ) jako baza w `content/Scripts`, kompilowane
  przez `gdc` 0.9.5 (`tools/get-gdc.ps1`). Zachowanie gry jak w oryginale.
- Zasada 9 konstytucji: mod jest darmowy i niekomercyjny (licencja GothicMOD). Wydania zawierają
  `NOTICE.txt` i tekst licencji.
- Combosy NPC w walce wręcz ([specyfikacja 001](specs/001-combosy-npc-w-walce-wrecz/spec.md)): NPC łączą
  ciosy w combo do przodu tak długie, jak pozwala ich talent, i zależnie od stylu walki używają serii
  bocznej, frontalnej, potrójnej, wirującej i mistrzowskiej. Mistrzowie i elita orków (nowy styl walki)
  bronią się w trakcie serii i przerywają ją, gdy przeciwnik ucieknie. Wymaga silnika z tego wydania.
  Na starszym silniku NPC walczą jak w oryginale.
- Silnik: listy ruchów stylów walki dłuższe niż 6, opcjonalne ustawienia combo stylu (`FA_COMBO_<N>`)
  i łączenie ciosów NPC w oknie combo. Bez skryptów moda silnik działa jak upstream
  ([ADR 0003](decisions/0003-przelaczniki-silnika-w-skryptach.md)).

## [0.1.0]

### Dodano

- Struktura projektu w SDD: konstytucja, cykl pracy, szablony specyfikacji, planów, zadań i ADR.
- Skrypty: budowanie silnika, kompilacja skryptów, pakowanie `.mod`, instalacja, uruchamianie i publikacja.
