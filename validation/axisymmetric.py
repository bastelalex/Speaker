"""Independent P1 finite element solver for axisymmetric linear pressure acoustics.

Rigid horn mounted in an infinite plane baffle; finite exterior truncation with
angle-aware outgoing spherical Robin condition, NO PML. Homogeneous inviscid air.
Continuous circular sections with the catalogue's piecewise-linear meridian.
"""
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
from scipy.special import j0
from acoustics import C,RHO

def boundary_mass(r):
    n=len(r);matrix=np.zeros((n,n));weights=np.zeros(n)
    for j,(a,b) in enumerate(zip(r[:-1],r[1:])):
        length=b-a;local=2*np.pi*length/12*np.array([[3*a+b,a+b],[a+b,a+3*b]])
        matrix[j:j+2,j:j+2]+=local
        weights[j:j+2]+=2*np.pi*length/6*np.array([2*a+b,a+2*b])
    return matrix,weights

def make_mesh(concept,h=.003,extent=.32,piston=False,smooth_meridian=False):
    length=0 if piston else concept['length']*.001;r0=concept['throat']*.0005
    if piston:radius=r0
    elif concept['geometry']=='os':radius=np.sqrt(r0*r0+length*length)
    else:radius=concept['width']*.0005
    nr=max(6,int(np.ceil(radius/h)))
    r=np.linspace(0,radius,nr+1)
    radial=np.r_[r,np.linspace(radius,extent,max(2,int(np.ceil((extent-radius)/h)))+1)[1:]]
    nodes=[];triangles=[];horn_flags=[];rows=[]
    def append_row(z,rad):
        ids=np.arange(len(nodes),len(nodes)+len(rad));nodes.extend([[rv,z] for rv in rad]);rows.append(ids);return ids
    def connect(a,b,flag,jmin=0):
        for j in range(jmin,min(len(a),len(b))-1):
            triangles.extend([[a[j],a[j+1],b[j]],[a[j+1],b[j+1],b[j]]]);horn_flags.extend([flag,flag])
    if not piston:
        rocket=concept['geometry']=='rocket'
        plug_z=length*np.array([.12,.28,.5,.7,.88]);plug_r=np.array([8,33,42,25,1.5])*.001
        nz=max(8,int(np.ceil(length/h)));zs=np.unique(np.round(np.r_[np.linspace(0,length,nz+1),np.linspace(0,length,9),plug_z if rocket else []],12))
        if rocket:
            inner_count=max(4,int(np.ceil(.042/h)));outer_count=max(6,int(np.ceil((radius-plug_r[-1])/h)))
            r=np.r_[np.linspace(0,plug_r[-1],inner_count+1),np.linspace(plug_r[-1],radius,outer_count+1)[1:]]
            radial=np.r_[r,np.linspace(radius,extent,max(2,int(np.ceil((extent-radius)/h)))+1)[1:]]
        zrings=np.linspace(0,length,9)
        rrings=np.sqrt(r0*r0+zrings*zrings) if concept['geometry']=='os' else r0+(radius-r0)*zrings/length
        for zi,z in enumerate(zs):
            wall=np.sqrt(r0*r0+z*z) if smooth_meridian and concept['geometry']=='os' else np.interp(z,zrings,rrings)
            if rocket:
                partition=np.interp(z,plug_z,plug_r)
                radial_row=np.r_[np.linspace(0,partition,inner_count+1),np.linspace(partition,wall,outer_count+1)[1:]]
            else:radial_row=r*wall/radius
            row=append_row(z,radial_row)
            if len(rows)>1:
                midpoint=(z+zs[zi-1])/2
                remove_inner=rocket and plug_z[0]<midpoint<plug_z[-1]
                connect(rows[-2],row,True,inner_count if remove_inner else 0)
        mouth=rows[-1].copy();source=rows[0].copy()
        # Add baffle nodes radially outside the aperture, sharing all mouth nodes.
        extras=np.arange(len(nodes),len(nodes)+len(radial)-len(r));nodes.extend([[rv,length] for rv in radial[len(r):]])
        exterior_base=np.r_[mouth,extras];rows[-1]=exterior_base
    else:
        exterior_base=append_row(0,radial);mouth=exterior_base[:len(r)];source=mouth.copy()
    extrows=[exterior_base]
    for z in np.linspace(length,length+extent,max(2,int(np.ceil(extent/h)))+1)[1:]:
        row=append_row(z,radial);connect(extrows[-1],row,False);extrows.append(row)
    radiation=[]
    # Each radiation edge carries cos(incidence) and 1/range factors for a source
    # located at the centre of the mouth plane. No far-field approximation of p.
    for a,b in zip(extrows[-1][:-1],extrows[-1][1:]):radiation.append((a,b,'front'))
    for a,b in zip(extrows[:-1],extrows[1:]):radiation.append((a[-1],b[-1],'side'))
    # A closed internal body leaves unused nodes; remove them from the pressure DOFs.
    triangles=np.array(triangles);used=np.unique(triangles);remap=np.full(len(nodes),-1,dtype=int);remap[used]=np.arange(len(used))
    nodes=np.array(nodes)[used];triangles=remap[triangles];source=remap[source];mouth=remap[mouth];radiation=[(int(remap[a]),int(remap[b]),kind) for a,b,kind in radiation]
    return {'nodes':nodes,'triangles':triangles,'horn':np.array(horn_flags),'mouth':mouth,'source':source,'mouth_r':r,'length':length,'radiation':radiation,'piston':piston}

