"""Generate a neutral-pose shape-basis pilot from a local FLAME 2023 Open model.

No model download, fitting framework, texture assets or anatomical labels are
included. Only the neutral linear shape equation is evaluated; expressions and
all articulated poses remain zero. NumPy is the only additional dependency.
"""

import argparse
import hashlib
import io
import json
import pickle
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np

from .generate_heads import view_frame, write_head_run
from .geometry import FRAME

MODEL_NAME = 'flame2023_open.pkl'
LICENSE_URL = 'https://flame.is.tue.mpg.de/modellicense.html'
DOWNLOAD_URL = 'https://download.is.tue.mpg.de/download.php?domain=flame&sfile=FLAME2023Open.zip'


class _UnusedSparse:
    """Inert storage for unused joint regressors; no SciPy runtime is required."""

    def __setstate__(self, state):
        pass


class ArrayUnpickler(pickle.Unpickler):
    """Allow array construction, not arbitrary globals from model pickle files."""

    def find_class(self, module, name):
        if module in ('numpy',) and name in ('ndarray', 'dtype'):
            return getattr(np, name)
        if module in ('numpy.core.multiarray', 'numpy._core.multiarray') and name in ('_reconstruct', 'scalar'):
            return getattr(np._core.multiarray, name)
        if module in ('numpy.core.numeric', 'numpy._core.numeric') and name == '_frombuffer':
            return np._core.numeric._frombuffer
        if module in ('scipy.sparse.csc', 'scipy.sparse._csc', 'scipy.sparse.csr', 'scipy.sparse._csr') and name in ('csc_matrix', 'csr_matrix'):
            return _UnusedSparse
        if module == '_codecs' and name == 'encode':
            import codecs
            return codecs.encode
        raise ValueError(f'Unsupported model pickle global: {module}.{name}')


def load_model(path):
    path = Path(path)
    if not path.is_file():
        raise ValueError(f'Missing FLAME 2023 Open asset: {path}. Download {DOWNLOAD_URL}')
    archive_hash = None
    if path.suffix.lower() == '.zip':
        archive_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        with zipfile.ZipFile(path) as archive:
            matches = [m for m in archive.infolist() if Path(m.filename).name.lower() == MODEL_NAME and not m.is_dir()]
            if len(matches) != 1:
                raise ValueError(f'Expected exactly one {MODEL_NAME} in the official Open ZIP; found {len(matches)}')
            member = matches[0]
            if member.file_size > 250*1024*1024:
                raise ValueError('Model pickle exceeds 250 MB limit')
            content = archive.read(member)
            filename = member.filename
    else:
        if path.name.lower() != MODEL_NAME:
            raise ValueError(f'Expected {MODEL_NAME}; older FLAME releases must not be relabeled as Open')
        if path.stat().st_size > 250*1024*1024:
            raise ValueError('Model pickle exceeds 250 MB limit')
        content, filename = path.read_bytes(), path.name
    data = ArrayUnpickler(io.BytesIO(content), encoding='latin1').load()
    if not isinstance(data, dict):
        raise ValueError('Expected a FLAME model dictionary')
    try:
        template = np.asarray(data['v_template'], dtype=np.float64)
        basis = np.asarray(data['shapedirs'], dtype=np.float64)
        faces = np.asarray(data['f'])
    except (KeyError, TypeError) as exc:
        raise ValueError('Model needs v_template, shapedirs and f arrays') from exc
    if template.ndim != 2 or template.shape[1] != 3 or not 3 <= len(template) <= 20000:
        raise ValueError('Invalid template vertex array')
    if basis.ndim != 3 or basis.shape[:2] != template.shape or basis.shape[2] < 300:
        raise ValueError('Expected at least 300 shape components in shapedirs (V,3,K)')
    if faces.ndim != 2 or faces.shape[1] != 3 or not 1 <= len(faces) <= 40000 or faces.dtype.kind not in 'iu':
        raise ValueError('Invalid triangle array')
    if faces.min() < 0 or faces.max() >= len(template) or np.any(np.diff(np.sort(faces, axis=1), axis=1) == 0):
        raise ValueError('Invalid triangle indices')
    if not np.isfinite(template).all() or not np.isfinite(basis).all():
        raise ValueError('Model arrays must be finite')
    return template, basis[:, :, :300], faces.astype(np.int64), {
        'model_sha256': hashlib.sha256(content).hexdigest(), 'archive_sha256': archive_hash,
        'model_member': filename, 'release': 'FLAME-2023-Open',
    }


