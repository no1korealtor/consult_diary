import re

with open('d:/부동산업무/antigravity/consult_diary/trade_viewer.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("if base_floor is None and floor is None:", "if base_floor is not None and floor is not None:")

# I need to ensure base_floor is initialized.
content = content.replace("diff_parts = []\n", "diff_parts = []\n                            base_floor = target_floor\n")

with open('d:/부동산업무/antigravity/consult_diary/trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(content)
