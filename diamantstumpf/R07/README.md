# Diamantstumpf R07

Interaktives Modell des kombinierten Drei-Modul-Aufbaus in hellem Birkenmultiplex. Die Außenseiten und Frontrahmen zeigen eine prozedurale Holzmaserung und sichtbare Lagen an den Kanten. Frontblenden, Reflektoren und Hornkanäle sind in satiniertem Silber dargestellt.

## Modell und Dateien

- [Interaktives 3D-Modell](Diamantstumpf_R07_Gesamtaufbau.html) herunterladen und lokal im Browser öffnen. Die HTML-Datei enthält Geometrie und Renderer.
- [Gesamtansicht](Diamantstumpf_R07_Gesamtansicht.png) und [Front](Diamantstumpf_R07_Frontal.png)
- [Neue Hornkassetten](Diamantstumpf_R07_Hornvergleich.png), [Seitenprofile](Diamantstumpf_R07_Hornvergleich_Profil.png) und [Halbschnitte](Diamantstumpf_R07_Hornvergleich_Schnitt.png)
- [3-Wege-Ansicht](Diamantstumpf_R07_Schallwege_3.png) und [4-Wege-Ansicht](Diamantstumpf_R07_Schallwege_4.png)
- [Top quer mit Manta-Horn](Diamantstumpf_R07_Top_Quer.png), [Rückseite](Diamantstumpf_R07_Rueckseite.png) und [Rollen gekippt](Diamantstumpf_R07_Rollen_Gekippt.png)
- [Manta Tief im Gesamtaufbau](Diamantstumpf_R07_Manta_Tief_Gesamt.png), [Manta-Vergleich](Diamantstumpf_R07_Manta_Vergleich.png), [Seitenprofile](Diamantstumpf_R07_Manta_Profil.png) und [Vertikalschnitte](Diamantstumpf_R07_Manta_Vertikalschnitt.png)
- [GLB des Gesamtaufbaus mit Manta Tief](Diamantstumpf_R07_Gesamtaufbau.glb), [elf Hornkassetten und Sitz als STL](Diamantstumpf_R07_Hornkassetten.zip) und [Zellberechnung](Diamantstumpf_R07_Zellberechnung.csv)

## Hornkassetten

| Variante | Form | Mund B × H | Vorsprung |
| --- | --- | ---: | ---: |
| F · Nautilus | Drei Spiralrippen und eine asymmetrische Mundkante | 244 × 228 mm | 105,4 mm |
| G · Manta | Breite Flügel mit vorgezogenen Spitzen | 254 × 163 mm | 132,4 mm |
| H · Krone | Fünf Blütenblätter mit tief zurückgesetzten Tälern | 239 × 235 mm | 120,4 mm |
| I · Orbital | Elliptischer, außen gerippter Trichter und vorstehender Zentralkörper | 237 × 192 mm | 125,0 mm |
| G2 · Manta Tief | Eingelassener Manta mit weichem Mundauslauf und asymmetrischer Vertikalkontur | 258 × 184 mm | 18,4 mm |

Alle elf Varianten sind im Modell auswählbar. Die bisherigen Varianten liegen unter „A bis E“ im Hornvergleich. In der Einzelansicht eines Tops lassen sich Gehäuse und Kassette jeweils um 90° drehen. Vorsprung und Öffnungsmaße beziehen sich auf die modellierte Geometrie. Die Wellenlinien zeigen die Wegzuordnung schematisch.

### Manta Tief

Der Hals sitzt 191 mm hinter der Frontblende, beim Manta G sind es 158 mm. Die projizierte Öffnung wächst von 304,5 auf 392,9 cm². Über die letzten rund 37 mm der nominellen Tiefe gehen die Wandkurven stetig in die aufgeweitete Mundpartie über. Im mittigen Vertikalschnitt endet der Mund 76 mm oberhalb und 108 mm unterhalb der Treiberachse. Die horizontale Kontur bleibt spiegelsymmetrisch. Ziel ist ein sanfterer Übergang in den Raum mit breiterer vertikaler Öffnung nach unten. Die erreichte Abdeckung, Reflexionen am Mund und der Übergang zum Tiefmittelton sind akustisch noch zu bestimmen. [AES · Horn's Directivity Related to the Pressure Distribution at Their Mouth](https://aes.org/publications/elibrary/elibrary-page/?id=9124)

## Modell erzeugen

Die Pakete in `src/requirements.txt` installieren und `python src/diamant_r07.py` aufrufen. HTML, GLB, ZIP und CSV landen in `outputs`. Die Three.js-Lizenz liegt in `src/three-face-LICENSE.txt`.
