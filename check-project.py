#!/usr/bin/env python
"""
Simple Project Check
"""

import os

def main():
    print("Digi Setu AI - Project Check")
    print("=" * 30)
    
    # Check key directories
    dirs_to_check = [
        "frontend",
        "backend", 
        "backend/app",
        "frontend/components"
    ]
    
    print("Checking directories...")
    all_good = True
    for dir_path in dirs_to_check:
        if os.path.exists(dir_path):
            print("  " + dir_path + ": OK")
        else:
            print("  " + dir_path + ": MISSING")
            all_good = False
    
    # Check key files
    files_to_check = [
        "README.md",
        "docker-compose.yml",
        "frontend/package.json",
        "backend/requirements.txt"
    ]
    
    print("\nChecking key files...")
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print("  " + file_path + ": OK")
        else:
            print("  " + file_path + ": MISSING")
            all_good = False
    
    if all_good:
        print("\nSUCCESS: Project structure is complete!")
    else:
        print("\nWARNING: Some files/directories are missing")
    
    print("\nProject is ready for development!")

if __name__ == "__main__":
    main()
