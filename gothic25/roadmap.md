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

## Pomysły przemyślane

Pomysły spoza głównych celów, przemyślane na tyle, że można dla nich założyć specyfikację
(`/g25-specify`).

### Idealne parowanie z ogłuszeniem

- **Warstwa:** silnik (wykrycie idealnego parowania, przerwanie ataku, ogłuszenie, kara za pusty
  blok, jedna funkcja dla skryptów) i skrypty (wartości, odporności, dźwięk). Bez nowych animacji.
- **Cel:** blok staje się agresywnym odpowiednikiem odskoku. Odskok jest bezpieczny i daje dystans.
  Parowanie wymaga wyczucia rytmu przeciwnika, a w nagrodę przerywa jego atak i daje okno na kontrę.
- Omówione 2026-10-28 i 2026-10-29.

**Stan obecny w OpenGothic**

- Odskok w trybie broni (`T_1HJUMPB`, `T_2HJUMPB`) dostaje stan `BS_PARADE`, a w danych nie ma
  okna `DEF_WINDOW`, więc chroni przez całą animację: 520 ms dla 1H i 920 ms dla 2H
  (`Pose::isJumpBack`). Animacje `T_*PARADEJUMPB`, które mają okno, silnik używa tylko dla pięści.
- Blok trwa 560 ms, chroni w 0–480 ms i nie da się go przerwać. Udany blok niczego nie daje:
  atakujący kontynuuje kombinację.
- Warunek odskoku w `Npc::takeDamage` obejmuje też blok w jego oknie, więc blok chroni również
  przed potworami. Osobny wyjątek dla potworów bez broni niczego nie zmienia.
- Zdarzenie `DEF_PAR_FRAME` silnik wczytuje (`Pose::isDefParWindow`), ale nie używa,
  a w `Humans.mds` Gothic II ono nie występuje.

**Czasy animacji Gothic II**

Czas od startu ataku do uderzenia (`DEF_OPT_FRAME`), w ms:

| Atak | Bez szkolenia | Wojownik | Mistrz |
|---|---|---|---|
| 1H z przodu | 240 | 120 | 120 |
| 1H z boku | 200 | 160 | 120 |
| 2H z przodu | 320 | 200 | 160 |
| 2H z boku | 240 | 200 | 200 |

Zachwianie po trafieniu (`T_STUMBLE`, `T_STUMBLEB`) trwa 320 ms. Źródła: `HumanS.mds`
zdekompilowany z `Humans.msb` (github.com/the-overdriven/G2-anims-humans-fixer) i tabele czasów
nakładek 1H/2H (github.com/Sumpfkraut-Online/SumpfkrautOnline-Khorinis, `AnimationFiles`).
Oba źródła zgadzają się dla wartości podstawowych. Nie sprawdzaliśmy ich z własną kopią gry.

**Zasady**

- Idealne parowanie zachodzi, gdy cios trafia w blok, który trwa krócej niż okno parowania.
  Okno liczymy wstecz od uderzenia, a nie od startu ataku. Na ciosy mistrzów (120 ms) nie da się
  zareagować, trzeba czytać rytm przeciwnika. Na słabszych przeciwników da się zareagować, więc
  trudność rośnie razem z ich wyszkoleniem.
- Skutek: atak przeciwnika zostaje przerwany, gracz nie dostaje obrażeń, a przeciwnik zostaje
  odepchnięty (`T_STUMBLEB`) i ogłuszony. Ogłuszenie to zachwianie plus wstrzymanie AI walki:
  w tym czasie NPC nie blokuje, nie odskakuje i nie atakuje.
- Ogłuszenie trwa około 600 ms. Kontra gracza ląduje 320–570 ms po parowaniu (reakcja 200–250 ms
  plus zamach bohatera 120–320 ms). Samo zachwianie (320 ms) nie wystarcza, bo zaraz po nim mistrz
  blokuje nadchodzący cios.
- Kontra daje jeden pewny cios. Trafienie ogłuszonego działa jak zwykłe trafienie (kończy
  wstrzymanie, daje zwykłe zachwianie), więc dalej toczy się normalna wymiana z inicjatywą po
  stronie gracza. Nie ma pętli „parowanie, pełna seria”.
- Kara za pusty blok: blok, w który nic nie trafiło, kończy się przerwą około 250 ms, w której nie
  można ponownie blokować. Bez kary ciągłe trzymanie bloku dawałoby przy oknie 150 ms idealne
  parowanie przy około 27% ciosów przeciwnika, a gracz byłby odsłonięty tylko przez około 14%
  czasu. Z karą odsłonięcie rośnie do około 40%, więc spam przestaje się opłacać.
