#!/usr/bin/env python3
"""
Enterprise RAG System Backend Runner
Supports both FastAPI server and CLI modes
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def load_environment():
    """Load environment variables from .env file if it exists"""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print(f"📁 Loading environment from {env_file}")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    else:
        # Load from config.env.example if .env doesn't exist
        example_env = Path(__file__).parent / "config.env.example"
        if example_env.exists():
            print(f"📁 Loading environment from {example_env}")
            with open(example_env) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        # Only set if not already set
                        if key.strip() not in os.environ:
                            os.environ[key.strip()] = value.strip()

def run_server(host="0.0.0.0", port=8000, reload=True):
    """Run the FastAPI server"""
    import uvicorn
    
    print("🚀 Starting Enterprise RAG System Server...")
    print(f"📍 Server will be available at: http://{host}:{port}")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🎯 Web Dashboard: http://localhost:8000/")
    print("=" * 60)
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
        access_log=True
    )

async def run_cli():
    """Run the CLI interface"""
    from app.cli import run_cli
    await run_cli()

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("openai", "openai"),
        ("lancedb", "lancedb"),
        ("pypdf", "pypdf"),
        ("python-docx", "docx"),  # python-docx imports as docx
        ("beautifulsoup4", "bs4"),  # beautifulsoup4 imports as bs4
        ("requests", "requests")
    ]
    
    missing_packages = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_environment():
    """Check if required environment variables are set"""
    model_provider = os.getenv("MODEL_PROVIDER", "openai").lower()
    
    required_vars = []
    if model_provider == "openai":
        required_vars = ["OPENAI_API_KEY"]
    elif model_provider == "anthropic":
        required_vars = ["ANTHROPIC_API_KEY"]
    elif model_provider == "google":
        required_vars = ["GOOGLE_API_KEY"]
    elif model_provider in ["vllm", "custom"]:
        required_vars = ["CUSTOM_API_BASE_URL"]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️  Warning: Missing environment variables for {model_provider}:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Set these variables in your .env file or environment")
        return False
    
    return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Enterprise RAG System Backend",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_backend.py                    # Run FastAPI server (default)
  python run_backend.py --cli              # Run CLI interface
  python run_backend.py --host 0.0.0.0 --port 8080  # Custom host/port
  python run_backend.py --no-reload        # Disable auto-reload
        """
    )
    
    parser.add_argument(
        "--cli", 
        action="store_true", 
        help="Run in CLI mode instead of server mode"
    )
    parser.add_argument(
        "--host", 
        default="0.0.0.0", 
        help="Host to bind the server to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port to bind the server to (default: 8000)"
    )
    parser.add_argument(
        "--no-reload", 
        action="store_true", 
        help="Disable auto-reload in development mode"
    )
    parser.add_argument(
        "--check", 
        action="store_true", 
        help="Check requirements and environment, then exit"
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_environment()
    
    # Check requirements
    print("🔍 Checking requirements...")
    if not check_requirements():
        sys.exit(1)
    
    print("✅ All required packages are installed")
    
    # Check environment
    print("🔍 Checking environment configuration...")
    env_ok = check_environment()
    if env_ok:
        print("✅ Environment configuration looks good")
    else:
        print("⚠️  Environment configuration has issues (see above)")
    
    # Show current configuration
    model_provider = os.getenv("MODEL_PROVIDER", "openai")
    print(f"🤖 Current LLM Provider: {model_provider}")
    
    if args.check:
        print("✅ Check completed")
        sys.exit(0 if env_ok else 1)
    
    if args.cli:
        # Run CLI mode
        print("🖥️  Starting CLI mode...")
        try:
            asyncio.run(run_cli())
        except KeyboardInterrupt:
            print("\n👋 CLI terminated by user")
    else:
        # Run server mode
        reload = not args.no_reload
        run_server(host=args.host, port=args.port, reload=reload)

if __name__ == "__main__":
    main() 