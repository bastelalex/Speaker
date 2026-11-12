"""Three docked Diamantstumpf cabinets and the center woofer section, in mm."""
import json
import math as m
import csv
import zipfile
import base64
import gzip
from functools import cache
from pathlib import Path

import diamant_blende as r

np, tm, mf = r.np, r.tm, r.mf
box, loft, rect, union = r.box, r.loft, r.rectangle, r.union
OUT, HERE = r.OUT, r.HERE
REVISION="R06"
CELL_PITCH=90.
HORN_BELT=274.
CASSETTE_SIZE=270.
CASSETTE_HALF=CASSETTE_SIZE/2
HORN_VARIANTS={
    "A": dict(name="Konturhorn",w=232.,h=210.,d=168.,p=4.5,color="#515d66",
              description="Runder Hals, stufenlos gerundetes Rechteck. Breite und Höhe öffnen sich unterschiedlich."),
    "B": dict(name="Schlitz-Waveformer",w=234.,h=204.,d=152.,p=6.,color="#525e64",
              description="Ø36 mm gehen in einen 20 × 58 mm hohen Schlitz über. Dahinter öffnet sich ein Fächer."),
    "C": dict(name="Dreizellen-Waveformer",w=232.,h=216.,d=178.,p=7.,color="#525b64",
              description="Zwei Leitstege teilen den vorderen Hornabschnitt in drei nebeneinanderliegende Zellen."),
    "AW": dict(name="A mit Zentral-Waveguide",w=232.,h=210.,d=168.,p=4.5,color="#6d7378",
              description="Kontur A mit einem zentrischen, tropfenförmigen Waveguide auf drei schlanken Stegen."),
    "D": dict(name="Vierlappen-Rechteck",w=258.,h=210.,d=176.,p=6.,color="#66756e",
              description="Vier innen gedrehte Wölbungen laufen in einen breiten rechteckigen Mund aus."),
    "E": dict(name="Versetztes Fächerhorn",w=264.,h=224.,d=197.,p=8.,color="#626879",
              description="Ein zweistufiger Fächer mit seitlich versetzter Innenachse. Hals und rechteckiger Mund sitzen auf Mitte."),
}
WHEEL_RADIUS=50
WHEEL_WIDTH=32
WHEEL_HUB=40
WHEEL_REAR_INSET=44
WHEEL_D=750
WHEEL_Z=58
TILT_EDGE_D=610
TILT_DEMO=30
WHEEL_XS=(WHEEL_REAR_INSET,300-WHEEL_REAR_INSET)


def wheel_floor_clearance(angle):
    a=m.radians(angle)
    return WHEEL_Z*m.cos(a)-(WHEEL_D-TILT_EDGE_D)*m.sin(a)-WHEEL_RADIUS


def wheel_contact_angle():
    return m.degrees(m.acos(WHEEL_RADIUS/m.hypot(WHEEL_Z,WHEEL_D-TILT_EDGE_D))-
                     m.atan2(WHEEL_D-TILT_EDGE_D,WHEEL_Z))


def section(left, right, d0, d1, z0, z1):
    return loft([(d,rect(left(d),right(d),z0,z1)) for d in (d0,d1)])


def inside_center(d):
    return 300-d/8-18*m.sqrt(1+1/64)


def center_span(d0,d1,z0,z1,margin=0):
    return section(lambda d:-inside_center(d)+margin,lambda d:inside_center(d)-margin,d0,d1,z0,z1)


def cabinet(mid):
    wide=300 if mid else 400
    outer_left=lambda d:-300+d/8 if mid else 0
    outer_right=lambda d:wide-d/8
    right=lambda d:outer_right(d)-18*m.sqrt(1+1/64)
    left=lambda d:-right(d) if mid else 18
    outer=section(outer_left,outer_right,0,800,0,1200)
    inner=section(left,right,18,782,18,1182)
    trim=box(-320,420,-600,700,-700,0).rotate((45,0,0)).translate((0,TILT_EDGE_D,0))
    envelope=outer-trim
    normal_offset=18/m.sqrt(2)
    inner=inner-trim.translate((0,-normal_offset,normal_offset))
    return envelope-inner


