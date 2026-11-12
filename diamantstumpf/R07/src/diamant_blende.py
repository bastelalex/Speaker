"""Functional cassette and bass-coupling prototype. All model coordinates are mm."""
from pathlib import Path
import csv
import base64
import json
import math as m
import shutil
import sys
import zipfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "face_deps"))
import numpy as np
import manifold3d as mf
import trimesh as tm

OUT = HERE.parent / "outputs"
KIT = HERE / "blende_R02"
CAD = KIT / "CAD"
CAD.mkdir(parents=True, exist_ok=True)

W, H = 546., 332.5
CW = W * 116 / 202
PX, PZ = CW/6, H/6
L, C = 168., 343.
MF_Z = 600
LF_RANGES = [(100., 158., 260.), (165., 167., 252.),
             (309., 181., 234.), (440., 130., 218.)]


def rectangle(x0, x1, z0, z1):
    return [(x0,z0),(x1,z0),(x1,z1),(x0,z1)]


def centered(x, z, w, h):
    return rectangle(x-w/2,x+w/2,z-h/2,z+h/2)


def to_manifold(mesh):
    if mesh.volume < 0:
        mesh.invert()
    assert mesh.is_watertight and mesh.volume > 0
    solid = mf.Manifold(mf.Mesh(np.asarray(mesh.vertices, dtype=np.float32),
                                np.asarray(mesh.faces, dtype=np.uint32)))
    assert solid.status() == mf.Error.NoError
    return solid


def loft(stations):
    n = len(stations[0][1])
    vertices = [(x,d,z) for d, ring in stations for x,z in ring]
    triangles = []
    for s in range(len(stations)-1):
        for i in range(n):
            j = (i+1)%n
            a,b,c,e = s*n+i,s*n+j,(s+1)*n+j,(s+1)*n+i
            triangles.extend(((a,b,c),(a,c,e)))
    end = (len(stations)-1)*n
    for i in range(1,n-1):
        triangles.extend(((0,i+1,i),(end,end+i,end+i+1)))
    return to_manifold(tm.Trimesh(vertices=vertices, faces=triangles, process=True))


def box(x0,x1,y0,y1,z0,z1):
    return mf.Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))


def cylinder(radius,y0,y1,x=0,z=0):
    return mf.Manifold.cylinder(y1-y0,radius,circular_segments=96).rotate((-90,0,0)).translate((x,y0,z))


def union(items):
    return mf.Manifold.batch_boolean(list(items), mf.OpType.Add)


def to_mesh(solid):
    assert solid.status() == mf.Error.NoError and not solid.is_empty()
    data = solid.to_mesh()
    mesh = tm.Trimesh(np.array(data.vert_properties)[:,:3], np.array(data.tri_verts), process=False)
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
    return mesh


def export_part(name, solid):
    mesh = to_mesh(solid)
    mesh.export(CAD / (name + ".stl"))
    return mesh


def length(depth, dx, dz):
    u = np.linspace(0,1,513)
    speed = np.hypot(depth,m.hypot(dx,dz)*m.pi/2*np.cos(m.pi*u/2))
    return float(np.trapezoid(speed,u))


def cells_data():
    entries = []
    for row in range(6):
        for col in range(6):
            if row in (2,3) and col in (2,3):
                continue
            x,z = (col-2.5)*PX,(2.5-row)*PZ
            dx,dz = m.copysign(10.5,x),m.copysign(9.5,z)
            lo,hi = L-5,L
            for _ in range(28):
                trial = (lo+hi)/2
                if length(trial,dx,dz) > L:
                    hi = trial
                else:
                    lo = trial
            depth = (lo+hi)/2
            w0,w1,h1 = (23,25,27,27,25,23)[col],PX-3,PZ-3
            a0,a1 = w0*25,w1*h1
            entries.append(dict(id=f"M{row+1}{col+1}",role="Tiefmittelton",bank="L" if col<3 else "R",
                x=x,z=z,w=w1,h=h1,wi=w0,hi=25,d=depth,length=L,dx=dx,dz=dz,ain=a0,aout=a1,
                exponent=m.log(a1/a0)/(L/1000), fc=C*m.log(a1/a0)/(4*m.pi*L/1000)))
    for side in (-1,1):
        for row in range(3):
            x=side*(W+CW)/4
            z=(1-row)*H/3
            a0,a1=94*91,((W-CW)/2-3)*(H/3-3)
            dx=side*211-x
            dz=-.155*z
            entries.append(dict(id=f"B{'L' if side<0 else 'R'}{row+1}",role="Bassmund",bank="Bass",
                x=x,z=z,w=(W-CW)/2-3,h=H/3-3,wi=94,hi=91,d=100,length=m.hypot(100,dx,dz),
                dx=dx,dz=dz,ain=a0,aout=a1,exponent=0,fc=None))
    entries.append(dict(id="H",role="Koax MF/HF",bank="H",x=0,z=0,w=2*PX-5,h=2*PZ-5,
        wi=36,hi=36,d=94,length=94,dx=0,dz=0,ain=m.pi*18**2,aout=None,exponent=None,fc=None))
    return entries


