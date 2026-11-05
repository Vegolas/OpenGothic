# anims/: animacje moda

Źródła animacji moda i ich definicji. Build robi z nich pliki gry (`MAN` i `<MODEL>.EXT.MDS`), a
`tools/pack.ps1` pakuje je do moda pod `_WORK/DATA/ANIMS/_COMPILED/`. Zasady:
[ADR 0007](../decisions/0007-zrodla-i-budowanie-animacji-moda.md) (źródła i build),
[ADR 0008](../decisions/0008-dokladanie-definicji-animacji-moda-przez.md) (definicje dokładane przez
silnik), [ADR 0009](../decisions/0009-zmienione-oryginalne-animacje-w-paczce.md) (zmienione
oryginały). Specyfikacja: [004](../specs/004-potok-animacji/spec.md).

## Co tu jest

| Plik | Co to |
|---|---|
| `anims.json` | modele z animacjami moda i reguły odbić lustrzanych |
| `<MODEL>/<MODEL>.EXT.MDS` | definicje moda dla modelu albo nakładki (tylko własne wpisy, ASCII) |
| `<MODEL>/<MODEL>.skeleton.json` | węzły, rodzice i suma kontrolna szkieletu z `<MODEL>.MDH` gry |
| `<MODEL>/<NAZWA>.anim` | klatki animacji w tekście, źródło buildu |
| `<MODEL>/<NAZWA>.blend` | szkielet i akcja tej animacji, bez siatek z gry, do dalszej edycji |

Teraz jest tu jeden model, `HUMANS`, z lewym sierpowym `T_FISTATTACKL`. Prawy sierpowy
`T_FISTATTACKR` nie ma źródła: robi go build z lewego (niżej, „Odbicia”).

Pliki robocze (oryginały z gry, `.blend` z ciałem, podglądy) leżą w `build/anims-work/<MODEL>/`,
poza gitem.

## Zasady

- Animacja moda może być nowa albo zmieniona z oryginału (ADR 0009). Niezmieniona kopia oryginału
  nie trafia do repozytorium ani do paczki (konstytucja, zasada 6): eksport jej odmawia, a
  `anim.py check-pack` sprawdza paczkę.
- Do gry potrzebna jest własna kopia Gothic II: Noc Kruka. Narzędzia czytają z niej szkielet, ciało
  i oryginalne animacje.
- Każdy krok robi narzędzie (`tools/anim.ps1`, `tools/anim.py`). Nie edytuj ręcznie `.anim` ani
  plików z `build/`.

## Przygotowanie (raz)

1. Blender 5.2: ścieżka w `gothic25/local.json`, klucz `blender` (wzór w `local.example.json`), albo
   zmienna `G25_BLENDER`. Folder gry: klucz `gothicDir` albo `G25_GOTHIC_DIR`.
2. Dodatek importu KrxImpExp w przypiętej wersji:

   ```
   tools/get-krx.ps1
   ```

   Instaluje się do `gothic25/.tools/blender-scripts/`, poza profilem Blendera. `anim.ps1` sam go
   tam wskazuje i sprawdza jego sumę kontrolną. Zła ścieżka Blendera albo inny commit dodatku kończy
   się komunikatem, co poprawić.

## Nowa animacja krok po kroku

Przykład: animacja `T_G25PROBA` modelu ludzi.

1. Plik roboczy na czystym szkielecie (poza spoczynkowa, domyślnie 30 klatek przy 25 fps):

   ```
   tools/anim.ps1 new -Anim T_G25PROBA -Frames 24
   ```

   Powstaje `build/anims-work/HUMANS/blend/T_G25PROBA.blend` ze szkieletem, ciałem do podglądu
   i pustą akcją `T_G25PROBA`. Przy pierwszym użyciu narzędzie wyciąga z gry pliki modelu do
   `build/anims-work/HUMANS/`.
2. Otwórz ten plik w Blenderze i ustaw pozy w trybie Pose Mode na akcji `T_G25PROBA`: obrót kości
   `R`, klucz `I`, odtwarzanie spacją. Zapisz `Ctrl+S`.
   - Długość animacji to ręczny zakres klatek akcji (Manual Frame Range: Dope Sheet, tryb Action
     Editor, panel boczny `N`), od 0 do liczby klatek minus 1. `new` ustawia go z `-Frames`.
     Zmieniasz długość, to zmieniasz ten zakres.
   - Postać patrzy w stronę `-Y`, jej lewa strona to `+X`.
   - Stopy powinny stać na ziemi, a korzeń `BIP01` nie powinien dryfować w bok (silnik przesuwa
     postać o ruch korzenia, flaga `M`).
   - Wzorzec z gry otwórz obok w osobnym pliku (`anim.ps1 import`, niżej). Jeśli dołączysz go do
     pliku roboczego, usuń go przed eksportem: eksport wymaga jednego szkieletu w pliku.
