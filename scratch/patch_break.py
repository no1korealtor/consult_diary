with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('break\n', 'pass\n')

with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(text)
