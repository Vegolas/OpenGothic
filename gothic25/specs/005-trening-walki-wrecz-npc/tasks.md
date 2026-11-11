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
  `Content/AI/Human/TA_Human/Practice_MeleeTest.d`. Ten plik stoi w `Gothic.src` po pliku treningu.

## Faza 1: Silnik, funkcje zewnętrzne i trening bez obrażeń

- [x] **Z1** Funkcja zewnętrzna `AI_ReadyFist` (plan E1).
      - Silnik:
        - `common/game/constants.h`: `AI_DrawWeaponFist` na końcu wyliczenia `Action`;
        - `common/world/aiqueue.*`: `AiQueue::aiReadyFist()`;
        - `common/game/gamescript.*`: `ai_readyfist` i `bindExternal("ai_readyfist", ...)`;
        - `common/world/objects/npc.cpp` `nextAiAction`: jak `AI_DrawWeaponMelee`, ale z
          `drawWeaponFist`; wraca na początek kolejki, dopóki broń się chowa.
      - Skrypty, nowe pliki na końcu `Content/Gothic.src`:
        - `AI/Human/TA_Human/Practice_Melee.d`: nagłówek pliku i `extern func void AI_ReadyFist(var instance par0);`;
        - plik testowy z `TST_ReadyFist(npc)` i `TST_IsFistMode(npc)`, która zwraca
          `Npc_IsInFightMode(npc, FMODE_FIST)` do `call`.
      - Sprawdzenie (pierwsza nowa funkcja, ryzyko R3): scenariusz roboczy. `insert Pal_230_Ritter`
        (ma miecz), `call TST_ReadyFist`, odczekanie, `call TST_IsFistMode` daje 1 i zrzut ekranu
        z pięściami. Do tego `expect nolog not implemented call` i `dat.py prefix` z kodem 0.
      - Wynik (2026-11-05):
        - Nazwy plików zmienione z `ZS_Practice_Melee*.d` na `Practice_Melee*.d`, bo wzorzec
          `AI\HUMAN\TA_Human\ZS*.d` z `Gothic.src:225` wciągnąłby je w środek kompilacji (plan
          poprawiony).
        - Pal_230 ma własny plan dnia, który odprowadziłby go do miasta. Scenariusz
          `tests/dev/005-z1-readyfist` używa więc `TST_ComboDummy` uzbrojonego przez `TST_Arm`
          (przeniesione tu z Z2), z `TST_ReadyMelee` i `TST_IsMeleeMode`.
        - Przebieg `20261105-222445-dev-005-z1-readyfist` zaliczony, 4 z 4 oczekiwań:
          - po `AI_ReadyMeleeWeapon` tryb broni 1;
          - po `AI_ReadyFist` tryb pięści 1, a tryb broni 0 (dobyty miecz najpierw schowany);
          - brak „not implemented call [AI_READYFIST]”. Nazwy w tej linii logu są nazwami
            symboli, czyli wielkimi literami.
        - Zrzuty niczego nie rozstrzygają, bo manekina zasłania bohater. Rozstrzyga wynik `call`.
        - `dat.py prefix`: kod 0, doszło 16 nazwanych symboli na końcu.

      (W1, W10)
