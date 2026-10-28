# Zadania 001: Combosy NPC w walce wręcz

- **Plan:** [plan.md](plan.md)
- **Utworzono:** 2026-10-28

Każde zadanie mieści się w jednym commicie. `[P]` oznacza zadanie, które można robić równolegle
z innymi `[P]` w tej samej fazie. W nawiasie: wymagania (W) i kryteria (K), które zadanie realizuje.

Zadania w silniku budujemy przez `tools/build-engine.ps1`. Zadania w skryptach sprawdzamy przez
`tools/build-scripts.ps1` i `tools/dat.py diff` (zmienić się mogą tylko zamierzone symbole).
Plan nie zmienia serializacji i nie dodaje funkcji zewnętrznych, więc nie ma dla nich osobnych zadań.
Uruchamianie gry i instalacja moda w folderze gry wymagają za każdym razem zgody właściciela projektu.

## Faza 1: Przygotowanie

- [x] **Z1** Zapis testowy z wersji 0.1.0 do K9: przed jakąkolwiek zmianą zbudować i zainstalować
      obecny mod, zrobić zapis w trakcie walki z `Pal_230_Ritter` i odłożyć go poza folder gry.
      Ścieżkę zanotować w sekcji „Weryfikacja” w spec.md. Bez commita, bo zapis jest plikiem lokalnym. (W10, K9)
- [x] **Z2** [P] `content/Scripts/README.md`: sekcja „Symbole dla silnika” (ADR 0003) z opisem
      `MAX_MOVE` do 16, klasy `C_FightAI_Combo`, instancji `FA_COMBO_<N>` i znaczenia
      `FA_MY_W_COMBO_<N>`. (W9)
- [x] **Z3** [P] `_intern/Fight.d`: `MAX_MOVE = 12` i klasa `C_FightAI_Combo` (`link_min`, `link_max`,
      `defend_in_series`, `break_on_lost`). Bez instancji, więc bez zmiany zachowania. `dat.py diff`:
      tylko nowa klasa i większa tablica `move`. (W3, W5, W6, W7)

## Faza 2: Mechanizmy w silniku

- [x] **Z4** [P] E1: listy ruchów FAI dłuższe niż 6. Własny typ listy ruchów w `FightAi::FA`
      (do 16), loader czyta liczbę ruchów z `C_FIGHTAI.MOVE`, `FightAlgo::fillQueue` losuje z nowej
      listy. Sprawdzenie: oryginalny `Fight.dat` daje te same listy co przed zmianą. (W3, W9)
- [x] **Z5** [P] E3: zapytanie o okno combo bieżącego ciosu w `Pose` i `MdlVisual`: początek i koniec
      okna bieżącego etapu, `DEF_HIT_END`, czy to wieloetapowe combo do przodu, czy etap jest ostatni.
      Bez użycia w logice walki. (W1, W4, W7)
- [x] **Z6** E2: rejestracja `C_FightAI_Combo` jako klasy nieprzezroczystej i wczytywanie opcjonalnych
      instancji `FA_COMBO_<N>` do `FightAi::FA` (parametry i znacznik obecności). Po Z4, te same pliki.
      (W5, W6, W7, W9)
- [x] **Z7** E4, rdzeń: łączenie ciosu z kolejki w oknie combo dla stylów z `FA_COMBO_<N>`. Nowa metoda
      wołana z gałęzi `BS_HIT` w `Npc::implAttack`, losowanie chwili z `link_min`/`link_max` raz
      na okno, margines przed `DEF_HIT_END`, `implFaiWait` po połączeniu, stan przejściowy
      w `FightAlgo` bez zapisu. Style bez `FA_COMBO_<N>` idą dotychczasową ścieżką. Po Z5 i Z6.
      (W1, W2, W7, W8, W9, W10)
- [x] **Z8** E4, kontynuacja: gdy kolejka jest pusta, raz na okno po ciosie do przodu (nie na ostatnim
      etapie) losowanie z `FA_MY_W_COMBO_<N>`. `MOVE_ATTACK` łączy kolejny cios do przodu, reszta
      kończy combo. (W2)
- [x] **Z9** E4, limit talentu: na ostatnim etapie combo do przodu usunąć z kolejki kolejne ciosy
      do przodu (z uwzględnieniem pięści, gdzie ciosy boczne są ciosami do przodu). (W4)
- [x] **Z10** E4, utrata celu: przy `break_on_lost` przerwanie serii, gdy przeciwnik jest poza zasięgiem
      broni albo kątem widzenia. Bez `break_on_lost` łączenie bez sprawdzania zasięgu. (W6)
- [x] **Z11** E4, obrona w serii: przy `defend_in_series`, gdy przeciwnik zaczyna cios (warunki jak
      w `fightalgo.cpp:45`), przerwanie serii i natychmiastowa reakcja z `FA_ENEMY_PREHIT_<N>`
      (blok albo odskok). (W5)

## Faza 3: Treść w skryptach

Uwaga z Z3: `FIGHT.DAT` nie zna stałych `TRUE` i `FALSE` (są tylko w `GOTHIC.DAT`), więc
w instancjach `FA_COMBO_<N>` wpisujemy `1` i `0` z komentarzem.

- [x] **Z12** [P] Style ludzi według tabeli z planu: `FAI_Human_Normal.d` (42), `FAI_Human_Strong.d` (3),
      `FAI_Human_Master.d` (4): listy `FA_MY_W_FOCUS_<N>`, `FA_MY_W_COMBO_<N>` i instancje
      `FA_COMBO_<N>`. Tchórz (2) bez zmian. Szkielety dostają zmiany przez swoje style. (W2, W3, W5, W6, W7)
- [x] **Z13** [P] Orkowie i elita orków: `FA_MY_W_COMBO_12` i `FA_COMBO_12` w `FAI_Orc.d`, nowy
      `FAI_Orc_Elite.d` (styl 13, pozostałe stany skopiowane z 12), `FAI_ORC_ELITE = 13`
      w `AI_Constants.d`, `fight_tactic = FAI_ORC_ELITE` w `MST_OrcElite.d`. (W2, W3, W5, W6, W7)
- [ ] **Z14** Wersja moda 0.2.0 w `mod.json` i wpis w `CHANGELOG.md` (bramka konstytucji, zasada 8).
      Po Z12 i Z13.

## Faza 4: Weryfikacja

- [ ] **Z15** Przejść kroki kryteriów akceptacji K1–K12 (K8 na silniku bez moda, K9 z zapisem z Z1)
      i uzupełnić sekcję „Weryfikacja” w spec.md. Wartości startowe z tabeli w planie stroić w skryptach
      z Z12 i Z13, a poprawki zapisywać osobnymi commitami. Na końcu przejść walki fabularne z P7 (Raven, paladyni,
      Lee, łowcy smoków, elita orków) i zanotować wnioski. (K1–K12)
