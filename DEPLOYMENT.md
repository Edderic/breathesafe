# Deployment Guide

## Environment-Specific Version-Based Deployment

The Lambda functions and model retraining are now deployed using environment-specific version tags. This ensures controlled, versioned deployments to staging and production environments with clear separation.

### Weekly Automatic Retraining

**Schedule**: Every Saturday at 12:00 AM Eastern Time (5:00 AM UTC)

Both staging and production models are automatically retrained weekly with:
- **Staging**: Separate model for staging environment
- **Production**: Separate model for production environment
- **Lambda Updates**: Both environments automatically deploy updated Lambda functions with new models
- **Notifications**: Email notifications for success/failure

### Manual Version-Based Deployment

#### Staging Environment
1. **Create a staging version tag** when you want to deploy to staging:
   ```bash
   git tag staging-recommender-v0.1.2
   git push origin staging-recommender-v0.1.2
   ```

#### Production Environment
1. **Create a production version tag** when you want to deploy to production:
   ```bash
   git tag production-recommender-v0.1.2
   git push origin production-recommender-v0.1.2
   ```

### Version Tag Format

- **Staging**: Use `staging-recommender-v*` format (e.g., `staging-recommender-v0.1.2`, `staging-recommender-v1.0.0`)
- **Production**: Use `production-recommender-v*` format (e.g., `production-recommender-v0.1.2`, `production-recommender-v1.0.0`)

### What Gets Deployed

#### Weekly Automatic Retraining (Saturday 12:00 AM ET)
- **Staging**: 
  - Model retraining and upload to staging S3 bucket
  - Lambda function update with new model
- **Production**: 
  - Model retraining and upload to production S3 bucket
  - Lambda function update with new model

#### Manual Version-Based Deployment
- **Staging Environment (staging-recommender-v* tags)**
  - **Inference Lambda**: `mask-recommender-inference-staging`
  - **Model Retraining**: Uploads model artifacts to staging S3 bucket
  - **Trigger**: Any changes in `python/mask_recommender/inference/**` or `python/mask_recommender/training/**`

- **Production Environment (production-recommender-v* tags)**
  - **Inference Lambda**: `mask-recommender-inference`
  - **Model Retraining**: Uploads model artifacts to production S3 bucket
  - **Trigger**: Any changes in `python/mask_recommender/inference/**` or `python/mask_recommender/training/**`

### Workflow Files

- `.github/workflows/deploy-inference-lambda-staging.yml` - Staging Lambda deployment (triggers on `staging-recommender-v*`)
- `.github/workflows/deploy-inference-lambda-production.yml` - Production Lambda deployment (triggers on `production-recommender-v*`)
- `.github/workflows/retrain-model-staging.yml` - Staging model retraining (weekly + `staging-recommender-v*`)
- `.github/workflows/retrain-model-production.yml` - Production model retraining (weekly + `production-recommender-v*`)

### Notifications

All deployments send email notifications with:
- Success/failure status
- Trigger type (Weekly Auto-Retrain or Version Tag)
- Deployment details

### Example Deployments

#### Deploy to Staging Only
```bash
# Make your changes
git add .
git commit -m "Update inference logic for testing"

# Create and push staging version tag
git tag staging-recommender-v0.1.3
git push origin staging-recommender-v0.1.3
```

#### Deploy to Production Only
```bash
# Make your changes
git add .
git commit -m "Update inference logic for production"

# Create and push production version tag
git tag production-recommender-v0.1.3
git push origin production-recommender-v0.1.3
```

#### Deploy to Both Environments
```bash
# Make your changes
git add .
git commit -m "Update inference logic"

# Deploy to staging first
git tag staging-recommender-v0.1.3
git push origin staging-recommender-v0.1.3

# After testing, deploy to production
git tag production-recommender-v0.1.3
git push origin production-recommender-v0.1.3
```

### Benefits

- **Automatic Updates**: Models are retrained weekly with fresh data
- **Manual Control**: Version tags allow immediate deployments when needed
- **Clear separation**: Staging and production deployments are completely independent
- **Controlled releases**: You can test in staging before deploying to production
- **Version tracking**: Each environment has its own version history
- **Rollback capability**: Easy to revert to previous versions in each environment 