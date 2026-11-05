# Plan 005: Trening walki wręcz NPC

- **Specyfikacja:** [spec.md](spec.md)
- **Status:** Zatwierdzony
- **Utworzono:** 2026-11-05

## Podsumowanie

Silnik dostaje dwie nowe funkcje dla skryptów, obie jako czynności kolejki AI:

- `AI_PracticeMove(npc, move)`: jeden ruch treningowy, czyli cios do przodu, z lewej, z prawej, blok
  albo odskok. Ruch nie ma celu, nie zadaje obrażeń, a ciosy łączą się w combo tak jak w walce;
- `AI_ReadyFist(npc)`: dobycie pięści także wtedy, gdy NPC ma broń.

Skrypty dostają plany dnia `TA_Practice_Melee` (bronią) i `TA_Practice_Fist` (pięściami). Stan AI
losuje w nich serie, przerwy, odpoczynki, bloki i odskoki według ustawień ze skryptów. Dziennik walki
oznacza ruchy treningowe i liczy miary do raportu. Scenariusze w `tests/005/` sprawdzają kryteria na
postaciach testowych na placu koszar straży w Khorinis.

## Warstwa

Skrypty i silnik. Skrypty decydują o treści treningu: kolejność, długość serii, przerwy, proporcje
i kto ćwiczy. Silnik dostaje tylko mechanizm „wykonaj ruch walki bez celu i bez obrażeń”. Same skrypty
nie wystarczą, bo:

- `AI_PlayAni` nie łączy ciosów w combo. Gra animację od początku (`startAnimAndGet`), a po
  `DEF_HIT_END` etapu silnik zdejmuje warstwę ataku. Combo do przodu (W2) wymaga ścieżki
  `Npc::doAttack` i `Pose::continueCombo`.
- Klatka trafienia każdej animacji ataku zadaje obrażenia bieżącemu celowi NPC (`commitDamage`).
  NPC po walce zachowuje cel, więc cios z `AI_PlayAni` może zranić bohatera (W6).
- Dziennik walki zapisuje tylko ciosy z `doAttack`, więc scenariusze nie policzyłyby treningu (W9).

Walka przez AI walki z celem (manekin, niewidzialny przeciwnik albo partner) odpada. Wymaga celu,
zasięgów i stylu walki, a przy partnerze wywołuje reakcje innych NPC. To pomysł sparingu
z `roadmap.md`, poza zakresem 005.

## Obecny stan

**Obecny trening z mieczem**

- `ZS_Practice_Sword` (`gothic25/content/Scripts/Content/AI/Human/TA_Human/ZS_Practice_Sword.d`):
  - na starcie zakłada najlepszą broń (`:19`);
  - w pętli NPC bez broni dostaje maczugę (`:28-33`);
  - pętla dobywa broni (`:34`), gra `T_1HSFREE` i wraca na waypoint (`:39-41`);
  - na końcu NPC chowa broń (`:48-49`).
- Plan dnia `TA_Practice_Sword` jest w `.../AI/Human/TA.d:19`. Używa go 26 NPC, np. strażnik
  `MIL_329_Miliz` od 07:00 do 20:58 na `NW_CITY_HABOUR_KASERN_CENTRE_02`
  (`.../Story/NPC/MIL_329_Miliz.d:43`).
- Talent: `B_SetFightSkills` (`.../Story/NPC_Scripts/B_SetFightSkills.d`) ustawia procent i poziom
  0/1/2 (próg 30% i 60%). Skrypty odczytują poziom przez `Npc_GetTalentSkill`
  (`common/game/gamescript.cpp:2137`), a silnik nakłada nakładki talentu `*_1HST1/2`
  (`common/world/objects/npc.cpp:1140-1149`). Szybkość ciosów i długość combo wynikają więc z modelu.

**Ciosy i combo w silniku**

- `Npc::doAttack` (`common/world/objects/npc.cpp:3960`) woła `MdlVisual::continueCombo`, a ten
  `Pose::continueCombo` (`common/graphics/mesh/pose.cpp:730`). W oknie combo kolejny cios do przodu
  przechodzi w następny etap, a cios boczny startuje od razu. Potem `doAttack` zapisuje cios do
  dziennika walki (`:3977`).
- Stan bieżącego ciosu podaje `Pose::comboInfo` (`common/graphics/mesh/pose.h:30-37`): okno,
  `DEF_HIT_END`, czy to combo do przodu i czy etap jest ostatni. Ostatni etap zależy od nakładki
  talentu.
