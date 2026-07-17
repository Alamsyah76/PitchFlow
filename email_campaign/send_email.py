"""
PitchFlow Email Campaign — CLI Entry Point
===========================================
Thin wrapper that delegates to the modules/campaign layer.
Usage: python send_email.py [--dry-run] [--preview N]
"""
import sys
from pathlib import Path

# Ensure modules/ is importable
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from modules.campaign import main

if __name__ == "__main__":
    main()
