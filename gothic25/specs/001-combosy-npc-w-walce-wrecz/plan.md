# Plan 001: Combosy NPC w walce wręcz

- **Specyfikacja:** [spec.md](spec.md)
- **Status:** Zatwierdzony
- **Utworzono:** 2026-10-28

## Podsumowanie

Silnik dostaje ogólny mechanizm łączenia ciosów NPC w oknie combo, tą samą ścieżką, której używa
gracz. Mechanizm włącza się tylko dla stylów walki, które w skryptach mają nową, opcjonalną instancję
`FA_COMBO_<N>`. Ta instancja niesie też parametry stylu (tempo łączenia, obrona i przerywanie serii).
Skrypty walki dostają serie wielociosowe, kontynuację combo (`FA_MY_W_COMBO_<N>`, dziś puste),
osobny styl dla elity orków i większy limit ruchów na stan. Bez skryptów moda nic się nie zmienia.

## Warstwa

**Skrypty i silnik.**

- **Zasoby nie wystarczą.** Okna combo w animacjach (`DEF_WINDOW`, `DEF_HIT_END`) są poprawne
  i działają u gracza. Problemem jest to, że NPC nigdy nie trafia w okno, a nie sama animacja.
- **Same skrypty nie wystarczą.** Skrypty decydują o wyborze ruchu (FAI) tylko między animacjami.
  Nie mają wpływu na to, kiedy w trakcie animacji ataku pada następny cios. Nawet seria mistrzowska
  wpisana w skrypty dałaby dziś cztery razy pierwszy cios (zob. „Obecny stan”). Łączenie w oknie,
  limit z talentu, obrona i przerywanie w trakcie serii wymagają decyzji podejmowanych co klatkę
  w trakcie animacji, czyli silnika.
- **Treść zostaje w skryptach** (zasada 2): które serie, jak często, jak szybko, kto się broni
  w trakcie serii.

## Obecny stan

**Wybór i wykonanie ruchów NPC**

- Skrypt `ZS_Attack` wywołuje `AI_Attack`. Akcja `AI_Attack` (`common/world/objects/npc.cpp:2715`)
  woła `FightAlgo::fetchInstructions`, która ocenia stany FAI stylu NPC i losuje jeden ruch
  (`common/game/fightalgo.cpp:33` `fillQueue`, losowanie równomierne w `:92`).
- Ruch rozwija się w kolejkę akcji `tr[6]` (`common/game/fightalgo.cpp:105` `nextFromQueue`).
  Np. `ATTACK_MASTER` to lewo, prawo, przód ×4 (`:163`), `ATTACK_TRIPLE`, `ATTACK_WHIRL`,
  `ATTACK_FRONT`, `ATTACK_SIDE` analogicznie.
- `Npc::implAttack` (`common/world/objects/npc.cpp:1557`) wykonuje kolejkę co klatkę:
  - Gdy trwa animacja ciosu (`BS_HIT`), NPC tylko obraca się do celu i wychodzi (`:1576-1581`).
    Kolejki w tym czasie nie czyta.
  - Po ciosie czeka do końca trafienia: `implFaiWait(atkTotalTime()+1)` (`:1712-1716`), czyli do
    `DEF_HIT_END` bieżącego etapu.
  - Atak boczny poza zasięgiem broni (gdy NPC nie biegnie) jest pomijany (`:1654-1658`).
  - Pięści zamieniają ataki boczne na cios do przodu (`:1708`).
- Reakcja na nadchodzący cios przeciwnika (`FA_ENEMY_PREHIT_<N>`) jest sprawdzana tylko przy
  wyborze nowego ruchu (`common/game/fightalgo.cpp:45`), nigdy w trakcie serii.
- Trafienie czyści kolejkę (`FightAlgo::onTakeHit`, `common/game/fightalgo.cpp:228`, wołane
  z `common/world/objects/npc.cpp:2080`). Leżący cel czyści ją na początku `implAttack` (`:1561`).

**Combo w animacji**

- Łączenie ciosów robi `Pose::continueCombo` (`common/graphics/mesh/pose.cpp:728`), wołane
  z `Npc::doAttack` (`common/world/objects/npc.cpp:3801`) dla gracza i NPC tak samo. W oknie
  combo kolejny cios do przodu przeskakuje animację na `DEF_HIT_END` bieżącego etapu i zwiększa
  licznik combo (`pose.cpp:783-785`). Inny atak (np. lewo po przodzie) w oknie startuje od razu
  i zeruje licznik. Blok w trakcie ataku przerywa atak („hit -> block”).
