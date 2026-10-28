# 002: Skalowanie obrażeń w kombo

- **Status:** Zatwierdzona
- **Utworzono:** 2026-10-28
- **Warstwa (wstępnie):** silnik i skrypty <!-- zasoby / skrypty / silnik -->

- **Powiązane:** [001: Combosy NPC w walce wręcz](../001-combosy-npc-w-walce-wrecz/spec.md)
  (NPC dostają mniejszą premię niż bohater, ale ich nowe combosy z 001 też będą zadawać więcej
  obrażeń; balans obu funkcji ustalamy razem).

## Problem

Każdy cios combo zadaje dziś takie same obrażenia. Kolejne ciosy combo mistrza trwają jednak dłużej
niż pierwszy, a ataki boczne są krótkie i można je szybko łączyć. W efekcie pełne combo to najmniej
opłacalny sposób walki dla postaci, która go się nauczyła. Więcej obrażeń na sekundę daje naprzemienne
lewo-prawo albo przerywanie animacji i ponawianie szybkiego ciosu.

Szacunek dla mistrza broni jednoręcznej w obecnej wersji moda, policzony z klatek animacji przy
idealnym wyczuciu czasu (do potwierdzenia pomiarem w K4):

| Sposób walki | Czas na jeden cios |
|---|---|
| pełne combo do przodu (4 ciosy) | ok. 0,63 s |
| naprzemienne ataki lewo-prawo | ok. 0,32 s |

Przy równych obrażeniach na cios lewo-prawo daje więc mniej więcej dwa razy więcej obrażeń na sekundę
niż combo, którego nauka kosztuje najwięcej punktów nauki. Gracz nie ma powodu z niego korzystać.

## Cel

Każdy kolejny cios combo do przodu zadaje więcej obrażeń niż poprzedni, tak że dla mistrza pełne
combo staje się najskuteczniejszym sposobem walki wręcz, a nie najsłabszym.

## Poza zakresem

- Zmiana animacji i tempa combo oraz ataków bocznych.
- Zmiana podstawowego wzoru obrażeń, obrażeń broni i ochrony pancerzy.
- Walka dystansowa i magia.
- Combosy NPC. To jest specyfikacja 001.
- Blokowanie technik przerywania animacji i osłabianie lewo-prawo. Ta specyfikacja tylko sprawia,
  że combo przebija lewo-prawo i powtarzanie pierwszego ciosu.
- Informacja dla gracza (dźwięk, efekt, liczby na ekranie) o mocniejszym ciosie poza trybem
  deweloperskim. Jeśli będzie potrzebna, to jako osobna funkcja.

## Scenariusze gracza

1. **Gdy** bohater z talentem mistrza broni jednoręcznej wyprowadza pełne combo do przodu, **wtedy**
   każdy kolejny cios zabiera przeciwnikowi wyraźnie więcej punktów życia niż poprzedni, a ostatni
   najwięcej.
2. **Gdy** ten sam bohater walczy na zmianę ciosami z lewej i prawej, **wtedy** każdy cios zadaje
   zwykłe obrażenia i w sumie pokonuje przeciwnika wolniej niż pełnymi combo.
3. **Gdy** nowicjusz (talent poniżej 30%) wyprowadza swoje dwuciosowe combo, **wtedy** drugi cios
   też jest mocniejszy, ale nowicjusz zyskuje na combo mniej niż wojownik, a wojownik mniej niż mistrz.
4. **Gdy** bohater uderza combo przeciwnika odpornego na dany typ obrażeń, **wtedy** przeciwnik
   pozostaje odporny, niezależnie od numeru ciosu.
5. **Gdy** gracz uruchomi grę bez moda Gothic 2.5, **wtedy** obrażenia są takie jak dotąd.

## Wymagania

- **W1:** Obrażenia ciosu z combo do przodu zależą od jego numeru w combo. Pierwszy cios zadaje tyle
  co dziś, a każdy kolejny co najmniej tyle co poprzedni.
- **W2:** Premię za każdy kolejny cios da się ustawić w danych moda bez przebudowy silnika, osobno:
  - dla broni jednoręcznej i dwuręcznej na każdym poziomie talentu (nowicjusz, wojownik, mistrz),
  - dla pięści (jedna tabela, bo pięści nie mają talentu),
  - dla bohatera i dla NPC.
- **W3:** Premia nie dotyczy ataków bocznych (także łączonych w serie lewo-prawo), ataku z biegu,
  dobijania, walki dystansowej ani magii. Ataki boczne nie dostają też żadnej kary: zadają takie
  obrażenia jak dziś.
- **W4:** Premia to procent od obrażeń końcowych: liczonych jak dziś (po odjęciu ochrony pancerza
  i po osłabieniu słabego ciosu przy niskim talencie), a przed zasadą obrażeń minimalnych.
  Odporny cel nadal nie traci życia. Przykład: siła z bronią 100, ochrona 80, premia 350%:
  20 obrażeń bez premii, 70 z premią.
