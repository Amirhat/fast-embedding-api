#!/bin/bash
# Quick start script for Fast Embedding API

echo "🚀 Starting Fast Embedding API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Run the application
echo "✨ Launching API server..."
python -m src.main
