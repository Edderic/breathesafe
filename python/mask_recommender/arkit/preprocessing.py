"""Preprocessing script for ARKit facial measurements data."""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, Any


def summarize_measurements(data: Dict[str, Any]) -> Dict[str, float]:
    """
    Summarize facial measurements by summing values into 5 subsections.

    Args:
        data: Dictionary with keys like "160-371" and numeric distance values.
              If data is nested, it will try to find the measurements dict.

    Returns:
        Dictionary with 5 aggregated measurements:
        - nose: sum of nose measurements
        - strap: sum of strap measurements
        - top_cheek: sum of top cheek measurements
        - mid_cheek: sum of mid cheek measurements
        - chin: sum of chin measurements
    """
    # Handle nested data structures - check if measurements are nested
    measurements_dict = data
    if isinstance(data, dict):
        # Check if data contains a nested dict with measurement-like keys
        # Look for common patterns: keys containing "-" or numeric tuples
        has_measurement_keys = any(
            isinstance(k, str) and "-" in str(k) for k in data.keys()
        )

        if not has_measurement_keys:
            # Try to find nested dict with measurements
            for key, value in data.items():
                if isinstance(value, dict):
                    # Check if this nested dict has measurement-like keys
                    nested_has_measurements = any(
                        isinstance(k, str) and "-" in str(k) for k in value.keys()
                    )
                    if nested_has_measurements:
                        measurements_dict = value
                        break
    # Define the measurement keys for each subsection
    nose_keys = [
        "160-371",  # nose left 4
        "371-367",  # nose left 3
        "367-387",  # nose left 2
        "387-14",   # nose left 1
        "609-802",  # nose right 4
        "802-798",  # nose right 3
        "798-14",   # nose right 2
        "14-818",   # nose right 1
    ]

    strap_keys = [
        "967-464",  # left strap 4
        "464-456",  # left strap 3
        "456-451",  # left strap 2
        "451-455",  # left strap 1
        "999-1027", # right strap 4
        "1027-884", # right strap 3
        "884-883",  # right strap 2
        "883-879",  # right strap 1
    ]

    top_cheek_keys = [
        "879-600",  # top right cheek 7
        "600-756",  # top right cheek 6
        "756-862",  # top right cheek 5
        "862-753",  # top right cheek 4
        "753-594",  # top right cheek 3
        "594-582",  # top right cheek 2
        "582-609",  # top right cheek 1
        "451-151",  # top left cheek 7
        "151-321",  # top left cheek 6
        "321-434",  # top left cheek 5
        "434-318",  # top left cheek 4
        "318-145",  # top left cheek 3
        "145-133",  # top left cheek 2
        "133-160",  # top left cheek 1
    ]

    mid_cheek_keys = [
        "509-893",  # mid right cheek 5
        "893-894",  # mid right cheek 4
        "894-881",  # mid right cheek 3
        "881-880",  # mid right cheek 2
        "880-879",  # mid right cheek 1
        "60-478",   # mid left cheek 5
        "478-479",  # mid left cheek 4
        "479-453",  # mid left cheek 3
        "453-452",  # mid left cheek 2
        "452-451",  # mid left cheek 1
    ]

    chin_keys = [
        "1049-983", # chin right 7
        "983-982",  # chin right 6
        "982-1050", # chin right 5
        "1050-1051", # chin right 4
        "1051-1052", # chin right 3
        "1052-1053", # chin right 2
        "1053-509", # chin right 1
        "1049-984", # chin left 7
        "984-985",  # chin left 6
        "985-986",  # chin left 5
        "986-987",  # chin left 4
        "987-988",  # chin left 3
        "988-989",  # chin left 2
        "989-60",   # chin left 1
    ]

    def sum_keys(keys: list, data: Dict[str, Any], section_name: str) -> float:
        """Sum values for given keys, warning about missing keys."""
        total = 0.0
        missing = []
        found = []

        def extract_value(value: Any) -> float:
            """Extract numeric value from various formats."""
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, dict):
                # Handle dict format: {'value': 3.82, 'description': '...'}
                if 'value' in value:
                    val = value['value']
                    if isinstance(val, (int, float)):
                        return float(val)
            return None

        for key in keys:
            # Try string key first
            if key in data:
                value = extract_value(data[key])
                if value is not None:
                    total += value
                    found.append(key)
                else:
                    print(f"Warning: Key '{key}' in {section_name} has non-numeric value: {data[key]}")
            else:
                # Try integer tuple key (e.g., (160, 371) instead of "160-371")
                try:
                    parts = key.split("-")
                    if len(parts) == 2:
                        tuple_key = (int(parts[0]), int(parts[1]))
                        if tuple_key in data:
                            value = extract_value(data[tuple_key])
                            if value is not None:
                                total += value
                                found.append(key)
                                continue
                except (ValueError, TypeError):
                    pass

                missing.append(key)

        if missing and len(found) == 0:
            # Only warn if we found nothing - might indicate wrong structure
            print(f"Warning: Missing {len(missing)} keys in {section_name}: {missing[:5]}{'...' if len(missing) > 5 else ''}")
        elif missing:
            # Some found, some missing - less critical
            pass

        return total

    return {
        'nose': sum_keys(nose_keys, measurements_dict, 'nose'),
        'strap': sum_keys(strap_keys, measurements_dict, 'strap'),
        'top_cheek': sum_keys(top_cheek_keys, measurements_dict, 'top_cheek'),
        'mid_cheek': sum_keys(mid_cheek_keys, measurements_dict, 'mid_cheek'),
        'chin': sum_keys(chin_keys, measurements_dict, 'chin'),
    }


def load_facial_measurements(input_dir: str):
    """
    Load all .txt files from the input directory and parse them as JSON.

    Args:
        input_dir: Path to directory containing .txt files with JSON data

    Returns:
        List of dictionaries containing parsed JSON data from each file
    """
    input_path = Path(input_dir).expanduser()

    if not input_path.exists():
        raise FileNotFoundError(f"Directory not found: {input_dir}")

    if not input_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {input_dir}")

    txt_files = sorted(input_path.glob("*.txt"))

    if not txt_files:
        print(f"Warning: No .txt files found in {input_dir}")
        return []

    measurements = []
    for txt_file in txt_files:
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                measurements.append({
                    'filename': txt_file.name,
                    'filepath': str(txt_file),
                    'data': data
                })
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse JSON from {txt_file.name}: {e}")
        except Exception as e:
            print(f"Warning: Error reading {txt_file.name}: {e}")

    return measurements


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Load and preprocess ARKit facial measurements from .txt files"
    )
    parser.add_argument(
        "--input_facial_measurements_dir",
        type=str,
        required=True,
        help="Directory containing .txt files with JSON-formatted facial measurements "
             "(e.g., ~/Downloads/facial_measurements)"
    )

    args = parser.parse_args()

    measurements = load_facial_measurements(args.input_facial_measurements_dir)

    print(f"Loaded {len(measurements)} measurement file(s)")

    # Process each file and store aggregated measurements
    aggregated_measurements = []
    for measurement in measurements:
        filename = measurement['filename']
        data = measurement['data']

        # Summarize measurements for this file
        summary = summarize_measurements(data)

        aggregated_measurements.append({
            'filename': filename,
            'filepath': measurement['filepath'],
            'aggregated': summary
        })

        print(f"\n{filename}:")
        for section, value in summary.items():
            print(f"  {section}: {value:.6f}")

    print(f"\n\nProcessed {len(aggregated_measurements)} file(s) with aggregated measurements")


