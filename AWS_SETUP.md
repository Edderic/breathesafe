# AWS Setup for GitHub Actions Deployment

## Required IAM Permissions

The AWS user used in GitHub Actions needs the following permissions for ECR and Lambda operations:

### ECR Permissions
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",
                "ecr:PutImage"
            ],
            "Resource": "*"
        }
    ]
}
```

### Lambda Permissions
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:UpdateFunctionCode",
                "lambda:GetFunction",
                "lambda:WaitForFunctionUpdate"
            ],
            "Resource": [
                "arn:aws:lambda:us-east-1:585068368316:function:mask-recommender-inference-staging",
                "arn:aws:lambda:us-east-1:585068368316:function:mask-recommender-training-staging"
            ]
        }
    ]
}
```

## How to Fix the ECR Permission Issue

### Option 1: Update IAM Policy (Recommended)
1. Go to AWS IAM Console
2. Find the user `***-production` (user ID: 585068368316)
3. Attach the ECR permissions policy above
4. Or create a new policy with the permissions and attach it

### Option 2: Use AWS CLI to Login (Temporary Workaround)
If you can't immediately update the IAM permissions, you can modify the workflow to use AWS CLI for ECR login:

```yaml
- name: Login to Amazon ECR (Alternative)
  run: |
    aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${{ steps.login-ecr.outputs.registry }}
```

### Option 3: Skip ECR for Now
If ECR is not immediately needed, you can comment out the ECR and Lambda deployment steps:

```yaml
# - name: Login to Amazon ECR
#   id: login-ecr
#   uses: aws-actions/amazon-ecr-login@v2

# - name: Build and deploy inference Lambda to staging
#   id: build-inference
#   ...
```

## Required GitHub Secrets

Make sure these secrets are set in your GitHub repository:
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `AWS_REGION`: AWS region (defaults to us-east-1)

## Verification

After setting up the permissions, the deployment should be able to:
1. Login to ECR successfully
2. Build and push Docker images
3. Update Lambda functions with the new images