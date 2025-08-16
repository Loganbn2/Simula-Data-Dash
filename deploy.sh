#!/bin/bash
# Render deployment script

echo "🚀 Starting Simula Data Dashboard deployment..."

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install core dependencies first
echo "📦 Installing core dependencies..."
pip install streamlit==1.28.0 pandas==2.0.3 plotly==5.17.0

# Install additional dependencies
echo "📦 Installing additional dependencies..."
pip install python-dotenv==1.0.0 supabase==2.0.0

# Verify installation
echo "✅ Verifying installation..."
python -c "import streamlit, pandas, plotly; print('Core packages imported successfully')"

echo "🎉 Deployment setup complete!"
