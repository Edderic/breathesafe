"""Self-contained private comparison; open locally without serving captures."""
import hashlib
import json
from pathlib import Path

import numpy as np
import trimesh


def write_view(out, report, source, target, camera):
    out = Path(out)
    rotation = np.diag([1., -1., -1.]) @ np.asarray(camera['R'])
    center = target.bounds.mean(axis=0)
    def payload(mesh):
        return {'vertices': np.round((mesh.vertices-center) @ rotation.T, 7).tolist(),
                'triangles': mesh.faces.tolist()}
    data = {'report': report, 'analysis': payload(source), 'target': payload(target), 'full_variants':{}, 'camera':camera,
            'display_transform':{'R':rotation.tolist(),'center':center.tolist()},
            'variants': {v.get('id',str(v['components'])): payload(trimesh.load(out/v['face_mesh'], process=False)) for v in report['variants']},
            'patches': [{'center': ((np.asarray(p['center'])-center) @ rotation.T).tolist(), 'radius': p['radius']} for p in report['exclusions']]}
    topology_file=out/'face-topology.json'
    if topology_file.is_file():
        topology=json.loads(topology_file.read_text())
        for row in report['variants']:
            path=out/row['full_mesh']
            if hashlib.sha256(path.read_bytes()).hexdigest()!=row['full_mesh_sha256']:
                raise ValueError('Fitted full mesh hash changed; cannot attach original indices.')
            full=trimesh.load(path,process=False)
            from .flame_mapping import topology_id
            if topology_id(full.faces)!=report['flame_topology_id'] or topology['topology_id']!=report['flame_topology_id']:
                raise ValueError('Fitted mesh original topology changed.')
            if not np.array_equal(full.faces[topology['original_triangle_ids']],topology['original_triangles']):
                raise ValueError('Face crop lost its original FLAME triangle correspondence.')
            whole=payload(full)
            whole.update(original_vertex_ids=list(range(len(full.vertices))),original_triangle_ids=list(range(len(full.faces))),
                         world_vertices=np.asarray(full.vertices).tolist(),fitted_vertex_ids=topology['original_vertex_ids'],
                         mesh_sha256=row['full_mesh_sha256'])
            data['full_variants'][row.get('id',str(row['components']))]=whole
            # Build the display directly from original indices, so it cannot
            # silently inherit a PLY loader's welding/reindexing convention.
            original=np.asarray(topology['original_vertex_ids'])
            remap=np.full(len(full.vertices),-1,dtype=int);remap[original]=np.arange(len(original))
            triangles=np.asarray(topology['original_triangles'])
            if not np.array_equal(np.unique(triangles),original):
                raise ValueError('Face crop original vertex mapping is incomplete or reordered.')
            mesh=trimesh.Trimesh(full.vertices[original],remap[triangles],process=False)
            item=payload(mesh)
            item.update(original_vertex_ids=original.tolist(),original_triangle_ids=topology['original_triangle_ids'])
            data['variants'][row.get('id',str(row['components']))]=item
    html = Path(__file__).with_name('flame_fit_view.html').read_text()
    encoded = json.dumps(data, separators=(',', ':'), allow_nan=False).replace('<', '\\u003c')
    helper=Path(__file__).with_name('flame_mapping_ui.js').read_text()
    measurements=Path(__file__).with_name('flame_measurements_ui.js').read_text()
    (out/'comparison.html').write_text(html.replace('/*FIT_DATA*/', encoded).replace('/*MAPPING_HELPERS*/',helper).replace('/*MEASUREMENT_HELPERS*/',measurements))
