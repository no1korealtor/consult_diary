import sys
import os

def make_headless(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Address input
    content = content.replace(
        'address = input("\\n[입력] 조회할 주소: ").strip()',
        'address = sys.argv[1] if len(sys.argv) > 1 else input("\\n[입력] 조회할 주소: ").strip()'
    )
    
    # 2. Expand choice
    content = content.replace(
        'expand_choice = input("[입력] 분석 범위를 선택하세요 (1: 엄격한 기준 | 2: 넓은 기준 | 3: 미확장) [기본값: 1]: ").strip()',
        'expand_choice = "1" if len(sys.argv) > 1 else input("[입력] 분석 범위를 선택하세요 (1: 엄격한 기준 | 2: 넓은 기준 | 3: 미확장) [기본값: 1]: ").strip()'
    )
    
    # 3. User choice (period)
    content = content.replace(
        'user_choice = input("[입력] 분석 대상 기간을 선택하세요 (1: 6개월 | 2: 1년 | 3: 2년): ").strip()',
        'user_choice = "2" if len(sys.argv) > 1 else input("[입력] 분석 대상 기간을 선택하세요 (1: 6개월 | 2: 1년 | 3: 2년): ").strip()'
    )
    
    # 4. Exit prompt
    content = content.replace(
        'input("\\n메뉴로 돌아가려면 엔터를 누르세요...")',
        'if len(sys.argv) <= 1: input("\\n메뉴로 돌아가려면 엔터를 누르세요...")'
    )
    
    # 5. Break __main__ loop
    content = content.replace(
        'run_trade_viewer(None, None, None, None)',
        'run_trade_viewer(None, None, None, None)\n                if len(sys.argv) > 1: break'
    )
    content = content.replace(
        'run_building_viewer(None, None)',
        'run_building_viewer(None, None)\n                if len(sys.argv) > 1: break'
    )

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'{file_path} made headless')

make_headless(r'd:\부동산업무\antigravity\consult_diary\trade_viewer.py')
make_headless(r'd:\부동산업무\antigravity\consult_diary\building_viewer.py')
