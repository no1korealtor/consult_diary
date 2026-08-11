import os

with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Fix while loops
text = text.replace('while prop_type_name == "아파트" and apt_groups:', 'if prop_type_name == "아파트" and apt_groups:')
text = text.replace('while insights:', 'if insights:')
text = text.replace('while sigunguCd and bjdong_nm:', 'if sigunguCd and bjdong_nm:')

# 2. Fix get_avg_display missing is_wolse=False
text = text.replace('def get_avg_display(items, is_rent, is_wolse):', 'def get_avg_display(items, is_rent, is_wolse=False):')
text = text.replace('def get_avg_display(subset, is_rent, is_wolse):', 'def get_avg_display(subset, is_rent, is_wolse=False):')

# 3. Fix get_numeric_averages missing is_wolse=False
text = text.replace('def get_numeric_averages(subset, is_rent, is_wolse):', 'def get_numeric_averages(subset, is_rent, is_wolse=False):')
text = text.replace('def get_numeric_averages(subset, is_rent, is_wolse):\n', 'def get_numeric_averages(subset, is_rent, is_wolse=False):\n')

# 4. Fix build_summary_table missing is_wolse=False
text = text.replace('def build_summary_table(section_title, items, is_rent, is_wolse):', 'def build_summary_table(section_title, items, is_rent, is_wolse=False):')

# 5. Fix pdf_title decompiled ternary
text = text.replace('pdf_title = is_expanded and "인근 유사 매물 실거래 시세 브리핑"', 'pdf_title = f"{masked_address} 인근 유사 매물 실거래 시세 브리핑" if is_expanded else f"{masked_address} 인근 실거래 시세 브리핑"')

# 6. Fix suffix decompiled ternary
text = text.replace('suffix = is_wolse and ""', 'suffix = "/월" if is_wolse else ""')

with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(text)

with open('test_briefing_integration.py', 'r', encoding='utf-8') as f:
    text = f.read()
text = text.replace('safe_addr = "서울중구신당동395"', 'safe_addr = "서울특별시마포구중동395"')
text = text.replace('safe_addr = "서울_중구_신당동_395"', 'safe_addr = "서울특별시마포구중동395"')
text = text.replace('safe_addr = "서울_중구_신당동_3**"', 'safe_addr = "서울특별시마포구중동395"')
with open('test_briefing_integration.py', 'w', encoding='utf-8') as f:
    f.write(text)