CELLS = cells_data()
MIDS = [s for s in CELLS if s["bank"] in ("L","R")]
BASS = [s for s in CELLS if s["bank"] == "Bass"]
HF = CELLS[-1]


def cell_cutter(s, offset=0):
    depth=s["d"]
    stations=[]
    for y in np.linspace(0,depth,19):
        u=y/depth
        easing=m.sin(m.pi*u/2) if s["role"]=="Tiefmittelton" else u
        stations.append((y,centered(s["x"]+s["dx"]*easing,s["z"]+s["dz"]*easing,
                         s["w"]*(s["wi"]/s["w"])**u+offset,s["h"]*(s["hi"]/s["h"])**u+offset)))
    return loft([(-1,stations[0][1]), *stations, (depth+4,stations[-1][1])])


def superellipse(w,h,p):
    def power(a):
        return m.copysign(abs(a)**(2/p),a) if abs(a)>1e-11 else 0.
    return [(w/2*power(m.cos(i*m.tau/96)),h/2*power(m.sin(i*m.tau/96))) for i in range(96)]


def hf_loft(extra):
    stations=[]
    for d in np.linspace(0,94,31):
        u=1-d/94
        w=36+(HF["w"]-36)*(.25*u+.75*u**9)
        h=36+(HF["h"]-36)*(.27*u+.73*u**1.9)
        stations.append((d,superellipse(w+extra,h+extra,2+4*u*u*(3-2*u))))
    return loft([(-1,stations[0][1]),*stations,(95,stations[-1][1])])


def hf_parts():
    throat = hf_loft(0)
    horn_outer = hf_loft(4.8)
    clearance = hf_loft(5.8)
    flange = cylinder(69,94,102)
    bolt = union(cylinder(3.3,93,103,i*50.8/m.sqrt(2),j*50.8/m.sqrt(2))
                 for i in (-1,1) for j in (-1,1))
    horn = (horn_outer + flange) - (throat + cylinder(18,93,103) + bolt)
    service_clearance = clearance + cylinder(70.5,93.99,316)
    return horn,service_clearance,throat


def mf_parts(service):
    cutters=[cell_cutter(s) for s in MIDS]
    for s,c in zip(MIDS,cutters):
        assert (c ^ service).volume() < .03, (s["id"],(c ^ service).volume())
    extent=box(-CW/2,CW/2,0,168,-H/2,H/2)
    front=box(-CW/2,CW/2,0,3,-H/2,H/2)
    rear=box(-CW/2,CW/2,164,168,-H/2,H/2)
    walls=union(cell_cutter(s,4.5) for s in MIDS)
    cassette=((front+rear+walls)^extent)-union([service,*cutters])
    plenums=[]
    rear_cones=[]
    for sign in (-1,1):
        def ring(x0,x1,z0,z1):
            return rectangle(x0,x1,z0,z1) if sign>0 else rectangle(-x1,-x0,z0,z1)
        outer=loft([(168,ring(0,161,-172,172)),(273,ring(0,173,-171,225)),
                    (309,ring(0,177,-174,230))])
        inner=loft([(167.9,ring(3,157,-168,168)),(273,ring(3,169,-167,221)),
                    (305,ring(3,173,-170,226))])
        inner=inner-cylinder(74.5,166,310)
        assert (inner^service).volume() < .01
        for cell,cutter in zip(MIDS,cutters):
            same_side=cell["x"]*sign>0
            overlap=(cutter^inner).volume()
            assert (overlap>600 if same_side else overlap<.01), (cell["id"],overlap)
        cut=cylinder(73.5,304,310,sign*87,136)
        bolts=union(cylinder(2.65,304,310,sign*87+i*86/m.sqrt(2),136+j*86/m.sqrt(2))
                    for i in (-1,1) for j in (-1,1))
        plenums.append(outer-union([inner,cut,bolts,service]))
        rear_cones.append(cylinder(73,309,317,sign*87,136)+cylinder(43.5,316,381,sign*87,136))
    return cassette,plenums,rear_cones


def interpolate_lf(d,i):
    return float(np.interp(d,[p[0] for p in LF_RANGES],[p[i] for p in LF_RANGES]))


