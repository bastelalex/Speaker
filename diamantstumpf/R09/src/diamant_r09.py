"""Full-width signature insert studies, in millimetres."""
import base64
import csv
import gzip
import json
import math
from pathlib import Path
import re
import sys
import zipfile

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "outputs"
ROOT = HERE.parent.parent
for revision in ("R08", "R07"):
    sibling = ROOT / revision / "src"
    if sibling.is_dir():
        sys.path.insert(0, str(sibling))

import diamant_r07 as r7
import diamant_r08 as r8

r = r7.r
np = r.np
BOX, UNION = r.box, r.union
PREFIX = "Diamantstumpf_R09"
REMOVED = {
    c["id"] for c in r7.portrait_cells(True)
    if c["id"].startswith("S")
}
PLATE_W, PLATE_H = 539, 273
VARIANTS = {
    "S1": dict(name="Schwingenmund", w=520, h=246, d=298, up=115, p=4.1, split=0,
               description="Ein weiter Mund mit stetig gerundeter Lippe, nach unten öffnender Kontur und zwei abnehmbaren Leitprismen."),
    "S2": dict(name="Fächer Vier", w=518, h=246, d=315, up=116, p=5.1, split=3,
               description="Vier sichtbare Fächersegmente, gemeinsamer Hals. Drei Leitstege teilen die vordere Expansion."),
    "S3": dict(name="Vierfach-Eintritt", w=516, h=246, d=301, up=115, p=3.6, split=0,
               description="Solana-inspirierte Eigengeometrie. Vier seitliche Tiefmittelton-Eintritte speisen den gemeinsamen Mund, Hochton sitzt am Hals."),
}
PORT_R = 15.5
PORT_D = 152
PORT_Z = 23


def section(key, d, extra=0):
    a = VARIANTS[key]
    u = 1 - min(1, max(0, d / a["d"]))
    last = max(0, (u-.83)/.17)
    if key == "S2":
        f = .21*u + .79*u**1.61
    else:
        f = .21*u + .66*u**1.56 + .13*last**3
    v = .27*u + .65*u**1.68 + .08*last**3
    w = 36 + (a["w"]-36)*f
    top = 18+(a["up"]-18)*v
    bottom = 18+(a["h"]-a["up"]-18)*v
    ring=[]
    for angle in np.linspace(0,math.tau,96,endpoint=False):
        cs,sn=math.cos(angle),math.sin(angle)
        limit=2.34 if sn>=0 else a["p"]
        p=2+(limit-2)*u**1.15
        x=(w+extra)/2*math.copysign(abs(cs)**(2/p),cs)
        z=((top if sn>=0 else bottom)+extra/2)*math.copysign(abs(sn)**(2/p),sn)
        ring.append((x,z))
    return ring


def horn_air(key, extra=0, extended=False):
    d = VARIANTS[key]["d"]
    steps = np.unique(np.r_[np.linspace(0,d,65), 5.])
    if extended:
        steps = np.r_[-.8,steps,d+11]
    return r.loft([(float(y),section(key,float(y),extra)) for y in steps])


def bay():
    return BOX(-270,270,-2,9,463,737)


def shell_front():
    remaining = [c for c in r7.portrait_cells(True) if c["id"] not in REMOVED]
    cutters = [r7.mouth_duct(c,extend=True) for c in remaining]
    air = UNION(cutters)
    retained_skin = UNION(r7.mouth_duct(c,5) for c in remaining)
    opening = bay()
    frame = r7.section(lambda d:-r7.inside_center(d),r7.inside_center,0,5,18,1182)
    face = frame-UNION([air,opening])
    walls = (retained_skin ^ BOX(-300,300,0,270,0,1200)) - UNION([face,air,opening])
    assert len(remaining) == 42 and len(REMOVED) == 12
    return face,walls,air


def xport(radius, low, high, z):
    return r.mf.Manifold.cylinder(high-low,radius,circular_segments=80).rotate((0,90,0)).translate((low,PORT_D,z))


