"""German campaign report from the computed results, including failed checks."""
import html

def num(x,n=2):return f'{x:.{n}f}'.replace('.',',')
def write_report(root,data,manifest):
    out=root/'validation';rows=data['screening'];byid={r['id']:r for r in rows}
    fine=[r for r in data['fem'] if r['h_m']==.00175]
    statuses={r['id']:('Adapter / Verteiler fehlt' if r['blocker'] else '1D-Screening; räumlicher Nachweis offen') for r in rows}
    for id in ('round-os','round-conical','rocket'):
        checks=[c for c in data['fem_convergence'] if c['id']==id and c['comparison']=='h=1.75 mm vs 1.25 mm']
        passed=all(c['beamwidth_delta_deg'] is not None and c['beamwidth_delta_deg']<2 and c['delta_z_normalized_abs']<.03 and c['max_pattern_delta_above_minus20_db']<2 for c in checks)
        statuses[id]=('2D-Teilnachweis 0,8/1,2/2/4/8 kHz' if id=='rocket' else '2D-Teilnachweis 1,2/2/4/8 kHz') if passed else '2D-Teilnachweis; 8-kHz-Richtwirkung nicht konvergiert'
    for r in rows:r['validation_status']=statuses[r['id']]
    # Keep this status in machine-readable data and the later catalogue build.
    import json
    (out/'results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    report=['# Theoretische Validierung und Simulation · Kampagne 1.0',
      '**Stand 12.11.2026.** Alle zwölf Katalogkonzepte wurden geometrisch und mit reduzierten akustischen Modellen untersucht. Für Rundkonus, rundes OS-Profil und den Raketen-Ringkanal wurden zusätzlich echte axialsymmetrische FEM-Felder gelöst und daraus Richtdiagramme berechnet. Das ist ein erster numerischer Teilnachweis, keine Validierung kompletter LaVoce-Lautsprecher.',
      '## Wichtigste Ergebnisse',
      '- Multicell, Polycell und Manifold sind im aktuellen CAD kein vollständig an den Treiber angeschlossenes System. Fehlende Verteiler und der 30-mm-Explosionsspalt werden nicht als Luftkanal ersetzt.',
      f'- Multicell: **{num(byid["multi"]["cell_path_span_mm"])} mm** Differenz der vorhandenen Kanal-Mittellinien; Polycell: **{num(byid["poly"]["cell_path_span_mm"])} mm**. Ein gemeinsamer, gleichphasiger Eingang reicht damit geometrisch nicht für identische Wege. Die angegebenen Phasenproxies sind keine FEM-Phasen der Zellen.',
      f'- Rechteck-Waveformer: vorhandener Port **{num(byid["prism"]["inlet_area_total_mm2"],0)} mm²**, LaVoce DN20.30TK **{num(byid["prism"]["driver_exit_area_mm2"],0)} mm²**. Ein nicht vorhandener Adapter müsste die Fläche auf **{num(byid["prism"]["area_ratio_to_driver"]*100,1)} %** reduzieren und die Form umwandeln.',
      f'- Rund-auf-Schlitz: der Flächenverlauf verengt sich nach einem Zwischenmaximum zum Ende um **{num(byid["round-slot"]["terminal_area_contraction_fraction"]*100,1)} %**. Der einfache Loft erzeugt keinen nachgewiesenen isophasischen Schlitz.',
      f'- Zusätzlich ist die Schlitzmündung zu grob vernetzt: Die CAD-Öffnung besitzt nur **{num(byid["round-slot"]["outlet_area_total_mm2"],0)} mm²** statt der durch die Superellipse vorgesehenen **{num(byid["round-slot"]["intended_outlet_area_total_mm2"],0)} mm²**. Das sind **{num(byid["round-slot"]["outlet_tessellation_area_error_fraction"]*100,1)} %** Flächenfehler. Die 1D-Kurven gelten für dieses grobe Netz.',
      f'- Das runde OS-Katalogmodell hat nur neun axiale Ringe. Seine lineare Zwischenkontur weicht radial bis **{num(data["os_contour_comparison"][0]["maximum_radial_interpolation_error_mm"])} mm** vom analytischen OS-Profil ab. Die FEM benutzt für den Hauptvergleich genau diese Katalog-Meridiankontur, nicht stillschweigend eine bessere Kurve.',
      '- Die 8-kHz-Konvergenz wird gesondert geprüft. Eine kleine Gleichungsrestnorm oder eine geschlossene Energiebilanz allein beweist keine genaue Richtwirkung.',
      '## 1. Treiber, Quelle und Filter',
      '| Treiber | Hals | Impedanz | Hersteller-Hochpass | Empfindlichkeitsbezug |\n|---|---:|---:|---|---|\n| LaVoce DN10.20-16 | 25,4 mm | 16 Ω | ≥1200 Hz, ≥12 dB/Okt. | 108 dB bei 2,83 V / 1 m, HD1003 |\n| LaVoce DN20.30TK | 50 mm | 8 Ω | ≥800 Hz, ≥12 dB/Okt. | 108 dB bei 2,83 V / 1 m, 60°×40°-Horn |',
      'Belegt durch die aktuellen Hersteller-PDFs: [DN10.20-16](https://www.lavocespeakers.com/wp-admin/admin-post.php?action=lv_generate_pdf&page=4973), [DN20.30TK](https://lavocespeakers.com/wp-admin/admin-post.php?action=lv_generate_pdf&page=4955). Die 2,83-V-Angabe des 16-Ω-Treibers entspricht nur unter der nominal-ohmschen Näherung etwa 0,5 W. Es wurde deshalb kein pauschaler 1-W-/Max-SPL-Wert abgeleitet.',
      '**Simulierte Anregung:** konstante, gleichphasige Halsgeschwindigkeit mit 0,01 m/s Spitzenamplitude; homogene Luft mit c=343 m/s und ρ=1,204 kg/m³. Die Amplitude ist eine frei gewählte lineare Normierung, keine Spannung am LaVoce-Treiber. Die wirkliche Ausgangswellenfront, akustische Quellimpedanz, Membranmechanik und nichtlinearen Verluste sind unbekannt. Die Hersteller-Hochpässe begrenzen die Einsatzdiskussion; sie wurden nicht als vollständiges DSP-/elektrisches Modell in den Feldsolver eingesetzt.',
      'Für zuvor mit JBL referenzierte Konzepte wurden **LaVoce-Alternativen** geprüft: 25-/25,4-mm-Klasse → DN10.20-16, 49-/50-mm- und Mehrzellenklasse → DN20.30TK. Die ursprünglichen Katalogmodelle wurden nicht auf andere Halsmaße umkonstruiert. Nennähnliche Durchmesser oder passende Flächen beweisen keine mechanische Flanschkompatibilität.',
      '## 2. Prüfmatrix aller zwölf Konzepte',
      '| Konzept | LaVoce-Prüfkandidat | Gesamt-Eingangsfläche / Treiberfläche | Befund |\n|---|---|---:|---|']
    for r in rows:
        notes=r['blocker'] or statuses[r['id']]
        report.append(f'| [{r["id"]}](../models/{r["id"]}.stl) | {str(r["driver_count"])+" × " if r["driver_count"]>1 else ""}{r["driver_model"]} | {num(r["area_ratio_to_driver"]*100,1)} % | {notes} |')
    report+=['Die Kreisöffnungen der 32-seitigen STL-Polygone besitzen rund 0,64 % weniger Fläche als ein exakter Kreis gleichen Radius. Die 24-seitigen Zellports weichen entsprechend stärker ab. Eine nahezu gleiche Flächenzahl ist daher keine Anpassungsfreigabe. Bei Multicell/Polycell wird über sechs Ports summiert; beim Manifold über die drei Eingänge, ohne den gemeinsamen Ausgang nochmals mitzuzählen.',
      '## 3. Geometrie und Laufwege',
      '| Modell | Vorgesehene lichte Mundfläche [mm²] | Tatsächliche Netzfläche [mm²] | Flächendefizit |\n|---|---:|---:|---:|']
    for r in rows:report.append(f'| {r["id"]} | {num(r["intended_outlet_area_total_mm2"],0)} | {num(r["outlet_area_total_mm2"],0)} | {num(r["outlet_tessellation_area_error_fraction"]*100,1)} % |')
    report += [
      'Die freien Luftquerschnitte stammen aus orientierten Ebenenschnitten der **tatsächlich exportierten Dreiecksnetze**. Innenkörperflächen werden abgezogen. Es werden 512 axiale Schnittmitten pro vorhandener Kanalhülle verwendet; Portflächen werden zusätzlich nahe den Endebenen bestimmt. Das prüft keine vollständige Kollisionsfreiheit sämtlicher Bauteile.',
      '![Querschnittsverläufe](plots/sections.svg)',
      '| Konzept | Wege der vorhandenen Komponenten [mm] | Wegspreizung Zellen [mm] | geometrischer Phasenproxy am Bandende |\n|---|---|---:|---:|']
    for id in ('multi','poly'):
        r=byid[id];report.append(f'| {id} | '+', '.join(num(x,1) for x in r['channel_lengths_mm'])+f' | {num(r["cell_path_span_mm"])} | {num(r["geometric_phase_proxy_deg_at_bandtop"],1)}° bei {r["band_hz"][1]/1000:g} kHz |')
    report+=['Die Mittellinienlängen sind Längenintegrale der aus den Schnitten gewonnenen Kanalzentren. Eine solche Geometriedifferenz verursacht nicht zwingend dieselbe akustische Phasendifferenz: Moden, reflektierte Wellen und der fehlende Verteiler fehlen im Wegmodell. Formel des reinen Proxys: Δφ=360° f Δl/c.',
      f'Der gerade Randwegproxy am Rechteck-Waveformer beträgt {num(byid["prism"]["geometric_edge_path_proxy_mm"])} mm, am Rund-auf-Schlitz-Waveformer {num(byid["round-slot"]["geometric_edge_path_proxy_mm"])} mm gegenüber der Achse. Auch dies sind nur Konstruktionswarnungen, keine berechneten Ausgangsphasen.',
      '## 4. Eindimensionale Lastsimulation',
      'Jeder vorhandene Kanal wird in kurze Zylinder mit gemessener Fläche zerlegt. Für gekrümmte Zellmittellinien wird ds/dz berücksichtigt und S_normal≈S_z/(ds/dz) verwendet. Innenkörper erzeugen entsprechend ihren tatsächlichen ebenen Endkappen Querschnittssprünge. Verluste, Querformen und gegenseitige Zellabstrahlung fehlen.',
      'T_j = [[cos(kℓ_j), i Z_j sin(kℓ_j)], [i sin(kℓ_j)/Z_j, cos(kℓ_j)]], Z_j=ρc/S_j. Zeitkonvention exp(+iωt). Aus der Produktmatrix folgen Z_in und U_out/U_in. Die Mundlast ist die analytische Impedanz eines gleichflächigen Kreis-Kolbenstrahlers in einer unendlichen Schallwand. Für rechteckige, ovale und mehrteilige Mündungen ist das ausdrücklich eine grobe Ersatzlast.',
      'Z_L=(ρc/S)[1−2J₁(x)/x+i2H₁(x)/x], x=2ka. Die Schallleistungsidentität des verlustfreien Modells wird geprüft: T_power=1−|Γ|². Γ bezieht sich auf eine ebene, rein reelle Referenzlast ρc/S am vorhandenen Port, **nicht auf einen gemessenen LaVoce-Treiber**.',
      '![1D-Reflexionen](plots/one_d_reflection.svg)',
      '**Gültigkeitsgrenze:** Die 1D-Kurven dienen dem Lastscreening. Die großen Mündungen erlauben im Nutzband Querformen; oberhalb ihres Cut-ons ersetzt das Modell keine räumliche Rechnung. Auch der erste nicht-axialsymmetrische Halsmodus eines starren Rundkanals liegt bei ungefähr 7,9 kHz für 25,4 mm und 4,0 kHz für 50 mm. Ob ein realer Treiber solche Moden anregt, hängt von seiner unbekannten Ausgangswellenfront ab. Der axialsymmetrische Solver enthält nur m=0.',
      'Der gezeichnete 1D-Frequenzverlauf gehört jeweils zur **ersten vorhandenen Komponente**: bei Multicell/Polycell zur äußeren Einzelzelle, beim Manifold zum ersten Eingangskanal. Er ist keine Übertragungsfunktion des fehlenden Gesamtsystems. Alle übrigen vorhandenen Komponenten wurden zusätzlich an Stützfrequenzen gerechnet. Rohdaten: [one_d_spectra.csv](one_d_spectra.csv), [component_probes.csv](component_probes.csv), [section_profiles.csv](section_profiles.csv).',
      '| 1D-Konvergenz | Segmentzahlen | max. komplexe Änderung von Γ |\n|---|---|---:|']
    for c in data['one_d_convergence']:report.append(f'| {c["id"]} | 512 → 1024 | {num(c["max_delta_reflection_complex"],5)} |')
    report+=['## 5. Räumliche Simulation: Rundkonus, OS und Ringkanal',
      'Eigenständiger P1-FEM-Solver für die axialsymmetrische Helmholtzgleichung: ∂r(r∂r p)+∂z(r∂z p)+k²rp=0. Die schwache Form verwendet die echte Gewichtung 2πr; Steifigkeit und gewichtete lineare Massenmatrix werden elementweise integriert. Rigidität gilt an Hornwand, Achse und unendlicher Mund-Schallwand. Der Außenraum ist radial und axial auf 0,32 m begrenzt.',
      'An der Außenbegrenzung gilt eine winkelabhängige auslaufende sphärische Robin-Näherung ∂n p=−(ik+1/R)(n·R̂)p. Das ist **keine PML und keine exakte Fernfeldrandbedingung**. Die Abhängigkeit von der Begrenzung wurde mit 0,45 m Gegenraum getestet. Schallabstrahlung nach hinten und ein frei stehendes Gehäuse sind nicht modelliert.',
      'Die komplexe Mundgeschwindigkeit stammt aus der schwachen FEM-Reaktion an der Horn-/Außenraum-Schnittstelle. Das Rayleigh-Fernfeldintegral enthält diese räumlich veränderliche Amplitude und Phase. Es setzt keine gleichphasige Apertur voraus. Die 32-eckigen CAD-Ringe werden in der axialsymmetrischen Rechnung als Kreise behandelt, ihre neun axialen Radien und die lineare Zwischenkontur bleiben erhalten.',
      '![FEM-Richtdiagramme](plots/fem_polars.svg)',
      '| Modell | Frequenz | berechnete volle −6-dB-Breite | Re(Zin)/(ρc/S) | Im(Zin)/(ρc/S) |\n|---|---:|---:|---:|---:|']
    for r in fine:
        label='nicht konvergiert; Diagnosewert '+num(r['beamwidth_6db_deg'],1)+'°' if r['frequency_hz']==8000 and 'nicht konvergiert' in statuses[r['id']] else ('keine Kreuzung bis ±90°' if r['beamwidth_6db_deg'] is None else num(r['beamwidth_6db_deg'],1)+'°')
        report.append(f'| {r["id"]} | {r["frequency_hz"]/1000:g} kHz | {label} | {num(r["zin_normalized_real"],3)} | {num(r["zin_normalized_imag"],3)} |')
    report+=['Die Breite ist die erste −6-dB-Kreuzung relativ zur Achse, vom Achsstrahl aus nach außen gesucht. Bei Einbrüchen auf Achse oder mehreren Keulen kann diese Kennzahl irreführend sein. H und V sind nur wegen der angenommenen Rotationssymmetrie gleich. Vier Stützfrequenzen bei Konus/OS und fünf beim Ringkanal beweisen keine durchgehende Bandabdeckung oder konstante Abstrahlung.',
      '![OS-Schallfeld](plots/field-round-os.svg)',
      '![Konus-Schallfeld](plots/field-round-conical.svg)',
      '![Ringkanal-Schallfeld](plots/field-rocket.svg)',
      'Beim Ringkanal ist der vorhandene Innenkörper als starrer Körper mit geschlossener Vorder- und Endkappe aus dem Luftgebiet ausgespart. Seine Halterung fehlt; deren akustische Störung ist nicht simuliert.',
      '## 6. Numerische Verifikation und offene Konvergenz',
      f'Die größte relative Energiebilanzabweichung der Horn-FEM-Läufe beträgt {max(r["power_balance_relative"] for r in data["fem"]):.2e}; die größte relative Gleichungsrestnorm {max(r["relative_residual"] for r in data["fem"]):.2e}. Diese Größen prüfen die diskrete Lösung, nicht deren Annäherung an den realen Lautsprecher.',
      '| Modell / Gegenprüfung | Frequenz | ΔZ normiert | ΔBreite | max. Pegeldifferenz, beide Kurven >−20 dB |\n|---|---:|---:|---:|---:|']
    for c in data['fem_convergence']:
        report.append(f'| {c["id"]}: {c["comparison"]} | {c["frequency_hz"]/1000:g} kHz | {num(c["delta_z_normalized_abs"],4)} | {"offen" if c["beamwidth_delta_deg"] is None else num(c["beamwidth_delta_deg"],2)+"°"} | {num(c["max_pattern_delta_above_minus20_db"],2)} dB |')
    report+=['Projektkriterium für den 8-kHz-Teilnachweis: Änderung der Breite <2°, |ΔZ_norm|<0,03 und Polardifferenz <2 dB, wo beide Kurven über −20 dB liegen, im feinsten Netzvergleich. Die Grenzwerte sind projektinterne Akzeptanzkriterien, keine Norm. Ein verfehltes Kriterium bleibt als offen gekennzeichnet.',
      '**Unabhängiger Benchmark:** Ein Kolbenstrahler ohne Horn mit Radius 12,7 mm in derselben Schallwand wurde mit seiner analytischen Strahlungsimpedanz verglichen. Die verbleibende Abweichung umfasst Randtrunkierung und FEM-Diskretisierung.',
      '| Frequenz | relativer Impedanzfehler h=3 mm | relativer Impedanzfehler h=1,75 mm |\n|---|---:|---:|']
    for f in (1200,2000,4000,8000):
        a=next(r for r in data['piston_benchmark'] if r['frequency_hz']==f and r['h_m']==.003);b=next(r for r in data['piston_benchmark'] if r['frequency_hz']==f and r['h_m']==.00175)
        report.append(f'| {f/1000:g} kHz | {num(a["relative_error"]*100,2)} % | {num(b["relative_error"]*100,2)} % |')
    report+=['### OS: CAD-Facettierung gegen analytische Kontur',
      '| Frequenz | −6-dB-Breite Katalogmeridian | −6-dB-Breite analytischer Meridian | |ΔZ_norm| |\n|---|---:|---:|---:|']
    for c in data['os_contour_comparison']:report.append(f'| {c["frequency_hz"]/1000:g} kHz | {num(c["catalogue_contour_beamwidth_deg"],1)}° | {num(c["analytic_contour_beamwidth_deg"],1)}° | {num(c["delta_z_normalized_abs"],3)} |')
    report+=['Die analytische Variante ist eine Sensitivitätsstudie bei h=1,75 mm, nicht ein fertig freigegebenes neues CAD-Modell. Sie zeigt, warum ein nominaler Profilname allein keine genaue Geometrie festlegt.',
      '## 7. Konsequenzen für die nächsten Revisionen',
      '1. Rundes OS-Profil als ersten DN10.20-16-Prototyp weiterführen: Hals-/Mundkontur fein auflösen, Treiberflansch ergänzen, Mundterminierung optimieren und danach mit realer Quelle erneut rechnen. Die aktuelle Form liefert keinen Nachweis von 90° über 1,2–18 kHz.',
      '2. Rundkonus bei 8 kHz weiter verfeinern und Keulen/On-axis-Einbrüche untersuchen. Einen instabilen −6-dB-Wert nicht als Produktabstrahlung übernehmen.',
      '3. Für DN20.30TK zuerst den ovalen Einzel-Waveguide in 3D untersuchen. Die 1D-Ersatzlast erlaubt derzeit keine Aussage über H-/V-/Diagonalpolaren.',
      '4. Multicell/Polycell: gemeinsamen Verteiler und Laufwegausgleich konstruieren, danach alle Zellen einschließlich gegenseitiger Kopplung in einem 3D-Modell lösen.',
      '5. Schlitzmündung zuerst mit einer an die starke Exzentrizität angepassten Umfangsvernetzung neu erstellen. Rechteck- und Schlitz-Waveformer benötigen außerdem ein echtes Phasenkorrekturkonzept und einen belegten Treiberübergang. Eine reine Querschnittsumformung reicht nicht als Funktionsnachweis.',
      '6. Manifold erst nach einer dichten, vollständigen CAD-Verbindung als System simulieren. Kein Schließen des Explosionsspalts durch eine unbelegte Rechenannahme.',
      '## 8. Reproduzieren und Daten',
      '```sh\npython -m pip install -r validation/requirements.txt\nOPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/speaker-mpl python validation/run.py\npython tests/acoustics_test.py\npython scripts/build.py\n```',
      '[Rechenparameter, Versionen und SHA-256-Eingangshashes](manifest.json) · [Maschinenlesbare Ergebnisse](results.json) · [FEM-Polaren CSV](fem_polars.csv) · [Mundgeschwindigkeit CSV](fem_mouth_velocity.csv). Der vollständige Schallfeldvektor wird reproduzierbar neu berechnet, nicht als großes Binärarchiv gespeichert.',
      'Einheiten: Meter, Quadratmeter, Sekunden, Hertz; p/U in Pa·s/m³. Alle Amplituden sind Spitzenwert-Zeiger. Positive Energie geht in die Luft. Angegebene Quellenphase ist einheitlich; ein elektrisches Hochpass-, Verstärker- oder Schutzlimiter-Modell fehlt.',
      '## Quellen und Reichweite',
      '[LaVoce DN10.20-16 PDF](https://www.lavocespeakers.com/wp-admin/admin-post.php?action=lv_generate_pdf&page=4973) · [LaVoce DN20.30TK PDF](https://lavocespeakers.com/wp-admin/admin-post.php?action=lv_generate_pdf&page=4955) · [COMSOL: analytische Kolbenstrahlerreferenz und Rayleigh-Integral](https://doc.comsol.com/6.3/doc/com.comsol.help.models.aco.baffled_piston_radiation/models.aco.baffled_piston_radiation.pdf) · [Webster-Grundlage](https://pmc.ncbi.nlm.nih.gov/articles/PMC1091593/) · [OS-Profilformel](https://at-horns.eu/release/OS-SE%20Waveguide.pdf). Die eigene Simulation wurde mit NumPy/SciPy ausgeführt; es wurde keine COMSOL-, AKABAK- oder ABEC-Rechnung behauptet.',
      '**Nicht untersucht:** vollständige 3D-Polaren nicht rotationssymmetrischer Modelle, reale elektrische Impedanz oder Spannung/SPL-Übertragung der Treiber, interner Phaseplug, Membranbelastung, thermische Kompression, Klirr, Grenzpegel, Fertigungstoleranzen, tragende Konstruktion und messtechnische Bestätigung. Kein Konzept erhält durch diese erste Kampagne eine Produkt- oder Leistungsfreigabe.']
    markdown='\n\n'.join(report)+'\n'
    while '|\n\n|' in markdown:markdown=markdown.replace('|\n\n|','|\n|')
    markdown=markdown.replace('| |ΔZ_norm| |','| ΔZ_norm Betrag |')
    (out/'REPORT.md').write_text(markdown)
    # Standalone readable HTML, requiring only local SVG files; escape all source text.
    chunks=[];in_table=False;in_code=False
    import re
    def inline(s):
        s=html.escape(s)
        s=re.sub(r'!\[([^\]]*)\]\(([^)]+)\)',r'<img alt="\1" src="\2">',s)
        s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'<a href="\2">\1</a>',s)
        s=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',s)
        return s
    for block in markdown.strip().split('\n\n'):
        if block.startswith('```'):chunks.append('<pre>'+html.escape(block.strip('`').removeprefix('sh\n'))+'</pre>')
        elif block.startswith('|'):
            lines=block.splitlines();parts=[]
            for line in lines:
                cells=[x.strip() for x in line.strip('|').split('|')]
                if all(re.fullmatch(r'[-: ]+',x) for x in cells):continue
                parts.append('<tr>'+''.join('<td>'+inline(c)+'</td>' for c in cells)+'</tr>')
            # Consecutive per-row blocks are valid separate compact tables.
            chunks.append('<table>'+''.join(parts)+'</table>')
        elif block.startswith('### '):chunks.append('<h3>'+inline(block[4:])+'</h3>')
        elif block.startswith('## '):chunks.append('<h2>'+inline(block[3:])+'</h2>')
        elif block.startswith('# '):chunks.append('<h1>'+inline(block[2:])+'</h1>')
        else:chunks.append('<p>'+inline(block)+'</p>')
    style='body{max-width:1200px;margin:auto;padding:30px;font:16px/1.65 system-ui;color:#173531;background:#f4f6f0}h1{font-size:40px;line-height:1.2}h2{border-top:1px solid #bed0bd;padding-top:25px;margin-top:40px}img{max-width:100%;background:white}table{width:100%;border-collapse:collapse;font-size:13px;table-layout:fixed;background:white}td{padding:9px;border:1px solid #d1dfd1;overflow-wrap:anywhere}a{color:#14665b}pre{overflow:auto;background:#e0eade;padding:20px}@media print{body{font-size:10px}h2{break-before:page}img{max-height:190mm}table{font-size:9px}}'
    (out/'report.html').write_text('<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LaVoce · Validierungskampagne 1.0</title><style>'+style+'</style>'+''.join(chunks)+'</html>')
