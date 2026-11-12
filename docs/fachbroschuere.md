# Horn-Waveguides · Fachbroschüre

## Seite 1: Entwicklungsatlas für Horn-Waveguides

Fachbroschüre · 30 Seiten · Ausgabe 1.0

Diese Broschüre führt von einer gewünschten horizontalen und vertikalen Abstrahlung und einem Frequenzband zu einem prüfbaren Waveguide-Vorentwurf. Sie behandelt Raketen- und Axtkopf-Phaseplugs, klassische Multicell-Hörner, Polycell als hier verwendeten Arbeitsbegriff, Turbosound Polyhorn sowie Kompressionskammern. Treiberbeispiele stammen von LaVoce und JBL. Der Schwerpunkt liegt auf Zusammenhängen zwischen Querschnitt, Laufweg, Wellenlänge und Richtwirkung.
Das Ergebnis ist ein Entwicklungswerkzeug: Formeln liefern Startmaße und zeigen Zielkonflikte. Gemessene Polardaten, Belastbarkeit am konkreten Horn und fertigungsgerechte Originalmaße werden dadurch nicht ersetzt. Ergänzend liegen eine erste 1D-Lastprüfung aller Konzepte und eine axialsymmetrische FEM-Kampagne für drei rotationssymmetrische Profile vor; der separate Validierungsbericht nennt die Grenzen. Eigene Prototypmessungen liegen nicht vor. Alle Katalogentwürfe sind eigenständige Studien, keine freigegebenen Turbosound-Nachbauten.

**Formel / Modell:** Zielkette: Anforderung → Modell → Geometrie → Simulation → Messung

**Prüfpunkt:** Leseschlüssel: H = Herstellerdatum; R = Rechenmodell; E = eigener Entwurf. Quellenkennungen verweisen auf das Quellenregister.

Quellen: T1, L1, L2, J1, J2

---

## Seite 2: Begriffe und Systemgrenzen

Ein Phaseplug ist noch kein vollständiges Horn

Ein Waveguide führt Schall entlang von Grenzflächen; ein Horn kann zusätzlich die akustische Last am Treiber transformieren. Im praktischen Lautsprecherbau überlappen beide Funktionen. Ein Kompressionstreiber besitzt bereits Membran, Vorderkammer und internen Phaseplug. Sein Austrittsdurchmesser bezeichnet die Hornschnittstelle und ist weder Membran- noch Schwingspulendurchmesser.
Eine Rakete bezeichnet hier einen zentralen, axial verlängerten Verdrängungskörper. Axtkopf bezeichnet einen in einer Ebene keilartigen Körper. Diese anschaulichen Namen sind keine hinreichende technische Spezifikation. Multicell beschreibt getrennte Zellen; ein Mehrtreiber-Manifold verbindet dagegen mehrere Quellen mit einem gemeinsamen Ausgang. Eine Aufteilung eines Treibers in mehrere Kanäle ist wiederum ein anderes System. Die Begriffe müssen in Zeichnungen durch Flächen, Wege und Quellenzuordnung ergänzt werden.

**Formel / Modell:** N = Zahl der Kanäle; N_T = Zahl der Treiber; N ist nicht automatisch N_T.

**Prüfpunkt:** Bei JBL und LaVoce bleibt der interne Phaseplug unangetastet. Externe Einsätze benötigen eine eigene akustische Auslegung.

Quellen: T2, T3, J1

---

## Seite 3: Anforderungen richtig formulieren

Abstrahlung braucht Frequenz und Pegelkriterium

Als Eingabe werden die vollen Öffnungswinkel horizontal und vertikal verwendet, beispielsweise 90° × 40°. Das gewünschte Frequenzband reicht von f_lo bis f_hi. Eine belastbare Anforderung nennt außerdem das Kriterium für die Strahlbreite, üblich etwa −6 dB relativ zur Achse, den gültigen Frequenzbereich und die zulässige Abweichung. Der Wandwinkel eines Horns entspricht nicht automatisch der gemessenen Strahlbreite.
Zwei Eingaben allein bestimmen keine eindeutige Geometrie. Deshalb setzt der Konfigurator offen ausgewiesene Projektannahmen: Luft bei 20 °C, vereinfachte Apertur, geradlinige Aufweitung, ausgewählter Treiber und gegebenenfalls Zellenzahl. Für eine finale Konstruktion kommen Maximalpegel, Distanz, Bauraum, Filter und Fertigung hinzu. Ohne diese Angaben ist eine thermische oder mechanische Freigabe nicht möglich.

**Formel / Modell:** θ_H, θ_V = volle Winkel in Grad; f_lo < f_hi, Einheit Hz.

**Prüfpunkt:** Prüffrage: Soll 90° bei 1 kHz gelten oder erst oberhalb 4 kHz? Das ergibt sehr unterschiedliche Mundmaße.

Quellen: A2

---

## Seite 4: Wellenlänge und Laufzeit

Der Maßstab jeder geometrischen Entscheidung

Für eine erste Rechnung wird die Schallgeschwindigkeit mit c = 343 m/s angesetzt. Damit beträgt die Wellenlänge bei 1 kHz 343 mm, bei 10 kHz 34,3 mm und bei 20 kHz 17,15 mm. Ein mechanisch kleiner Versatz kann am oberen Bandende bereits eine erhebliche Phasenabweichung verursachen.
Die Laufzeit eines Weges ist seine Länge geteilt durch c. Für die Differenz zweier Wege ist nur deren Differenz maßgebend. Im Konfigurator dient 45° als frei gewähltes Phasenbudget; daraus entsteht Δl_max = c/(8 f_hi). Bei 18 kHz sind das etwa 2,38 mm. Dieser Wert ist kein Fertigungstoleranzstandard. Er beschreibt lediglich, wie streng gleich lange Kanäle im einfachen Laufwegmodell sein müssten. Wandreflexionen und Modenkonversion können darüber hinaus Phase verändern.

