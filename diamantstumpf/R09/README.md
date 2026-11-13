# restless.audio · Diamantstumpf R09

Die Signature-Kassette sitzt ausschließlich im mittleren Rechteck des 600 × 1.200 mm großen Mittelmoduls. Der Wechsel betrifft zwölf Seitenzellen und den kleinen 270-mm-Kassettensitz. Die beiden 3 × 6-Polycell-Felder und sechs Bassmünder bleiben in der Front.

## Modell und Studie

- [Interaktives 3D-Modell](Diamantstumpf_R09_Signature.html) herunterladen und lokal im Browser öffnen.
- [Studiendokumentation](Diamantstumpf_R09_Studiendoku.pdf) mit historischer Einordnung, Solana-Vergleich, Bildanalyse und Prüfplan.
- [Mittelmodul](Diamantstumpf_R09_Mittelmodul.png), [Gesamtaufbau](Diamantstumpf_R09_Gesamtaufbau.png), [drei Varianten](Diamantstumpf_R09_Vergleich.png) und [S3-Seiteneintritte](Diamantstumpf_R09_Seiteneintritte.png).
- [STL-Geometrien](Diamantstumpf_R09_Geometrien_STL.zip) und [Maße](Diamantstumpf_R09_Geometriedaten.csv).

| Option | Mund | Tiefe ab Blende | Aufbau |
| --- | ---: | ---: | --- |
| S1 Schwingenmund | 520 × 246 mm | 298 mm | Zwei abnehmbare Leitprismen |
| S2 Fächer Vier | 518 × 246 mm | 315 mm | Drei vordere Stege, vier Segmente, gemeinsamer Hals |
| S3 Vierfach-Eintritt | 516 × 246 mm | 301 mm | Vier seitliche Ø31-mm-Durchlässe und zentraler Hochtonhals |

Rechteckige Montageplatte 539 × 273 mm, geometrische Öffnung 540 × 274 mm. Die S1-Prismen haben vier Ø2,8-mm-Durchgänge für die Befestigung. Die bisherige 54-Öffnungen-Front mit elf kleinen Hörnern und drei Prismenvarianten ist im selben Viewer auswählbar. S3 ist eine von Solana inspirierte Eigengeometrie. Treiberadapter, Anschlusskammern, Weiche, Dichtung und Montage müssen für den Prototyp ausgelegt werden. Abstrahlung und Bandbreite werden im Prüfplan der Studiendokumentation behandelt.

## Modell erzeugen

Im R09-Ordner `python src/diamant_r09.py` aufrufen. Der Generator verwendet den R08-Datenstand und die R07-Module, Laufzeit und Python-Abhängigkeiten aus den jeweiligen Nachbarrevisionen. HTML, STL-ZIP und CSV landen in `outputs`.
