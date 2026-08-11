from trade_viewer import run_trade_viewer, get_kakao_address_info
addr_info = get_kakao_address_info("성산동 200-94")
if addr_info:
    run_trade_viewer(pre_address_info=addr_info, pre_prop_type='1')
else:
    print("Failed to resolve address")
