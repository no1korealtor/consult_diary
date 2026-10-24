import re

def patch_get_price_range(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    old_block = """        def get_price_range(subset):
            prices = []
            for item in subset:
                val = str(item.get('dealAmount', '') or item.get('rowPrice', '') or item.get('deposit', '') or item.get('guaranteeAmt', '')).strip().replace(',', '')
                if val:
                    try:
                        prices.append(float(val))
                    except:
                        pass
            if not prices: return None
            min_p = min(prices)
            max_p = max(prices)
            if min_p == max_p: return local_format_price(min_p)
            return f"{local_format_price(min_p)} ~ {local_format_price(max_p)}"
            
        trade_str = get_price_range(trades)
        jeonse_str = get_price_range(jeonses)"""

    new_block = """        
        trade_str = get_price_range(trades) if 'get_price_range' in locals() or 'get_price_range' in globals() else None
        jeonse_str = get_price_range(jeonses) if 'get_price_range' in locals() or 'get_price_range' in globals() else None"""
        
    # Let's just define get_price_range before the loop.
    # Where does the loop start?
    # for label, txs, prop_type in [("🏢 아파트 (최근 24개월 기준)", filtered_apt_txs, '1')]:
    
    definition = """
    def get_price_range(subset):
        prices = []
        for item in subset:
            val = str(item.get('dealAmount', '') or item.get('rowPrice', '') or item.get('deposit', '') or item.get('guaranteeAmt', '')).strip().replace(',', '')
            if val:
                try:
                    prices.append(float(val))
                except:
                    pass
        if not prices: return None
        min_p = min(prices)
        max_p = max(prices)
        if min_p == max_p: return local_format_price(min_p)
        return f"{local_format_price(min_p)} ~ {local_format_price(max_p)}"
"""
    # Insert it before the first loop
    content = content.replace(
        '    # 1. Main sections',
        definition + '\n    # 1. Main sections'
    )
    
    # And remove the nested definition
    nested_def = """        def get_price_range(subset):
            prices = []
            for item in subset:
                val = str(item.get('dealAmount', '') or item.get('rowPrice', '') or item.get('deposit', '') or item.get('guaranteeAmt', '')).strip().replace(',', '')
                if val:
                    try:
                        prices.append(float(val))
                    except:
                        pass
            if not prices: return None
            min_p = min(prices)
            max_p = max(prices)
            if min_p == max_p: return local_format_price(min_p)
            return f"{local_format_price(min_p)} ~ {local_format_price(max_p)}"
            """
    content = content.replace(nested_def, "")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed get_price_range scope issue")

if __name__ == "__main__":
    patch_get_price_range(r"d:\부동산업무\antigravity\AutoBot_Clean\market_analyser.py")
