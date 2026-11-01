# Plan 002: Skalowanie obrażeń w kombo

- **Specyfikacja:** [spec.md](spec.md)
- **Status:** Zatwierdzony
- **Utworzono:** 2026-11-01

## Podsumowanie

Silnik mnoży obrażenia ciosu wręcz z combo do przodu przez procent z tablic w skryptach moda.
Tablica zależy od broni (jednoręczna, dwuręczna, pięści), poziomu talentu i tego, czy atakuje
bohater, czy NPC. Premia działa po obliczeniu obrażeń, a przed zasadą obrażeń minimalnych.
Bez tablic premia wynosi 100%, czyli silnik działa jak upstream.

Dziennik walki z 003 zapisuje premię każdego ciosu. Raport liczy obrażenia na sekundę według
techniki (pełne combo, lewo-prawo, powtarzanie pierwszego ciosu). Kryteria z ciosami NPC
sprawdzają scenariusze, a kryteria z ciosami bohatera krótka gra z dziennikiem, z której liczby
wylicza raport.

## Warstwa

Silnik i skrypty.

- **Silnik.** Obrażenia ciosu wręcz liczy silnik (`DamageCalculator`), a skrypty nie mają
  w tym miejscu żadnego punktu zaczepienia. Wiedzą o trafieniu dopiero po fakcie, w reakcji
  `B_AssessDamage`. Haki pamięci Ikarus/LeGo odpadają (zasada 1). Silnik dostaje więc ogólny
  mechanizm: mnożnik obrażeń według numeru ciosu w combo.
- **Skrypty.** Wartości premii to treść moda (zasada 2), więc są stałymi w skryptach.
  Zmienia się je przez `tools/build-scripts.ps1` i paczkę, bez przebudowy silnika (W2, K2).

Tablice stałych są tańsze w utrzymaniu niż funkcja skryptu wywoływana przy każdym trafieniu
(zob. „Alternatywy odrzucone”). Zmiana w silniku to jedno miejsce w obliczeniu obrażeń i odczyt
stałych przy starcie, więc łatwo ją utrzymać przy aktualizacjach z upstreamu.

## Obecny stan

- **Obrażenia wręcz:** `common/game/damagecalculator.cpp:127-187` (`swordDamage`). W Nocy Kruka
  (`:149-168`) dla każdego typu obrażeń: `max(siła + obrażenia broni − ochrona, 0)`. Słaby cios,
  gdy losowanie przegra z szansą trafienia z talentu, daje `(x−1)/10` (`:160-161`). Typy,
  na które cel jest odporny (ochrona < 0), się nie liczą (`:162`).
- **Obrażenia minimalne:** `damagecalculator.cpp:33-34` (`damageValue`), co najmniej 5
  (`MinDamage`, `damagecalculator.h:13`). Dotyczy tylko trafienia w nieodporny cel.
- **Wywołanie przy trafieniu:** `common/world/objects/npc.cpp:2197` (`Npc::takeDamage`).
  Strzały mają `b != nullptr`, a czary `isSpell`. Obie ścieżki omijają `swordDamage`.
- **Numer ciosu w combo:** `common/graphics/mesh/pose.cpp:821-844`.
  - `Pose::comboLength()` to indeks bieżącego ciosu w animacji, liczony od 0.
  - `Pose::comboInfo().forward` mówi, czy animacja ma kilka ciosów, czyli czy to combo do przodu.
    Ataki boczne to animacje z jednym ciosem.
  - Dziennik walki liczy etap tak samo: `comboLength()+1` (`common/game/fightlog.cpp:319`).
- **Zapis combo:** `Pose::save` i `Pose::load` zapisują `combo.bits` razem z warstwami animacji
  (`pose.cpp:55`, `:83`). Po wczytaniu numer ciosu wynika z zapisanej animacji, bez nowego stanu.
- **Talent:** `Npc::talentSkill` (`npc.cpp:1198`) daje poziom 0, 1, 2 (nowicjusz, wojownik, mistrz).
  NPC dostają talent przez `B_RaiseFightTalent`, tak samo jak bohater
  (`content/Scripts/Content/Story/NPC_Scripts/B_SetFightSkills.d:7-14`).
