import time
import pyautogui
import pyperclip
import keyboard
import sys

def read_contract_fields():
    fields = [
        "소재지", "동", "호", "토지 지목", "토지 면적", 
        "건물 구조", "건물 용도", "건물 면적", "임대할 부분", "임대 면적"
    ]
    extracted_data = {}
    
    print("\n[+] 계약서 데이터 추출을 시작합니다. 마우스에서 손을 떼세요!")
    
    # 윈도우 포커스를 위한 짧은 대기
    time.sleep(0.2)
    
    for i, field_name in enumerate(fields):
        # 1. 클립보드 초기화 (빈 칸일 경우를 대비)
        pyperclip.copy("")
        
        # 2. 전체 선택(Ctrl+A) 후 복사(Ctrl+C)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.05)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.1) # 복사될 시간 확보
        
        # 3. 클립보드에서 텍스트 가져오기
        text = pyperclip.paste().strip()
        extracted_data[field_name] = text
        print(f"[+] [{field_name}]: {text}")
        
        # 4. 마지막 항목이 아니면 Tab 키를 눌러 다음 칸으로 이동
        if i < len(fields) - 1:
            pyautogui.press('tab')
            time.sleep(0.1) # 다음 칸으로 이동할 시간 확보
            
    print("\n[!] 추출 완료! 파이썬이 데이터를 모두 기억했습니다.")
    print("="*50)

def main():
    print("="*50)
    print("[+] 한방 계약서 자동 읽기 봇 대기 중...")
    print("사용법:")
    print("1. 한방 프로그램 계약서의 '소재지' 입력칸을 클릭하여 깜빡이게 만드세요.")
    print("2. 키보드에서 'F3' 키를 누르세요.")
    print("3. 눈 깜짝할 사이에 봇이 데이터를 훔쳐(?)옵니다!")
    print("종료하려면 'ESC' 키를 누르세요.")
    print("="*50)
    
    # F3 키를 누르면 read_contract_fields 함수 실행
    keyboard.add_hotkey('f3', read_contract_fields)
    
    # ESC 키를 누를 때까지 무한 대기
    keyboard.wait('esc')
    print("프로그램을 종료합니다.")

if __name__ == "__main__":
    main()