- NPC w walce łączy ciosy w `Npc::implComboLink` (`npc.cpp:1916`). Na ostatnim etapie combo usuwa
  kolejne ciosy do przodu (limit talentu, `:1923-1929`). Pięści biją bokiem tylko wtedy, gdy model
  ma sierpowe (`Npc::hasFistSideAttack`, `:1057`, 004).
- `Npc::implAttack` (`npc.cpp:1584`) działa tylko z celem (`:1585`).
- Blok to `doAttack(AttackBlock, BS_PARADE)` (`blockSword` `:4029`, `blockFist` `:3987`), a odskok
  to `setAnim(Anim::MoveBack)` (`:1819`).
- Gdy NPC czeka, ruch z animacji nadal go przesuwa (`MoveAlgo::npcMoveSpeed` z `WaitMove`,
  `common/game/movealgo.cpp:552-564`). Ciosy i odskoki odsuwają więc NPC od waypointu.

**Obrażenia i percepcje**

- Zdarzenie `DEF_OPT_FRAME` woła `Npc::commitDamage` (`npc.cpp:2490-2491`). Ta zadaje obrażenia
  celowi `currentTarget`, jeśli jest w zasięgu i kącie (`:2134-2149`), a inaczej zapisuje pudło
  (`no_target`, `range`, `angle`).
- Percepcje walki (`PERC_ASSESSFIGHTSOUND`, `PERC_ASSESSOTHERSDAMAGE` i inne) wysyła dopiero
  `takeDamage` (`npc.cpp:2168`, `:2269-2274`). Cios, który nie trafia, ich nie wywołuje.

**Kolejka AI, plany dnia i funkcje zewnętrzne**

- Czynności kolejki AI są wyliczone w `common/game/constants.h:342-394`, a wykonuje je
  `Npc::nextAiAction` (`npc.cpp:2578`). `AI_PlayAnim` (`:2698-2707`) czeka całą długość animacji.
- `AI_DrawWeaponMelee` (`:2851`) woła `drawWeaponMelee`. Ta dobywa pięści tylko wtedy, gdy NPC nie ma
  broni (`:3867-3868`). `drawWeaponFist` (`:3837`) istnieje, ale żadna czynność skryptów jej nie woła.
- `AiQueue::save` zapisuje numer czynności i ogólne pola (`common/world/aiqueue.cpp:9-17`).
  Nowa czynność nie zmienia formatu zapisu.
- `Npc::startState` (`npc.cpp:3072`) przy zmianie stanu czyści kolejkę AI i woła koniec poprzedniego
  stanu (`:3086-3087`). Pozostałe ruchy treningu znikają więc przy końcu pory treningu.
- Silnik zapisuje plan dnia postaci (`npc.cpp:347-352`).
- Funkcje zewnętrzne: `bindExternal` (`common/game/gamescript.cpp:111-303`). Nieznaną funkcję silnik
  ignoruje z jedną linią w logu (`common/gothic.cpp:1012`, `:1057`). `gdc` przyjmuje `extern func`
  w zwykłym pliku skryptów ([ADR 0010](../../decisions/0010-nowe-funkcje-zewnetrzne-silnika.md)).
  Nazwy `AI_PracticeMove`, `AI_ReadyFist`, `TA_Practice_Melee`, `TA_Practice_Fist`
  i `ZS_Practice_Melee` nie występują w skryptach gry ani w funkcjach wbudowanych `gdc`.
- Wolne `aivar`: skrypty używają indeksów do 88 (`AI/AI_Intern/AI_Constants.d:339`), a silnik
  sięga tylko po `aivar[88]` (`npc.cpp:4058`).

**Dziennik walki i scenariusze**

- `FightLog::attack` (`common/game/fightlog.cpp:186`) zapisuje cios z polem `src` (`player`, `queue`,
  `continue`), połączeniem (`link`) i serią FAI. `FightLog::miss` zapisuje pudło z przyczyną.
  Zdarzenia `state` są dziś tylko dla śmierci, nieprzytomności i zachwiania (`npc.cpp:607`, `:2287`).
- Miary raportu liczy `gothic25/tools/fightlog.py`, a opisuje `gothic25/tests/README.md:311-367`.
  Pola dziennika można dopisywać bez ponownego porównania z obserwacją (`tests/README.md:9-11`,
  ADR 0004).
- Postacie testowe w skryptach moda mają precedens: `TST_ComboDummy`
  (`.../AI/AI_INTERN/ComboDamageTest.d`).

## Projekt

### Silnik (C++)