- Animacje z oknem combo są klasy `Transition` bez następnika
  (`common/graphics/mesh/animation.cpp:183-187`). Po `DEF_HIT_END` bieżącego etapu warstwa jest
  zdejmowana (`pose.cpp:280`, `animation.cpp:239`).
- `Npc::tick` przetwarza animacje (`tickAnimationTags`, `npc.cpp:2345`) przed `implAttack`
  (`:2391`). Kiedy NPC kończy czekanie (`DEF_HIT_END`+1 ms), warstwa ataku już zniknęła,
  `continueCombo` nie ma czego kontynuować, a następny cios do przodu zaczyna combo od zera.
  **To jest przyczyna, dla której seria mistrzowska daje dziś „pierwszy cios ×4”.**

**Dane FAI**

- `FightAi` (`common/game/definitions/fightaidefinitions.cpp`) wczytuje z `Fight.dat` instancje
  `FA_*_<N>` dla `N < MAX_FIGHTAI`, w tym `FA_MY_W_COMBO_<N>` (`:60`). `FightAlgo` z niej
  nie korzysta. We wszystkich 28 plikach FAI Nocy Kruka `FA_MY_W_COMBO_*` i `FA_MY_G_COMBO_*` są puste.
- Limit 6 ruchów na stan pochodzi z ZenKit (`zenkit::IFightAi::move_count`,
  `lib/ZenKit/include/zenkit/addon/daedalus.hh:1171`, podmoduł). Loader odrzuca nadmiarowe ruchy.
  W skryptach to `MAX_MOVE = 6` (`content/Scripts/Content/_intern/Fight.d:24`).
- Klasa `C_FIGHTAI` jest rejestrowana jako nieprzezroczysta (`common/gothic.cpp:997`),
  a ruchy czyta się przez instancję nieprzezroczystą i symbol składowej `C_FIGHTAI.MOVE`.

**Skrypty**

- Style ludzi: tchórz 2, normalny 42, silny 3, mistrz 4
  (`content/Scripts/Content/AI/AI_Intern/AI_Constants.d:468-471`). Orkowie 12 (`:497`).
- Ruchy w `FA_MY_W_FOCUS_<N>`: tchórz `ATTACK, WAIT, WAIT`, normalny `ATTACK`, silny
  `FRONTATTACK, ATTACK, JUMPBACK`, mistrz `FRONTATTACK, ATTACK, WAIT`
  (`FAI/FAI_Human_Master.d:72`), orkowie `ATTACK, SIDEATTACK, TRIPLEATTACK, WAIT ×3` (`FAI/FAI_Orc.d:72`).
- Elita orków, wojownicy, szamani, nieumarli orkowie i jaszczuroludzie mają styl `FAI_ORC`
  (`Story/NPC/Orc/MST_OrcElite.d:45`, `Story/NPC/Monster/MST_Draconian.d:45`). Szkielety mają
  style ludzi (`Story/NPC/Monster/MST_Skeleton.d:39`). Wolne numery stylów: 13, 14, 17, 25–30 i inne.
- `Fight.src` dołącza `FAI\FAI_*.D`, więc nowy plik FAI wejdzie do `FIGHT.DAT` bez zmiany listy.

**Zapisy**

- `FightAlgo::save` zapisuje `queueId`, `tr[6]` i `hitFlg` (`common/game/fightalgo.cpp:26`).
  `Pose::save` zapisuje warstwy z czasem startu i stan combo (`pose.cpp:48-56`). Wersja zapisu
  pochodzi z upstreamu (`Serialize::Version::Current = 55`, `common/game/serialize.h:36`).

## Projekt

Zmianę włącza i parametryzuje skrypt zgodnie z [ADR 0003](../../decisions/0003-przelaczniki-silnika-w-skryptach.md).
Mechanizm działa dla NPC, którego styl walki `<N>` ma instancję `FA_COMBO_<N>`.
Pozostałe style, a także oryginalne skrypty G1 i G2, działają jak dotąd.

### Silnik (C++)

Zmiany w dwóch grupach, które da się zgłosić upstreamowi osobno.

**E1. Więcej niż 6 ruchów na stan FAI** (`common/game/definitions/fightaidefinitions.*`,
`common/game/fightalgo.*`)

- `FightAi::FA` przechowuje ruchy we własnym typie (tablica do 16 ruchów i ich liczba) zamiast
  `zenkit::IFightAi`. Loader czyta tyle ruchów, ile ma składowa `C_FIGHTAI.MOVE` w skryptach
  (`MAX_MOVE`), najwyżej 16.
- `FightAlgo::fillQueue` losuje z tej listy. Przy `MAX_MOVE = 6` (oryginalne skrypty)
  zachowanie jest identyczne.

