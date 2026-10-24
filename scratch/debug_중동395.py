import sys
import json
import trade_viewer

def main():
    address = "마포구 중동 395"
    addr_no_ho, dong, ho = trade_viewer.parse_address_and_ho(address)
    print(f"Parsed: addr={addr_no_ho}, dong={dong}, ho={ho}")
    
    addr_info = trade_viewer.get_kakao_address_info(addr_no_ho)
    if not addr_info:
        print("Address info not found.")
        return
        
    print(f"Address info: {json.dumps(addr_info, ensure_ascii=False)}")
    
    sigunguCd = addr_info['sigunguCd']
    bjdong_nm = addr_info['bjdongNm']
    main_no = addr_info['bun']
    sub_no = addr_info['ji']
        
    print(f"sigunguCd={sigunguCd}, bjdong_nm={bjdong_nm}, main_no={main_no}, sub_no={sub_no}")
    
    for prop_type in ["1", "2", "3", "4"]:
        print(f"Fetching transactions for prop_type={prop_type}...")
        try:
            transactions = trade_viewer.get_recent_transactions(sigunguCd, main_no, sub_no, prop_type, bjdong_nm)
            print(f"Found {len(transactions) if transactions else 0} transactions.")
            if transactions:
                print(f"Sample: {transactions[0]}")
        except Exception as e:
            print(f"Error fetching: {e}")

if __name__ == '__main__':
    main()
