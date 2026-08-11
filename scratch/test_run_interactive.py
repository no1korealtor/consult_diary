import sys
from unittest.mock import patch
import building_viewer

print("Running building_viewer with mock input '성산동 200-94'...")
with patch('builtins.input', side_effect=["성산동 200-94", ""]):
    try:
        building_viewer.run_building_viewer()
    except Exception as e:
        print(f"Error occurred: {e}")
