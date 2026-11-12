"""Own parametric concept meshes, OBJ exports and vector renderings, in millimetres.

Shells are closed material volumes around OPEN acoustic channels. Multiple parts
remain separate closed components; no Boolean union or acoustic solution is implied.
"""
from pathlib import Path
import math, json, html

N = 32
STEPS = 8
PALETTE = [(36,96,103),(80,155,151),(151,217,188),(227,156,83)]

def sub(a,b): return [a[i]-b[i] for i in range(3)]
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def unit(v):
    size=math.sqrt(dot(v,v))
    return [x/(size or 1) for x in v]

class Mesh:
    def __init__(self): self.vertices=[]; self.faces=[]; self.parts=[]
    def add(self,verts,faces,name):
        # Keep individual bodies consistently outward-oriented.
        volume=sum(dot(verts[a],cross(verts[b],verts[c])) for a,b,c,_ in faces)/6
        if volume<0: faces=[(a,c,b,m) for a,b,c,m in faces]
        start=len(self.vertices); face_start=len(self.faces)
        self.vertices.extend([[round(v,6) for v in p] for p in verts])
        self.faces.extend([[a+start,b+start,c+start,m] for a,b,c,m in faces])
        self.parts.append({'name':name,'face_start':face_start,'face_count':len(faces)})

def section(a,b,n,theta):
    # Polar-ray sampling avoids a cluster of nearly coincident vertices at corners.
    c,s=math.cos(theta),math.sin(theta)
    if n==0:
        q=(theta/(2*math.pi)*4)%4
        if q<1:return [a,b*(2*q-1)]
        if q<2:return [a*(3-2*q),b]
        if q<3:return [-a,b*(5-2*q)]
        return [a*(2*q-7),-b]
    r=(abs(c/a)**n+abs(s/b)**n)**(-1/n)
    return [r*c,r*s]

def shell(mesh,profile,name,wall=4,sides=N,steps=STEPS):
    """profile(t) -> a,b,n,cx,cy,z; wall is a SEMIAXIS offset, not normal thickness."""
    verts=[]; faces=[]; rings=steps+1; layer=rings*sides
    for outer in (False,True):
        for j in range(rings):
            a,b,n,cx,cy,z=profile(j/steps)
            if outer:a+=wall;b+=wall
            for i in range(sides):
                x,y=section(a,b,n,2*math.pi*i/sides)
                verts.append([x+cx,y+cy,z])
    for j in range(steps):
        for i in range(sides):
            k=(i+1)%sides;a=j*sides+i;b=j*sides+k;c=(j+1)*sides+i;d=(j+1)*sides+k
            faces.extend([(a,c,b,1),(b,c,d,1)])
            a+=layer;b+=layer;c+=layer;d+=layer
            faces.extend([(a,b,c,0),(b,d,c,0)])
    for i in range(sides):
        k=(i+1)%sides
        faces.extend([(i,k,layer+i,2),(k,layer+k,layer+i,2)])
        a=steps*sides+i;b=steps*sides+k
        faces.extend([(a,a+layer,b,2),(b,a+layer,b+layer,2)])
    mesh.add(verts,faces,name)

def body(mesh,rings,name,exponent=2):
    verts=[];faces=[]
    for z,a,b in rings:
        for i in range(N):
            x,y=section(a,b,exponent,2*math.pi*i/N);verts.append([x,y,z])
    for j in range(len(rings)-1):
        for i in range(N):
            k=(i+1)%N;a=j*N+i;b=j*N+k;c=(j+1)*N+i;d=(j+1)*N+k
            faces.extend([(a,b,c,3),(b,d,c,3)])
    for j,flip in [(0,True),(len(rings)-1,False)]:
        pole=len(verts);verts.append([0,0,rings[j][0]])
        for i in range(N):
            a=j*N+i;b=j*N+(i+1)%N
            faces.append((pole,b,a,3) if flip else (pole,a,b,3))
    mesh.add(verts,faces,name)

