# AWS Profile Setup for Lambda Deployment

## Overview

The deployment script now supports AWS profiles with **'breathesafe' as the default**.

## Quick Start

### Option 1: Use 'breathesafe' Profile (Recommended)

```bash
# Configure the profile
aws configure --profile breathesafe

# Deploy (uses 'breathesafe' automatically)
./deploy.sh
```

### Option 2: Use Different Profile

```bash
# Deploy with custom profile
./deploy.sh --profile myprofile

# Deploy with default profile
./deploy.sh --profile default
```

### Option 3: Different Region

```bash
./deploy.sh --profile breathesafe --region us-west-2
```

## Configuration

### Set Up 'breathesafe' Profile

```bash
aws configure --profile breathesafe
```

You'll be prompted for:
- **AWS Access Key ID**: Your AWS access key
- **AWS Secret Access Key**: Your AWS secret key
- **Default region**: `us-east-1` (recommended)
- **Default output format**: `json` (recommended)

### Verify Configuration

```bash
# Check if profile exists
aws configure list --profile breathesafe

# Test credentials
aws sts get-caller-identity --profile breathesafe
```

Expected output:
```json
{
    "UserId": "AIDAXXXXXXXXXXXXXXXXX",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/yourname"
}
```

## Deployment Examples

### Basic Deployment

```bash
cd lambda/mask_predictor

# Uses 'breathesafe' profile by default
./deploy.sh
```

Output:
```
=========================================
AWS Lambda Deployment
=========================================

Profile: breathesafe
Region: us-east-1

✓ AWS CLI configured for profile: breathesafe
  Account ID: 123456789012
...
```

### Custom Profile

```bash
# Use 'production' profile
./deploy.sh --profile production

# Use default AWS credentials
./deploy.sh --profile default
```

### Different Region

```bash
# Deploy to us-west-2
./deploy.sh --region us-west-2

# Deploy to eu-west-1 with custom profile
./deploy.sh --profile eu-prod --region eu-west-1
```

## AWS Credentials File

Your credentials are stored in `~/.aws/credentials`:

```ini
[breathesafe]
aws_access_key_id = AKIA...
aws_secret_access_key = ...

[default]
aws_access_key_id = AKIA...
aws_secret_access_key = ...

[production]
aws_access_key_id = AKIA...
aws_secret_access_key = ...
```

And configuration in `~/.aws/config`:

```ini
[profile breathesafe]
region = us-east-1
output = json

[profile production]
region = us-west-2
output = json
```

## Troubleshooting

### "Unable to locate credentials"

**Problem**: Profile doesn't exist or credentials not configured.

**Solution**:
```bash
# Configure the profile
aws configure --profile breathesafe

# Or check existing profiles
cat ~/.aws/credentials
```

### "The security token included in the request is invalid"

**Problem**: Credentials are expired or invalid.

**Solution**:
```bash
# Reconfigure the profile
aws configure --profile breathesafe

# Test credentials
aws sts get-caller-identity --profile breathesafe
```

### "Access Denied"

**Problem**: IAM user doesn't have required permissions.

**Required permissions**:
- `lambda:CreateFunction`
- `lambda:UpdateFunctionCode`
- `lambda:UpdateFunctionConfiguration`
- `lambda:GetFunction`
- `lambda:InvokeFunction`
- `iam:CreateRole`
- `iam:GetRole`
- `iam:AttachRolePolicy`

**Solution**: Ask your AWS administrator to grant these permissions.

### Wrong Profile Used

**Problem**: Deployed to wrong AWS account.

**Solution**:
```bash
# Check which profile was used
aws sts get-caller-identity --profile breathesafe

# Redeploy with correct profile
./deploy.sh --profile breathesafe
```

## Multiple Environments

### Development

```bash
# Configure dev profile
aws configure --profile breathesafe-dev

# Deploy to dev
./deploy.sh --profile breathesafe-dev --region us-east-1
```

### Production

```bash
# Configure prod profile
aws configure --profile breathesafe-prod

# Deploy to prod
./deploy.sh --profile breathesafe-prod --region us-east-1
```

### Staging

```bash
# Configure staging profile
aws configure --profile breathesafe-staging

# Deploy to staging
./deploy.sh --profile breathesafe-staging --region us-west-2
```

## Environment Variables

You can also set the profile via environment variable:

```bash
# Set profile for all AWS commands
export AWS_PROFILE=breathesafe

# Now deploy (will use AWS_PROFILE)
./deploy.sh
```

**Note**: Command-line `--profile` flag takes precedence over `AWS_PROFILE`.

## Best Practices

1. **Use Named Profiles**: Don't use the default profile for production
2. **Separate Environments**: Use different profiles for dev/staging/prod
3. **Least Privilege**: Grant only required IAM permissions
4. **Rotate Keys**: Regularly rotate AWS access keys
5. **MFA**: Enable MFA for production accounts

## Help

```bash
# Show all options
./deploy.sh --help
```

Output:
```
Usage: ./deploy.sh [OPTIONS]

Options:
  --profile PROFILE    AWS profile to use (default: breathesafe)
  --region REGION      AWS region (default: us-east-1)
  --help               Show this help message

Examples:
  ./deploy.sh                           # Use breathesafe profile
  ./deploy.sh --profile default         # Use default profile
  ./deploy.sh --profile prod --region us-west-2
```

## Summary

- **Default profile**: `breathesafe`
- **Default region**: `us-east-1`
- **Configure**: `aws configure --profile breathesafe`
- **Deploy**: `./deploy.sh`
- **Custom profile**: `./deploy.sh --profile myprofile`
- **Help**: `./deploy.sh --help`

---

**Ready to deploy?** Just run `./deploy.sh` and it will use the 'breathesafe' profile automatically! 🚀
