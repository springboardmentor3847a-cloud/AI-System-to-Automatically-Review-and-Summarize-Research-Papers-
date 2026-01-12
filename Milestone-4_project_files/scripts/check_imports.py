"""
Dependency Checker for Milestone 1
===================================
Verifies that all required packages are installed and working.
"""

import sys
import importlib


def check_import(package_name, display_name=None):
    """Check if a package can be imported."""
    if display_name is None:
        display_name = package_name
    
    try:
        module = importlib.import_module(package_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {display_name:25} - version {version}")
        return True
    except ImportError as e:
        print(f"❌ {display_name:25} - NOT INSTALLED")
        print(f"   Error: {str(e)}")
        return False


def main():
    """Check all required dependencies for Milestone 1."""
    print("="*80)
    print("MILESTONE 1 - DEPENDENCY CHECK")
    print("="*80)
    print()
    
    # Core dependencies
    print("Core Dependencies:")
    print("-" * 80)
    
    required = [
        ('semanticscholar', 'semanticscholar'),
        ('requests', 'requests'),
        ('dotenv', 'python-dotenv'),
        ('tqdm', 'tqdm'),
    ]
    
    results = []
    for package, display in required:
        results.append(check_import(package, display))
    
    print()
    
    # Future milestone dependencies
    print("Future Milestones (optional for now):")
    print("-" * 80)
    
    optional = [
        ('langchain', 'langchain'),
        ('langgraph', 'langgraph'),
        ('openai', 'openai'),
        ('fitz', 'PyMuPDF4LLM'),
        ('gradio', 'gradio'),
    ]
    
    for package, display in optional:
        check_import(package, display)
    
    print()
    print("="*80)
    
    # Summary
    if all(results):
        print("✅ ALL REQUIRED DEPENDENCIES INSTALLED")
        print("   Ready for Milestone 1!")
    else:
        print("❌ SOME DEPENDENCIES MISSING")
        print("   Run: pip install -r requirements.txt")
    
    print("="*80)
    
    # Python version check
    print(f"\nPython Version: {sys.version}")
    if sys.version_info >= (3, 8):
        print("✅ Python version is compatible (3.8+)")
    else:
        print("⚠️  Python 3.8+ recommended")


if __name__ == "__main__":
    main()
