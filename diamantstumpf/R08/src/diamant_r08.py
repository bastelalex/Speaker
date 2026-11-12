"""The interchangeable central prism plate. All dimensions are in millimetres."""
import base64
import csv
import gzip
import json
from pathlib import Path
import re
import sys
import zipfile

HERE=Path(__file__).resolve().parent
SIBLING=HERE.parent.parent/"R07"
if (SIBLING/"src").is_dir():
    sys.path.insert(0,str(SIBLING/"src"))

import diamant_r07 as r7

r=r7.r
OUT=HERE.parent/"outputs"
PREFIX="Diamantstumpf_R08"
AXIS_HEIGHT=600
BACKING="A"
PRISMS={
    "P1": dict(name="Doppelprisma",description="Zwei spiegelbildliche, hohe Keile mit einer langen vorderen Kante.",
               stations=[(-91,40,10,16,1),(-69,40,19,40,2),(-28,39,27,72,4),
                         (34,39,26,69,4),(71,40,16,36,2),(91,40,10,16,1)]),
    "P2": dict(name="Scherenprisma",description="Zwei nach außen wandernde Grate. Die oberen und unteren Enden fächern verschieden auf.",
               stations=[(-92,32,10,20,-2),(-65,34,17,55,-4),(-24,39,27,95,-8),
                         (27,48,24,75,4),(65,55,17,44,8),(92,58,9,18,4)]),
    "P3": dict(name="Prisma Tief",description="Die beiden Grate sitzen weiter unten und laufen nach oben flacher aus.",
               stations=[(-94,43,10,24,3),(-70,41,24,69,6),(-40,41,28,87,6),
                         (5,41,25,65,5),(55,41,17,31,3),(93,43,10,14,1)]),
}


def bearing_plate():
    a=r7.HORN_VARIANTS[BACKING]
    mouth=r.superellipse(a["w"],a["h"],a["p"])
    return r.box(-135,135,-5,-.3,-135,135)-r.union([
        r.loft([(-6,mouth),(1,mouth)]),r7.fastener_bores(-6,1)])


def wedge_section(x,w,tip,ridge):
    """A bevelled hexagon viewed in the horizontal plane."""
    return [(x-w*.44,-2.1),(x+w*.44,-2.1),(x+w*.5,-9),
            (x+ridge+.55,-tip),(x+ridge-.55,-tip),(x-w*.5,-9)]


def prism_leaf(spec,side):
    st=spec["stations"]
    blade=r.loft([(z,[(x,-d) for x,d in wedge_section(x0,w,tip,ridge)])
                  for z,x0,w,tip,ridge in st]).rotate((90,0,0))
    ears=[]
    for (z,x,*_),end in ((st[0],-118),(st[-1],118)):
        z0,z1=sorted((z-(1.4 if z>0 else -1.4),end))
        ears.append(r.box(x-3.5,x+3.5,-8,-1.35,z0,z1))
    solid=blade+r.union(ears)
    assert len(solid.decompose())==1
    return solid if side>0 else solid.mirror((1,0,0))


def fasteners():
    centers=(-127,127)
    return r.union(r.cylinder(5.8,-8,-4.85,x,z)
                   for x in centers for z in centers)


def payload(mesh):
    return r.data_mesh(r.to_mesh(mesh))


def prism_data():
    plate=bearing_plate()
    backing=r7.horn_cassette(BACKING)
    pieces={}
    for key,spec in PRISMS.items():
        leaves=r.union(prism_leaf(spec,side) for side in (-1,1))
        unit=leaves+plate
        assert len(unit.decompose())==1,key
        assert (unit^backing).volume()<.01,key
        assert unit.bounding_box()[0]>=-135 and unit.bounding_box()[3]<=135
        depth=round(-unit.bounding_box()[1],1)
        pieces[key]=(unit,dict(name=spec["name"],description=spec["description"],
                              projection=depth,blades=payload(leaves)))
    return pieces,plate,backing


def read_prior():
    choices=(OUT/"Diamantstumpf_R07_Gesamtaufbau.html",SIBLING/"Diamantstumpf_R07_Gesamtaufbau.html")
    source=next((p for p in choices if p.exists()),None)
    if source is None:
        r7.build()
        source=r7.OUT/"Diamantstumpf_R07_Gesamtaufbau.html"
    pattern=r'<script id="model-data" type="application/octet-stream">([A-Za-z0-9+/=]+)</script>'
    match=re.search(pattern,source.read_text(encoding="utf-8"))
    assert match,source
    return json.loads(gzip.decompress(base64.b64decode(match[1])))


def build():
    OUT.mkdir(exist_ok=True)
    parts,plate,backing=prism_data()
    data=read_prior()
    data["prisms"]={key:obj for key,(_,obj) in parts.items()}
    data["prismPlate"]=payload(plate)
    data["prismFasteners"]=payload(fasteners())
    data["prismBacking"]=BACKING
    data["geometry"]["fixedCellCount"]=len(r7.portrait_cells(True))
    data["geometry"]["topHorn"]=r7.FEATURED
    raw=json.dumps(data,separators=(",",":"),ensure_ascii=False).encode()
    packed=base64.b64encode(gzip.compress(raw,mtime=0,compresslevel=6)).decode()
    template=(HERE/"diamant_r08.html").read_text(encoding="utf-8")
    prior=(r7.HERE/"diamant_r07.html").read_text(encoding="utf-8")
    studio=prior[prior.index("function studioEnvironment("):prior.index("function mount(){")]
    library=(r7.HERE/"three-face.min.js").read_text(encoding="utf-8")
    page=template.replace("/*THREE*/",library).replace("/*STUDIO*/",studio).replace("/*DATA*/",packed)
    (OUT/f"{PREFIX}_Prismenplatte.html").write_text(page,encoding="utf-8")
    with zipfile.ZipFile(OUT/f"{PREFIX}_Prismen_STL.zip","w",zipfile.ZIP_DEFLATED) as archive:
        for key,(unit,_) in parts.items():
            archive.writestr(f"Aufsatz_{key}.stl",r7.cassette_stl(unit))
        archive.writestr("Horn_A.stl",r7.cassette_stl(backing))
        archive.writestr("Kassettensitz.stl",r7.cassette_stl(r7.horn_seat()))
        archive.writestr("Montage.txt",
            "STL in mm. X quer, Y Tiefe, Z hoch. Y=0 ist die feste Blendenebene.\n"
            "270 x 270 mm, vier Durchgangsbohrungen Ø5,5 mm auf 254 x 254 mm.\n"
            "Der Aufsatz sitzt vor Konturhorn A. Die anderen elf Hornvarianten können "
            "als alternative Zentralkassetten in denselben Sitz.\n"
            "Senkung und Schraubenlänge an Material und Sitz anpassen. Akustischer Prototyp.\n")
    with (OUT/f"{PREFIX}_Prismenmasse.csv").open("w",encoding="utf-8-sig",newline="") as out:
        table=csv.writer(out,delimiter=";")
        table.writerow(["Variante","Name","Rahmen B mm","Rahmen H mm","Vorsprung vor Blende mm","Bohrbild mm"])
        for key,(_,obj) in parts.items():
            table.writerow([key,obj["name"],270,270,obj["projection"],254])
    print("Feste Zellen:",data["geometry"]["fixedCellCount"],"Bestandskassetten:",len(data["hornMeshes"]),
          "Prismenaufsätze:",len(parts))


if __name__=="__main__":
    build()
