# Speaker · Waveguide-Werkstatt

Deutschsprachige Fachunterlagen und Offline-Konfigurator für Horn-Waveguides, Raketen-/Axtkopf-Phaseplugs, Multicell, Polycell/Polyhorn und Kompressionskammern. Mit recherchierten LaVoce- und JBL-Treiberdaten und GitHub-Werkzeugquellen.

## Direkt zu den Ergebnissen

- **[Fachbroschüre · 30 Seiten als PDF](docs/fachbroschuere.pdf)** · [HTML](docs/fachbroschuere.html) · [Markdown](docs/fachbroschuere.md)
- **[Designkatalog · 6 Familien als PDF](docs/designkatalog.pdf)** · [illustrierte HTML-Ausgabe](docs/designkatalog.html) · [Markdown](docs/designkatalog.md)
- **[Konfigurator herunterladen](https://raw.githubusercontent.com/bastelalex/Speaker/main/configurator/index.html)**: Link speichern und die gespeicherte HTML-Datei im Browser öffnen. Alternativ das Repository als ZIP herunterladen und `configurator/index.html` öffnen. Die GitHub-Dateivorschau führt JavaScript nicht aus.
- [Quellenregister mit Zugriffshinweisen](docs/quellen.md) · [strukturierte Treiberdaten](data/drivers.json)

## Was der Rechner berechnet

Eingaben: volle horizontale und vertikale Abstrahlwinkel, untere/obere Bandgrenze, Treiber und Designfamilie; bei Multicell/Polycell außerdem ein Zellraster.

Ausgaben: Apertur-Startmaße bei −6 dB, Halsfläche, geradlinige Referenzhülle, tatsächliche Wandwinkel, Laufwegbudget, idealisierter Abstands-/Querformcheck und Bandvorauswahl. Entwürfe lassen sich als JSON und eine Frontskizze als SVG exportieren. Ein separater Lernrechner berechnet die ideale Helmholtz-Resonanz aus Kammerinhalt, Halsfläche und effektiver Halslänge.

**Es handelt sich um Vorbemessung.** Innenkonturen für Raketen, Axtköpfe, Verteiler und Polycell sind Konzeptstudien, keine fertig konstruierten oder gemessenen Produkte. Die gleiche Referenzhülle ist kein Beweis für gleiche akustische Eigenschaften. Keine STL-Fertigungsvorlagen oder originalen Turbosound-CAD-Daten enthalten.

## Datenstand und Beleglage

Recherche: **12.11.2026**. Treiber: LaVoce DN10.20-16, DN20.30TK; JBL 2426H, 2446H. Herstellerangaben, Modellannahmen und eigene Entwürfe bleiben getrennt. Beim 2446H gilt im Rechner eine ausdrücklich eigene Projekt-Untergrenze von 800 Hz. AES- und Program-Leistung werden nicht gleichgesetzt. Nicht verfügbare interne Kammermaße werden nicht erfunden.

GitHub-Referenz: [Waveguide_PSO, geprüfter Commit](https://github.com/rafaelst00/Waveguide_PSO/tree/baefd510603ce75612bbed62191f5786c170c6b1). Ergänzend Bempp und Gmsh, siehe Quellenregister. Kein fremder Programmcode übernommen, keine externen Solverläufe durchgeführt.

## Reproduzieren und prüfen

Benötigt werden Python 3 und Node.js ≥20. Für Build und Rechentests sind keine zusätzlichen Pakete nötig.

```sh
python scripts/build.py
node tests/core.test.mjs
```

Die Inhalte stehen in `data/pages.json`, die Quellen in `data/sources.json`. `scripts/build.py` erzeugt PDF-, HTML- und Markdown-Ausgaben sowie den vollständig eingebetteten Offline-Konfigurator. `configurator/core.mjs` enthält die Rechenformeln, `app.mjs` die Oberfläche und `template.html` das Layout. Nach Änderungen den Build ausführen; erzeugte Dateien mit ablegen.

Die PDFs besitzen bewusst einfache Standardschriften und ASCII-kodierte Datenströme. Griechische Formelzeichen werden in der PDF-Ausgabe ausgeschrieben; HTML und Markdown behalten die Zeichen.

## Validierung

Sechs Rechentests bestanden: Referenzmaße, Treibergrenzen, Frequenzskalierung, ungültige Eingaben, Zellraster und Helmholtz-Modell. PDF-Seitenzahl geprüft: 30 + 6. Eine PDF-Seite visuell geprüft. Browserinteraktion nicht geprüft: Die in dieser Umgebung vorgeschriebene Browser-QA-Schnittstelle `cua_repl.js` war nicht verfügbar. Keine akustische BEM-/FEM-Simulation und keine Prototypmessung.

Unabhängiges Entwicklungsprojekt; keine Herstellerfreigabe oder Originalteil-Kompatibilitätszusage. Die Rechte an Herstellerunterlagen und Markennamen verbleiben bei deren Inhabern.