**Formel / Modell:** λ = c/f; Δt = Δl/c; Δφ = 360° · f · Δl/c.

**Prüfpunkt:** Beispiel: 5 mm Wegdifferenz verursachen bei 10 kHz ungefähr 52,5° Phasenunterschied.

Quellen: A1

---

## Seite 5: Akustische Größen und Einheiten

Druck, Volumenstrom und Leistung

Schalldruck p hat die Einheit Pascal. Der Volumenstrom U ist das Integral der normalen Teilchengeschwindigkeit über einen Querschnitt und wird in m³/s angegeben. Für die ebene fortschreitende Welle ist die akustische Impedanz bezogen auf Volumenstrom Z_a = p/U = ρc/S. Dieser Bezug unterscheidet sich von der spezifischen Impedanz p/v = ρc.
Eine kleinere Fläche erzeugt bei gleichem Volumenstrom höhere Geschwindigkeit. Daraus lässt sich keine beliebige Leistungssteigerung ableiten, denn viskose Verluste, nichtlineare Ausbreitung und Membranhub begrenzen das System. Für harmonische Spitzenwert-Zeiger lautet die mittlere Wirkleistung ein Halb mal Realteil von p mal konjugiertem U. Bei Effektivwert-Zeigern entfällt der Faktor ein Halb. Die verwendete Konvention muss im Simulationsbericht stehen.

**Formel / Modell:** Z_a = ρc/S [Pa·s/m³]; P = ½ Re{p U*} bei Spitzenwert-Zeigern.

**Prüfpunkt:** Projektluft: ρ = 1,204 kg/m³. Alle Formeln im Rechenkern verwenden Meter, Hertz und Kubikmeter.

Quellen: A1

---

## Seite 6: Websters Hornmodell

Nützliche 1D-Näherung mit klaren Grenzen

Die eindimensionale Hornbeschreibung betrachtet einen über den Querschnitt gemittelten Druck. Für eine Flächenfunktion S(x) entsteht eine Differentialgleichung, die Ausbreitung und Flächenänderung verbindet. Sie erklärt, weshalb zwei gleich lange Kanäle mit unterschiedlichen Flächenverläufen unterschiedliche Eingangsimpedanzen zeigen können.
Das Modell setzt einen geeigneten, weitgehend einheitlichen Zustand über den Querschnitt voraus. Es bildet weder vollständige dreidimensionale Polarantwort noch die Feldverteilung um einen Axtkopf zuverlässig ab. Es ist deshalb ein Werkzeug für Last und Ausbreitung, kein Ersatz für ein Richtwirkungsmodell. Bei abrupten Verzweigungen, scharfen Kanten und hochfrequent angeregten Querformen muss ein räumliches Verfahren folgen. In diesem Projekt werden keine 1D-Ergebnisse als reale Frequenzgänge ausgegeben.

**Formel / Modell:** (1/S) d/dx [S dp/dx] + k²p = 0; k = 2πf/c.

**Prüfpunkt:** Dokumentation: Flächenfunktion, Randbedingung am Mund und Quellenbedingung am Hals immer gemeinsam angeben.

Quellen: A1, A2

---

## Seite 7: Konisch und exponentiell

Flächenverlauf und Winkelführung sind verschiedene Ziele

Ein rotationssymmetrischer konischer Kanal hat einen linear wachsenden Radius und damit quadratisch wachsende Fläche. Für eine rechteckige Studie können Breite und Höhe jeweils linear wachsen. Das exponentielle Vergleichshorn verwendet dagegen einen exponentiellen Flächenverlauf. Seine theoretische Grenzfrequenz folgt aus der eindimensionalen Wellengleichung für das idealisierte, unendliche Horn.
Ein reales endliches Horn besitzt Mundreflexionen und einen Treiber mit eigener Impedanz. Die theoretische Grenzfrequenz darf deshalb nicht direkt zur Trennfrequenz werden. Der Konfigurator berechnet aus Mund- und Halsfläche einen äquivalenten Exponentialparameter als Vergleichswert, obwohl seine gezeichnete Kontur geradlinig ist. Dieser Vergleichswert ist ausdrücklich keine Simulation der gewählten Form. Breite Abstrahlung und tiefe Last erfordern oft getrennte Optimierungsschritte.

**Formel / Modell:** S_exp(x) = S_t exp(mx); m = ln(S_m/S_t)/L; f_c,exp = mc/(4π).

**Prüfpunkt:** Für denselben Hals und Mund ändert eine größere Länge m. Das sagt noch nichts über die tatsächliche Strahlbreite.

Quellen: A1

---

## Seite 8: Mundgröße aus einer Apertur

Eine nachvollziehbare Startschätzung

Die Vorbemessung behandelt jede Hauptachse als gleichmäßig belegte, ebene Rechteckapertur. Deren normierter Fernfelddruck ist eine sinc-Funktion. Für halben Schalldruck, ungefähr −6 dB, liegt das erste positive Argument bei rund 1,895. Daraus ergibt sich eine Startgröße für jede Achse. Sie wächst mit Wellenlänge und wird bei engerem Zielwinkel größer.
Die wirkliche Hornmündung besitzt eine gekrümmte Wellenfront und ungleichmäßige Belegung; die Formel ist deshalb keine allgemeine Hornregel. Sie erlaubt aber eine ehrliche Größenordnung ohne erfundene Polardaten. Eine besonders große vertikale Abmessung bei engem vertikalem Winkel ist in diesem Modell erwartbar. Für den Entwurf wird mindestens Halsdurchmesser plus 10 mm angesetzt, damit der Mund nicht kleiner als die Schnittstelle wird.

