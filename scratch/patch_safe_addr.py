with open('test_briefing_integration.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('safe_addr = "서울중구신당동395"', 'safe_addr = "서울특별시마포구중동395"')

with open('test_briefing_integration.py', 'w', encoding='utf-8') as f:
    f.write(content)
