import sys
import io
import os
from pywinauto import Desktop
from pywinauto.application import Application

def inspect_shallow():
    print("--- uia 방식으로 얕게 탐색 ---")
    try:
        windows = Desktop(backend="uia").windows()
        for w in windows:
            title = w.window_text()
            if not title: continue
            
            if "계약" in title or "확인" in title:
                print(f"[+] 발견된 창: '{title}'")
                try:
                    app = Application(backend="uia").connect(handle=w.handle)
                    dlg = app.window(handle=w.handle)
                    
                    safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                    file_name = f"hanbang_tree_shallow_{safe_title[:10]}.txt"
                    file_path = os.path.join(os.getcwd(), file_name)
                    
                    old_stdout = sys.stdout
                    sys.stdout = my_stdout = io.StringIO()
                    # 깊이를 아주 얕게 제한
                    dlg.print_control_identifiers(depth=3)
                    sys.stdout = old_stdout
                    
                    output = my_stdout.getvalue()
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(output)
                    print(f"    -> 분석 완료. {file_name}에 저장되었습니다.")
                except Exception as e:
                    print(f"    -> 트리 출력 에러: {e}")
    except Exception as e:
        print(f"탐색 실패: {e}")

if __name__ == "__main__":
    inspect_shallow()
