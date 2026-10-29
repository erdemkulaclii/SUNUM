"""Compatibility entry point for the current academic presentation."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('export_concise_deck.py')),run_name="__main__")
