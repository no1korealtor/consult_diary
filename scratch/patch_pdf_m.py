with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if line.strip() == 'member = load_member_info()' and 'phone_line =' in lines[i+2]:
        new_lines.append('''        member = load_member_info()
        m_name = "조항준 공인중개사"
        m_phone = "010-9128-0586 | ☎ 02-375-4489"
        m_addr = "서울 마포구 모래내로 7길 52"
        m_reg = ""
        if member:
            m_name = format_member_name(member.get("name", "")) or m_name
            m_phone = member.get("phone", "") or m_phone
            m_addr = member.get("office_address", "") or m_addr
            m_reg = member.get("registration_number", "")
''')
        skip = True
    elif skip and line.strip() == "story.append(Paragraph(f\"<b>{m_name}</b>\", center_bold_style))":
        skip = False
        new_lines.append(line)
    elif not skip:
        new_lines.append(line)

with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