**E1. `AI_ReadyFist(npc)`** (`gamescript.cpp`, `constants.h`, `npc.cpp` `nextAiAction`)

- Nowa czynność `AI_DrawWeaponFist`, dopisana na końcu wyliczenia, żeby nie przesunąć numerów
  zapisanych w kolejce.
- Działa jak `AI_DrawWeaponMelee`, ale woła `drawWeaponFist`. Gdy NPC ma dobytą broń, `drawWeaponFist`
  najpierw ją chowa i zwraca `false`, więc czynność wraca na początek kolejki aż do skutku.
- Założona broń zostaje założona, więc po treningu walka i ekwipunek działają jak dotąd.

**E2. `AI_PracticeMove(npc, move)`** (`gamescript.cpp`, `constants.h`, `npc.cpp`, `npc.h`)

Nowa czynność `AI_PracticeMove` z parametrem `move` (`i0`): 0 cios do przodu, 1 z lewej, 2 z prawej,
3 blok, 4 odskok. Stałe dla skryptów są w pliku treningu.

1. **Warunki.** Działa tylko w trybie pięści, 1H albo 2H. W innym trybie i przy nieznanym `move`
   czynność przepada. NPC ćwiczy bez celu: czynność czyści `currentTarget`, co chroni też przed
   obrażeniami po wczytaniu zapisu („Zapisy gry”).
2. **Cios (0-2) bez trwającego ciosu:** `doAttack` z kierunkiem. Pięściami z boku, gdy
   `hasFistSideAttack`, a inaczej cios do przodu, tak jak w walce.
3. **Cios w trakcie trwającego ciosu** (`comboInfo`):
   - przed oknem combo czynność wraca na początek kolejki i czeka;
   - w oknie cios do przodu na ostatnim etapie combo przepada, a dziennik dostaje przerwanie
     `talent`, jak w `implComboLink`. Pozostałe ciosy idą przez `doAttack`, który łączy je w oknie
     (`continueCombo`);
   - po oknie czynność czeka do końca ciosu i zaczyna od postawy.
4. **Czekanie po ciosie.** Gdy następna czynność w kolejce to cios treningowy, silnik czeka do chwili
   połączenia: losowo od 25% do 75% użytecznej części okna, liczonej jak w 001 E3 (od początku okna do
   `min(koniec okna, DEF_HIT_END) - 50 ms`). Inaczej czeka do końca ciosu (`atkTotalTime`), żeby
   `AI_Wait` albo `AI_GotoWP` nie weszły w trwający cios.
5. **Blok i odskok (3, 4)** startują tylko z postawy. W trakcie ciosu czynność czeka na jego koniec.
   Blok to `blockFist` albo `blockSword`, a odskok `setAnim(MoveBack)`. Silnik czeka do końca
   animacji.
6. **Bez obrażeń.** `doAttack` dostaje znacznik „trening” zapamiętany w `Npc` (pole bez zapisu).
   Każde inne wywołanie `doAttack` go kasuje. `commitDamage` przy znaczniku nie woła `takeDamage`,
   tylko zapisuje pudło z przyczyną `practice`. Bez `takeDamage` nie ma też percepcji walki (W6).

Bez wywołań nowych funkcji silnik zachowuje się jak dotąd: oryginalne skrypty ich nie znają
(ADR 0010).

**E3. Dziennik walki** (`fightlog.*`, `npc.cpp`)

- `attack` dla ciosu treningowego ma `src` `practice`.
- Nowe zdarzenie `practice` dla każdego ruchu treningowego (5 rodzajów), z polami:
  - `move`: `fwd`, `left`, `right`, `block`, `jumpback`;
  - `link`: dla ciosów jak w `attack`, a `dropped`, gdy cios przepadł przez limit talentu;
  - `pseries`: numer serii treningowej, nowy przy każdym ruchu z postawy;
  - `end_ms`: przewidywany koniec ruchu, potrzebny do liczenia przerw;
  - `wp_dist`: odległość od waypointu planu dnia NPC w cm;
  - `wp_angle`: różnica kierunku NPC i waypointu w stopniach.
- Nowe zdarzenie `ai`: postać, która jest już w dzienniku, zaczyna stan AI (`startState`, nazwa
  stanu). Służy K7 i K8, a przydaje się też przy innych testach.
- Bez zmiany znaczenia istniejących pól, więc bez ponownego porównania z 003 K3.

### Skrypty (Daedalus)

