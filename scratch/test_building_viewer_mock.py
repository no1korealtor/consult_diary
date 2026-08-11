import sys
from unittest.mock import patch

# Mock input to automatically supply "중동 395" followed by "q"
inputs = ["중동 395", "q"]
def mock_input(prompt=""):
    if inputs:
        val = inputs.pop(0)
        print(f"{prompt}{val}")
        return val
    return "q"

# Patch builtins.input and execute
with patch('builtins.input', mock_input):
    import building_viewer
    building_viewer.run_building_viewer()
