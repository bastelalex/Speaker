"""Linear acoustic screening of the actual catalogue meshes (SI units in solvers).

Convention exp(+j*w*t); p and U are peak phasors. No electrical driver model.
"""
from pathlib import Path
import sys
import numpy as np
from scipy.special import j1,struve
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from catalog_models import generate

C=343.0
RHO=1.204

def section_properties(vertices,faces,z):
    """Oriented plane cuts. Returns signed area and centroid, in mesh units.

    Inner material surfaces give positive air area; insert surfaces negative area.
    Opposite intersections of each triangle form oriented polygon segments.
    """
    tri=vertices[faces[:,:3]]
    select=(tri[:,:,2].min(axis=1)<z)&(tri[:,:,2].max(axis=1)>z)
    a=tri[select]
    if not len(a):return 0.,np.zeros(2)
    b=np.roll(a,-1,axis=1)
    up=(a[:,:,2]<z)&(b[:,:,2]>z)
    down=(a[:,:,2]>z)&(b[:,:,2]<z)
    index=np.arange(len(a))
    def point(mask):
        i=np.argmax(mask,axis=1);p=a[index,i];q=b[index,i]
        t=(z-p[:,2])/(q[:,2]-p[:,2])
        return p[:,:2]+t[:,None]*(q[:,:2]-p[:,:2])
    p,q=point(up),point(down)
    det=p[:,0]*q[:,1]-q[:,0]*p[:,1]
    area=det.sum()/2
    centroid=((p+q)*det[:,None]).sum(axis=0)/(6*area) if abs(area)>1e-12 else np.zeros(2)
    return float(area),centroid

def channel_profiles(concept,n=1024):
    """Per-component air sections extracted from the exported triangle surfaces.

    An insert is subtracted from its enclosing single shell. ds accounts for a
    bent centreline; S_normal = S_z/(ds/dz) is an approximate 1D reduction.
    """
    mesh=generate(concept);vertices=np.array(mesh.vertices);allfaces=np.array(mesh.faces)
    inserts=allfaces[allfaces[:,3]==3];profiles=[]
    for part in mesh.parts:
        faces=allfaces[part['face_start']:part['face_start']+part['face_count']]
        faces=faces[faces[:,3]==1]
        if not len(faces):continue
        points=vertices[np.unique(faces[:,:3])];zmin,zmax=points[:,2].min(),points[:,2].max()
        edges=np.linspace(zmin,zmax,n+1);z=(edges[:-1]+edges[1:])/2
        areas=[];centres=[]
        for position in z:
            area,centroid=section_properties(vertices,faces,position)
            if len(inserts):
                extra,extra_centroid=section_properties(vertices,inserts,position)
                if area+extra>0:centroid=(area*centroid+extra*extra_centroid)/(area+extra)
                area+=extra
            areas.append(area);centres.append(centroid)
        areas=np.array(areas);centres=np.array(centres)
        if np.any(areas<=0):raise ValueError('Nonpositive air section: '+concept['id'])
        slope=np.gradient(centres,z,axis=0);factor=np.sqrt(1+(slope*slope).sum(axis=1))
        profiles.append({'name':part['name'],'z_m':z*.001,'area_z_m2':areas*1e-6,'area_m2':areas*1e-6/factor,'centres_m':centres*.001,'ds_m':np.diff(edges)*.001*factor,'length_m':float(np.sum(np.diff(edges)*.001*factor))})
    return profiles

def piston_load(freq,area):
    """Equivalent circular, uniformly moving piston in an INFINITE rigid baffle.

    Equal-area approximation for a non-circular port; mutual cell radiation omitted.
    Acoustic impedance p/U, not p/v or mechanical force/velocity.
    """
    x=2*(2*np.pi*np.asarray(freq)/C)*np.sqrt(area/np.pi)
    return RHO*C/area*(1-2*j1(x)/x+1j*2*struve(1,x)/x)

def transfer(freq,areas,lengths,load=None):
    freq=np.atleast_1d(np.asarray(freq,float));areas=np.asarray(areas,float);lengths=np.asarray(lengths,float)
    if len(areas)!=len(lengths) or np.any(areas<=0):raise ValueError('Invalid sections')
    zref=RHO*C/areas[0]
    # State [p, Zref*U]; rescaling avoids ill-conditioned dimensional matrix products.
    a=np.ones(len(freq),complex);b=np.zeros(len(freq),complex);cc=b.copy();d=a.copy()
    for area,length in zip(areas,lengths):
        phase=2*np.pi*freq/C*length;co=np.cos(phase);si=np.sin(phase);ratio=areas[0]/area
        aa=a*co+b*1j*si/ratio;bb=a*1j*si*ratio+b*co
        cnew=cc*co+d*1j*si/ratio;dd=cc*1j*si*ratio+d*co
        a,b,cc,d=aa,bb,cnew,dd
    zl=piston_load(freq,areas[-1]) if load is None else np.broadcast_to(load,freq.shape)
    zn=(a*(zl/zref)+b)/(cc*(zl/zref)+d)
    uout=1/(cc*(zl/zref)+d)
    reflection=(zn-1)/(zn+1)
    transmission=4*np.real(zl/zref)*abs(uout)**2/abs(zn+1)**2
    return {'zin_normalized':zn,'uout_over_uin':uout,'reflection':reflection,'transmission':transmission,'power_error':np.max(abs(transmission-(1-abs(reflection)**2)))}

def ray_path_proxy(concept):
    """Straight meridional path proxy, NOT simulated pressure phase.

    Only used to flag gross geometrical path differences in a plane-to-slot loft.
    """
    if concept['geometry']=='prism':
        delta=np.hypot(concept['width']/2-20,concept['height']/2-12)
    else:
        delta=np.hypot(concept['width']/2-concept['throat']/2,concept['height']/2-concept['throat']/2)
    return float(np.hypot(concept['length'],delta)-concept['length'])
