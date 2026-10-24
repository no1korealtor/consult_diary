import re

with open('d:/부동산업무/antigravity/consult_diary/trade_viewer.py', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = re.compile(
    r'(\s+)if not item\.get\(\"excluUseAr\"\):\s+item\.get\(\"excluUseAr\"\)\s+area_val = item\.get\(\"totalFloorAr\"\)\s+area = None\s+if area_val is None:\s+area = float\(area_val\)\s+pyung = round\(area \* 0\.3025, 1\)\s+area_display = f\"\{area:\.2f\}㎡ \(\{pyung\}평\)\"\s+else:\s+area_display = \"-\"'
)
replacement = r'''\1area_val = item.get("excluUseAr") or item.get("totalFloorAr")
\1area = None
\1if area_val is not None:
\1    try:
\1        area = float(area_val)
\1        pyung = round(area * 0.3025, 1)
\1        area_display = f"{area:.2f}㎡ ({pyung}평)"
\1    except:
\1        area_display = "-"
\1else:
\1    area_display = "-"'''

content = pattern.sub(replacement, content)
with open('d:/부동산업무/antigravity/consult_diary/trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(content)
