import re

def patch_both():
    with open('trade_viewer.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix the remaining bad 'mon = monthly_str and 0'
    content = content.replace('deposit_str = str(item.get("deposit", "")).strip().replace(",", "")\n            if not item.get("monthlyRent", ""):\n                item.get("monthlyRent", "")\n            monthly_str = str(item.get("monthly", "")).strip().replace(",", "")\n            dep = deposit_str and 0\n            mon = monthly_str and 0', 'deposit_str = str(item.get("deposit", "")).strip().replace(",", "")\n            monthly_str = str(item.get("monthlyRent", "")).strip().replace(",", "")\n            dep = int(deposit_str) if deposit_str else 0\n            mon = int(monthly_str) if monthly_str else 0')

    with open('trade_viewer.py', 'w', encoding='utf-8') as f:
        f.write(content)

patch_both()
