# Mask Component Predictor - Quick Start

## 🚀 Get Started in 5 Minutes

### 1. Train the Model

```bash
rails mask_predictor:train
```

### 2. Test It

```bash
rails mask_predictor:test
```

### 3. Use It

```ruby
result = MaskComponentPredictorService.predict('3M Aura 9205+ N95')
puts result[:components][:brand]  # => ["3M"]
puts result[:components][:model]  # => ["Aura", "9205+"]
```

## 📊 Example Output

```ruby
{
  mask_name: "3M Aura 9205+ N95",
  tokens: ["3M", "Aura", "9205+", "N95"],
  breakdown: [
    {"3M" => "brand"},
    {"Aura" => "model"},
    {"9205+" => "model"},
    {"N95" => "filter_type"}
  ],
  components: {
    brand: ["3M"],
    model: ["Aura", "9205+"],
    filter_type: ["N95"],
    size: [], color: [], style: [], strap: [], valved: [], misc: []
  },
  confidence: 0.9677
}
```

## 🎯 Common Use Cases

### Single Prediction

```ruby
result = MaskComponentPredictorService.predict('Honeywell H910 Plus')
```

### Batch Prediction

```ruby
results = MaskComponentPredictorService.predict_batch([
  '3M 1860s',
  'Zimi ZM9233 w/ Headstraps',
  'BreatheTeq - Large'
])
```

### Health Check

```ruby
health = MaskComponentPredictorService.health_check
# => { "status" => "ok", "model_loaded" => true, "type" => "inline" }
```

## 🚢 Deploy to Heroku

```bash
# Commit the model
git add python/mask_component_predictor/crf_model.pkl
git commit -m "Add pre-trained CRF model"
git push heroku main
```

**That's it!** No extra configuration needed. Cost: $0/month.

## 🔧 Configuration (Optional)

### Use Flask Service (Faster)

```bash
# Terminal 1: Start Flask
cd python/mask_component_predictor
python3 app.py 1234

# Terminal 2: Configure Rails
export USE_FLASK_PREDICTOR=true
export MASK_PREDICTOR_PORT=1234
rails server
```

### Use AWS Lambda (Future)

```bash
export USE_LAMBDA_PREDICTOR=true
export AWS_REGION=us-east-1
export LAMBDA_FUNCTION_NAME=mask-component-predictor
```

## 📈 Performance

| Mode | Speed | Cost | Setup |
|------|-------|------|-------|
| **Inline (default)** | 50ms | $0 | ✅ None |
| Flask | 20ms | $7-25/mo | Start service |
| Lambda | 10ms | $0.01/mo | Deploy function |

## 🐛 Troubleshooting

**Model not found?**
```bash
rails mask_predictor:train
```

**Dependencies missing?**
```bash
pip3 install -r python/mask_component_predictor/requirements.txt
```

**Port conflict?**
```bash
python3 app.py 1234  # Use different port
```

## 📚 Full Documentation

See [MASK_PREDICTOR_SETUP.md](MASK_PREDICTOR_SETUP.md) for complete details.

## ✅ Status

- ✅ Model trained (87.7% accuracy)
- ✅ Inline Python integration
- ✅ Ready for production
- 🔄 Bulk import integration (next)
- 🔄 Deduplication UI (next)