def generate(c):
    mesh=Mesh();r=c['throat']/2;W,H,L=c['width'],c['height'],c['length'];kind=c['geometry']
    def loft(t,nend=8):
        smooth=t*t*(3-2*t)
        return r+(W/2-r)*t,r+(H/2-r)*t,2+(nend-2)*smooth,0,0,L*t
    if kind in ('round_rect','superellipse','slot'):
        shell(mesh,lambda t:loft(t,4 if kind=='superellipse' else 8),'shell')
    elif kind in ('round','ellipse'):
        shell(mesh,lambda t:(r+(W/2-r)*t,r+(H/2-r)*t,2,0,0,L*t),'shell')
    elif kind=='os':
        shell(mesh,lambda t:(math.sqrt(r*r+(L*t)**2),math.sqrt(r*r+(L*t)**2),2,0,0,L*t),'shell')
    elif kind=='rocket':
        shell(mesh,lambda t:(r+(W/2-r)*t,r+(H/2-r)*t,2,0,0,L*t),'shell')
        body(mesh,[(L*.12,8,8),(L*.28,33,33),(L*.5,42,42),(L*.7,25,25),(L*.88,1.5,1.5)],'rocket_insert')
    elif kind=='axe':
        shell(mesh,loft,'shell')
        body(mesh,[(L*.16,8,4),(L*.33,36,13),(L*.55,62,19),(L*.82,2,2)],'axe_insert',4)
    elif kind in ('multi','poly'):
        for iy in range(2):
            for ix in range(3):
                cx=(ix-1)*108;cy=(iy-.5)*108
                def cell(t,cx=cx,cy=cy):
                    spread=(.52+.48*t) if kind=='multi' else (.45+.55*t*t*(3-2*t))
                    # Each opening 100x100; outer offset +4 leaves 0 mm at full pitch.
                    return 9+41*t,9+41*t,2+6*t,spread*cx,spread*cy,L*t
                shell(mesh,cell,f'cell_{ix+1}_{iy+1}',wall=3,sides=24,steps=6)
    elif kind=='prism':
        shell(mesh,lambda t:(20+100*t,12+18*t,0,0,0,L*t),'prismatic_shell',sides=16,steps=2)
    elif kind=='manifold':
        for index,cx in enumerate((-55,0,55)):
            shell(mesh,lambda t,cx=cx:(r+(22-r)*t,r+(12-r)*t,2+6*t,cx,0,160*t),f'input_{index+1}',wall=3,sides=24,steps=6)
        shell(mesh,lambda t:(80+70*t,15+75*t,8,0,0,190+200*t),'common_horn',wall=4)
    else:raise ValueError(kind)
    return mesh

def obj(mesh,c):
    lines=[f'# Speaker concept {c["id"]}; units mm; NOT acoustically validated','# Outer/inner surfaces bound closed material shells; acoustic ports are open.']
    lines += ['v '+' '.join(f'{v:.6f}' for v in p) for p in mesh.vertices]
    starts={p['face_start']:p['name'] for p in mesh.parts}
    for i,(a,b,c_,material) in enumerate(mesh.faces):
        if i in starts:lines.append('g '+starts[i])
        lines.append(f'f {a+1} {b+1} {c_+1}')
    return '\n'.join(lines)+'\n'

def stl(mesh,c):
    lines=['solid speaker_'+c['id']]
    for a,b,c_,_ in mesh.faces:
        vertices=[mesh.vertices[i] for i in (a,b,c_)]
        normal=unit(cross(sub(vertices[1],vertices[0]),sub(vertices[2],vertices[0])))
        lines+=['facet normal '+' '.join(f'{v:.8g}' for v in normal),'outer loop']
        lines+=['vertex '+' '.join(f'{v:.6f}' for v in p) for p in vertices]
        lines+=['endloop','endfacet']
    return '\n'.join(lines+['endsolid speaker_'+c['id']])+'\n'