Nowe pliki na końcu `Content/Gothic.src` (ADR 0005), w cp1250. Zmiany sprawdza `tools/dat.py prefix`.

Nazwy plików nie mogą pasować do wzorców z `Gothic.src`, np. `AI\HUMAN\TA_Human\ZS*.d` (linia 225),
bo wzorzec wciągnąłby plik w środek kompilacji. Stąd `Practice_Melee.d`, a nie `ZS_Practice_Melee.d`
(poprawka przy Z1).

**`AI/Human/TA_Human/Practice_Melee.d`** (treść):

- Deklaracje `extern func` z E1 i E2 (ADR 0010), stałe `PRACTICE_FRONT`, `PRACTICE_LEFT`,
  `PRACTICE_RIGHT`, `PRACTICE_BLOCK`, `PRACTICE_JUMPBACK` oraz `AIV_PracticeProfile = 90`.
- **Ustawienia (W4):** zmienne skryptu i `B_PracticeMelee_Settings()`, wołana przed każdą serią
  dla `self`. Ustawia wartości domyślne, a potem nadpisuje je według profilu
  `self.aivar[AIV_PracticeProfile]`. Treść moda dodaje profile, a NPC wybiera profil w swojej
  instancji. Zmienne:
  - wagi rodzajów serii: prosty, combo do przodu, lewy, prawy, mieszana;
  - najdłuższa seria mieszana i najdłuższe zlecane combo (4, a krótsze przytnie talent);
  - co ile serii blok albo odskok (wartość startowa 3-7, średnio 5);
  - przerwy dla trzech poziomów talentu, co ile serii odpoczynek (4-8) i jego długość (6-10 s), według
    tabeli z W3.

  Profil 0 to wartości z W2 i W3. Profil 99 to profil testowy K4: tylko ciosy z lewej i stała
  przerwa 2 s, z komentarzem, że nie używa go żaden NPC świata.
- **Plany dnia:** `TA_Practice_Melee` i `TA_Practice_Fist`, w stylu `TA.d` (`TA_Min`), dla
  `ZS_Practice_Melee` i `ZS_Practice_Fist`. Wariant wybiera autor planu dnia (W1). Oba stany
  korzystają ze wspólnych funkcji `B_PracticeMelee_*` z parametrem „pięści”.
- **Start stanu:** jak w `ZS_Practice_Sword`: `Perception_Set_Normal`, `B_ResetAll`, chód, powrót na
  waypoint. NPC nie dostaje broni (W1). Na koniec losowe `AI_WaitMs` 0-2 s, żeby NPC zaczynający
  razem nie ćwiczyli w jednym rytmie (W3).
- **Pętla, jedna seria na przebieg:**
  1. Przy pierwszym przebiegu NPC dobywa broni. W wariancie bronią woła `AI_ReadyMeleeWeapon`, co bez
     broni daje pięści. W wariancie pięściami woła `AI_ReadyFist`.
  2. `B_PracticeMelee_Settings()` i poziom talentu: `Npc_GetTalentSkill` dla 1H albo 2H według
     broni z `Npc_GetEquippedMeleeWeapon`. Pięści mają poziom wojownika (W3).
  3. Gdy licznik serii dojdzie do progu, NPC robi blok albo odskok (`AI_PracticeMove`, po połowie).
  4. Losowanie rodzaju serii według wag i dopisanie jej ruchów: kolejne `AI_PracticeMove`.
  5. Przerwa `AI_WaitMs` z zakresu poziomu talentu albo, co wylosowaną liczbę serii, odpoczynek.
  6. Gdy NPC odszedł od waypointu, `AI_GotoWP`, a potem zawsze `AI_AlignToWP` (W5).
- **Koniec stanu:** `AI_RemoveWeapon`. Kolejkę czyści już silnik (`startState`), więc trening nie
  przechodzi do następnego punktu planu dnia (W8).
- Reakcje (W7) dają te same percepcje co w `ZS_Practice_Sword` (`Perception_Set_Normal`).

**`AI/Human/TA_Human/Practice_MeleeTest.d`** (dane testowe, po pliku treningu):

- Postacie testowe (id od 9910) z planami dnia na waypointach placu koszar
  (`NW_CITY_HABOUR_KASERN_*`, dokładne nazwy w zadaniu):
  - mistrz 1H (K1, K5, K6, K10);
  - nowicjusz 2H i mistrz 2H obok siebie (K2);
  - 1H w wariancie pięściami i NPC bez broni w wariancie bronią (K3);
  - profil 99 (K4);
  - zmiana pory: trening 8:00-9:00, potem stanie na innym waypoincie (K8).
