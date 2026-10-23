"""Validate labeled reference geometry and measure it in millimeters.

These are label-generation tools, not an image estimator. In particular, loading
a mesh at inference would leak the quantities the camera model must predict.
"""

import math

from . import MEASUREMENT_VERSION, SCHEMA_VERSION

MM_PER_UNIT = {"mm": 1.0, "m": 1000.0}
FRAME = {
    "handedness": "right",
    "x": "subject_left",
    "y": "superior",
    "z": "anterior",
}


def _number(value):
    return type(value) in (int, float) and math.isfinite(value)


def _vector(value, size):
    return isinstance(value, list) and len(value) == size and all(
        _number(component) for component in value
    )


def _nonempty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_reference(record):
    """Fail closed on unsupported versions, units, attachments and geometry."""
    _require(isinstance(record, dict), "reference must be an object")
    _require(record.get("schema_version") == SCHEMA_VERSION, "unsupported schema_version")
    _require(isinstance(record.get("units"), str) and record["units"] in MM_PER_UNIT,
             "units must be mm or m")
    _require(record.get("coordinate_frame") == FRAME, "unsupported coordinate_frame")
    for field in ("record_id", "topology_id"):
        _require(_nonempty_string(record.get(field)), f"missing {field}")
    source = record.get("source", {})
    _require(isinstance(source, dict), "source must be an object")
    for field in ("identity_id", "asset_id", "license", "provenance"):
        _require(_nonempty_string(source.get(field)), f"missing source.{field}")
    _require(source.get("domain") in ("analytic", "synthetic", "printed", "human"),
             "unsupported source.domain")
    parents = source.get("parent_record_ids")
    _require(isinstance(parents, list) and all(_nonempty_string(p) for p in parents),
             "source.parent_record_ids must be a list of record IDs")
    _require(record["record_id"] not in parents, "record cannot be its own parent")
    mesh = record.get("mesh", {})
    _require(isinstance(mesh, dict), "mesh must be an object")
    vertices, faces = mesh.get("vertices"), mesh.get("triangles")
    _require(isinstance(vertices, list) and len(vertices) >= 3
             and all(_vector(v, 3) for v in vertices), "invalid mesh.vertices")
    _require(isinstance(faces, list) and bool(faces), "mesh.triangles must not be empty")
    for face in faces:
        _require(isinstance(face, list) and len(face) == 3
                 and all(type(i) is int and 0 <= i < len(vertices) for i in face)
                 and len(set(face)) == 3,
                 "invalid triangle indices")
        a, b, c = [vertices[i] for i in face]
        u, v = [b[i] - a[i] for i in range(3)], [c[i] - a[i] for i in range(3)]
        cross = [u[1]*v[2] - u[2]*v[1], u[2]*v[0] - u[0]*v[2],
                 u[0]*v[1] - u[1]*v[0]]
        _require(math.hypot(*cross) > 0, "degenerate triangle")
    landmarks = record.get("landmarks")
    _require(isinstance(landmarks, dict) and bool(landmarks), "missing landmarks")
    for name, attachment in landmarks.items():
        _require(_nonempty_string(name) and isinstance(attachment, dict),
                 "invalid landmark")
        if attachment.get("kind") == "vertex":
            index = attachment.get("vertex_index")
            _require(type(index) is int and 0 <= index < len(vertices),
                     f"invalid vertex attachment: {name}")
        elif attachment.get("kind") == "barycentric":
            index, weights = attachment.get("triangle_index"), attachment.get("weights")
            _require(type(index) is int and 0 <= index < len(faces),
                     f"invalid triangle attachment: {name}")
            _require(_vector(weights, 3) and all(0 <= w <= 1 for w in weights)
                     and math.isclose(sum(weights), 1, abs_tol=1e-9),
                     f"invalid barycentric weights: {name}")
        else:
            raise ValueError(f"unsupported attachment kind: {name}")
    measurements = record.get("measurements")
    _require(isinstance(measurements, list) and bool(measurements), "missing measurements")
    names = set()
    for target in measurements:
        _require(isinstance(target, dict), "measurement must be an object")
        name = target.get("id")
        _require(_nonempty_string(name) and name not in names, "duplicate/missing measurement ID")
        names.add(name)
        kind, points = target.get("kind"), target.get("landmarks")
        _require(kind in ("straight_distance", "surface_polyline", "angle"),
                 "unsupported measurement kind")
        _require(isinstance(points, list) and all(isinstance(p, str) and p in landmarks for p in points),
                 f"unknown landmarks: {name}")
        expected_count = 3 if kind == "angle" else 2
        _require(len(points) >= expected_count and len(set(points)) == len(points),
                 f"invalid landmark count: {name}")
        _require(kind == "surface_polyline" or len(points) == expected_count,
                 f"wrong landmark count: {name}")
        _require(target.get("role") in ("target", "scale_anchor", "diagnostic"),
                 f"invalid role: {name}")
        _require(target.get("role") != "scale_anchor" or kind != "angle",
                 "angle cannot anchor metric scale")
        _require(target.get("definition_status") in ("analytic_only", "pending_review", "reviewed"),
                 f"missing definition_status: {name}")
        _require(_nonempty_string(target.get("definition")), f"missing definition: {name}")
        if kind == "surface_polyline":
            # Each short chord must stay within a single triangle. This is a
            # specified polyline on the surface, not an inferred geodesic.
            for left, right in zip(points, points[1:]):
                supports = []
                for point in (left, right):
                    attachment = landmarks[point]
                    if attachment["kind"] == "vertex":
                        supports.append({attachment["vertex_index"]})
                    else:
                        supports.append({i for i, w in zip(
                            faces[attachment["triangle_index"]], attachment["weights"]
                        ) if w > 0})
                _require(any(supports[0] | supports[1] <= set(face) for face in faces),
                         f"polyline leaves mesh surface: {name}")
    _require(record.get("camera") is None or isinstance(record["camera"], dict),
             "camera must be null or metadata object")
    review = record.get("review")
    _require(isinstance(review, dict) and review.get("status") in ("pending", "approved"),
             "missing review status")
    _require(review["status"] != "approved" or _nonempty_string(review.get("reviewer")),
             "approved review must name the reviewer")
    return record