def projection(mesh):
    yaw,pitch=math.radians(-32),math.radians(25)
    u=[math.cos(yaw),0,math.sin(yaw)]
    v=[-math.sin(yaw)*math.sin(pitch),math.cos(pitch),math.cos(yaw)*math.sin(pitch)]
    view=cross(u,v)
    pts=[[dot(p,u),-dot(p,v),dot(p,view)] for p in mesh.vertices]
    light=unit([-.4,.7,.8]);polys=[]
    for a,b,c,m in mesh.faces:
        n=unit(cross(sub(mesh.vertices[b],mesh.vertices[a]),sub(mesh.vertices[c],mesh.vertices[a])))
        if dot(n,view)<=0:continue
        # Two-sided technical rendering, including the acoustic inner surface.
        strength=.42+.58*abs(dot(n,light))
        color=tuple(round(ch*strength) for ch in PALETTE[m])
        polys.append({'p':[pts[a][:2],pts[b][:2],pts[c][:2]],'z':sum(pts[i][2] for i in (a,b,c))/3,'color':color})
    return sorted(polys,key=lambda p:p['z'])

def fit(polys,x,y,w,h):
    pts=[q for p in polys for q in p['p']]
    minx,miny=min(p[0] for p in pts),min(p[1] for p in pts)
    maxx,maxy=max(p[0] for p in pts),max(p[1] for p in pts)
    s=min(w/(maxx-minx),h/(maxy-miny))
    dx=x+(w-(maxx-minx)*s)/2;dy=y+(h-(maxy-miny)*s)/2
    return [([(dx+(px-minx)*s,dy+(py-miny)*s) for px,py in p['p']],p['color']) for p in polys]

def svg(mesh,c):
    polys=fit(projection(mesh),40,30,680,380)
    paths=''.join(f'<path d="M{p[0][0]:.2f},{p[0][1]:.2f} L{p[1][0]:.2f},{p[1][1]:.2f} L{p[2][0]:.2f},{p[2][1]:.2f}Z" fill="rgb{color}" stroke="rgb{color}" stroke-width=".25"/>' for p,color in polys)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 460" role="img"><title>{html.escape(c["title"])} – Rendering des exportierten OBJ-Modells</title><rect width="760" height="460" rx="16" fill="#10282d"/>{paths}<text x="28" y="440" fill="#b4d8c4" font-size="13" font-family="sans-serif">{c["code"]} · Eigenes 3D-Konzept · mm · Keine akustische Freigabe</text></svg>'

def pdf_model(polys,x,y,w,h):
    ops=[]
    for pts,color in fit(polys,x,y,w,h):
        rgb=' '.join(f'{v/255:.3f}' for v in color)
        ops.append(rgb+' rg '+rgb+' RG 0.2 w '+f'{pts[0][0]:.2f} {842-pts[0][1]:.2f} m {pts[1][0]:.2f} {842-pts[1][1]:.2f} l {pts[2][0]:.2f} {842-pts[2][1]:.2f} l h B')
    return '\n'.join(ops)

