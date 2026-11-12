import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import trimesh

from dimension_pipeline.flame_arc_coverage import diagnose, exclude_triangles, run
from dimension_pipeline.flame_arc_loss import supported_edges


class ArcCoverageTests(unittest.TestCase):
    def fixture(self):
        source=np.column_stack([np.arange(16)*.03,np.zeros((16,2))])
        normals=np.tile([0.,0.,1.],(16,1))
        target=trimesh.Trimesh([[0,0,0],[1,0,0],[0,1,0]],[[0,1,2]],process=False)
        return source,normals,target

    def test_all_flags_preserved_primary_precedence_and_exact_support_policy(self):
        source,normals,target=self.fixture();projected=source.copy()
        distances=np.zeros(16);distances[5]=.1
        normals[5]=[1,0,0]  # Same sample fails both distance and orientation.
        projected[10:]+=[0,.4,0]
        with patch('dimension_pipeline.flame_arc_coverage.nearest',return_value=(projected,distances,np.zeros(16,dtype=int))):
            result=diagnose(source,normals,target,1.,[])
        self.assertIn(5,result['sample_flags']['distance'])
        self.assertIn(5,result['sample_flags']['normal'])
        self.assertEqual(result['primary_reasons'][4],'distance')
        self.assertEqual(result['primary_reasons'][9],'projection_jump')
        valid=np.ones(16,dtype=bool);valid[5]=False
        self.assertEqual(result['supported_edges'],supported_edges(source,projected,valid,1.).tolist())
        self.assertEqual(sum(result['primary_counts'].values()),15)

    def test_short_islands_and_exclusion_are_not_promoted(self):
        source,normals,target=self.fixture();distances=np.ones(16)*.1;distances[:3]=0
        with patch('dimension_pipeline.flame_arc_coverage.nearest',return_value=(source.copy(),distances,np.zeros(16,dtype=int))):
            result=diagnose(source,normals,target,1.,[])
            excluded=diagnose(source,normals,target,1.,[{'center':[0,0,0],'radius':2}])
        self.assertEqual(result['primary_reasons'][:2],['short_run','short_run'])
        self.assertEqual(result['supported_edges'],[])
        self.assertTrue(all(r=='exclusion' for r in excluded['primary_reasons']))
        self.assertIn(4,excluded['edge_flags']['distance'])

    def test_broader_target_keeps_conservative_triangle_exclusion(self):
        mesh=trimesh.Trimesh([[0,0,0],[.1,0,0],[0,.1,0],[2,0,0],[3,0,0],[2,1,0]],[[0,1,2],[3,4,5]],process=False)
        result=exclude_triangles(mesh,[{'center':[0,0,0],'radius':.05}])
        self.assertEqual(len(result.faces),1)
        self.assertGreater(result.vertices[:,0].min(),1)
        with self.assertRaisesRegex(ValueError,'No broader'):
            exclude_triangles(mesh,[{'center':[0,0,0],'radius':10}])

    def test_output_cannot_overwrite_or_nest_under_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            source=Path(folder)/'fit';source.mkdir()
            with self.assertRaisesRegex(ValueError,'fresh output'):
                run(source,source,source,source/'nested')


if __name__=='__main__': unittest.main()