def landmark_mm(record, name):
    """Resolve a topology-specific surface attachment into millimeter coordinates."""
    attachment = record["landmarks"][name]
    vertices = record["mesh"]["vertices"]
    if attachment["kind"] == "vertex":
        point = vertices[attachment["vertex_index"]]
    else:
        face = record["mesh"]["triangles"][attachment["triangle_index"]]
        point = [sum(weight * vertices[index][axis] for index, weight in zip(
            face, attachment["weights"]
        )) for axis in range(3)]
    return tuple(component * MM_PER_UNIT[record["units"]] for component in point)


def measure_reference(record):
    """Export geometry labels with units, provenance and review validity flags."""
    validate_reference(record)
    output = []
    for target in record["measurements"]:
        points = [landmark_mm(record, name) for name in target["landmarks"]]
        if target["kind"] == "angle":
            u, v = [[p[i] - points[1][i] for i in range(3)] for p in (points[0], points[2])]
            norm = math.hypot(*u) * math.hypot(*v)
            _require(norm > 0, f"undefined angle: {target['id']}")
            value = math.degrees(math.acos(max(-1, min(1, sum(
                a*b for a, b in zip(u, v)
            ) / norm))))
            unit = "deg"
        else:
            value = sum(math.dist(a, b) for a, b in zip(points, points[1:]))
            unit = "mm"
        _require(math.isfinite(value) and value > 0, f"invalid measurement: {target['id']}")
        output.append({
            "id": target["id"], "kind": target["kind"], "role": target["role"],
            "value": value, "unit": unit, "valid_geometry": True,
            "definition_status": target["definition_status"],
            "approved_for_anatomical_use": (
                target["definition_status"] == "reviewed"
                and record["review"]["status"] == "approved"
                and record["source"]["domain"] != "analytic"
            ),
        })
    return {
        "schema_version": SCHEMA_VERSION,
        "measurement_version": MEASUREMENT_VERSION,
        "model_version": None,
        "record_id": record["record_id"],
        "source": record["source"],
        "label_source": "reference_mesh_not_camera_prediction",
        "measurements": output,
    }
