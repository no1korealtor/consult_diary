import sys
import os
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from market_analyser import load_member_info

member_info = load_member_info()
print("Member Info loaded:", json.dumps(member_info, ensure_ascii=False, indent=2))

office_name = member_info.get("office_name") or member_info.get("office") or ""
office_address = member_info.get("office_address") or ""
phone = member_info.get("phone") or ""

if phone == "01091280586" or "010-9128-0586" in phone or "신대림" in office_name:
    formatted_phone = "02-375-4489"
else:
    formatted_phone = phone
    if phone:
        digits = "".join(filter(str.isdigit, phone))
        if len(digits) == 10:
            formatted_phone = f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11:
            formatted_phone = f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
        elif len(digits) == 9:
            formatted_phone = f"{digits[:2]}-{digits[2:5]}-{digits[5:]}"

print("Formatted Phone in Header:", formatted_phone)
