from building_viewer import get_kakao_address_info, get_building_title_info
import sys

def main():
    addr = "부천 중동 393"
    info = get_kakao_address_info(addr)
    if not info:
        print("Address failed")
        return
    print(info)
    
    b_code = info['b_code']
    sigungu = b_code[:5]
    bjdong = b_code[5:]
    h_code = info['h_code']
    bun = info['bun'].zfill(4)
    ji = info['ji'].zfill(4)
    
    res = get_building_title_info(sigungu, bjdong, bun, ji)
    if res:
        for item in res:
            print("bldNm:", item.get("bldNm"), "mainPurps:", item.get("mainPurpsCdNm"), "etcPurps:", item.get("etcPurps"), "hhldCnt:", item.get("hhldCnt"))
    else:
        print("No building title info")

if __name__ == "__main__":
    main()