def x_cylinder(radius,x0,x1,d=WHEEL_D,z=WHEEL_Z):
    return mf.Manifold.cylinder(x1-x0,radius,circular_segments=96).rotate((0,90,0)).translate((x0,d,z))


def wheel_parts(shell,mid):
    parts=[]
    centers=(-200+WHEEL_REAR_INSET,200-WHEEL_REAR_INSET) if mid else WHEEL_XS
    for i,x in enumerate(centers,1):
        x0,x1=x-WHEEL_WIDTH/2,x+WHEEL_WIDTH/2
        tire=x_cylinder(WHEEL_RADIUS,x0,x1)-x_cylinder(31,x0-1,x1+1)
        assert (tire^shell).volume()<1
        parts.append((f"Bluewheel {i} · Ø100",tire,"#246bc2","wheel"))
        hub0,hub1=x-WHEEL_HUB/2,x+WHEEL_HUB/2
        hub=x_cylinder(31,hub0,hub1)-x_cylinder(6.2,hub0-1,hub1+1)
        parts.append((f"Bluewheel {i} · Nabe",hub,"#566779","wheel"))
        normal_gap=(WHEEL_D-TILT_EDGE_D-WHEEL_Z)/m.sqrt(2)
        d,z=WHEEL_D-normal_gap/m.sqrt(2),WHEEL_Z+normal_gap/m.sqrt(2)
        plate=box(x-28,x+28,-32,31,-4,0).rotate((45,0,0)).translate((0,d,z))
        arm_profile=[(d-18,z-19),(d+12,z+11),(WHEEL_D+9,WHEEL_Z+10),
                     (WHEEL_D+9,WHEEL_Z-8),(WHEEL_D-10,WHEEL_Z-12)]
        def ear(a,b):
            solid=loft([(a,arm_profile),(b,arm_profile)])
            return solid.transform(((0,1,0,0),(1,0,0,0),(0,0,1,0)))
        bracket=(plate+ear(x-27,x-21)+ear(x+21,x+27))-x_cylinder(6.2,x-29,x+29)
        axle=x_cylinder(6,x-27,x+27)
        parts.extend([(f"45°-Rollenträger {i}",bracket,"#a9afb0","wheel"),(f"Rollenachse {i}",axle,"#777f84","wheel")])
        assert (tire^bracket).volume()<1 and (hub^bracket).volume()<1
        assert (hub^shell).volume()<1
    assert abs(wheel_floor_clearance(wheel_contact_angle()))<1e-7
    assert wheel_floor_clearance(0)==8 and wheel_floor_clearance(TILT_DEMO)<0
    assert WHEEL_D+WHEEL_RADIUS==800
    return parts


def zcyl(radius,z0,z1,x=0,d=260):
    return mf.Manifold.cylinder(z1-z0,radius,circular_segments=96).translate((x,d,z0))


WOOFER_D=332


def woofer():
    flange=zcyl(230,286,302,d=WOOFER_D)-zcyl(204,285,303,d=WOOFER_D)
    brace=union(box(91,206,-11,11,142,154).rotate((0,-40,0)).translate((15,0,33)).rotate((0,0,a))
                for a in range(0,360,45)).translate((0,WOOFER_D,0))
    rim=zcyl(207,298,305,d=WOOFER_D)-zcyl(191,297,306,d=WOOFER_D)
    cone_outer=mf.Manifold.cylinder(52,54,194,circular_segments=96).translate((0,WOOFER_D,250))
    cone_inner=mf.Manifold.cylinder(53,51,191,circular_segments=96).translate((0,WOOFER_D,253))
    cone=cone_outer-cone_inner
    dome=mf.Manifold.sphere(52,circular_segments=48).scale((1,1,.36)).translate((0,WOOFER_D,251))
    motor=zcyl(109,54,134,d=WOOFER_D)+zcyl(120,134,147,d=WOOFER_D)+zcyl(99,147,178,d=WOOFER_D)
    return [("18-Zoll Korb und Rand",flange+rim+brace,"#c89762"),
            ("18-Zoll Membran",cone+dome,"#ed9f51"),
            ("18-Zoll Magnet",motor,"#8e5331")]