**E2. Parametry combo stylu walki** (`common/game/definitions/fightaidefinitions.*`, `common/gothic.cpp`)

- Nowa opcjonalna klasa skryptowa `C_FightAI_Combo` (rejestrowana jako nieprzezroczysta, jak `C_FIGHTAI`)
  i instancje `FA_COMBO_<N>`. Składowe:

  | Składowa | Znaczenie |
  |---|---|
  | `link_min`, `link_max` | moment połączenia ciosu: losowo między tymi procentami użytecznej części okna combo |
  | `defend_in_series` | `TRUE`: w trakcie serii NPC reaguje na nadchodzący cios przeciwnika (`FA_ENEMY_PREHIT_<N>`) i przerywa serię |
  | `break_on_lost` | `TRUE`: NPC przerywa serię, gdy przeciwnik wyjdzie z zasięgu broni albo z pola widzenia z przodu |

- `FightAi::FA` dostaje pole z tymi parametrami i znacznik, czy instancja istnieje.

**E3. Okno combo bieżącego ciosu** (`common/graphics/mesh/pose.*`, `common/graphics/mdlvisual.*`)

- Nowe zapytanie o bieżącą warstwę ataku: początek i koniec okna combo bieżącego etapu, `DEF_HIT_END`
  etapu (w czasie gry), czy to wieloetapowe combo do przodu i czy etap jest ostatni.
- Użyteczna część okna to od `DEF_WINDOW` (początek) do `min(DEF_WINDOW koniec, DEF_HIT_END) − margines`
  (ok. 50 ms). Po `DEF_HIT_END` warstwa znika i połączenie jest już niemożliwe.

**E4. Łączenie ciosów w oknie** (`common/game/fightalgo.*`, `common/world/objects/npc.cpp` `implAttack`)

W gałęzi `BS_HIT` w `implAttack` (zamiast samego obracania), gdy styl ma `FA_COMBO_<N>`,
a bieżący cios jest już w oknie combo:

1. **Kandydat na następny cios:**
   - pierwsza akcja z kolejki, jeśli to atak (dla pięści zamieniony na cios do przodu jak dziś),
   - w przeciwnym razie kontynuacja: raz na okno, tylko po ciosie do przodu i gdy etap nie jest
     ostatni, silnik losuje ruch z `FA_MY_W_COMBO_<N>`. `MOVE_ATTACK` oznacza kolejny cios do przodu,
     każdy inny ruch albo pusta lista oznacza koniec combo.
2. **Limit talentu (W4):** gdy kandydat to cios do przodu, a bieżąca animacja jest ostatnim etapem
   combo do przodu, silnik usuwa z kolejki wszystkie kolejne ciosy do przodu i nie łączy.
3. **Utrata celu (W6):** gdy `break_on_lost` i przeciwnik jest poza zasięgiem broni albo poza kątem
   widzenia, silnik czyści serię i nie łączy (NPC kończy bieżący cios, potem zwykła ocena FAI).
   Bez `break_on_lost` cios jest łączony bez względu na zasięg (cios w powietrze). Dzisiejsze
   pomijanie ataków bocznych poza zasięgiem (`npc.cpp:1654`) w tej ścieżce nie jest stosowane.
4. **Obrona w serii (W5):** gdy `defend_in_series` i przeciwnik zaczyna cios (te same warunki co
   `fightalgo.cpp:45`), silnik czyści serię i od razu wykonuje reakcję z `FA_ENEMY_PREHIT_<N>`
   (blok przerywa animację ataku tak jak u gracza, odskok jak dziś).
5. **Moment połączenia (W7):** raz na okno silnik losuje chwilę między `link_min` a `link_max`
   procent użytecznej części okna. Gdy nadejdzie, wywołuje `doAttack` z kandydatem (`continueCombo`),
   zdejmuje akcję z kolejki i ustawia `implFaiWait` na koniec nowego etapu.
6. **Stan przejściowy:** wylosowana chwila i decyzja o kontynuacji dla bieżącego okna siedzą
   w polach `FightAlgo`, których nie zapisujemy. Okno rozpoznajemy po czasie startu warstwy
   i liczniku combo.

Gdy leżący cel albo trafienie czyści kolejkę, działa to bez zmian (`npc.cpp:1561`, `fightalgo.cpp:228`).

### Skrypty (Daedalus)

Wszystkie pliki w `content/Scripts/Content`, kodowanie cp1250, zmiany sprawdzane `tools/dat.py diff`.

