import sys
# Make sure we import our trade_viewer
from trade_viewer import run_trade_viewer, get_kakao_address_info

addr_info = get_kakao_address_info("성산동 200-94")
if addr_info:
    # Run the trade viewer using pre-resolved address
    run_trade_viewer(pre_address_info=addr_info, pre_prop_type='4')
else:
    print("Address resolution failed")
