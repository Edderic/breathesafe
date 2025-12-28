#!/usr/bin/env python3
"""
Inline mask component predictor for Rails integration.

This script loads the pre-trained CRF model and makes predictions.
It can be called directly from Rails using backticks or Open3.

Usage:
    python3 predict_inline.py "3M Aura 9205+ N95"
    python3 predict_inline.py --batch "3M 1860s" "Honeywell H910"
"""

import sys
import json
import pickle
import re
from pathlib import Path

# Model path
MODEL_PATH = Path(__file__).parent / 'crf_model.pkl'

# Global model cache
_model = None


def load_model():
    """Load CRF model from pickle file."""
    global _model
    if _model is None:
        with open(MODEL_PATH, 'rb') as f:
            _model = pickle.load(f)
    return _model


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


def main():
    """Main entry point for CLI usage."""
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Usage: predict_inline.py [--batch] <mask_name> [mask_name2 ...]'}))
        sys.exit(1)

    # Load model
    try:
        model = load_model()
    except Exception as e:
        print(json.dumps({'error': f'Model loading failed: {str(e)}'}))
        sys.exit(1)

    # Check for batch mode
    if sys.argv[1] == '--batch':
        mask_names = sys.argv[2:]
        results = []
        for mask_name in mask_names:
            result = predict_components(mask_name, model)
            results.append(result)
        print(json.dumps({'predictions': results}))
    else:
        # Single prediction
        mask_name = ' '.join(sys.argv[1:])
        result = predict_components(mask_name, model)
        print(json.dumps(result))


if __name__ == '__main__':
    main()