def lf_chimney(sign,wall):
    a=[]
    for y,inner,outer in LF_RANGES:
        x0,x1=inner-wall,outer+wall
        a.append((y, rectangle(x0,x1,-183-wall,H/2-3+wall) if sign>0
                  else rectangle(-x1,-x0,-183-wall,H/2-3+wall)))
    return loft(a)


def header(wall):
    return loft([(100-wall,centered(0,-270,520+2*wall,180+2*wall)),
                 (440+wall,centered(0,-270,436+2*wall,180+2*wall))])


ANGLE=m.degrees(m.atan(.125))
PORT_X,PORT_Y,PORT_Z=238.7,315.,-265.
PORT_WIDTH,PORT_HEIGHT=220.,160.


def port_local(geometry,sign):
    if sign < 0:
        return geometry.rotate((0,0,180)).rotate((0,0,-ANGLE)).translate((-PORT_X,PORT_Y,PORT_Z))
    return geometry.rotate((0,0,ANGLE)).translate((PORT_X,PORT_Y,PORT_Z))


def gate_geometry():
    raw = box(-4,4,-134,134,-103,104)
    hole = box(-5,5,-113.5,113.5,-83.5,83.5)
    frame=raw-hole
    plate=box(6,10,-121,121,-91,91)
    rails=union([box(3,17,-134,-121.5,-103,287),box(3,17,121.5,134,-103,287)])
    gasket=(box(4,6,-120,120,-90,90)-box(3,7,-113.5,113.5,-83.5,83.5))
    return frame,plate,rails,gasket


def lf_parts():
    cutters=[cell_cutter(s) for s in BASS]
    face=[]
    for sign in (-1,1):
        x0,x1=(CW/2,W/2) if sign>0 else (-W/2,-CW/2)
        bounds=loft([(0,rectangle(x0,x1,-H/2,H/2)),
                     (100,centered(sign*211,0,102,H))])
        plate=box(x0,x1,0,4,-H/2,H/2)
        seat=box(sign*211-51,sign*211+51,96,100,-H/2,H/2)
        thick=union(cell_cutter(s,7) for s in BASS if s["x"]*sign>0)
        face.append(((plate+seat+thick)^bounds)-union([c for c,s in zip(cutters,BASS) if s["x"]*sign>0]))
    inlets=[box(s["x"]+s["dx"]-s["wi"]/2,s["x"]+s["dx"]+s["wi"]/2,99,106,
                s["z"]+s["dz"]-s["hi"]/2,s["z"]+s["dz"]+s["hi"]/2) for s in BASS]
    entry=box(-205,205,438,451,-322.5,-207.5)
    windows=[port_local(box(-58,56,-110,110,-80,80),sign) for sign in (-1,1)]
    airway=union([header(0),*(lf_chimney(sign,0) for sign in (-1,1)),*inlets,entry,*windows])
    skin=union([header(4),*(lf_chimney(sign,4) for sign in (-1,1))])
    seats=[port_local(box(-19.3,21,-113.5,113.5,-83.5,83.5),sign) for sign in (-1,1)]
    for cutter in cutters:
        assert (cutter^airway).volume()>1000
    return face, skin-union([airway,*seats]), airway, windows


def wing_selector():
    # Two linked slide plates. The entry is below, with a straight front exit and a side exit.
    shell=box(-119,119,-125,120,-111,108)
    intake=box(-106,106,-112,108,-125,-45)
    side=box(-122,25,-110,110,-80,80)
    front=box(-110,110,-129,76,-80,80)
    side_frame=box(-123,-118,-134,134,-103,105)-box(-124,-117,-110,110,-80,80)
    front_frame=box(-134,134,-129,-124,-103,105)-box(-110,110,-130,-123,-80,80)
    body=(shell-union([intake,side,front]))+side_frame+front_frame
    flap_a=box(-127.4,-123.4,-121,121,-91,91)
    flap_b=box(-121,121,-133.4,-129.4,-91,91)
    rails_a=union([box(-139,-121,-134,-121.5,-103,287),box(-139,-121,121.5,134,-103,287)])
    rails_b=union([box(-134,-121.5,-145,-127,-103,287),box(121.5,134,-145,-127,-103,287)])
    return body,flap_a,flap_b,rails_a+rails_b


RESTRICTED_WIDTH=5.5
RESTRICTED_HEIGHT=23.
WEIGHT=RESTRICTED_WIDTH*RESTRICTED_HEIGHT/(23*25)