- [x] **Z2** Funkcja zewnętrzna `AI_PracticeMove` (plan E2, pkt 1-5).
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
        - w `Practice_Melee.d` deklaracja `extern func void AI_PracticeMove(var instance par0, var int par1);`
          oraz stałe `PRACTICE_FRONT` (0), `PRACTICE_LEFT`, `PRACTICE_RIGHT`, `PRACTICE_BLOCK`,
          `PRACTICE_JUMPBACK` (4);
        - w pliku testowym `TST_PracticeMove(npc, move)`. `TST_Arm(npc, broń, procent)` jest już
          z Z1.
      - Sprawdzenie: scenariusze robocze z `TST_ComboDummy`, który ma wyłączone percepcje i stoi
        w miejscu. Cztery kolejne ciosy do przodu:
        - mistrz 1H: `combo.max == 4`;
        - nowicjusz 2H: `combo.max == 2` i przerwanie `talent`;
        - pięści: lewy i prawy dają `attacks.dir.left` i `attacks.dir.right`;
        - blok i odskok grają animację; zrzut ekranu.
      - Wynik (2026-11-05):
        - Limit talentu: cios do przodu przepada, gdy trwa ostatni etap combo. Gdy ostatni etap
          nie ma okna, a następna czynność to cios treningowy, silnik od razu oddaje ją do kolejki,
          bez czekania do końca etapu. Inaczej cios trafiłby na koniec etapu i zaczął nowe combo,
          zamiast trafić na limit.
        - Pomocnicze `AiQueue::front()` i wyliczenie `Npc::PracticeMove`, czyli wartości `move` dla
          skryptów.
        - Scenariusze `tests/dev/005-z2-*`, zaliczone za pierwszym razem:
          - `mistrz-1h`, przebieg `20261105-223353`, 8 z 8: combo 4 (etapy połączone w 28-43% okna),
            potem lewy (`new`), prawy (`side`) i cios do przodu (`side`), a po bloku i odskoku jeszcze
            jeden cios. Kolejka się nie zablokowała;
          - `nowicjusz-2h`, przebieg `20261105-223438`, 6 z 6: combo 2 i dwa przerwania `talent`
            9-17 ms po drugim ciosie, potem lewy i prawy (`side`);
          - `piesci`, przebieg `20261105-223517`, 7 z 7: combo 2, przerwanie `talent`, sierpowe
            lewy i prawy, cios do przodu po prawym (`side`). Na zrzutach blok z rękami w górze
            i manekin odsunięty odskokiem.
        - Ciosy treningowe mają w dzienniku jeszcze `src` `continue` i serię `combo`. Oznaczenie
          `practice` dochodzi w Z4.
        - `dat.py prefix`: kod 0, 27 nazwanych symboli na końcu.

      (W2)
- [x] **Z3** Trening bez obrażeń (plan E2, pkt 1 i 6).
      - `npc.h` / `npc.cpp`:
        - znacznik treningu w `Npc` (bez zapisu), ustawiany przez `doAttack` z czynności treningowej
          i kasowany przez każde inne `doAttack`;
        - `commitDamage` przy znaczniku zapisuje pudło `practice` i nie woła `takeDamage`;
        - `AI_PracticeMove` czyści cel NPC.
      - Plik testowy: `TST_SetTarget(npc, cel)` udaje cel, który został po walce.
      - Sprawdzenie: scenariusz roboczy. Uzbrojony manekin ma cel ustawiony na bohatera. Bohater bez
        nieśmiertelności stoi pół metra przed nim, a manekin wykonuje serię ciosów treningowych.
        Oczekiwania: `expect hero taken.hit == 0`, `res.miss.practice > 0`, `res.hit == 0`.
      - Wynik (2026-11-05):
        - Znacznik `Npc::practiceHit` ustawia udane `doAttack(..., practice)`, a kasuje każde inne
          `doAttack` i jego użycie w `commitDamage`. Dzięki temu animacja ataku zagrana później przez
          `AI_PlayAni` nie straci obrażeń. Znacznik trafia do sprawdzenia przed testem celu, więc trening
          nie rani nawet NPC w zasięgu.
        - `expect hero taken.hit` odpada: bohatera, który nic nie robi, nie ma w dzienniku, a takie
          oczekiwanie jest niezaliczone. Zamiast tego `TST_HpLost hero` zwraca 0. Do tego
          `TST_HasTarget` przed treningiem (1) i po nim (0) oraz `TST_HpLost` w pliku testowym.
        - `tests/dev/005-z3-bez-obrazen`, przebieg `20261105-223944`, 6 z 6: 6 ciosów, 6 pudeł
          `practice`, 0 trafień, cel wyczyszczony, bohater bez strat.
        - Zmiana dotyka `doAttack` i `commitDamage`, więc poszły też scenariusze kontrolne:
          - `dev/005-z2-mistrz-1h` (`20261105-224023`, 8 z 8): combo treningu bez zmian;
          - `002/K01a-pal230-cel` (`20261105-224110`, 10 z 10): zwykła walka zadaje obrażenia,
            88 trafień z premiami 002 jak dotąd.
        - `dat.py prefix`: kod 0, 34 nazwane symbole na końcu.

      (W6)

## Faza 2: Dziennik walki, treść treningu i dane testowe

