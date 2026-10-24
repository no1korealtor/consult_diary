with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_logic = '''    trade_amts = []
    
    for item in subset:
        if is_wolse:
            _, dep, mon = format_price(item, is_rent=True)
            amt = (dep or 0) + (mon or 0) * 100
        else:
            _, amt, _ = format_price(item, is_rent=is_rent)
            
        if not amt:
            continue
        trade_amts.append(amt)'''

new_logic = '''    trade_list = []
    
    for item in subset:
        if is_wolse:
            _, dep, mon = format_price(item, is_rent=True)
            amt = (dep or 0) + (mon or 0) * 100
        else:
            _, amt, _ = format_price(item, is_rent=is_rent)
            
        if not amt:
            continue
            
        apt_nm = (item.get("aptNm") or item.get("mhouseNm") or "").strip()
        trade_list.append({"amt": amt, "apt_nm": apt_nm})'''

content = content.replace(old_logic, new_logic)

old_stats = '''    if not trade_amts:
        return None
        
    min_amt = min(trade_amts)
    max_amt = max(trade_amts)
    avg_amt = sum(trade_amts) / len(trade_amts)
    
    def local_format(val):
        if val >= 10_000:
            eok = int(val // 10_000)
            man = int(val % 10_000)
            if man > 0:
                return f"{eok}억 {man:,}만"
            return f"{eok}억"
        return f"{int(val):,}만"
        
    price_range = f"{local_format(min_amt)} ~ {local_format(max_amt)}" if min_amt != max_amt else local_format(min_amt)'''

new_stats = '''    if not trade_list:
        return None
        
    min_item = min(trade_list, key=lambda x: x["amt"])
    max_item = max(trade_list, key=lambda x: x["amt"])
    avg_amt = sum(x["amt"] for x in trade_list) / len(trade_list)
    
    def local_format(val):
        if val >= 10_000:
            eok = int(val // 10_000)
            man = int(val % 10_000)
            if man > 0:
                return f"{eok}억 {man:,}만"
            return f"{eok}억"
        return f"{int(val):,}만"
        
    def format_with_apt(item_data):
        p_str = local_format(item_data["amt"])
        apt = item_data["apt_nm"]
        if apt:
            short_apt = apt if len(apt) <= 7 else apt[:6] + ".."
            return f"{p_str}({short_apt})"
        return p_str
        
    if min_item["amt"] != max_item["amt"]:
        price_range = f"{format_with_apt(min_item)} ~ {format_with_apt(max_item)}"
    else:
        price_range = format_with_apt(min_item)'''

content = content.replace(old_stats, new_stats)

content = content.replace('len(trade_amts)', 'len(trade_list)')

with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(content)
