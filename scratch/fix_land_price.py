import sys

file_path = "building_viewer.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

target = """    if bld_data.get("land_price_m2"):
        p_m2 = bld_data["land_price_m2"]"""

replacement = """    land_price_str = "정보없음"
    if bld_data.get("land_price_m2"):
        p_m2 = bld_data["land_price_m2"]"""

content = content.replace(target, replacement)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("done")