def throat_insert():
    outer=loft([(0,centered(0,0,22.4,24.4)),(4,centered(0,0,22.4,24.4)),
                (30,centered(0,0,26,28))])
    inner=loft([(-1,centered(0,0,RESTRICTED_WIDTH,RESTRICTED_HEIGHT)),
                (4,centered(0,0,RESTRICTED_WIDTH,RESTRICTED_HEIGHT)),
                (31,centered(0,0,21,23))])
    return outer-inner


def analyse():
    mids=MIDS
    angles=np.linspace(0,90,181)
    theta=np.radians(angles)
    # Ideal baffled aperture with uniform mouth pressure and no mutual loading.
    pressure=np.array([s["aout"] for s in mids])
    x=np.array([s["x"] for s in mids])/1000
    w=np.array([s["w"] for s in mids])/1000
    length_mm=np.array([s["length"] for s in mids])
    polar=[]
    def directivity(a,value):
        db=20*np.log10(np.maximum(1e-5,np.abs(value)/abs(value[0])))
        hits=np.flatnonzero(db<=-6)
        width=None
        if hits.size:
            i=hits[0]
            width=2*float(np.interp(-6,db[i-1:i+1][::-1],angles[i-1:i+1][::-1]))
        return {a+"db67":round(float(db[135]),2),a+"beam":None if width is None else round(width,1),
                a+"db":[round(float(n),3) for n in db]}
    for f in (250,400,500,630,710,800,850,900,1000,1250):
        components=(pressure[:,None]*np.sinc(f/C*w[:,None]*np.sin(theta)) *
                    np.exp(2j*m.pi*f/C*(x[:,None]*np.sin(theta)-length_mm[:,None]/1000)))
        unweighted=np.sum(components,axis=0)
        weighted=np.sum(components*np.where(abs(x)>.12,WEIGHT,1.)[:,None],axis=0)
        polar.append(dict(hz=f,**directivity("",unweighted),**directivity("insert_",weighted)))
    csy=0.
    for (d0,i0,o0),(d1,i1,o1) in zip(LF_RANGES,LF_RANGES[1:]):
        csy+=(d1-d0)*(o0-i0+o1-i1)/2
    ports=2*PORT_WIDTH*PORT_HEIGHT
    bass_mouth=sum(s["aout"] for s in BASS)
    header_min=436*180
    min_flow_area=min(bass_mouth,2*csy,header_min)
    # Geometric diaphragm swept-volume reference, not actual horn air speed.
    center_vd=.121*.0165
    wing_vd=2*.0522*.0105
    flow=[]
    for f in (35,50,63,80,90,100):
        for mode,displacement in (("Mitte",center_vd),("Mono",center_vd+wing_vd)):
            q=2*m.pi*f*displacement
            flow.append(dict(hz=f,mode=mode,q=round(q,4),
                             velocity=round(q/(min_flow_area/1e6),2),
                             mach=round(q/(min_flow_area/1e6)/C,4)))
    hf_area=HF["w"]*HF["h"]*m.gamma(1+1/6)**2/m.gamma(1+2/6)
    stats=dict(mid_mouth=sum(s["aout"] for s in mids)/100,mid_throat=sum(s["ain"] for s in mids)/100,
               mid_fc=[round(min(s["fc"] for s in mids)),round(max(s["fc"] for s in mids))],
               mid_compression=26000/sum(s["ain"] for s in mids),
               hf_area=hf_area/100,hf_model_fc=C*m.log(hf_area/HF["ain"])/(4*m.pi*.094),
               hf_wall_angle=m.degrees(m.atan((HF["w"]-36)/2*(.25+.75*9)/94)),
               mouths=bass_mouth/100,chimneys=2*csy/100,header=header_min/100,ports=ports/100,
               bottleneck=min_flow_area/100,polar=polar,flow=flow,insert_weight=WEIGHT,
               insert_total_throat=(sum(s["ain"] for s in mids)-12*(575-RESTRICTED_WIDTH*RESTRICTED_HEIGHT))/100)
    HF["aout"]=hf_area
    return stats


