#!/usr/bin/env python3
"""
UI server runner script for AGUIApp
"""
import os
import sys
from pathlib import Path

# Add the ui directory to Python path
ui_dir = Path(__file__).parent / "ui"
sys.path.insert(0, str(ui_dir))

if __name__ == "__main__":
    # Load environment variables if config.env exists
    env_file = Path(__file__).parent / "config.env"
    if env_file.exists():
        print(f"Loading environment from {env_file}")
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Import and run the AGUIApp
    from main import agui_app
    
    port = int(os.getenv("UI_PORT", 8501))
    print(f"🚀 Starting Enterprise RAG UI on port {port}")
    print(f"🔗 Backend URL: {os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')}")
    print(f"🤖 Model Provider: {os.getenv('MODEL_PROVIDER', 'openai')}")
    
    agui_app.serve(app="main:app", port=port, reload=True) 