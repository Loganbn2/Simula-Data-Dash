#!/bin/bash

# AI Chat Analytics Dashboard - Run Script

echo "🚀 Starting AI Chat Analytics Dashboard..."
echo "=================================="

# Check if Python virtual environment exists
if [ ! -d ".venv" ]; then
    echo "⚠️  Virtual environment not found. Please run setup first."
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    echo "✅ Virtual environment found"
    source .venv/bin/activate
fi

# Check if required packages are installed
echo "📦 Checking dependencies..."
python -c "import streamlit, pandas, plotly" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ All dependencies installed"
else
    echo "⚠️  Installing missing dependencies..."
    pip install -r requirements.txt
fi

# Generate sample data if database doesn't exist
if [ ! -f "chat_analytics.db" ]; then
    echo "📊 Generating sample data..."
    python -c "from data_generator import DataGenerator; import sqlite3; import pandas as pd; gen = DataGenerator(); data = gen.generate_sample_data(1000); conn = sqlite3.connect('chat_analytics.db'); data.to_sql('chat_logs', conn, if_exists='replace', index=False); conn.close(); print('Sample data generated successfully!')"
fi

# Check for environment file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. AI insights may use fallback mode."
    echo "Add your API keys to .env file for full AI functionality."
fi

echo "🎯 Starting dashboard..."
echo "Dashboard will open at: http://localhost:8501"
echo "Press Ctrl+C to stop the server"
echo "=================================="

# Run the Streamlit app
streamlit run dashboard.py