- **Stałe skryptów w silniku:** `GameScript` czyta stałe po nazwie przy starcie, np.
  `DAM_CRITICAL_MULTIPLIER` (`common/game/gamescript.cpp:379-381`).
- **Dziennik walki (003):**
  - zdarzenie `result` z `combo` i `dmg` (`fightlog.cpp:293-338`);
  - raport z obrażeniami według etapu combo (`gothic25/tools/fightlog.py:187-188`, `:360-366`).
- **Skrypty:** nie ma symboli `COMBO_DAMAGE_*` ani w oryginale, ani w modzie. `Gothic.src` kończy
  się na `STORY\Startup.d`. Nowe symbole muszą trafić do nowych plików za nim (ADR 0005).

## Projekt

### Silnik (C++)

1. **`GameScript`: odczyt tablic.** Przy starcie (`initCommon`, obok `DAM_CRITICAL_MULTIPLIER`)
   silnik szuka stałych tablic `int`:

   | Symbol | Rozmiar | Zawartość |
   |---|---|---|
   | `COMBO_DAMAGE_1H_PLAYER`, `COMBO_DAMAGE_2H_PLAYER` | 3 × n | premie bohatera w procentach: wiersz na poziom talentu (0, 1, 2), kolumna na numer ciosu combo (1..n) |
   | `COMBO_DAMAGE_FIST_PLAYER` | n | premie bohatera dla pięści |
   | `COMBO_DAMAGE_1H_NPC`, `COMBO_DAMAGE_2H_NPC`, `COMBO_DAMAGE_FIST_NPC` | jak wyżej | premie NPC |

   - Długość wiersza `n` silnik liczy z rozmiaru tablicy. Ciosy dalsze niż `n` biorą ostatnią
     kolumnę.
   - Brak tablicy oznacza premię 100%, czyli upstream (ADR 0003).
   - Tablica o złym rozmiarze daje ostrzeżenie w logu i jest pomijana.

   Nowa metoda: `int32_t GameScript::comboDamage(bool player, Talent tal, int32_t level, uint16_t hit) const`.

2. **`Npc::comboDamage()`: premia bieżącego ciosu atakującego.**
   - Gdy `comboInfo().forward`, wynik to procent dla ciosu `comboLength()+1`, broni z `activeWeapon`
     (pięści, gdy jej nie ma) i `talentSkill`. Wybór tablicy bohatera albo NPC: `isPlayer()`.
   - W każdym innym wypadku 100%: ataki boczne, atak z biegu, dobijanie (animacje z jednym ciosem),
     brak animacji ataku.
   - Potwory bez broni: 100% (doprecyzowane przy Z4). Nie walczą pięściami, a silnik już traktuje
     je osobno w `swordDamage` (zawsze mocny cios), więc tablica pięści ich nie dotyczy.

3. **`DamageCalculator::swordDamage`.** Na końcu obliczenia, po filtrze odporności, a przed
   `MinDamage` w `damageValue`: `value = value * premia / 100` (W4). Odporny cel ma `value = 0`
   i flagę `invincible`, więc premia go nie dotyka, a minimum go nie obejmuje (K5).
   Strzały i czary nie przechodzą przez `swordDamage` (W3).

4. **Dziennik walki (W8).**
   - Zdarzenie `result` przy `hit` dostaje pole `bonus`: procent premii, 100 bez premii. Pole `dmg`
     zostaje obrażeniami końcowymi.
   - Wartość premii przekazuje `Npc::takeDamage` z tego samego wywołania, które liczy obrażenia.
   - Dopisanie pola nie zmienia znaczenia istniejących, więc nie wymaga porównania z obserwacją
     (`tests/README.md`).

Bez nowego stanu w zapisach (zob. niżej). Kod w stylu `DamageCalculator` i `GameScript`.

### Skrypty (Daedalus)