def center_parts():
    parts=[]
    def add(name,solid,color,kind="inside"):
        parts.append((name,solid,color,"center",kind))
    opening=box(-r.W/2,r.W/2,-1,19,600-r.H/2,600+r.H/2)
    add("Mitte · geschlossenes Gehäuse",cabinet(True)-opening,"#292d31","shell")
    hf, service, _=r.hf_parts()
    mf_baffle,banks,motors=r.mf_parts(service)
    cheeks,_,_,_=r.lf_parts()
    add("Mitte · 32 Tiefmitteltonzellen",mf_baffle.translate((0,0,600)),"#333a40","front")
    add("Mitte · zentrales Koaxialhorn",hf.translate((0,0,600)),"#333a43","front")
    for tag,cheek,bank,motor in zip(("L","R"),cheeks,banks,motors):
        add(f"Mitte · drei Basszellen {tag}",cheek.translate((0,0,600)),"#424548","front")
        add(f"Mitte · Tiefmitteltonkammer {tag}",bank.translate((0,0,600)),"#536c6e")
        add(f"Mitte · Mitteltöner {tag}",motor.translate((0,0,600)),"#394246")
    add("Mitte · Koaxialtreiber",r.cylinder(66.5,102,222.8,z=600),"#383d46")
    baffle=center_span(18,782,302,320)-zcyl(212.5,301,321)
    add("18-Zoll Treiberträger · Auflage 302 mm",baffle,"#c0a981","baffle")
    for name,solid,color in woofer():
        add(name,solid,color,"driver")

    # Front-loaded fold: rearward, up, forward, down the two separate side legs.
    low=center_span(18,685,320,420)
    riser=center_span(590,782,320,1182)
    high=center_span(100,782,990,1182)
    passages=[]
    ducts=[]
    for sign in (-1,1):
        def duct_section(wall):
            stations=[]
            for d,l,u in r.LF_RANGES:
                x0,x1=(l-wall,u+wall) if sign>0 else (-u-wall,-l+wall)
                stations.append((d,rect(x0,x1,439-wall,1009+wall)))
            return loft(stations)
        passage=duct_section(0)
        mouths=union(r.cell_cutter(s).translate((0,0,600)) for s in r.BASS if s["x"]*sign>0)
        assert (mouths^passage).volume()>1000
        passages.append(passage+mouths)
        ducts.append(duct_section(4))
    air=union([low,riser,high,*passages])
    assert len(air.decompose())==1
    mid_objects=union([mf_baffle,*banks,*motors,hf]).translate((0,0,600))
    assert (mid_objects^air).volume()<1
    add("Mitte · eigener Bassluftweg",air,"#cb7c39","air")
    add("Mitte · Wandungen der Bassabstiege",union(ducts)-air-mid_objects,"#83664d","duct")
    add("Mitte · erste Falte",center_span(18,590,420,438),"#a49070","baffle")
    add("Mitte · Steigwand",center_span(572,590,438,990),"#a49070","baffle")
    # Upper shelf with apertures for the two side legs.
    add("Mitte · Rücklaufboden",center_span(18,572,972,990)-union(passages),"#a49070","baffle")
    return parts