- **W5:** Dla postaci z talentem mistrza (60%+) pełne combo do przodu zadaje na sekundę więcej obrażeń
  niż naprzemienne ataki boczne (lewo-prawo) i powtarzanie pierwszego ciosu, tą samą bronią przeciw
  temu samemu celowi, i to co najmniej o 20%. Przerywanie ciosu blokiem albo odskokiem nie jest
  częścią tego porównania. Wartości startowe premii bohatera-mistrza dla kolejnych ciosów combo to
  100%, 175%, 275%, 400% (średnio ok. 240% na cios). Ostateczne wartości ustala pomiar z K4.
- **W6:** Nowicjusz i wojownik dostają premię z własnych tabel (W2). Zysk z pełnego combo w porównaniu
  z lepszą z technik z W5 rośnie z talentem: u nowicjusza jest najmniejszy, u wojownika większy,
  u mistrza największy. Dotyczy to także wojownika z bronią jednoręczną, który ma combo z 4 ciosów
  jak mistrz.
- **W7:** Premia dotyczy bohatera i NPC, ale NPC mają mniejszą premię niż bohater. Wartość startowa
  dla NPC to połowa nadwyżki premii bohatera ponad 100%: przy wartościach startowych z W5 daje to
  ok. 100%, 140%, 190%, 250%.
- **W8:** W trybie deweloperskim da się odczytać, ile obrażeń zadał każdy cios wręcz, który to był cios
  combo i jaką premię dostał. Gracz bez trybu deweloperskiego tego nie widzi.
- **W9:** Bez moda Gothic 2.5 obrażenia są takie same jak w obecnej wersji silnika.
- **W10:** Zapisy gry z poprzednich wersji moda się wczytują. Po wczytaniu zapisu zrobionego w trakcie
  combo premia pierwszego ciosu zgadza się z tym, który to faktycznie cios combo (widać to po animacji):
  gra nie daje np. premii ostatniego ciosu ciosowi, który zaczyna nowe combo.

## Kryteria akceptacji

Wspólne przygotowanie (P0): mod zbudowany i zainstalowany, gra uruchomiona przez `tools/run.ps1 -Dev`,
nowa gra. Konsola: `F2`. W konsoli `cheat god`, potem `insert ch` i w rozmowie z nim: punkty nauki,
siła potrzebna do broni, „Umiejętności bojowe” → broń jednoręczna i dwuręczna do 80%. Bronie:
`insert ItMw_1h_Pal_Sword`, `insert ItMw_2h_Pal_Sword`. Cel testowy: NPC, który nie blokuje i nie
oddaje, z dużą liczbą punktów życia (przygotowany w planie i wstawiany przez `insert`).

- [ ] **K1** (W1, W8): Kolejne ciosy combo zadają rosnące obrażenia.
  - Kroki: P0, miecz jednoręczny, trzy pełne combo do przodu w cel testowy, odczyt z W8.
  - Oczekiwane: obrażenia każdego ciosu odpowiadają premii z danych moda dla jego numeru,
    a pierwszy cios zadaje tyle samo, co przed zmianą (porównanie z K8).
- [ ] **K2** (W2): Premię zmienia się bez przebudowy silnika.
  - Kroki: zmień w danych moda premię za trzeci cios broni jednoręcznej, przebuduj i zainstaluj
    tylko moda, powtórz K1.
  - Oczekiwane: zmienia się tylko obrażenie trzeciego ciosu, zgodnie z nową wartością.
- [ ] **K3** (W3): Ataki spoza combo nie dostają premii.
  - Kroki: P0, w cel testowy: seria ataków bocznych, atak z biegu, strzał z łuku, zaklęcie,
    a na końcu dobicie powalonego człowieka (`insert BDT_1013_Bandit_L`, powal go i dobij).
  - Oczekiwane: odczyt z W8 nie pokazuje premii ani kary dla żadnego z tych ataków, także dla
    kolejnych ataków bocznych w długiej serii lewo-prawo.
- [ ] **K4** (W5): Pełne combo mistrza daje najwięcej obrażeń na sekundę.
  - Kroki: P0, dla każdej broni (jednoręczna, dwuręczna) po 20 sekund nieprzerwanego ataku w cel testowy
    każdą techniką: pełne combo, powtarzanie pierwszego ciosu, lewo-prawo.
    Z odczytu W8 policz obrażenia na sekundę.
  - Oczekiwane: pełne combo ma wynik co najmniej o 20% wyższy od lepszej z dwóch pozostałych technik.
    Jeśli tak nie jest, wartości premii poprawiamy w danych moda i powtarzamy pomiar.
