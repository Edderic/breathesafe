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
    recommendations = recommend(
        event,
        model_filename='./models/fit_predictor.pkl',
        mask_dummies_and_predictors_filename='./models/mask_dummies_and_predictors.pkl'
    )
    version = '0.1.0'

    return {
        'statusCode': 200,
        'body': json.dumps(recommendations),
        'version': version
    }