def write_calculations(stats):
    def german(value):
        return (f"{value:.4f}".rstrip("0").rstrip(".").replace(".",",")
                if isinstance(value,float) else value)
    cell_keys=("id","role","bank","x","z","w","h","wi","hi","d","length","dx","dz","ain","aout","exponent","fc")
    headers=["Zelle","Funktion","Bank","Mund x mm","Mund z mm ab Blendenmitte",
             "Mundweite mm","Mundhöhe mm","Halsweite mm","Halshöhe mm","Tiefe mm","Mittellinie mm",
             "Halsversatz x mm","Halsversatz z mm","Hals mm²","Mund mm²","Flarekonstante 1/m",
             "Ideale Flaregrenze Hz"]
    with (KIT/"Zellen_und_Berechnung.csv").open("w",encoding="utf-8-sig",newline="") as f:
        writer=csv.writer(f,delimiter=";")
        writer.writerow(headers)
        for s in CELLS:
            writer.writerow([german(s[k]) for k in cell_keys])
    with (KIT/"Polar_Tiefmittelton_ideal.csv").open("w",encoding="utf-8-sig",newline="") as f:
        writer=csv.writer(f,delimiter=";")
        writer.writerow(["Winkel Grad"]+[f"{r['hz']} Hz {mode} rel. dB" for r in stats["polar"]
                                             for mode in ("offen","mit geometrischer Drosselgewichtung")])
        for i in range(181):
            writer.writerow([german(i*.5),*[german(r[k][i]) for r in stats["polar"] for k in ("db","insert_db")]])
    with (KIT/"Basskanal_Volumenstrom_Referenz.csv").open("w",encoding="utf-8-sig",newline="") as f:
        writer=csv.writer(f,delimiter=";")
        writer.writerow(["Hz","Anregung","Q Spitze m3/s","Q/A am Engpass m/s","Mach Referenz"])
        for row in stats["flow"]:
            writer.writerow([german(v) for v in row.values()])
    (KIT/"Berechnung.json").write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding="utf-8")


def window_dxf():
    sys.path.insert(1,str(HERE/"dxf_deps"))
    import ezdxf
    document=ezdxf.new("R2000")
    document.units=4
    layout=document.modelspace()
    layout.units=4
    for layer in ("LICHTMASS","MUFFENTASCHE","RAHMEN","REFERENZ"):
        document.layers.new(layer)
    for layer,w,h in (("LICHTMASS",220,160),("MUFFENTASCHE",227,167),("RAHMEN",268,207)):
        layout.add_lwpolyline(centered(0,0,w,h),close=True,dxfattribs={"layer":layer})
    layout.add_line((-15,0),(15,0),dxfattribs={"layer":"REFERENZ"})
    layout.add_line((0,-15),(0,15),dxfattribs={"layer":"REFERENZ"})
    document.saveas(CAD/"Koppelfenster_Profil_1zu1.dxf")


def data_mesh(mesh):
    # GL coordinate system: x right, y up, z toward viewer.
    v=np.asarray(mesh.vertices)[:,[0,2,1]].astype("<f4")
    v[:,2]*=-1
    t=np.asarray(mesh.faces,dtype="<u4")
    return dict(v=base64.b64encode(v.tobytes()).decode("ascii"),
                t=base64.b64encode(t.tobytes()).decode("ascii"))


def make_model():
    parts=[]
    assembly=tm.Scene()
    def part(name,solid,tone,group="face",motion="",write=True):
        mesh=export_part(name,solid) if write else to_mesh(solid)
        parts.append(dict(name=name,color=tone,group=group,motion=motion,**data_mesh(mesh)))
        if group not in ("wing","air") and not motion.endswith("sleeve"):
            transform=np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]],dtype=float)
            export=mesh.copy().apply_transform(transform).apply_scale(.001)
            export.visual.vertex_colors=np.tile(tm.visual.color.hex_to_rgba(tone),(len(export.vertices),1))
            assembly.add_geometry(export,geom_name=name,node_name=name)

    horn,clearance,throat=hf_parts()
    cassette,plenums,cones=mf_parts(clearance)
    cheeks,lf_skin,lf_air,_=lf_parts()
    # Relieve the overlapping outer skins at the common joint. The air paths are already separated.
    lf_skin=lf_skin-union([cassette,*plenums])
    for s in MIDS:
        assert (cell_cutter(s) ^ lf_air).volume() < 1e-3, s["id"]
    assert (lf_skin ^ union([cassette,*plenums])).volume() < 1
    assert (lf_air ^ horn).volume() < 1
    assert len(lf_air.decompose()) == 1
    part("Blende_Multicell_32",cassette,"#333A41")
    for index,tag in enumerate(("L","R")):
        part(f"Blende_Bass_{tag}_3_Zellen",cheeks[index],"#4C5055")
        part(f"Verteiler_Tiefmittelton_{tag}",plenums[index],"#5C7779")
        part(f"Bauraum_6PR160_{tag}",cones[index],"#222B32",write=False)
    part("Zentralhorn_Koax",horn,"#373C45")
    part("Bauraum_BMS4594HE",cylinder(66.5,102,222.8),"#35303E",write=False)
    part("Basssammler_und_Abstiege",lf_skin,"#806653")
    part("Bass_Air_Referenz",lf_air,"#BC814D","air",write=False)
    part("Basszellen_Air",union(cell_cutter(s) for s in BASS),"#BC814D","air",write=False)
    frame,plate,rail,gasket=gate_geometry()
    collar=box(-19,19,-113,113,-83,83)-box(-20,20,-110,110,-80,80)
    assert (collar^union([frame,rail,gasket,plate.translate((0,0,183))])).volume()<1
    gate_path=box(6,10,-110,110,-80,80)
    assert abs((plate^gate_path).volume()-gate_path.volume())<1
    assert (plate.translate((0,0,183))^gate_path).volume()<1
    for tag,sign in (("L",-1),("R",1)):
        for name,solid,tone,motion in (("Rahmen",frame,"#73665D",""),
                 ("Schieber",plate,"#C4AD83","center"),
                 ("Führung",rail,"#766557",""),
                 ("Dichtung",gasket,"#27292C",""),
                 ("Koppelmuffe",collar,"#7AA0A2","sleeve")):
            part(f"Mitte_Klappe_{tag}_{name}",port_local(solid,sign),tone,motion=motion)
    body,s1,s2,wing_rails=wing_selector()
    part("Top_Weiche_Gehaeuse",body,"#6F797A","wing")
    part("Top_Weiche_Schieberfuehrungen",wing_rails,"#817569","wing")
    part("Top_Schieber_Seitenkanal",s1,"#C4AD83","wing","wing-side")
    part("Top_Schieber_Frontmund",s2,"#C4AD83","wing","wing-front")
    export_part("Drosseleinsatz_aeussere_MF_Zellen_12x",throat_insert())
    assembly.export(CAD/"Mittelblende_und_Klappen_2-1.glb")
    return parts


