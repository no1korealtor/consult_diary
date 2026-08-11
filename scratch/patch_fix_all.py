import sys

with open('fix_all_bugs.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('new_classify_by_floor = """def classify_by_floor', 'new_classify_by_floor = r"""def classify_by_floor')

with open('fix_all_bugs.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("fixed fix_all_bugs.py")