**Formel / Modell:** |sin(u)/u| = 0,5 bei u ≈ 1,895; D ≈ 0,603 λ / sin(θ/2).

**Prüfpunkt:** Alle Winkel in der Formel im Bogenmaß auswerten. θ bezeichnet den vollen −6-dB-Zielwinkel.

Quellen: A2

---

## Seite 9: Länge und Geometriehülle

Ein Bauraumvorschlag, keine eindeutige Lösung

Aus Mundbreite W, Mundhöhe H und Halsdurchmesser d entsteht eine einfache Längenschätzung. In jeder Achse wird die zur Zielwinkelhälfte passende geradlinige Aufweitung berechnet. Die größere der beiden Längen wird als gemeinsame Hornlänge verwendet. Dadurch ist in mindestens einer Achse der tatsächliche Wandwinkel kleiner als der Zielwinkel; der Konfigurator zeigt beide Werte separat.
Diese Geometriehülle dient zur Platzplanung und zur Erstellung eines ersten CAD-Modells. Halsübergang, Mundverrundung, Flansch und Treibertiefe kommen hinzu. Die Zeichnung verwendet einen rechteckigen Hals als schematischen Übergang; der reale runde Treiberaustritt erfordert einen glatten Rund-auf-Rechteck-Adapter. Die akustische Gleichwertigkeit dieser Übergangszone wird nicht vorausgesetzt.

**Formel / Modell:** L = max[(W−d)/(2 tan(θ_H/2)), (H−d)/(2 tan(θ_V/2))].

**Prüfpunkt:** Wandwinkel tatsächlich: 2 atan((D−d)/(2L)). Flanschmaße sind nicht im akustischen Mundmaß enthalten.

Quellen: E

---

## Seite 10: Raketen-Phaseplug

Ringkanal statt bloßer Dekoration

Ein zentraler Körper verdrängt Luftvolumen und erzeugt zwischen Außenwand und Innenkörper einen ringförmigen Kanal. Bei rotationssymmetrischer Betrachtung ist dessen Fläche die Differenz zweier Kreisflächen. Der Verlauf beider Radien bestimmt die Aufweitung. Ein optisch schlanker Körper kann akustisch eine Engstelle erzeugen, wenn sein Radius zu schnell zunimmt.
Turbosounds Mehrtreiber-Patent US4882562A zeigt ein verwandtes Konzept mit einem zentralen Körper und einem ringförmigen Abschnitt. Daraus folgt keine eindeutige Identifikation jedes historischen, umgangssprachlich Rakete genannten Bauteils. Für eine eigene Studie werden Innen- und Außenkontur gemeinsam parametrisiert. Engstellen, Eintrittsrichtungen und der Übergang am Ende des Innenkörpers müssen untersucht werden. Ein zusätzlicher Körper direkt hinter einem fertigen Kompressionstreiber kann dessen Ausgangslast wesentlich verändern.

**Formel / Modell:** S_ring(x) = π [R_a(x)² − R_i(x)²]; R_a > R_i.

**Prüfpunkt:** Konstruktionsprüfung: Querschnitt entlang x ausgeben, nicht nur den maximalen Außendurchmesser messen.

Quellen: T2

---

## Seite 11: Axtkopf-Phaseplug

Asymmetrie verlangt mehrere Schnitte

Ein Axtkopf besitzt in einer Schnittebene eine keil- oder schneidenartige Form. Er kann den Schallfluss in zwei Hauptkanäle aufteilen. Seine Wirkung hängt von der gegenüberliegenden Wand, der Lage zur Membran und der räumlichen Kontur ab. Eine Zeichnung des Körpers allein beschreibt daher kein vollständiges akustisches System.
Das Gebrauchsmuster CN204425636U belegt diese Formbezeichnung, ist jedoch kein Nachweis einer Turbosound-Urheberschaft. Im Designkatalog ist der Axtkopf ein eigener Konzeptentwurf. Er wird über Kanalflächen, Weglängen und Verrundungen beschrieben. Besonders zu prüfen sind ungleiche Wege seitlicher Membranzonen und die Feldzusammenführung hinter dem Körper. Eine geometrisch scharfe Schneide ist kein generelles Qualitätsmerkmal: mechanische Robustheit und akustische Streuung müssen gemeinsam betrachtet werden.

**Formel / Modell:** S_gesamt(x) = S_links(x) + S_rechts(x); Δl = |l_links − l_rechts|.

**Prüfpunkt:** Mindestens horizontalen, vertikalen und diagonalen Schnitt prüfen. Symmetrie nur dort annehmen, wo sie tatsächlich vorhanden ist.

Quellen: P2

---

## Seite 12: Kompressionskammer

Ein kleines Volumen mit großer Wirkung

