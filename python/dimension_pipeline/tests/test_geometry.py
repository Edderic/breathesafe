"""Analytical checks independent of any face detector, weights or human data."""

import ast
import copy
import json
import math
from pathlib import Path
import re
import unittest

from dimension_pipeline.geometry import landmark_mm, measure_reference

FIXTURES = Path(__file__).parents[1] / "fixtures"


def load(name="base_mm.json"):
    return json.loads((FIXTURES / name).read_text())


def values(record):
    return {m["id"]: m["value"] for m in measure_reference(record)["measurements"]}


class GeometryTest(unittest.TestCase):
    def test_known_lengths_and_arc_not_chord(self):
        result = values(load())
        self.assertEqual(result["pilot_tip_to_base_midpoint"], 4)
        self.assertEqual(result["pilot_lower_span"], 12)
        self.assertEqual(result["analytic_ridge_polyline"], 10)
        self.assertEqual(result["analytic_ridge_chord"], 6)
        self.assertAlmostEqual(result["analytic_tip_angle"],
                               math.degrees(math.acos(7/25)))

    def test_meters_and_millimeters_match(self):
        mm, meters = load(), load()
        meters["units"] = "m"
        meters["mesh"]["vertices"] = [[v/1000 for v in p] for p in mm["mesh"]["vertices"]]
        for name, expected in values(mm).items():
            self.assertAlmostEqual(values(meters)[name], expected)

    def test_rotation_and_translation_preserve_measurements(self):
        record = load()
        expected = values(record)
        # Proper 90 degree rotation about y, followed by a translation.
        record["mesh"]["vertices"] = [[z+20, y-13, -x+8]
                                        for x, y, z in record["mesh"]["vertices"]]
        for name, value in values(record).items():
            self.assertAlmostEqual(value, expected[name])

    def test_global_size_changes_lengths_but_not_angles(self):
        base, larger = values(load()), values(load("larger_m.json"))
        for name, value in base.items():
            self.assertAlmostEqual(larger[name], value * (1 if name.endswith("angle") else 1.5))

    def test_local_shape_changes_without_changing_independent_span(self):
        base, local = values(load()), values(load("local_nose_mm.json"))
        self.assertEqual(local["pilot_lower_span"], base["pilot_lower_span"])
        self.assertEqual(local["analytic_ridge_chord"], base["analytic_ridge_chord"])
        self.assertEqual(local["pilot_tip_to_base_midpoint"], 6)
        self.assertAlmostEqual(local["analytic_ridge_polyline"], 2 * math.sqrt(45))
        self.assertNotEqual(local["analytic_tip_angle"], base["analytic_tip_angle"])

    def test_barycentric_landmark_uses_surface_attachment(self):
        self.assertEqual(landmark_mm(load(), "ridge_base_midpoint"), (0, 0, 0))

    def test_manifest_oracle_and_identity_lineage(self):
        manifest = json.loads((FIXTURES / "manifest.json").read_text())
        for variant in manifest["variants"]:
            record = load(variant["path"])
            self.assertEqual(record["source"]["identity_id"], "analytic-source-001")
            for name, expected in variant["expected_mm"].items():
                self.assertAlmostEqual(values(record)[name], expected)
            if variant["path"] != "base_mm.json":
                self.assertEqual(record["source"]["parent_record_ids"], [load()["record_id"]])

    def test_provenance_and_validity_do_not_claim_camera_or_anatomical_accuracy(self):
        record = load()
        record["review"]["status"] = "approved"
        record["review"]["reviewer"] = "mathematical-test-only"
        result = measure_reference(record)
        self.assertIsNone(result["model_version"])
        self.assertEqual(result["label_source"], "reference_mesh_not_camera_prediction")
        self.assertEqual(result["source"]["domain"], "analytic")
        for target in result["measurements"]:
            self.assertTrue(target["valid_geometry"])
            self.assertFalse(target["approved_for_anatomical_use"])

    def test_invalid_inputs_fail(self):
        mutations = [
            lambda r: r.update(units="pixels"),
            lambda r: r.update(schema_version="2.0.0"),
            lambda r: r["mesh"]["vertices"][0].__setitem__(0, float("nan")),
            lambda r: r["mesh"]["triangles"].__setitem__(0, [0, 0, 2]),
            lambda r: r["landmarks"]["tip"].update(vertex_index=999),
            lambda r: r["landmarks"]["tip"].update(vertex_index=True),
            lambda r: r["landmarks"]["ridge_base_midpoint"].update(weights=[1, 1, 0]),
            lambda r: r["measurements"][0].update(landmarks=["tip", "unknown"]),
            lambda r: r["measurements"].append(copy.deepcopy(r["measurements"][0])),
            lambda r: r["measurements"][2].update(landmarks=["span_left", "tip", "span_right"]),
            lambda r: r.update(review=None),
            lambda r: r.update(review={"status": "approved", "reviewer": None}),
            lambda r: r["mesh"]["vertices"].__setitem__(2, [0, 0, 0]),
        ]
        for mutate in mutations:
            record = load()
            mutate(record)
            with self.subTest(mutate=mutate), self.assertRaises(ValueError):
                measure_reference(record)

    def test_legacy_snapshot_preserves_both_existing_definitions(self):
        root = Path(__file__).parents[3]
        snapshot = json.loads((FIXTURES.parent / "legacy_arkit_paths.json").read_text())
        function = next(node for node in ast.parse((root / "python/mask_recommender/arkit/preprocessing.py").read_text()).body
                        if isinstance(node, ast.FunctionDef) and node.name == "summarize_measurements")
        python_paths = {node.targets[0].id[:-5]: ast.literal_eval(node.value)
                        for node in function.body if isinstance(node, ast.Assign)
                        and isinstance(node.targets[0], ast.Name)
                        and node.targets[0].id.endswith("_keys")}
        ruby = (root / "app/models/facial_measurement.rb").read_text()
        ruby_paths = {name: keys.split() for name, keys in re.findall(
            r"(\w+)_keys = %w\[(.*?)\]", ruby, re.DOTALL)}
        self.assertEqual(snapshot["segments"], python_paths)
        self.assertEqual(snapshot["segments"], ruby_paths)
        segments = [segment for name in snapshot["scoring_paths"]
                    for segment in snapshot["segments"][name]]
        self.assertEqual(len(segments), 46)
        self.assertEqual(len({v for segment in segments for v in segment.split("-")}), 46)

    def test_retrieved_definitions_preserve_surface_chord_and_height_distinctions(self):
        registry = json.loads((FIXTURES.parent / "target_registry.json").read_text())
        candidates = {feature["id"]: feature for feature in registry["compact_candidates"]}
        self.assertEqual(len(candidates), 5)
        self.assertEqual(candidates["yu2024_mid_nose_slope"]["kind"], "surface_distance")
        nasal_surface = candidates["yu2024_nose_protrusion"]
        nasal_chord = registry["pilot_candidates"][0]
        self.assertEqual(nasal_surface["landmarks"], nasal_chord["landmarks"])
        self.assertEqual(nasal_surface["kind"], "surface_distance")
        self.assertEqual(nasal_chord["kind"], "straight_distance")
        self.assertEqual(candidates["yu2024_ear_height_top"]["kind"], "vertical_distance_to_plane")
        for feature in candidates.values():
            self.assertEqual(feature["unit"], "mm")
            self.assertEqual(feature["status"], "definition_retrieved_pending_anatomical_review")
            self.assertEqual(feature["implementation_status"], "not_implemented")
            self.assertTrue(feature["blocker"])
        self.assertEqual(registry["review"]["status"], "pending")
        for feature in registry["other_candidates"]:
            self.assertEqual(feature["status"], "blocked_definition")
            self.assertIsNone(feature["kind"])


if __name__ == "__main__":
    unittest.main()
