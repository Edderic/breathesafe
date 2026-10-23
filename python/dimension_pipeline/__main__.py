"""Run a tiny geometry-contract smoke experiment with no third-party packages."""

import argparse
import json
from pathlib import Path

from .geometry import measure_reference


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path, nargs="?",
                        default=Path(__file__).parent / "fixtures" / "base_mm.json")
    args = parser.parse_args()
    try:
        result = measure_reference(json.loads(args.reference.read_text()))
    except (ValueError, OSError) as error:
        parser.exit(1, f"Invalid reference: {error}\n")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
