import sys
import os
from unittest.mock import patch

if sys.platform == 'win32':
    try:
        sys.stdin.reconfigure(encoding='utf-8', errors='replace')
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def test_run():
    # Mocking standard inputs: first address query, then n for cma_choice, then 'q' to quit the loop.
    inputs = ["성산동 135-1", "n", "q"]
    
    with patch('builtins.input', side_effect=inputs):
        from building_viewer import run_building_viewer
        print("Starting building viewer mock test...")
        run_building_viewer()

if __name__ == "__main__":
    test_run()
