"""Compatibility entry point for current concise presentation validation."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name("verify_concise.py")),run_name="__main__")
