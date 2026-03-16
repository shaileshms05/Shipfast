#!/bin/bash

echo "🚀 Starting ShipFast v3.0 Backend (Clean Environment)..."
echo

# Always use a dedicated venv for shipfast_v3 to avoid conflicts
VENV_PATH="venv_shipfast"

if [ ! -d "$VENV_PATH" ]; then
    echo "Creating dedicated virtual environment for ShipFast v3.0..."
    python3 -m venv "$VENV_PATH"
fi

# Activate the dedicated venv
echo "Activating dedicated virtual environment..."
source "$VENV_PATH/bin/activate"

# Verify activation
echo "Python: $(which python)"
echo "Pip: $(which pip)"
echo

# Install dependencies
echo "Installing ShipFast v3.0 dependencies..."
pip install --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org -q
pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org

# Verify critical packages
echo
echo "Verifying installation..."
python -c "import structlog; print('✅ structlog')" 2>/dev/null || echo "❌ structlog"
python -c "import fastapi; print('✅ fastapi')" 2>/dev/null || echo "❌ fastapi"
python -c "import langchain; print('✅ langchain')" 2>/dev/null || echo "❌ langchain"
python -c "import langgraph; print('✅ langgraph')" 2>/dev/null || echo "❌ langgraph"
python -c "from cerebras.cloud.sdk import Cerebras; print('✅ cerebras-cloud-sdk')" 2>/dev/null || echo "❌ cerebras-cloud-sdk"

# Start server
echo
echo "======================================================================"
echo "🚀 Starting ShipFast v3.0 Server..."
echo "======================================================================"
echo

# Set PYTHONPATH to include the shipfast_v3 directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
echo "PYTHONPATH set to: $PYTHONPATH"
echo

python api/server.py
