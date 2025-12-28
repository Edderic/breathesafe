#!/bin/bash
set -e

# AWS Lambda Docker Deployment Script
# This script builds and deploys the Lambda function as a Docker container
# Docker images support up to 10GB (vs 250MB for ZIP files)

FUNCTION_NAME="mask-component-predictor"
REGION="us-east-1"
AWS_PROFILE="breathesafe"
IMAGE_NAME="mask-component-predictor"
TIMEOUT=30
MEMORY=512

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --profile)
            AWS_PROFILE="$2"
            shift 2
            ;;
        --region)
            REGION="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --profile PROFILE    AWS profile to use (default: breathesafe)"
            echo "  --region REGION      AWS region (default: us-east-1)"
            echo "  --help               Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                           # Use breathesafe profile"
            echo "  $0 --profile default         # Use default profile"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

AWS_OPTS="--profile $AWS_PROFILE --region $REGION"

echo "========================================="
echo "AWS Lambda Docker Deployment"
echo "========================================="
echo ""
echo "Profile: $AWS_PROFILE"
echo "Region: $REGION"
echo ""

# Check prerequisites
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker Desktop:"
    echo "   https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it:"
    echo "   brew install awscli"
    exit 1
fi

echo "✓ Docker installed"
echo "✓ AWS CLI installed"
echo ""

# Check AWS credentials
if ! aws sts get-caller-identity $AWS_OPTS &> /dev/null; then
    echo "❌ AWS credentials not configured for profile '$AWS_PROFILE'"
    echo "Run: aws configure --profile $AWS_PROFILE"
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity $AWS_OPTS --query Account --output text)
echo "✓ AWS credentials configured"
echo "  Account ID: $ACCOUNT_ID"
echo ""

# Train model if not exists
if [ ! -f "crf_model.pkl" ]; then
    echo "📦 Training CRF model..."
    cd ../../
    PORT=1234 rails mask_predictor:train
    cp python/mask_component_predictor/crf_model.pkl lambda/mask_predictor/
    cd lambda/mask_predictor
    echo "✓ Model copied"
else
    echo "✓ Model already exists"
fi
echo ""

# Create ECR repository if it doesn't exist
echo "📦 Setting up ECR repository..."
ECR_REPO_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${IMAGE_NAME}"

if ! aws ecr describe-repositories --repository-names $IMAGE_NAME $AWS_OPTS &> /dev/null; then
    echo "Creating ECR repository..."
    aws ecr create-repository \
        --repository-name $IMAGE_NAME \
        --image-scanning-configuration scanOnPush=true \
        $AWS_OPTS > /dev/null
    echo "✓ ECR repository created"
else
    echo "✓ ECR repository exists"
fi
echo "  Repository URI: $ECR_REPO_URI"
echo ""

# Login to ECR
echo "🔐 Logging in to ECR..."
aws ecr get-login-password $AWS_OPTS | docker login --username AWS --password-stdin $ECR_REPO_URI
echo "✓ Logged in to ECR"
echo ""

# Build Docker image
echo "🐳 Building Docker image..."
docker build --platform linux/amd64 -t $IMAGE_NAME:latest .
echo "✓ Docker image built"
echo ""

# Tag and push to ECR
echo "📤 Pushing image to ECR..."
docker tag $IMAGE_NAME:latest $ECR_REPO_URI:latest
docker push $ECR_REPO_URI:latest
echo "✓ Image pushed to ECR"
echo ""

# Create or update Lambda function
echo "🚀 Deploying Lambda function..."

# Check if function exists
if aws lambda get-function --function-name $FUNCTION_NAME $AWS_OPTS &> /dev/null; then
    echo "Updating existing function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --image-uri $ECR_REPO_URI:latest \
        $AWS_OPTS > /dev/null

    echo "✓ Function code updated"

    # Wait for update to complete
    echo "⏳ Waiting for update to complete..."
    aws lambda wait function-updated \
        --function-name $FUNCTION_NAME \
        $AWS_OPTS

    # Update configuration
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --timeout $TIMEOUT \
        --memory-size $MEMORY \
        $AWS_OPTS > /dev/null

    echo "✓ Function configuration updated"
else
    echo "Creating new function..."

    # Create IAM role if needed
    ROLE_NAME="mask-predictor-lambda-role"
    if ! aws iam get-role --role-name $ROLE_NAME $AWS_OPTS &> /dev/null; then
        echo "Creating IAM role..."

        cat > trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

        aws iam create-role \
            --role-name $ROLE_NAME \
            --assume-role-policy-document file://trust-policy.json \
            --description "Execution role for mask component predictor Lambda" \
            $AWS_OPTS > /dev/null

        aws iam attach-role-policy \
            --role-name $ROLE_NAME \
            --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
            $AWS_OPTS

        rm trust-policy.json

        echo "✓ IAM role created"
        echo "⏳ Waiting 10 seconds for role to propagate..."
        sleep 10
    fi

    ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME $AWS_OPTS --query 'Role.Arn' --output text)

    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --package-type Image \
        --code ImageUri=$ECR_REPO_URI:latest \
        --role $ROLE_ARN \
        --timeout $TIMEOUT \
        --memory-size $MEMORY \
        --description "Mask component predictor using CRF model (Docker)" \
        $AWS_OPTS > /dev/null

    echo "✓ Function created"
fi
echo ""

# Test the function
echo "🧪 Testing Lambda function..."
cat > test-event.json <<EOF
{
  "mask_name": "3M Aura 9205+ N95"
}
EOF

aws lambda invoke \
    --function-name $FUNCTION_NAME \
    --payload file://test-event.json \
    response.json \
    --no-cli-pager \
    $AWS_OPTS > /dev/null

if [ -f response.json ]; then
    echo "✓ Test invocation successful"
    echo ""
    echo "Response:"
    cat response.json | python3 -m json.tool
    echo ""
    rm response.json test-event.json
fi

echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Function Name: $FUNCTION_NAME"
echo "Region: $REGION"
echo "Profile: $AWS_PROFILE"
echo "Package Type: Docker Image"
echo "Image URI: $ECR_REPO_URI:latest"
echo "Memory: ${MEMORY}MB"
echo "Timeout: ${TIMEOUT}s"
echo ""
echo "To invoke from Rails, use:"
echo "  AWS_REGION=$REGION"
echo "  LAMBDA_FUNCTION_NAME=$FUNCTION_NAME"
echo ""
