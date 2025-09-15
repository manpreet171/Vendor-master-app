import os
import sys
import runpy

# Path to the Phase2 application directory (contains the real app.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHASE2_DIR = os.path.join(BASE_DIR, "Phase2 (Vendor management app)")

# Ensure Phase2 directory is on sys.path so its local imports work
if PHASE2_DIR not in sys.path:
    sys.path.insert(0, PHASE2_DIR)

# Execute the Phase2 app as if it were the main module
APP_PATH = os.path.join(PHASE2_DIR, "app.py")
runpy.run_path(APP_PATH, run_name="__main__")