def documentation(stats):
    p800=next(p for p in stats["polar"] if p["hz"]==800)
    p850=next(p for p in stats["polar"] if p["hz"]==850)
    v50=next(r["velocity"] for r in stats["flow"] if r["hz"]==50 and r["mode"]=="Mono")
    v80=next(r["velocity"] for r in stats["flow"] if r["hz"]==80 and r["mode"]=="Mono")
    de=lambda number,dec=1:f"{number:.{dec}f}".replace(".",",")
    return f"""# Diamantstumpf R02 · Funktionsmodell

## Sichtfront

Die Referenz bestimmt das Raster und die Proportionen. Die Front ist 546 × 332,5 mm groß.
Die beiden Außenspalten haben je drei große Basszellen. Das Mittelfeld ist ein 6 × 6 Raster,
dessen zentrale 2 × 2 Positionen zu einer Koaxöffnung zusammengefasst sind. Es bleiben 32
kleine Zellen. Alle 39 sichtbaren Öffnungen führen Schall. Zellkennungen in der CSV laufen
von oben nach unten und von links nach rechts. x ist horizontal, d geht nach hinten und
z nach oben. Die CAD-Dateien verwenden die Blendenmitte als x/z-Null, d=0 ist die Sichtseite.

## Tiefmittelton

Je ein 6PR160 speist 16 Zellen in einer separaten linken bzw. rechten, rückseitig bestückten
Kammer. Die Luftquerschnitte jeder Zelle wachsen von 23/25/27 × 25 mm auf ca.
{de(PX-3)} × {de(PZ-3)} mm. Die Mittelachsen sind geometrisch auf 168,0 mm abgeglichen.
Die Aufweitung ist näherungsweise exponentiell:

`S(u) = S_Hals · (S_Mund / S_Hals)^u`, `m = ln(S_Mund / S_Hals) / L`,
`f_c = c · m / (4π)`, mit `c = 343 m/s` und `L` in Metern.

Die idealisierten Flaregrenzen liegen bei {stats['mid_fc'][0]}–{stats['mid_fc'][1]} Hz.
Die 32 Hälse ergeben {de(stats['mid_throat'])} cm². Mit zusammen 260 cm² Membranfläche
entspricht das geometrisch etwa {de(stats['mid_compression'],2)}:1.
Die Kammern und ihre Anregung können zusätzliche Amplituden- und Phasenfehler verursachen.
Die Zahl für die Flaregrenze ist weder ein DSP-Hochpass noch eine Aussage zum −3-dB-Punkt.

Im Horizontalmodell summieren sich die rechteckigen Teilaperturen komplex und phasengleich.
Die offene Version liegt bei 800 Hz und ±67,5° bei {de(p800['db67'])} dB. Die zwölf
äußeren Rasterzellen können über austauschbare Halseinsätze mit einem 5,5 × 23 mm
Engpass leiser gewichtet werden. Sie bleiben dabei akustisch aktiv. Das vereinfachte
Drosselmodell verwendet die Querschnittsquote {de(WEIGHT,2)} als Amplitudenfaktor:
bei 800 Hz {de(p800['insert_db67'])} dB, bei 850 Hz {de(p850['insert_db67'])} dB bei ±67,5°.
Die tatsächliche Dämpfung und Phase der Einsätze sind zu messen. Für die ersten
Messungen einen Vergleich mit und ohne Einsätze aufnehmen.

## Zentralzelle

Der BMS 4594HE sitzt axial auf Ø36 mm mit vier M6-Punkten auf Ø101,6 mm.
Das freigeformte Horn ist 94 mm tief, der gerundete Mund rund {de(stats['hf_area'])} cm² groß.
Der horizontale Wandwinkel am Austritt beträgt rechnerisch ±{de(stats['hf_wall_angle'])}°.
Das ist ein Konstruktionswinkel. Der Öffnungswinkel des abgestrahlten Schalls ergibt
sich aus der Messung. Die vereinfachte, flächengleiche Flareabschätzung liefert
ca. {round(stats['hf_model_fc'])} Hz; für den Übergang zur Rasterbank sind 780–900 Hz
ein Bereich für erste Kleinsignal-Messungen. Der Hersteller nennt 6,3 kHz als MF/HF-Trennung
für den 4594HE. 22 kHz sind Bandbreitenziel auf Achse, 135° sind ein frequenzabhängiges
Richtziel. HF- und MF-Pegel, Winkelverläufe und Übergangsphase getrennt erfassen.

## Bassweg und Hornklappen

| Stellung | Mittelblock L/R | Top zur Seite | Top nach vorne |
|---|---|---|---|
| 2.1 | geschlossen | geschlossen | offen |
| Mono | offen, Muffen eingelegt | offen | geschlossen |

Der 18-Zöller speist den Sammler von hinten. Jede Seite des Sammlers mündet nach oben
in einen Zuleitkanal zu drei Basszellen. In Mono kommen die beiden
Top-Bässe über seitliche Fenster hinzu. Die **Top-Weiche** besteht aus zwei gegenläufig
bedienten Schiebern auf einer gemeinsamen Verzweigung. In der Vorschau bewegt der Modus
die Schieber um 183 mm. Bedienelemente und Verriegelung sind als Werkstattbeschläge
vorzusehen. Zwischenstellungen sind für das Umschalten bei stummen Endstufen gedacht.

Die zwei Kopplungsfenster haben je **220 × 160 mm** lichte Weite. Die 38 mm langen
Muffen überspannen die beiden Gehäusewände. Je eine herausnehmbare Muffe und
eine komprimierte umlaufende Dichtung vorsehen. Muffen vor dem Andocken einlegen.
Dichtflächen glatt bearbeiten,
Schieber in beiden Endlagen arretieren und mit einem Andruck gegen die Dichtung setzen.
Die Mittelpunkte der Fenster liegen bei d315 / z−265 relativ zur Blendenmitte.
Mit Blendenmitte auf Gehäusehöhe 600 mm ergibt sich Fensterhöhe 335 mm.
Der Sitz am Top liegt im angedockten Zustand rund 314 mm hinter seiner vorderen
Flankenkante entlang der Andockfläche. Das DXF enthält Lichtmaß und Muffentasche.
Die R02-Teile brauchen einen Ausschnitt und versenkten Schieberraum in der Andockfläche.

| Querschnitt | Fläche |
|---|---:|
| Sammler (kleinster horizontaler Rechenquerschnitt) | {de(stats['header'])} cm² |
| Zwei Kopplungsfenster | {de(stats['ports'])} cm² |
| Zwei Zuleitkanäle nach oben (zusammen) | {de(stats['chimneys'])} cm² |
| Sechs Bassmünder (zusammen) | {de(stats['mouths'])} cm² |

Der Sammler hat hinten einen 410 × 115 mm großen Anschluss für den einzelnen
Mittelbass. Die beiden Zuleitkanäle bilden den engsten gemeinsam durchströmten
Nennquerschnitt. Als reine Hub- und Flächenreferenz ergeben sich bei gleichphasiger
Anregung und nominalem Spitzenhub rechnerisch {de(v50)} m/s bei 50 Hz und {de(v80)} m/s
bei 80 Hz. Dabei gilt `Q = 2πf · Σ(Sd·Xmax)` und `v = Q/A`. Die Werte erfassen
weder Hornübersetzung noch Kammerresonanzen oder gegenseitige Last. Auch zwei
angesteuerte Bässe können einen dritten mechanisch anregen. Die Kopplung mit
Impedanzmessungen je Treiber und Druckmessungen im Sammler prüfen, bevor Pegel,
Polarität und Laufzeiten des Gruppenbetriebs eingestellt werden.

## Einbau und Dateien

R02 ist die neu konstruierte Front mit Sammler, Schiebern und Schnittstelle für die
drei Falthörner. Die Lage des gemeinsamen Kanals erfordert geänderte Endstücke der
R01-Faltwege. Die Außenkontur der Boxen bleibt der Einbaurahmen. Für den Zuschnitt
des kompletten Gehäuses müssen die Anschlussstücke der inneren Faltwege bemaßt werden.
Die 35-Hz-Systemgrenze und 50-Hz-Gruppengrenze sind Ziele für das Gesamtsystem.
Die Dateien enthalten keine gemessene Freigabe dieser Frequenzen.

- **GLB:** Mittelmodul komplett, Klappen geschlossen. Einheiten im GLB sind Meter.
- **STL:** Bauteile mit Baugruppenkoordinaten in Millimetern. Drosselteil bei Bedarf zwölfmal
  drucken. Die Weiche ist ein gemeinsames Muster für die gespiegelten Tops. STL-Bauraum
  und Wandstärken für den gewählten Fertigungsweg auslegen. Bei Segmentierung die
  Fugen an Mundrippen und Dichtflächen luftdicht schließen.
- **DXF:** Koppelfenster als 1:1-Profil in Millimetern. Lichtmaß, Muffentasche
  und Rahmen auf separaten Layern. Nur den vorgesehenen Bearbeitungslayer auswählen.
- **CSV/JSON:** Zellmaße, idealisierte horizontale Polardaten, Querschnitte und
  Volumenstrom-Referenz. Die Reihen für die Drosseleinsätze verwenden
  eine modellierte Gewichtung anstelle gemessener Einfügedämpfung.
- **Quelle:** Parametrischer Python-Generator der Geometrie und Berechnung.

Quellen:
[Turbosound, Wellenfront und Pfadlängen](https://data.epo.org/publication-server/rest/v1.2/patents/EP2001261NWA1/document.pdf)
· [BMS 4594HE](https://bmsspeakers.com/product/1-4-coaxial-neodymium-compression-driver-4594he/)
· [FaitalPRO 6PR160](https://faitalpro.com/en/products/LF_Loudspeakers/product_details/index.php?id=101020145)
· [B&C 18DS115](https://www.bcspeakers.com/en/products/lf-driver/18-0/8/18ds115-8)
· [B&C 12BG100](https://www.bcspeakers.com/en/products/lf-driver/12-0/8/12bg100.pdf)
· [AES zur Modellierung von Falthörnern](https://aes.org/publications/elibrary/elibrary-page/?id=13023)
"""