Die Luft vor einer Membran bildet im konzentrierten Modell eine akustische Nachgiebigkeit. Eine enge Verbindung besitzt eine akustische Masse. Beide können eine Resonanz ausbilden. Das bekannte Helmholtz-Modell beschreibt diese Kombination im Bereich, in dem die Abmessungen klein gegenüber der Wellenlänge sind. Ein abstrahlendes Horn ist jedoch keine einfache massenbehaftete Öffnung mit konstanter Last.
Die Kammerrechnung im Konfigurator ist deshalb ein separater Lernrechner mit frei gewähltem Volumen, Halsfläche und effektiver Länge. Seine Werte werden nicht aus dem Treibernamen erfunden. Herstellerangaben wie Driver Displacement Volume bezeichnen den vom gesamten Treiber verdrängten Bauraum, nicht automatisch dessen interne Vorderkammer. Dieser häufige Verwechslungsfehler würde Resonanzrechnungen um Größenordnungen verfälschen.

**Formel / Modell:** C_a = V/(ρc²); M_a = ρl_eff/S; f_H = 1/(2π√(M_a C_a)).

**Prüfpunkt:** V in m³: 1 cm³ = 10⁻⁶ m³. l_eff enthält Endkorrekturen und ist nicht zwangsläufig die sichtbare Halslänge.

Quellen: A3, L1, L2

---

## Seite 13: Kompressionsverhältnis und Strömung

Fläche ist nur ein Teil der Belastung

Das geometrische Kompressionsverhältnis CR wird als wirksame Membranfläche geteilt durch die Summe der offenen Kanalflächen definiert. Dafür benötigt man die tatsächlich akustisch wirksame Fläche. Der Schwingspulendurchmesser liefert diese Fläche nicht. Für die gewählten Kompressionstreiber liegen hier keine ausreichend belegten internen Kanalflächen vor; daher wird kein produktspezifisches CR ausgewiesen.
Bei gegebenem Volumenstrom wächst die mittlere Kanalgeschwindigkeit mit abnehmender Fläche. Druck- und Geschwindigkeitsmaxima können bei Resonanzen an unterschiedlichen Orten liegen. Ein harmloser Mittelwert schließt lokale Überlastung nicht aus. Für eine eigene Konus-Vorkammer müssen mindestens wirksame Membranfläche, Hub, Kanalflächen und Bandbegrenzung bekannt sein. Eine frei gewählte Verringerung der Halsfläche ist kein zuverlässiger Weg zu höherem Nutzpegel.

**Formel / Modell:** CR = S_d / ΣS_Kanal; v_mittel = U / ΣS_Kanal.

**Prüfpunkt:** Keine CR-Ausgabe aus dem Schwingspulendurchmesser ableiten. Fehlende innere Geometrie bleibt als Datenlücke markiert.

Quellen: E

---

## Seite 14: Laufwegausgleich

Gleiche Länge ist notwendig, aber nicht hinreichend

Treffen zwei gleich starke Teilwellen mit unterschiedlicher Phase aufeinander, hängt die Summe von ihrer Phasendifferenz ab. Bei 180° können sie sich idealisiert vollständig auslöschen. Für einen Phaseplug werden deshalb die Wege verschiedener Membranzonen bis zu einer gemeinsamen Bezugsfläche untersucht. Die Mittellinie ist dafür nur eine erste geometrische Näherung.
Gleiche geometrische Wege garantieren noch keine identischen Übertragungsfunktionen. Unterschiedliche Querschnittsverläufe, Reflexionen oder Moden können zusätzliche Phasenlagen erzeugen. Bei einem Mehrtreiber-Manifold kommen Toleranzen der Treiber und elektrische Filter hinzu. Das Projekt verwendet ein 45°-Budget am oberen Bandende als transparenten Prüfwert. Für den späteren Prototyp müssen Amplitude und Phase der Kanäle möglichst getrennt gemessen oder räumlich simuliert werden.

**Formel / Modell:** |p_sum| = 2 |p_0| · |cos(Δφ/2)| bei zwei gleich starken Teilwellen.

**Prüfpunkt:** Bei f_hi = 20 kHz liegt das 45°-Wegbudget bei rund 2,14 mm. Fertigungstoleranz und akustischer Weg sind getrennt zu bilanzieren.

Quellen: R

---

## Seite 15: Multicell

Viele Zellen bilden eine gemeinsame Apertur

Ein klassisches Multicell-Horn besteht aus mehreren kleinen Hornzellen mit jeweils eigener Achse. Eine gemeinsame Quelle kann über einen Verteiler mehrere Zellen speisen. Die Richtwirkung entsteht aus der Überlagerung aller Zellfelder, deren Ausrichtung, Abstand, Phase und Einzelcharakteristik. Die Anzahl der Zellen allein bestimmt weder Strahlbreite noch Klangqualität.
Im Katalog wird eine 3 × 2-Anordnung als leicht nachvollziehbare Studie dargestellt. Die Außenhülle stammt aus der Aperturvorbemessung; die Unterteilung ist zunächst geometrisch. Die Winkel werden nicht einfach durch drei beziehungsweise zwei geteilt und als bewiesene Zellabstrahlung ausgegeben. Trennwände beanspruchen Fläche, und jede Zellmündung streut Schall. Deshalb muss die spätere Simulation sowohl die Einzelzelle als auch das vollständige Gebilde einschließlich Verteiler enthalten.

**Formel / Modell:** p(θ,φ,f) = Σ p_n(θ,φ,f) · exp(jψ_n).

**Prüfpunkt:** Zellzahl, Quellenzahl und Treiberzahl getrennt dokumentieren. Im lokalen Rechner bedeutet Zellenzahl keine automatische Mehrtreiberbestückung.

Quellen: P1

---

## Seite 16: Polycell und Polyhorn

Arbeitsbegriff und Herstellerkonzept unterscheiden

