"""
Quick Setup Verification for Milestone 1
=========================================
Fast check to ensure everything is ready.
"""

import os
import sys

def check_files():
    """Check if all required files exist."""
    print("Checking files...")
    files = {
        "modules/search_papers.py": "Paper search module",
        "modules/download_pdf.py": "PDF download module",
        "scripts/prepare_dataset.py": "Dataset preparation",
        "scripts/check_imports.py": "Dependency checker",
        "scripts/demo_milestone1.py": "Complete demo",
        "requirements.txt": "Dependencies list",
        "README.md": "Documentation",
        ".env.example": "Configuration template",
        "MILESTONE1_SUMMARY.md": "Implementation summary"
    }
    
    all_good = True
    for filepath, description in files.items():
        if os.path.exists(filepath):
            print(f"  ✅ {filepath}")
        else:
            print(f"  ❌ {filepath} - MISSING")
            all_good = False
    
    return all_good

def check_folders():
    """Check if required folders exist."""
    print("\nChecking folders...")
    folders = ["data/pdfs", "data/metadata", "data/logs", "modules", "scripts"]
    
    for folder in folders:
        if os.path.exists(folder):
            print(f"  ✅ {folder}")
        else:
            print(f"  ⚠️  {folder} - creating...")
            os.makedirs(folder, exist_ok=True)

def check_imports():
    """Check critical imports."""
    print("\nChecking critical imports...")
    
    try:
        import semanticscholar
        print("  ✅ semanticscholar")
    except:
        print("  ❌ semanticscholar - run: pip install semanticscholar")
        return False
    
    try:
        import requests
        print("  ✅ requests")
    except:
        print("  ❌ requests - run: pip install requests")
        return False
    
    try:
        import tqdm
        print("  ✅ tqdm")
    except:
        print("  ❌ tqdm - run: pip install tqdm")
        return False
    
    try:
        from dotenv import load_dotenv
        print("  ✅ python-dotenv")
    except:
        print("  ❌ python-dotenv - run: pip install python-dotenv")
        return False
    
    return True

def main():
    print("="*60)
    print(" MILESTONE 1 - QUICK VERIFICATION ")
    print("="*60)
    print()
    
    # Check Python version
    print(f"Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    if sys.version_info >= (3, 8):
        print("  ✅ Compatible")
    else:
        print("  ⚠️  3.8+ recommended")
    print()
    
    # Run checks
    files_ok = check_files()
    check_folders()
    imports_ok = check_imports()
    
    print()
    print("="*60)
    
    if files_ok and imports_ok:
        print(" ✅ MILESTONE 1 READY! ")
        print()
        print("Run: python scripts/prepare_dataset.py")
    else:
        print(" ⚠️  SETUP INCOMPLETE ")
        print()
        if not imports_ok:
            print("Run: pip install -r requirements.txt")
    
    print("="*60)

if __name__ == "__main__":
    main()