- **`_intern/Fight.d`:** `MAX_MOVE = 12` oraz klasa `C_FightAI_Combo` (składowe z E2).
- **Style i wartości startowe** (do strojenia w trakcie weryfikacji):

  | Styl (plik) | `FA_MY_W_FOCUS_<N>` | `FA_MY_W_COMBO_<N>` | `FA_COMBO_<N>`: link, obrona, przerywanie |
  |---|---|---|---|
  | tchórz 2 (`FAI_Human_Coward.d`) | bez zmian | bez zmian (puste) | brak instancji: mechanizm wyłączony |
  | normalny 42 (`FAI_Human_Normal.d`) | `ATTACK ×2, SIDEATTACK, FRONTATTACK` | puste | 60–100%, nie, nie |
  | silny 3 (`FAI_Human_Strong.d`) | `ATTACK ×2, SIDEATTACK, FRONTATTACK, TRIPLEATTACK, JUMPBACK` | `ATTACK, WAIT` | 30–80%, nie, nie |
  | mistrz 4 (`FAI_Human_Master.d`) | `ATTACK ×5, SIDEATTACK, FRONTATTACK, TRIPLEATTACK, WHIRLATTACK, MASTERATTACK, WAIT` | `ATTACK ×3, WAIT` | 0–40%, tak, tak |
  | orkowie 12 (`FAI_Orc.d`) | bez zmian | `ATTACK, WAIT` | 50–100%, nie, nie |
  | elita orków 13 (nowy `FAI_Orc_Elite.d`) | `ATTACK ×4, SIDEATTACK, FRONTATTACK, TRIPLEATTACK, WHIRLATTACK, MASTERATTACK, WAIT ×2` | `ATTACK ×2, WAIT` | 0–40%, tak, tak |

  Pozostałe stany FAI elity orków kopiujemy ze stylu 12.
- **`AI/AI_Intern/AI_Constants.d`:** `FAI_ORC_ELITE = 13`.
- **`Story/NPC/Orc/MST_OrcElite.d:45`:** `fight_tactic = FAI_ORC_ELITE` (dotyczy wszystkich
  instancji elity, w tym pułkowników).
- **`content/Scripts/README.md`:** sekcja „Symbole dla silnika” z `C_FightAI_Combo`, `FA_COMBO_<N>`
  i nowym znaczeniem `FA_MY_W_COMBO_<N>` (ADR 0003).

### Zasoby

Brak zmian.

### Zapisy gry

Brak nowego stanu w zapisie. Kolejka serii i stan animacji (z licznikiem combo) są zapisywane już
dziś. Nowe pola (wylosowana chwila połączenia, decyzja o kontynuacji) są przejściowe. Po wczytaniu
NPC losuje je od nowa dla bieżącego okna albo kończy serię zwykłą drogą. Wartości akcji kolejki
(`MV_*`) się nie zmieniają, więc zapisy z 0.1.0 wczytują się bez konwersji, a wersja zapisu
pozostaje upstreamowa.

## Pokrycie wymagań

| Wymaganie | Gdzie realizowane |
|---|---|
| W1 | E3 i E4 (łączenie w oknie przez `continueCombo`), długości combo z animacji bez zmian |
| W2 | skrypty: serie w `FA_MY_W_FOCUS_<N>`, kontynuacja w `FA_MY_W_COMBO_<N>`; E4 krok 1 |
| W3 | skrypty: tabela stylów, styl 13 dla elity orków; E1 (więcej ruchów, by zmieścić proporcje mistrza) |
| W4 | E4 krok 2 (usuwanie nadmiarowych ciosów do przodu na ostatnim etapie) |
| W5 | E4 krok 4 i `defend_in_series` w skryptach; trafienie czyści serię jak dziś |
| W6 | istniejące czyszczenie przy leżącym celu; E4 krok 3 i `break_on_lost` w skryptach |
| W7 | E3 (granice okna) i E4 krok 5 (`link_min`/`link_max` w skryptach) |
| W8 | ta sama ścieżka `implAttack` dla walki z graczem, z NPC, na arenie i „do nieprzytomności” |
| W9 | ADR 0003: bez `FA_COMBO_<N>` i przy `MAX_MOVE = 6` silnik działa jak dziś |
| W10 | brak nowego stanu w zapisie, stan przejściowy losowany od nowa (sekcja „Zapisy gry”) |

## Bramka konstytucji

- [x] 1. Najniższa wystarczająca warstwa: zasoby i skrypty nie sterują chwilą ciosu w trakcie
      animacji (sekcja „Warstwa”).
- [x] 2. Silnik daje mechanizmy (łączenie w oknie, limit ruchów, parametry stylu), a skrypty decydują,
      które style, serie, tempo i obrona.
