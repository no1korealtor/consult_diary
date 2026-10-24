import re

with open('d:/부동산업무/antigravity/consult_diary/trade_viewer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all base_* UnboundLocalErrors and "is None and" bugs.

# Fix condition:
content = content.replace("if base_area is None and area is None:", "if base_area is not None and area is not None:")
content = content.replace("if base_price is None and amt_val is None:", "if base_price is not None and amt_val is not None:")

# Inject initializations before loops
content = re.sub(
    r'(\s+)for idx, item in enumerate\(trades\):',
    r'\1base_price = None\n\1base_floor = target_floor\n\1base_area = target_area\n\1for idx, item in enumerate(trades):',
    content
)

content = re.sub(
    r'(\s+)for idx, item in enumerate\(jeonses\):',
    r'\1base_price = None\n\1base_floor = target_floor\n\1base_area = target_area\n\1for idx, item in enumerate(jeonses):',
    content
)

content = re.sub(
    r'(\s+)for idx, item in enumerate\(wolses\):',
    r'\1base_price = None\n\1base_floor = target_floor\n\1base_area = target_area\n\1for idx, item in enumerate(wolses):',
    content
)

with open('d:/부동산업무/antigravity/consult_diary/trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(content)
