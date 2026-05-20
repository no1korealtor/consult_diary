import urllib.request
import json
import traceback

url = "https://yqolkvmrfvumpwlxjimp.supabase.co/rest/v1/"
headers = {
    "apikey": "sb_publishable_Y3waCN-Y0LA26BC80eUO-g_Njmuq1Hu",
    "Authorization": "Bearer sb_publishable_Y3waCN-Y0LA26BC80eUO-g_Njmuq1Hu",
    "Content-Type": "application/json"
}

try:
    # Get properties
    req_p = urllib.request.Request(url + "properties?select=*", headers=headers)
    with urllib.request.urlopen(req_p) as res:
        properties = json.loads(res.read().decode())
    
    # Get clients
    req_c = urllib.request.Request(url + "clients?select=*", headers=headers)
    with urllib.request.urlopen(req_c) as res:
        clients = json.loads(res.read().decode())

    with open("debug_output.txt", "w", encoding="utf-8") as f:
        target_p = next((p for p in properties if p.get('deposit') == 1000 and p.get('monthly_rent') == 40), None)
        target_c = next((c for c in clients if c.get('client_phone') == '010-2940-6428'), None)
        
        f.write("=== TARGET PROPERTY ===\n")
        f.write(json.dumps(target_p, ensure_ascii=False, indent=2) if target_p else "NOT FOUND\n")
        f.write("\n=== TARGET CLIENT ===\n")
        f.write(json.dumps(target_c, ensure_ascii=False, indent=2) if target_c else "NOT FOUND\n")

    print("DONE! Check debug_output.txt")
except Exception as e:
    with open("debug_output.txt", "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())
    print("FAILED! Check debug_output.txt")
