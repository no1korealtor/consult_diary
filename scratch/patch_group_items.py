import re
import traceback

def patch_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    new_func = """        def group_items(items):
            under_26 = []; between_26_43 = []; above_43 = []
            if not items:
                return (under_26, between_26_43, above_43)
            for item in items:
                area_val = item.get("excluUseAr")
                if not area_val:
                    area_val = item.get("totalFloorAr")
                if area_val is None:
                    area_val = 0
                try:
                    area = float(area_val)
                except:
                    area = 0.0
                if area < 26.0:
                    under_26.append(item)
                elif area < 43.0:
                    between_26_43.append(item)
                else:
                    above_43.append(item)
            return (under_26, between_26_43, above_43)"""

    content = re.sub(
        r'        def group_items\(items\):.*?        report_lines\.append\("■ \[매매\] 시세 요약"\)',
        new_func + '\n        report_lines.append("■ [매매] 시세 요약")',
        content,
        flags=re.DOTALL
    )

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Patched {file_path}")

try:
    patch_file('trade_viewer.py')
except Exception as e:
    traceback.print_exc()
