# Mask Component Predictor - Quick Start Guide

> **⚠️ macOS Port Conflict:** Port 5000 is used by AirPlay Receiver on macOS.
> **Recommended:** Use port 1234 instead. See [PORT_CONFLICT.md](PORT_CONFLICT.md) for details.

## Starting the Service

### Recommended Port (1234)
```bash
cd python/mask_component_predictor
python3 app.py 1234
```

### Default Port (5000)
```bash
python3 app.py
# Note: May conflict with AirPlay Receiver on macOS
```

### Custom Port (Environment Variable)
```bash
PORT=8888 python3 app.py
```

## Testing from Rails

### Default Port
```bash
rails mask_predictor:test
```

### Custom Port
```bash
PORT=1234 rails mask_predictor:test
```

## Using in Rails Code

### Configure Service URL

```ruby
# Option 1: Set full URL (production)
ENV['MASK_PREDICTOR_URL'] = 'http://localhost:5000'

# Option 2: Set port only (development)
ENV['MASK_PREDICTOR_PORT'] = '1234'
```

### Make Predictions

```ruby
# Single prediction
result = MaskComponentPredictorService.predict("3M Aura 9205+ N95")
# => {
#   mask_name: "3M Aura 9205+ N95",
#   tokens: ["3M", "Aura", "9205+", "N95"],
#   breakdown: [
#     {"3M" => "brand"},
#     {"Aura" => "model"},
#     {"9205+" => "model"},
#     {"N95" => "filter_type"}
#   ],
#   components: {
#     brand: ["3M"],
#     model: ["Aura", "9205+"],
#     filter_type: ["N95"],
#     size: [],
#     color: [],
#     style: [],
#     strap: [],
#     valved: [],
#     misc: []
#   },
#   confidence: 0.95
# }

# Batch prediction
results = MaskComponentPredictorService.predict_batch([
  "3M 1860s",
  "Honeywell H910 Plus",
  "Zimi ZM9233 w/ Headstraps"
])

# Health check
health = MaskComponentPredictorService.health_check
# => {"status" => "ok", "model_loaded" => true}
```

## Retraining the Model

When mask breakdowns are updated:

```bash
# Export latest training data and retrain
rails mask_predictor:train
```

This will:
1. Export all annotated mask breakdowns to `training_data.json`
2. Train a new CRF model
3. Save to `crf_model.pkl`

## Troubleshooting

### Port Already in Use

If you see "Address already in use" error:

```bash
# On macOS, disable AirPlay Receiver in System Settings
# Or use a different port:
python3 app.py 8888
```

### Model Not Found

```bash
# Train the model first
rails mask_predictor:train
```

### Service Not Running

```bash
# Check if service is running
curl http://localhost:5000/health

# If not, start it
cd python/mask_component_predictor
python3 app.py
```

### Connection Refused from Rails

Make sure:
1. Python service is running
2. Port matches in both Rails and Python
3. Environment variables are set correctly

```bash
# Check Rails configuration
rails console
> MaskComponentPredictorService::PYTHON_SERVICE_URL
# => "http://localhost:5000"

# Test connection
> MaskComponentPredictorService.health_check
```

## Performance Tips

### Batch Predictions
Use `predict_batch` for multiple masks to reduce HTTP overhead:

```ruby
# ❌ Slow - multiple HTTP requests
masks.each do |mask|
  MaskComponentPredictorService.predict(mask.unique_internal_model_code)
end

# ✅ Fast - single HTTP request
mask_names = masks.map(&:unique_internal_model_code)
results = MaskComponentPredictorService.predict_batch(mask_names)
```

### Caching
Consider caching predictions for frequently accessed masks:

```ruby
Rails.cache.fetch("mask_components:#{mask.id}", expires_in: 1.day) do
  MaskComponentPredictorService.predict(mask.unique_internal_model_code)
end
```

## Model Performance

- **Overall Accuracy**: 87.7%
- **Brand Detection**: 93.8% precision (excellent for deduplication!)
- **Filter Type**: 91.4% precision
- **Size**: 96.9% precision
- **Training Data**: 296 annotated masks

See `README.md` for detailed performance metrics.
