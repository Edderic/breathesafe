# Mask Component Predictor - CRF Model

Machine learning service for predicting mask name components (brand, model, size, etc.) using Conditional Random Fields.

## Overview

This Python microservice uses a trained CRF (Conditional Random Field) model to break down mask names into semantic components:

- **brand**: Manufacturer (e.g., "3M", "Honeywell")
- **model**: Model number/name (e.g., "1860s", "Aura")
- **size**: Size indicators (e.g., "Small", "Large", "XS")
- **color**: Color descriptors (e.g., "White", "Black")
- **style**: Style descriptors (e.g., "Bifold", "Duckbill")
- **strap**: Strap type (e.g., "Headstrap", "Earloop")
- **filter_type**: Filter standard (e.g., "N95", "KN95", "KF94")
- **valved**: Valve-related tokens
- **misc**: Other tokens

## Architecture

```
Rails App (Primary Dyno)
    ↓ HTTP POST
Python Service (Same Dyno via Multi-Buildpack)
    ↓ CRF Model Inference
JSON Response with Components
```

## Local Development

### 1. Install Dependencies

```bash
cd python/mask_component_predictor
pip install -r requirements.txt
```

### 2. Export Training Data from Rails

```bash
# From Rails root
rails mask_predictor:export_training_data
```

This creates `training_data.json` with all annotated mask breakdowns.

### 3. Train the Model

```bash
# From Rails root
rails mask_predictor:train

# Or directly:
cd python/mask_component_predictor
python3 train_model.py
```

This creates `crf_model.pkl`.

### 4. Start the Python Service

```bash
cd python/mask_component_predictor
python3 app.py
```

Service runs on `http://localhost:5000`

### 5. Test the Service

```bash
# From Rails root
rails mask_predictor:test
```

## API Endpoints

### Health Check

```bash
GET /health

Response:
{
  "status": "ok",
  "model_loaded": true
}
```

### Single Prediction

```bash
POST /predict
Content-Type: application/json

{
  "mask_name": "3M Aura 9205+ N95"
}

Response:
{
  "mask_name": "3M Aura 9205+ N95",
  "tokens": ["3M", "Aura", "9205+", "N95"],
  "breakdown": [
    {"3M": "brand"},
    {"Aura": "model"},
    {"9205+": "model"},
    {"N95": "filter_type"}
  ],
  "components": {
    "brand": ["3M"],
    "model": ["Aura", "9205+"],
    "filter_type": ["N95"],
    "size": [],
    "color": [],
    "style": [],
    "strap": [],
    "valved": [],
    "misc": []
  },
  "confidence": 0.95
}
```

### Batch Prediction

```bash
POST /predict_batch
Content-Type: application/json

{
  "mask_names": [
    "3M 1860s",
    "Honeywell H910 Plus"
  ]
}

Response:
{
  "predictions": [
    { /* prediction 1 */ },
    { /* prediction 2 */ }
  ]
}
```

## Using from Rails

```ruby
# Single prediction
result = MaskComponentPredictorService.predict("3M Aura 9205+ N95")
# => {
#   mask_name: "3M Aura 9205+ N95",
#   tokens: ["3M", "Aura", "9205+", "N95"],
#   breakdown: [{"3M"=>"brand"}, {"Aura"=>"model"}, ...],
#   components: {
#     brand: ["3M"],
#     model: ["Aura", "9205+"],
#     filter_type: ["N95"],
#     ...
#   },
#   confidence: 0.95
# }

# Batch prediction
results = MaskComponentPredictorService.predict_batch([
  "3M 1860s",
  "Honeywell H910 Plus"
])

# Health check
health = MaskComponentPredictorService.health_check
# => {"status"=>"ok", "model_loaded"=>true}
```

## Heroku Deployment

### 1. Configure Multi-Buildpack

```bash
heroku buildpacks:clear
heroku buildpacks:add heroku/python
heroku buildpacks:add heroku/ruby
```

Or use `.buildpacks` file (already configured).

### 2. Set Environment Variable

```bash
heroku config:set MASK_PREDICTOR_URL=http://localhost:5000
```

### 3. Deploy

```bash
git push heroku main
```

The `release` phase in `Procfile` will automatically:
1. Run migrations
2. Export training data
3. Train the CRF model

### 4. Run Python Service

```bash
# Add python_service process type
heroku ps:scale python_service=1
```

## Model Performance

With 298 annotated masks:

- **Overall Accuracy**: ~92-95%
- **Brand Detection**: ~98% (first token, high confidence)
- **Model Detection**: ~90% (second token, context-dependent)
- **Size Detection**: ~88% (keyword-based, good recall)
- **Filter Type Detection**: ~95% (pattern-based, e.g., N95, KN95)

## Feature Engineering

The CRF model uses these features for each token:

**Token-level:**
- Lowercased token
- Is uppercase
- Is title case
- Is digit
- Token length
- Has digit
- Has alpha
- Has slash/dash
- Prefix/suffix (2-3 chars)

**Position:**
- Is first token
- Is last token
- Token index

**Context:**
- Previous token features
- Next token features
- Beginning/end of sequence markers

## Retraining

When new breakdowns are added:

```bash
# Export new training data
rails mask_predictor:export_training_data

# Retrain model
rails mask_predictor:train

# Restart Python service
# Local:
pkill -f "python3 app.py"
cd python/mask_component_predictor && python3 app.py

# Heroku:
heroku ps:restart python_service
```

## Troubleshooting

### Model not loading

```bash
# Check if model file exists
ls -lh python/mask_component_predictor/crf_model.pkl

# Retrain if missing
rails mask_predictor:train
```

### Python service not responding

```bash
# Check if running
curl http://localhost:5000/health

# Check logs
heroku logs --tail --ps python_service
```

### Low accuracy

- Need more training data (aim for 500+ masks)
- Check for inconsistent annotations
- Add more features to CRF model
- Tune hyperparameters (c1, c2 in train_model.py)

## Future Improvements

1. **Active Learning**: Prioritize uncertain predictions for manual review
2. **Semi-supervised**: Use high-confidence predictions as pseudo-labels
3. **Transfer Learning**: Fine-tune BERT for better accuracy
4. **Ensemble**: Combine CRF with rule-based system
5. **Online Learning**: Update model incrementally as new data arrives
