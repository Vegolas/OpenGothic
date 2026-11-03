# ADR 0007: Źródła i budowanie animacji moda

- **Status:** Przyjęta, punkt 3 zastąpiony przez [ADR 0008](0008-dokladanie-definicji-animacji-moda-przez.md) <!-- Proponowana / Przyjęta / Zastąpiona przez ADR NNNN / Odrzucona -->
- **Data:** 2026-11-03 (zaproponowana i przyjęta razem z planem 004)

## Kontekst

[Specyfikacja 004](../specs/004-potok-animacji/spec.md) wprowadza pierwsze animacje moda. Następne
funkcje będą z nich korzystać tak samo: styl walki bez broni, nowe animacje stania NPC, losowe
animacje bezczynności, zmiany w nakładkach stylów walki. Dlatego układ źródeł, formaty, narzędzia
i sposób włączania zachowań silnika zależnych od animacji ustalamy raz, dla wszystkich funkcji.

Ustalenia ze specyfikacji 004 (P1, P2, P6) i fakty:

- Silnik w trybie Gothic II szuka definicji modelu pod nazwą `<MODEL>.MSB`
  (`common/resources.cpp:672`). Biblioteka ZenKit rozpoznaje przy tym, czy treść jest binarna,
  czy tekstowa (`lib/ZenKit/src/ModelScript.cc:436-446`). Tekstowe definicje w składni Gothica
  (MDS) działają więc bez zmian w silniku.
- Klatki silnik czyta z `<MODEL>-<ANI>.MAN` (`common/graphics/mesh/animation.cpp:36`). Nazwa,
  warstwa, fps i liczba klatek pochodzą z nagłówka MAN (`animation.cpp:228-232`).
- W kopii gry właściciela są tekstowe źródła definicji z MDK Piranha Bytes
  (`_work/Data/Anims/HumanS.mds` i `mds_overlay/*.mds`).
- KrxImpExp eksportuje ASC, ale nie bezstratnie: w teście z 2026-11-02 pomijał klatki i interpolował
  krzywą Beziera, z błędem do 0,5° w pojedynczych klatkach. Prototyp z 2026-11-03 przenosił MAN do
  Blendera i z powrotem bajt w bajt.
- Konstytucja, zasada 6: bez oryginalnych plików gry w niezmienionej postaci. Zasada 10: każdy
  powtarzalny krok robi narzędzie z `tools/`.
