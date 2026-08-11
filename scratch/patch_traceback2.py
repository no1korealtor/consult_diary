import re
file_path = r'd:\부동산업무\antigravity\consult_diary\scratch\trade_viewer.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all except Exception as e: print(...) with raise
content = re.sub(
    r'except Exception(?: as e)?:\s*\n\s*print\(f"\\n \[오류\] PDF 브리핑 파일 생성 중 오류 발생: \{e\}"\)',
    r'except Exception as e:\n        import traceback; traceback.print_exc()\n        raise',
    content
)

content = re.sub(
    r'except Exception as e:\s*\n\s*print\(f"       \[!\] 브리핑 파일 저장 중 오류 발생: \{e\}"\)',
    r'except Exception as e:\n        import traceback; traceback.print_exc()\n        raise',
    content
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched trade_viewer.py again")
