# 3D-Modellbibliothek · zwölf eigene Konzepte

[Illustrierter Katalog](../docs/designkatalog.md) · [HTML mit drehbarer Ansicht](../docs/designkatalog.html) · [PDF](../docs/designkatalog.pdf)

Jedes Konzept liegt als **ASCII-STL** und **OBJ** vor. GitHub kann die STL-Dateien direkt in seiner 3D-Vorschau anzeigen. Für die Offline-Ansicht das gesamte Repository als ZIP herunterladen, entpacken und `docs/designkatalog.html` öffnen. Das HTML lädt ausschließlich lokale Dateien. Die GitHub-Quelltextvorschau führt den HTML-Viewer nicht aus.

| Konzept | STL mit GitHub-Vorschau | OBJ |
|---|---|---|
| Einzel-Waveguide | [single.stl](single.stl) | [single.obj](single.obj) |
| Raketen-Ringkanal | [rocket.stl](rocket.stl) | [rocket.obj](rocket.obj) |
| Axtkopf-Zweikanal | [axe.stl](axe.stl) | [axe.obj](axe.obj) |
| Multicell 3 × 2 | [multi.stl](multi.stl) | [multi.obj](multi.obj) |
| Polycell mit geschwenkten Zellen | [poly.stl](poly.stl) | [poly.obj](poly.obj) |
| Mehrtreiber-Manifold, Explosion | [manifold.stl](manifold.stl) | [manifold.obj](manifold.obj) |
| Runder Konus | [round-conical.stl](round-conical.stl) | [round-conical.obj](round-conical.obj) |
| Rundes OS-Profil | [round-os.stl](round-os.stl) | [round-os.obj](round-os.obj) |
| Oval / Ellipse | [oval.stl](oval.stl) | [oval.obj](oval.obj) |
| Superellipse | [superellipse.stl](superellipse.stl) | [superellipse.obj](superellipse.obj) |
| Prismatischer Rechteck-Waveformer | [prism.stl](prism.stl) | [prism.obj](prism.obj) |
| Rund-auf-Schlitz-Waveformer | [round-slot.stl](round-slot.stl) | [round-slot.obj](round-slot.obj) |

## Koordinaten und Flächen

Alle Koordinaten sind in **Millimetern** zu interpretieren; STL und OBJ speichern keine verbindliche Maßeinheit. x = horizontal, y = vertikal, z = von Eingang zu Ausgang. Die Parameter in [catalog.json](../data/catalog.json) definieren eigene illustrative Modellabmessungen. Es sind weder Herstellermaße noch aus einem akustischen Optimierer berechnete Konturen. Mundmaße beschreiben die lichte Endöffnung, bei Zellen die gesamte Zellgruppe; die Hüllenaußenmaße kommen hinzu.

Die Kanalhüllen sind geschlossene Materialkörper um offene Luftwege. Die Außenkontur entsteht durch Addition von 4 mm auf beide Querschnittshalbachsen; bei Zellen und Eingangskanälen sind es 3 mm. Dies ist **keine konstante Wandstärke in Normalenrichtung**. Flansche, Schraubenbohrungen, Mund-Rollback und konstruktive Halterungen sind nicht enthalten.

Raketen-/Axtkopf-Modelle enthalten je einen separaten Innenkörper ohne Halterung. Multicell und Polycell enthalten sechs getrennte Zellen ohne gemeinsamen Treiberverteiler. Das Manifold besteht aus vier getrennten Hüllen mit 30 mm Explosionsabstand zwischen Eingängen und gemeinsamem Horn. Dieser Zwischenraum ist kein funktionsfähiger Kanal. Mehrteilige STL-Dateien sind nicht boolesch vereinigt; OBJ-Gruppen bewahren die Bauteilnamen.

## Modell und Bild gehören zusammen

Die SVG- und PDF-Renderings entstehen aus denselben Dreiecksnetzen wie STL/OBJ. Das lokale HTML zeigt diese Netze als drehbare orthografische 3D-Ansicht mit Front-/Seitenansicht, Zoom und optionaler Halbschnittdarstellung. Halbschnitt blendet Flächen aus und verändert weder Modell noch Download. Es ist kein Volumenschnitt mit neuen Abschlussflächen.

## Reproduzieren und prüfen

```sh
python scripts/build.py
python tests/catalog_models_test.py
node tests/core.test.mjs
```

[catalog_models.py](../scripts/catalog_models.py) benötigt nur die Python-Standardbibliothek. Geschlossene Netze und konsistente Orientierung sind technische Datenprüfungen. Sie belegen keine Kollisionsfreiheit mehrerer Körper, Druckbarkeit, Strömungseigenschaften, Impedanz, Phasengleichheit oder Richtwirkung. Für den Einsatz müssen Simulation, mechanische Konstruktion und Messung folgen.
