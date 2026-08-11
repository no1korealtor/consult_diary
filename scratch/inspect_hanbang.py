import sys
import io
import os

try:
    from pywinauto import Desktop
except ImportError:
    print("pywinauto is not installed. Please install it first.")
    sys.exit(1)

def scan_windows(backend_name):
    print(f"\n--- Scanning with backend: {backend_name} ---")
    try:
        desktop = Desktop(backend=backend_name)
        windows = desktop.windows()
        found = False
        for w in windows:
            title = w.window_text()
            if not title:
                continue
            # 한방 프로그램이나 확인설명서 관련 창을 찾습니다.
            if "한방" in title or "확인" in title or "설명서" in title:
                found = True
                print(f"\n[+] 발견된 창 이름: '{title}'")
                
                # UI 구조를 텍스트로 추출
                old_stdout = sys.stdout
                sys.stdout = my_stdout = io.StringIO()
                try:
                    w.print_control_identifiers(depth=4) # 너무 깊으면 오래걸리므로 4단계까지만
                except Exception as e:
                    print(f"컨트롤을 읽는 중 에러 발생: {e}")
                sys.stdout = old_stdout
                
                output = my_stdout.getvalue()
                
                # 파일로 저장
                safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                file_name = f"hanbang_controls_{backend_name}_{safe_title[:10]}.txt"
                file_path = os.path.join(os.getcwd(), file_name)
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(output)
                print(f"    -> UI 구조 분석 결과를 저장했습니다: {file_name}")
        
        if not found:
            print("현재 열려있는 '한방' 또는 '확인설명서' 관련 창을 찾지 못했습니다.")
            
    except Exception as e:
        print(f"Backend {backend_name} 스캔 실패: {e}")

if __name__ == "__main__":
    print("한방 프로그램 UI 분석을 시작합니다...")
    scan_windows('win32')
    scan_windows('uia')
    print("\n분석 완료.")
