"""Build dependency-free HTML and ASCII-only PDFs from reviewed source data."""
from pathlib import Path
import json, math, html, textwrap

ROOT = Path(__file__).resolve().parents[1]
def read(name): return json.loads((ROOT/'data'/name).read_text())
pages, sources, drivers = read('pages.json'), read('sources.json'), read('drivers.json')
esc = html.escape
CSS = '''@page{size:A4;margin:0}*{box-sizing:border-box}body{margin:0;background:#e7ece8;color:#10282d;font:16px/1.6 system-ui,sans-serif}header{padding:25px 7%;background:#10282d;color:#eff7f1}a{color:#136c60}nav a{color:#8ee0c1;margin-right:25px}.page{width:210mm;min-height:297mm;margin:20px auto;padding:18mm 19mm;background:#fff;position:relative;break-after:page}.eyebrow{font-size:12px;letter-spacing:2px;text-transform:uppercase;color:#137762}h1{font-size:37px;line-height:1.12;margin:15px 0}h2{font-size:19px;font-weight:500;color:#527068}p{margin:16px 0}.formula{background:#e7f5ee;border-left:4px solid #117d65;padding:16px;font-size:17px}.check{border-top:1px solid #b9d0c4;padding-top:15px}.refs{font-size:11px;margin-top:20px}svg{width:100%;height:155px}.folio{font-size:12px;color:#63776c;margin-top:20px}@media print{header{display:none}body{background:white}.page{margin:0;height:297mm;min-height:0;overflow:hidden}}@media(max-width:800px){.page{width:auto;min-height:0;margin:12px;padding:25px}h1{font-size:30px}}'''

families = [
 ('single','S-90 · Einzel-Waveguide','90° × 40° · 1200–18000 Hz · DN10.20-16',
  'Einfacher Referenzentwurf für einen Treiber. Geradlinige Hülle mit separat zu konstruierendem Rund-auf-Rechteck-Halsübergang. Gut geeignet, um den eigenen Messaufbau und die Größenordnung des Aperturmodells zu prüfen.',
  'W, H, L, Halsdurchmesser, Mundverrundung und Halsübergang',
  'Große vertikale Apertur; unbewiesene Zielabstrahlung; Hals- und Mundreflexionen.',
  'Räumliches Netz des gesamten Horns, vollständige Polaren, Impedanz und Verzerrung.',90,40,1200,18000,0),
 ('rocket','R-60 · Raketen-Ringkanal','60° × 40° · 800–16000 Hz · DN20.30TK',
  'Konzept mit axialem Innenkörper. Die äußere Referenzhülle entspricht derselben Eingabe wie bei einem Einzelhorn. Der Innenkörper ist eine Funktionsskizze und besitzt keine abgeleiteten Fertigungsmaße. Verwandter historischer Nachweis: T2.',
  'Außenradius R_a(x), Innenradius R_i(x), Einlauf, Endauslauf, Mindestspalt',
  'Unbeabsichtigte Ringkanal-Engstelle, Moden, Reflexion am Innenkörperende.',
  'Flächenverlauf und axialsymmetrische Studie; danach 3D bei nicht rotationssymmetrischem Mund.',60,40,800,16000,1),
 ('axe','A-90 · Axtkopf-Zweikanal','90° × 60° · 1200–16000 Hz · JBL 2426H',
  'Zwei Hauptkanäle um einen keilförmigen Körper. Die Skizze beschreibt das Funktionsprinzip, keine vermessene Turbosound-Originalkontur. Das Beispiel P2 belegt den Formbegriff. Die Treiberschnittstelle bleibt extern; der interne Phaseplug wird nicht verändert.',
  'S_links(x), S_rechts(x), Schneidenradius, Wegdifferenz, Zusammenführung',
  'Asymmetrische Wellenfront, lokale Überhöhung, scharfe Übergänge.',
  'Drei Schnittebenen, komplexe Felder vor und nach der Zusammenführung.',90,60,1200,16000,2),
 ('multi','M-60 · Multicell 3 × 2','60° × 40° · 1000–16000 Hz · JBL 2446H',
  'Ein Treiber speist sechs Zellen über einen noch auszulegenden Verteiler. Das Raster zeigt eine erste Unterteilung der Außenapertur. Zellwände und Zellachsen sind im Hüllmaß nicht enthalten. Die Einzelzellwinkel folgen nicht automatisch aus dem Gesamtwinkel geteilt durch Zellzahl.',
  '3 Spalten, 2 Reihen, Wandstärken, Zellachsen, Verteilerwege und Quellfläche',
  'Interferenz, Zellgrenzen, ungleiche Wege und zu großer Bauraum.',
  'Einzelzelle und vollständige Anordnung mit Verteiler getrennt und gemeinsam simulieren.',60,40,1000,16000,3),
 ('poly','P-25 · Polycell-Konzept','25° × 30° · 1600–16000 Hz · DN20.30TK',
  'Arbeitsstudie für eine kontrollierte gemeinsame Ausgangswellenfront. Sechs symbolische Kanäle stehen für ein noch zu optimierendes Netzwerk. Der Winkel ist ein eigener Zielwert; die Studie ist kein TA-880-Nachbau. Polyhorn-Kontext: T1 und P1.',
  'Ausgangsphase Φ(x,y), Kanalwege, Flächenverläufe, Zellmündungen, Arraykrümmung',
  'Die Zielwellenfront wird geometrisch nicht automatisch erreicht; komplexe Kopplung.',
  'Phase und Amplitude über der Apertur, Arrayüberlagerung und vollständige Polaren.',25,30,1600,16000,1),
 ('manifold','D-60 · Mehrtreiber-Manifold','60° × 40° · 2000–16000 Hz · JBL 2426H als Kanalreferenz',
  'Konzept für mehrere identische Quellen mit zentralem Zusammenführungsbereich nach eigenständiger Auslegung. Die angegebenen Hüllmaße beziehen sich nur auf einen Referenzaustritt und legen weder Treiberzahl noch Gesamtfläche fest. T2 liefert einen historischen Funktionsbeleg.',
  'Treiberzahl, Gesamtquellfläche, Eingangsachsen, identische Wege, gemeinsame Last',
  'Gegenseitige Rückwirkung, komplexe elektrische Last, Phasendifferenzen.',
  'Gekoppeltes Mehrquellenmodell und Messung jedes Kanals. Keine Watt- oder SPL-Addition.',60,40,2000,16000,2)
]