def top_front_parts():
    parts=[]
    bass_open=box(26,372,-1,19,760,930)
    horn_open=box(41,359,-1,19,555,735)
    mids_open=union(r.cylinder(73.5,-1,19,x,445) for x in (117,283))
    parts.append(("Gehäuse",cabinet(False)-union([bass_open,horn_open,mids_open]),"#262c2e","shell"))
    # Display the front end of each R01 12-inch horn; the original cut plan carries its rear fold.
    nose=loft([(0,rect(25,373,759,931)),(18,rect(25,373,759,931)),(165,rect(25,353,759,931))])
    hole=loft([(-1,rect(26,372,760,930)),(18,rect(26,372,760,930)),(166,rect(29,350,761,929))])
    parts.append(("eigener Bassmund",nose-hole,"#3f4647","front"))
    horn_mesh=tm.load_mesh(HERE/"schnittpaket"/"STL"/"Horn_Top_Ganz.stl",process=True)
    horn_mesh.apply_transform(np.array([[1,0,0,200],[0,0,-1,161],[0,1,0,645],[0,0,0,1]],float))
    parts.append(("Mittel-Hochton-Horn",r.to_manifold(horn_mesh),"#333b42","front"))
    parts.append(("Koaxialtreiber",r.cylinder(66.5,161,281.8,200,645),"#353740","inside"))
    for i,x in enumerate((117,283),1):
        rim=r.cylinder(80.5,0,8,x,445)-r.cylinder(69,-1,9,x,445)
        taper=mf.Manifold.cylinder(29,71,39,circular_segments=96).rotate((-90,0,0)).translate((x,4,445))
        recess=mf.Manifold.cylinder(27,67,35,circular_segments=96).rotate((-90,0,0)).translate((x,3,445))
        dome=r.cylinder(33,24,31,x,445)
        parts.append((f"Mitteltöner {i} · Rahmen",rim,"#555c5c","front"))
        parts.append((f"Mitteltöner {i} · Konus",taper-recess+dome,"#313635","front"))
    return parts


def portrait_cells(mid):
    w=600 if mid else 400
    cx=0 if mid else 200
    columns=6 if mid else 4
    px=pz=CELL_PITCH
    band=(1200-40-6*pz-HORN_BELT)/2
    rows=[]
    for row in range(6):
        for col in range(columns):
            k=col-(columns-1)/2
            direction=1 if row<3 else -1
            distance=2-row if row<3 else row-3
            z=600+direction*(HORN_BELT/2+(distance+.5)*pz)
            zr=600+direction*(102+distance*(46 if mid else 42))
            rows.append(dict(id=f"M{row+1}{col+1}",kind="Tiefmittelton",
                x=cx+k*px,z=z,x1=cx+k*(50 if mid else 48),z1=zr,
                w=px-4,h=pz-4,wi=(23,25,27,27,25,23)[col] if mid else (26,28,28,26)[col],
                hi=25 if mid else 24,depth=230 if mid else 207,ease=2.5))
    for side,label in ((-1,"L"),(1,"R")):
        shapes=[(157.5,41,151 if mid else 149)]
        if mid:
            shapes.append((225.,86,209.))
        z_values=(-90.,0.,90.) if mid else (-45.,45.)
        for col,(x,width,rear_x) in enumerate(shapes,1):
            for row,z in enumerate(z_values,1):
                rows.append(dict(id=f"S{label}{col}{row}",kind="Tiefmittelton",
                    x=cx+side*x,z=600+z,x1=cx+side*rear_x,z1=600+(.68 if mid else .93)*z,
                    w=width,h=86,wi=21 if width==41 else 27,hi=25,depth=142,ease=2.1))
    for sign,label in ((1,"O"),(-1,"U")):
        count=3 if mid else 2
        for col in range(count):
            k=col-(count-1)/2
            rows.append(dict(id=f"B{label}{col+1}",kind="Bassmund",
                x=cx+k*2*px,z=600+sign*(HORN_BELT/2+3*pz+band/2),
                x1=cx+k*(128 if mid else 156),z1=600+sign*(360 if mid else 355),
                w=2*px-4,h=band-4,wi=104 if mid else 85,hi=86 if mid else 76,
                depth=90 if mid else 82,ease=1.85))
    return rows


def get_station(cell,d,wall=0):
    v=max(0.,min(1.,d/cell["depth"]))
    f=1-(1-v)**cell["ease"]
    x=cell["x"]+(cell["x1"]-cell["x"])*f
    z=cell["z"]+(cell["z1"]-cell["z"])*f
    w=cell["w"]*(cell["wi"]/cell["w"])**f+wall
    h=cell["h"]*(cell["hi"]/cell["h"])**f+wall
    return r.centered(x,z,w,h)