def ports():
    tubes,bores,motors=[],[],[]
    for z in (-PORT_Z,PORT_Z):
        for sign in (-1,1):
            mirror = lambda solid: solid if sign > 0 else solid.mirror((1,0,0))
            tubes.append(mirror(xport(PORT_R+3,45,139,z)))
            bores.append(mirror(xport(PORT_R,45,142,z)))
            # Clearance placeholders for an angled plenum and a candidate driver,
            # shown in inspection only. They are deliberately excluded from STL.
            motors.append(mirror(xport(20,145,182,z)))
    return UNION(tubes), UNION(bores), UNION(motors), bores


def fanned_vanes():
    solids=[]
    for i in (-1,0,1):
        stations=[]
        for d in np.linspace(0,150,29):
            contour=np.array(section("S2",float(d)))
            x=i*.51*contour[:,0].max()
            cut=np.roll(contour,-1,axis=0)
            crossings=[]
            for (x0,z0),(x1,z1) in zip(contour,cut):
                if min(x0,x1)<=x<max(x0,x1):
                    crossings.append(z0+(z1-z0)*(x-x0)/(x1-x0))
            assert len(crossings)==2
            t=2.1-1.15*d/150
            stations.append((float(d),r.rectangle(x-t/2,x+t/2,min(crossings)-.95,max(crossings)+.95)))
        solids.append(r.loft(stations))
    return UNION(solids)


def signature_prisms():
    stations=[(-101,78,14,18,0),(-77,84,26,53,8),(-26,91,36,81,10),
              (33,89,35,69,7),(75,82,22,36,2),(92,77,12,16,0)]
    pieces=[]
    for sign in (-1,1):
        rings=[(z,[(x,-d) for x,d in r8.wedge_section(x0,w,tip,ridge)])
               for z,x0,w,tip,ridge in stations]
        piece=r.loft(rings).rotate((90,0,0))
        piece=piece+BOX(74,81,-8,-1.25,-133,-99)+BOX(74,81,-8,-1.25,90,126)
        pieces.append(piece if sign==1 else piece.mirror((1,0,0)))
    return UNION(pieces)


def prism_bores():
    return UNION(r.cylinder(1.4,-9,6,x,z) for x in (-77,77) for z in (-131,123))


def panel_local():
    return BOX(-PLATE_W/2,PLATE_W/2,0,5,-PLATE_H/2,PLATE_H/2)


def signature(key, obstacles):
    a=VARIANTS[key]
    inner=horn_air(key,extended=True)
    outer=horn_air(key,5.4)
    d=a["d"]
    mount=r.cylinder(69,d-.8,d+9)
    screws=UNION(r.cylinder(3.3,d-2,d+10,x*50.8/math.sqrt(2),z*50.8/math.sqrt(2))
                 for x in (-1,1) for z in (-1,1))
    anchor_points=[(x,z) for x in (-263,0,263) for z in (-132,129)]
    mounts=UNION(r.cylinder(2.75,-1,6,x,z) for x,z in anchor_points)
    block=panel_local()+outer+mount
    additions={}
    if key=="S3":
        tubes,bores,drives,individual=ports()
        assert all((b^inner).volume()>100 for b in individual)
        solid=(block+tubes)-UNION([inner,bores,mounts,screws])
        additions["entries"]=bores-inner
        additions["drivers"]=drives
    else:
        solid=block-UNION([inner,mounts,screws])
    if key=="S2":
        solid=solid+fanned_vanes()
    if key=="S1":
        holes=prism_bores()
        assert (holes^solid).volume()>20
        solid=solid-holes
        additions["reflectors"]=signature_prisms()-holes
    wall,air,face,wood=obstacles
    # Relieve the rear lip where adjacent ducts start to curve inward.
    solid=solid-air.translate((0,0,-600))
    fragments=solid.decompose()
    if len(fragments)!=1:
        print(key,[(round(f.volume(),4),tuple(round(v,2) for v in f.bounding_box())) for f in fragments],flush=True)
    assert len(fragments)==1,key
    for part in (solid,*[p for n,p in additions.items() if n=="reflectors"]):
        absolute=part.translate((0,0,600))
        for name,other in (("wall",wall),("air",air),("face",face),("wood",wood)):
            cross=absolute^other
            assert cross.volume()<.02,(key,name,cross.volume(),cross.bounding_box())
    mouth=np.array(section(key,0))
    x,z=mouth.T
    area=abs(np.dot(x,np.roll(z,1))-np.dot(z,np.roll(x,1)))/200
    return solid,additions,round(area)


