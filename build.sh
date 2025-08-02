#!/bin/bash
# Build script to force correct dependency installation

echo "=== Starting Build Process ==="

# Clear pip cache
pip cache purge

# Uninstall WTForms if it exists
pip uninstall -y WTForms

# Install dependencies with force reinstall
pip install --force-reinstall --no-cache-dir -r requirements.txt

# Verify WTForms version
echo "=== Checking WTForms Version ==="
python -c "import wtforms; print(f'WTForms version: {wtforms.__version__}')"

echo "=== Build Complete ===" 