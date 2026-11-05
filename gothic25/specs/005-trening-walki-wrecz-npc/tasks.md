# Zadania 005: Trening walki wręcz NPC

- **Plan:** [plan.md](plan.md)
- **Utworzono:** 2026-11-05

Każde zadanie mieści się w jednym commicie. `[P]` oznacza zadanie, które można robić równolegle
z innymi `[P]` w tej samej fazie. W nawiasie: wymagania (W) i kryteria (K), które zadanie realizuje.

**Zasady dla wszystkich zadań:**

- Plan nie zmienia serializacji (plan, „Zapisy gry”), więc nie ma dla niej zadania. Każda nowa
  funkcja zewnętrzna ma osobne zadanie (Z1, Z2), według [ADR 0010](../../decisions/0010-nowe-funkcje-zewnetrzne-silnika.md).
- Silnik budujemy przez `tools/build-engine.ps1`, a skrypty przez `tools/build-scripts.ps1`.
- Po każdej zmianie skryptów uruchamiamy `tools/dat.py prefix` względem `GOTHIC.DAT` skompilowanego
  z commitu sprzed 005 (`02ddcb93`).
- W każdym zadaniu uruchamiamy tylko scenariusze, które dotykają zmiany. Pełne zestawy regresji
  (`-Spec 001`, `-Spec 004`) idą raz, w Z11. Wynik zadania podaje, które scenariusze poszły i dlaczego
  wystarczą.
- Scenariusze robocze trafiają do `tests/dev/005-*.txt`. Scenariusze kryteriów powstają w Z9 i Z10.
- Postacie i funkcje pomocnicze dla scenariuszy są w nowym pliku testowym
  `Content/AI/Human/TA_Human/ZS_Practice_MeleeTest.d`. Ten plik stoi w `Gothic.src` po pliku treningu.

## Faza 1: Silnik, funkcje zewnętrzne i trening bez obrażeń

- [ ] **Z1** Funkcja zewnętrzna `AI_ReadyFist` (plan E1).
      - Silnik:
        - `common/game/constants.h`: `AI_DrawWeaponFist` na końcu wyliczenia `Action`;
        - `common/world/aiqueue.*`: `AiQueue::aiDrawWeaponFist()`;
        - `common/game/gamescript.*`: `ai_readyfist` i `bindExternal("ai_readyfist", ...)`;
        - `common/world/objects/npc.cpp` `nextAiAction`: jak `AI_DrawWeaponMelee`, ale z
          `drawWeaponFist`; wraca na początek kolejki, dopóki broń się chowa.
      - Skrypty, nowe pliki na końcu `Content/Gothic.src`:
        - `AI/Human/TA_Human/ZS_Practice_Melee.d`: nagłówek pliku i `extern func void AI_ReadyFist(var instance par0);`;
        - plik testowy z `TST_ReadyFist(npc)` i `TST_IsFistMode(npc)`, która zwraca
          `Npc_IsInFightMode(npc, FMODE_FIST)` do `call`.
      - Sprawdzenie (pierwsza nowa funkcja, ryzyko R3): scenariusz roboczy. `insert Pal_230_Ritter`
        (ma miecz), `call TST_ReadyFist`, odczekanie, `call TST_IsFistMode` daje 1 i zrzut ekranu
        z pięściami. Do tego `expect nolog not implemented call` i `dat.py prefix` z kodem 0.

      (W1, W10)
- [ ] **Z2** Funkcja zewnętrzna `AI_PracticeMove` (plan E2, pkt 1-5).
      - Silnik:
        - `constants.h`: `AI_PracticeMove` na końcu wyliczenia;
        - `aiqueue.*`: `aiPracticeMove(move)`;
        - `gamescript.*`: `ai_practicemove` i `bindExternal`;
        - `npc.h` / `npc.cpp`: wykonanie w `nextAiAction`. Ciosy z postawy i łączone w oknie przez
          `doAttack`. Cios do przodu na ostatnim etapie przepada i trafia do dziennika jako przerwanie
          `talent`. Sierpowe przez `hasFistSideAttack`. Czekanie do chwili połączenia (25-75%
          użytecznej części okna), gdy następna czynność to cios treningowy, a inaczej do końca ciosu.
          Blok i odskok tylko z postawy.
      - Skrypty:
        - w `ZS_Practice_Melee.d` deklaracja `extern func void AI_PracticeMove(var instance par0, var int par1);`
          oraz stałe `PRACTICE_FRONT` (0), `PRACTICE_LEFT`, `PRACTICE_RIGHT`, `PRACTICE_BLOCK`,
          `PRACTICE_JUMPBACK` (4);
        - w pliku testowym `TST_PracticeMove(npc, move)` oraz `TST_Arm(npc, broń, procent)`. Ta druga
          daje wstawionej postaci miecz 1H albo 2H i talent przez `B_SetFightSkills`.
      - Sprawdzenie: scenariusze robocze z `TST_ComboDummy`, który ma wyłączone percepcje i stoi
        w miejscu. Cztery kolejne ciosy do przodu:
        - mistrz 1H: `combo.max == 4`;
        - nowicjusz 2H: `combo.max == 2` i przerwanie `talent`;
        - pięści: lewy i prawy dają `attacks.dir.left` i `attacks.dir.right`;
        - blok i odskok grają animację; zrzut ekranu.

      (W2)
