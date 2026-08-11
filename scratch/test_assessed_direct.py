import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from building_viewer import (
    get_vworld_land_price,
    get_vworld_individual_house_price,
    get_vworld_apartment_house_price,
    format_assessed_price
)

vworld_key = "80194C85-0EE3-3220-A3C1-3268AD8756B9"

def run_test():
    # 1. 성산동 200-94 (일반/단독주택)
    pnu_single = "1144012500102000094"
    print("=== 성산동 200-94 (개별공시지가 & 개별주택가격) ===")
    land_price = get_vworld_land_price(vworld_key, pnu_single)
    if land_price:
        p_m2 = land_price["price"]
        p_py = round(p_m2 / 0.3025)
        print(f"  • 공시지가  : {land_price['year']}년 기준 ㎡당 {p_m2:,}원 (평당 약 {p_py:,}원)")
    else:
        print("  • 공시지가 조회 실패")
        
    indiv_price = get_vworld_individual_house_price(vworld_key, pnu_single)
    if indiv_price:
        formatted = format_assessed_price(indiv_price["price"])
        print(f"  • 주택공시가격: {indiv_price['year']}년 기준 {formatted}")
    else:
        print("  • 개별주택가격 조회 실패")
        
    # 2. 성산동 164 (집합건축물 지층2호)
    pnu_multi = "1144012500101640000"
    print("\n=== 성산동 164 지층2호 (공동주택가격) ===")
    apt_price = get_vworld_apartment_house_price(vworld_key, pnu_multi, "", "지층2호")
    if apt_price:
        formatted = format_assessed_price(apt_price["price"])
        print(f"  • 공동주택가격: {apt_price['year']}년 기준 {formatted}")
    else:
        print("  • 공동주택가격 조회 실패")

if __name__ == "__main__":
    run_test()
