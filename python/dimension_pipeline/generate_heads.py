"""Offline head variants and orthographic SVG captures for landmark review.

Run: PYTHONPATH=python python3 -m dimension_pipeline.generate_heads --out /tmp/heads
No anatomical labels are invented. All variants share a single source identity.
"""

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path

ASSETS = Path(__file__).parent / "assets"


def load(name):
    return json.loads((ASSETS / name).read_text())


def variant_record(base, variant):
    record = copy.deepcopy(base)
    record["record_id"] = "makehuman-head-" + variant["id"]
    record["source"]["parent_record_ids"] = [base["record_id"]] if variant["id"] != "base" else []
    record["generation"] = {"version": "1.0.0", "seed": 0, "controls": variant}
    vertices = []
    for x, y, z in base["mesh"]["vertices"]:
        # Narrow anterior-only smooth bump; no assumed landmark at its center.
        nasal = math.exp(-((x / 15) ** 2 + ((y + 20) / 22) ** 2 + ((z - 150) / 35) ** 2))
        jaw = math.exp(-((y + 65) / 30) ** 2)
        vertices.append([round(x * variant["width"] * (1 + (variant["jaw"] - 1) * jaw) * variant["scale"], 6),
                         round(y * variant["scale"], 6),
                         round((z + variant["nose_mm"] * nasal) * variant["scale"], 6)])
    record["mesh"]["vertices"] = vertices
    return record


def view_frame(base):
    vertices = base["mesh"]["vertices"]
    low = [min(p[i] for p in vertices) for i in range(3)]
    high = [max(p[i] for p in vertices) for i in range(3)]
    return {"center_mm": [(a + b) / 2 for a, b in zip(low, high)], "pixels_per_mm": 1.45,
            "projection": "orthographic", "width": 720, "height": 480,
            "mirrored": False, "distortion": "none", "version": "1.0.0"}


def project(point, camera):
    x, y, z = [v - c for v, c in zip(point, camera["center_mm"])]
    a, b = math.radians(camera["yaw"]), math.radians(camera["pitch"])
    rx, rz = math.cos(a)*x + math.sin(a)*z, -math.sin(a)*x + math.cos(a)*z
    ry, depth = math.cos(b)*y - math.sin(b)*rz, math.sin(b)*y + math.cos(b)*rz
    return [360 + rx*camera["pixels_per_mm"], 240 - ry*camera["pixels_per_mm"], depth]


def render_svg(record, camera):
    points = [project(p, camera) for p in record["mesh"]["vertices"]]
    faces = sorted(record["mesh"]["triangles"], key=lambda f: sum(points[i][2] for i in f))
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 480" width="720" height="480">',
             '<rect width="720" height="480" fill="#edf2f5"/>']
    for face in faces:
        a, b, c = [points[i] for i in face]
        u, v = [b[i]-a[i] for i in range(3)], [c[i]-a[i] for i in range(3)]
        n = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]]
        norm = math.hypot(*n)
        brightness = .4 + .6 * abs((-.3*n[0]-.5*n[1]+n[2]) / (norm * math.sqrt(1.34))) if norm else .4
        color = [round(channel*brightness) for channel in (180, 202, 212)]
        polygon = ' '.join(f'{points[i][0]:.3f},{points[i][1]:.3f}' for i in face)
        parts.append(f'<polygon points="{polygon}" fill="rgb({color[0]},{color[1]},{color[2]})"/>')
    parts.append('</svg>')
    return '\n'.join(parts)


def generate(out):
    # Refuse overwriting an existing run, including annotation files.
    out.mkdir(parents=True, exist_ok=False)
    base = load("makehuman_head.json")
    template_hash = hashlib.sha256((ASSETS / "makehuman_head.json").read_bytes()).hexdigest()
    manifest = {"version": "1.0.0", "seed": 0, "source_identity": base["source"]["identity_id"],
                "template_sha256": template_hash, "evidence": "synthetic_geometry_preview",
                "anatomical_review": "pending", "variants": []}
    for variant in load("head_variants.json"):
        record = variant_record(base, variant)
        mesh_file = variant["id"] + '.json'
        content = json.dumps(record, separators=(',', ':')) + '\n'
        (out / mesh_file).write_text(content)
        # OBJ makes the same surface available to other 3D tools.
        obj = ['v ' + ' '.join(map(str, p)) for p in record["mesh"]["vertices"]]
        obj += ['f ' + ' '.join(str(i+1) for i in f) for f in record["mesh"]["triangles"]]
        (out / (variant["id"] + '.obj')).write_text('\n'.join(obj) + '\n')
        item = {"id": record["record_id"], "mesh": mesh_file,
                "sha256": hashlib.sha256(content.encode()).hexdigest(), "views": []}
        for view in load("head_views.json"):
            camera = {**view_frame(base), **view}
            filename = variant["id"] + '-' + view["id"] + '.svg'
            (out / filename).write_text(render_svg(record, camera))
            item["views"].append({"image": filename, "camera": camera})
        manifest["variants"].append(item)
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    cards = ''.join(f'<figure><img width="300" src="{view["image"]}"><figcaption>{view["image"]}</figcaption></figure>'
                    for item in manifest["variants"] for view in item["views"])
    (out / 'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Head review</title>'
                                  '<h1>Synthetic head previews — anatomical review pending</h1>'
                                  '<p>Five derivatives of one identity; nominal model millimeters.</p>'
                                  '<main style="display:flex;flex-wrap:wrap">' + cards + '</main></html>')
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = generate(args.out)
    print(f'Generated {len(result["variants"])} heads and 35 views in {args.out}')