def mouth_duct(cell,wall=0,extend=False):
    d=cell["depth"]
    ds=np.linspace(0,d,23)
    if extend:
        ds=np.r_[-1,ds,d+2]
    return loft([(float(y),get_station(cell,y,wall)) for y in ds])


def fastener_bores(d0,d1):
    return union(r.cylinder(2.75,d0,d1,x,z) for x in (-127,127) for z in (-127,127))


def horn_profile(key,d):
    spec=HORN_VARIANTS[key]
    u=1-max(0,min(d/spec["d"],1))
    if key in ("A","AW"):
        w=36+(spec["w"]-36)*(.29*u+.71*u**1.85)
        h=36+(spec["h"]-36)*(.18*u+.82*u**2.55)
        p=2+(spec["p"]-2)*u**.85
    elif key=="B":
        if u<.25:
            t=u/.25
            f=t*t*(3-2*t)
            w,h,p=36-16*f,36+22*f,2+3*f
        else:
            t=(u-.25)/.75
            w=20+(spec["w"]-20)*t**1.35
            h=58+(spec["h"]-58)*t**1.65
            p=5+t
    elif key=="C":
        w=36+(spec["w"]-36)*(.2*u+.8*u**1.38)
        h=36+(spec["h"]-36)*(.38*u+.62*u**2.2)
        p=2+(spec["p"]-2)*u**.9
    elif key=="D":
        w=36+(spec["w"]-36)*(.25*u+.75*u**1.43)
        h=36+(spec["h"]-36)*(.44*u+.56*u**2.55)
        p=2+(spec["p"]-2)*u
    else:
        # The second flare starts near the mouth, with a continuous slope.
        turn=max(0.,(u-.58)/.42)
        w=36+(spec["w"]-36)*(.39*u+.33*u**1.5+.28*turn**2)
        h=36+(spec["h"]-36)*(.24*u+.58*u**2.15+.18*turn**2)
        p=2+(spec["p"]-2)*u**1.5
    return w,h,p


def horn_air(key,addition=0,extended=False):
    spec=HORN_VARIANTS[key]
    depths=np.unique(np.r_[np.linspace(0,spec["d"],49),.75*spec["d"]])
    if extended:
        depths=np.r_[-1,depths,spec["d"]+1]
    stations=[]
    for d in depths:
        w,h,p=horn_profile(key,d)
        points=r.superellipse(w+addition,h+addition,p)
        u=1-max(0.,min(float(d)/spec["d"],1.))
        if key=="D":
            amplitude=.16*m.sin(m.pi*u)**2
            points=[(x*f,z*f) for x,z in points
                    for f in [1+amplitude*m.cos(4*m.atan2(z/(h+addition),x/(w+addition))+.94*u)]]
        if key=="E":
            points=[(x+16*m.sin(m.pi*u)**2,z-6*m.sin(m.tau*u)*m.sin(m.pi*u)) for x,z in points]
        stations.append((float(d),points))
    return loft(stations)


def vane_at(d,sign):
    w,h,p=horn_profile("C",d)
    x=sign*(w/2)*(.34-.05*d/(HORN_VARIANTS["C"]["d"]*.62))
    thick=2.0-1.3*d/(HORN_VARIANTS["C"]["d"]*.62)
    z=h/2*(1-((abs(x)+thick/2)/(w/2))**p)**(1/p)
    return x,thick,z


def central_waveguide():
    core=loft([(d,r.superellipse(radius*2,radius*2,2)) for d,radius in
               ((24,.65),(28,3.5),(38,8),(55,13),(70,14.5),(84,13.5),(99,10.5),(117,6),(129,2.2))])
    d=77.
    w,h,p=horn_profile("A",d)
    bridges=[]
    for angle in (0.,m.tau/3,2*m.tau/3):
        cs,sn=m.cos(angle),m.sin(angle)
        reach=(abs(cs/(w/2))**p+abs(sn/(h/2))**p)**(-1/p)
        front=[(a*cs-b*sn,a*sn+b*cs) for a,b in rect(10,reach+1.5,-1.45,1.45)]
        back=[(a*cs-b*sn,a*sn+b*cs) for a,b in rect(10,reach+.8,-.75,.75)]
        bridges.append(loft([(d-1.15,front),(d+1.15,back)]))
    return core+union(bridges)


