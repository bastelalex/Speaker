"""Run the first validation campaign. No proprietary solver or network required."""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/speaker-validation-mpl')
import sys,json,csv,hashlib,platform,time,math
import numpy as np
import scipy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
from acoustics import C,RHO,channel_profiles,transfer,piston_load,ray_path_proxy,section_properties
from axisymmetric import make_mesh,assemble,solve,farfield,beamwidth
from catalog_models import generate

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'validation';PLOTS=OUT/'plots'
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','svg.hashsalt':'speaker-validation-1','axes.grid':True,'grid.alpha':.2,'figure.facecolor':'white'})

DRIVER_IDS={id:('lavoce-dn1020-16' if id in ('single','axe','manifold','round-conical','round-os') else 'lavoce-dn2030tk') for id in ['single','rocket','axe','multi','poly','manifold','round-conical','round-os','oval','superellipse','prism','round-slot']}
BLOCKERS={
 'axe':'25,4-mm-LaVoce auf 25-mm-Port: Übergang nötig; Innenkörperhalterung fehlt.',
 'multi':'Gemeinsamer Verteiler fehlt; sechs einzelne 18-mm-Ports sind kein 50-mm-Anschluss.',
 'poly':'Verteiler und Laufwegausgleich fehlen; sechs einzelne 18-mm-Ports.',
 'manifold':'30-mm-Explosionsspalt und fehlende Zusammenführung; drei 25,4→25-mm-Übergänge fehlen.',
 'superellipse':'50-mm-LaVoce auf 49-mm-Port: glatter Übergang nötig.',
 'prism':'Runder 50-mm-Eingang auf 40 × 24 mm: nicht vorhandener Adapter mit erheblicher Flächenreduktion.',
}

def savefig(fig,name):
    fig.savefig(PLOTS/name,bbox_inches='tight',metadata={'Date':None})
    fig.savefig('/tmp/speaker-validation-'+Path(name).stem+'.png',bbox_inches='tight',dpi=120)
    plt.close(fig)

def intended_outlet_area_mm2(c):
    kind=c['geometry'];w,h=c['width'],c['height']
    if kind in ('round','ellipse','rocket','os'):return np.pi*w*h/4
    if kind in ('multi','poly'):w=h=100
    if kind=='prism':return w*h
    n=4 if kind=='superellipse' else 8
    value=w*h*math.gamma(1+1/n)**2/math.gamma(1+2/n)
    return value*6 if kind in ('multi','poly') else value

def port_area(concept,profile):
    mesh=generate(concept);vertices=np.array(mesh.vertices);faces=np.array(mesh.faces)
    part=next(p for p in mesh.parts if p['name']==profile['name']);f=faces[part['face_start']:part['face_start']+part['face_count']];f=f[f[:,3]==1]
    points=vertices[np.unique(f[:,:3])];lo,hi=points[:,2].min(),points[:,2].max()
    ai,_=section_properties(vertices,f,lo+1e-7);ao,_=section_properties(vertices,f,hi-1e-7)
    return ai*1e-6,ao*1e-6

