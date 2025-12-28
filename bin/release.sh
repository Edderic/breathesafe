#!/bin/bash
set -e

echo "=== Release Phase ==="
echo "Python version:"
python3 --version

echo ""
echo "Checking Python packages..."
python3 -c "import sys; print('Python path:', sys.path)"

echo ""
echo "Attempting to import sklearn_crfsuite..."
python3 -c "import sklearn_crfsuite; print('✓ sklearn_crfsuite found')" || echo "✗ sklearn_crfsuite NOT found"

echo ""
echo "Running migrations..."
bundle exec rails db:migrate

echo ""
echo "Training mask predictor model..."
bundle exec rails mask_predictor:train

echo ""
echo "=== Release Phase Complete ==="