Z5 wymaga formatu z Z4, a Z7 skryptów z Z6. Z5, Z6 i Z8 nie zależą od siebie.

- [x] **Z4** Dziennik walki dla treningu (plan E3).
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
      - Wynik (2026-11-05):
        - `FightLog::practice` i `FightLog::aiState`. Licznik `pseries` siedzi w danych postaci
          dziennika, nie w `Npc`. `Npc::isPracticeHit()` daje `src` `practice`.
        - Waypoint: `wp` postaci z `World::findPoint`. `wp_angle` liczony jak `Npc::angleDir`, czyli
          w konwencji `rotation()`.
        - W pliku testowym `TST_SetWp` i `TST_StartStand`.
        - `tests/dev/005-z4-dziennik`, przebieg `20261105-224716`, 2 z 2, na placu koszar
          (`NW_CITY_HABOUR_KASERN_CENTRE_01`):
          - zdarzenia `practice`: `fwd`/`new`, `fwd`/`fwd`, `block`, `jumpback`, `left`/`new`, z
            `pseries` 1-4, `end_ms`, `wp_dist` 194-236 i `wp_angle` 30;
          - po `TST_StartStand` zdarzenie `ai` `ZS_STAND_ARMSCROSSED`.
        - Kontrola istniejących miar: `dev/005-z2-mistrz-1h` (`20261105-224801`, 8 z 8) i
          `dev/005-z2-nowicjusz-2h` (`20261105-224848`, 6 z 6), te same wartości. W drugim
          przepadłe ciosy mają `link` `dropped`.
        - **Ryzyko R2 potwierdzone.** W `dev/005-z2-mistrz-1h` combo 4 ciosów mistrza 1H przesuwa
          manekina z 77 do 356 cm od waypointu, czyli o około 2,8 m. Odskok cofa o około 1,2 m.
          W5 dopuszcza 1,5 m jako wartość startową. Do decyzji przy Z6: próg W5 albo krótsze serie
          do przodu.
        - `dat.py prefix`: kod 0, 40 nazwanych symboli na końcu.

      (W5, W7, W9)
- [x] **Z5** [P] Miary treningu w `tools/fightlog.py` (plan, „Narzędzia i testy”).
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
      - Wynik (2026-11-05):
        - Pomiar przerw zmieniony decyzją właściciela przy Z5. Plan liczył przerwę jako odstęp od
          `end_ms` serii do następnej, ale w odstęp wlicza się powrót na waypoint (combo mistrza
          odsuwa NPC o około 2,8 m, Z4). Zostaje odstęp, a raport pomija odstępy, po których
          następna seria zaczyna się mniej niż 30 cm dalej od waypointu niż poprzednia, bo wtedy
          postać mogła wracać. Odstęp od 5,5 s to odpoczynek. Silnik bez zmian.
          - Ograniczenia: obrót do waypointu wlicza się w przerwę. Seria, która prawie nie przesuwa
            postaci (sam cios z boku), też wypada z próbki. Reguła zakłada, że postać ćwiczy na
            waypoincie zwrócona jak on, więc ciosy ją od niego odsuwają.
        - Miary `practice.*`: `moves`, `move.<ruch>`, `dropped`, `series`, `series.<rodzaj>`
          (`fwd`, `combo`, `left`, `right`, `mixed`), `series_per_defend`, `pause.count`,
          `pause.min_ms`, `pause.max_ms`, `pause.median_ms`, `rest.count`, `series_per_rest`,
          `period.min` (okres powtórzony co najmniej dwa razy), `wp_dist.max_cm` (ciosy),
          `wp_angle.max_deg` (pierwszy ruch serii), `sync_pct` (200 ms) i `after_ai.max_ms`.
          Raport ma dla każdej postaci trzy linie „Trening”.
        - Ręczne przeliczenie `dev/005-z2-mistrz-1h` (`20261105-224801`):
          - 10 ruchów i 3 serie ciosów (combo, mieszana, prosty), 1,5 serii na blok albo odskok;
          - jedna czysta przerwa 9017 − 7207 = 1810 ms, zgodna z raportem;
          - `wp_dist` najwyżej 365 cm;
          - odstęp przed blokiem pominięty, bo seria lewy-prawy przesunęła manekina tylko o 28 cm.
        - Oczekiwania na dzienniku `dev/005-z4-dziennik`: 11 z 12. Niezaliczone `sync_pct`, bo
          ćwiczy tylko jedna postać, więc słusznie wychodzi „brak danych”.
        - Sztuczny dziennik dwóch postaci w scratchpadzie (poza gitem) potwierdził okres 2,
          odpoczynek, przerwy 1000 ms, `sync_pct` 100% i `after_ai` 1500 ms.
        - Wcześniejsze oczekiwania bez zmian: `dev/005-z2-nowicjusz-2h` sprawdzony ponownie,
          zaliczony.

      (W9)
