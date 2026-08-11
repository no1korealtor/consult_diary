import sys
import os
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trade_viewer import load_member_info, format_member_name

member = load_member_info()
if member:
    m_name = format_member_name(member.get("name", ""))
    raw_phone = member.get("phone", "")
    if raw_phone == "01091280586" or "010-9128-0586" in raw_phone:
        m_phone = "☎ 02-375-4489<br/>📞 010-9128-0586"
    else:
        m_phone = f"📞 {raw_phone}"
    m_addr = member.get("office_address", "")
    m_reg = member.get("registration_number", "")
else:
    m_name = "조항준 공인중개사"
    m_phone = "☎ 02-375-4489<br/>📞 010-9128-0586"
    m_addr = "서울 마포구 모래내로 7길 52"
    m_reg = ""

print("PDF Footer m_phone (HTML/Paragraph):")
print(m_phone)

if member:
    raw_phone = member.get("phone", "")
    if raw_phone == "01091280586" or "010-9128-0586" in raw_phone:
        phone_line = "☎ 02-375-4489\n📞 010-9128-0586"
    else:
        phone_line = f"📞 {raw_phone}"
else:
    phone_line = "☎ 02-375-4489\n📞 010-9128-0586"

print("\nText Footer phone_line:")
print(phone_line)
