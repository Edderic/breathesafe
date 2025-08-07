# Mask Recommender Inference Lambda

This directory contains the AWS Lambda function for mask recommendation inference.

## Architecture

The inference Lambda function:
1. Loads PyMC traces from S3
2. Scales facial features using the same scaler from training
3. Predicts fit probabilities for each mask
4. Returns sorted recommendations

## Files

- `lambda_function.py` - Main Lambda handler
- `Dockerfile` - Container definition for Lambda
- `requirements.txt` - Python dependencies
- `environment.yml` - Conda environment for development
- `tests/` - Test suite

## Deployment

### Automatic Deployment (Recommended)

The inference Lambda is automatically deployed when you push a version tag:

```bash
# Make changes to inference code
git add .
git commit -m "Update inference logic"
git tag v1.0.1
git push origin v1.0.1
```

This triggers the GitHub workflow that:
1. Builds the Docker image
2. Pushes to Amazon ECR
3. Updates the Lambda function
4. Sends email notification

### Manual Deployment

```bash
# Build and push to ECR
docker build -t mask-recommender-inference .
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
docker tag mask-recommender-inference:latest $AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/mask-recommender-inference:latest
docker push $AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/mask-recommender-inference:latest

# Update Lambda
aws lambda update-function-code \
  --function-name mask-recommender-inference \
  --image-uri $AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/mask-recommender-inference:latest
```

## Testing

Run tests locally:

```bash
# Activate environment
mamba activate mask-recommender-inference

# Run tests
pytest tests/ -v
```

## Required AWS Resources

1. **S3 Bucket**: `breathesafe-models` (or configure via `S3_BUCKET` environment variable)
   - Contains model artifacts: `pymc_trace_latest.nc`, `mask_data_latest.json`, `scaler_latest.json`

2. **ECR Repository**: `mask-recommender-inference`
   - Stores Docker images for Lambda

3. **Lambda Function**: `mask-recommender-inference`
   - Executes inference code
   - Configured with appropriate IAM roles and environment variables

## Environment Variables

The Lambda function expects these environment variables:
- `S3_BUCKET`: S3 bucket containing model artifacts (default: `breathesafe-models`)

## GitHub Secrets

Configure these secrets in your GitHub repository:

- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_REGION`: AWS region (default: us-east-1)
- `EMAIL_USERNAME`: Gmail username for notifications
- `EMAIL_PASSWORD`: Gmail app password for notifications
- `NOTIFICATION_EMAIL`: Email address for deployment notifications

## Model Updates

The inference Lambda automatically uses the latest model artifacts from S3. To update the model:

1. **Automatic**: The training workflow uploads new artifacts to S3
2. **Manual**: Upload new artifacts to S3:
   ```bash
   aws s3 cp pymc_trace.nc s3://breathesafe-models/models/pymc_trace_latest.nc
   aws s3 cp mask_data.json s3://breathesafe-models/models/mask_data_latest.json
   aws s3 cp scaler.json s3://breathesafe-models/models/scaler_latest.json
   ```

The Lambda function will automatically load the new model on the next invocation.