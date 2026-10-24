import re

with open("trade_viewer.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix target_floor is None -> is not None
content = content.replace("if target_floor is None:\n                floor_lbl", "if target_floor is not None:\n                floor_lbl")
content = content.replace("if target_floor is None:\n            floor_lbl", "if target_floor is not None:\n            floor_lbl")
content = content.replace("if target_floor is None:\n                        floor_lbl", "if target_floor is not None:\n                        floor_lbl")

content = content.replace("if target_floor is None:\n                    fl = int(target_floor)", "if target_floor is not None:\n                    fl = int(target_floor)")

content = content.replace("if target_floor is not None or target_area is None:", "if target_floor is not None or target_area is not None:")
content = content.replace("if target_floor is None and floor is None:", "if target_floor is not None and floor is not None:")
content = content.replace("if target_area is None and area is None:", "if target_area is not None and area is not None:")

with open("trade_viewer.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed trade_viewer.py")
