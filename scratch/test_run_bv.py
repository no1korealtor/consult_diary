import sys
import building_viewer
import time

def mock_input(prompt):
    print("MOCK INPUT PROMPT:", prompt)
    if "건물 주소" in prompt: return "마포구 중동 395"
    if "동 이름" in prompt: return ""
    if "호수" in prompt: return ""
    if "매매, 전세, 월세" in prompt: return "매매"
    if "의뢰인 전화번호" in prompt: return ""
    if "희망가" in prompt: return "10000"
    if "범위를 선택하세요" in prompt: return "3"  # 미확장
    if "기간을 선택" in prompt: return "3"  # 24개월
    if "자동 등록" in prompt: return "n"
    if "계속하시려면" in prompt:
        sys.exit(0)
    return "3"

building_viewer.input = mock_input

try:
    building_viewer.run_building_viewer()
except SystemExit:
    pass
except Exception as e:
    print(f"Error: {e}")