def build_catalog(root,make_pdf):
    concepts=json.loads((root/'data/catalog.json').read_text());sources=json.loads((root/'data/sources.json').read_text())
    result_path=root/'validation/results.json'
    validation={r['id']:r for r in json.loads(result_path.read_text())['screening']} if result_path.exists() else {}
    modeldir=root/'models';renders=root/'docs/renders';modeldir.mkdir(exist_ok=True);renders.mkdir(exist_ok=True)
    library={};cards=[];markdown=['# Designkatalog · 12 Konzepte mit 3D-Modellen','Eigene Geometriestudien; Modellmaße sind frei gewählte Katalogparameter und keine Herstellermaße oder Abstrahlvorhersagen. Runde/ovale Hörner und Waveformer zur Wellenfrontumformung erfüllen unterschiedliche Aufgaben.','[PDF](designkatalog.pdf) · [Drehbare HTML-Ansicht](designkatalog.html) · [Modellhinweise](../models/README.md)'];pdf=[]
    for i,c in enumerate(concepts,1):
        review=validation.get(c['id']);status=review.get('validation_status','Numerische Teilprüfung') if review else 'Noch keine numerische Prüfung'
        review_note='LaVoce-Prüfstand: '+status
        if review:
            review_note+='; Prüfkandidat '+review['driver_model']+'.'
            if review.get('outlet_tessellation_area_error_fraction',0)>.05:review_note+=f' Achtung: {review["outlet_tessellation_area_error_fraction"]*100:.1f}% Flächendefizit im groben Mundnetz.'
        mesh=generate(c);library[c['id']]={'vertices':mesh.vertices,'faces':mesh.faces,'parts':mesh.parts,'title':c['title']}
        (modeldir/(c['id']+'.obj')).write_text(obj(mesh,c),encoding='ascii')
        (modeldir/(c['id']+'.stl')).write_text(stl(mesh,c),encoding='ascii')
        (renders/(c['id']+'.svg')).write_text(svg(mesh,c))
        dims=f'{c["width"]:g} × {c["height"]:g} × {c["length"]:g} mm'
        ref=' · '.join(f'<a href="{html.escape(s["url"])}">{s["id"]}</a>' for s in sources if s['id'] in c['refs'])
        cards.append(f'''<article class="card" id="{c['id']}" data-group="{c['group']}"><div class="card-head"><span>{c['group']} / {c['code']}</span><h2>{html.escape(c['title'])}</h2></div><button class="render-button" data-open="{c['id']}" aria-label="{html.escape(c['title'])} als drehbares 3D-Modell öffnen"><img src="renders/{c['id']}.svg" alt="3D-Rendering: {html.escape(c['title'])}" loading="lazy"><span>3D drehen ↗</span></button><div class="card-body"><p>{html.escape(c['description'])}</p><dl><dt>Modell-W × H × L, lichte Endmaße / axiale Länge</dt><dd>{dims}</dd><dt>Treiberbezug</dt><dd>{html.escape(c['driver'])}</dd><dt>Band / Einordnung</dt><dd>{html.escape(c['band'])}</dd></dl><p class="formula">{html.escape(c['formula'])}</p><details><summary>Entwicklungsstand und Grenzen</summary><p>{html.escape(c['risk'])}</p><p>{html.escape(c['missing'])}</p><p>Wandmodell: +4 mm auf die Halbachsen (+3 mm bei Zell-/Eingangskanälen); keine konstante Normalwandstärke. Keine Flanschbohrungen.</p><p>Quellen: {ref}</p></details><div class="actions"><button data-open="{c['id']}">3D-Ansicht</button><a href="../models/{c['id']}.obj" download>OBJ ↓</a><button data-stl="{c['id']}">STL ↓</button></div></div></article>''')
        cards[-1]=cards[-1].replace('<div class="card-body">','<div class="card-body"><p class="formula"><strong>'+html.escape(review_note)+'</strong> <a href="../validation/REPORT.md">Prüfbericht ↗</a></p>')
        markdown += [f'## {c["code"]} · {c["title"]}',f'![3D-Rendering des Modells](renders/{c["id"]}.svg)',c['description'],f'**Modellmaße:** {dims}. **Treiberbezug:** {c["driver"]}.',f'**Band:** {c["band"]}',f'**Formel:** {c["formula"]}',f'**Prüfen:** {c["risk"]}',f'**Noch offen:** {c["missing"]}',f'**{review_note}** [Numerische Ergebnisse](../validation/REPORT.md)',f'[3D-Modell OBJ](../models/{c["id"]}.obj) · [STL mit GitHub-Vorschau](../models/{c["id"]}.stl) · [Interaktiv](designkatalog.html#{c["id"]}) · Quellen: '+', '.join(c['refs'])]
        pdf.append(dict(page=i,title=c['title'],subtitle=f'{c["code"]} / {c["group"]} / eigenes Konzeptmodell',body=c['description']+'\nTreiberbezug: '+c['driver']+'.\n'+c['missing'],formula=dims+' (Modellmaße). '+c['formula'],check=c['risk']+' '+review_note,refs=c['refs'],polygons=projection(mesh)))
    (modeldir/'catalog-meshes.js').write_text('/* Own concept meshes; coordinates mm; not acoustically validated. */\nwindow.SPEAKER_MODELS='+json.dumps(library,separators=(',',':'),ensure_ascii=False)+';\n')
    template=(root/'scripts/catalog-template.html').read_text()
    (root/'docs/designkatalog.html').write_text(template.replace('<!--CARDS-->','\n'.join(cards)))
    (root/'docs/designkatalog.md').write_text('\n\n'.join(markdown)+'\n')
    make_pdf(pdf,root/'docs/designkatalog.pdf')
    print(f'Katalog: {len(concepts)} OBJ/STL-Modellpaare, {len(concepts)} SVG-Renderings und {len(concepts)} PDF-Seiten.')
