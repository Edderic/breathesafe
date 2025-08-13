from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

try:
    # 3DDFA-V2 provides a convenient API when installed
    # pip install 3ddfa-v2
    from FaceBoxes import FaceBoxes
    from TDDFA_ONNX import TDDFA_ONNX
except Exception:
    FaceBoxes = None
    TDDFA_ONNX = None


class FaceToPLYExtractor:
    """
    Wrapper around 3DDFA-V2 (ONNX) to detect a face and export fitted mesh as .ply.

    Note: This assumes 3ddfa-v2 is installed and ONNX models are available.
    See: https://github.com/cleardusk/3DDFA_V2
    """

    def __init__(self, onnx_config: Optional[str] = None):
        if TDDFA_ONNX is None:
            raise RuntimeError("3DDFA-V2 not available. Please install 3ddfa-v2.")
        if onnx_config is None or not os.path.exists(onnx_config):
            raise RuntimeError(
                "Please provide --onnx_config pointing to a valid 3DDFA-V2 ONNX config YAML."
            )
        self.tddfa = TDDFA_ONNX(onnx_config)
        self.face_boxes = FaceBoxes()

    def image_to_ply(self, image_path: str, out_ply: str) -> str:
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Could not read image: {image_path}")

        boxes = self.face_boxes(img)
        if len(boxes) == 0:
            raise RuntimeError("No face detected")

        # take the largest face
        boxes = sorted(boxes, key=lambda b: (b[2]-b[0])*(b[3]-b[1]), reverse=True)
        param_lst, roi_box_lst = self.tddfa(img, boxes)
        vertices = self.tddfa.recon_vers(param_lst, roi_box_lst, dense_flag=True)[0]

        # vertices: (3, N), convert to (N, 3)
        verts = vertices.T

        # faces (triangles) from 3ddfa template
        tri = self.tddfa.tri

        self._write_ply(out_ply, verts, tri)
        return out_ply

    @staticmethod
    def _write_ply(path: str, vertices: np.ndarray, triangles: np.ndarray) -> None:
        Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write("ply\n")
            f.write("format ascii 1.0\n")
            f.write(f"element vertex {vertices.shape[0]}\n")
            f.write("property float x\n")
            f.write("property float y\n")
            f.write("property float z\n")
            f.write(f"element face {triangles.shape[0]}\n")
            f.write("property list uchar int vertex_indices\n")
            f.write("end_header\n")
            for v in vertices:
                f.write(f"{v[0]} {v[1]} {v[2]}\n")
            for t in triangles:
                f.write(f"3 {t[0]} {t[1]} {t[2]}\n")


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--onnx_config", default=None)
    args = parser.parse_args()

    extractor = FaceToPLYExtractor(args.onnx_config)
    out_path = extractor.image_to_ply(args.image, args.out)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    cli()
