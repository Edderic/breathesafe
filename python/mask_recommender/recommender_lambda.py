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
    recommendations = recommend(event)
    version = '0.1.0'

    return {
        'statusCode': 200,
        'body': json.dumps(recommendations),
        'version': version
    }