- [ ] **Z3** Trening bez obrażeń (plan E2, pkt 1 i 6).
      - `npc.h` / `npc.cpp`:
        - znacznik treningu w `Npc` (bez zapisu), ustawiany przez `doAttack` z czynności treningowej
          i kasowany przez każde inne `doAttack`;
        - `commitDamage` przy znaczniku zapisuje pudło `practice` i nie woła `takeDamage`;
        - `AI_PracticeMove` czyści cel NPC.
      - Plik testowy: `TST_SetTarget(npc, cel)` udaje cel, który został po walce.
      - Sprawdzenie: scenariusz roboczy. Uzbrojony manekin ma cel ustawiony na bohatera. Bohater bez
        nieśmiertelności stoi pół metra przed nim, a manekin wykonuje serię ciosów treningowych.
        Oczekiwania: `expect hero taken.hit == 0`, `res.miss.practice > 0`, `res.hit == 0`.

      (W6)

## Faza 2: Dziennik walki, treść treningu i dane testowe

Z5 wymaga formatu z Z4, a Z7 skryptów z Z6. Z5, Z6 i Z8 nie zależą od siebie.

- [ ] **Z4** Dziennik walki dla treningu (plan E3).
      - `common/game/fightlog.*`:
        - `src` `practice` w `attack`;
        - nowe zdarzenie `practice` z polami `move`, `link` (z `dropped`), `pseries`, `end_ms`,
          `wp_dist` i `wp_angle`. Waypoint pochodzi z planu dnia NPC (`wp`); bez waypointu oba pola
          to `null`;
        - nowe zdarzenie `ai`, wołane z `Npc::startState` tylko dla postaci, które już są
          w dzienniku.
      - `tests/README.md`: opis nowych zdarzeń i pól w „Dzienniku walki”.
      - Sprawdzenie: scenariusze robocze z Z2 i Z3 mają zdarzenia `practice` z pełnymi polami, a cios
        przepadły przez talent ma `link` `dropped`. Obecne miary dają te same wartości co przed zmianą.

      (W5, W7, W9)
- [ ] **Z5** [P] Miary treningu w `tools/fightlog.py` (plan, „Narzędzia i testy”).
      - Miary `practice.*`:
        - ruchy i serie według rodzaju;
        - stosunek serii do bloków i odskoków oraz do odpoczynków;
        - przerwy: minimum, maksimum i mediana, osobno zwykłe i odpoczynki;
        - najkrótszy okres ciągu rodzajów serii;
        - największe `wp_dist` i `wp_angle` na początku serii;
        - odsetek ciosów zsynchronizowanych z inną postacią;
        - czas ruchów po końcu treningu (zdarzenie `ai`).
      - Opis miar w tabeli „Oczekiwania” w `tests/README.md`.
      - Sprawdzenie: raport z dzienników Z4 i ręcznie przeliczone wartości dla jednego przebiegu.

      (W9)
- [ ] **Z6** [P] Skrypty treningu w `ZS_Practice_Melee.d` (plan, „Skrypty”).
      - `AIV_PracticeProfile = 90`, zmienne ustawień i `B_PracticeMelee_Settings()`: profil 0 według
        W2 i W3, profil 99 testowy (tylko ciosy z lewej, przerwa 2 s).
      - `TA_Practice_Melee`, `TA_Practice_Fist`, `ZS_Practice_Melee` i `ZS_Practice_Fist` (start, pętla,
        koniec) na wspólnych `B_PracticeMelee_*`:
        - dobycie broni albo pięści;
        - poziom talentu z broni, a pięści na poziomie wojownika;
        - bloki i odskoki według licznika;
        - losowanie serii;
        - przerwa albo odpoczynek;
        - powrót i ustawienie na waypoincie;
        - losowe opóźnienie startu;
        - `AI_RemoveWeapon` na końcu.
      - Plik testowy: `TST_StartPractice(npc, pięści)` startuje stan treningu bez planu dnia.
      - Sprawdzenie: scenariusz roboczy, 3 minuty treningu uzbrojonego manekina. Dziennik ma serie
        wszystkich rodzajów, przerwy, bloki i odskoki, a `wp_dist` jest małe. `dat.py prefix` daje 0.

      (W1, W2, W3, W4, W5, W7, W8, W11)
