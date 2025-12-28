# AWS Lambda Mask Component Predictor

Serverless mask component prediction using AWS Lambda and CRF model.

## Overview

This Lambda function provides a cost-effective, auto-scaling API for predicting mask name components (brand, model, size, etc.) using a trained Conditional Random Fields (CRF) model.

### Benefits vs Heroku

- **99% cost savings**: $0.01/month vs $7-25/month
- **Auto-scaling**: Handles traffic spikes automatically
- **No deployment complexity**: No multi-buildpack issues
- **Faster Rails deployments**: No Python dependencies in Rails

## Quick Start

### Prerequisites

1. **AWS CLI** installed and configured:
   ```bash
   brew install awscli
   aws configure
   ```

2. **AWS Credentials** with Lambda permissions:
   - `lambda:CreateFunction`
   - `lambda:UpdateFunctionCode`
   - `lambda:InvokeFunction`
   - `iam:CreateRole`
   - `iam:AttachRolePolicy`

3. **Trained CRF model**:
   ```bash
   cd ../../
   PORT=1234 rails mask_predictor:train
   ```

### Deploy to AWS Lambda

```bash
cd lambda/mask_predictor

# Use 'breathesafe' profile (default)
./deploy.sh

# Or specify a different profile
./deploy.sh --profile myprofile

# Or use default AWS profile
./deploy.sh --profile default

# Deploy to a different region
./deploy.sh --profile breathesafe --region us-west-2
```

This script will:
1. ✅ Check AWS CLI configuration for specified profile
2. ✅ Train model if not exists
3. ✅ Install Python dependencies
4. ✅ Create deployment package (~15MB)
5. ✅ Create IAM role
6. ✅ Deploy Lambda function
7. ✅ Test the deployment

### Configure Rails

```bash
# On Heroku
heroku config:set USE_LAMBDA_PREDICTOR=true
heroku config:set AWS_REGION=us-east-1
heroku config:set LAMBDA_FUNCTION_NAME=mask-component-predictor
heroku config:set AWS_ACCESS_KEY_ID=your_key
heroku config:set AWS_SECRET_ACCESS_KEY=your_secret

# Or in .env for local development
USE_LAMBDA_PREDICTOR=true
AWS_REGION=us-east-1
LAMBDA_FUNCTION_NAME=mask-component-predictor
```

### Test from Rails

```bash
rails console

# Health check
> MaskComponentPredictorService.health_check
# => {"status"=>"ok", "function_name"=>"mask-component-predictor", ...}

# Single prediction
> result = MaskComponentPredictorService.predict("3M Aura 9205+ N95")
> result[:components][:brand]
# => ["3M"]

# Batch prediction
> results = MaskComponentPredictorService.predict_batch([
    "3M 1860s",
    "Honeywell H910 Plus"
  ])
```

## Architecture

```
┌─────────────────┐
│   Rails App     │
│   (Heroku)      │
└────────┬────────┘
         │ HTTP POST (aws-sdk-lambda)
         ▼
┌─────────────────┐
│  AWS Lambda     │
│  Python 3.11    │
│  512MB / 30s    │
└────────┬────────┘
         │ Load model (cached)
         ▼
┌─────────────────┐
│  CRF Model      │
│  139KB pickle   │
│  87.7% accuracy │
└─────────────────┘
```

## Lambda Function Details

### Handler

**File**: `lambda_function.py`
**Handler**: `lambda_function.lambda_handler`
**Runtime**: Python 3.11
**Memory**: 512MB
**Timeout**: 30 seconds

### Input Format

**Single prediction:**
```json
{
  "mask_name": "3M Aura 9205+ N95"
}
```

**Batch prediction:**
```json
{
  "mask_names": [
    "3M 1860s",
    "Honeywell H910 Plus",
    "Zimi ZM9233 w/ Headstraps"
  ]
}
```

### Output Format

```json
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

## Performance

### Cold Start
- **First invocation**: ~1-2 seconds (model loading)
- **Subsequent invocations**: ~10-50ms (model cached)

### Warm Invocations
- **Single prediction**: ~10-50ms
- **Batch prediction (10 masks)**: ~50-100ms

### Cost Estimate

**10,000 predictions/month:**
- Requests: 10,000 × $0.20/1M = **$0.002**
- Compute: 10,000 × 0.1s × 0.5GB × $0.0000166667 = **$0.008**
- **Total: ~$0.01/month**

**100,000 predictions/month:**
- **Total: ~$0.10/month**

Compare to Heroku dyno: **$7-25/month**

## Deployment

### Manual Deployment

```bash
cd lambda/mask_predictor
./deploy.sh
```

### Update Function Code Only

```bash
aws lambda update-function-code \
  --function-name mask-component-predictor \
  --zip-file fileb://deployment.zip \
  --region us-east-1
