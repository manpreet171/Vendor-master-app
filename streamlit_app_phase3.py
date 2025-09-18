# Phase 3 Requirements System - Root Level Launcher
# This file enables Streamlit Cloud deployment (same pattern as Phase 2)

import os
import sys
import runpy

# Path to the Phase3 application directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHASE3_DIR = os.path.join(BASE_DIR, "Phase3")

# Ensure Phase3 directory is on sys.path so its local imports work
if PHASE3_DIR not in sys.path:
    sys.path.insert(0, PHASE3_DIR)

# Execute the Phase3 app as if it were the main module
APP_PATH = os.path.join(PHASE3_DIR, "app.py")
runpy.run_path(APP_PATH, run_name="__main__")