- ADR 0003 każe włączać zmiany silnika opcjonalnymi symbolami skryptów.
- **Licencja MDK (sprawdzone 2026-11-03, zadanie Z4 planu 004).** Źródło: umowa licencyjna MDK
  `G2MDK-EULA.rtf` (© 2004 Pluto 13 GmbH / Piranha Bytes), sekcje „Lizensierung der Daten/Software”
  i „Ausnahmen”, w kopii instalatora MDK na
  [github.com/dzieje-khorinis/Gothic-2-Mod-Development-Kit](https://github.com/dzieje-khorinis/Gothic-2-Mod-Development-Kit).
  Umowa dzieli dane tak:
  - na licencji GothicMOD są dane nowo utworzone narzędziami Gothica II oraz skrypty
    z `/_work/data/Scripts`;
  - `/_work/tools` i `/_work/demo` mają licencję w stylu BSD;
  - wszystkie inne dane zainstalowane, rozpakowane i przekonwertowane przez instalator podlegają
    umowie licencyjnej samej gry, która daje prawo osobistego użytku przy legalnej instalacji gry,
    bez prawa rozpowszechniania.

  Definicje animacji z MDK (`_work/Data/Anims/*.mds`) i oryginalne animacje z archiwów gry nie są
  więc objęte GothicMOD. Punkt 3 decyzji w pierwotnej postaci (pełne definicje z MDK w paczce moda)
  jest nieważny, zob. „Konsekwencje”.

## Opcje

Źródło animacji:

1. **Plik Blendera i bezstratny eksport tekstowy.** Plik Blendera do edycji, tekst klatka po klatce
   jako źródło buildu. Build bez Blendera, czytelny diff. Wady: dwie postacie tego samego, trzeba
   pilnować ich zgodności.
2. **Tylko plik Blendera.** Najprościej, ale bez diffu, a build wymaga Blendera.
3. **ASC z KrxImpExp.** Znany format, ale stratny i bez sceny Blendera.

Definicje animacji:

1. **Pełne tekstowe definicje z MDK, zmienione przez moda**, pod nazwą wersji skompilowanej. Silnik
   bez zmian. Wady: duży plik tekstowy w repozytorium, warunek licencji GothicMOD dla MDK.
2. **Własna nakładka z samymi animacjami moda.** Wady: nakładkę musi dostać każda postać, także
   w starych zapisach.
3. **Silnik dokłada definicje moda do oryginalnych.** Wady: zmiana w silniku i własna składnia
   łączenia.
4. **Własny zapis skompilowanego MSB.** Wady: nowy format do napisania, a w paczce lądują oryginalne
   definicje.

Narzędzia:

1. **Przypięte wersje pobierane narzędziem** (jak kompilator skryptów w ADR 0001).
2. **Ręczna instalacja dodatku w profilu Blendera.**

Zachowania silnika zależne od animacji (np. ataki boczne pięściami):

1. **Włącza je sama animacja w modelu.** Bez animacji (oryginalna gra, inne mody) silnik działa jak
   upstream.
2. **Osobny symbol skryptu według ADR 0003.** Wady: konfiguracja jednej funkcji w dwóch miejscach,
   a animacja bez symbolu albo symbol bez animacji nic nie znaczą.

## Decyzja

Przyjęta razem z planem 004. Punkt 3 zależy od licencji MDK, którą sprawdza zadanie Z4 planu 004:

1. **Układ.** Źródła animacji leżą w `gothic25/anims/<MODEL>/`, poza `content/`, więc nie trafiają
   do paczki. Wynik buildu trafia do `gothic25/build/anims/_COMPILED/`, a `tools/pack.ps1` pakuje go
   pod `_WORK/DATA/ANIMS/_COMPILED/`. Lista modeli, odbić lustrzanych i nazw docelowych jest
   w `gothic25/anims/anims.json`.
2. **Źródło animacji:** opcja 1.
   - Plik `<ANI>.blend` zawiera tylko szkielet i akcje, bez siatek z gry. Ciało narzędzie dokłada
     lokalnie z kopii gry przy otwieraniu.
   - Plik `<ANI>.anim` to tekst UTF-8 z nagłówkiem (model, fps, checksum szkieletu, lista węzłów,
     opcjonalnie kwantyzacja i metadane źródła oryginału) i jedną linią na węzeł w każdej klatce:
     kwaternion `w x y z` i pozycja w centymetrach, ze stałą liczbą miejsc po przecinku.
   - MAN buduje z niego `tools/anim.py build`, bez Blendera.
3. **Definicje (zastąpione przez ADR 0008, bo licencja MDK nie pozwala ich rozpowszechniać):**
   opcja 1. Mod trzyma pełne tekstowe definicje z MDK tylko dla modeli i nakładek,
   które zmienia, w kodowaniu i końcach linii oryginału (cp1252, CRLF). Build zapisuje je pod nazwą
   `<MODEL>.MSB`. Zmienione definicje z MDK rozpowszechniamy na licencji GothicMOD i wymieniamy
   w `NOTICE.txt`. Zanim definicje z MDK zastąpią oryginał, porównujemy je z grą
   (`tools/anim.py mdk-diff`).
4. **Narzędzia:** opcja 1.
   - Ścieżka do Blendera jest w `local.json` (`blender`).
   - Commit KrxImpExp jest przypięty w `tools/lib/common.ps1`. `tools/get-krx.ps1` pobiera go
     przez git do `.tools/blender-scripts/addons/krximpexp/` i sprawdza SHA-256 plików.
   - Blender działa z `BLENDER_USER_SCRIPTS` wskazującym na ten katalog, z `--background
     --factory-startup --python-exit-code 1`. Dodatek jest włączany jawnie w skrypcie, bo samo
     `--addons` przy `--factory-startup` nie dodaje go do preferencji.
5. **Zachowania zależne od animacji:** opcja 1, jako uzupełnienie ADR 0003. Zmiana silnika, która
   tylko korzysta z animacji, jeśli model ją ma, nie dostaje symbolu skryptu. Plan funkcji dowodzi, że
   oryginalne modele G1 i G2 takiej animacji nie mają. Listę takich animacji prowadzi
   `gothic25/anims/README.md`.

## Konsekwencje

- Animację da się zbudować i przetestować bez Blendera (CI, inny komputer). Blender jest potrzebny
  tylko do edycji, importu oryginałów i sprawdzenia zgodności `.blend` z `.anim`.
- Kolejne funkcje dopisują definicje do tych samych plików moda, więc mogą wchodzić sobie
  w konflikty. Zmiany grupujemy w blokach oznaczonych numerem specyfikacji.
- Zachowania zależne od animacji zadziałają tylko na nowym silniku.
- MDK okazało się nieobjęte licencją GothicMOD (Z4). Punkt 3 zastępuje
  [ADR 0008](0008-dokladanie-definicji-animacji-moda-przez.md): silnik dokłada definicje moda do
  oryginalnych, a w paczce są tylko animacje i definicje moda.