def geometry_report(vertices, faces, neutral):
    triangles = vertices[faces]
    normals = np.cross(triangles[:, 1]-triangles[:, 0], triangles[:, 2]-triangles[:, 0])
    areas = np.linalg.norm(normals, axis=1)/2
    reference = neutral[faces]
    reference_normals = np.cross(reference[:, 1]-reference[:, 0], reference[:, 2]-reference[:, 0])
    flipped = int(np.count_nonzero(np.einsum('ij,ij->i', normals, reference_normals) < 0))
    edges = Counter(tuple(sorted((int(a), int(b)))) for face in faces for a, b in zip(face, np.roll(face, -1)))
    return {
        'vertices': len(vertices), 'triangles': len(faces),
        'bounds_mm': {'min': vertices.min(axis=0).tolist(), 'max': vertices.max(axis=0).tolist()},
        'extent_mm': np.ptp(vertices, axis=0).tolist(), 'minimum_triangle_area_mm2': float(areas.min()),
        'degenerate_triangles': int(np.count_nonzero(areas <= 1e-12)), 'flipped_triangles_vs_neutral': flipped,
        'boundary_edges': sum(n == 1 for n in edges.values()), 'nonmanifold_edges': sum(n > 2 for n in edges.values()),
        'rms_vertex_change_mm': float(np.sqrt(np.mean(np.sum((vertices-neutral)**2, axis=1)))),
        'self_intersection_check': 'not_performed', 'anatomical_landmark_coverage': 'pending_visual_review',
    }


