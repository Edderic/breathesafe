#!/bin/bash
set -e

echo "=== Release Phase ==="
echo "Python version:"
python3 --version

echo ""
echo "Installing Python dependencies..."
python3 -m pip install --user -r requirements.txt

echo ""
echo "Verifying sklearn_crfsuite installation..."
python3 -c "import sklearn_crfsuite; print('✓ sklearn_crfsuite found')"

echo ""
echo "Running migrations..."
bundle exec rails db:migrate

echo ""
echo "Training mask predictor model..."
bundle exec rails mask_predictor:train

echo ""
echo "=== Release Phase Complete ==="
