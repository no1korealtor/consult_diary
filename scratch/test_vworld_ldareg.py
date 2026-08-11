import urllib.request
import json
import re

vworld_key = "80194C85-0EE3-3220-A3C1-3268AD8756B9"
pnu = "1144012500101640000"

def get_vworld_land_share(vworld_key, pnu, dong_name, ho_name):
    def match_part(target, item):
        if not target:
            return True
        if not item:
            return False
        t_str = str(target).strip().lower()
        i_str = str(item).strip().lower()
        if t_str == i_str:
            return True
        t_clean = t_str.replace('호', '').replace('동', '')
        i_clean = i_str.replace('호', '').replace('동', '')
        if t_clean == i_clean:
            return True
        t_num = re.sub(r'[^0-9]', '', t_clean)
        i_num = re.sub(r'[^0-9]', '', i_clean)
        if t_num and i_num:
            try:
                if int(t_num) == int(i_num):
                    return True
            except:
                pass
        return False

    url = f"http://api.vworld.kr/ned/data/ldaregList?key={vworld_key}&domain=http://localhost&pnu={pnu}&format=json&numOfRows=1000&pageNo=1"
    try:
        req = urllib.request.Request(url)
        req.add_header("Referer", "http://localhost")
        res = urllib.request.urlopen(req)
        data = json.loads(res.read().decode('utf-8'))
        
        items = data.get('ldaregVOList', {}).get('ldaregVOList', [])
        if not items:
            items = data.get('response', {}).get('ldaregVOList', [])
            
        for item in items:
            i_dong = str(item.get('buldDongNm', ''))
            i_ho = str(item.get('buldHoNm', ''))
            
            dong_match = match_part(dong_name, i_dong)
            ho_match = match_part(ho_name, i_ho)
            
            if dong_match and ho_match:
                rate = item.get('ldaQotaRate', '')
                if rate and '/' in rate:
                    return rate.split('/')[0].strip()
                return rate
    except Exception as e:
        print(f" -> [VWorld 에러] {e}")
    return ""

share = get_vworld_land_share(vworld_key, pnu, "", "지층2호")
print(f"Matched share for '지층2호': {share}")
