import os
import sys
import subprocess
import importlib.util

def check_module(module_name):
    """Check if a module is installed"""
    return importlib.util.find_spec(module_name) is not None

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Packages installed successfully.")
        return True
    except subprocess.CalledProcessError:
        print("Failed to install required packages.")
        return False

def main():
    """Main function to run the import process"""
    print("SDGNY Vendor Management System - Data Import")
    print("==========================================")
    print()
    
    # Check if required modules are installed
    required_modules = ["pandas", "pyodbc", "dotenv"]
    missing_modules = [module for module in required_modules if not check_module(module)]
    
    if missing_modules:
        print(f"Missing required modules: {', '.join(missing_modules)}")
        if not install_requirements():
            print("Please install the required packages manually and try again.")
            return
    
    # Import the import_data module
    try:
        from import_data import main as run_import
        print("Starting data import...")
        run_import()
    except Exception as e:
        print(f"Error running import: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
    print("\nPress Enter to exit...")
    input()
