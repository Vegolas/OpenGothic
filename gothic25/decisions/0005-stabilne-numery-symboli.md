# ADR 0005: Stabilne numery symboli w GOTHIC.DAT

- **Status:** Przyjęta <!-- Proponowana / Przyjęta / Zastąpiona przez ADR NNNN / Odrzucona -->
- **Data:** 2026-10-30 (po wykryciu niezgodności zapisów 0.1.0 w 001)

## Kontekst

OpenGothic zapisuje w zapisie gry instancję każdego NPC i przedmiotu jako numer symbolu w skompilowanych
skryptach, a nie jego nazwę (`common/game/serialize.cpp:312`, `common/world/worldobjects.cpp:921`).
Każdy symbol dodany albo usunięty w środku `GOTHIC.DAT` przesuwa numery wszystkich dalszych symboli.
Zapis z poprzedniej wersji wskazuje wtedy na inne symbole i się nie wczytuje.

Tak stało się w [001](../specs/001-combosy-npc-w-walce-wrecz/spec.md): nowa stała `FAI_ORC_ELITE`
w `AI_Constants.d` przesunęła 72715 symboli. Zapis z 0.1.0 kończył się błędem „Cannot init RTN_TOT_3:
not an instance” i powrotem do menu, wbrew W10 i zasadzie 4 konstytucji. Wykrył to scenariusz
`tests/001/K09c` ([003](../specs/003-scenariusze-testowe-i-dziennik-walki/spec.md)).

Każda kolejna funkcja zmieni skrypty, więc problem będzie wracał.

## Opcje

1. **Numery istniejących symboli się nie zmieniają.** Zmiany w istniejących plikach skryptów
   nie dodają ani nie usuwają symboli. Nowe stałe, instancje i funkcje trafiają do nowych plików
   dopisanych na końcu `Content/Gothic.src`. Tam, gdzie stary plik potrzebuje nowej wartości, wpisujemy
   liczbę z komentarzem. Zalety: bez zmian w silniku i formacie zapisu, działa od razu. Wady: wymaga
   dyscypliny. Daedalus wymaga deklaracji przed użyciem, więc nowy symbol z końca nie jest widoczny
   w starych plikach.
2. **Silnik zapisuje NPC i przedmioty po nazwie symbolu.** Nowa wersja zapisu, stare zapisy czytane
   jak dotąd. Zalety: skrypty można zmieniać dowolnie. Wady: zmiana formatu zapisu (zasada 4),
   rozjazd z upstreamem, a stare zapisy nadal zależą od numerów. Wymaga osobnej specyfikacji.
3. **Godzimy się na niezgodność** i ogłaszamy ją w wersji MAJOR (zasada 8). Wady: prawie każde
   wydanie łamałoby zapisy graczy.

## Decyzja

**Opcja 1**, z kontrolą narzędziem:

- Przed wydaniem i przy każdej zmianie skryptów `tools/dat.py prefix <stary GOTHIC.DAT> <nowy GOTHIC.DAT>`
  sprawdza, że każdy symbol poprzedniej wersji ma ten sam numer. Kod 1 oznacza przesunięcie.
- Poprzednią wersję daje paczka poprzedniego wydania (`tools/vdf.py extract`) albo skrypty
  skompilowane z jej commita.
- Scenariusz z zapisem poprzedniej wersji (jak `tests/001/K09c`) sprawdza całość w grze.
- 001 wraca do zgodności: `FAI_ORC_ELITE` usunięte, `MST_OrcElite.d` ma `fight_tactic = 13`.

Opcja 2 zostaje na później, jako osobna specyfikacja, gdy opcja 1 zacznie przeszkadzać.

## Konsekwencje

- Zasada trafia do `content/Scripts/README.md`, który czyta się przed każdą zmianą skryptów.
- Nowe symbole żyją w plikach na końcu kompilacji. Starsze pliki odwołują się do nich tylko liczbą
  albo przez funkcje wywoływane z nowych plików.
- `FIGHT.DAT` i pozostałe pliki `.DAT` nie są objęte zasadą: zapisy nie odwołują się do ich numerów.
  Jeśli się to zmieni, zasada rozszerza się na nie.
- Zapisy zrobione na wersji z przesuniętymi symbolami (lokalne 0.2.0 sprzed poprawki) przestają
  się wczytywać. To dotyczy tylko testów deweloperskich, bo 0.2.0 nie zostało wydane.

## Uzupełnienie (2026-11-01, przy 002 Z1)

`gdc` układa tablicę symboli `GOTHIC.DAT` tak, że wszystkie nazwane symbole stoją przed symbolami
tworzonymi przez kompilator (nazwa zaczyna się bajtem 0xFF, `dat.py` pokazuje go jako `$`; to głównie
stałe literałów). Nowy nazwany symbol, także w nowym pliku na końcu `Gothic.src`, trafia więc
na koniec części nazwanej i przesuwa symbole kompilatora.

Zapis gry odwołuje się tylko do symboli nazwanych: instancji postaci i przedmiotów, kwestii
dialogowych, funkcji planów dnia i stanów AI. Symboli kompilatora używa wyłącznie kod bajtowy tego
samego pliku, który kompiluje się razem z nimi. Dlatego `tools/dat.py prefix` sprawdza tylko symbole
nazwane, a przesunięte symbole kompilatora podaje jako informację.

Pierwszy przypadek: tablice premii z 002 Z1 (6 nowych stałych w `ComboDamage.d`). Nazwane symbole
z 0.1.0 zachowały numery, przesunęło się 45690 symboli kompilatora, a zapis z 0.1.0 wczytuje się
(`tests/001/K09c-zapis-z-0.1.0`).