- [ ] **K5** (W4): Odporność i ochrona działają jak dotąd.
  - Kroki: P0, pełne combo w `insert MagicGolem` (odporny na ostrze i obuch), potem w cel z wysoką
    ochroną przed ostrzem `insert StoneGolem`.
  - Oczekiwane: MagicGolem nie traci punktów życia żadnym ciosem. Na StoneGolemie każdy kolejny cios
    zadaje obrażenia, jakie zadałby bez premii, pomnożone przez premię (W4). Jeśli wynik jest mniejszy
    niż minimum obrażeń, cios zadaje minimum, tak jak dziś.
- [ ] **K6** (W6): Zysk z combo rośnie z talentem.
  - Kroki: P0, ale w rozmowie z `ch` „Całkowity reset postaci” i broń jednoręczna do 10%.
    Zmierz obrażenia na sekundę jak w K4 dla pełnego combo, lewo-prawo i powtarzania pierwszego ciosu.
    Potem podnieś broń jednoręczną do 40% i powtórz pomiar.
  - Oczekiwane: względny zysk z pełnego combo nad lepszą z dwóch pozostałych technik jest u nowicjusza
    (10%) mniejszy niż u wojownika (40%), a u wojownika mniejszy niż u mistrza w K4.
- [ ] **K7** (W7): Premia dotyczy właściwych postaci.
  - Kroki: P0, `insert Pal_230_Ritter`, pozwól mu wyprowadzić combo w bohatera (`cheat god` chroni
    przed śmiercią) i sprawdź odczyt W8 dla jego ciosów.
  - Oczekiwane: kolejne ciosy combo paladyna dostają premię z tabeli dla NPC, mniejszą niż premia
    bohatera za ten sam cios w K1.
- [ ] **K8** (W9): Bez moda bez zmian.
  - Kroki: uruchom silnik z tej samej kompilacji bez moda (zwykły Gothic II: Noc Kruka), powtórz K1
    na dowolnym przeciwniku.
  - Oczekiwane: wszystkie ciosy combo zadają takie same obrażenia jak przed zmianą.
- [ ] **K9** (W10): Zapisy.
  - Kroki: wczytaj zapis z wersji 0.1.0. Potem zrób szybki zapis w środku combo, wczytaj go i od razu
    uderz.
  - Oczekiwane: oba zapisy się wczytują. Odczyt W8 dla pierwszego ciosu po wczytaniu pokazuje numer
    ciosu zgodny z animacją i premię zgodną z tym numerem.

## Wpływ na zapisy gry

Funkcja nie powinna dodawać nowego stanu zapisywanego w grze: numer ciosu w combo wynika z bieżącej
animacji, a ta jest już zapisywana. Zapisy z wersji 0.1.0 muszą się wczytać (K9). Jeśli plan wykaże,
że potrzebny jest nowy stan, dostanie on wersjonowany zapis zgodnie z konstytucją, zasada 4.

## Zasoby i prawa

Brak. Zmieniają się tylko zasady obrażeń i wartości w skryptach moda.

## Pytania otwarte

- [x] **P1:** Czy premia dotyczy też NPC? **Rozstrzygnięcie (2026-10-28):** tak, ale NPC mają osobno
  ustawianą, mniejszą premię. Opis w W2 i W7, kryterium K7.
- [x] **P2:** Co z atakami bocznymi? **Rozstrzygnięcie (2026-10-28):** bez premii i bez kary.
  Combo wygrywa wyłącznie premią, więc premie muszą być wysokie. Opis w W3, kryterium K3.
- [x] **P3:** W którym miejscu obliczenia działa premia? **Rozstrzygnięcie (2026-10-28):** po odjęciu
  ochrony i po osłabieniu słabego ciosu, przed zasadą obrażeń minimalnych. Opis w W4, kryterium K5.
- [x] **P4:** Jak duża ma być przewaga pełnego combo z W5? **Rozstrzygnięcie (2026-10-28):** co najmniej
  20%, wartości startowe premii bohatera 100/175/275/400%, korekta pomiarem. Opis w W5, kryterium K4.
- [x] **P5:** Czy premia zależy od talentu, czy tylko od numeru ciosu i rodzaju broni?
  **Rozstrzygnięcie (2026-10-28):** zależy od talentu: osobne tabele dla nowicjusza, wojownika
  i mistrza (pięści jedna tabela). Opis w W2 i W6, kryterium K6.
- [x] **P6:** Jakie techniki przerywania animacji gracze dziś stosują i które porównujemy w K4?
  **Rozstrzygnięcie (2026-10-28):** naprzemienne lewo-prawo i powtarzanie pierwszego ciosu.
  Przerywania blokiem i odskokiem nie porównujemy. Opis w W5, kryterium K4.
- [x] **P7:** Czy gracz ma dostać sygnał, że cios był mocniejszy (inny dźwięk, efekt trafienia)?
  **Rozstrzygnięcie (2026-10-28):** nie w tej specyfikacji. Jeśli tak, to jako osobna funkcja.

## Weryfikacja

<!-- Wypełniane po implementacji: kto, kiedy, na jakiej wersji, wynik dla każdego K. -->
