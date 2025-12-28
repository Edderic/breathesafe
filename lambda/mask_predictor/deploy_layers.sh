#!/bin/bash
set -e

# AWS Lambda Deployment with Layers
# This script creates a Lambda Layer for dependencies and deploys the function code separately

FUNCTION_NAME="mask-component-predictor"
LAYER_NAME="mask-predictor-dependencies"
REGION="us-east-1"
AWS_PROFILE="breathesafe"
RUNTIME="python3.11"
HANDLER="lambda_function.lambda_handler"
TIMEOUT=30
MEMORY=512
ROLE_NAME="mask-predictor-lambda-role"

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
echo "AWS Lambda Deployment with Layers"
echo "========================================="
echo ""
echo "Profile: $AWS_PROFILE"
echo "Region: $REGION"
echo ""

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found"
    exit 1
fi

if ! aws sts get-caller-identity $AWS_OPTS &> /dev/null; then
    echo "❌ AWS credentials not configured for profile '$AWS_PROFILE'"
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity $AWS_OPTS --query Account --output text)
echo "✓ AWS CLI configured"
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

# Step 1: Create Lambda Layer with dependencies
echo "📦 Creating Lambda Layer..."
rm -rf layer python layer.zip

mkdir -p python
pip3 install -r requirements.txt -t python/ --platform manylinux2014_x86_64 --only-binary=:all: --quiet

echo "📦 Optimizing layer size..."
cd python

# Remove unnecessary files
find . -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "test" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.md" -delete 2>/dev/null || true
find . -name "*.txt" -delete 2>/dev/null || true
find . -name "*.rst" -delete 2>/dev/null || true
find . -type d -name "examples" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "benchmarks" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyx" -delete 2>/dev/null || true
find . -name "*.pxd" -delete 2>/dev/null || true
find . -name "*.c" -delete 2>/dev/null || true
find . -name "*.cpp" -delete 2>/dev/null || true
find . -name "*.h" -delete 2>/dev/null || true

# Remove scipy/numpy test data and docs
rm -rf scipy/datasets 2>/dev/null || true
rm -rf numpy/doc 2>/dev/null || true
rm -rf numpy/tests 2>/dev/null || true
rm -rf scipy/tests 2>/dev/null || true
rm -rf sklearn/datasets/tests 2>/dev/null || true
rm -rf sklearn/datasets/data 2>/dev/null || true

# Strip debug symbols from .so files
find . -name "*.so" -exec strip {} + 2>/dev/null || true

cd ..

LAYER_SIZE=$(du -sh python/ | cut -f1)
echo "✓ Layer optimized (${LAYER_SIZE})"

# Create layer ZIP
echo "📦 Creating layer ZIP..."
zip -r layer.zip python/ -q
LAYER_ZIP_SIZE=$(du -h layer.zip | cut -f1)
echo "✓ Layer ZIP created (${LAYER_ZIP_SIZE})"
echo ""

# Publish layer
echo "🚀 Publishing Lambda Layer..."
LAYER_VERSION=$(aws lambda publish-layer-version \
    --layer-name $LAYER_NAME \
    --description "Dependencies for mask component predictor (scikit-learn, sklearn-crfsuite)" \
    --zip-file fileb://layer.zip \
    --compatible-runtimes $RUNTIME \
    $AWS_OPTS \
    --query 'Version' \
    --output text)

echo "✓ Layer published: version $LAYER_VERSION"

LAYER_ARN="arn:aws:lambda:${REGION}:${ACCOUNT_ID}:layer:${LAYER_NAME}:${LAYER_VERSION}"
echo "  Layer ARN: $LAYER_ARN"
echo ""

# Step 2: Create function deployment package (code + model only)
echo "📦 Creating function deployment package..."
rm -rf function function.zip

mkdir function
cp lambda_function.py function/
cp crf_model.pkl function/

cd function
zip -r ../function.zip . -q
cd ..

FUNCTION_ZIP_SIZE=$(du -h function.zip | cut -f1)
echo "✓ Function ZIP created (${FUNCTION_ZIP_SIZE})"
echo ""

# Step 3: Create IAM role if needed
echo "🔐 Checking IAM role..."
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
else
    echo "✓ IAM role exists"
fi

ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME $AWS_OPTS --query 'Role.Arn' --output text)
echo "  Role ARN: $ROLE_ARN"
echo ""

# Step 4: Deploy Lambda function
echo "🚀 Deploying Lambda function..."

if aws lambda get-function --function-name $FUNCTION_NAME $AWS_OPTS &> /dev/null; then
    echo "Updating existing function..."

    # Update function code
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://function.zip \
        $AWS_OPTS > /dev/null

    echo "✓ Function code updated"

    # Wait for update
    echo "⏳ Waiting for update to complete..."
    aws lambda wait function-updated \
        --function-name $FUNCTION_NAME \
        $AWS_OPTS

    # Update configuration with layer
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --layers $LAYER_ARN \
        --timeout $TIMEOUT \
        --memory-size $MEMORY \
        $AWS_OPTS > /dev/null

    echo "✓ Function configuration updated"
else
    echo "Creating new function..."

    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --role $ROLE_ARN \
        --handler $HANDLER \
        --zip-file fileb://function.zip \
        --layers $LAYER_ARN \
        --timeout $TIMEOUT \
        --memory-size $MEMORY \
        --description "Mask component predictor using CRF model (with layers)" \
        $AWS_OPTS > /dev/null

    echo "✓ Function created"
fi
echo ""

# Step 5: Test the function
echo "🧪 Testing Lambda function..."

TEST_PAYLOAD='{"mask_name":"3M Aura 9205+ N95"}'

aws lambda invoke \
    --function-name $FUNCTION_NAME \
    --cli-binary-format raw-in-base64-out \
    --payload "$TEST_PAYLOAD" \
    response.json \
    --no-cli-pager \
    $AWS_OPTS > /dev/null

if [ -f response.json ]; then
    # Check for errors
    if grep -q "errorType" response.json; then
        echo "❌ Test invocation failed"
        echo ""
        echo "Response:"
        cat response.json | python3 -m json.tool
        echo ""
        rm response.json
        exit 1
    else
        echo "✓ Test invocation successful"
        echo ""
        echo "Response:"
        cat response.json | python3 -m json.tool
        echo ""
        rm response.json
    fi
fi

# Cleanup
echo "🧹 Cleaning up..."
rm -rf python function layer.zip function.zip
echo "✓ Temporary files removed"
echo ""

echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Function Name: $FUNCTION_NAME"
echo "Region: $REGION"
echo "Profile: $AWS_PROFILE"
echo "Runtime: $RUNTIME"
echo "Layer: $LAYER_NAME (version $LAYER_VERSION)"
echo "Memory: ${MEMORY}MB"
echo "Timeout: ${TIMEOUT}s"
echo ""
echo "Function ZIP: ${FUNCTION_ZIP_SIZE}"
echo "Layer ZIP: ${LAYER_ZIP_SIZE}"
echo ""
echo "To invoke from Rails, use:"
echo "  AWS_REGION=$REGION"
echo "  LAMBDA_FUNCTION_NAME=$FUNCTION_NAME"
echo ""
