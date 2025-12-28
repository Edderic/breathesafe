"""
AWS Lambda handler for mask component prediction using CRF model.

This Lambda function provides a serverless API for predicting mask name components.
It loads a pre-trained CRF model and returns predictions for mask names.
"""

import json
import pickle
import re
import os
from pathlib import Path

# Global variable for model caching (survives across warm invocations)
crf_model = None
MODEL_PATH = Path(__file__).parent / 'crf_model.pkl'


def load_model():
    """Load CRF model from pickle file. Called once per Lambda container."""
    global crf_model
    if crf_model is None:
        print(f"Loading CRF model from {MODEL_PATH}")
        with open(MODEL_PATH, 'rb') as f:
            crf_model = pickle.load(f)
        print(f"✓ Model loaded successfully")
    return crf_model


def tokenize(mask_name):
    """Split mask name into tokens."""
    tokens = re.split(r'[\s\-—,\[\]()]+', mask_name)
    return [t for t in tokens if t]


def token_features(tokens, i):
    """Extract features for token at position i."""
    token = tokens[i]

    features = {
        'bias': 1.0,
        'token.lower': token.lower(),
        'token.isupper': token.isupper(),
        'token.istitle': token.istitle(),
        'token.isdigit': token.isdigit(),
        'token.length': len(token),
        'position.first': i == 0,
        'position.last': i == len(tokens) - 1,
        'position.index': i,
    }

    # Prefix and suffix features
    if len(token) >= 2:
        features['token.prefix2'] = token[:2].lower()
        features['token.suffix2'] = token[-2:].lower()
    if len(token) >= 3:
        features['token.prefix3'] = token[:3].lower()
        features['token.suffix3'] = token[-3:].lower()

    # Character type features
    features['token.hasdigit'] = any(c.isdigit() for c in token)
    features['token.hasalpha'] = any(c.isalpha() for c in token)
    features['token.hasslash'] = '/' in token
    features['token.hasdash'] = '-' in token

    # Context features (previous token)
    if i > 0:
        prev_token = tokens[i-1]
        features.update({
            'prev.token.lower': prev_token.lower(),
            'prev.token.isupper': prev_token.isupper(),
            'prev.token.istitle': prev_token.istitle(),
        })
    else:
        features['BOS'] = True

    # Context features (next token)
    if i < len(tokens) - 1:
        next_token = tokens[i+1]
        features.update({
            'next.token.lower': next_token.lower(),
            'next.token.isupper': next_token.isupper(),
            'next.token.istitle': next_token.istitle(),
        })
    else:
        features['EOS'] = True

    return features


def predict_components(mask_name, model):
    """Predict mask components for a single mask name."""
    tokens = tokenize(mask_name)
    if not tokens:
        return {'error': 'No tokens found'}

    # Extract features
    features = [token_features(tokens, i) for i in range(len(tokens))]

    # Predict
    labels = model.predict([features])[0]

    # Build breakdown
    breakdown = []
    for token, label in zip(tokens, labels):
        breakdown.append({token: label})

    # Group by category
    components = {
        'brand': [],
        'model': [],
        'size': [],
        'color': [],
        'style': [],
        'strap': [],
        'filter_type': [],
        'valved': [],
        'misc': []
    }

    for token, label in zip(tokens, labels):
        if label in components:
            components[label].append(token)

    # Get marginal probabilities for confidence scores
    try:
        marginals = model.predict_marginals([features])[0]
        avg_confidence = sum(max(m.values()) for m in marginals) / len(marginals)
    except:
        avg_confidence = None

    return {
        'mask_name': mask_name,
        'tokens': tokens,
        'breakdown': breakdown,
        'components': components,
        'confidence': avg_confidence
    }


def lambda_handler(event, context):
    """
    AWS Lambda handler function.

    Expected event formats:

    1. Single prediction:
       {
         "mask_name": "3M Aura 9205+ N95"
       }

    2. Batch prediction:
       {
         "mask_names": ["3M 1860s", "Honeywell H910"]
       }

    3. API Gateway format (automatically handled):
       {
         "body": "{\"mask_name\": \"3M Aura 9205+ N95\"}"
       }
    """

    print(f"Lambda invoked with event: {json.dumps(event)}")

    # Load model (cached after first invocation)
    try:
        model = load_model()
    except Exception as e:
        print(f"Error loading model: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Model loading failed: {str(e)}'})
        }

    # Handle API Gateway format (body is JSON string)
    if 'body' in event:
        try:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid JSON in body'})
            }
    else:
        body = event

    # Handle batch prediction
    if 'mask_names' in body:
        mask_names = body['mask_names']
        if not isinstance(mask_names, list):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'mask_names must be an array'})
            }

        results = []
        for mask_name in mask_names:
            result = predict_components(mask_name, model)
            results.append(result)

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'predictions': results})
        }

    # Handle single prediction
    elif 'mask_name' in body:
        mask_name = body['mask_name']
        result = predict_components(mask_name, model)

        if 'error' in result:
            return {
                'statusCode': 400,
                'body': json.dumps(result)
            }

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }

    # Invalid request
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Missing required parameter: mask_name or mask_names'
            })
        }


# For local testing
if __name__ == '__main__':
    # Test single prediction
    test_event = {
        'mask_name': '3M Aura 9205+ N95'
    }

    result = lambda_handler(test_event, None)
    print(json.dumps(json.loads(result['body']), indent=2))

    # Test batch prediction
    batch_event = {
        'mask_names': [
            '3M 1860s',
            'Zimi ZM9233 w/ Headstraps',
            'BreatheTeq - Large'
        ]
    }

    result = lambda_handler(batch_event, None)
    print(json.dumps(json.loads(result['body']), indent=2))
