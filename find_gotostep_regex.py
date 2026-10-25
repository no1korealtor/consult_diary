import os
import re

path = "d:/부동산업무/antigravity/consult_diary/rosary.html"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Let's search for method goToStep in class RosaryApp
m = re.search(r'^\s*goToStep\s*\([^\)]*\)\s*\{', text, re.MULTILINE)
if m:
    pos = m.start()
    print("Found method goToStep at:", pos)
    print(text[pos:pos+400])
else:
    print("Method goToStep not found with regex!")