def assemble(mesh):
    nodes=mesh['nodes'];tri=mesh['triangles'];p=nodes[tri];x=p[:,:,0];y=p[:,:,1]
    determinant=(x[:,1]-x[:,0])*(y[:,2]-y[:,0])-(x[:,2]-x[:,0])*(y[:,1]-y[:,0]);area=abs(determinant)/2
    grads=np.stack([np.stack([y[:,1]-y[:,2],x[:,2]-x[:,1]],axis=-1),np.stack([y[:,2]-y[:,0],x[:,0]-x[:,2]],axis=-1),np.stack([y[:,0]-y[:,1],x[:,1]-x[:,0]],axis=-1)],axis=1)/determinant[:,None,None]
    stiffness=2*np.pi*area[:,None,None]*x.mean(axis=1)[:,None,None]*np.einsum('nik,njk->nij',grads,grads)
    mass=np.empty_like(stiffness);sumr=x.sum(axis=1)
    # Exact integration of r*Ni*Nj (cubic barycentric polynomial).
    for i in range(3):
        for j in range(3):mass[:,i,j]=2*np.pi*area*((sumr+2*x[:,i])/30 if i==j else (sumr+x[:,i]+x[:,j])/60)
    ii=np.repeat(tri,3,axis=1).ravel();jj=np.tile(tri,(1,3)).ravel();size=(len(nodes),len(nodes))
    def matrix(values,mask=None):
        if mask is None:return coo_matrix((values.ravel(),(ii,jj)),shape=size).tocsr()
        m=np.repeat(mask,9);return coo_matrix((values.ravel()[m],(ii[m],jj[m])),shape=size).tocsr()
    k=matrix(stiffness);m=matrix(mass);kh=matrix(stiffness,mesh['horn']);mh=matrix(mass,mesh['horn'])
    ri=[];rj=[];br=[];bi=[]
    for a,b,kind in mesh['radiation']:
        ra,za=nodes[a];rb,zb=nodes[b];length=np.linalg.norm(nodes[b]-nodes[a]);r=(ra+rb)/2;z=(za+zb)/2-mesh['length'];distance=np.hypot(r,z)
        incidence=(z if kind=='front' else r)/distance
        local=2*np.pi*length/12*np.array([[3*ra+rb,ra+rb],[ra+rb,ra+3*rb]])
        for i,nodei in enumerate((a,b)):
            for j,nodej in enumerate((a,b)):
                ri.append(nodei);rj.append(nodej);bi.append(local[i,j]*incidence);br.append(local[i,j]*incidence/distance)
    bcos=coo_matrix((bi,(ri,rj)),shape=size).tocsr();bcurv=coo_matrix((br,(ri,rj)),shape=size).tocsr()
    source_r=nodes[mesh['source'],0];_,source_weights=boundary_mass(source_r)
    force=np.zeros(len(nodes));force[mesh['source']]=source_weights
    bmouth,wmouth=boundary_mass(mesh['mouth_r'])
    return {'K':k,'M':m,'Kh':kh,'Mh':mh,'Bcos':bcos,'Bcurv':bcurv,'source_weights':force,'source_area':source_weights.sum(),'mouth_mass':bmouth,'mouth_weights':wmouth}

def solve(mesh,matrices,freq,velocity=.01):
    w=2*np.pi*freq;k=w/C
    a=matrices['K']-k*k*matrices['M']+matrices['Bcurv']+1j*k*matrices['Bcos']
    rhs=1j*w*RHO*velocity*matrices['source_weights'];p=spsolve(a.tocsc(),rhs)
    residual=float(np.linalg.norm(a@p-rhs)/np.linalg.norm(rhs))
    p_source=np.dot(matrices['source_weights'],p)/matrices['source_area'];uin=velocity*matrices['source_area']
    pin=.5*float(np.real(p_source*np.conj(uin)))
    pout=.5/(RHO*C)*float(np.real(np.vdot(p,matrices['Bcos']@p)))
    if mesh['piston']:v=np.full(len(mesh['mouth']),velocity,dtype=complex)
    else:
        reaction=(matrices['Kh']-k*k*matrices['Mh'])@p-rhs
        v=np.linalg.solve(matrices['mouth_mass'],-reaction[mesh['mouth']]/(1j*w*RHO))
    return {'pressure':p,'mouth_velocity':v,'zin_normalized':p_source/(RHO*C*velocity),'input_power_w':pin,'radiated_power_w':pout,'power_balance_relative':abs(pin-pout)/max(abs(pin),1e-30),'relative_residual':residual}

def farfield(mouth_r,velocity,freq,angles):
    """Rayleigh far-field integral of the complex FEM mouth-normal velocity.

    Valid for this infinite-baffle scenario. Includes radial phase/amplitude, not
    the uniform-aperture assumption. Overall propagation and source scale omitted.
    """
    gauss,weight=np.polynomial.legendre.leggauss(6);r=[];v=[];weights=[]
    for i,(a,b) in enumerate(zip(mouth_r[:-1],mouth_r[1:])):
        t=(gauss+1)/2;r.extend(a+(b-a)*t);v.extend(velocity[i]*(1-t)+velocity[i+1]*t);weights.extend(weight*(b-a)/2)
    r=np.array(r);v=np.array(v);weights=np.array(weights);k=2*np.pi*freq/C
    return j0(k*np.sin(np.radians(angles))[:,None]*r)@(2*np.pi*r*weights*v)

def beamwidth(angles,db):
    hits=np.flatnonzero(db<=-6)
    if not len(hits):return None
    i=hits[0]
    if i==0:return 0.
    angle=np.interp(-6,[db[i],db[i-1]],[angles[i],angles[i-1]])
    return float(2*angle)
