# Deployment Guide

## Development Branch Deployment Pipeline

The main deployment pipeline automatically deploys from the `development` branch to staging and production environments.

### Pipeline Overview

1. **Test Phase** (required for all PRs and development pushes):
   - RuboCop (Ruby linting)
   - RSpec (Ruby tests)
   - Python inference tests
   - Python training tests

2. **Staging Deployment** (only on development branch pushes):
   - Deploy to Heroku staging: `breathesafe-staging`
   - Clone production database to staging
   - Run database migrations
   - Deploy inference Lambda to staging
   - Deploy training Lambda to staging

3. **Production Deployment** (only after successful staging deployment):
   - Deploy to Heroku production: `breathesafe`
   - Run database migrations
   - Deploy inference Lambda to production
   - Deploy training Lambda to production

### Required GitHub Secrets

Add these secrets to your GitHub repository:

#### Heroku Configuration
- `HEROKU_API_KEY`: Your Heroku API key
- `HEROKU_STAGING_APP`: `breathesafe-staging`
- `HEROKU_PRODUCTION_APP`: `breathesafe` (or your production app name)

#### AWS Configuration
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `AWS_REGION`: Your AWS region (default: `us-east-1`)

#### Email Notifications
- `EMAIL_USERNAME`: Your Gmail username
- `EMAIL_PASSWORD`: Your Gmail app password
- `NOTIFICATION_EMAIL`: Email address for notifications

### How to Use

#### For Pull Requests to Development
1. Create a feature branch from `development`
2. Make your changes
3. Create a pull request to `development`
4. All tests must pass before merging
5. Merge the pull request

#### For Direct Pushes to Development
1. Push directly to `development` branch
2. Tests run automatically
3. If tests pass, staging deployment begins
4. If staging succeeds, production deployment begins

### Workflow Files

- `.github/workflows/deploy-pipeline.yml` - Main deployment pipeline
- `.github/workflows/deploy-inference-lambda-staging.yml` - Staging Lambda deployment (version tags)
- `.github/workflows/deploy-inference-lambda-production.yml` - Production Lambda deployment (version tags)
- `.github/workflows/retrain-model-staging.yml` - Staging model retraining (weekly + version tags)
- `.github/workflows/retrain-model-production.yml` - Production model retraining (weekly + version tags)

## Weekly Automatic Retraining

**Schedule**: Every Saturday at 12:00 AM Eastern Time (5:00 AM UTC)

Both staging and production models are automatically retrained weekly with:
- **Staging**: Separate model for staging environment
- **Production**: Separate model for production environment
- **Lambda Updates**: Both environments automatically deploy updated Lambda functions with new models
- **Notifications**: Email notifications for success/failure

## Manual Version-Based Deployment

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

#### Development Branch Pipeline
- **Test Phase**: All tests must pass
- **Staging**: Heroku app + Lambda functions + database clone
- **Production**: Heroku app + Lambda functions + migrations

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

### Notifications

All deployments send email notifications with:
- Success/failure status
- Trigger type (Development Pipeline, Weekly Auto-Retrain, or Version Tag)
- Deployment details

### Example Deployments

#### Development Branch Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature
git add .
git commit -m "Add new feature"

# Push and create PR to development
git push origin feature/new-feature
# Create PR on GitHub

# After PR is merged to development, pipeline runs automatically
```

#### Manual Version Tags
```bash
# Deploy to staging only
git tag staging-recommender-v0.1.3
git push origin staging-recommender-v0.1.3

# Deploy to production only
git tag production-recommender-v0.1.3
git push origin production-recommender-v0.1.3
```

### Benefits

- **Automated Testing**: All tests run before any deployment
- **Staged Deployment**: Staging first, then production
- **Database Safety**: Staging gets production data clone
- **Automatic Updates**: Models retrained weekly
- **Manual Control**: Version tags for immediate deployments
- **Clear separation**: Staging and production are independent
- **Rollback capability**: Easy to revert to previous versions


export ENVIRONMENT='production'
export SUBFOLDER_NAME='training'
export FUNCTION_NAME="mask-recommender-${SUBFOLDER_NAME}-${ENVIRONMENT}"
export FUNCTION_TAG=${FUNCTION_NAME}:latest
export FOLDER_TO_SAVE_TAR=${PWD}/python/mask_recommender/${SUBFOLDER_NAME}
export AWS_ACCOUNT_ID=585068368316
export PROFILE_NAME='breathesafe'
export AWS_REGION='us-east-1'
git pull && docker build --platform linux/amd64 -t ${FUNCTION_TAG} ${FOLDER_TO_SAVE_TAR} && docker save ${FUNCTION_TAG} > ${FOLDER_TO_SAVE_TAR}/myimage.tar

export FOLDER_WITH_IMAGE_TAR_PATH="remote:/workspaces/breathesafe/python/mask_recommender/${SUBFOLDER_NAME}/myimage.tar"
export CODESPACE_NAME=reimagined-couscous-54xjwp5p5wfp6j6
export AWS_FUNCTION_TAG=${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/$FUNCTION_NAME:latest
# gh cs cp -e "${FOLDER_WITH_IMAGE_TAR_PATH}" ${FOLDER_TO_SAVE_TAR} -c ${CODESPACE_NAME} && docker load < ${FOLDER_TO_SAVE_TAR}/myimage.tar

docker tag ${FUNCTION_TAG} ${AWS_FUNCTION_TAG} && aws ecr get-login-password  --region ${AWS_REGION} | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com && docker push ${AWS_FUNCTION_TAG}

aws lambda create-function \
  --function-name ${FUNCTION_NAME}\
  --package-type Image \
  --code ImageUri=${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/${FUNCTION_TAG} \
  --role arn:aws:iam::${AWS_ACCOUNT_ID}:role/lambda-ex

&& aws lambda update-function-code \
  --function-name ${FUNCTION_NAME} \
  --image-uri=${AWS_FUNCTION_TAG}\
  --publish



     # Login and push with the right profile
     aws ecr get-login-password --profile "$PROFILE_NAME" --region $AWS_REGION | \
       docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.$AWS_REGION.amazonaws.com"

     docker push $AWS_FUNCTION_TAG
