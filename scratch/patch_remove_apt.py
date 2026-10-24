import os

def patch_remove_apt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    old_fetch_apt = """            apt_res = get_recent_transactions(sigunguCd, '', '', '1', bjdong_nm=tdong, expand_similar=True)
            if apt_res is None:
                has_auth_error = True
            else:
                apt_txs.extend(apt_res)
                if getattr(apt_res, "connection_timeout_error", False):
                    has_timeout = True
                if getattr(apt_res, "trade_permission_error", False) or getattr(apt_res, "rent_permission_error", False):
                    has_auth_error = True"""
                    
    new_fetch_apt = """            # [업데이트] 아파트 실거래가 수집은 생략 (개별 단지 조회 기능으로 이관)"""
    
    if old_fetch_apt in content:
        content = content.replace(old_fetch_apt, new_fetch_apt)
        
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Apartment fetching completely removed from market_analyser.py")

if __name__ == "__main__":
    patch_remove_apt(r"d:\부동산업무\antigravity\AutoBot_Clean\market_analyser.py")
