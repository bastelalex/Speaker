# Speaker · Waveguide-Werkstatt

Deutschsprachige Fachunterlagen und Offline-Konfigurator für Horn-Waveguides, Raketen-/Axtkopf-Phaseplugs, Multicell, Polycell/Polyhorn und Kompressionskammern. Mit recherchierten LaVoce- und JBL-Treiberdaten und GitHub-Werkzeugquellen.

## Direkt zu den Ergebnissen

- **[Fachbroschüre · 30 Seiten als PDF](docs/fachbroschuere.pdf)** · [HTML](docs/fachbroschuere.html) · [Markdown](docs/fachbroschuere.md)
- **[3D-Designkatalog · 12 Konzepte als PDF](docs/designkatalog.pdf)** · [HTML mit drehbarer 3D-Ansicht](docs/designkatalog.html) · [Markdown mit Renderings](docs/designkatalog.md)
- **[3D-Modellbibliothek · STL und OBJ](models/README.md)** – einschließlich runder, ovaler und prismatischer Profile. Die STL-Dateien lassen sich direkt in GitHub als 3D-Modell ansehen.
- **[Konfigurator herunterladen](https://raw.githubusercontent.com/bastelalex/Speaker/main/configurator/index.html)**: Link speichern und die gespeicherte HTML-Datei im Browser öffnen. Alternativ das Repository als ZIP herunterladen und `configurator/index.html` öffnen. Die GitHub-Dateivorschau führt JavaScript nicht aus.
- [Quellenregister mit Zugriffshinweisen](docs/quellen.md) · [strukturierte Treiberdaten](data/drivers.json)
- **[Theoretische Validierung und erste Simulationen](validation/REPORT.md)** · [HTML-Bericht mit Diagrammen](validation/report.html) · [Ergebnisdaten](validation/results.json)

## Erste LaVoce-Simulationskampagne

Alle zwölf vorhandenen Konzepte wurden anhand der exportierten Netze auf freie Querschnitte, Anschlussflächen und Kanalwege geprüft. Ein verlustfreies 1D-Lastmodell untersucht die vorhandenen Kanäle. Für das runde OS-Profil, den Rundkonus und den Raketen-Ringkanal wurden zusätzlich axialsymmetrische FEM-Schallfelder und Richtdiagramme bei 1,2, 2, 4 und 8 kHz gerechnet; beim Ringkanal mit DN20.30TK-Hals kommt 800 Hz hinzu. Hersteller-Hochpässe und der genaue 2,83-V-Bezug der LaVoce-Empfindlichkeiten wurden aus den aktuellen Datenblättern ergänzt.

Die Quelle ist eine idealisierte, gleichphasige Halsgeschwindigkeit, kein vollständiges elektromechanisches LaVoce-Modell. Es gibt keine Aussage zu maximalem SPL, Klirr oder thermischer Belastbarkeit. Der FEM-Außenraum nimmt eine unendliche Mund-Schallwand an. Das OS-Profil besteht die dokumentierten numerischen Gegenprüfungen an den untersuchten Stützfrequenzen; die 8-kHz-Strahlbreite des Konus ist noch nicht konvergiert.

Die Prüfung findet konkrete Konstruktionsprobleme: fehlende Verteiler/Adapter, ungleiche Zellwege und eine stark zu grob vernetzte Schlitzmündung. Der [Bericht](validation/REPORT.md) zeigt Befunde, gescheiterte Kriterien und die nächsten Revisionen. Die Katalogeinträge tragen den jeweiligen Prüfstand. Keine der zwölf Formen besitzt damit eine Produktfreigabe.

## Was der Rechner berechnet

Eingaben: volle horizontale und vertikale Abstrahlwinkel, untere/obere Bandgrenze, Treiber und Designfamilie; bei Multicell/Polycell außerdem ein Zellraster.

Ausgaben: Apertur-Startmaße bei −6 dB, Halsfläche, geradlinige Referenzhülle, tatsächliche Wandwinkel, Laufwegbudget, idealisierter Abstands-/Querformcheck und Bandvorauswahl. Entwürfe lassen sich als JSON und eine Frontskizze als SVG exportieren. Ein separater Lernrechner berechnet die ideale Helmholtz-Resonanz aus Kammerinhalt, Halsfläche und effektiver Halslänge.

**Es handelt sich um Vorbemessung.** Innenkonturen für Raketen, Axtköpfe, Verteiler und Polycell sind Konzeptstudien, keine fertig konstruierten oder gemessenen Produkte. Die gleiche Referenzhülle ist kein Beweis für gleiche akustische Eigenschaften. Die neuen STL-/OBJ-Dateien sind eigene illustrative Geometrien und keine fertigungsfreigegebenen Produkte oder originalen Turbosound-CAD-Daten.

## 3D-Katalog, Ausgabe 2.0

Zwölf Konzepte: Einzel-Waveguide, Raketen-Ringkanal, Axtkopf-Zweikanal, Multicell, Polycell und Mehrtreiber-Manifold sowie Rundkonus, rundes OS-Profil, Ellipse, Superellipse, prismatischer Rechteck-Waveformer und Rund-auf-Schlitz-Waveformer. Jede Form besitzt einen STL-/OBJ-Export, ein SVG-Rendering und eine PDF-Katalogseite. Alle Renderings entstehen aus den exportierten Netzen.

Für die drehbare Offline-Ansicht das **gesamte Repository als ZIP** herunterladen und entpacken, dann `docs/designkatalog.html` öffnen. Die HTML-Datei lädt `catalog-viewer.js`, die Meshbibliothek und die Renderings aus benachbarten Verzeichnissen. Drehen, Front-/Seitenansicht, Zoom, Halbschnitt und STL-Export erfolgen lokal. Der Konfigurator behält seine sechs bisherigen Rechenfamilien; die zusätzlichen Katalogformen sind keine bereits integrierten akustischen Rechenmodelle.

## Datenstand und Beleglage

Recherche: **12.11.2026**. Treiber: LaVoce DN10.20-16, DN20.30TK; JBL 2426H, 2446H. Herstellerangaben, Modellannahmen und eigene Entwürfe bleiben getrennt. Beim 2446H gilt im Rechner eine ausdrücklich eigene Projekt-Untergrenze von 800 Hz. AES- und Program-Leistung werden nicht gleichgesetzt. Nicht verfügbare interne Kammermaße werden nicht erfunden.

GitHub-Referenz: [Waveguide_PSO, geprüfter Commit](https://github.com/rafaelst00/Waveguide_PSO/tree/baefd510603ce75612bbed62191f5786c170c6b1). Ergänzend Bempp und Gmsh als weiterführende Werkzeuge, siehe Quellenregister. Kein fremder Programmcode übernommen; die neue Kampagne verwendet eigene NumPy-/SciPy-Solver. Keine Waveguide_PSO-, ABEC-, AKABAK- oder COMSOL-Läufe durchgeführt.

## Reproduzieren und prüfen

Benötigt werden Python 3 und Node.js ≥20. Für Build und Rechentests sind keine zusätzlichen Pakete nötig.

```sh
python scripts/build.py
python tests/catalog_models_test.py
node tests/core.test.mjs
```

Die Broschüreninhalte stehen in `data/pages.json`, die Katalogparameter in `data/catalog.json`, die Quellen in `data/sources.json`. `scripts/build.py` erzeugt PDF-, HTML- und Markdown-Ausgaben, 3D-Modelle und Renderings sowie den vollständig eingebetteten Offline-Konfigurator. `scripts/catalog_models.py` enthält die eigenen parametrischen Modellgeneratoren. `configurator/core.mjs` enthält die Rechenformeln, `app.mjs` die Oberfläche und `template.html` das Layout. Nach Änderungen den Build ausführen; erzeugte Dateien mit ablegen.

Die PDFs besitzen bewusst einfache Standardschriften und ASCII-kodierte Datenströme. Griechische Formelzeichen werden in der PDF-Ausgabe ausgeschrieben; HTML und Markdown behalten die Zeichen.

Für die akustische Kampagne kommen NumPy, SciPy und Matplotlib hinzu; die getesteten Versionen stehen in `validation/requirements.txt`. Der Dokumenten- und Modellbuild selbst benötigt diese Pakete weiterhin nicht.

```sh
python -m pip install -r validation/requirements.txt
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/speaker-mpl python validation/run.py
python tests/acoustics_test.py
python scripts/build.py
```

Die Simulation erzeugt Bericht, CSV-Rohdaten, Parameter-/Versionsmanifest und SVG-Plots. Die HTML-Katalogansicht und das PDF übernehmen danach den numerischen Prüfstand aus `validation/results.json`. Die ursprünglichen STL-/OBJ-Konturen bleiben für die dokumentierte Untersuchung erhalten; bekannte Geometriefehler werden nicht stillschweigend ersetzt.

## Validierung

Sechs Rechentests und fünf Geometrie-/Exporttests bestanden. Die Modellprüfungen behandeln alle zwölf Netze: geschlossene Materialkörper, gerichtete Flächenkanten, nicht entartete Dreiecke, positive Komponenten-Volumina, reproduzierbare Exporte und getrennte Zellöffnungen. PDF-Seitenzahl: 30 + 12; Katalog-Renderings visuell geprüft. Das beweist keine Kollisionsfreiheit, Druckbarkeit oder akustische Funktion.

Zusätzlich bestehen sieben akustische Referenztests: angepasster Zylinderkanal, niederfrequenter Kolbenstrahler, Leistungsidentität der Transfermatrix, analytisches Rayleigh-/Bessel-Richtdiagramm, FEM-Netzqualität und FEM-Kolbenstrahler gegen analytische Impedanz und korrekt ausgespartem Ringkanal-Innenkörper. Die Simulationskampagne enthält Netz- und Außenraumgegenprüfungen, die eine fehlgeschlagene Konvergenz ausdrücklich offen lassen.

Browserprüfung mit installiertem Chromium/Playwright versucht, aber der Browserstart wurde durch die Ausführungs-Sandbox blockiert (`setsockopt` / `shutdown: Operation not permitted`). Die JavaScript-Syntax ist geprüft; die tatsächliche Browserinteraktion blieb ungeprüft. Keine Prototypmessung und keine vollständige 3D-/Elektromechanik-Simulation.

Unabhängiges Entwicklungsprojekt; keine Herstellerfreigabe oder Originalteil-Kompatibilitätszusage. Die Rechte an Herstellerunterlagen und Markennamen verbleiben bei deren Inhabern.
