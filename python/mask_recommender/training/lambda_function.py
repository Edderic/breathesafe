import json
import os
import logging
from train import main

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _build_train_argv(event):
    event = event or {}
    argv = []
    if event.get('epochs') is not None:
        argv.extend(['--epochs', str(event['epochs'])])
    if event.get('learning_rate') is not None:
        argv.extend(['--learning-rate', str(event['learning_rate'])])
    if event.get('model_type'):
        argv.extend(['--model-type', str(event['model_type'])])
    if event.get('loss_type'):
        argv.extend(['--loss-type', str(event['loss_type'])])
    if event.get('class_reweight'):
        argv.append('--class-reweight')
    if event.get('use_facial_perimeter'):
        argv.append('--use-facial-perimeter')
    if event.get('use_diff_perimeter_bins'):
        argv.append('--use-diff-perimeter-bins')
    if event.get('use_diff_perimeter_mask_bins'):
        argv.append('--use-diff-perimeter-mask-bins')
    if event.get('exclude_mask_code'):
        argv.append('--exclude-mask-code')
    if event.get('retrain_with_full'):
        argv.append('--retrain-with-full')
    return argv

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

        train_argv = _build_train_argv(event)
        logger.info("Training argv: %s", train_argv)

        # Call the main training function
        result = main(train_argv)

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
