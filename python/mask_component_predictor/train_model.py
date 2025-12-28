#!/usr/bin/env python3
"""
Train CRF model for mask component prediction from breakdown annotations.
"""

import json
import pickle
import sys
from pathlib import Path
import sklearn_crfsuite
from sklearn_crfsuite import metrics
from sklearn.model_selection import train_test_split


def tokenize(mask_name):
    """Split mask name into tokens (matches Ruby tokenizer)."""
    import re
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
        features['BOS'] = True  # Beginning of sequence

    # Context features (next token)
    if i < len(tokens) - 1:
        next_token = tokens[i+1]
        features.update({
            'next.token.lower': next_token.lower(),
            'next.token.isupper': next_token.isupper(),
            'next.token.istitle': next_token.istitle(),
        })
    else:
        features['EOS'] = True  # End of sequence

    return features


def extract_features_and_labels(breakdown_data):
    """
    Convert breakdown data to CRF format.

    Args:
        breakdown_data: List of dicts with 'mask_name' and 'breakdown' keys

    Returns:
        X: List of feature sequences
        y: List of label sequences
    """
    X = []
    y = []

    for item in breakdown_data:
        mask_name = item['mask_name']
        breakdown = item['breakdown']  # List of {token: category} dicts

        tokens = tokenize(mask_name)

        # Create label sequence from breakdown
        labels = []
        for token_dict in breakdown:
            # Each dict has one key-value pair: {token: category}
            token = list(token_dict.keys())[0]
            category = list(token_dict.values())[0]
            labels.append(category)

        # Verify token count matches
        if len(tokens) != len(labels):
            print(f"Warning: Token mismatch for '{mask_name}'")
            print(f"  Tokens ({len(tokens)}): {tokens}")
            print(f"  Labels ({len(labels)}): {labels}")
            continue

        # Extract features for each token
        features = [token_features(tokens, i) for i in range(len(tokens))]

        X.append(features)
        y.append(labels)

    return X, y


def train_crf_model(X_train, y_train):
    """Train CRF model."""
    crf = sklearn_crfsuite.CRF(
        algorithm='lbfgs',
        c1=0.1,  # L1 regularization
        c2=0.1,  # L2 regularization
        max_iterations=100,
        all_possible_transitions=True,
        verbose=True
    )

    crf.fit(X_train, y_train)
    return crf


def evaluate_model(crf, X_test, y_test):
    """Evaluate CRF model."""
    y_pred = crf.predict(X_test)

    # Flatten predictions and labels for metrics
    labels = list(crf.classes_)

    print("\n" + "="*80)
    print("EVALUATION RESULTS")
    print("="*80)

    # Overall metrics
    print(f"\nAccuracy: {metrics.flat_accuracy_score(y_test, y_pred):.3f}")

    # Per-category metrics
    print("\nPer-category metrics:")
    print(metrics.flat_classification_report(
        y_test, y_pred, labels=labels, digits=3
    ))

    return y_pred


def main():
    """Main training script."""
    print("Mask Component Predictor - CRF Model Training")
    print("="*80)

    # Load training data from Rails
    training_data_path = Path(__file__).parent / 'training_data.json'

    if not training_data_path.exists():
        print(f"\nError: Training data not found at {training_data_path}")
        print("Please run: rails mask_predictor:export_training_data")
        sys.exit(1)

    with open(training_data_path, 'r') as f:
        breakdown_data = json.load(f)

    print(f"\nLoaded {len(breakdown_data)} annotated masks")

    # Extract features and labels
    print("\nExtracting features...")
    X, y = extract_features_and_labels(breakdown_data)

    print(f"Total sequences: {len(X)}")
    print(f"Total tokens: {sum(len(seq) for seq in X)}")

    # Category distribution
    all_labels = [label for seq in y for label in seq]
    from collections import Counter
    label_counts = Counter(all_labels)
    print("\nCategory distribution:")
    for label, count in label_counts.most_common():
        print(f"  {label}: {count}")

    # Split into train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"\nTrain set: {len(X_train)} sequences")
    print(f"Test set: {len(X_test)} sequences")

    # Train model
    print("\nTraining CRF model...")
    crf = train_crf_model(X_train, y_train)

    # Evaluate
    evaluate_model(crf, X_test, y_test)

    # Save model
    model_path = Path(__file__).parent / 'crf_model.pkl'
    with open(model_path, 'wb') as f:
        pickle.dump(crf, f)

    print(f"\n✓ Model saved to {model_path}")

    # Show top features for each category
    print("\n" + "="*80)
    print("TOP FEATURES PER CATEGORY")
    print("="*80)

    for label in crf.classes_:
        print(f"\n{label.upper()}:")
        top_features = sorted(
            [(feat, weight) for feat, weight in crf.state_features_.items()
             if feat.startswith(f'{label}:')],
            key=lambda x: abs(x[1]),
            reverse=True
        )[:10]

        for feat, weight in top_features:
            feat_name = feat.split(':', 1)[1] if ':' in feat else feat
            print(f"  {feat_name:40s} {weight:+.3f}")


if __name__ == '__main__':
    main()