- `Rtn_TST_PRACTICE_329` i funkcja `TST_PracticeMilitia()` dla `call`: strażnik `MIL_329_Miliz`
  ćwiczy nowym treningiem na swoim waypoincie (K7, ma dialogi gry).

**README skryptów:** w „Symbolach dla silnika” tabela funkcji zewnętrznych (ADR 0010), a do tego
opis planów dnia i ustawień treningu.

### Narzędzia i testy

- `tools/fightlog.py`: miary `practice.*` (opis w `tests/README.md`):
  - liczby ruchów według rodzaju i serie według rodzaju (prosty, combo, lewy, prawy, mieszana);
  - stosunek serii do bloków i odskoków oraz do odpoczynków;
  - przerwy: minimum, maksimum i mediana, osobno zwykłe przerwy i odpoczynki (próg 5 s);
  - najkrótszy okres ciągu rodzajów serii;
  - największe `wp_dist` i `wp_angle` na początku serii;
  - odsetek ciosów, które startują w odstępie do 200 ms od ciosu innej postaci (K2);
  - najdłuższy czas ruchu treningowego po zdarzeniu `ai` kończącym trening (K8).
- `tests/005/`: scenariusze K01-K11 (K07 w `reczne/`, a K02 ma też wersję ręczną). Każdy scenariusz
  z treningiem ma `expect nolog not implemented call` (ADR 0010).

### Zasoby

Brak. Trening używa animacji z gry i sierpowych z 004.

### Zapisy gry

- Nie ma nowych pól ani wersji zapisu.
- Nowe czynności kolejki zapisuje dotychczasowy format (`aiqueue.cpp:9-17`).
- Znacznik treningu z E2 nie trafia do zapisu. Po wczytaniu zapisu z ciosem treningowym w trakcie
  klatka trafienia działa jak dziś. NPC nie ma jednak celu, bo wyczyściła go czynność treningu, więc
  cios kończy się pudłem `no_target` (K10).
- Nowe symbole skryptów są w nowych plikach na końcu, więc nazwane symbole poprzedniej wersji zachowują
  numery (`dat.py prefix`, K10).

## Pokrycie wymagań

| Wymaganie | Gdzie realizowane |
|---|---|
| W1 | Skrypty: `TA_Practice_Melee`, `TA_Practice_Fist`, start stanu. E1 (`AI_ReadyFist`) |
| W2 | E2 (ciosy, combo przez `continueCombo`, limit talentu, blok, odskok). Skrypty: rodzaje serii i przerywniki |
| W3 | Skrypty: losowanie serii, przerwy według talentu, odpoczynki, losowe opóźnienie startu |
| W4 | Skrypty: `B_PracticeMelee_Settings` i profile `AIV_PracticeProfile` |
| W5 | Skrypty: powrót i ustawienie na waypoincie po serii. E3: `wp_dist`, `wp_angle` |
| W6 | E2: znacznik treningu w `commitDamage`, czyszczenie celu, brak `takeDamage`, więc brak percepcji |
| W7 | Skrypty: `Perception_Set_Normal` i `B_ResetAll` jak w `ZS_Practice_Sword`. E3: zdarzenie `ai` |
| W8 | Silnik: `startState` czyści kolejkę (istniejące). Skrypty: `AI_RemoveWeapon` na końcu stanu |
| W9 | E3: `src` `practice`, zdarzenia `practice` i `ai`. Miary `practice.*` w `fightlog.py` |
| W10 | ADR 0010: nowe funkcje działają tylko po wywołaniu, a oryginalne skrypty ich nie znają. Świat bez zmian (P3) |
| W11 | Brak nowego stanu w zapisie, format kolejki bez zmian, nowe symbole na końcu (ADR 0005) |

## Bramka konstytucji

- [x] 1. **Tylko OpenGothic, warstwa najtańsza.** Treść w skryptach, a w silniku tylko to, czego
  skrypty nie zrobią: combo bez celu, ciosy bez obrażeń, dobycie pięści i dziennik.
- [x] 2. **Mechanizmy w silniku, treść w skryptach.** Silnik wykonuje pojedynczy ruch. O kolejności,
  przerwach, proporcjach, profilach i o tym, kto ćwiczy, decydują skrypty.
- [x] 3. **Fork łatwy do aktualizacji.** Dwie nowe czynności kolejki i znacznik w `commitDamage`,
  w stylu repozytorium. Działają tylko po wywołaniu nowych funkcji, których oryginalne skrypty nie
  znają (ADR 0010), więc bez moda silnik działa jak upstream (K9). Treść moda jest tylko
  w `gothic25/`.