- [x] 3. Fork łatwy do aktualizacji: zmiany włączane symbolami skryptów (ADR 0003), w stylu
      OpenGothic, w dwóch grupach zgłaszalnych upstreamowi (E1 oraz E2–E4). W silniku nie ma treści moda.
- [x] 4. Zapisy gry: bez nowego stanu, bez zmiany wersji zapisu.
- [x] 5. Kryteria akceptacji K1–K12 w specyfikacji mają kroki w grze.
- [x] 6. Prawa do zasobów: brak nowych zasobów.
- [x] 7. Język: dokumenty po polsku, kod, komentarze i commity po angielsku.
- [x] 8. Wersja: **MINOR**, mod 0.2.0. Zapisy zgodne. Mod na starszym silniku działa, tylko bez nowej
      walki (silnik czyta pierwsze 6 ruchów i pomija `FA_COMBO_<N>`). Wpis w `CHANGELOG.md`.
- [x] 9. Licencja GothicMOD: zmienione skrypty walki pozostają na GothicMOD, kod silnika na MIT.

## Odstępstwa od konstytucji

Brak. Zasada 3 („flaga albo ustawienie moda”) jest spełniona przez symbole skryptów zgodnie
z przyjętym ADR 0003.

## Ryzyka

- **Przeskok animacji przy wczesnym łączeniu.** `continueCombo` przeskakuje do `DEF_HIT_END` etapu,
  więc połączenie na początku okna pomija część animacji, tak samo jak u gracza. Ciosy mistrzów
  (`link_min = 0`) mogą przez to wyglądać na szarpane. Wykrycie: K1 i K3 w zwolnionym tempie
  (`ztimer multiplyer 0.3`). Reakcja: podnieść `link_min` w skryptach.
- **Spóźnione połączenie przy niskiej liczbie klatek.** Jeśli klatka trwa dłużej niż margines przed
  `DEF_HIT_END`, łączenie się nie uda i cios zacznie combo od nowa (dzisiejsze zachowanie). Wykrycie:
  K1 przy ograniczonej liczbie klatek. Reakcja: margines zależny od długości klatki.
- **Kolejka AI blokuje `implAttack`.** Gdy w kolejce AI coś czeka, `implAttack` wychodzi przed gałęzią
  `BS_HIT` (`npc.cpp:1568`) i okno może minąć. Wykrycie: K1 i K10 (serie urwane bez powodu).
  Reakcja: obsłużyć łączenie przed tym sprawdzeniem.
- **Obrona mistrzów zbyt skuteczna.** Blok w każdej serii może zrobić z mistrzów ściany. Wykrycie:
  K5 i walki fabularne (P7). Reakcja: rzadszy blok przez proporcje w `FA_ENEMY_PREHIT_4`
  i `FA_ENEMY_PREHIT_13` (np. dodatkowe `WAIT`).
- **Konflikty z upstreamem w `implAttack`.** To często zmieniany kod. Ograniczenie: logikę łączenia
  trzymamy w `FightAlgo` i jednej nowej metodzie, a w `implAttack` zostaje tylko wywołanie.
- **Wzrost trudności walk fabularnych** (zaakceptowany w P7): po implementacji przechodzimy walki
  z Ravenem, paladynami, Lee, łowcami smoków i elitą orków.

## Alternatywy odrzucone

- **Tylko skrypty** (ruchy wielociosowe w FAI): bez zmian w silniku seria mistrzowska daje
  „pierwszy cios ×4”, a skrypty nie mają wpływu na chwilę ciosu w trakcie animacji.
- **Klucz w `.ini` moda albo jedna globalna stała:** zob. ADR 0003. `.ini` moda nie jest dziś
  czytane poza `[FILES]` i `[SETTINGS]`, a jedna stała nie pozwala zostawić tchórza bez zmian.
- **Tempo łączenia przez `MOVE_WAIT` w `FA_MY_W_COMBO_<N>`** (sprawdzanie co 200 ms): łączy decyzję
  o kontynuacji z tempem i daje skok co 200 ms przy oknach długości 0,25–0,9 s.
- **Zwiększenie limitu ruchów w ZenKit:** to podmoduł z zewnętrznego repozytorium. Własny typ
  w `FightAi` jest mniejszą zmianą i nie wymaga forka biblioteki.
- **Zapisywanie stanu łączenia w zapisie gry:** wymagałoby własnej wersji zapisu, która koliduje
  z numeracją upstreamu, a ten stan bez straty da się wylosować po wczytaniu od nowa.
- **Sztywne reguły w silniku dla gildii albo nazw NPC** (np. „paladyni się bronią”): łamie zasadę 2.
