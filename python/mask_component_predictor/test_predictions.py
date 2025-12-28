#!/usr/bin/env python3
"""
Quick test script to verify CRF model predictions.
"""

import pickle
import re
from pathlib import Path

# Load model
MODEL_PATH = Path(__file__).parent / 'crf_model.pkl'
with open(MODEL_PATH, 'rb') as f:
    crf = pickle.load(f)

print("✓ Model loaded successfully")
print(f"  Classes: {crf.classes_}")
print()

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

    if len(token) >= 2:
        features['token.prefix2'] = token[:2].lower()
        features['token.suffix2'] = token[-2:].lower()
    if len(token) >= 3:
        features['token.prefix3'] = token[:3].lower()
        features['token.suffix3'] = token[-3:].lower()

    features['token.hasdigit'] = any(c.isdigit() for c in token)
    features['token.hasalpha'] = any(c.isalpha() for c in token)
    features['token.hasslash'] = '/' in token
    features['token.hasdash'] = '-' in token

    if i > 0:
        prev_token = tokens[i-1]
        features.update({
            'prev.token.lower': prev_token.lower(),
            'prev.token.isupper': prev_token.isupper(),
            'prev.token.istitle': prev_token.istitle(),
        })
    else:
        features['BOS'] = True

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

# Test cases
test_masks = [
    "3M 1860s",
    "3M Aura 9205+ N95",
    "Zimi ZM9233 w/ Headstraps",
    "Honeywell H910 Plus",
    "BreatheTeq - Large",
    "Drager X-plore 1950 - Small",
    "Wellbefore Kids KN95 Petite X-Small",
]

print("="*80)
print("PREDICTION TESTS")
print("="*80)

for mask_name in test_masks:
    tokens = tokenize(mask_name)
    features = [token_features(tokens, i) for i in range(len(tokens))]
    labels = crf.predict([features])[0]

    print(f"\n{mask_name}")
    print("-" * 80)
    for token, label in zip(tokens, labels):
        print(f"  {token:30s} → {label}")

print("\n" + "="*80)
print("✓ All predictions completed successfully!")
