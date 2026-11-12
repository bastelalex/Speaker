"""Independent analytic references and energy checks for the acoustic campaign."""
from pathlib import Path
import sys,unittest,json
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'validation'))
from acoustics import C,RHO,piston_load,transfer,channel_profiles
from axisymmetric import make_mesh,assemble,solve,farfield
from scipy.special import j1

class AcousticReferences(unittest.TestCase):
    def test_matched_uniform_tube_analytic_phase_and_impedance(self):
        f=np.array([200,1200,4000,18000]);area=.001;length=.27;z=RHO*C/area
        result=transfer(f,np.full(300,area),np.full(300,length/300),load=z)
        np.testing.assert_allclose(result['zin_normalized'],1,atol=1e-12)
        np.testing.assert_allclose(result['uout_over_uin'],np.exp(-1j*2*np.pi*f/C*length),atol=1e-12)
        np.testing.assert_allclose(result['transmission'],1,atol=1e-12)

    def test_piston_load_low_ka_limit_and_positive_radiation(self):
        area=np.pi*.0127**2;f=np.array([1.,200.,1200.,4000.,18000.]);ka=2*np.pi*f/C*.0127
        z=piston_load(f,area)*area/(RHO*C)
        self.assertAlmostEqual(z[0].real/(ka[0]**2/2),1,places=5)
        self.assertAlmostEqual(z[0].imag/(8*ka[0]/(3*np.pi)),1,places=5)
        self.assertTrue(np.all(z.real>=0))

    def test_lossless_area_transformer_power_identity(self):
        areas=np.geomspace(.0005,.04,400);r=transfer(np.linspace(200,20000,300),areas,np.full(400,.2/400))
        self.assertLess(r['power_error'],1e-11)
        self.assertTrue(np.all(r['transmission']>=0));self.assertTrue(np.all(r['transmission']<=1+1e-11))

    def test_axisymmetric_rayleigh_uniform_disk_against_bessel(self):
        radius=.05;r=np.linspace(0,radius,70);angles=np.linspace(0,89,100);f=4000;v=np.ones_like(r,dtype=complex)
        actual=farfield(r,v,f,angles);x=2*np.pi*f/C*radius*np.sin(np.radians(angles));expected=np.ones_like(x);expected[1:]=2*j1(x[1:])/x[1:]
        np.testing.assert_allclose(actual/actual[0],expected,atol=1e-12)

    def test_fem_mesh_has_no_nearly_duplicate_axial_layers(self):
        c=next(c for c in json.loads((ROOT/'data/catalog.json').read_text()) if c['id']=='round-conical')
        mesh=make_mesh(c,h=.004);p=mesh['nodes'][mesh['triangles']]
        area=abs((p[:,1,0]-p[:,0,0])*(p[:,2,1]-p[:,0,1])-(p[:,2,0]-p[:,0,0])*(p[:,1,1]-p[:,0,1]))/2
        self.assertGreater(area.min(),1e-10)

    def test_fem_analytic_piston_and_energy_balance(self):
        c=next(c for c in json.loads((ROOT/'data/catalog.json').read_text()) if c['id']=='round-os')
        mesh=make_mesh(c,h=.00175,piston=True);m=assemble(mesh);s=solve(mesh,m,2000)
        ref=piston_load([2000],m['source_area'])[0]*m['source_area']/(RHO*C)
        self.assertLess(abs(s['zin_normalized']-ref)/abs(ref),.03)
        self.assertLess(s['power_balance_relative'],1e-8);self.assertLess(s['relative_residual'],1e-8)

    def test_rocket_domain_keeps_body_out_of_the_air_and_has_no_isolated_dofs(self):
        c=next(c for c in json.loads((ROOT/'data/catalog.json').read_text()) if c['id']=='rocket')
        mesh=make_mesh(c,h=.004)
        self.assertEqual(len(np.unique(mesh['triangles'])),len(mesh['nodes']))
        centroids=mesh['nodes'][mesh['triangles'][mesh['horn']]].mean(axis=1)
        z=centroids[:,1];inside_span=(z>.12*.24)&(z<.88*.24)
        radius=np.interp(z[inside_span],.24*np.array([.12,.28,.5,.7,.88]),.001*np.array([8,33,42,25,1.5]))
        self.assertTrue(np.all(centroids[inside_span,0]>=radius-1e-10))
        m=assemble(mesh);self.assertAlmostEqual(m['source_area'],np.pi*.025**2,places=12)

if __name__=='__main__':unittest.main(verbosity=2)
