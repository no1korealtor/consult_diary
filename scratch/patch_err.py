with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('print(f"        [!] 브리핑 보고서 생성 중 오류 발생: {copy_err}")', 'import traceback; traceback.print_exc(); print(f"        [!] 브리핑 보고서 생성 중 오류 발생: {copy_err}")')
content = content.replace('print(f"        [!] 브리핑 PDF 생성 중 오류 발생: {pdf_err}")', 'import traceback; traceback.print_exc(); print(f"        [!] 브리핑 PDF 생성 중 오류 발생: {pdf_err}")')
content = content.replace('print(f"        [!] 데이터 가공 중 예외 발생: {e}")', 'import traceback; traceback.print_exc(); print(f"        [!] 데이터 가공 중 예외 발생: {e}")')

with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(content)