- [x] **Z6** [P] Skrypty treningu w `Practice_Melee.d` (plan, „Skrypty”).
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
      - Wynik (2026-11-05):
        - **Decyzje właściciela przy Z6:**
          - R2: W5 i K5 zmienione w spec.md. W trakcie serii do 3,5 m od waypointu, początek serii
            najwyżej 0,6 m. Najpierw było 0,5 m, ale `AI_GotoWP` kończy się 20-60 cm od punktu.
          - Pomiar przerw: odstęp między seriami zawiera powrót na waypoint, więc reguła z Z5 nie
            zostawiała próbek. Silnik zapisuje zdarzenie `wait` (`AI_Wait`, `AI_WaitMs`, tylko postacie
            z dziennika). `fightlog.py` liczy przerwy i odpoczynki z czekania zaraz po serii.
          - Doszła miara `practice.start_dist.max_cm`.
        - Skrypty jak w planie, a do tego:
          - zawsze `AI_GotoWP` i `AI_AlignToWP` po serii;
          - po bloku albo odskoku powrót przed serią (odskok przesuwa o około 1,2 m, blok pięściami
            o około 0,6 m);
          - liczniki bloków i odpoczynków w `aivar` 91 i 92;
          - seria mieszana bez dwóch takich samych ciosów pod rząd, bo dwa razy ten sam cios z boku
            silnik łączy jak combo do przodu.
        - R4 (pięści przy broni w walce) nie wymaga zmian. Gdy NPC dostaje `B_Attack`, koniec stanu
          treningu się nie wykonuje, ale `B_SelectWeapon` w `ZS_Attack` chowa pięści i dobywa broni.
        - W pliku testowym `TST_StartPractice`, `TST_SetProfile` i `TST_SetWalk`.
        - Scenariusze robocze:
          - `dev/005-z6-mistrz-1h`, 6 minut czasu gry, przebieg `20261105-232940`: 66 serii (prosty 15,
            combo 16, lewy 14, prawy 7, mieszana 14), combo 1-4, przerwy 0,52-1,98 s, 11 odpoczynków
            (seria na 6), 4,7 serii na blok albo odskok, 0 trafień, cios najdalej 152 cm, początek serii
            najdalej 53 cm, odchylenie 0°. Zaliczony po zmianie progu startu na 0,6 m
            (`fightlog.py check` z tym samym dziennikiem);
          - `dev/005-z6-piesci`, przebieg `20261105-233311`, zaliczony: pięści przy założonym mieczu,
            37 serii, combo 2 (12 przepadłych), sierpowe z obu stron, przerwy 1,06-3,49 s, start do 39 cm;
          - diagnoza `dev/005-z6-lewy` i `dev/005-z6-profil99`. W pierwszym przebiegu mistrza 1H
            (3 minuty) nie wypadła żadna seria „sam lewy”. Lewy z postawy działa w obu trybach chodu
            (4 z 4), profil 99 daje 18 lewych i przerwy dokładnie 2000 ms, a bajtkod wyboru serii jest
            poprawny. W dłuższym przebiegu lewych było 14, więc to był przypadek losowania.
        - `dat.py prefix`: kod 0.

      (W1, W2, W3, W4, W5, W7, W8, W11)