- **Tablice premii.** Nowy plik `Content/AI/AI_Intern/ComboDamage.d`, dopisany na końcu
  `Gothic.src`, za `STORY\Startup.d` (ADR 0005). Wartości startowe w procentach dla ciosów 1–4
  (komentarze w pliku po angielsku, jak w skryptach):

  | Tablica | Nowicjusz | Wojownik | Mistrz |
  |---|---|---|---|
  | `COMBO_DAMAGE_1H_PLAYER` | 100, 130, 130, 130 | 100, 150, 200, 260 | 100, 175, 275, 400 |
  | `COMBO_DAMAGE_2H_PLAYER` | 100, 130, 130, 130 | 100, 150, 210, 210 | 100, 175, 275, 400 |
  | `COMBO_DAMAGE_FIST_PLAYER` | 100, 150, 150, 150 | | |
  | `*_NPC` | połowa nadwyżki ponad 100% z tablic bohatera, zaokrąglona do 5 (W7), np. mistrz: 100, 140, 190, 250 | | |

  - Mistrz to wartości z W5.
  - Nowicjusz i wojownik to propozycja dla W6 (zysk rośnie z talentem), do strojenia pomiarem z K6.
  - Kolumny dalej niż długość combo danego poziomu (nowicjusz: 2 ciosy, wojownik z bronią
    dwuręczną: 3) powtarzają ostatnią wartość i nie mają znaczenia.
- **Cel testowy (P0 w spec).** Nowy plik `Content/AI/AI_Intern/ComboDamageTest.d`, także na końcu
  `Gothic.src`:
  - postać `TST_ComboDummy`: człowiek bez broni, ochrona 0, dużo punktów życia;
  - stan startowy `ZS_ComboDummy`: wyłączone percepcje, więc postać stoi, nie blokuje
    i nie oddaje.

  W scenariuszach dochodzi `immortal`, żeby walka nie kończyła się śmiercią celu. Dziennik zapisuje
  obrażenia także wtedy, gdy życie nie spada.
- **Dokumentacja symboli.** Symbole `COMBO_DAMAGE_*` trafiają do tabeli „Symbole dla silnika”
  w `content/Scripts/README.md`.

### Zasoby

Brak.

### Zapisy gry

Brak nowego stanu.
- **Numer ciosu.** Wynika z animacji, a `combo.bits` jest już w zapisie (`pose.cpp:55`, `:83`).
- **Tablice.** Są stałymi skryptów, nie stanem gry.
- **Nowe symbole.** Trafiają do nowych plików na końcu `Gothic.src`, więc numery symboli
  istniejących postaci i przedmiotów się nie zmieniają. Sprawdzenie: `tools/dat.py prefix`
  na `GOTHIC.DAT` z 0.1.0 (ADR 0005). Sprawdza nazwane symbole; symbole tworzone przez kompilator
  przesuwają się przy każdym nowym symbolu i zapisy się do nich nie odwołują (uzupełnienie ADR 0005
  z 2026-11-01, wykryte przy Z1).
- **Zapisy z 0.1.0 i 0.2.0.** Wczytują się (K9).

### Testy (scenariusze 003)

Zasada 10: wszystko, co da się zmierzyć, sprawdza scenariusz.

- **Dziennik i raport.** `tools/fightlog.py` dostaje:
  - kolumnę premii w tabeli „Etap combo”;
  - miary `bonus.stage.<N>.min` i `bonus.stage.<N>.max`;
  - miarę `bonus.dir.<dir>.max` (atak `n` łączony z jego `result`);
  - sekcję „Techniki” dla bohatera: odcinki ciosów rozpoznane po `dir` i `link`, czyli pełne combo
    (łączenia do przodu), lewo-prawo (naprzemienne `left` i `right`) i powtarzanie pierwszego ciosu
    (`fwd`, `link: new`, `combo: 1`). Dla każdego odcinka czas na cios, obrażenia na cios
    i obrażenia na sekundę;
  - opcję `--bonus <tablica>`, która liczy te same obrażenia na sekundę dla innych premii, z obrażeń
    bez premii i zmierzonego czasu na cios. Strojenie wartości nie wymaga wtedy ponownej gry.