@cache
def horn_cassette(key):
    spec=HORN_VARIANTS[key]
    d=spec["d"]
    face=box(-CASSETTE_HALF,CASSETTE_HALF,0,5,-CASSETTE_HALF,CASSETTE_HALF)
    mount=r.cylinder(69,d-.5,d+9)
    fasteners=union(r.cylinder(3.3,d-1,d+10,x*50.8/m.sqrt(2),z*50.8/m.sqrt(2))
                    for x in (-1,1) for z in (-1,1))
    solid=(face+horn_air(key,5)+mount)-union([horn_air(key,extended=True),
                   r.cylinder(18,d,d+10),fastener_bores(-1,6),fasteners])
    if key=="C":
        guides=[]
        for sign in (-1,1):
            stations=[]
            for p in np.linspace(0,.62*d,27):
                x,t,z=vane_at(p,sign)
                stations.append((float(p),rect(x-t/2,x+t/2,-z-1.3,z+1.3)))
            guides.append(loft(stations))
        solid=solid+union(guides)
    if key=="AW":
        solid=solid+central_waveguide()
    return solid


def horn_seat():
    clear=r.superellipse(270,270,8)
    return box(-137,137,5,20,-137,137)-union([loft([(4,clear),(21,clear)]),fastener_bores(4,21)])


def portrait_front(mid):
    w=600 if mid else 400
    cx=0 if mid else 200
    cells=portrait_cells(mid)
    cutters={c["id"]:mouth_duct(c,extend=True) for c in cells}
    airflow=union(cutters.values())
    assert abs(sum(c.volume() for c in cutters.values())-airflow.volume())<1
    bay=box(cx-CASSETTE_HALF-.4,cx+CASSETTE_HALF+.4,-1,6,
            600-CASSETTE_HALF-.4,600+CASSETTE_HALF+.4)
    face=box(cx-w/2,cx+w/2,0,5,0,1200)-union([airflow,bay])
    seat=horn_seat().translate((cx,0,600))
    horn_space=union([bay,*[horn_air(key,6).rotate((0,angle,0)).translate((cx,0,600))
                            for key in HORN_VARIANTS for angle in (0,90)]])
    parts=[("vollflächiger Frontrahmen",face,"#363e43","front")]
    parts.append(("quadratischer Kassettensitz",seat,"#353d42","front"))
    duct_walls=[]
    for kind,tone in (("Tiefmittelton","#303a40"),("Bassmund","#41474b")):
        group=[c for c in cells if c["kind"]==kind]
        skins=union(mouth_duct(c,5) for c in group)
        ext=box(cx-w/2,cx+w/2,0,270,0,1200)
        solid=(skins^ext)-union([face,seat,airflow,horn_space])
        duct_walls.append(solid)
        parts.append((kind+" · Frontkanäle",solid,tone,"front"))
    for key,spec in HORN_VARIANTS.items():
        horn=horn_cassette(key)
        for a in (0,90):
            placed=horn.rotate((0,a,0)).translate((cx,0,600))
            assert (placed^seat).volume()<.5,(key,a,(placed^seat).volume())
            assert (placed^airflow).volume()<.5,(key,a)
            assert all((placed^wall).volume()<.5 for wall in duct_walls),(key,a)
        driver=r.cylinder(66.5,spec["d"]+9,spec["d"]+129.8).translate((cx,0,600))
        assert (driver^airflow).volume()<.5
        assert all((driver^wall).volume()<.5 for wall in duct_walls)
        parts.append((key+" · "+spec["name"],horn.translate((cx,0,600)),spec["color"],"horn-"+key))
    return parts