- [x] **Z7** Dane testowe treningu w pliku testowym (plan, „Skrypty”).
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
      - Wynik (2026-11-05):
        - Postacie `TST_Practice_Master1H`, `Novice2H`, `Master2H`, `Fist1H`, `NoWeapon`, `Profile`,
          `Shift` (id 9910-9916, gildia straży, plany dnia `Rtn_Start_99xx`). Imiona po polsku, plik
          testowy w cp1250.
        - `TST_PracticeMilitia` używa `B_StartOtherRoutine`. Samo `Npc_ExchangeRoutine` zostawiało
          strażnika 329 w starym treningu do końca jego pory (20:58), bo stan nie kończył się sam.
        - Poprawki skryptu treningu znalezione w Z7:
          - przed pierwszą serią NPC jeszcze raz staje na miejscu (`B_PracticeMelee_Place`), bo po
            marszu z daleka pierwsza seria startowała odwrócona o 74-127° od kierunku waypointu;
          - drugie `AI_GotoWP` do tego samego waypointu nic nie robi (silnik nie liczy nowej trasy do
            tego samego celu), więc zostaje jedno.
        - **Decyzja właściciela przy Z7:** początek serii najwyżej 0,75 m od waypointu (W5, K5).
          Postacie 2H po powrocie zaczynały serię do 68 cm od niego, bo silnik kończy dojście około
          60 cm od punktu, a dochodzi obrót.
        - Scenariusze robocze (10:00, strażnicy 330 i 331 usunięci, czas ×2, 150 s gry):
          - `dev/005-z7-postacie-a` (`20261105-234857`): mistrz 1H 24 serie, nowicjusz 2H 16 (combo
            najwyżej 2), mistrz 2H 19, odchylenie 0°. Początek serii do 52, 64 i 68 cm. Zaliczony po
            zmianie progu na 0,75 m (`fightlog.py check` tego samego dziennika);
          - `dev/005-z7-postacie-b` (`20261105-235042`), zaliczony: pięściami przy mieczu 23 serie
            (tryb pięści), bez broni 23 (pięści, combo 2), profil 99 36 lewych i 0 prawych, strażnik
            329 po `TST_PracticeMilitia` 20 serii nowego treningu, odchylenie 0°.
          - Przebiegi poszły jeszcze z drugim `AI_GotoWP`, które nic nie robiło. Jego usunięcie nie
            zmienia zachowania.
        - `TST_Practice_Shift` (K8) sprawdzi dopiero Z10.
        - `dat.py prefix`: kod 0.

      (W1, K1-K8, K10)
- [x] **Z8** [P] Dokumentacja skryptów i changelog.
      - `content/Scripts/README.md`, sekcja „Symbole dla silnika”: tabela funkcji zewnętrznych
        (`AI_ReadyFist`, `AI_PracticeMove`, ADR 0010), plany dnia treningu, ustawienia i profile,
        `AIV_PracticeProfile`.
      - `CHANGELOG.md` `[Unreleased]`: trening walki wręcz NPC i nowe funkcje silnika. Na starszym
        silniku wywołania są ignorowane.
      - Wynik (2026-11-05):
        - README skryptów: tabela „Funkcje zewnętrzne” (`AI_ReadyFist`, `AI_PracticeMove`) i część
          „Trening walki wręcz”: plany dnia, pętla serii, profile z wartościami profilu 0, `aivar`
          90-92 i postacie testowe.
        - Changelog: wpis 005 w „Dodano”, z działaniem na starszym silniku (wywołania ignorowane, postać
          stoi z dobytą bronią).
        - Bez zmian w kodzie, więc bez scenariuszy.

      (W4, W10)

## Faza 3: Scenariusze kryteriów

