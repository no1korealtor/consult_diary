with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('suffix = is_wolse and ""', 'suffix = "/월" if is_wolse else ""')

with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open('test_briefing_integration.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('safe_addr = "서울_중구_신당동_3**"', 'safe_addr = "서울중구신당동395"')

with open('test_briefing_integration.py', 'w', encoding='utf-8') as f:
    f.write(content)
