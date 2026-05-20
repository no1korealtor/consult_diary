import urllib.request
import json

url = "https://yqolkvmrfvumpwlxjimp.supabase.co/rest/v1/"
headers = {
    "apikey": "sb_publishable_Y3waCN-Y0LA26BC80eUO-g_Njmuq1Hu",
    "Authorization": "Bearer sb_publishable_Y3waCN-Y0LA26BC80eUO-g_Njmuq1Hu"
}

def get_data(table):
    req = urllib.request.Request(url + table, headers=headers)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

properties = get_data("properties?select=*")
clients = get_data("clients?select=*")

def is_match(p, c):
    if p.get('status') != '거래가능': return False
    if c.get('status') != '탐색중': return False
    
    p_types = p.get('deal_types') or []
    c_types = c.get('target_types') or []
    if not p_types or not c_types: return False
    
    type_match = any(pt in c_types for pt in p_types)
    if not type_match: return False
    
    is_budget_ok = False
    p_sale = p.get('sale_price') or 0
    p_dep = p.get('deposit') or 0
    p_rent = p.get('monthly_rent') or 0
    
    c_budget = c.get('max_budget') or 9999999
    c_max_monthly = c.get('max_monthly')
    flex_rent = c_max_monthly + 10 if c_max_monthly else 9999999
    
    if '매매' in c_types and '매매' in p_types:
        if p_sale > 0 and p_sale <= c_budget: is_budget_ok = True
    if '전세' in c_types and '전세' in p_types:
        if p_dep > 0 and p_rent == 0 and p_dep <= c_budget: is_budget_ok = True
    if '월세' in c_types and '월세' in p_types:
        if p_dep <= c_budget and p_rent > 0 and p_rent <= flex_rent: is_budget_ok = True
        
    if not is_budget_ok: return False
    
    p_room = p.get('room_count')
    c_room = c.get('min_room_count')
    if c_room and p_room and p_room < c_room - 1: return False
    
    if c.get('need_pet') and not p.get('pet_allowed'): return False
    if c.get('need_parking') and not p.get('parking_allowed'): return False
    if c.get('need_loan') and not p.get('loan_allowed'): return False
    if c.get('need_lh_sh') and not p.get('lh_sh_allowed'): return False
    if c.get('need_exclude_basement') and p.get('is_basement'): return False
    
    if p.get('occupancy_type') == '입주불가(세안고)' and c.get('occupancy_type') != '무관': return False
    
    return True

print(f"Total properties: {len(properties)}, Total clients: {len(clients)}")

target_property = None
for p in properties:
    if p.get('deposit') == 1000 and p.get('monthly_rent') == 40:
        target_property = p
        break

target_client = None
for c in clients:
    if c.get('client_phone') == '010-2940-6428':
        target_client = c
        break

if target_property and target_client:
    print("Found Property:", target_property.get('address'), target_property.get('deposit'), target_property.get('monthly_rent'))
    print("Found Client:", target_client.get('client_phone'), target_client.get('max_budget'), target_client.get('max_monthly'))
    print("MATCH RESULT:", is_match(target_property, target_client))
    
    # Trace logic
    p = target_property
    c = target_client
    print(f"p.status: {p.get('status')} == '거래가능' -> {p.get('status') == '거래가능'}")
    print(f"c.status: {c.get('status')} == '탐색중' -> {c.get('status') == '탐색중'}")
    print(f"deal_types match: {any(pt in (c.get('target_types') or []) for pt in (p.get('deal_types') or []))}")
    print(f"budget match: {p.get('deposit')} <= {c.get('max_budget')} AND {p.get('monthly_rent')} <= {c.get('max_monthly') + 10 if c.get('max_monthly') else 9999999}")
    print(f"room match: p_room={p.get('room_count')}, c_room={c.get('min_room_count')}")
else:
    print("Could not find property or client.")