def diagram(kind='single'):
    lines='<path d="M90 100 L220 25 L510 25 L510 155 L220 155 Z" fill="none"/>'
    if kind=='rocket': lines+='<path d="M160 90 Q280 40 420 90 Q280 140 160 90 Z" fill="#9ad7bf"/>'
    elif kind=='axe': lines+='<path d="M170 90 L340 50 L420 90 L340 130 Z" fill="#9ad7bf"/>'
    elif kind in ('multi','poly'):
        lines='<rect x="130" y="25" width="360" height="130" fill="none"/><path d="M250 25 V155 M370 25 V155 M130 90 H490"/>'
        if kind=='poly': lines+='<path d="M150 50 Q310 130 470 50 M150 130 Q310 50 470 130" stroke-dasharray="5 5"/>'
    elif kind=='manifold': lines='<path d="M100 25 L280 70 L500 25 M100 90 H500 M100 155 L280 110 L500 155" fill="none"/>'
    return f'<svg viewBox="0 0 600 180" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Funktionsskizze, nicht maßstäblich"><g stroke="#137762" stroke-width="3">{lines}</g></svg>'

def refs(ids):
    return ' · '.join(f'<a href="{esc(s["url"])}">{esc(s["id"])}</a>' for s in sources if s['id'] in ids)

def book_html(ps,title):
    content=''
    for p in ps:
        body=''.join(f'<p>{esc(t)}</p>' for t in p['body'].split('\n'))
        kind=p.get('kind') or ('rocket' if p['page']==10 else 'axe' if p['page']==11 else 'multi' if p['page']==15 else 'poly' if p['page']==16 else 'manifold' if p['page']==17 else 'single')
        content+=f'<section class="page"><div class="eyebrow">Speaker / Entwicklungsatlas / {p["page"]:02d}</div><h1>{esc(p["title"])}</h1><h2>{esc(p["subtitle"])}</h2>{body}<div class="formula">{esc(p["formula"])}</div><p class="check">{esc(p["check"])}</p>{diagram(kind)}<div class="refs">Quellen: {refs(p["refs"])}</div><div class="folio">{p["page"]} / {len(ps)} · 12.11.2026 · Konzeptstudie ohne eigene Messdaten</div></section>'
    return f'<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title><style>{CSS}</style><header><b>{title}</b><nav><a href="../configurator/index.html">Konfigurator</a><a href="designkatalog.html">Designkatalog</a><a href="fachbroschuere.pdf">PDF</a><a href="quellen.md">Quellenregister</a></nav></header>{content}</html>'

