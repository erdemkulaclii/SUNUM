"""Compatibility entry point for the current Leaflet presentation checks."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name("verify_leaflet.py")),run_name="__main__")