def run_screening(concepts,drivers):
    freq=np.arange(200.,20000.1,25.);records=[];spectra=[];curves={};allprofiles={};geometry_rows=[];component_probes=[]
    for c in concepts:
        print('1D / Schnittprüfung:',c['id'],flush=True)
        profiles=channel_profiles(c,512);allprofiles[c['id']]=profiles
        driver=drivers[DRIVER_IDS[c['id']]];lo=max(driver['crossover_hz'],1600 if c['id']=='poly' else 2000 if c['id']=='manifold' else 1000 if c['id']=='multi' else 0)
        hi=16000 if c['id'] in ('multi','poly','manifold') else driver['range_hz'][1]
        lengths=[p['length_m'] for p in profiles];ports=[port_area(c,p) for p in profiles]
        active=[p for p in profiles if p['name'].startswith('cell_') or p['name'].startswith('input_')]
        if not active:active=profiles[:1]
        active_ports=[ports[profiles.index(p)] for p in active] if len(active)==1 else [ports[i] for i,p in enumerate(profiles) if p['name'].startswith('cell_') or p['name'].startswith('input_')]
        driver_count=3 if c['id']=='manifold' else 1
        inlet_total=sum(a for a,b in active_ports);driver_area=driver_count*np.pi*(driver['throat_mm']*.0005)**2
        ratio=inlet_total/driver_area
        pathspan=(max(lengths)-min(lengths))*1000 if c['id'] in ('multi','poly') else 0
        source_mode=1.841183781*C/(np.pi*driver['throat_mm']*.001)
        minimum=min(min(a for a,b in ports),min(float(p['area_z_m2'].min()) for p in profiles))
        maxcontraction=max(float(1-p['area_z_m2'][-1]/p['area_z_m2'].max()) for p in profiles)
        primary=profiles[0];result=transfer(freq,primary['area_m2'],primary['ds_m']);curves[c['id']]=result
        mask=(freq>=lo)&(freq<=hi)
        # Conditional bound for equal excitation at all existing cell inlets.
        band_phase=360*hi*pathspan/1000/C
        outlet_total=sum(b for a,b in ports) if c['id'] in ('multi','poly') else ports[-1][1]
        intended_area=intended_outlet_area_mm2(c)
        record={'id':c['id'],'title':c['title'],'driver_id':driver['id'],'driver_model':driver['model'],'driver_count':driver_count,'original_driver_reference':c['driver'],'band_hz':[lo,hi],
          'source_model':'uniform prescribed acoustic velocity; no electromechanical LaVoce model',
          'continuous_existing_air_path':c['id'] not in BLOCKERS,'blocker':BLOCKERS.get(c['id'],''),'simulation_scope':'individual existing component; no complete electroacoustic driver system',
          'component_count':len(profiles),'inlet_area_total_mm2':inlet_total*1e6,'driver_exit_area_mm2':driver_area*1e6,'area_ratio_to_driver':ratio,
          'minimum_air_area_mm2':minimum*1e6,'outlet_area_total_mm2':outlet_total*1e6,'intended_outlet_area_total_mm2':intended_area,'outlet_tessellation_area_error_fraction':1-outlet_total*1e6/intended_area,'terminal_area_contraction_fraction':maxcontraction,
          'channel_lengths_mm':[length*1000 for length in lengths],'cell_path_span_mm':pathspan,'geometric_phase_proxy_deg_at_bandtop':band_phase,
          'geometric_edge_path_proxy_mm':ray_path_proxy(c) if c['id'] in ('prism','round-slot') else None,
          'driver_circular_first_transverse_mode_hz':source_mode,'max_power_identity_error':float(result['power_error']),
          'primary_1d_reflection_abs_band_median':float(np.median(abs(result['reflection'][mask]))),
          'components':[{'name':p['name'],'path_mm':p['length_m']*1000,'inlet_mm2':ports[i][0]*1e6,'outlet_mm2':ports[i][1]*1e6} for i,p in enumerate(profiles)]}
        records.append(record)
        for i,f in enumerate(freq):spectra.append([c['id'],f,result['zin_normalized'][i].real,result['zin_normalized'][i].imag,abs(result['reflection'][i]),abs(result['uout_over_uin'][i]),np.angle(result['uout_over_uin'][i],deg=True),result['transmission'][i]])
        for p in profiles:
            probes=np.unique([lo,1200,2000,4000,8000,16000,18000,20000]);rp=transfer(probes,p['area_m2'],p['ds_m'])
            for i,f in enumerate(probes):component_probes.append([c['id'],p['name'],f,rp['zin_normalized'][i].real,rp['zin_normalized'][i].imag,abs(rp['reflection'][i]),abs(rp['uout_over_uin'][i]),np.angle(rp['uout_over_uin'][i],deg=True)])
            for z,a in zip(p['z_m'],p['area_z_m2']):geometry_rows.append([c['id'],p['name'],z*1000,a*1e6])
    with (OUT/'one_d_spectra.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['concept','frequency_hz','zin_normalized_real','zin_normalized_imag','reflection_abs','uout_over_uin_abs','uout_over_uin_phase_deg','transmitted_incident_acoustic_power_fraction']);w.writerows(spectra)
    with (OUT/'section_profiles.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['concept','component','z_mm','free_air_area_mm2']);w.writerows(geometry_rows)
    with (OUT/'component_probes.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['concept','component','frequency_hz','zin_normalized_real','zin_normalized_imag','reflection_abs','uout_over_uin_abs','uout_over_uin_phase_deg']);w.writerows(component_probes)
    fig,axes=plt.subplots(3,4,figsize=(15,9),constrained_layout=True)
    for c,ax in zip(concepts,axes.flat):
        for p in allprofiles[c['id']]:ax.plot(p['z_m']*1000,p['area_z_m2']*1e6,lw=1)
        ax.set_title(c['code']+' / '+c['id'],fontsize=10);ax.set_xlabel('z [mm]');ax.set_ylabel('Freie Fläche [mm²]')
    fig.suptitle('Schnitte der tatsächlichen Katalognetze · kein akustischer Frequenzgang',fontsize=14);savefig(fig,'sections.svg')
    fig,axes=plt.subplots(3,4,figsize=(15,9),constrained_layout=True)
    for c,rec,ax in zip(concepts,records,axes.flat):
        ax.plot(freq,abs(curves[c['id']]['reflection']),color='#146c64');ax.axvspan(200,rec['band_hz'][0],color='grey',alpha=.2);ax.set_xscale('log');ax.set_ylim(0,1.05);ax.set_xlim(200,20000);ax.set_title(c['code']+' / '+c['id'],fontsize=10);ax.set_xlabel('Frequenz [Hz]');ax.set_ylabel('|Γ| am Kanal-Eingang')
    fig.suptitle('1D-Screening / ebene Welle / Kreisersatzstrahler am Mund\nGrau: unter Hersteller-/Projektgrenze · keine reale Treiberantwort / keine 3D-Richtwirkung',fontsize=12);savefig(fig,'one_d_reflection.svg')
    # N=512 versus 1024, with the same 25-Hz evaluation grid.
    convergence=[]
    for id in ('single','rocket','round-os','round-slot'):
        c=next(c for c in concepts if c['id']==id);fine=channel_profiles(c,1024)[0];r=transfer(freq,fine['area_m2'],fine['ds_m']);old=curves[id]
        convergence.append({'id':id,'segments':[512,1024],'max_delta_reflection_complex':float(np.max(abs(r['reflection']-old['reflection']))),'max_delta_z_normalized':float(np.max(abs(r['zin_normalized']-old['zin_normalized'])))})
    return records,curves,freq,convergence

def run_fem(concepts):
    frequencies=[1200.,2000.,4000.,8000.];angles=np.linspace(0,90,361)
    measurements=[];angular=[];mouth_rows=[];convergence=[];benchmarks=[];fine_results={};plots=[]
    for id in ('round-os','round-conical','rocket'):
        c=next(c for c in concepts if c['id']==id);history={}
        case_frequencies=[800.]+frequencies if id=='rocket' else frequencies
        for h in (.003,.00175):
            mesh=make_mesh(c,h=h,extent=.32);mat=assemble(mesh)
            print('FEM:',id,'h=',h,'nodes=',len(mesh['nodes']),flush=True)
            history[h]={}
            for f in case_frequencies:
                s=solve(mesh,mat,f);ff=farfield(mesh['mouth_r'],s['mouth_velocity'],f,angles);db=20*np.log10(np.maximum(abs(ff/ff[0]),1e-8));bw=beamwidth(angles,db)
                history[h][f]=(s,db,bw)
                item={'id':id,'frequency_hz':f,'h_m':h,'extent_m':.32,'nodes':len(mesh['nodes']),'elements':len(mesh['triangles']),'zin_normalized_real':float(s['zin_normalized'].real),'zin_normalized_imag':float(s['zin_normalized'].imag),'beamwidth_6db_deg':bw,'relative_residual':s['relative_residual'],'power_balance_relative':s['power_balance_relative']}
                measurements.append(item)
                if h==.00175:
                    fine_results[(id,f)]=(s,db,bw);plots.append((id,f,db))
                    for angle,level in zip(angles,db):angular.append([id,f,angle,level])
                    for radius,v in zip(mesh['mouth_r'],s['mouth_velocity']):mouth_rows.append([id,f,radius,v.real,v.imag])
                    if f==4000:
                        fig,ax=plt.subplots(figsize=(10,4),constrained_layout=True)
                        triangles=mesh['triangles'];points=mesh['nodes'];tri=mtri.Triangulation(points[:,1]*1000,points[:,0]*1000,triangles)
                        field=20*np.log10(np.maximum(abs(s['pressure'])/(RHO*C*.01),1e-6))
                        image=ax.tripcolor(tri,field,shading='gouraud',vmin=-35,vmax=15,rasterized=True,cmap='viridis');fig.colorbar(image,ax=ax,label='20 log₁₀ |p/(ρc v₀)| [dB], kein SPL')
                        ax.set(xlabel='z [mm]',ylabel='r [mm]',title=f'{id} / 4 kHz / axialsymmetrisches FEM-Feld, starre unendliche Schallwand');savefig(fig,'field-'+id+'.svg')
            for f in case_frequencies:
                if h==.00175:
                    coarse,db0,bw0=history[.003][f];fine,db1,bw1=history[h][f];mask=(db0>-20)&(db1>-20)
                    convergence.append({'id':id,'frequency_hz':f,'comparison':'h=3 mm vs 1.75 mm','delta_z_normalized_abs':float(abs(coarse['zin_normalized']-fine['zin_normalized'])),'max_pattern_delta_above_minus20_db':float(np.max(abs(db0[mask]-db1[mask]))),'beamwidth_delta_deg':None if bw0 is None or bw1 is None else float(abs(bw0-bw1))})
        # Independent outer-boundary and finer-mesh checks at the highest frequency.
        for h,extent,label in [(.00125,.32,'h=1.75 mm vs 1.25 mm'),(.00175,.45,'extent=0.32 m vs 0.45 m')]:
            mesh=make_mesh(c,h=h,extent=extent);mat=assemble(mesh);s=solve(mesh,mat,8000);ff=farfield(mesh['mouth_r'],s['mouth_velocity'],8000,angles);db=20*np.log10(np.maximum(abs(ff/ff[0]),1e-8));bw=beamwidth(angles,db);baseline,db0,bw0=fine_results[(id,8000)]
            mask=(db>-20)&(db0>-20)
            convergence.append({'id':id,'frequency_hz':8000,'comparison':label,'delta_z_normalized_abs':float(abs(baseline['zin_normalized']-s['zin_normalized'])),'max_pattern_delta_above_minus20_db':float(np.max(abs(db[mask]-db0[mask]))),'beamwidth_delta_deg':None if bw is None or bw0 is None else float(abs(bw-bw0))})
            print('FEM Gegenprüfung:',id,label,flush=True)
    # OS analytic contour versus the coarse 9-ring CAD meridian, same source/baffle.
    c=next(c for c in concepts if c['id']=='round-os');mesh=make_mesh(c,h=.00175,smooth_meridian=True);mat=assemble(mesh)
    contour_comparison=[]
    z=np.linspace(0,c['length']*.001,1001);r0=c['throat']*.0005;zrings=np.linspace(0,c['length']*.001,9)
    shape_error=float(np.max(np.interp(z,zrings,np.sqrt(r0*r0+zrings*zrings))-np.sqrt(r0*r0+z*z))*1000)
    for f in frequencies:
        s=solve(mesh,mat,f);ff=farfield(mesh['mouth_r'],s['mouth_velocity'],f,angles);db=20*np.log10(np.maximum(abs(ff/ff[0]),1e-8));bw=beamwidth(angles,db);baseline,db0,bw0=fine_results[('round-os',f)]
        contour_comparison.append({'frequency_hz':f,'cad_meridian_rings':9,'maximum_radial_interpolation_error_mm':shape_error,'analytic_contour_beamwidth_deg':bw,'catalogue_contour_beamwidth_deg':bw0,'delta_z_normalized_abs':float(abs(baseline['zin_normalized']-s['zin_normalized']))})
    # Independent analytic baffled-piston impedance, using the actual prescribed-v port.
    c=next(c for c in concepts if c['id']=='round-os')
    for h in (.003,.00175):
        mesh=make_mesh(c,h=h,piston=True);mat=assemble(mesh)
        for f in frequencies:
            s=solve(mesh,mat,f);reference=piston_load([f],mat['source_area'])[0]*mat['source_area']/(RHO*C)
            benchmarks.append({'frequency_hz':f,'h_m':h,'numerical_real':float(s['zin_normalized'].real),'numerical_imag':float(s['zin_normalized'].imag),'analytic_real':float(reference.real),'analytic_imag':float(reference.imag),'absolute_normalized_error':float(abs(s['zin_normalized']-reference)),'relative_error':float(abs(s['zin_normalized']-reference)/abs(reference))})
    with (OUT/'fem_polars.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['concept','frequency_hz','off_axis_angle_deg','db_relative_to_on_axis']);w.writerows(angular)
    with (OUT/'fem_mouth_velocity.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['concept','frequency_hz','radius_m','velocity_peak_real_m_per_s','velocity_peak_imag_m_per_s']);w.writerows(mouth_rows)
    fig,axes=plt.subplots(1,3,figsize=(18,4.5),constrained_layout=True)
    for id,ax in zip(('round-os','round-conical','rocket'),axes):
        ymax=7
        for cid,f,db in plots:
            if cid==id:
                diagnostic=id=='round-conical' and f==8000
                ax.plot(angles,db,label=f'{f/1000:g} kHz'+(' (nicht konvergiert)' if diagnostic else ''),ls='--' if diagnostic else '-')
                ymax=max(ymax,float(np.max(db))+1)
        driver_name='DN20.30TK' if id=='rocket' else 'DN10.20-16'
        ax.axhline(-6,color='grey',ls='--',lw=1);ax.set(xlim=(0,90),ylim=(-35,ymax),xlabel='Winkel zur Achse [°]',ylabel='Pegel relativ zur Achse [dB]',title=id+' / '+driver_name+' idealisiert');ax.legend()
    fig.suptitle('2D-axialsymmetrische FEM + Rayleigh-Integral / unendliche Schallwand\nKeine gemessenen LaVoce-Polaren; diskrete Stützfrequenzen, 800 Hz nur beim Ringkanal',fontsize=12);savefig(fig,'fem_polars.svg')
    return measurements,convergence,benchmarks,contour_comparison

def main():
    started=time.time();PLOTS.mkdir(exist_ok=True)
    concepts=json.loads((ROOT/'data/catalog.json').read_text());drivers={d['id']:d for d in json.loads((ROOT/'data/drivers.json').read_text())}
    records,curves,freq,conv1=run_screening(concepts,drivers)
    fem,conv2,benchmark,contour=run_fem(concepts)
    data={'campaign':'1.0','date':'2026-11-12','air':{'c_m_per_s':C,'rho_kg_per_m3':RHO},'source_velocity_peak_m_per_s':.01,'screening':records,'one_d_convergence':conv1,'fem':fem,'fem_convergence':conv2,'piston_benchmark':benchmark,'os_contour_comparison':contour}
    (OUT/'results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    paths=['data/catalog.json','data/drivers.json','scripts/catalog_models.py','validation/acoustics.py','validation/axisymmetric.py','validation/run.py']
    manifest={'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'matplotlib':matplotlib.__version__,'input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},'runtime_seconds':round(time.time()-started,2),'one_d_frequency_hz':{'start':200,'stop':20000,'step':25},'one_d_segments':512,'fem_cases_hz':{'round-os':[1200,2000,4000,8000],'round-conical':[1200,2000,4000,8000],'rocket':[800,1200,2000,4000,8000]},'fem_boundary':'rigid infinite mouth baffle; finite exterior; angle-aware spherical outgoing Robin condition; no PML; rigid closed inner body for rocket','field_method':'axisymmetric P1 FEM; complex mouth velocity from weak-interface reaction; Rayleigh far-field integral','geometry_approximation':'circular meridian interpolated from 9 catalogue axial rings; rocket insert meridian retained; 32-facet azimuthal tessellation replaced by continuous circles','limitations':['no electrical or mechanical LaVoce equivalent circuit','uniform prescribed exit velocity, unknown real driver exit wavefront','no nonlinear distortion or thermal compression','no validated output above 8 kHz','non-axisymmetric concepts have only reduced 1D screening','no complete systems for missing distributors, adapters or exploded interfaces']}
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    from report import write_report
    write_report(ROOT,data,manifest)
    print('Kampagne abgeschlossen, Sekunden:',manifest['runtime_seconds'],flush=True)

if __name__=='__main__':main()