3. Eksport do źródeł moda:

   ```
   tools/anim.ps1 export -Blend build/anims-work/HUMANS/blend/T_G25PROBA.blend
   ```

   Powstają `anims/HUMANS/T_G25PROBA.anim` i lekki `anims/HUMANS/T_G25PROBA.blend`. Bez `-Action`
   eksportuje się akcja przypięta do szkieletu.
4. Definicja w `anims/HUMANS/HUMANS.EXT.MDS`, w bloku z numerem specyfikacji (`// G25 NNN`):

   ```
   // G25 NNN: krótko, po co ta animacja.
   ani ("t_G25Proba" 1 "" 0.1 0.2 M. "T_G25PROBA.ASC" F 1 24)
   {
       *eventTag (0 "DEF_HIT_LIMB" "BIP01 R HAND")
       *eventTag (0 "DEF_OPT_FRAME" "11")
       *eventTag (0 "DEF_HIT_END" "16")
       *eventTag (0 "DEF_WINDOW" "11 16")
       *eventSFX (9 "WHOOSH" R:2500)
   }
   ```

   - Nazwa `ani` to nazwa animacji (wielkość liter bez znaczenia). Silnik bierze klatki
     z `HUMANS-T_G25PROBA.MAN`, a nazwę pliku `.ASC` pomija.
   - Zakres `F 1 N`: `N` to liczba klatek animacji. Build sprawdza, że się zgadza.
   - Klatki zdarzeń: `DEF_OPT_FRAME` (chwila trafienia) i efekty (`eventSFX`, `eventPFX`) liczą się od
     pierwszej klatki zakresu. `DEF_HIT_END` (koniec ataku) i `DEF_WINDOW` (okno combo) liczą się od
     początku animacji. Trafienie przy `DEF_OPT_FRAME 11` wypada 11 klatek, czyli 440 ms, po
     początku ciosu.
   - Dźwięk jak w oryginałach: `R:2500`. Bez `R:` zasięg ma tylko 1000.
5. Build i podgląd w grze. `tools/test.ps1` sam pakuje moda z bieżących plików. Scenariusz, np.
   `build/proba.txt`:

   ```
   info told DIA_Xardas_Hello
   set time 12 0
   wait 1
   ani info hero T_G25PROBA
   play ani hero T_G25PROBA
   wait 0.4
   screenshot proba-1.png
   wait 0.4
   screenshot proba-2.png
   quit
   ```

   ```
   tools/test.ps1 -Scenario build/proba.txt
   ```

   Wyniki trafiają do `build/test-runs/<data>-<czas>-proba/`. `ani info` w `log.txt`
   (`scenario: ani T_G25PROBA origin mod ...`) pokazuje definicję tak, jak ją widzi gra. Zrzuty
   pokazują ruch. Gra otwiera się wtedy w małym oknie i zamyka sama. W zwykłej grze:
   `tools/run.ps1 -Pack -Dev`, potem konsola `F2` i `play ani hero T_G25PROBA`. Format scenariuszy
   opisuje [`tests/README.md`](../tests/README.md).
6. Przed commitem:

   ```
   tools/anim.ps1 check
   python tools/anim.py check-pack --gothic "<folder gry>"
   ```

   `check` porównuje każdy `.blend` z `anims/` z jego `.anim` (eksportuje go jeszcze raz).
   `check-pack` sprawdza zbudowaną paczkę z `build/game`: nie może w niej być pliku równego plikowi
   gry ani MAN z próbkami oryginału.
7. Commit: `.anim`, lekki `.blend` i zmiana w `*.EXT.MDS`.

Dalsza edycja zacommitowanej animacji: `tools/anim.ps1 open -Blend anims/HUMANS/T_G25PROBA.blend`
robi plik roboczy z ciałem w `build/anims-work/HUMANS/blend/`. Potem kroki 2, 3, 5 i 6.

## Oryginał jako wzorzec albo punkt wyjścia

```
tools/anim.ps1 import -Anim S_FISTATTACK
tools/anim.ps1 import -Anim T_1HATTACKL -Overlay HUMANS_1HST1
```

Powstaje `build/anims-work/HUMANS/blend/<NAZWA>.blend` z oryginalną animacją na szkielecie z ciałem.
Akcja jest oznaczona jako pochodząca z gry. Jeśli ją zmienisz, możesz ją wyeksportować jako
animację moda, także pod nową nazwą (zmień nazwę akcji). Eksport niezmienionej kopii kończy się
błędem. Wyjątek dla lokalnych danych testowych, tylko do `build/`:

```
tools/anim.ps1 export -Blend <plik> -AllowDerived -Out build/<katalog>
```

## Definicje moda w `<MODEL>.EXT.MDS`

- Plik ma tylko wpisy moda, w składni MDS z blokiem `Model` i `aniEnum`, i tylko znaki ASCII.
  Zmiany jednej specyfikacji idą do bloku z komentarzem `// G25 NNN`.
