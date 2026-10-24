import re

with open('d:/부동산업무/antigravity/consult_diary/trade_viewer.py', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = re.compile(
    r'(\s+)if expand_choice == "1":\s+print\(" -> 인근 유사 매물 데이터 수집 중 \(엄격한 기준: 준공년도 ±3년, 전용면적 ±15%\)\.\.\."\)\s+expanded_txs = get_recent_transactions\((.*?)\)\s+if expand_choice == "2":'
)
replacement = r'''\1if expand_choice == "1":
\1    print(" -> 인근 유사 매물 데이터 수집 중 (엄격한 기준: 준공년도 ±3년, 전용면적 ±15%)...")
\1    expanded_txs = get_recent_transactions(\2)
\1    if expanded_txs:
\1        transactions = expanded_txs
\1        is_expanded = True
\1        expansion_mode = "strict"
\1        print(f" -> 엄격한 기준의 유사 매물 {len(transactions)}건을 발견하여 분석을 진행합니다.")
\1    else:
\1        print(" -> 엄격한 기준에 부합하는 인근 매물이 없어 해당 지번의 데이터로만 분석합니다.")
\1if expand_choice == "2":'''

content = pattern.sub(replacement, content)

with open('d:/부동산업무/antigravity/consult_diary/trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(content)