Polyhorn ist ein historisches Turbosound-Konzept. Das TA-880-Handbuch erläutert die Anpassung der Wellenfront an Array-Geometrien; als Herstellerdokument beschreibt es ein konkretes System, keine universelle Bauformel. Eine spätere Patentanmeldung von GP Acoustics nennt Polyhorn im Hintergrund im Zusammenhang mit einzelnen Zellen und einer toroidalen Welle. Diese spätere Quelle stammt von einem anderen Hersteller.
Polycell wird in diesem Projekt als Arbeitsbegriff für einen mehrkanaligen Entwurf mit gezielt entworfener Ausgangswellenfront verwendet. Daraus wird weder eine offizielle Turbosound-Produktkategorie noch eine bestimmte Originalkontur abgeleitet. Der Unterschied zum einfachen Multicell-Ansatz liegt hier im Entwicklungsziel: kontrollierte Phase über der gemeinsamen Mündung. Ohne Feldsimulation ist diese Zielsetzung noch kein erreichtes Ergebnis.

**Formel / Modell:** Ziel: vorgegebene Phase Φ(x,y,f) über der gemeinsamen Mündung.

**Prüfpunkt:** Originale CAD-Querschnitte und Kammermaße sind nicht verifiziert. Der Katalog zeigt deshalb Konzeptstudien mit expliziter Kennzeichnung.

Quellen: T1, P1

---

## Seite 17: Mehrtreiber-Manifolds

Mehr Quellen benötigen mehr Kontrolle

Ein Manifold führt mehrere Treiberausgänge zusammen. Im Turbosound-Patent US4882562A werden Kanäle und ein zentraler Körper kombiniert, um die Schallführung im gemeinsamen Bereich zu beeinflussen. Die patentierte Anordnung ist ein konkretes historisches Beispiel; ihre Leistungsversprechen werden hier nicht als Messergebnis eines Eigenbaus übernommen.
Für die Entwicklung sind identische Treibermodelle, Polarität, Verzögerung und die elektrische Last relevant. Zwei nominell gleiche 8-Ohm-Treiber ergeben parallel nominell 4 Ohm, in Serie 16 Ohm. Reale Impedanz ist frequenzabhängig. Auch bei korrekter elektrischer Beschaltung kann akustische Rückwirkung zwischen den Quellen entstehen. Der Konfigurator wählt deshalb zunächst einen Treiber pro Horn. Die Zellenoption verändert lediglich die schematische Unterteilung; sie erhöht nicht die zulässige Leistung.

**Formel / Modell:** Z_parallel = Z/N_T; Z_Serie = N_T · Z nur für identische Impedanzen.

**Prüfpunkt:** Keine automatische Addition von SPL- oder Wattwerten ohne gemeinsame Quellen- und Lastbedingungen.

Quellen: T2

---

## Seite 18: Abstände, Moden und Zellgrenzen

Das obere Bandende setzt enge Maßstäbe

Die Regel d ≤ λ/2 ist ein konservativer Abstandscheck für kohärente, räumlich abgetastete Quellen; sie ist kein allgemeines Verbot breiter Zellmündungen. Gitterkeulen hängen von Frequenz, Blickrichtung, Abstand und Einzelzellcharakteristik ab. Bei geformten Wellenfronten oder zusammenhängenden Mündungen muss das reale Feld untersucht werden.
Als zweiter Warnwert kann die erste Querform eines idealen starren Rechteckkanals abgeschätzt werden. Bei größerer Kanalbreite sinkt deren Cut-on-Frequenz. Ein aufgeweiteter, offener Hornkanal hat jedoch keine über seine gesamte Länge konstante Modenstruktur. Der Konfigurator zeigt den Wert anhand der größten idealisierten Zellabmessung nur als Prüfhinweis. Er erklärt keine Konstruktion für unbrauchbar und behauptet keine realen Resonanzfrequenzen.

**Formel / Modell:** d_check = c/(2f_hi); f_quer ≈ c/(2a) für einen idealen Rechteckkanal.

**Prüfpunkt:** Bei 18 kHz ist λ/2 etwa 9,53 mm. Das zeigt, warum einfache Zellenraster im Hochton räumliche Analyse brauchen.

Quellen: R

---

## Seite 19: Turbosound: Quellen richtig lesen

Historische Funktion ist keine Fertigungszeichnung

Für den historischen Überblick werden Herstellerhandbuch und Patente getrennt ausgewertet. Das TA-880-Handbuch nennt für sein System 25° horizontale Abstrahlung und einen entsprechenden Winkel zwischen benachbarten Gehäusen. Dieser Wert gilt für die beschriebene Systemanordnung; er ist kein allgemeiner Winkel für alle Turbosound-Hörner oder für einen selbst gezeichneten Polycell-Entwurf.
US4882562A dokumentiert ein Mehrtreiber-Manifold mit Innenkörper. GB2404520A betrifft einen Phaseplug mit thermischer Zusatzfunktion. Die bloße Ähnlichkeit eines Bauteils zu einer Rakete oder Axt genügt nicht zur Zuordnung zu einer Patentzeichnung. Für den Nachbau eines konkreten historischen Geräts wären Modellbezeichnung, Revision und vermessene Querschnitte erforderlich. Das Quellenregister hält fehlenden Volltextzugriff und nicht verifizierte Maße fest.

**Formel / Modell:** Belegkette: Modell + Revision + Zeichnung + Maßbezug + akustischer Nachweis.

**Prüfpunkt:** Für den vorliegenden Katalog wird keine Originalteil-Kompatibilität behauptet. Patentstatus ist keine technische Qualitätsbewertung.

