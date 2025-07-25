#!/usr/bin/env python3
"""
Integrated startup script for the full-stack application.
This script starts the FastAPI backend which also serves the React frontend.
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are available."""
    print("🔍 Checking dependencies...")
    
    # Check if frontend is built
    frontend_build = Path("frontend/build")
    if not frontend_build.exists():
        print("❌ Frontend build directory not found!")
        print("📦 Building frontend...")
        try:
            subprocess.run(["npm", "run", "build"], cwd="frontend", check=True)
            print("✅ Frontend built successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to build frontend. Please run 'npm install' and 'npm run build' in the frontend directory.")
            return False
    else:
        print("✅ Frontend build found!")
    
    # Check if virtual environment exists
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected!")
    else:
        print("⚠️  No virtual environment detected. Consider using a virtual environment.")
    
    return True

def start_server():
    """Start the integrated server."""
    print("\n🚀 Starting integrated server...")
    print("📡 Backend API will be available at: http://localhost:8000/api/")
    print("🌐 Frontend will be available at: http://localhost:8000/")
    print("📚 API Documentation will be available at: http://localhost:8000/docs")
    print("\n" + "="*60)
    print("Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    try:
        # Start the server using uvicorn
        subprocess.run([
            "uvicorn", 
            "complete_app:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        return False
    
    return True

def main():
    """Main function to start the integrated application."""
    print("🏗️  Starting Full-Stack Application")
    print("="*50)
    
    # Change to the script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Start the server
    if not start_server():
        sys.exit(1)

if __name__ == "__main__":
    main()
