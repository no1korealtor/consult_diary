def patch_trade_viewer():
    file_path = r'd:\부동산업무\antigravity\consult_diary\scratch\trade_viewer.py'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the except block in save_briefing_report that prints the error
    import re
    content = re.sub(r'except Exception as e:\s*\n\s*print\(f"       \[!\] 브리핑 파일 저장 중 오류 발생: \{e\}"\)', 'except Exception as e:\n            raise', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched trade_viewer.py")

patch_trade_viewer()