def portrait_module(mid):
    tag,module=("Mitte","center") if mid else ("Top","right")
    shell=cabinet(mid)-box(-302,402,-1,18.01,-1,1201)
    parts=[(f"{tag} · Gehäuse",shell,"#292f33",module,"shell")]
    for name,shape,color,kind in portrait_front(mid):
        parts.append((f"{tag} · {name}",shape,color,module,kind))
    if mid:
        assert inside_center(WOOFER_D)>230*m.sqrt(1+1/64)
        assert WOOFER_D-230>90
        baffle=center_span(100,782,302,320)-zcyl(212.5,301,321,d=WOOFER_D)
        front_partition=center_span(100,118,18,302)
        parts.append(("18-Zoll Treiberträger · Auflage 302 mm",baffle,"#c0a981",module,"baffle"))
        parts.append(("Mitte · Vorderwand der Rückkammer",front_partition,"#ab9373",module,"inside"))
        for name,solid,color in woofer():
            parts.append((name,solid,color,module,"driver"))
    for name,solid,color,kind in wheel_parts(shell,mid):
        parts.append((f"{tag} · {name}",solid,color,module,kind))
    return parts


def docked_parts(tops):
    length=m.hypot(800,100)
    a=m.degrees(m.atan2(100,800))
    end=(length-800)/2
    x0=300-end*100/length
    d0=end*800/length
    result=portrait_module(True)
    for name,solid,color,_,kind in tops:
        name=name.removeprefix("Top · ")
        posed=solid.rotate((0,0,a)).translate((x0,d0,0))
        result.append(("Top R · "+name,posed,color,"right",kind))
        result.append(("Top L · "+name,posed.mirror((1,0,0)),color,"left",kind))
    shells=[s for _,s,_,_,k in result if k=="shell"]
    assert len(shells)==3
    for i,a in enumerate(shells):
        for b in shells[i+1:]:
            assert (a^b).volume()<1
    return result


def cells_csv():
    path=OUT/f"Diamantstumpf_{REVISION}_Zellberechnung.csv"
    with path.open("w",encoding="utf-8-sig",newline="") as out:
        csvwriter=csv.writer(out,delimiter=";")
        csvwriter.writerow(["Modul","Zelle","Funktion","Mundbreite mm","Mundhöhe mm","Halsbreite mm",
                            "Halshöhe mm","Mund cm²","Hals cm²","Tiefe mm","Mittellinie mm",
                            "Ideale Exponentialgrenze Hz (nur MF)"])
        for mid,label in ((True,"Mitte 600 × 1200"),(False,"Top 400 × 1200, je Gerät")):
            for c in portrait_cells(mid):
                u=np.linspace(0,1,1025)
                axis=m.hypot(c["x1"]-c["x"],c["z1"]-c["z"])
                length=float(np.trapezoid(np.hypot(c["depth"],axis*c["ease"]*(1-u)**(c["ease"]-1)),u))
                marea=c["w"]*c["h"]
                harea=c["wi"]*c["hi"]
                if c["id"]=="H":
                    marea*=m.gamma(1+1/6)**2/m.gamma(1+2/6)
                    harea=m.pi*18**2
                fc=343*m.log(marea/harea)/(4*m.pi*length/1000) if c["kind"]=="Tiefmittelton" else ""
                numbers=(c["w"],c["h"],c["wi"],c["hi"],marea/100,harea/100,c["depth"],length,fc)
                csvwriter.writerow([label,c["id"],c["kind"],*[f"{v:.2f}".replace(".",",") if v!="" else v for v in numbers]])
        for key,spec in variant_data().items():
            values=(spec["w"],spec["h"],36,36,spec["area"],m.pi*18**2/100,spec["d"],spec["d"])
            csvwriter.writerow(["Mitte und Tops",key,spec["name"],*[f"{v:.2f}".replace(".",",") for v in values],""])


def variant_data():
    out={}
    for key,spec in HORN_VARIANTS.items():
        p=spec["p"]
        area=spec["w"]*spec["h"]*m.gamma(1+1/p)**2/m.gamma(1+2/p)
        if key=="C":
            _,t,z=vane_at(0,1)
            area-=4*t*z
        out[key]=dict(spec,area=round(area/100,1))
    return out


