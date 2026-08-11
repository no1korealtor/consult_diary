import json
from trade_viewer import get_recent_transactions, get_kakao_address_info

def main():
    addr = "마포구 중동 393"
    addr_info = get_kakao_address_info(addr)
    if not addr_info:
        print("주소 정보를 가져오는데 실패했습니다.")
        return
        
    print("주소 정보:", addr_info)
    
    # 아파트 (prop_type='1')
    txs = get_recent_transactions(
        addr_info['sigunguCd'], 
        addr_info['bun'], 
        addr_info['ji'], 
        '1', 
        bjdong_nm=addr_info.get('bjdongNm')
    )
    
    if txs is None:
        print("실거래 정보를 가져오는데 실패했습니다.")
        return
        
    print(f"총 {len(txs)}건의 실거래 정보를 찾았습니다.")
    for idx, t in enumerate(txs[:10]):
        print(f"[{idx+1}] {t.get('_trade_type')} {t.get('dealYear')}-{t.get('dealMonth')}-{t.get('dealDay')} / {t.get('excluUseAr')}㎡ / {t.get('dealAmount') or t.get('deposit') or t.get('monthlyRent')} / {t.get('floor')}층")

if __name__ == '__main__':
    main()
