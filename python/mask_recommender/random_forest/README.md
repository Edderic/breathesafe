# Random Forest Mask Recommender (Lambda)

This mirrors the PyTorch Lambda interface but uses a scikit-learn RandomForest.

## Handler

- Training: `method: "train"`, returns metrics and artifact paths
- Inference: `method: "infer"`, returns `{ mask_id: {...}, proba_fit: {...}, threshold }`

## Build and Run Locally

```bash
# Build image
docker build -t breathesafe-rf -f python/mask_recommender/random_forest/Dockerfile .

# Run locally
docker run --rm -p 9001:8080 breathesafe-rf

# Invoke
curl -s -H 'Content-Type: application/json' \
  -d '{"method":"infer","facial_measurements":{"face_width":140,"face_length":120}}' \
  http://localhost:9001/2015-03-31/functions/function/invocations | jq .
```
