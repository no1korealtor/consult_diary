# -*- coding: utf-8 -*-
import json, math, os

with open("scratch/sungsan_villa_data.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# Calculate regression curves for old and new
def fit_curve(items):
    pts = [(d["pyung"], d["unit_price"]) for d in items if d["pyung"] > 0 and d["unit_price"] > 0]
    n = len(pts)
    if n < 2:
        return 0, 0
    sum_lnx = sum(math.log(x) for x, y in pts)
    sum_y = sum(y for x, y in pts)
    sum_lnx_sq = sum(math.log(x)**2 for x, y in pts)
    sum_lnx_y = sum(math.log(x) * y for x, y in pts)
    denom = (n * sum_lnx_sq - sum_lnx**2)
    if denom == 0:
        return 0, 0
    b = (n * sum_lnx_y - sum_lnx * sum_y) / denom
    a = (sum_y - b * sum_lnx) / n
    return a, b

old_items = [d for d in raw_data if not d["is_new"]]
new_items = [d for d in raw_data if d["is_new"]]

a_old, b_old = fit_curve(old_items)
a_new, b_new = fit_curve(new_items)

# Attach expected price & diff_pct to all items
for d in raw_data:
    p = d["pyung"]
    if p > 0:
        # benchmark is old curve for base land value
        exp_old = a_old + b_old * math.log(p)
        exp_new = a_new + b_new * math.log(p)
        d["exp_base"] = round(exp_old, 1)
        d["exp_new"] = round(exp_new, 1)
        # diff relative to its own category
        cat_exp = exp_new if d["is_new"] else exp_old
        d["cat_exp"] = round(cat_exp, 1)
        d["diff_pct"] = round((d["unit_price"] - cat_exp) / cat_exp * 100, 1)
        d["base_diff_pct"] = round((d["unit_price"] - exp_old) / exp_old * 100, 1)
    else:
        d["exp_base"] = 0
        d["exp_new"] = 0
        d["cat_exp"] = 0
        d["diff_pct"] = 0
        d["base_diff_pct"] = 0

print(f"Old regression: Y = {a_old:.2f} + ({b_old:.2f}) * ln(X)")
print(f"New regression: Y = {a_new:.2f} + ({b_new:.2f}) * ln(X)")

# Save enriched data
with open("scratch/enriched_villa_data.json", "w", encoding="utf-8") as f:
    json.dump(raw_data, f, ensure_ascii=False, indent=2)

print("Enriched data saved.")
