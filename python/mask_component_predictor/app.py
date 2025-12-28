#!/usr/bin/env python3
"""
Flask API for mask component prediction using trained CRF model.
"""

import json
import os
import pickle
import re
import sys
from pathlib import Path
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load model at startup
MODEL_PATH = Path(__file__).parent / 'crf_model.pkl'
crf_model = None

def load_model():
    """Load trained CRF model."""
    global crf_model
    if MODEL_PATH.exists():
        with open(MODEL_PATH, 'rb') as f:
            crf_model = pickle.load(f)
        print(f"✓ Loaded CRF model from {MODEL_PATH}")
    else:
        print(f"⚠ Model not found at {MODEL_PATH}")
        print("  Run: python train_model.py")

def tokenize(mask_name):
    """Split mask name into tokens (matches Ruby tokenizer)."""
    # Split by space, hyphen, em-dash, comma, brackets, parentheses
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

def predict_components(mask_name):
    """Predict components for a mask name."""
    if crf_model is None:
        return {'error': 'Model not loaded'}

    tokens = tokenize(mask_name)
    if not tokens:
        return {'error': 'No tokens found'}

    # Extract features
    features = [token_features(tokens, i) for i in range(len(tokens))]

    # Predict
    labels = crf_model.predict([features])[0]

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
        marginals = crf_model.predict_marginals([features])[0]
        confidences = [max(m.values()) for m in marginals]
        avg_confidence = sum(confidences) / len(confidences)
    except:
        avg_confidence = None

    return {
        'mask_name': mask_name,
        'tokens': tokens,
        'breakdown': breakdown,
        'components': components,
        'confidence': avg_confidence
    }

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'model_loaded': crf_model is not None
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Predict components for a mask name."""
    data = request.get_json()

    if not data or 'mask_name' not in data:
        return jsonify({'error': 'mask_name required'}), 400

    mask_name = data['mask_name']
    result = predict_components(mask_name)

    if 'error' in result:
        return jsonify(result), 500

    return jsonify(result)

@app.route('/predict_batch', methods=['POST'])
def predict_batch():
    """Predict components for multiple mask names."""
    data = request.get_json()

    if not data or 'mask_names' not in data:
        return jsonify({'error': 'mask_names array required'}), 400

    mask_names = data['mask_names']
    results = []

    for mask_name in mask_names:
        result = predict_components(mask_name)
        results.append(result)

    return jsonify({'predictions': results})

if __name__ == '__main__':
    load_model()

    # Get port from command line argument or environment variable
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get('PORT', 5000))

    # For development
    app.run(host='0.0.0.0', port=port, debug=True)