```

### Update Model Only

```bash
# 1. Train new model
cd ../../
rails mask_predictor:train

# 2. Copy to Lambda directory
cp python/mask_component_predictor/crf_model.pkl lambda/mask_predictor/

# 3. Redeploy
cd lambda/mask_predictor
./deploy.sh
```

## Monitoring

### View Logs

```bash
# Recent logs
aws logs tail /aws/lambda/mask-component-predictor --follow

# Filter errors
aws logs tail /aws/lambda/mask-component-predictor --filter-pattern "ERROR"
```

### View Metrics

```bash
# Invocations
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=mask-component-predictor \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum

# Duration
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=mask-component-predictor \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Average
```

### Test Invocation

```bash
aws lambda invoke \
  --function-name mask-component-predictor \
  --payload '{"mask_name":"3M Aura 9205+ N95"}' \
  --region us-east-1 \
  response.json

cat response.json | jq
```

## Troubleshooting

### Error: "Unable to import module 'lambda_function'"

**Cause**: Dependencies not included in deployment package.

**Solution**: Redeploy with `./deploy.sh`

### Error: "Task timed out after 30.00 seconds"

**Cause**: Model loading takes too long (cold start).

**Solution**: Increase timeout:
```bash
aws lambda update-function-configuration \
  --function-name mask-component-predictor \
  --timeout 60
```

### Error: "Memory Size: 512 MB Max Memory Used: 600 MB"

**Cause**: Not enough memory.

**Solution**: Increase memory:
```bash
aws lambda update-function-configuration \
  --function-name mask-component-predictor \
  --memory-size 1024
```

### Rails can't connect to Lambda

**Cause**: Missing AWS credentials or wrong region.

**Solution**: Check environment variables:
```bash
heroku config:get AWS_REGION
heroku config:get AWS_ACCESS_KEY_ID
heroku config:get LAMBDA_FUNCTION_NAME
```

## Advanced Configuration

### Function URL (Public HTTP Endpoint)

Create a public URL for the Lambda function:

```bash
aws lambda create-function-url-config \
  --function-name mask-component-predictor \
  --auth-type NONE \
  --region us-east-1
```

Then use HTTP instead of AWS SDK:
```ruby
# In Rails
response = HTTParty.post(
  'https://abc123.lambda-url.us-east-1.on.aws/',
  body: { mask_name: "3M Aura 9205+ N95" }.to_json,
  headers: { 'Content-Type' => 'application/json' }
)
```

### Keep Lambda Warm

Prevent cold starts with periodic pings:

```bash
# CloudWatch Events rule (every 5 minutes)
aws events put-rule \
  --name keep-mask-predictor-warm \
  --schedule-expression "rate(5 minutes)"

aws events put-targets \
  --rule keep-mask-predictor-warm \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:123456789:function:mask-component-predictor"
```

### VPC Configuration

If you need to access private resources:

```bash
aws lambda update-function-configuration \
  --function-name mask-component-predictor \
  --vpc-config SubnetIds=subnet-123,SecurityGroupIds=sg-123
```

## Cost Optimization

### Tips

1. **Use batch predictions**: 10 masks in 1 request vs 10 requests
2. **Cache results**: Store predictions in Rails cache
3. **Increase memory**: More memory = faster execution = lower cost
4. **Keep warm**: Prevent cold starts with periodic pings

### Example: Caching in Rails

```ruby
# Cache predictions for 1 day
Rails.cache.fetch("mask_components:#{mask.id}", expires_in: 1.day) do
  MaskComponentPredictorService.predict(mask.unique_internal_model_code)
end
```

## Next Steps

1. ✅ Deploy Lambda function
2. ✅ Configure Rails to use Lambda
3. ✅ Test predictions
4. 🔲 Integrate into bulk import flow
5. 🔲 Build deduplication UI
6. 🔲 Add caching layer
7. 🔲 Set up CloudWatch alarms

---

**Questions?** Check the main [AWS_LAMBDA_COMPARISON.md](../../AWS_LAMBDA_COMPARISON.md) for more details.
