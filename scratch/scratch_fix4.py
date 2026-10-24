with open('d:/부동산업무/antigravity/consult_diary/trade_viewer.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
'''                            try:
                                floor = int(floor_str)''',
'''                            floor = None
                            try:
                                floor = int(floor_str)'''
)

with open('d:/부동산업무/antigravity/consult_diary/trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(content)
