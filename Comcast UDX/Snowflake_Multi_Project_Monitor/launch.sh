#!/bin/bash

# Snowflake Multi-Project Monitor - Launch Script
# This script sets up and launches the monitoring application

set -e

echo "🏢 Snowflake Multi-Project Monitor - Setup & Launch"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not installed."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip
pip install --upgrade pip

# Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if secrets file exists
if [ ! -f ".streamlit/secrets.toml" ]; then
    echo "⚠️  Snowflake connection not configured."
    echo "📝 Please copy .streamlit/secrets.toml.example to .streamlit/secrets.toml"
    echo "   and update it with your Snowflake credentials."
    echo ""
    
    # Create .streamlit directory if it doesn't exist
    mkdir -p .streamlit
    
    # Copy example file if it doesn't exist
    if [ ! -f ".streamlit/secrets.toml" ]; then
        cp .streamlit/secrets.toml.example .streamlit/secrets.toml
        echo "✅ Created .streamlit/secrets.toml from example. Please edit this file with your credentials."
    fi
    
    echo ""
    echo "🔧 Required Snowflake Privileges:"
    echo "   GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE <your_role>;"
    echo "   GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY TO ROLE <your_role>;"
    echo "   GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY TO ROLE <your_role>;"
    echo ""
    echo "Press any key to continue once you've configured your connection..."
    read -n 1 -s
fi

# Launch the application
echo "🚀 Launching Snowflake Multi-Project Monitor..."
echo "   Application will be available at: http://localhost:8501"
echo "   Press Ctrl+C to stop the application"
echo ""

streamlit run main.py 