- [ ] **Z7** Dane testowe treningu w pliku testowym (plan, „Skrypty”).
      - Postacie testowe od id 9910, gildia `GIL_MIL`, z planami dnia na waypointach placu koszar
        (`NW_CITY_HABOUR_KASERN_CENTRE_01` do `_04`):
        - mistrz 1H;
        - nowicjusz 2H i mistrz 2H na sąsiednich waypointach;
        - 1H w wariancie pięściami;
        - postać bez broni w wariancie bronią;
        - profil 99;
        - zmiana pory: trening 8:00-9:00, potem `TA_Stand_ArmsCrossed` na innym waypoincie.
      - `Rtn_TST_PRACTICE_329` i `TST_PracticeMilitia()`: `MIL_329_Miliz` ćwiczy nowym treningiem na
        `NW_CITY_HABOUR_KASERN_CENTRE_02`.
      - Strażnicy 330 i 331 ćwiczą na `_03` i `_04` od 7:00. Scenariusze usuwają ich przez
        `call B_RemoveNpc`, tak jak w 001.
      - Sprawdzenie: scenariusz roboczy wstawia każdą postać. Każda dochodzi na swój waypoint i ćwiczy,
        co widać w dzienniku i na zrzucie.

      (W1, K1-K8, K10)
- [ ] **Z8** [P] Dokumentacja skryptów i changelog.
      - `content/Scripts/README.md`, sekcja „Symbole dla silnika”: tabela funkcji zewnętrznych
        (`AI_ReadyFist`, `AI_PracticeMove`, ADR 0010), plany dnia treningu, ustawienia i profile,
        `AIV_PracticeProfile`.
      - `CHANGELOG.md` `[Unreleased]`: trening walki wręcz NPC i nowe funkcje silnika. Na starszym
        silniku wywołania są ignorowane.

      (W4, W10)

## Faza 3: Scenariusze kryteriów

- [ ] **Z9** Scenariusze `tests/005` K01-K06.
      - `K01-mistrz-1h`, `K02-talent-2h` i `reczne/K02-talent-2h`, `K03a-piesci-z-bronia`,
        `K03b-bez-broni`, `K03c-bronia`, `K04-profil-testowy`, `K06-bez-obrazen`. Każdy ma
        `expect nolog not implemented call`.
      - K05 nie ma osobnego scenariusza: jego oczekiwania (`wp_dist`, `wp_angle`) siedzą w K01-K03,
        z nagłówkiem `criterion: 005 K5`.
      - Progi oczekiwań według kryteriów ze spec.md. Gdy próg trzeba poprawić, robimy to osobnym
        commitem z uzasadnieniem w scenariuszu (ADR 0004).
      - Sprawdzenie: każdy scenariusz uruchomiony pojedynczo (`-Scenario`).

      (K1, K2, K3, K4, K5, K6)
- [ ] **Z10** Scenariusze `tests/005` K07-K11.
      - `reczne/K07-rozmowa`: strażnik 329 przez `TST_PracticeMilitia()`, opis w komentarzu
        scenariusza.
      - `K08-koniec-pory`: `set time 8 58`, potem `wait`.
      - `K09-bez-moda`: `# mod: off`, strażnik 329 w porze treningu, zrzuty.
      - `K10a-zapis-w-serii`, `K10b-wczytanie`, `K10c-zapis-z-0.1.0`
        (`build/testsaves/001-K9-v0.1.0-pal230.sav`).
      - `K11-swiat-bez-zmian`: strażnik 329 ze swoim planem dnia, a dziennik bez ruchów treningowych.
      - Sprawdzenie: każdy scenariusz uruchomiony pojedynczo.

      (K7, K8, K9, K10, K11)

## Faza 4: Weryfikacja

- [ ] **Z11** Przejść kroki kryteriów akceptacji i uzupełnić sekcję „Weryfikacja” w spec.md (K1-K11).
      - `tools/test.ps1 -Spec 005` na czystym drzewie.
      - Regresja `-Spec 001` i `-Spec 004` (K9).
      - `dat.py prefix` względem `02ddcb93`.
      - Sesje ręczne z właścicielem: `reczne/K02` (wygląd i rytm) i `reczne/K07` (rozmowa i reakcje).
      - Wpisy według ADR 0004: scenariusz, commit, kto uruchomił i liczby z raportu.

      (K1-K11)
