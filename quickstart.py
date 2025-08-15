#!/usr/bin/env python3
"""
Quick Start Script for AI Chat Analytics Dashboard
"""

import os
import sys
import subprocess
from pathlib import Path

def install_dependencies():
    """Install required Python packages."""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False
    return True

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported. Please use Python 3.8+")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def create_env_file():
    """Create .env file if it doesn't exist."""
    env_path = Path(".env")
    if env_path.exists():
        print("✅ .env file already exists")
        return True
    
    print("📝 Creating .env file...")
    env_content = """# AI Chat Analytics Dashboard Configuration

# AI Services (Optional - for enhanced insights)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Supabase Configuration (Optional - for production database)
# Get these from your Supabase project dashboard
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here

# Fallback Database (SQLite - used automatically if Supabase not configured)
DATABASE_URL=sqlite:///chat_analytics.db
"""
    
    with open(env_path, "w") as f:
        f.write(env_content)
    
    print("✅ .env file created with template configuration")
    return True

def run_dashboard():
    """Launch the Streamlit dashboard."""
    print("🚀 Launching dashboard...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to launch dashboard")
        return False
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    return True

def main():
    print("🎯 AI Chat Analytics Dashboard - Quick Start")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n💡 Try running manually: pip install -r requirements.txt")
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    print("\n" + "=" * 50)
    print("🎉 Setup Complete!")
    print("\n📋 What's configured:")
    print("   • SQLite database (automatic fallback)")
    print("   • Sample data generation")
    print("   • All analytics features")
    print("\n🔧 Optional enhancements:")
    print("   • Edit .env to add OpenAI/Anthropic keys for AI insights")
    print("   • Set up Supabase for production database (see SUPABASE_SETUP.md)")
    print("\n🚀 Starting dashboard...")
    
    # Launch dashboard
    run_dashboard()

if __name__ == "__main__":
    main()
