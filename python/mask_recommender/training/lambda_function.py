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