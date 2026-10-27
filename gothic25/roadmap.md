# Roadmapa

Pomysły, które nie mają jeszcze specyfikacji. Gdy pomysł dojrzeje, zakładamy dla niego
specyfikację (`/g25-specify`) i przenosimy tutaj tylko link.

## Funkcje

### Spójne polskie głosy w Nocy Kruka

- **Warstwa:** zasoby (bez zmian w kodzie).
- Kwestie z dodatku to pliki `_WORK/DATA/SOUND/SPEECH/DIA_ADDON_*.WAV` w `Speech_Addon.vdf`.
  Podmiana polega na wrzuceniu WAV o tej samej nazwie do `content/Sound/Speech/`.
- Potrzebna lista postaci, które w dodatku mówią innym głosem niż w podstawce, wraz z liczbą
  kwestii do przegrania.
- Głos AI (np. ElevenLabs) tylko za zgodą aktora, zob. konstytucja, zasada 6.

### Losowe zdarzenia i bardziej żywy świat

- **Warstwa:** silnik i skrypty. Silnik: „reżyser zdarzeń” (losowanie, planowanie, zapis stanu,
  nowe funkcje dla skryptów). Skrypty: konkretne zdarzenia.
- Ze skryptów da się już używać LeGo FrameFunctions (`DirectMemory::tick`), ale HookEngine
  nie działa i nie zadziała.

### Skradanie

- **Warstwa:** silnik i skrypty.
- Dziś NPC wykrywa gracza tylko na podstawie zasięgu, linii wzroku i hałasu
  (`Npc::canSenseNpc` w `common/world/objects/npc.cpp`). Skradanie wyłącza jedynie hałas kroków.
- Kierunek: widoczność zależna od światła i postawy, stopniowe wykrywanie, wskaźnik na ekranie.

## Infrastruktura

- Kompilator Daedalus i baza skryptów: [ADR 0001](decisions/0001-kompilator-daedalus.md).
- Przechowywanie dużych zasobów: [ADR 0002](decisions/0002-duze-zasoby-w-repo.md).
- CI: budowanie silnika i paczki moda na GitHub Actions (po decyzji z ADR 0001).
