# Diamantstumpf R06

Drei Lautsprechermodule mit angedockten Tops. Die Front misst in der Mitte 600 × 1.200 mm und an jedem Top 400 × 1.200 mm. Der interaktive Aufbau zeigt Front, Rückseite, Rollpositionen, den 18-Zöller und den Querbetrieb eines Tops.

## Dateien

- [Offline-3D-Modell](Diamantstumpf_R06_Gesamtaufbau.html). Die HTML-Datei herunterladen und im Browser öffnen. Die GitHub-Dateivorschau führt das Modell nicht aus.
- [3D-Export mit Konturhorn A](Diamantstumpf_R06_Gesamtaufbau.glb)
- [Sechs Hornkassetten und Sitz als STL](Diamantstumpf_R06_Hornkassetten.zip)
- [Zellberechnung](Diamantstumpf_R06_Zellberechnung.csv)
- [Front](Diamantstumpf_R06_Frontal.png), [Rückseite](Diamantstumpf_R06_Rueckseite.png), [Top quer](Diamantstumpf_R06_Top_Quer.png)
- [Drei Wege](Diamantstumpf_R06_Schallwege_3.png), [vier Wege](Diamantstumpf_R06_Schallwege_4.png), [Hornvergleich](Diamantstumpf_R06_Hornvergleich.png), [Halbschnitte](Diamantstumpf_R06_Hornvergleich_Schnitt.png)

## Front und Schallwege

Das Grundraster der Tops hat 4 × 6 quadratische Zellen, das der Mitte 6 × 6. Das Rastermaß beträgt 90 mm, die volle lichte Zellweite 86 mm. Links und rechts vom Top-Horn sitzen jeweils zwei halbe Zellen übereinander. In der Mitte stehen auf beiden Seiten je eine ganze und eine halbe Zelle über drei Reihen. Die Bassöffnungen sitzen oberhalb und unterhalb des Rasters.

Rot kennzeichnet Bass und Blau Tiefmittelton. Gelb kennzeichnet den Koaxialweg. In der Vierwegeansicht ist der Koax-Mittelton durchgezogen und der Koax-Hochton gepunktet. Die Wellenlinien sind schematisch.

## Hornkassetten

Die gemeinsame Kassette misst 270 × 270 mm. Alle Formen sind im Modell auswählbar und im STL-Paket enthalten. Das Top lässt sich quer legen. Die Kassette wird gelöst, um 90° um die Schallachse versetzt und wieder verschraubt.

| Variante | Geometrie | Mund, B × H |
| --- | --- | ---: |
| A | Gerundetes Konturhorn | 232 × 210 mm |
| B | Schlitz mit anschließendem Fächer | 234 × 204 mm |
| C | Drei Zellen mit zwei Leitstegen | 232 × 216 mm |
| A mit Waveguide | Kontur A mit axialem Tropfenkörper auf drei Stegen | 232 × 210 mm |
| D | Vier innen gedrehte Lappen vor rechteckigem Mund | 258 × 210 mm |
| E | Zweistufiger Fächer mit versetzter Innenachse | 264 × 224 mm |

## Rollen und Stand

Jedes Gehäuse hat zwei Ø100-mm-Bluewheels und eine durchgehende 45°-Schräge an der unteren Rückseite. Die Schräge reicht ab Tiefe 610 mm bis zur Rückwand bei 800 mm. Die Radmitten liegen je 44 mm von den Seitenkanten der Rückseite entfernt. Die Räder bleiben im Stand 8 mm über dem Boden und berühren ihn beim Kippen rechnerisch ab etwa 3,2°. Das Modell zeigt die Befestigung geometrisch. Für die Halterung ist die Tragfähigkeit separat zu prüfen.

Die akustische Abstimmung der Hornvarianten, der Bassübergang zu den Frontkanälen und die Systemabstrahlung sind am Prototyp zu prüfen.

## Modell erzeugen

Python und die Pakete in src/requirements.txt installieren. Der Aufruf „python src/diamant_gesamt.py“ erzeugt HTML, GLB, STL-ZIP und CSV im Ordner outputs. Die HTML-Datei enthält ihre Geometrien und die Three.js-Laufzeit. Die Lizenz liegt unter src/three-face-LICENSE.txt.