def generate(path, out, source_units, source_x='subject_left', coefficient=1.):
    if not np.isfinite(coefficient) or not 0 < coefficient <= 2:
        raise ValueError('Shape coefficient magnitude must be finite, greater than zero and at most 2')
    template, basis, faces, provenance = load_model(path)
    factor = {'m': 1000., 'mm': 1.}[source_units]
    axes = np.array([-1., 1., 1.]) if source_x == 'subject_right' else np.ones(3)
    if source_x == 'subject_right':
        faces = faces[:, [0, 2, 1]]  # Reflection also reverses winding.
    neutral = template*factor*axes
    diagonal = float(np.linalg.norm(np.ptp(neutral, axis=0)))
    if not 50 <= diagonal <= 1000:
        raise ValueError(f'Head extent is {diagonal:.3f} mm: check --source-units and the supplied asset')
    topology_hash = hashlib.sha256(faces.astype('<i8').tobytes()).hexdigest()[:16]
    identity = 'flame-open-pilot-' + provenance['model_sha256'][:16]
    choices = [('neutral', None, 0.), ('pc1-minus', 0, -coefficient), ('pc1-plus', 0, coefficient),
               ('pc2-minus', 1, -coefficient), ('pc2-plus', 1, coefficient)]
    records, reports = [], []
    for slug, component, coefficient in choices:
        beta = np.zeros(300)
        if component is not None:
            beta[component] = coefficient
        # At zero pose the identity skinning transforms leave this shape intact.
        vertices = np.round((template + np.einsum('vci,i->vc', basis, beta))*factor*axes, 6)
        report = geometry_report(vertices, faces, np.round(neutral, 6))
        if report['degenerate_triangles'] or report['flipped_triangles_vs_neutral']:
            raise ValueError(f'{slug} has {report["degenerate_triangles"]} degenerate triangles and '
                             f'{report["flipped_triangles_vs_neutral"]} triangle normal reversals relative to neutral; '
                             'inspect the region or choose a smaller --coefficient')
        record_id = identity + '-' + slug
        record = {
            'surface_record_version': '1.0.0', 'record_id': record_id,
            'topology_id': 'flame-open-' + topology_hash, 'units': 'mm', 'coordinate_frame': FRAME,
            'source': {'identity_id': identity, 'asset_id': 'FLAME-2023-Open', 'domain': 'synthetic',
                       'license': 'FLAME-2023-Open-Model-License', 'license_url': LICENSE_URL,
                       'url': DOWNLOAD_URL, 'attribution': 'Li et al., Learning a model of facial shape and expression from 4D scans, SIGGRAPH Asia 2017; Max Planck Institute for Intelligent Systems.',
                       'provenance': 'Local Open-release model; neutral pose/expression, first 300 shape directions only. Source units converted explicitly; no average-head size normalization. Source axes require visual confirmation.',
                       'parent_record_ids': [] if component is None else [identity+'-neutral'], **provenance},
            'generation': {'version': '1.0.0', 'method': 'neutral_linear_shape_basis', 'shape_coefficients': beta.tolist(),
                           'coefficient_magnitude': coefficient,
                           'expression': 'zero', 'pose': 'zero', 'source_units': source_units,
                           'source_axes': {'x': source_x, 'y': 'superior', 'z': 'anterior'}},
            'mesh': {'vertices': vertices.tolist(), 'triangles': faces.tolist()},
            'review': {'status': 'pending', 'reviewer': None},
            'limitations': ['Five basis perturbations share one conservative pilot lineage; not five independent participants.',
                            'No verified anatomical labels, tape routes, physical calibration, or population coverage.',
                            'No expression/articulated pose evaluation; PCA axes are not named anatomical controls.'],
        }
        records.append((slug, record)); reports.append({'record_id': record_id, **report})
    frame = view_frame(records[0][1])
    # Keep one framing for all pilot variants and rotations, without rescaling meshes.
    center = np.array(frame['center_mm'])
    radius = max(float(np.linalg.norm(np.array(record['mesh']['vertices'])-center, axis=1).max()) for _, record in records)
    frame['pixels_per_mm'] = min(1.45, 200/radius)
    manifest = {'version': '1.0.0', 'source_identity': identity, 'evidence': 'synthetic_geometry_preview',
                'anatomical_review': 'pending', 'source': provenance, 'variants': []}
    write_head_run(Path(out), records, manifest, frame)
    evaluation = {'release': 'FLAME-2023-Open', 'source': provenance, 'numpy_version': np.__version__,
                  'coefficient_magnitude': coefficient,
                  'decision': 'pending_visual_and_anatomical_review', 'meshes': reports,
                  'not_evaluated': ['Anatomical ear/nose/jaw landmark coverage', 'Population representativeness',
                                    'Self-intersections', 'Physical metric accuracy', 'Fixed-perimeter nasal controls',
                                    'Agreement with full articulated model implementation']}
    (Path(out)/'evaluation.json').write_text(json.dumps(evaluation, indent=2)+'\n')
    return evaluation


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, required=True, help='Official FLAME2023Open.zip or flame2023_Open.pkl')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--source-units', choices=['m', 'mm'], required=True)
    parser.add_argument('--source-x', choices=['subject_left', 'subject_right'], default='subject_left')
    parser.add_argument('--coefficient', type=float, default=1., help='Magnitude for the PC1/PC2 pilot; default 1, maximum 2')
    args = parser.parse_args()
    try:
        report = generate(args.model, args.out, args.source_units, args.source_x, args.coefficient)
    except (ValueError, OSError, pickle.UnpicklingError, zipfile.BadZipFile) as exc:
        parser.exit(1, f'FLAME import failed: {exc}\n')
    print(f'Generated {len(report["meshes"])} neutral-pose pilot meshes and 35 views in {args.out}')
