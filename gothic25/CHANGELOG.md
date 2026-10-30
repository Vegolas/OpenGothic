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
- Narzędzia deweloperskie ([specyfikacja 003](specs/003-scenariusze-testowe-i-dziennik-walki/spec.md)):
  - scenariusze testowe (`tools/test.ps1`, `tests/`), dziennik walki wręcz i raport z oczekiwaniami
    (`tools/fightlog.py`),
  - nowe polecenia konsoli w trybie deweloperskim: `call`, `give`, `equip`, `save game`, `screenshot`,
    `toggle fightlog`, `info told`, `immortal`, `remove npc`, `quit`; `insert` stawia postać przed
    bohaterem,
  - silnik wczytuje moda spoza folderu gry (`-game:` ze ścieżką bezwzględną) i zapis spod ścieżki
    (`-save`).

  Gra bez trybu deweloperskiego działa jak dotąd. Kryteria, które da się ocenić z raportu, zalicza
  automatyczny przebieg ([ADR 0004](decisions/0004-zaliczanie-kryteriow-przez-scenariusze.md)).

### Poprawiono

- Zapisy z 0.1.0 znów się wczytują. Nowa stała w skryptach przesuwała numery symboli, którymi
  OpenGothic zapisuje postacie ([ADR 0005](decisions/0005-stabilne-numery-symboli.md)).

## [0.1.0]

### Dodano

- Struktura projektu w SDD: konstytucja, cykl pracy, szablony specyfikacji, planów, zadań i ADR.
- Skrypty: budowanie silnika, kompilacja skryptów, pakowanie `.mod`, instalacja, uruchamianie i publikacja.
