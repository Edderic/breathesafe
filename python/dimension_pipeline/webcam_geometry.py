"""Research geometry. COLMAP world -> camera is Xc = R Xw + t; pixels are unmirrored."""
import copy
import heapq
import math
import statistics


def readings(values):
    if not isinstance(values, list) or len(values) != 3 or any(
        type(v) not in (float, int) or not math.isfinite(v) or v <= 0 for v in values
    ):
        raise ValueError('Provide three positive finite tape readings in mm.')
    return {'readings_mm': values, 'median_mm': statistics.median(values),
            'spread_mm': max(values)-min(values)}


def attachment(mesh, a):
    if not isinstance(a, dict):
        raise ValueError('Invalid surface attachment.')
    i, w = a.get('triangle_index'), a.get('weights')
    if a.get('kind') != 'barycentric' or type(i) is not int or not 0 <= i < len(mesh['triangles']) or not isinstance(w, list) or len(w) != 3 or any(
        type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1 for v in w
    ) or abs(sum(w)-1) > 1e-8:
        raise ValueError('Invalid surface attachment.')
    return [sum(mesh['vertices'][v][axis]*weight for v, weight in zip(mesh['triangles'][i], w)) for axis in range(3)]


def route_length(mesh, route, via):
    """Piecewise mesh-edge paths through all tape controls, never across components."""
    if not isinstance(route, list) or not 3 <= len(route) <= 200 or not all(isinstance(a, dict) for a in route) or route[0].get('label') != 'left_tragion' or route[-1].get('label') != 'right_tragion' or sum(a.get('label') == via for a in route) != 1:
        raise ValueError(f'Trace left tragion through {via} to right tragion, with intermediate controls.')
    graph = [{} for _ in mesh['vertices']]
    for face in mesh['triangles']:
        for a, b in zip(face, face[1:]+face[:1]):
            graph[a][b] = graph[b][a] = math.dist(mesh['vertices'][a], mesh['vertices'][b])
    points = [attachment(mesh, a) for a in route]
    total = 0.
    for a, b, pa, pb in zip(route, route[1:], points, points[1:]):
        if a['triangle_index'] == b['triangle_index']:
            total += math.dist(pa, pb)
            continue
        goals = {v: math.dist(mesh['vertices'][v], pb) for v in mesh['triangles'][b['triangle_index']]}
        distances = {v: math.dist(pa, mesh['vertices'][v]) for v in mesh['triangles'][a['triangle_index']]}
        heap = [(d, v) for v, d in distances.items()]; heapq.heapify(heap)
        best = math.inf
        while heap:
            d, v = heapq.heappop(heap)
            if d != distances[v]:
                continue
            if d > best:
                break
            if v in goals:
                best = min(best, d+goals[v])
            for n, edge in graph[v].items():
                if d+edge < distances.get(n, math.inf):
                    distances[n] = d+edge; heapq.heappush(heap, (d+edge, n))
        if not math.isfinite(best):
            raise ValueError('Tape route crosses disconnected or missing surface coverage.')
        total += best
    if total <= 0:
        raise ValueError('Tape route has zero length.')
    return total


def calibrate(surface, cameras, payload):
    anchor = readings(payload['scale_readings_mm']); check = readings(payload['check_readings_mm'])
    length = route_length(surface['mesh'], payload['scale_route'], 'subnasale')
    check_length = route_length(surface['mesh'], payload['check_route'], 'menton')
    scale = anchor['median_mm']/length
    record = copy.deepcopy(surface); models = copy.deepcopy(cameras)
    record['mesh']['vertices'] = [[v*scale for v in p] for p in surface['mesh']['vertices']]
    record['units'] = 'mm'
    for c in models.values():
        c['t'] = [v*scale for v in c['t']]; c['units'] = 'mm'
    report = {'method': 'uniform_tape_arc_median_v1', 'route_method': 'mesh_edge_dijkstra_v1',
              'mm_per_reconstruction_unit': scale, 'scale': {**anchor, 'route': payload['scale_route'], 'length_reconstruction_units': length},
              'independent_check': {**check, 'route': payload['check_route'], 'mesh_length_mm': check_length*scale,
                                    'discrepancy_mm': check_length*scale-check['median_mm'],
                                    'discrepancy_percent': 100*(check_length*scale/check['median_mm']-1)},
              'accuracy_status': 'not_independently_validated'}
    record['scale'] = report
    return record, models, report


def camera_pixel(camera, point):
    p = [sum(camera['R'][i][j]*point[j] for j in range(3))+camera['t'][i] for i in range(3)]
    if p[2] <= 0:
        raise ValueError('Point behind camera.')
    x, y = p[0]/p[2], p[1]/p[2]
    factor = 1+camera.get('k', 0)*(x*x+y*y)
    return [camera['fx']*x*factor+camera['cx'], camera['fy']*y*factor+camera['cy']]


def ray(camera, pixel):
    xd, yd = (pixel[0]-camera['cx'])/camera['fx'], (pixel[1]-camera['cy'])/camera['fy']
    x, y = xd, yd
    for _ in range(50):
        f = 1+camera.get('k', 0)*(x*x+y*y)
        if f <= 0:
            raise ValueError('Noninvertible radial distortion.')
        x, y = xd/f, yd/f
    if math.hypot(x*(1+camera.get('k', 0)*(x*x+y*y))-xd, y*(1+camera.get('k', 0)*(x*x+y*y))-yd) > 1e-7:
        raise ValueError('Radial inversion failed.')
    rt = list(zip(*camera['R']))
    origin = [-sum(row[j]*camera['t'][j] for j in range(3)) for row in rt]
    direction = [sum(row[j]*[x, y, 1][j] for j in range(3)) for row in rt]
    return origin, direction


def project(mesh, camera, landmarks):
    if camera.get('k', 0) != 0 or camera.get('mirrored') is not False:
        raise ValueError('Projection requires an undistorted unmirrored image and its camera.')
    sub = lambda a, b: [x-y for x, y in zip(a, b)]
    dot = lambda a, b: sum(x*y for x, y in zip(a, b))
    cross = lambda a, b: [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
    rows = []
    for index, raw in enumerate(landmarks):
        row = {'index': index, 'raw': raw, 'acceptance': 'pending', 'status': 'missed_surface'}
        if any(type(raw.get(v)) not in (int, float) or not math.isfinite(raw[v]) for v in ('x', 'y')):
            row['status'] = 'invalid_coordinates'; rows.append(row); continue
        if not 0 <= raw['x'] <= 1 or not 0 <= raw['y'] <= 1:
            row['status'] = 'outside_image'; rows.append(row); continue
        origin, direction = ray(camera, [raw['x']*camera['width'], raw['y']*camera['height']])
        best = math.inf
        for i, face in enumerate(mesh['triangles']):
            a, b, c = [mesh['vertices'][v] for v in face]
            e1, e2 = sub(b, a), sub(c, a); h = cross(direction, e2); determinant = dot(e1, h)
            if abs(determinant) < 1e-12:
                continue
            s = sub(origin, a); u = dot(s, h)/determinant
            q = cross(s, e1); v = dot(direction, q)/determinant; depth = dot(e2, q)/determinant
            if u >= 0 and v >= 0 and u+v <= 1 and 0 < depth < best:
                best = depth
                row.update(status='ok', attachment={'kind': 'barycentric', 'triangle_index': i, 'weights': [1-u-v, u, v]},
                           point=[origin[j]+depth*direction[j] for j in range(3)], units=camera['units'])
        rows.append(row)
    return rows
