# Diamantstumpf R08 · Zentrale Prismenplatte

Das 600 × 1.200 mm große Mittelmodul hat eine austauschbare Zentralkassette. Sein Zellraster und die Frontkanäle stammen aus R07. Beide Tops zeigen Manta Tief. Das Doppelprisma nimmt die separate Leitfläche der Vollzelle M23 und die zwei aufrechten Keile der Bildvorlage auf.

- [Interaktives 3D-Modell](Diamantstumpf_R08_Prismenplatte.html). HTML herunterladen und im Browser öffnen.
- [Gesamtaufbau](Diamantstumpf_R08_Gesamtaufbau.png) und [Mittelmodul](Diamantstumpf_R08_Mittelmodul.png)
- [Doppelprisma](Diamantstumpf_R08_Doppelprisma.png), [abgehobener Aufsatz](Diamantstumpf_R08_Aufsatz_abgehoben.png) und [Prismenvergleich](Diamantstumpf_R08_Prismenvergleich.png)
- [STL-Teile](Diamantstumpf_R08_Prismen_STL.zip) und [Abmessungen](Diamantstumpf_R08_Prismenmasse.csv)

## Wechselplatte

Alle drei Aufsätze werden vor dem Konturhorn A montiert. Platte und Horn nutzen vier Durchgangsbohrungen Ø5,5 mm im 254 × 254 mm großen Bohrbild. Die Rahmenbreite und -höhe betragen jeweils 270 mm. In der 3D-Ansicht „Kassette“ lässt sich der Aufsatz von Horn und Schrauben trennen. Die elf R07-Hörner lassen sich als vollständige Alternativen in denselben Sitz einsetzen.

| Variante | Geometrie | Vorsprung vor Blende |
| --- | --- | ---: |
| P1 Doppelprisma | Zwei spiegelbildliche, aufrechte Keile | 72 mm |
| P2 Scherenprisma | Seitlich wandernde Grate | 95 mm |
| P3 Prisma Tief | Nach unten gezogene Grate | 87 mm |

Die Aufsätze sind geometrische Prototypen. Ihre akustische Wirkung und die resultierenden horizontalen und vertikalen Öffnungswinkel sind zu messen. [AES zur Druckverteilung am Hornmund](https://aes.org/publications/elibrary/elibrary-page/?id=9124)

## Modell erzeugen

Die Anforderungen aus `../R07/src/requirements.txt` installieren. Im R08-Ordner `python src/diamant_r08.py` ausführen. Der Generator verwendet das R07-Modell und die dortige Three.js-Laufzeit. HTML, STL-ZIP und CSV landen in `outputs`.
