# SOLANAL · restless.audio

**Persönlicher Abdruck. Ein eigenes Horn.**

SOLANAL ist eine individualisierbare Spaß-Edition für das mittlere Rechteck des Diamantstumpfs. In der Multiplex-Ansicht machen die sichtbaren Holzlagen die gewellte Hornkontur lesbar. Die Formidee nimmt den Holz-Waveguide aus der bereitgestellten Referenz und das Mehrfacheintrittsprinzip der [Solana von JW Sound](https://www.jwsound.live/designs/solana-diy) auf.

- [Interaktives 3D-Modell](Diamantstumpf_R10_SOLANAL.html) herunterladen und im Browser öffnen.
- [Beispiel im Detail](Diamantstumpf_R10_SOLANAL.png) und [Mittelmodul](Diamantstumpf_R10_Mittelmodul.png).
- [JSON-Konturvorlage](Diamantstumpf_R10_Konturvorlage.json) und [STL-Beispiel „Falte“](Diamantstumpf_R10_SOLANAL_Falte.stl).

## Eigene Kontur

Falte, Vierblatt und Wirbel sind synthetische Profile. Für die Individualisierung erwartet der Viewer eine JSON-Datei mit `version: 1` und einer Liste `radien` aus genau 32 positiven Zahlen. Die Radien in 11,25°-Schritten von rechts nach oben und weiter gegen den Uhrzeigersinn eintragen. Die Verarbeitung läuft lokal. Beim Neuladen beginnt der Viewer wieder mit dem synthetischen Profil.

Der Viewer glättet und normiert die Kontur und überträgt sie als axiales Relief auf die Hornwand. Über den Regler lässt sich die Ausprägung zwischen 0 und maximal ±18 mm einstellen. „Horn als STL“ exportiert die aktuelle Geometrie in Millimetern. X zeigt quer, Y nach hinten und Z nach oben. Das Multiplex-Finish ist eine Ansicht im 3D-Modell.

## Schnittstelle

Die Geometrie baut auf S3 auf. Die Wechselplatte misst 539 × 273 mm, der Mund 516 × 246 mm und die Horntiefe 301 mm. Die Verformung liegt 7–130 mm hinter der Front. Die vier Seiteneintritte und der zentrale Hochtonhals liegen außerhalb dieses Bereichs. Die Klangwirkung der Profile und die Eignung für eine konkrete Fertigung sind am Prototyp zu prüfen.

## Modell erzeugen

Im R10-Ordner `python src/diamant_r10.py` aufrufen. Der Generator verwendet das R09-Modell und dessen STL-Archiv sowie die R07-Laufzeit und die Python-Abhängigkeiten der Nachbarrevisionen. Die HTML-Datei landet in `outputs`.
