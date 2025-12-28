#!/bin/bash
set -e

# AWS Lambda Deployment Script for Mask Component Predictor
# This script packages and deploys the Lambda function

FUNCTION_NAME="mask-component-predictor"
REGION="us-east-1"  # Change to your preferred region
RUNTIME="python3.11"
HANDLER="lambda_function.lambda_handler"
TIMEOUT=30
MEMORY=512
ROLE_NAME="mask-predictor-lambda-role"

echo "========================================="
echo "AWS Lambda Deployment"
echo "========================================="
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first:"
    echo "   brew install awscli"
    echo "   aws configure"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Run:"
    echo "   aws configure"
    exit 1
fi

echo "✓ AWS CLI configured"
echo ""

# Step 1: Train model if not exists
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

# Step 2: Create deployment package directory
echo "📦 Creating deployment package..."
rm -rf package deployment.zip
mkdir -p package

# Step 3: Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt -t package/ --quiet
echo "✓ Dependencies installed"
echo ""

# Step 4: Copy Lambda function and model
echo "📦 Copying Lambda function and model..."
cp lambda_function.py package/
cp crf_model.pkl package/
echo "✓ Files copied"
echo ""

# Step 5: Create ZIP file
echo "📦 Creating deployment ZIP..."
cd package
zip -r ../deployment.zip . -q
cd ..
echo "✓ Deployment package created: $(du -h deployment.zip | cut -f1)"
echo ""

# Step 6: Create IAM role if it doesn't exist
echo "🔐 Checking IAM role..."
if ! aws iam get-role --role-name $ROLE_NAME &> /dev/null; then
    echo "Creating IAM role: $ROLE_NAME"

    # Create trust policy
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

    # Create role
    aws iam create-role \
        --role-name $ROLE_NAME \
        --assume-role-policy-document file://trust-policy.json \
        --description "Execution role for mask component predictor Lambda"

    # Attach basic Lambda execution policy
    aws iam attach-role-policy \
        --role-name $ROLE_NAME \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

    echo "✓ IAM role created"
    echo "⏳ Waiting 10 seconds for role to propagate..."
    sleep 10

    rm trust-policy.json
else
    echo "✓ IAM role exists"
fi

# Get role ARN
ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)
echo "   Role ARN: $ROLE_ARN"
echo ""

# Step 7: Deploy Lambda function
echo "🚀 Deploying Lambda function..."

if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION &> /dev/null; then
    echo "Updating existing function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://deployment.zip \
        --region $REGION \
        --no-cli-pager

    echo "✓ Function code updated"

    # Update configuration
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --timeout $TIMEOUT \
        --memory-size $MEMORY \
        --region $REGION \
        --no-cli-pager > /dev/null

    echo "✓ Function configuration updated"
else
    echo "Creating new function..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --role $ROLE_ARN \
        --handler $HANDLER \
        --zip-file fileb://deployment.zip \
        --timeout $TIMEOUT \
        --memory-size $MEMORY \
        --region $REGION \
        --description "Mask component predictor using CRF model" \
        --no-cli-pager

    echo "✓ Function created"
fi
echo ""

# Step 8: Test the function
echo "🧪 Testing Lambda function..."
cat > test-event.json <<EOF
{
  "mask_name": "3M Aura 9205+ N95"
}
EOF

aws lambda invoke \
    --function-name $FUNCTION_NAME \
    --payload file://test-event.json \
    --region $REGION \
    response.json \
    --no-cli-pager > /dev/null

if [ -f response.json ]; then
    echo "✓ Test invocation successful"
    echo ""
    echo "Response:"
    cat response.json | python3 -m json.tool
    echo ""
    rm response.json test-event.json
fi

# Step 9: Get function URL (if using Function URLs)
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Function Name: $FUNCTION_NAME"
echo "Region: $REGION"
echo "Runtime: $RUNTIME"
echo "Memory: ${MEMORY}MB"
echo "Timeout: ${TIMEOUT}s"
echo ""
echo "To invoke from Rails, use:"
echo "  AWS_REGION=$REGION"
echo "  LAMBDA_FUNCTION_NAME=$FUNCTION_NAME"
echo ""
echo "Or create a Function URL:"
echo "  aws lambda create-function-url-config \\"
echo "    --function-name $FUNCTION_NAME \\"
echo "    --auth-type NONE \\"
echo "    --region $REGION"
echo ""
echo "Clean up:"
rm -rf package
echo "✓ Cleaned up temporary files"
