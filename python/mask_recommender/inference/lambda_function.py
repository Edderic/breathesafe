from recommender import recommend
import datetime
import logging
logger = logging.getLogger()
logger.setLevel("INFO")

import pandas as pd
import json

import numpy as np
import traceback

def handler(event, context):
    """
    Parameters:
        event: dict
        context: dict
    """
    model_filename = './models/fit_predictor.pkl'

    if 'model_filename' in event:
        model_filename = event['model_filename']

    mask_dummies_and_predictors_filename = './models/mask_dummies_and_predictors.pkl'
    if 'mask_dummies_and_predictors_filename' in event:
        mask_dummies_and_predictors_filename = event['mask_dummies_and_predictors_filename']

    recommendations = recommend(
        event,
        model_filename=model_filename,
        mask_dummies_and_predictors_filename=mask_dummies_and_predictors_filename
    )
    version = '0.1.0'

    return {
        'statusCode': 200,
        'body': recommendations.to_json(),
        'version': version
    }