Quellen: T1, T2, T3, T4

---

## Seite 20: LaVoce: zwei sinnvolle Größenklassen

DN10.20-16 und DN20.30TK

Der DN10.20-16 besitzt einen 25,4-mm-Austritt und nominal 16 Ohm. LaVoce nennt einen Frequenzbereich von 1 bis 18 kHz sowie eine empfohlene Trennung bei 1,2 kHz. Der DN20.30TK besitzt einen 50-mm-Austritt und nominal 8 Ohm; seine genannten Werte sind 0,5 bis 20 kHz und 800 Hz als empfohlene Trennung. Diese Daten machen beide zu unterschiedlichen Startpunkten für einen Hochton- beziehungsweise größeren Mittel-Hochton-Waveguide.
Die gemeldeten 70 beziehungsweise 110 W AES sind von 140 beziehungsweise 220 W Program zu unterscheiden. Der Konfigurator prüft Band und Projektgrenze, aber keine Pegelfreigabe. Die 108-dB-Angaben beider Treiber sind ohne identische Messbedingungen kein vollständiger Vergleich. Auch identische Nenndurchmesser reichen für eine mechanische Montageentscheidung nicht aus.

**Formel / Modell:** Halsfläche DN10.20-16 ≈ 507 mm²; DN20.30TK ≈ 1963 mm².

**Prüfpunkt:** Die Endung −16 gehört zur hier recherchierten 16-Ohm-Variante. Keine ungeprüfte Übertragung auf andere Varianten.

Quellen: L1, L2

---

## Seite 21: JBL: Referenztreiber korrekt einordnen

2426H und 2446H

Der JBL 2426H ist ein 8-Ohm-Treiber mit 25-mm-Austritt. Das offizielle Datenblatt nennt 500 Hz bis 20 kHz als Frequenzbereich, empfiehlt jedoch eine Trennung ab 800 Hz mit mindestens 12 dB/Oktave. Ein ausgewiesener Frequenzbereich ist somit nicht gleich der erlaubten Vollleistungstrennung. Die Empfindlichkeit hängt vom Horn ab: Das Datenblatt nennt unterschiedliche Werte für 2344A und 2370A.
Für den 2446H sind 49 mm Austritt, 8 Ohm und ein 100-mm-Schwingspulendurchmesser belegt. Die indexierten offiziellen Daten nennen 100 W continuous program oberhalb 500 Hz und 150 W oberhalb 1 kHz. Der direkte PDF-Abruf war gesperrt. Der Rechner setzt daher 800 Hz als eigene konservative Projekt-Untergrenze und kennzeichnet dies. J-Varianten sind keine automatisch identischen elektrischen Ersatzteile.

**Formel / Modell:** JBL-Leistungsart: continuous program; in der Datenbank steht AES ausdrücklich auf unbekannt.

**Prüfpunkt:** Historische Treiber vor Einsatz auf Originaldiaphragma, Zustand, Dichtheit und passende mechanische Schnittstelle prüfen.

Quellen: J1, J2, J3

---

## Seite 22: Treiberwahl und mechanische Schnittstelle

Eine Vorauswahl braucht ehrliche Statusmeldungen

Der Rechner verwirft Kandidaten, deren Band nicht bis zur gewünschten oberen Frequenz reicht oder deren Mindestgrenze über der gewünschten unteren Bandgrenze liegt. Bei LaVoce und 2426H werden die recherchierten Trennempfehlungen verwendet; beim 2446H gilt die gekennzeichnete Projektgrenze. Eine positive Vorauswahl heißt nur: Die erfassten Banddaten widersprechen der Eingabe nicht.
Der Hals wird mit dem tatsächlichen Millimeterwert der Datenbank gerechnet. Die nominelle Zollklasse kann gerundet sein: 49 mm sind nicht 50,8 mm. Vor der Fertigung werden Lochkreis, Gewinde, Dichtung, Austrittsebene und freier Querschnitt aus der aktuellen technischen Zeichnung übernommen. Ein Adapter soll keine Stufe, Tasche oder Leckstelle erzeugen. Der vorliegende Katalog enthält bewusst keine erfundenen Flanschbohrungen.

**Formel / Modell:** Status = Bandprüfung + Trennprüfung; Pegelprüfung bleibt offen.

**Prüfpunkt:** Bei ungeeignetem Treiber bleiben die Zahlen sichtbar, aber ein deutlicher Hinweis verhindert die Darstellung als Empfehlung.

Quellen: L1, L2, J1, J2

---

## Seite 23: Designfamilien im Vergleich

Vom einfachen Referenzhorn zur komplexen Kanalführung

Der erweiterte Katalog enthält zwölf Konzepte: Einzel-Waveguide, Raketen-Ringkanal, Axtkopf-Zweikanal, Multicell, Polycell, Mehrtreiber-Manifold, Rundkonus, rundes OS-Profil, Ellipse, Superellipse sowie prismatische Rechteck- und Rund-auf-Schlitz-Waveformer. Nur die erste Familie besitzt im Browser eine direkt berechnete Konturhülle. Bei den anderen Familien sind dieselben Außenmaße lediglich eine Bauraumreferenz; ihre inneren Konturen müssen zusätzlich entwickelt werden.
Für jeden Entwurf stehen Zweck, Parameter, Treibervorschlag, Risiken und nächster Nachweis. Die gleichen Eingaben können bewusst mehrere Familien erzeugen, denn Abstrahlung und Band sind keine eindeutige Konstruktionsvorschrift. Als Entwicklungsstrategie dient ein gut messbarer Einzel-Waveguide als Referenz. Zusätzliche Körper und Zellen sollen einen konkret gemessenen Vorteil liefern, etwa bessere Wellenfrontanpassung oder geringere Bautiefe, und nicht nur komplexer aussehen.