- Cios, który trafia w blok poza oknem parowania, jest zwykłym blokiem, tak jak dziś.
- Odporni na ogłuszenie są NPC z `bodyStateInterruptableOverride`: trolle, smoki, golemy, kamienni
  strażnicy, poszukiwacze i bohater. Dla nich idealne parowanie działa jak zwykły blok.
- Na początek idealnie paruje tylko gracz. AI reaguje na atak gracza od jego pierwszej klatki
  (mistrz blokuje w 100%), więc symetryczna zasada przerywałaby każdy cios gracza.

**Podział silnik / skrypty**

- Silnik w `Npc::takeDamage` mierzy, jak długo trwa blok w chwili uderzenia, i wywołuje opcjonalną
  funkcję skryptową (robocza nazwa `G25_OnParry(obrońca, atakujący, czasBloku)`), która zwraca
  długość ogłuszenia, a 0 oznacza zwykły blok. Silnik przerywa atak (`Pose::interrupt`), gra
  zachwianie, wstrzymuje AI walki (`implFaiWait`) i nakłada karę za pusty blok.
- Skrypty ustalają okno parowania zależne od talentu 1H/2H, odporności, długość ogłuszenia
  i osobny dźwięk idealnego parowania, różny od `D_PARADE`.
- Działa pod flagą moda, domyślnie wyłączoną. Nie dodaje nowego stanu do zapisu gry.

**Wartości startowe do strojenia w grze**

| Parametr | Wartość |
|---|---|
| Okno parowania | 80 / 120 / 160 ms (bez szkolenia / wojownik / mistrz) |
| Ogłuszenie | 600 ms |
| Przerwa po pustym bloku | 250 ms |

**Otwarte**

- Czasy ataków potworów (wilk, ork, zębacz): czy idealne parowanie ma sens przeciw zwierzętom.
- Zachowanie oryginału: czy da się blokować potwory i czy zablokowany atakujący coś traci.
- Czy osłabić odskok (ochrona tylko na początku albo chwila bezbronności na końcu), żeby blok był
  realnym wyborem także przeciw potworom.
- Docelowo osobna animacja odrzutu (około 600 ms) zamiast zachwiania i postoju. Zależy od ADR
  o narzędziach do animacji. Spowolnienie zachwiania przez nakładkę MDS odpada, bo wymagałoby
  kopii oryginalnego `.MAN` (konstytucja, zasada 6).

### Oświetlenie materiałów (PBR)

- **Warstwa:** silnik (shadery oświetlenia, G-buffer, wczytywanie tekstur). Same zasoby nie
  wystarczą, bo w silniku nie ma członu odbić (specular).
- **Cel:** metal, mokry kamień i woda połyskują w świetle słońca i pochodni, a materiały różnią się
  nie tylko kolorem tekstury.
- Omówione 2026-10-29. Szacunki czasu są zgrubne i zakładają osobę znającą Vulkan i GLSL.

**Stan obecny w OpenGothic**

- Oświetlenie to sam Lambert: słońce w `shader/lighting/direct_light.frag`, światła punktowe
  w `shader/lighting/light.frag`, otoczenie w `shader/lighting/ambient_light.frag`. Ten sam model
  powtarza się w wariantach VSM i RTSM oraz w GI, łącznie w około 8 shaderach.
- G-buffer ma kolor (RGBA8) i normalną (R32U, kodowanie oktaedryczne). Alfa koloru niesie 3 bity
  flag (`encodeHintBits` w `shader/materials/main.frag`), więc 5 bitów jest wolnych.
- Otoczenie to tablica irradiancji 3×2 texele, czyli tylko światło rozproszone. Nie ma cubemap
  ani sond odbić, a odbicia w przestrzeni ekranu (SSR) ma tylko woda.
- ZenGin daje grupę materiału (`zenkit::MaterialGroup`: METAL, STONE, WOOD, EARTH, WATER, SNOW).
  Silnik używa jej dziś do fizyki i dźwięku kroków. `DrawBuckets::BucketGpu` ma wolne pole `padd[1]`.
- Siatki nie mają wektorów stycznych.

**Etapy**

- **A. Odbicia z grupy materiału (około 1–2 tygodni).** Grupa materiału trafia do wolnych bitów
  alfy G-buffera, a światło bezpośrednie dostaje człon GGX z tabelą roughness i F0 dla każdej grupy.
  Bez nowych tekstur. Daje odblaski od słońca i świateł oraz mokre powierzchnie w deszczu.
  To zarazem spike: sprawdza, czy odblaski pasują do malowanego stylu Gothica.