def stl(solid):
    return r7.cassette_stl(solid)


def model_data():
    local=OUT/"Diamantstumpf_R08_Prismenplatte.html"
    source=local if local.exists() else ROOT/"R08"/local.name
    match=re.search(r'<script id="model-data" type="application/octet-stream">([A-Za-z0-9+/=]+)</script>',
                    source.read_text(encoding="utf-8"))
    return json.loads(gzip.decompress(base64.b64decode(match[1])))


def pack(solid):
    return r.data_mesh(r.to_mesh(solid))


def build():
    OUT.mkdir(exist_ok=True)
    fixed_face, fixed_wall, fixed_air = shell_front()
    wood=next(s for name,s,*_ in r7.portrait_front(True) if name.startswith("umlaufender"))
    data=model_data()
    data["wideFront"]=[pack(fixed_face),pack(fixed_wall)]
    data["replacedCells"]=sorted(REMOVED)
    data["signaturePlate"]=[PLATE_W,PLATE_H]
    data["signature"]={}
    records=[]
    with zipfile.ZipFile(OUT/f"{PREFIX}_Geometrien_STL.zip","w",zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("Front_42_Festzellen.stl",stl(fixed_face))
        archive.writestr("Kanaele_42_Festzellen.stl",stl(fixed_wall))
        for key,spec in VARIANTS.items():
            solid,extras,area=signature(key,(fixed_wall,fixed_air,fixed_face,wood))
            data["signature"][key]={k:v for k,v in spec.items() if k!="split"}
            data["signature"][key].update(mesh=pack(solid),area=area,
                **{n:pack(v) for n,v in extras.items()})
            archive.writestr(f"{key}_Horn.stl",stl(solid))
            if "reflectors" in extras:
                archive.writestr(f"{key}_Leitprismen.stl",stl(extras["reflectors"]))
            records.append([key,spec["name"],spec["w"],spec["h"],spec["d"],area,
                            4 if key=="S3" else 0, 2 if key=="S1" else spec["split"]])
        archive.writestr("Montage.txt",
            "STL in mm. X quer, Y Tiefe, Z hoch. S1–S3 liegen lokal um Z=0; "
            "für den Einbau Z um 600 mm verschieben. Restfront und Restkanäle nutzen Gehäusekoordinaten.\n"
            "Gehäusebreite 600 mm. Rechteckplatte 539 x 273 mm. Sechs Ø5,5-mm-Bohrungen im Hornrahmen. "
            "S1: vier Ø2,8-mm-Durchgänge durch Prismenhalter und Hornrahmen. "
            "Gegenlager, Dichtung, Einbaureihenfolge, Treiberschlitten und belastbare Bass-/MF-Rückkammern weiter auslegen.\n"
            "Bei S3 sind vier Durchlässe vorhanden. Konkrete Treiberaufnahme, Kammer, Adapter und DSP sind Studienaufgaben.\n")
    with (OUT/f"{PREFIX}_Geometriedaten.csv").open("w",encoding="utf-8-sig",newline="") as out:
        writer=csv.writer(out,delimiter=";")
        writer.writerow(["ID","Geometrie","Mund B mm","Mund H mm","Hals bis Front mm",
                         "Projizierte Bruttofläche cm²","Seiteneintritte","Leitkörper"])
        writer.writerows(records)
    prior=(r7.HERE/"diamant_r07.html").read_text(encoding="utf-8")
    studio=prior[prior.index("function studioEnvironment("):prior.index("function mount(){")]
    library=(r7.HERE/"three-face.min.js").read_text(encoding="utf-8")
    packed=base64.b64encode(gzip.compress(json.dumps(data,separators=(",",":"),ensure_ascii=False).encode(),
                                          mtime=0,compresslevel=6)).decode()
    template=(HERE/"diamant_r09.html").read_text(encoding="utf-8")
    (OUT/f"{PREFIX}_Signature.html").write_text(template.replace("/*THREE*/",library).replace("/*STUDIO*/",studio)
                                               .replace("/*DATA*/",packed),encoding="utf-8")
    print(records)


if __name__=="__main__":
    build()