**Formel / Modell:** Vergleichsgrößen: Strahlbreite(f), Richtmaß(f), Impedanz(f), Verzerrung(P), Bauraum.

**Prüfpunkt:** Katalogstatus aller Familien: E · unvalidierter Vorentwurf. Kein Entwurf besitzt hier eine Herstellerfreigabe.

Quellen: E

---

## Seite 24: Rechenbeispiel 90° × 40°

1,2 bis 18 kHz mit LaVoce DN10.20-16

Bei c = 343 m/s und f_lo = 1200 Hz beträgt die Wellenlänge 285,8 mm. Die gleichmäßig belegte Apertur liefert horizontal etwa 243,8 mm und vertikal etwa 504,0 mm. Der enge vertikale Zielwinkel führt zu der größeren vertikalen Öffnung. Mit 25,4 mm Hals ergibt die geradlinige Hüllrechnung eine gemeinsame Länge von etwa 657 mm.
Der große Wert ist ein wichtiges Ergebnis: Vollständige Richtkontrolle bis 1,2 kHz bei 40° vertikal ist im verwendeten Aperturmodell bauraumintensiv. Der Rechner macht diese Konsequenz sichtbar. Ein kompaktes Serienhorn kann andere Wellenfronten und frequenzabhängige Abstrahlung nutzen. Soll das Gehäuse kleiner werden, muss die Richtkontrolle erst bei höherer Frequenz einsetzen, der Winkel erweitert oder die Form räumlich optimiert werden.

**Formel / Modell:** Δl_45° bei 18 kHz ≈ 2,38 mm; λ/2 bei 18 kHz ≈ 9,53 mm.

**Prüfpunkt:** Die Zahlen sind gerundete Modellwerte. Der automatisierte Test vergleicht den Rechenkern mit diesen Größenordnungen.

Quellen: R, L1

---

## Seite 25: Rechenbeispiel 60° × 40°

800 Hz bis 16 kHz als größere Studie

Bei 800 Hz beträgt die Wellenlänge 428,8 mm. Das Aperturmodell ergibt für 60° horizontal rund 517 mm und für 40° vertikal rund 756 mm. Mit einem LaVoce DN20.30TK und 50-mm-Hals führt die steilere Anforderung in vertikaler Richtung zu ungefähr 970 mm gemeinsamer Länge. Das Modell verlangt damit eine große Richtapertur am unteren Bandende.
Für einen kleineren Entwurf kann eine zweite Rechnung bei 1600 Hz als Beginn der Zielrichtwirkung dienen. Die Aperturmaße halbieren sich näherungsweise, obwohl das akustische Nutzband eventuell weiter bei 800 Hz beginnt. Dann müssen Nutzband und Richtkontrollband in der Spezifikation getrennt stehen. Der aktuelle Rechner koppelt beide bewusst an f_lo; eine solche Entkopplung ist eine dokumentierte spätere Erweiterung.

**Formel / Modell:** Bei Verdopplung von f_lo halbiert sich D im Aperturmodell; der feste Hals skaliert nicht mit.

**Prüfpunkt:** Treiberwahl 800 Hz: Banddaten sind nur ein Eingang. Last, Filter, gewünschter Pegel und Verzerrung müssen folgen.

Quellen: R, L2

---

## Seite 26: Simulation als überprüfbarer Ablauf

GitHub liefert Werkzeuge, keine automatische Wahrheit

Das geprüfte GitHub-Projekt Waveguide_PSO verbindet ATH-Geometrieerzeugung mit ABEC/AKABAK und einer Partikelschwarmoptimierung. Sein README beschreibt mehrere Winkelebenen und Zielgrößen wie Glätte und Winkelfolge. Die benötigten externen Programme sowie eine empfindliche GUI-Automation begrenzen die direkte Reproduzierbarkeit. Hier wurde kein fremder Code übernommen und kein solcher Optimierungslauf ausgeführt.
Als Alternative kann ein eigenes Modell mit Gmsh vernetzt und mit einer BEM-Implementierung wie Bempp untersucht werden. Gmsh erzeugt Netze, löst aber allein keine akustische Abstrahlung. Der Ablauf muss Quellfläche, Randbedingungen, Einheiten, Frequenzraster, Winkelauswertung und Normierung enthalten. Ergebnisse werden mit Dateihash und Werkzeugversion gespeichert, damit eine spätere Revision denselben Stand nachvollziehen kann.

**Formel / Modell:** Startwert Netzweite h ≤ λ_min/6; danach Netzkonvergenz prüfen.

**Prüfpunkt:** Mindestens zwei verfeinerte Netze vergleichen. Der Wert λ/6 ist eine Startregel und kein allgemeiner Genauigkeitsnachweis.

Quellen: G1, G2, G3

---

## Seite 27: Messen und beurteilen

Ein Achsfrequenzgang reicht nicht