# Minimal PDF writer. CP1252 text is escaped to ASCII octal; all bytes remain UTF-8-safe
# for the GitHub text-file API. No binary font or third-party assets are embedded.
REPLACE={'λ':'lambda','ρ':'rho','π':'pi','θ':'theta','φ':'phi','Φ':'Phi','Δ':'Delta','Σ':'Summe','√':'sqrt','≈':'~','≤':'<=','≥':'>=','→':'->','−':'-','∝':'~','ψ':'psi','²':'^2','³':'^3','⁻':'-','⁶':'6','½':'1/2','∫':'Integral','Ω':'Ohm','·':' * '}
def plain(t):
    for a,b in REPLACE.items():t=t.replace(a,b)
    return t
def pdfstr(t):
    b=plain(t).encode('cp1252',errors='replace')
    return ''.join(chr(c) if 32<=c<127 and c not in (40,41,92) else '\\%03o'%c for c in b)
def make_pdf(ps,path):
    objects=['<< /Type /Catalog /Pages 2 0 R >>','', '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>','<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>']
    kids=[]
    for p in ps:
        ops=[]
        def text(x,y,t,size=11,bold=False,color='0.06 0.16 0.18'):
            ops.append(f'BT /F{2 if bold else 1} {size} Tf {color} rg 1 0 0 1 {x} {y} Tm ({pdfstr(t)}) Tj ET')
        ops.append('0.06 0.16 0.18 rg 0 780 595 62 re f')
        text(50,807,'SPEAKER / ENTWICKLUNGSATLAS',11,True,'0.65 0.9 0.79')
        y=746
        for line in textwrap.wrap(p['title'],33):text(50,y,line,25,True);y-=30
        for line in textwrap.wrap(p['subtitle'],78):text(50,y-5,line,12);y-=17
        y-=18
        for para in p['body'].split('\n'):
            for line in textwrap.wrap(plain(para),87):text(50,y,line,10.5);y-=15
            y-=10
        if y<285: raise ValueError(f'Text overflow page {p["page"]}: {y}')
        fy=min(y-8,310)
        ops.append(f'0.9 0.96 0.92 rg 45 {fy-61} 505 70 re f')
        for i,line in enumerate(textwrap.wrap(plain(p['formula']),83)):text(57,fy-10-i*15,line,11,True)
        cy=fy-82
        for line in textwrap.wrap(plain(p['check']),88):text(50,cy,line,10);cy-=14
        # Vector concept illustration: all dimensions intentionally schematic.
        ops.append('0.1 0.45 0.36 RG 2 w 90 90 m 220 175 l 510 175 l 510 70 l 220 70 l h S')
        kind=p.get('kind') or ('rocket' if p['page']==10 else 'axe' if p['page']==11 else 'multi' if p['page']==15 else 'poly' if p['page']==16 else 'manifold' if p['page']==17 else 'single')
        if kind in ('rocket','axe'):ops.append('180 122 m 340 157 l 430 122 l 340 88 l h S')
        if kind in ('multi','poly'):ops.append('250 70 m 250 175 l S 370 70 m 370 175 l S 220 122 m 510 122 l S')
        if kind=='manifold':ops.append('90 175 m 220 140 l S 90 70 m 220 105 l S 90 122 m 510 122 l S')
        text(50,52,'Funktionsskizze: schematisch, keine Fertigungskontur.',8)
        actual_sources=[s for s in sources if s['id'] in p['refs']]
        text(50,35,'Quellen:',7)
        for i,s in enumerate(actual_sources):text(85+i*26,35,s['id'],7)
        text(450,20,f'{p["page"]} / {len(ps)}',9)
        stream='\n'.join(ops)+'\n'
        sid=len(objects)+1;objects.append(f'<< /Length {len(stream.encode("ascii"))} >>\nstream\n{stream}endstream')
        annotations=[]
        for i,source in enumerate(actual_sources):
            aid=len(objects)+1;objects.append(f'<< /Type /Annot /Subtype /Link /Rect [{85+i*26} 30 {110+i*26} 43] /Border [0 0 0] /A << /S /URI /URI ({pdfstr(source["url"])}) >> >>');annotations.append(f'{aid} 0 R')
        pid=len(objects)+1;objects.append(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents {sid} 0 R /Annots [{" ".join(annotations)}] >>');kids.append(f'{pid} 0 R')
    objects[1]=f'<< /Type /Pages /Count {len(kids)} /Kids [{" ".join(kids)}] >>'
    data='%PDF-1.4\n% ASCII edition\n';offsets=[0]
    for i,o in enumerate(objects,1):offsets.append(len(data.encode('ascii')));data+=f'{i} 0 obj\n{o}\nendobj\n'
    start=len(data.encode('ascii'));data+=f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'
    data+=''.join(f'{n:010d} 00000 n \n' for n in offsets[1:]);data+=f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n'
    path.write_text(data,encoding='ascii')

def dimensions(h,v,lo,d):
    w=max(d+.01,.603*343/lo/math.sin(math.radians(h/2)))
    height=max(d+.01,.603*343/lo/math.sin(math.radians(v/2)))
    length=max((w-d)/(2*math.tan(math.radians(h/2))),(height-d)/(2*math.tan(math.radians(v/2))))
    return f'W {w*1000:.1f} × H {height*1000:.1f} × L {length*1000:.1f} mm'

out=ROOT/'docs';out.mkdir(exist_ok=True)
(out/'fachbroschuere.html').write_text(book_html(pages,'Horn-Waveguides · Fachbroschüre'),encoding='utf-8')
(out/'fachbroschuere.md').write_text('# Horn-Waveguides · Fachbroschüre\n\n'+ '\n\n---\n\n'.join(f'## Seite {p["page"]}: {p["title"]}\n\n{p["subtitle"]}\n\n{p["body"]}\n\n**Formel / Modell:** {p["formula"]}\n\n**Prüfpunkt:** {p["check"]}\n\nQuellen: '+', '.join(p['refs']) for p in pages)+'\n\n[Quellenregister](quellen.md)\n',encoding='utf-8')
make_pdf(pages,out/'fachbroschuere.pdf')
catalog=[]
for i,(kind,title,sub,body,params,risk,next_step,h,v,lo,hi,di) in enumerate(families,1):
    dims=dimensions(h,v,lo,drivers[di]['throat_mm']/1000)
    catalog.append(dict(page=i,kind=kind,title=title,subtitle=sub,body=body+'\nParameter: '+params+'.\nEntwicklungsrisiken: '+risk+'\nNächster Nachweis: '+next_step,formula=dims,check='E · eigene Konzeptstudie; Außenmaße nach Aperturmodell, keine geprüfte Innengeometrie. Familienzeichnung nicht maßstäblich.',refs=['T2' if kind in ('rocket','manifold') else 'P2' if kind=='axe' else 'T1' if kind=='poly' else 'A2',drivers[di]['source']]))
catalog_html=book_html(catalog,'Waveguide-Designkatalog · 6 Familien')
(out/'designkatalog.html').write_text(catalog_html,encoding='utf-8')
make_pdf(catalog,out/'designkatalog.pdf')
(out/'designkatalog.md').write_text('# Designkatalog · sechs Konzeptfamilien\n\n'+ '\n\n---\n\n'.join(f'## {p["title"]}\n\n{p["subtitle"]}\n\n{p["body"]}\n\n**Referenzhülle:** {p["formula"]}\n\n{p["check"]}' for p in catalog)+'\n\n[Quellen](quellen.md) · [Illustrierte Ausgabe](designkatalog.html)\n',encoding='utf-8')
(out/'quellen.md').write_text('# Quellenregister\n\nRecherche: 12.11.2026. Primärquellen, Zugriffslücken ausdrücklich markiert. Keine eigenen Messdaten. Quelleninhalte wurden zusammengefasst, keine Zeichnungen kopiert.\n\n'+ '\n\n'.join(f'## {s["id"]} · {s["title"]}\n\n[{s["title"]}]({s["url"]})\n\n{s["note"]}' for s in sources)+'\n',encoding='utf-8')

template=(ROOT/'configurator/template.html').read_text()
# Inline classic script makes file:// opening work without module-CORS or fetch.
core=(ROOT/'configurator/core.mjs').read_text().replace('export ','')
app=(ROOT/'configurator/app.mjs').read_text().split('\n',1)[1]
app=app.replace('</script','<\\/script')
template=template.replace('<!--DATA-->',f'<script id="drivers" type="application/json">{json.dumps(drivers,ensure_ascii=False)}</script><script id="sources" type="application/json">{json.dumps(sources,ensure_ascii=False)}</script>')
template=template.replace('<!--APP-->',f'<script>{core}\n{app}</script>')
(ROOT/'configurator/index.html').write_text(template,encoding='utf-8')
print('Erzeugt: 30-seitige Fachbroschüre, 6-seitiger Designkatalog, Quellenregister und Offline-Konfigurator.')