- **Scenariusze `tests/002/` (tryb automatyczny, NPC atakuje cel testowy albo bohatera):**
  - K1/K7: paladyn-mistrz i Torwache. Premie według etapu równe tablicy NPC, etap 1 = 100.
  - K2: kopia K1 uruchamiana przez `test.ps1` po zmianie wartości w `ComboDamage.d` bez commita,
    jak 003 K2.
  - K3: bandyta ze stylem normalnym (tylko serie boczne i frontalne) i paladyn: `bonus.dir.left.max`
    i `bonus.dir.right.max` = 100, atak z biegu i dobijanie bez premii.
  - K5: paladyn kontra `MagicGolem` (bez utraty życia) i `StoneGolem` (obrażenia = bez premii ×
    premia, nie mniej niż 5).
  - K8: K1 bez moda (`# mod: off`), premia zawsze 100.
  - K9: zapis w środku combo paladyna, wczytanie i zgodność etapu oraz premii pierwszego ciosu
    po wczytaniu z animacją. Do tego wczytanie zapisu z 0.1.0 (jak 001 K09c).
- **Ciosy bohatera (K1, K4, K6).** Scenariusz do trybu ręcznego ustawia talent, broń i cel testowy.
  Gracz walczy po 20 s każdą techniką, a liczby wylicza sekcja „Techniki” raportu. To jedyny krok
  ręczny (zob. „Odstępstwa”).
- **Regresja.** Zestaw `tests/001` po zmianie: progi z obrażeniami w 001 nie istnieją, a serie
  i combo NPC nie powinny się zmienić.

## Pokrycie wymagań

| Wymaganie | Gdzie realizowane |
|---|---|
| W1 | `Npc::comboDamage` (numer ciosu z `Pose`), tablice z premią 100 dla pierwszego ciosu |
| W2 | tablice `COMBO_DAMAGE_{1H,2H}_{PLAYER,NPC}` (3 poziomy talentu) i `COMBO_DAMAGE_FIST_*` w `ComboDamage.d`, odczyt w `GameScript` |
| W3 | premia tylko przy `comboInfo().forward`, strzały i czary poza `swordDamage`; scenariusz K3 |
| W4 | mnożenie w `swordDamage` po ochronie, osłabieniu słabego ciosu i filtrze odporności, przed `MinDamage`; scenariusz K5 |
| W5 | wartości mistrza 100/175/275/400, sekcja „Techniki” i `--bonus` w raporcie, pomiar K4 |
| W6 | osobne wiersze nowicjusza i wojownika, pomiar K6 i strojenie przez `--bonus` |
| W7 | tablice `*_NPC` (połowa nadwyżki), wybór po `isPlayer()`; scenariusz K7 |
| W8 | pole `bonus` w zdarzeniu `result`, kolumna premii w raporcie, `toggle fightlog` w zwykłej grze deweloperskiej |
| W9 | brak tablic oznacza 100% (ADR 0003); scenariusz K8 bez moda |
| W10 | numer ciosu z zapisanej animacji (`combo.bits`), nowe symbole na końcu `Gothic.src` (ADR 0005); scenariusz K9 i `dat.py prefix` |

## Bramka konstytucji

- [x] 1. Tylko OpenGothic, warstwa najtańsza w utrzymaniu: mechanizm w `DamageCalculator`, bez haków.
- [x] 2. Silnik daje mechanizmy, skrypty decydują o treści: wszystkie wartości w `ComboDamage.d`.
- [x] 3. Fork łatwy do aktualizacji z upstreamu: bez tablic zachowanie upstreamu; ogólne nazwy
      symboli bez przedrostka moda; zmiany w trzech miejscach silnika.
- [x] 4. Zapisy gry wersjonowane: brak nowego stanu, nowe symbole na końcu `Gothic.src` (ADR 0005).
- [x] 5. Kryteria akceptacji sprawdzalne w grze: scenariusze `tests/002` i gra z dziennikiem dla
      ciosów bohatera.
