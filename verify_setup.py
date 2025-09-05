#!/usr/bin/env python3
"""
Setup verification script for AI Communication Assistant.
"""
import sys
import subprocess
import os
from pathlib import Path


def check_python_version():
    """Check Python version."""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    return True


def check_uv():
    """Check uv installation."""
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ uv {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    print("❌ uv not found")
    return False


def check_node():
    """Check Node.js installation."""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js {version}")
            return True
    except FileNotFoundError:
        pass
    print("❌ Node.js not found")
    return False


def check_project_structure():
    """Check project structure."""
    required_files = [
        "pyproject.toml",
        "backend/main.py",
        "frontend/dashboard/package.json",
        "docker-compose.yml",
        ".env.example"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ Project structure complete")
    return True


def check_backend_imports():
    """Check backend imports."""
    try:
        result = subprocess.run(
            ["uv", "run", "python", "-c", "from backend.main import app; print('OK')"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ Backend imports successfully")
            return True
        else:
            print(f"❌ Backend import error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Backend check failed: {e}")
        return False


def check_frontend_build():
    """Check frontend build."""
    try:
        original_dir = os.getcwd()
        frontend_path = Path("frontend/dashboard")
        
        if not frontend_path.exists():
            print("❌ Frontend directory not found")
            return False
            
        os.chdir(frontend_path)
        result = subprocess.run(["npm", "run", "build"], capture_output=True, text=True, shell=True)
        os.chdir(original_dir)
        
        if result.returncode == 0:
            print("✅ Frontend builds successfully")
            return True
        else:
            print(f"❌ Frontend build error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Frontend check failed: {e}")
        return False


def main():
    """Main verification function."""
    print("🔍 Verifying AI Communication Assistant setup...\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("uv Package Manager", check_uv),
        ("Node.js", check_node),
        ("Project Structure", check_project_structure),
        ("Backend Configuration", check_backend_imports),
        ("Frontend Build", check_frontend_build),
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        print(f"Checking {name}...")
        if check_func():
            passed += 1
        print()
    
    print(f"📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 Setup verification complete! Your environment is ready.")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and configure your API keys")
        print("2. Run 'make dev' or './dev.sh' to start development servers")
        print("3. Visit http://localhost:3000 for the frontend")
        print("4. Visit http://localhost:8000/docs for the API documentation")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()