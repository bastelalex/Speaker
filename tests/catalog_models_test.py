"""Geometric/export invariants; independent of any acoustic performance claims."""
from pathlib import Path
from collections import Counter
import unittest,json,sys,math
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from catalog_models import generate,sub,cross,dot,obj,stl
CATALOG=json.loads((ROOT/'data/catalog.json').read_text())

class CatalogModels(unittest.TestCase):
    def test_required_families_and_source_ids(self):
        self.assertEqual(len(CATALOG),12)
        ids={s['id'] for s in json.loads((ROOT/'data/sources.json').read_text())}
        self.assertTrue({'round-conical','round-os','oval','superellipse','prism','round-slot'} <= {c['id'] for c in CATALOG})
        for c in CATALOG:self.assertTrue(set(c['refs'])<=ids)

    def test_closed_oriented_nondegenerate_material_components(self):
        for c in CATALOG:
            with self.subTest(model=c['id']):
                mesh=generate(c);edges=Counter();directed=Counter()
                self.assertTrue(all(math.isfinite(v) for p in mesh.vertices for v in p))
                for a,b,c_,_ in mesh.faces:
                    v=mesh.vertices
                    self.assertGreater(dot(cross(sub(v[b],v[a]),sub(v[c_],v[a])),cross(sub(v[b],v[a]),sub(v[c_],v[a]))),1e-12)
                    for x,y in [(a,b),(b,c_),(c_,a)]:edges[tuple(sorted((x,y)))]+=1;directed[(x,y)]+=1
                self.assertTrue(all(n==2 for n in edges.values()),'each material edge must have exactly 2 faces')
                self.assertTrue(all(directed[(b,a)]==n for (a,b),n in directed.items()),'neighbor faces must have opposite edge directions')
                for part in mesh.parts:
                    faces=mesh.faces[part['face_start']:part['face_start']+part['face_count']]
                    volume=sum(dot(mesh.vertices[a],cross(mesh.vertices[b],mesh.vertices[c_])) for a,b,c_,_ in faces)/6
                    self.assertGreater(volume,0)

    def test_exports_are_reproducible_and_stl_keeps_every_face(self):
        for c in CATALOG:
            with self.subTest(model=c['id']):
                mesh=generate(c)
                self.assertEqual((ROOT/'models'/(c['id']+'.obj')).read_text(),obj(mesh,c))
                content=(ROOT/'models'/(c['id']+'.stl')).read_text()
                self.assertEqual(content,stl(mesh,c));self.assertEqual(content.count('facet normal '),len(mesh.faces))

    def test_exact_prism_corners_and_os_radius(self):
        prism=generate(next(c for c in CATALOG if c['id']=='prism'))
        for x,y in [(120,30),(-120,30),(-120,-30),(120,-30)]:self.assertIn([x,y,180],prism.vertices)
        c=next(c for c in CATALOG if c['id']=='round-os');mesh=generate(c)
        radius=math.sqrt((c['throat']/2)**2+c['length']**2)
        mouth=[p for p in mesh.vertices if p[2]==c['length']]
        self.assertTrue(any(abs(math.hypot(p[0],p[1])-radius)<1e-5 for p in mouth))

    def test_multicell_ports_stay_distinct(self):
        for id in ('multi','poly'):
            mesh=generate(next(c for c in CATALOG if c['id']==id))
            self.assertEqual(len(mesh.parts),6)
            # At both port planes outer rings of adjacent cells have a positive gap.
            for z in (0,max(p[2] for p in mesh.vertices)):
                boxes=[]
                for part in mesh.parts:
                    faces=mesh.faces[part['face_start']:part['face_start']+part['face_count']]
                    points=[mesh.vertices[i] for f in faces for i in f[:3] if mesh.vertices[i][2]==z]
                    boxes.append((min(p[0] for p in points),max(p[0] for p in points),min(p[1] for p in points),max(p[1] for p in points)))
                for i,a in enumerate(boxes):
                    for b in boxes[i+1:]:self.assertTrue(a[1]<b[0] or b[1]<a[0] or a[3]<b[2] or b[3]<a[2])

if __name__=='__main__':unittest.main(verbosity=2)