def export_horns():
    path=OUT/f"Diamantstumpf_{REVISION}_Hornkassetten.zip"
    info=[
        "Diamantstumpf R06 / sechs Hornkassetten",
        "STL-Einheit mm. X quer, Y Tiefe ab Sichtfläche, Z hoch. Der Mittelpunkt des Hornmunds ist X0/Z0.",
        "Kassettenplatte 270 x 270 mm, Sitzöffnung 270,8 x 270,8 mm.",
        "Vier Bohrungen auf quadratischem 254-mm-Raster. Schrauben lösen, Kassette herausziehen,",
        "um 90° um die Schallachse drehen und bündig wieder verschrauben. Umlaufende Dichtung vorsehen.",
        "BMS 4594HE: Hals Ø36 mm, 4 x M6 auf Ø101,6 mm. Treibergewicht zusätzlich abstützen.",
        "Gemeinsamer Sitz für alle Varianten. Geometrisch geprüft für 0° und 90°.",
        "",
    ]
    with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED) as archive:
        for key,spec in variant_data().items():
            archive.writestr(f"Horn_{key}.stl",r.to_mesh(horn_cassette(key)).export(file_type="stl"))
            info.append(f"{key} {spec['name']}: Mund {spec['w']:.0f} x {spec['h']:.0f} mm, "
                        f"Fläche {spec['area']:.1f} cm², Hals-Mund-Tiefe {spec['d']:.0f} mm.")
        archive.writestr("Kassettensitz.stl",r.to_mesh(horn_seat()).export(file_type="stl"))
        info.extend(["", "Geometrievarianten zur Prüfung. Die tatsächliche Abstrahlung und der Übergang",
                     "zwischen Horn und Tiefmittelton sind akustisch noch zu messen."])
        archive.writestr("Masse_und_Montage.txt","\n".join(info))


def build():
    meshes=[]
    glb=tm.Scene()
    transform=np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]],dtype=float)
    tops=portrait_module(False)
    parts=docked_parts(tops)+[(name,solid,color,"demo",kind) for name,solid,color,_,kind in tops]
    for name,solid,color,module,kind in parts:
        mesh=r.to_mesh(solid)
        meshes.append(dict(name=name,color=color,module=module,kind=kind,**r.data_mesh(mesh)))
        if kind!="air" and module!="demo" and (not kind.startswith("horn-") or kind=="horn-A"):
            export=mesh.copy().apply_transform(transform).apply_scale(.001)
            export.visual.vertex_colors=np.tile(tm.visual.color.hex_to_rgba(color),(len(export.vertices),1))
            glb.add_geometry(export,geom_name=name,node_name=name)
    glb.export(OUT/f"Diamantstumpf_{REVISION}_Gesamtaufbau.glb")
    template=(HERE/"diamant_gesamt.html").read_text(encoding="utf-8")
    library=(HERE/"three-face.min.js").read_text(encoding="utf-8")
    geometry=dict(pivot=TILT_EDGE_D,d=WHEEL_D,z=WHEEL_Z,radius=WHEEL_RADIUS,tilt=TILT_DEMO,
                  firstContact=wheel_contact_angle(),wheelCenters=WHEEL_XS,edgeInset=WHEEL_REAR_INSET,
                  horns=variant_data())
    payload=json.dumps(dict(parts=meshes,geometry=geometry),ensure_ascii=False,separators=(",",":")).encode("utf-8")
    packed=base64.b64encode(gzip.compress(payload,compresslevel=6,mtime=0)).decode("ascii")
    page=template.replace("/*THREE_JS*/",library).replace("/*MODEL_DATA*/",packed)
    (OUT/f"Diamantstumpf_{REVISION}_Gesamtaufbau.html").write_text(page,encoding="utf-8")
    cells_csv()
    export_horns()
    print(len(meshes),"separate 3D parts; isolated portrait cells and no inter-cabinet bass ports")


if __name__=="__main__":
    build()