def build():
    stats=analyse()
    parts=make_model()
    window_dxf()
    write_calculations(stats)
    (KIT/"Einbau_und_Berechnung.md").write_text(documentation(stats),encoding="utf-8")
    source=KIT/"Quelle"
    source.mkdir(exist_ok=True)
    for name in ("diamant_blende.py","blende_viewer.html","three-face.min.js","three-face-LICENSE.txt"):
        shutil.copyfile(HERE/name,source/name)
    (source/"Regenerieren.txt").write_text(
        "In einer Python-Umgebung: pip install numpy manifold3d trimesh ezdxf\n"
        "Dann python diamant_blende.py. Dateien entstehen unter blende_R02 und ../outputs.\n",encoding="utf-8")
    template=(HERE/"blende_viewer.html").read_text(encoding="utf-8")
    lib=(HERE/"three-face.min.js").read_text(encoding="utf-8")
    data=dict(cells=CELLS,stats=stats,parts=parts)
    view=template.replace("/*THREE_JS*/",lib).replace("/*MODEL_DATA*/",json.dumps(data,ensure_ascii=False,separators=(",",":")))
    OUT.mkdir(exist_ok=True)
    (OUT/"Diamantstumpf_R02_Funktionsmodell.html").write_text(view,encoding="utf-8")
    (OUT/"Diamantstumpf_R02_Berechnung.md").write_text(documentation(stats),encoding="utf-8")
    with zipfile.ZipFile(OUT/"Diamantstumpf_R02_Modellpaket.zip","w",zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(KIT.rglob("*")):
            if path.is_file():
                archive.write(path,path.relative_to(KIT).as_posix())
    print("Zellen:",len(CELLS)," | Teile in der Ansicht:",len(parts))
    print("Mindestquerschnitt gemeinsam:",stats["bottleneck"],"cm2")
    print("800 Hz:",next((p["db67"],p["insert_db67"]) for p in stats["polar"] if p["hz"]==800))


if __name__=="__main__":
    build()
