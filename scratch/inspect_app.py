import sys
import io
import os
from pywinauto.application import Application

def inspect_app(backend_name):
    print(f"--- {backend_name} 방식으로 연결 시도 ---")
    try:
        # title_re를 사용해 한방 창에 연결 (정규식으로 느슨하게 매칭)
        app = Application(backend=backend_name).connect(title_re=".*계약서.*|.*확인서.*|.*한방.*", timeout=5)
        dlg = app.top_window()
        title = dlg.window_text()
        print(f"[+] 연결된 창: '{title}'")
        
        # 파일에 저장
        safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        file_name = f"hanbang_tree_{backend_name}_{safe_title[:10]}.txt"
        file_path = os.path.join(os.getcwd(), file_name)
        
        old_stdout = sys.stdout
        sys.stdout = my_stdout = io.StringIO()
        try:
            dlg.print_control_identifiers()
        except Exception as e:
            print(f"트리 출력 에러: {e}")
        sys.stdout = old_stdout
        
        output = my_stdout.getvalue()
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(output)
            
        print(f"    -> 분석 완료. {file_name}에 저장되었습니다.\n")
        
    except Exception as e:
        print(f"연결 실패: {e}\n")

if __name__ == "__main__":
    inspect_app("win32")
    inspect_app("uia")
