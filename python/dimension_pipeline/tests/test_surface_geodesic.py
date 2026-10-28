import copy
import math
import unittest

from dimension_pipeline.surface_geodesic import DEFAULT_BINARY, solve_payload, validate_payload


def endpoint(face, weights):
    return {'kind': 'barycentric', 'triangle_index': face, 'weights': weights}


def query(mesh, a, b):
    return {'units': 'mm', 'mesh': mesh, 'queries': [{'id': 'test', 'start': a, 'end': b}]}


def point(mesh, attachment):
    if attachment['kind'] == 'vertex':
        return mesh['vertices'][attachment['vertex_index']]
    face = mesh['triangles'][attachment['triangle_index']]
    return [sum(attachment['weights'][j]*mesh['vertices'][face[j]][i] for j in range(3)) for i in range(3)]


class SurfaceGeodesicValidationTest(unittest.TestCase):
    def test_bad_payloads_fail_before_native_process(self):
        mesh = {'vertices': [[0, 0, 0], [1, 0, 0], [0, 1, 0]], 'triangles': [[0, 1, 2]]}
        payload = query(mesh, endpoint(0, [1, 0, 0]), endpoint(0, [0, 1, 0]))
        for mutate in [lambda p: p.update(units='m'), lambda p: p['mesh']['vertices'][0].__setitem__(0, math.nan),
                       lambda p: p['queries'][0]['start'].update(triangle_index=-1),
                       lambda p: p['queries'][0]['start'].update(weights=[0, 0, 0]),
                       lambda p: p['mesh']['triangles'][0].__setitem__(0, 999)]:
            invalid = copy.deepcopy(payload); mutate(invalid)
            with self.assertRaises(ValueError):
                validate_payload(invalid)


@unittest.skipUnless(DEFAULT_BINARY.is_file(), 'Build native/surface_geodesic to run CGAL integration tests')
class ContinuousSurfaceGeodesicTest(unittest.TestCase):
    def test_flat_square_crosses_triangle_interior_and_recovers_chord(self):
        mesh = {'vertices': [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], 'triangles': [[0, 1, 2], [0, 2, 3]]}
        a, b = endpoint(0, [0, 1, 0]), endpoint(1, [0, 0, 1])
        result = solve_payload(query(mesh, a, b))['results'][0]
        self.assertAlmostEqual(result['length_mm'], math.sqrt(2), places=12)
        points = [point(mesh, p) for p in result['path']]
        self.assertTrue(any(math.dist(p, [.5, .5, 0]) < 1e-10 for p in points))
        self.assertEqual(result['path'][0], a)
        self.assertEqual(result['path'][-1], b)

    def test_folded_triangles_match_unfolded_analytic_distance_and_scale(self):
        mesh = {'vertices': [[0, 0, 0], [2, 0, 0], [0, 0, 2], [0, 2, 0]], 'triangles': [[0, 1, 2], [0, 2, 3]]}
        a, b = endpoint(0, [.2, .5, .3]), endpoint(1, [.2, .2, .6])
        result = solve_payload(query(mesh, a, b))['results'][0]
        self.assertAlmostEqual(result['length_mm'], math.hypot(2.2, .2), places=10)
        self.assertGreater(result['length_mm'], math.dist(point(mesh, a), point(mesh, b)))
        mesh['vertices'] = [[-1.5*y+10, 1.5*x-7, 1.5*z+30] for x, y, z in mesh['vertices']]
        transformed = solve_payload(query(mesh, a, b))['results'][0]
        self.assertAlmostEqual(transformed['length_mm'], 1.5*result['length_mm'], places=10)

    def test_same_face_preserves_barycentric_order_for_interior_endpoints(self):
        mesh = {'vertices': [[4, 0, 0], [0, 3, 0], [0, 0, 0]], 'triangles': [[2, 0, 1]]}
        a, b = endpoint(0, [.2, .3, .5]), endpoint(0, [.1, .7, .2])
        result = solve_payload(query(mesh, a, b))['results'][0]
        self.assertAlmostEqual(result['length_mm'], math.dist(point(mesh, a), point(mesh, b)), places=12)

    def test_disconnected_components_do_not_connect_at_coincident_points(self):
        mesh = {'vertices': [[0, 0, 0], [1, 0, 0], [0, 1, 0]]*2, 'triangles': [[0, 1, 2], [3, 4, 5]]}
        result = solve_payload(query(mesh, endpoint(0, [.2, .3, .5]), endpoint(1, [.2, .3, .5])))['results'][0]
        self.assertEqual(result['status'], 'disconnected')
        self.assertIsNone(result['length_mm'])

    def test_inconsistent_face_orientation_is_rejected(self):
        mesh = {'vertices': [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], 'triangles': [[0, 1, 2], [0, 3, 2]]}
        with self.assertRaisesRegex(ValueError, 'manifold'):
            solve_payload(query(mesh, endpoint(0, [.2, .3, .5]), endpoint(1, [.2, .3, .5])))


if __name__ == '__main__':
    unittest.main()