- [x] 6. Prawa do zasobów: brak nowych zasobów.
- [x] 7. Język dokumentów i kodu: dokumenty po polsku, kod i komentarze po angielsku.
- [x] 8. Wpływ na wersję: MINOR (nowa funkcja, zapisy zgodne). Wymaga silnika z tego wydania,
      jak 001; na starszym silniku obrażenia jak w oryginale.
- [x] 9. Licencja GothicMOD: nowe pliki skryptów na tej samej licencji, bez opłat.
- [ ] 10. Automatyzacja: wyjątek dla ciosów bohatera, zob. „Odstępstwa”.

## Odstępstwa od konstytucji

- **Zasada 10, ciosy bohatera grane ręcznie (K1 dla bohatera, K4, K6).**
  - Scenariusze z 003 nie sterują bohaterem: symulowanie wejścia gracza jest poza zakresem 003.
  - Ręczna część to sama gra: po 20 s każdej techniki dla każdej broni i poziomu talentu,
    około 10 minut. Scenariusz przygotowuje sytuację, a liczby, czyli obrażenia na sekundę
    i porównanie technik, wylicza raport.
  - Strojenie premii nie wymaga ponownej gry: `--bonus` przelicza zmierzony czas na cios.
  - Automatyzacja na później: osobna specyfikacja „bohater w scenariuszu”, czyli polecenie, które
    wyprowadza ciosy bohatera z ustalonym wyczuciem czasu (np. na początku okna combo). Wtedy
    K4 i K6 przejdą bez człowieka.

## Ryzyka

- **Atak z biegu albo dobijanie jako animacja z kilkoma ciosami.** Plan zakłada, że to animacje
  z jednym ciosem (`forward = false`). Nawet jeśli nie, ich pierwszy cios ma premię 100%.
  Wczesne wykrycie: scenariusz K3 (`bonus.dir.run.max`, `bonus.dir.finish.max`).
- **Pomiar techniki bohatera jest głośny.** Wyczucie czasu gracza się waha. Zapobieganie: sekcja
  „Techniki” bierze medianę czasu na cios z każdego odcinka i pokazuje rozrzut, a ostateczną
  przewagę W5 sprawdzamy z zapasem.
- **Silniejsze NPC po 001.** Mistrzowie z combo z 001 dostają do 250% na czwartym ciosie, więc
  walki z nimi będą trudniejsze. Wczesne wykrycie: raport obrażeń NPC w scenariuszach 001 po zmianie
  i playtest z P7 w 001 (walki fabularne). Tablice NPC stroi się bez przebudowy silnika.
- **Słaby cios przy niskim talencie.** `(x−1)/10` razy premia daje małe liczby, które minimum 5
  wyrównuje do tej samej wartości dla każdego ciosu. U nowicjusza premia może więc w praktyce
  znikać. To zgodne z W4, ale osłabia W6 dla nowicjusza; K6 to pokaże.
- **Tablice o złym rozmiarze.** Literówka w skrypcie mogłaby po cichu wyłączyć premię. Zapobieganie:
  ostrzeżenie w logu i scenariusz K1, który sprawdza wartości premii.

## Alternatywy odrzucone

- **Funkcja skryptu wywoływana przy każdym trafieniu** (np. `B_ComboDamage(self, other, hit)`
  zwraca procent). Daje dowolną logikę, ale kosztuje wywołanie maszyny skryptów przy każdym
  trafieniu, a kolejność z W4 musiałaby pilnować skrypt. Tablice wystarczają dla W2 i są łatwiejsze
  do sprawdzenia w raporcie.
- **Klasa i instancje jak `C_FightAI_Combo` z 001.** Wymaga nowej klasy i instancji w `GOTHIC.DAT`.
  Stałe tablice są prostsze i nie dodają klasy.
- **Premia do obrażeń broni przed ochroną.** Odrzucone w spec (P3): pancerz zjadałby małe premie,
  a wynik byłby trudny do przewidzenia.
- **Kara dla ataków bocznych zamiast premii dla combo.** Odrzucone w spec (P2).
- **Haki Ikarus/LeGo na obliczenie obrażeń.** Zasada 1: mod jest tylko dla OpenGothic.