Für die Bewertung wird das Horn mit demselben Treiber und derselben Signalverarbeitung auf einer ausreichend freien Messstrecke untersucht. Winkelraster, Abstand und zeitliche Fensterung werden dokumentiert. Tiefe Frequenzen benötigen lange Fenster; die untere verlässliche Messfrequenz ist daher an Umgebung und Fensterlänge gebunden. Horizontal, vertikal und diagonal werden frequenzabhängige Kurven aufgenommen.
Die Strahlbreite wird bei jeder Frequenz relativ zum Achspegel bestimmt. Eine reine Normierung kann starke absolute Pegelverluste verbergen; deshalb gehören absolute Referenz und normierte Darstellung zusammen. Ergänzend werden Impedanz, Verzerrung bei mehreren Pegeln und ein Zeitverhalten erfasst. Die Freifeld-Fernfeldabschätzung mit größter Apertur D hilft bei der Wahl des Abstands, ist bei realen Hörnern aber keine exakte Grenzlinie.

**Formel / Modell:** Fernfeld-Orientierung: r ≳ 2D²/λ; Strahlbreite an −6 dB relativ zur Achse.

**Prüfpunkt:** Projekt-Abnahmekriterium vor dem Bau festlegen, etwa Zielwinkel ±10° über einem ausdrücklich benannten Teilband.

Quellen: E

---

## Seite 28: Fertigung und Revision

CAD, Druck und Messung müssen denselben Stand tragen

Vor dem ersten Druck werden alle Querschnitte auf monotone und unbeabsichtigt verengte Bereiche geprüft. Ein glatter Flächenverlauf allein genügt nicht: Die Tangenten an Übergängen und die tatsächliche Mindestspaltweite sind ebenfalls relevant. Geteilte Druckteile benötigen reproduzierbare Zentrierung und dichte Fugen. Die Wandstärke folgt Werkstoff, Größe und mechanischer Beanspruchung und wird nicht akustisch aus dem Zielwinkel berechnet.
Für jede Revision werden Eingabe-JSON, CAD-Datei, Netz, Simulationsbericht und Messdaten gemeinsam abgelegt. Eine Änderung des Halsadapters kann eine neue akustische Revision sein, auch wenn das Mundmaß gleich bleibt. Bei einer Konzeptstudie mit Innenkörper wird zusätzlich dessen Position und Befestigung dokumentiert. Tragende oder geflogene Beschallungssysteme verlangen eine gesonderte mechanische Auslegung; diese Broschüre liefert dafür keine Bemessung.

**Formel / Modell:** Revisionssatz: Geometrie + Treiber/Diaphragma + Filter + Messaufbau + Datum.

**Prüfpunkt:** Erst ein gemessener und dokumentierter Prototyp kann als validierte Designvariante in den Katalog wechseln.

Quellen: E

---

## Seite 29: Konfigurator und Datenpflege

So wird aus einem Rechner ein brauchbares Arbeitsmittel

Die Browseranwendung läuft ohne Installation durch Öffnen von configurator/index.html. Sie benötigt keinen externen Dienst. Eingaben sind volle horizontale und vertikale Winkel sowie untere und obere Bandgrenze; hinzu kommen Treiber, Designfamilie und Zellraster. Ergebnisse zeigen Halsfläche, Mundmaße, Hülllänge, tatsächliche Wandwinkel, Wegbudget und Prüfhinweise. Ein JSON-Export hält die getroffenen Annahmen und Quellenkennungen fest.
Ungültige Zahlen und umgekehrte Bandgrenzen werden abgefangen. Ein Treiber außerhalb der hinterlegten Grenzen erhält keine positive Bandvorauswahl. Der Kammerrechner bleibt getrennt von der Treiberauswahl, weil interne Volumina unbekannt sind. Die Quelldaten stehen in data/drivers.json; ein Generatorskript bettet sie beim Erstellen in die Anwendung ein. Damit ist nachvollziehbar, welcher Datenstand zu einem Export gehört.

**Formel / Modell:** Datenstand: 12.11.2026; Rechenmodell: Apertur −6 dB + geradlinige Hülle, Version 1.0.

**Prüfpunkt:** Testkommando: node --test tests/core.test.mjs. PDF und HTML aus denselben Seiteninhalten erzeugen.

Quellen: E

---

## Seite 30: Quellenkarte und offene Aufgaben

Beleglage ist Teil des Designs

Die vollständigen Quellen mit direkten Links und Zugriffshinweisen stehen in docs/quellen.md und data/sources.json. Herstellerdaten werden als solche erfasst; eigene Herleitungen und Projektannahmen bleiben getrennt. Relevante Grundlagen sind Webster für das 1D-Modell, Geddes für räumliche Waveguide-Theorie und die offizielle COMSOL-Modellbeschreibung für Kammer und Hals. Turbosound-Handbuch und Patente liefern den historischen Zusammenhang.
Offen bleiben genaue originale Raketen- und Axtkopf-Maße, vollständige Polyhorn-Konturen, interne Vorderkammern der ausgewählten Treiber und eine akustische Validierung der eigenen Kataloggeometrien. Diese Lücken werden nicht durch Schätzwerte im Herstellerdatensatz geschlossen. Der nächste belastbare Schritt ist ein einzelner Referenzprototyp mit dokumentiertem Treiber, gemessenen Polaren und einer daran abgeglichenen räumlichen Simulation. Danach lassen sich komplexere Familien anhand identischer Kriterien vergleichen.

**Formel / Modell:** Primärdaten → offen gerechnete Annahmen → reproduzierbare Dateien → geprüfter Prototyp.

**Prüfpunkt:** Hauptquellen: T1–T3, P1–P2, L1–L2, J1–J3, A1–A3 und G1–G3. Keine eigenen Messdaten vorhanden.

Quellen: T1, T2, T3, P1, P2, L1, L2, J1, J2, J3, A1, A2, A3, G1, G2, G3

[Quellenregister](quellen.md)
