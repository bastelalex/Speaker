"""Generate the SOLANAL folded waveguide from an atlas cross section."""
import base64
import csv
import gzip
from io import BytesIO
import json
import math as m
from pathlib import Path
import re
import sys

HERE=Path(__file__).resolve().parent
OUT=HERE.parent/"outputs"
ROOT=HERE.parent.parent
for revision in ("R10","R09","R08","R07"):
    src=ROOT/revision/"src"
    if src.is_dir():
        sys.path.insert(0,str(src))
import diamant_r09 as r9

r=r9.r
np=r9.np
PREFIX="Diamantstumpf_R11_SOLANAL"
SOURCE=HERE/"r11_scan"/"FJ2571.obj"
ANGLES=np.linspace(0,m.tau,192,endpoint=False)
FOLD_END=130


def cross(a,b):
    return a[...,0]*b[...,1]-a[...,1]*b[...,0]


def sample_section(mesh,z):
    edges=r.tm.intersections.mesh_plane(mesh,[0,0,1],[0,0,z])[:,:,:2]
    center=edges.reshape(-1,2).mean(axis=0)
    start=edges[:,0]-center
    segment=edges[:,1]-edges[:,0]
    radii=[]
    for angle in ANGLES:
        ray=np.array([m.cos(angle),m.sin(angle)])
        det=cross(ray,segment)
        active=np.abs(det)>1e-9
        t=cross(start[active],segment[active])/det[active]
        u=cross(start[active],ray)/det[active]
        hits=t[(t>0)&(u>=-1e-7)&(u<=1+1e-7)]
        if not len(hits):
            raise ValueError(f"Open section at z={z} and angle {angle}")
        radii.append(float(min(hits)))
    return np.array(radii)


def atlas_profiles():
    mesh=r.tm.load_mesh(SOURCE,file_type="obj")
    sections=[round(float(mesh.bounds[0,2]+offset),3) for offset in (7,9,11)]
    radii=np.array([sample_section(mesh,z) for z in sections])
    mean=(radii/radii.mean(axis=1,keepdims=True)).mean(axis=0)
    coeff=np.fft.rfft(mean)
    coeff[:3]=0
    coeff[13:]=0
    detail=np.fft.irfft(coeff,n=len(ANGLES))
    detail/=np.max(np.abs(detail))
    return sections,radii,mean,detail


def wall_ring(depth,extra,measured,detail):
    base=np.asarray(r9.section("S3",depth,extra))
    dense=np.empty((192,2))
    dense[::2]=base
    dense[1::2]=(base+np.roll(base,-1,axis=0))/2
    if 3<depth<FOLD_END:
        t=(depth-3)/(FOLD_END-3)
        swell=m.sin(m.pi*t)**1.48
        shape=8*ANGLES+.78*detail+1.06*(t-.32)*np.sin(2*ANGLES+.42)
        pleat=np.cos(shape)
        pleat=.77*pleat+.23*np.cos(2*shape+.65)
        ripple=.30*pleat+.09*detail+.13*(measured-1)
        form=1-swell*np.clip(.25-ripple,.025,.54)
        dense*=form[:,None]
    return dense.tolist()


def folded_horn(measured,detail):
    spec=r9.VARIANTS["S3"]
    d=spec["d"]
    steps=np.unique(np.r_[np.linspace(0,d,99),5,3,FOLD_END])
    inner=r.loft([(float(y),wall_ring(float(y),0,measured,detail))
                  for y in np.r_[-.8,steps,d+11]])
    outer=r.loft([(float(y),wall_ring(float(y),5.4,measured,detail)) for y in steps])
    tubes,bores,drives,individual=r9.ports()
    assert all((b^inner).volume()>100 for b in individual)
    assert r9.PORT_D-r9.PORT_R-3>FOLD_END
    bolts=r9.UNION(r.cylinder(3.3,d-2,d+10,x*50.8/m.sqrt(2),z*50.8/m.sqrt(2))
                   for x in (-1,1) for z in (-1,1))
    face_bolts=r9.UNION(r.cylinder(2.75,-1,6,x,z)
                        for x in (-263,0,263) for z in (-132,129))
    horn=r9.panel_local()+outer+r.cylinder(69,d-.8,d+9)+tubes
    face,wall,air=r9.shell_front()
    horn=horn-r9.UNION([inner,bores,bolts,face_bolts,air.translate((0,0,-600))])
    components=horn.decompose()
    if len(components)>1:
        horn=max(components,key=lambda component:component.volume())
        assert sum(c.volume() for c in components)-horn.volume()<1e-3, [c.volume() for c in components]
    mounted=horn.translate((0,0,600))
    assert (mounted^wall).volume()<.02 and (mounted^face).volume()<.02, (
        (mounted^wall).volume(),(mounted^face).volume(),(mounted^wall).bounding_box())
    assert (mounted^air).volume()<.02
    payload=r9.stl(horn)
    checked=r.tm.load_mesh(BytesIO(payload),file_type="stl")
    assert checked.is_watertight and checked.is_winding_consistent and checked.area_faces.min()>0
    return payload,r.data_mesh(checked),r9.pack(bores-inner),r9.pack(drives)


