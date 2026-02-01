import json
import os
import logging
from train import main

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """
    Lambda handler for training the mask recommender model
    """
    try:
        logger.info("Starting training process")

        # Allow caller to specify environment and S3 bucket
        env = (event or {}).get('environment') or os.environ.get('ENVIRONMENT') or 'staging'
        bucket = (event or {}).get('s3_bucket') or os.environ.get('S3_BUCKET_NAME')
        region = (event or {}).get('s3_bucket_region') or os.environ.get('S3_BUCKET_REGION')
        base_url = (event or {}).get('base_url') or os.environ.get('BREATHESAFE_BASE_URL')
        if env:
            os.environ['ENVIRONMENT'] = str(env)
            os.environ['RAILS_ENV'] = str(env)
        if bucket:
            os.environ['S3_BUCKET_NAME'] = str(bucket)
        if region:
            os.environ['S3_BUCKET_REGION'] = str(region)
        if base_url:
            os.environ['BREATHESAFE_BASE_URL'] = str(base_url)

        # Call the main training function
        result = main()

        logger.info("Training completed successfully")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Training completed successfully',
                'result': result
            })
        }

    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Training failed',
                'message': str(e)
            })
        }
