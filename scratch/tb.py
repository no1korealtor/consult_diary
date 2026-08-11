import re
with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    content = f.read()
content = re.sub(r'except Exception as copy_err:.*?print\(.*?copy_err.*?$', r'except Exception as copy_err:\n        import traceback; traceback.print_exc(); raise', content, flags=re.DOTALL | re.MULTILINE)
with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(content)