- [x] 4. **Zapisy.** Bez nowego stanu i bez zmiany formatu („Zapisy gry”). Zapis z poprzedniej
  wersji moda sprawdza K10.
- [x] 5. **Kryteria sprawdzalne w grze.** K1-K6 i K8-K11 to scenariusze automatyczne. K7 i wizualna
  część K2 to scenariusze ręczne.
- [x] 6. **Prawa do zasobów.** Brak nowych zasobów.
- [x] 7. **Język.** Plan, ADR i README po polsku. Kod, komentarze i commity po angielsku.
- [x] 8. **Wersja.** MINOR: nowa funkcja, zapisy zgodne. Na starszym silniku mod działa, ale postać
  z nowym treningiem stoi z dobytą bronią (wywołania są ignorowane z linią w logu). W świecie żaden
  NPC nie ma nowego treningu (P3), więc gracz tego nie zobaczy.
- [x] 9. **GothicMOD.** Nowe skrypty to opracowanie na licencji GothicMOD. Bez opłat.
- [x] 10. **Automatyzacja.** Build i scenariusze bez zmian w narzędziach poza nowymi miarami
  `fightlog.py`. Ręczne zostają K7 (rozmowa z NPC wymaga gracza) i ocena wyglądu w K2.

## Odstępstwa od konstytucji

Brak. Nowe funkcje bez symbolu-przełącznika z ADR 0003 opisuje ADR 0010.

## Ryzyka

- **R1: łączenie ciosów przez kolejkę AI.** Następny ruch rusza z opóźnieniem jednej klatki po
  chwili połączenia, a przy przyspieszonym czasie (`ztimer`) klatki są dłuższe. Jeśli trafi za okno,
  combo zacznie się od nowa. Wykrycie: K1 (długości combo, `link`). W razie potrzeby losujemy chwilę
  połączenia bliżej początku okna.
- **R2: ruch z animacji odsuwa NPC od miejsca.** Combo 1H mistrza i odskok mogą przekroczyć 1,5 m
  przed powrotem po serii. Wykrycie: K5 (`wp_dist`). Wtedy skracamy serie albo dodajemy powrót po
  odskoku.
- **R3: pierwsza nowa funkcja zewnętrzna.** Rejestracja w ZenKit sprawdza zgodność typów
  parametrów z deklaracją w `.DAT`. Sprawdzamy to w pierwszym zadaniu, na małym scenariuszu z
  `expect nolog not implemented call`.
- **R4: dobyte pięści przy założonej broni** mogą wyglądać nienaturalnie, np. broń zniknie z pasa,
  albo zmieszać stan broni przy przejściu do walki. Wykrycie: K3 (zrzut) i K7 (atak na
  ćwiczącego pięściami).
- **R5: czyszczenie celu** zmienia wynik `Npc_GetTarget` dla ćwiczącego. Skrypty treningu go nie
  używają, a percepcje ustawiają cel na nowo przy zagrożeniu. Wykrycie: K7.
- **R6: dziennik przy wielu postaciach.** Zdarzenie `ai` dla każdej postaci z dziennika zwiększy
  plik przy długich walkach grupowych. Ograniczenie: tylko postacie, które już są w dzienniku.
  Regresja: zestawy 001 i 004 (K9).

## Alternatywy odrzucone

- **Same skrypty z `AI_PlayAni`.** Brak combo, ryzyko obrażeń zadanych celowi NPC i brak wpisów
  w dzienniku („Warstwa”).
- **AI walki z celem** (manekin, niewidzialny przeciwnik, partner). Wymaga celu i zasięgów,
  a z partnerem wywołuje reakcje świadków. To sparing z `roadmap.md`.
- **Logika treningu w silniku** (losowanie serii i przerw w C++). Łamie zasadę 2, a autor moda nie
  mógłby jej zmieniać.
- **Zdjęcie broni na czas treningu pięściami** (`AI_UnequipWeapons`). Zmienia ekwipunek. Przy
  napadzie w trakcie treningu NPC walczyłby pięściami, a broń trzeba by zakładać od nowa.
- **Zapis znacznika treningu w zapisie gry.** Wymagałby nowej wersji zapisu. Czyszczenie celu daje
  ten sam efekt bez zmiany formatu.
- **Własny plik funkcji wbudowanych dla `gdc`.** Zob. ADR 0010, opcja 2.
