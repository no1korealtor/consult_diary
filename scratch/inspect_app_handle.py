import sys
import io
import os
from pywinauto import Desktop
from pywinauto.application import Application

def inspect_via_handle(backend_name):
    print(f"--- {backend_name} 방식으로 윈도우 탐색 ---")
    try:
        windows = Desktop(backend=backend_name).windows()
        for w in windows:
            title = w.window_text()
            if not title: continue
            
            if "계약" in title or "확인" in title:
                print(f"[+] 발견된 창: '{title}' (Handle: {w.handle})")
                
                try:
                    app = Application(backend=backend_name).connect(handle=w.handle)
                    dlg = app.window(handle=w.handle)
                    
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
                    print(f"    -> 분석 완료. {file_name}에 저장되었습니다.")
                except Exception as e:
                    print(f"    -> 핸들 연결 실패: {e}")
    except Exception as e:
        print(f"탐색 실패: {e}")

if __name__ == "__main__":
    inspect_via_handle("win32")
    inspect_via_handle("uia")