def main():
    previous=OUT/"Diamantstumpf_R10_SOLANAL.html"
    if not previous.is_file():
        previous=ROOT/"R10"/previous.name
    page=previous.read_text(encoding="utf-8")
    expression=r'(<script id="model-data" type="application/octet-stream">)([A-Za-z0-9+/=]+)(</script>)'
    match=re.search(expression,page)
    data=json.loads(gzip.decompress(base64.b64decode(match[2])))
    sections,radii,measured,detail=atlas_profiles()
    payload,mesh,entries,drives=folded_horn(measured,detail)
    record=dict(data["signature"]["S3"],name="SOLANAL Faltenhorn",mesh=mesh,
                description="Stark gewellter Hornverlauf aus drei Querschnitten des MRT-basierten BodyParts3D-Rektummodells. Acht konstruktiv verstärkte Falten, vier Seiteneintritte und gemeinsamer Mund.",
                entries=entries,drivers=drives)
    data["signature"]={"SF":record,**data["signature"]}
    packed=base64.b64encode(gzip.compress(json.dumps(data,separators=(",",":"),ensure_ascii=False).encode(),
                                         mtime=0,compresslevel=6)).decode()
    page=page[:match.start(2)]+packed+page[match.end(2):]
    replacements={
        "<title>SOLANAL · restless.audio · Diamantstumpf R10</title>":"<title>SOLANAL Faltenhorn · restless.audio · Diamantstumpf R11</title>",
        "Diamantstumpf R10</div><h1>SOLANAL</h1>":"Diamantstumpf R11</div><h1>SOLANAL Faltenhorn</h1>",
        "selected='SL',exploded":"selected='SF',exploded",
        "if(key==='SL'){":"if(key==='SF'){\n    group.add(new THREE.Mesh(geometry(spec.mesh,true),layerMat));\n  }else if(key==='SL'){",
        "window.r10State=":"window.r11State=",
        "selected==='SL'?[.09,.12,940":"['SL','SF'].includes(selected)?[.075,.10,940",
        "selected==='SL'?'Multiplex-Ansicht":"selected==='SF'?'MRT-basierter Atlasquerschnitt mit verstärkten Falten. Ziehen zum Drehen.':\n      selected==='SL'?'Multiplex-Ansicht",
        '<p class="small">Geometriestudie. Abstrahlung und Übergänge zwischen den Wegen bleiben zu messen.</p>':
            '<p class="small">Geometriestudie. Abstrahlung und Übergänge zwischen den Wegen bleiben zu messen.</p>\n        <p class="small" id="atlas-credit">BodyParts3D, © The Database Center for Life Science, <a href="https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html">CC BY 4.0</a>. Querschnitte verstärkt und auf das Hornprofil übertragen.</p>',
        "solanal.hidden=selected!=='SL'||gallery;":"solanal.hidden=selected!=='SL'||gallery;\n  $('#atlas-credit').hidden=selected!=='SF'||gallery;",
    }
    for old,new in replacements.items():
        if page.count(old)!=1:
            raise ValueError(f"R10 template anchor changed: {old}")
        page=page.replace(old,new,1)
    (OUT/f"{PREFIX}_Faltenhorn.html").write_text(page,encoding="utf-8")
    (OUT/f"{PREFIX}_Faltenhorn.stl").write_bytes(payload)
    with (OUT/f"{PREFIX}_Atlasprofil.csv").open("w",encoding="utf-8-sig",newline="") as out:
        writer=csv.writer(out,delimiter=";")
        writer.writerow(["Winkel °",*(f"Radius bei Z={z:.3f} mm" for z in sections),
                         "Mittlerer normierter Radius","Gefilterte normierte Kontur"])
        for angle,samples,mean,value in zip(ANGLES,radii.T,measured,detail):
            writer.writerow([round(m.degrees(angle),3),*np.round(samples,5),round(mean,6),round(value,6)])
    print(f"Atlasquerschnitte: {sections}; Horn: {len(payload)} STL-Bytes")


if __name__=="__main__":
    main()