- **B. Opcjonalne mapy obok tekstur (około 2–4 tygodni).** Normal mapa i mapa roughness/metallic
  są wczytywane, gdy istnieją, a bez nich działa etap A. Wymaga drugiego zestawu tekstur w ścieżce
  bindless i zwykłej (`DrawCommands`), nowego załącznika G-buffera (RG8) i stycznych liczonych
  z pochodnych ekranowych. Wygenerowane TGA nie są kompresowane jak `.TEX` (DXT), więc rośnie
  zużycie VRAM.
- **C. Odbicia otoczenia (od tygodni do miesięcy).** Dopiero ten etap sprawia, że metal w cieniu
  i we wnętrzach nie jest czarny. Bez niego etapy A i B dają odblaski, a nie PBR. Zależy od GI v2.
- Materiały przezroczyste (ścieżka forward w `shader/materials/main.frag`) zostają przy Lambercie.

**Zależność etapu C od GI v2**

- GI v2 (Try/OpenGothic#945, `-gi 2`) to pamięć podręczna irradiancji w punktach (surfele). Punkt
  przechowuje samo `vec3 irradiance` (`shader/lighting/surfels/surf_common.glsl`), bez kierunku,
  więc GI v2 nie daje odbić połyskliwych.
- Daje za to infrastrukturę: promienie przez RayQuery i odczyt albedo w miejscu trafienia
  (`surf_pathtrace.comp`). Odbicie z RT to promień z piksela, a w miejscu trafienia albedo, słońce
  z promieniem cienia i światło pośrednie z pamięci GI.
- Odbicia chropowatych materiałów (kamień, drewno, skóra) można przybliżyć lokalną irradiancją
  z GI zamiast nieba, więc niebo nie prześwieca w jaskiniach. Gładki metal nadal wymaga prawdziwych
  odbić.
- Punkty powstają z G-buffera, więc istnieją tylko dla widocznych powierzchni. Promień odbicia,
  który trafia poza ekran, nie ma skąd odczytać światła. Zgłoszenie wymienia pamięć w przestrzeni
  świata jako nierozwiązany element (pomysł: klucz `(instanceID, primitiveID)`). Od niej zależy,
  czy etap C zajmie tygodnie, czy miesiące.
- Stan na 2026-10-29: GI v2 nie jest domyślne, brakuje wielokrotnych odbić światła (ciemne domy
  i jaskinie), a shadery surfeli wymagają sprzętowego RT (`RAY_QUERY` włączone bezwarunkowo).
  Try chce nim zastąpić `-gi 1` po poprawie wydajności i jakości.
- Etapu C nie zaczynamy przed ustabilizowaniem GI v2. Bez RT etap C kończy się na niebie i SSAO.

**Tekstury**

- Normal mapy da się w dużej części wygenerować skryptem (wysokość z jasności), ale nie z tekstur
  z namalowanym światłem (fałdy ubrań, twarze), bo wychodzi podwójne cieniowanie. Przy 256–512 px
  w DXT1 skrypt wzmacnia artefakty kompresji. Potrzebne są reguły dla klas tekstur i lista wykluczeń.
- Roughness nie wynika z jasności piksela. Etap A bierze ją z grupy materiału.
- Metallic nie da się wygenerować mechanicznie. Tekstury zbroi i broni to atlasy, w których skóra,
  materiał i blacha leżą na jednym arkuszu, więc potrzebna jest maska per piksel: ręcznie albo
  segmentacją ML z przeglądem.
- Tekstury Gothica mają wypalone AO i rozbłyski, które przy odbiciach, SSAO i GI liczą się
  podwójnie. Usunięcie wypalonego światła (de-lighting) nie jest skryptem i zmienia styl gry.
- Przed etapem B obejrzeć paczki normal map do renderera GD3D11 dla oryginalnego Gothica: jak
  powstały i jak wyglądają.

**Zgodność z konstytucją**

- Zasada 3 to największe ryzyko. Od początku 2025 roku 103 commity zmieniły `shader/`, w tym 17
  główne pliki oświetlenia i materiałów (`main.frag`, `direct_light.frag`, `light.frag`,
  `ambient_light.frag`, `common.glsl`). Mechanizm jest ogólny, więc przed specyfikacją pytamy Try,
  czy przyjąłby go do upstreamu. Działa pod ustawieniem grafiki, domyślnie wyłączonym.
- Zasada 6: mapy wygenerowane z oryginalnych tekstur to dzieła pochodne. Generujemy je u gracza
  (instalator albo silnik przy wczytywaniu) i ich nie dystrybuujemy. Dzięki temu nie zależymy też
  od ADR 0002.

**Otwarte**

- Jak gęsto grupy materiałów są ustawione w danych Nocy Kruka. Na siatce świata raczej tak (dźwięki
  kroków), na obiektach i zbrojach prawdopodobnie głównie UNDEFINED. Do zmierzenia na komputerze
  z grą przed specyfikacją etapu A.
- Pytanie do Try w Try/OpenGothic#945: czy pamięć GI w przestrzeni świata będzie dostępna
  w dowolnym punkcie trafienia, także dla promieni odbić.
- Czy GI ma uwzględniać metallic (`base*(1-metallic)` w odbiciu rozproszonym). Odczyt trafień
  nie zna dziś parametrów materiału.
- Konwencja nazw map leżących obok tekstury.

## Pomysły do dyskusji

Luźne pomysły na zróżnicowanie rozgrywki, omówione 2026-10-28 pod kątem możliwości silnika.
To nie są planowane funkcje: najpierw trzeba rozstrzygnąć, czy pasują do ducha oryginału.

- Wszystkie trzy wymagają nowych animacji, a silnik czyta tylko skompilowane pliki `.MAN`
  (`Animation::Animation` w `common/graphics/mesh/animation.cpp`). Przed specyfikacją któregoś
  z nich potrzebny jest ADR o narzędziach do animacji.
- Wszystkie sięgają do silnika (sterowanie, cykl rzucania, okno uniku), więc działają pod flagą
  moda, domyślnie wyłączoną.

### Szybkie zaklęcie z bronią w ręku (paladyn, mag z kosturem)

- **Warstwa:** zasoby (animacje górnej części ciała), silnik (nowa ścieżka rzucania), skrypty
  (które zaklęcia, koszt).
- Silnik zna jeden stan broni naraz (`MdlVisual::fgtMode`), a `Npc::drawSpell` chowa broń.
  Zamiast nowego stanu broni: osobna akcja w trybie 1H/2H, która gra animację na wyższej warstwie
  (`Pose` miesza warstwy osobno dla każdej kości) i odpala zaklęcie bez zmiany broni.
- Do zmiany w silniku: punkt startu pocisku (dziś `ZS_RIGHTHAND` tylko w trybie magii,
  `MdlVisual::mapWeaponBone`), odpalenie bez powrotu do animacji spoczynku (`Npc::tickCast`)
  i stan ciała (`Pose::bodyState` bierze maksimum z warstw, a `BS_CASTING` blokuje ruch).
- Runy paladyna używają 4 schematów animacji (SLE, HEA, FBT, FIB): około 4 animacji dla 1H
  i 4 dla 2H.
- Kostur jest bronią 2H, więc wariant 2H obsługuje też maga z kosturem. Pełny zestaw animacji
  magii z kosturem (12 schematów) odrzuciliśmy jako za drogi.
- Balans: czas przełączania broni to w Gothicu celowy koszt. Propozycja: tylko w miejscu,
  przerywane trafieniem, listę dozwolonych zaklęć ustalają skrypty.

### Premia do obrażeń zaklęć za kostur

- **Warstwa:** silnik (punkt wpięcia), skrypty (lista kosturów, wartość premii).
- Obrażenia zaklęć liczy silnik w `Npc::commitSpell` (pociski) i `Npc::takeDamage` (pozostałe
  zaklęcia). Skrypty nie mają tu punktu wpięcia, więc potrzebna jest opcjonalna funkcja skryptowa
  modyfikująca obrażenia.
- Kostury to zwykłe `ITEM_2HD_AXE` bez wyróżniającej flagi (`Items/IT_Addon_Weapons.d`),
  a w Nocy Kruka jest ich tylko kilka. Potrzebna też treść: nowe kostury i handlarze.

### Unik lub przewrót (akrobatyka)

- **Warstwa:** zasoby (animacje), silnik (klawisz, okno uniku), skrypty (kto może się nauczyć).
- W Nocy Kruka akrobatyki nikt nie uczy: dostaje ją każdy przy zręczności 90
  (`B_Story/B_RaiseAttribute.d`). Powiązanie z najemnikiem i łowcą smoków zmienia tę zasadę,
  więc raczej poziom 2 talentu albo osobny talent.
- Dzisiejszy unik (odskok, `Pose::isJumpBack`) chroni tylko przed ciosami wręcz z przodu.
  Przewrót w bok wymaga nowego okna uniku, najlepiej zapisanego w danych animacji (`DEF_WINDOW`).
- Skrypty nie odczytują klawiatury, więc nowa akcja to zmiana w `PlayerControl`.
- Główne ryzyko: Gothic nie ma staminy, więc przewrót z nietykalnością da się spamować.
  Ostrożniejszy wariant: krótki unik w bok bez nietykalności albo z krótkim oknem i chwilą
  bezbronności na końcu. Najpierw prototyp na istniejących animacjach odskoku.
