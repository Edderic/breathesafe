#!/bin/bash
set -e

echo "=== Release Phase ==="

echo "Running migrations..."
bundle exec rails db:migrate

echo ""
echo "Verifying mask predictor model..."
if [ -f "python/mask_component_predictor/crf_model.pkl" ]; then
  echo "✓ Pre-trained CRF model found"
else
  echo "⚠️  Warning: CRF model not found, predictions will use fallback"
fi

echo ""
echo "=== Release Phase Complete ==="
