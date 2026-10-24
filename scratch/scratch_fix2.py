import re

with open('d:/부동산업무/antigravity/consult_diary/trade_viewer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace land_val is None:
pattern2 = re.compile(
    r'(\s+)if land_val is None:\s+land_area = float\(land_val\)\s+if land_area > 0:\s+land_pyung = round\(land_area \* 0\.3025, 1\)\s+land_display = f\"\{land_area:\.2f\}㎡ \(\{land_pyung\}평\)\"'
)

replacement2 = r'''\1if land_val is not None:
\1    try:
\1        land_area = float(land_val)
\1        if land_area > 0:
\1            land_pyung = round(land_area * 0.3025, 1)
\1            land_display = f"{land_area:.2f}㎡ ({land_pyung}평)"
\1    except:
\1        pass'''

content = pattern2.sub(replacement2, content)

with open('d:/부동산업무/antigravity/consult_diary/trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(content)