- [x] **Z9** Scenariusze `tests/005` K01-K06.
      - `K01-mistrz-1h`, `K02-talent-2h` i `reczne/K02-talent-2h`, `K03a-piesci-z-bronia`,
        `K03b-bez-broni`, `K03c-bronia`, `K04-profil-testowy`, `K06-bez-obrazen`. Każdy ma
        `expect nolog not implemented call [AI_PRACTICEMOVE]` i `[AI_READYFIST]`, z nazwą funkcji,
        bo log gry ma inne linie „not implemented call”.
      - K05 nie ma osobnego scenariusza: jego oczekiwania (`start_dist`, `wp_dist`, `wp_angle`) siedzą
        w K01-K03,
        z nagłówkiem `criterion: 005 K5`.
      - Progi oczekiwań według kryteriów ze spec.md. Gdy próg trzeba poprawić, robimy to osobnym
        commitem z uzasadnieniem w scenariuszu (ADR 0004).
      - Sprawdzenie: każdy scenariusz uruchomiony pojedynczo (`-Scenario`).
      - Wynik (2026-11-06 i 2026-11-11):
        - Nowe polecenie konsoli `wp info <waypoint>` (`common/marvin.*`, opis w `tests/README.md`)
          wypisuje pozycję i kierunek waypointu. K06 stawia z niego bohatera 70 cm przed `CENTRE_01`
          (`goto pos 4423 800 7010`). Tekst powstaje przez `std::string`, bo `string_frm` przepełniał
          stertę przy dłuższym napisie z liczbami (osobna poprawka upstreamu na gałęzi
          `claude/xenodochial-booth-7cd831`).
        - **Decyzja właściciela przy Z9:** w K6 mieszczanin i owca stają obok ćwiczącego (1-3 m), nie
          w miejscu bohatera. Dopisek jest w spec.md.
        - Funkcje testowe: `TST_HpLostSum`, `TST_HasMeleeWeapon`, `TST_MarkMace`, `TST_MaceGained`,
          `TST_IsPracticing`, `TST_IsCalm` i `TST_IsMonsterCalm`, a także mieszczanin
          `TST_Practice_Bystander` ze zwykłymi percepcjami ludzi (id 9917).
        - Pierwsza runda (2026-11-06): K01, K03b i K06 przegrały przez walkę, nie przez trening.
          - Bohater stał w budynku koszar (`NW_CITY_KASERN_BARRACK02_03`), a ćwiczący z gildii straży
            atakują intruza w swoich pomieszczeniach.
          - Trafienia miały `src` `queue`. Postać bez broni wzięła maczugę, przeszukując powalonego
            bohatera.
          - Właściciel przypadkiem zamknął jedno okno i latał Marvinem.
          - Scenariusze stawiają teraz bohatera na placu (`CENTRE_02`), a K06 usuwa też strażników 330
            i 331.
        - K03b: `B_RefreshAtInsert` z gry daje wstawionemu NPC straży bez broni maczugę do ekwipunku
          (bez zakładania). Scenariusz sprawdza więc przyrost od chwili po wstawieniu
          (`TST_MarkMace`, `TST_MaceGained`), a nie samą obecność maczugi.
        - Przebiegi zaliczone:
          - `K01-mistrz-1h` (`20261111-165255`, 24 z 24). Serie: prosty 24, combo 35, lewy 10,
            prawy 18, mieszana 20. Combo 2, 3 i 4 są (13, 8 i 14 razy), blok albo odskok co 5,1 serii,
            przerwy 521-1997 ms, odpoczynek co 5,9 serii, okres 107 (brak cyklu), start serii do 62 cm,
            odchylenie 0°, najdalej 256 cm, 0 trafień;
          - `K02-talent-2h` (`20261111-165855`, 17 z 17). Combo nowicjusza 2 i mistrza 4, trafienie
            nowicjusza od 324 ms, mistrza do 216 ms, przerwy 2000-4989 i 520-1999 ms, synchronizacja
            10,6% i 7,7%, start serii do 64 i 70 cm, odchylenie 0°, najdalej 280 cm;
          - `K03a-piesci-z-bronia` (`20261106-002001`, 10 z 10): tryb pięści, combo 2, sierpowe;
          - `K03b-bez-broni` (`20261111-171031`, 10 z 10): pięści, bez założonej broni, bez nowej
            maczugi;
          - `K03c-bronia` (`20261106-002353`, 6 z 6): tryb broni, combo 4;
          - `K04-profil-testowy` (`20261106-002554`, 9 z 9): 43 lewe, poza tym 0, przerwa 2000 ms,
            0 odpoczynków;
          - `K06-bez-obrazen` (`20261111-170555`, 8 z 8): 171 pudeł `practice`, 0 trafień, bohater,
            mieszczanin i owca bez straty życia, mieszczanin i owca spokojni, ćwiczący dalej ćwiczy,
            odchylenie do 5°.
        - K03a, K03c i K04 poszły jeszcze z bohaterem w koszarach, ale ich oczekiwania nie zależą od
          walki o wtargnięcie. Z11 uruchomi cały zestaw na zacommitowanym kodzie.
        - `dat.py prefix`: kod 0.

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
