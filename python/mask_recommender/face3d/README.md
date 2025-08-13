3DDFA-V2 Face to PLY

This module wraps 3DDFA-V2 to convert an input image to a dense 3D face mesh and export as .ply.

Install:

- pip install -r python/mask_recommender/face3d/requirements.txt
- pip install 3ddfa-v2
- Download ONNX configs/weights as per 3DDFA-V2 instructions.

Usage:

```
python -m python.mask_recommender.face3d.extractor_3ddfa --image /path/to/face.jpg --out /tmp/face.ply
```
