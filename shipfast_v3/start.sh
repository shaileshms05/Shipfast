#!/bin/bash

echo "🚀 Starting ShipFast v3.0 Backend..."
echo

# Determine which venv to use
if [ -d "../venv" ]; then
    echo "Using existing virtual environment from parent directory..."
    VENV_PATH="../venv"
elif [ -d "venv" ]; then
    echo "Using local virtual environment..."
    VENV_PATH="venv"
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    VENV_PATH="venv"
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Verify activation
echo "Python path: $(which python)"
echo "Pip path: $(which pip)"

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org
pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org

# Verify structlog installation
echo
echo "Verifying installation..."
python -c "import structlog; print('✅ structlog installed')" || echo "❌ structlog not found"
python -c "import fastapi; print('✅ fastapi installed')" || echo "❌ fastapi not found"
python -c "import langchain; print('✅ langchain installed')" || echo "❌ langchain not found"

# Start server
echo
echo "======================================================================"
echo "Starting ShipFast v3.0 Server..."
echo "======================================================================"

# Set PYTHONPATH to include the shipfast_v3 directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

python api/server.py
