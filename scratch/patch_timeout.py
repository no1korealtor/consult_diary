import os
import re

def patch_timeouts(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Replace timeout=5 with timeout=20 globally for urlopen to fix API timeouts
    content = content.replace('timeout=5', 'timeout=20')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Timeout patched successfully in", file_path)

if __name__ == '__main__':
    patch_timeouts(r"d:\부동산업무\antigravity\AutoBot_Clean\trade_viewer.py")
    # Also patch market_analyser.py just in case there are timeout=5 there
    patch_timeouts(r"d:\부동산업무\antigravity\AutoBot_Clean\market_analyser.py")
