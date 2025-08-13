Usage

1) Install requirements (suggest a venv):

```
pip install -r python/mask_recommender/pytorch/requirements.txt
```

2) Prepare a CSV with columns like:
- face_width, face_length, nose_protrusion, bitragion_subnasale_arc, facial_hair_beard_length_mm, lip_width, perimeter_mm
- headstrap, adjustable_headstrap, earloops, adjustable_earloops, boat, duckbill, cup, bifold, bifold+gasket
- mask_id_1, mask_id_2, ... (optional one-hots)
- target (0=too small, 1=ok, 2=too big)

3) Train:

```
python -m python.mask_recommender.pytorch.train --csv /path/to/data.csv --epochs 50 --save fit_classifier.pt
```

4) Inference on features-only CSV (no target column required):

```
python -m python.mask_recommender.pytorch.infer --model fit_classifier.pt --csv /path/to/features.csv --out preds.json
```
