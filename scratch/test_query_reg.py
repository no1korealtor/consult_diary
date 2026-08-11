from building_viewer import get_kakao_address_info, get_vworld_land_use_info

addr_info = get_kakao_address_info("성산동 200-94")
if addr_info:
    vworld_key = "80194C85-0EE3-3220-A3C1-3268AD8756B9"
    bun_val = str(addr_info['bun']).zfill(4) if addr_info['bun'] else "0000"
    ji_val = str(addr_info['ji']).zfill(4) if addr_info['ji'] else "0000"
    pnu = f"{addr_info['sigunguCd']}{addr_info['bjdongCd']}1{bun_val}{ji_val}"
    
    print("PNU:", pnu)
    reg_info = get_vworld_land_use_info(vworld_key, pnu, addr_info['sigunguCd'])
    print("Regulation Info:")
    for k, v in reg_info.items():
        print(f"  {k}: {v}")
else:
    print("Address not found")
