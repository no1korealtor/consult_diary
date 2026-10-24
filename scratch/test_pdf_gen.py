import sys; sys.path.append('.')
from trade_viewer import get_kakao_address_info, parse_address_and_ho, match_dong, classify_property_type, get_recent_transactions, print_comparison_table

transactions = get_recent_transactions('11440', '0393', '0000', '1', '중동', None, None)
print('Count:', len(transactions))
try:
    print_comparison_table(transactions, '1', 0, 0, '서울 마포구 성암로 41', sigunguCd='11440', bun='0393', ji='0000', bjdong_nm='중동', target_build_year=None, target_house_type=None, save_report=True)
except Exception as e:
    import traceback
    traceback.print_exc()