- Silnik dokłada go do definicji modelu z gry (ADR 0008). Wpis o nazwie animacji z gry zastępuje
  wszystkie wpisy o tej nazwie (`ani`, `aniAlias`, `aniComb`). `aniBlend` zastępuje wpis o tych
  samych dwóch nazwach. `aniDisable` i `modelTag` dochodzą. W `log.txt` gry jest linia
  `model script extension "HUMANS.EXT.MDS": N added, M replaced`.
- Nakładka (np. `HUMANS_1HST1`) ma własny plik `HUMANS_1HST1.EXT.MDS` w `anims/HUMANS/`.
- Definicje, które widzi gra, wypisuje:

  ```
  python tools/anim.py defs HUMANS T_FISTATTACKL T_FISTATTACKR --gothic "<folder gry>"
  ```

  W grze to samo daje `ani info <postać> <animacja>` (konsola albo scenariusz).

## Format `.anim`

Tekst z każdym polem MAN, więc MAN -> `.anim` -> MAN daje te same bajty (opis na początku
`tools/anim.py`):

- nagłówek `g25-anim 1`, `model`, `name`, `next`, `version`, `layer`, `fps`, `checksum` szkieletu,
  `bbox`;
- lista węzłów (`node <indeks w MDH> <nazwa>`);
- klatki: w każdej po jednej linii na węzeł, kwaternion `w x y z` i pozycja w cm.

Nagłówek MAN (nazwa, warstwa, `next`) build bierze z definicji.

## Odbicia

Animację z drugiej strony (np. prawy sierpowy z lewego) robi build z reguły w `anims.json`, bez
osobnego źródła:

```json
"mirrors": {
  "t_FistAttackR": {"mirror": "t_FistAttackL", "stance": "S_FISTRUN", "blend": [4, 7]}
}
```

- Build odbija klatki względem płaszczyzny symetrii postaci i zamienia kości lewe z prawymi.
  Odbija też definicję (strony w `DEF_HIT_LIMB` i innych slotach) i wstawia ją do zbudowanego
  `HUMANS.EXT.MDS` zaraz za źródłem.
- `stance` i `blend`: źródło zaczyna się i kończy w niesymetrycznej postawie (lewa noga z przodu).
  Odbicie wchodzi z pierwszej klatki tej postawy przez `blend[0]` klatek i wraca do niej przez
  `blend[1]`, a stopy zostają tam, gdzie ma je postawa. Bez tego nogi zamieniałyby się miejscami.
- Odbicie potrzebuje szkieletu z gry, więc build z regułą odbicia wymaga folderu gry.
- Samo odbicie, z raportem kierunku ruchu: `python tools/anim.py mirror <.anim albo SKRYPT-ANI>
  --name <NOWA> --gothic "<folder gry>" [--compare SKRYPT-ANI] [--out plik.anim]`.

## Dane, które włączają zachowania silnika

| Dane | Zachowanie |
|---|---|
| `<MODEL>.EXT.MDS` w paczce | silnik dokłada definicje moda do modelu z gry (ADR 0008); bez pliku model działa jak oryginał |
| `T_FISTATTACKL`, `T_FISTATTACKR` w modelu | atak z lewej i z prawej pięściami: bohater i NPC wyprowadzają sierpowe (004 W15); bez nich ciosy boczne pięściami są ciosami do przodu |

## Polecenia

| Polecenie | Co robi |
|---|---|
| `tools/anim.ps1 new -Anim <N> [-Frames K]` | plik roboczy nowej animacji na czystym szkielecie |
| `tools/anim.ps1 import -Anim <N> [-Overlay <SKRYPT>]` | plik roboczy z oryginałem z gry |
| `tools/anim.ps1 open -Blend anims/<MODEL>/<N>.blend` | plik roboczy z ciałem ze źródła moda |
| `tools/anim.ps1 export -Blend <plik> [-Action <A>]` | `.anim` i lekki `.blend` do `anims/<MODEL>/` |
| `tools/anim.ps1 check` | każdy `.blend` z `anims/` zgodny ze swoim `.anim` |
| `tools/anim.ps1 roundtrip` | wszystkie oryginały modelu: MAN -> Blender -> MAN bajt w bajt |
| `python tools/anim.py build --gothic <gra>` | MAN i `*.EXT.MDS` do `build/anims/_COMPILED/` (robi to też `pack.ps1`) |
| `python tools/anim.py defs <MODEL> [ANI...] --gothic <gra>` | definicje modelu z gry i moda, jak w grze |
| `python tools/anim.py check-pack --gothic <gra>` | paczka moda kontra pliki gry |
| `python tools/anim.py mirror ...` | odbicie lustrzane z raportem |
| `python tools/anim.py fixtures --gothic <gra>` | lokalne dane testowe 004 w `build/anims-fixtures/` (nigdy do repozytorium) |
| `ani info <postać> <ani>`, `play ani <postać> <ani>` | konsola gry i scenariusze: definicja i odtworzenie animacji |
