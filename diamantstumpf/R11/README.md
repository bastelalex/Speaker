# SOLANAL · Faltenhorn R11

Eine stark gefaltete Mehrfacheintritts-Kassette für das mittlere Rechteck des Diamantstumpfs. Acht ausgeprägte Falten laufen in den gemeinsamen Mund. Vier seitliche Ø31-mm-Eintritte und der zentrale Hochtonhals bleiben frei. Die Kassette nutzt die 539 × 273 mm große R09-Schnittstelle. Das akustische Konzept greift das Prinzip eines [Mehrwege-Horns mit gemeinsamer Öffnung](https://patents.google.com/patent/US6411718B1/en) auf. Treiberanbindung, Weiche und Abstrahlung sind für einen spielbereiten Prototyp auszulegen und zu prüfen.

- [Offline-3D-Modell](Diamantstumpf_R11_SOLANAL_Faltenhorn.html)
- [Faltenhorn als STL, in Millimetern](Diamantstumpf_R11_SOLANAL_Faltenhorn.stl)
- [Abgetastete Querschnitte](Diamantstumpf_R11_SOLANAL_Atlasprofil.csv)
- [Detail](Diamantstumpf_R11_SOLANAL_Faltenhorn.png), [Mittelmodul](Diamantstumpf_R11_SOLANAL_Mittelmodul.png), [Seiteneintritte](Diamantstumpf_R11_SOLANAL_Seiteneintritte.png)

## Anatomische Quelle und Änderungen

BodyParts3D, © The Database Center for Life Science licensed under [CC Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/). [Offizielle Lizenz](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html) · [Datensatz und Download](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html) · [Originalpublikation](https://doi.org/10.1093/nar/gkn613).

Verwendet wurde die Atlas-Komponente **FJ2571** (Rektum, FMA14544), direkt aus dem offiziellen ZIP „isa_BP3D_4.0_obj_99.zip“. Die Quelle ist ein anatomisch bearbeitetes, MRT-basiertes Referenzmodell. Die Formdaten stammen aus drei Querschnitten am unteren Modellende, nicht aus einem äußeren Oberflächenscan. Für die Hornform wurden die Radien gemittelt, gefiltert und mit acht konstruktiv verstärkten Falten überlagert. Die Veränderung endet vor den Seiteneintritten. Der STL-Export wurde auf geschlossenes Mesh und der Einbau rechnerisch auf Überschneidungen mit den festen Frontkanälen geprüft.

Zum Regenerieren liegt die Quellenkomponente unter `src/r11_scan/FJ2571.obj`. Mit den R09-Python-Abhängigkeiten und dem R10-Viewer im Nachbarordner erzeugt `python src/diamant_r11.py` den Viewer, das STL und die CSV.
