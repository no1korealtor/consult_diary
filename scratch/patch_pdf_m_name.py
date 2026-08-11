with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.strip().startswith('member = load_member_info()') and 'm_name' in lines[i+1]:
        # Insert m_name logic
        lines[i] = '''        member = load_member_info()
        m_name = "조항준 공인중개사"
        phone_line = "📞 010-9128-0586 | ☎ 02-375-4489"
        if member:
            m_name = format_member_name(member.get("name", "")) or m_name
            if member.get("phone"):
                phone_line = f"📞 {member.get('phone')}"
'''

with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
