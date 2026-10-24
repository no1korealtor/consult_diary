import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET
import re
import time

API_KEY = "88ec4e85897c086c4c9438db67c35f2bc10d730913b9ba6be67a9ea755e70770"

def get_building_data(sigungu, bjdong, bun, ji, plat_code=None):
    bun_pad = str(bun).strip().zfill(4)
    ji_pad = str(ji).strip().zfill(4)
    sigungu = str(sigungu).strip()
    bjdong = str(bjdong).strip()
    
    # 대지구분 최적화: PNU 기반 지정 시 핀포인트 조회, 미지정 시 일반대지(0) 우선 조회
    if plat_code is not None and str(plat_code) in ['0', '1', '2']:
        plat_list = [int(plat_code)]
    else:
        plat_list = [0, 1, 2]

    recap_item = None
    title_items = []
    url_title = "http://apis.data.go.kr/1613000/BldRgstHubService/getBrTitleInfo"
    url_recap = "http://apis.data.go.kr/1613000/BldRgstHubService/getBrRecapTitleInfo"

    # 1. 일반/동별 표제부 (getBrTitleInfo) 우선 조회 (다세대, 빌라, 단독은 표제부에 즉시 데이터 존재!)
    for plat in plat_list:
        query = f"?serviceKey={API_KEY}&sigunguCd={sigungu}&bjdongCd={bjdong}&platGbCd={plat}&bun={bun_pad}&ji={ji_pad}&numOfRows=100&pageNo=1&_type=json"
        for attempt in range(2):
            try:
                req = urllib.request.Request(url_title + query)
                req.add_header("User-Agent", "Mozilla/5.0")
                req.add_header("Accept", "application/json, text/plain, */*")
                with urllib.request.urlopen(req, timeout=10) as response:
                    res_text = response.read().decode('utf-8')
                    if not res_text.strip(): continue
                    json_data = json.loads(res_text)
                    if json_data.get('response', {}).get('header', {}).get('resultCode') == '00':
                        items = json_data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
                        if isinstance(items, dict): items = [items]
                        if items:
                            title_items = items
                            break
                if title_items:
                    break
            except Exception:
                time.sleep(0.3)
        if title_items:
            break

    # 2. 총괄표제부 (getBrRecapTitleInfo) 조회: 표제부가 없거나 대단지 복수 동인 경우에만 선택적 조회
    need_recap = False
    if not title_items:
        need_recap = True
    elif len(title_items) > 1:
        need_recap = True

    if need_recap:
        for plat in plat_list:
            query = f"?serviceKey={API_KEY}&sigunguCd={sigungu}&bjdongCd={bjdong}&platGbCd={plat}&bun={bun_pad}&ji={ji_pad}&numOfRows=10&pageNo=1&_type=json"
            for attempt in range(2):
                try:
                    req = urllib.request.Request(url_recap + query)
                    req.add_header("User-Agent", "Mozilla/5.0")
                    req.add_header("Accept", "application/json, text/plain, */*")
                    with urllib.request.urlopen(req, timeout=10) as response:
                        res_text = response.read().decode('utf-8')
                        if not res_text.strip(): continue
                        json_data = json.loads(res_text)
                        if json_data.get('response', {}).get('header', {}).get('resultCode') == '00':
                            items = json_data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
                            if isinstance(items, dict): items = [items]
                            if items:
                                it = items[0]
                                tot_ar = float(it.get('totArea', 0) or 0)
                                hh = int(it.get('hhldCnt', 0) or 0)
                                ar_ar = float(it.get('archArea', 0) or 0)
                                if tot_ar > 0 or hh > 0 or ar_ar > 0:
                                    recap_item = it
                                    break
                    if recap_item:
                        break
                except Exception:
                    time.sleep(0.3)
            if recap_item:
                break

    if not recap_item and not title_items:
        return None

    building_info = {}

    if recap_item:
        # --- A. 총괄표제부 기반 데이터 구성 ---
        building_info['bldNm'] = recap_item.get('bldNm', '') or ''
        building_info['platArea'] = str(recap_item.get('platArea', 0) or 0)
        building_info['archArea'] = str(recap_item.get('archArea', 0) or 0)
        building_info['totArea'] = str(recap_item.get('totArea', 0) or 0)
        building_info['bcRat'] = str(recap_item.get('bcRat', '') or '')
        building_info['vlRat'] = str(recap_item.get('vlRat', '') or '')
        
        hhld = int(recap_item.get('hhldCnt', 0) or 0)
        fmly = int(recap_item.get('fmlyCnt', 0) or 0)
        building_info['households'] = str(max(hhld, fmly))
        
        building_info['purpose'] = recap_item.get('mainPurpsCdNm', '') or ''
        building_info['etcPurps'] = recap_item.get('etcPurps', '') or ''
        building_info['regstrGbCd'] = str(recap_item.get('regstrGbCd', '')).strip()
        building_info['regstrGbCdNm'] = str(recap_item.get('regstrGbCdNm', '')).strip()
        
        # 총 주차대수 (totPkngCnt 우선, 없으면 세부 주차대수 합산)
        pk = int(recap_item.get('totPkngCnt', 0) or 0)
        if pk == 0:
            for p_type in ['indrAutoUtcnt', 'indrMechUtcnt', 'oudrAutoUtcnt', 'oudrMechUtcnt']:
                val = recap_item.get(p_type, 0)
                if val:
                    try: pk += int(val)
                    except: pass
        if pk == 0 and title_items:
            for it in title_items:
                for p_type in ['indrAutoUtcnt', 'indrMechUtcnt', 'oudrAutoUtcnt', 'oudrMechUtcnt']:
                    val = it.get(p_type, 0)
                    if val:
                        try: pk += int(val)
                        except: pass
        building_info['totalParking'] = str(pk)
        building_info['canPark'] = 'Y' if pk > 0 else 'N'

        apr = str(recap_item.get('useAprDay', '') or '')
        building_info['useAprDay'] = apr

        # 표제부에서 구조, 층수, 승강기, 위반여부 보완
        if title_items:
            main_titles = [it for it in title_items if '주건축물' in str(it.get('mainAtchGbCdNm', '')) or float(it.get('totArea', 0) or 0) > 300]
            rep_title = main_titles[0] if main_titles else title_items[0]
            
            building_info['strctCdNm'] = rep_title.get('strctCdNm', '') or rep_title.get('etcStrct', '') or ''
            if not building_info['purpose']:
                building_info['purpose'] = rep_title.get('mainPurpsCdNm', '') or ''
            if not building_info['useAprDay']:
                building_info['useAprDay'] = str(rep_title.get('useAprDay', '') or '')
                
            grnd = max([int(it.get('grndFlrCnt', 0) or 0) for it in title_items] + [0])
            ugrnd = max([int(it.get('ugrndFlrCnt', 0) or 0) for it in title_items] + [0])
            building_info['grndFlrCnt'] = str(grnd)
            building_info['ugrndFlrCnt'] = str(ugrnd)
            
            ride_elvt = sum(int(it.get('rideUseElvtCnt', 0) or 0) for it in title_items)
            emgen_elvt = sum(int(it.get('emgenUseElvtCnt', 0) or 0) for it in title_items)
            building_info['rideUseElvtCnt'] = str(ride_elvt)
            building_info['emgenUseElvtCnt'] = str(emgen_elvt)
            
            has_viol = any(str(it.get('violBldYn', 'N')).strip() == 'Y' for it in title_items)
            building_info['violBldYn'] = 'Y' if has_viol else 'N'
        else:
            building_info['strctCdNm'] = ''
            building_info['grndFlrCnt'] = '0'
            building_info['ugrndFlrCnt'] = '0'
            building_info['rideUseElvtCnt'] = '0'
            building_info['emgenUseElvtCnt'] = '0'
            building_info['violBldYn'] = 'N'

    else:
        # --- B. 일반/집합 표제부 기반 데이터 구성 ---
        main_titles = [it for it in title_items if str(it.get('mainAtchGbCdNm', '')) != '부속건축물']
        if not main_titles: main_titles = title_items
        rep_title = max(main_titles, key=lambda x: float(x.get('totArea', 0) or 0))
        
        building_info['bldNm'] = rep_title.get('bldNm', '') or ''
        building_info['purpose'] = rep_title.get('mainPurpsCdNm', '') or ''
        building_info['etcPurps'] = rep_title.get('etcPurps', '') or ''
        building_info['strctCdNm'] = rep_title.get('strctCdNm', '') or rep_title.get('etcStrct', '') or ''
        building_info['regstrGbCd'] = str(rep_title.get('regstrGbCd', '')).strip()
        building_info['regstrGbCdNm'] = str(rep_title.get('regstrGbCdNm', '')).strip()
        building_info['useAprDay'] = str(rep_title.get('useAprDay', '') or '')
        
        tot_area = sum(float(it.get('totArea', 0) or 0) for it in title_items)
        arch_area = sum(float(it.get('archArea', 0) or 0) for it in title_items)
        plat_area = max(float(it.get('platArea', 0) or 0) for it in title_items)
        
        building_info['totArea'] = str(tot_area)
        building_info['archArea'] = str(arch_area)
        building_info['platArea'] = str(plat_area)
        
        bc_rat = rep_title.get('bcRat', '')
        vl_rat = rep_title.get('vlRat', '')
        building_info['bcRat'] = str(bc_rat) if bc_rat else ''
        building_info['vlRat'] = str(vl_rat) if vl_rat else ''
        
        hhld = sum(max(int(it.get('hhldCnt', 0) or 0), int(it.get('fmlyCnt', 0) or 0)) for it in title_items)
        building_info['households'] = str(hhld)
        
        parking = 0
        for it in title_items:
            for p_type in ['indrAutoUtcnt', 'indrMechUtcnt', 'oudrAutoUtcnt', 'oudrMechUtcnt']:
                val = it.get(p_type, 0)
                if val:
                    try: parking += int(val)
                    except: pass
        building_info['totalParking'] = str(parking)
        building_info['canPark'] = 'Y' if parking > 0 else 'N'
        
        grnd = max([int(it.get('grndFlrCnt', 0) or 0) for it in title_items] + [0])
        ugrnd = max([int(it.get('ugrndFlrCnt', 0) or 0) for it in title_items] + [0])
        building_info['grndFlrCnt'] = str(grnd)
        building_info['ugrndFlrCnt'] = str(ugrnd)
        
        ride_elvt = sum(int(it.get('rideUseElvtCnt', 0) or 0) for it in title_items)
        emgen_elvt = sum(int(it.get('emgenUseElvtCnt', 0) or 0) for it in title_items)
        building_info['rideUseElvtCnt'] = str(ride_elvt)
        building_info['emgenUseElvtCnt'] = str(emgen_elvt)
        
        has_viol = any(str(it.get('violBldYn', 'N')).strip() == 'Y' for it in title_items)
        building_info['violBldYn'] = 'Y' if has_viol else 'N'

    apr = building_info.get('useAprDay', '')
    if apr and len(apr) == 8:
        building_info['aprYear'] = apr[:4]
        building_info['aprMonth'] = apr[4:6]
        building_info['aprDay'] = apr[6:8]
    else:
        building_info['aprYear'] = building_info['aprMonth'] = building_info['aprDay'] = ''
        
    return building_info


def get_basis_ouln_data(sigungu, bjdong, bun, ji):
    """총괄표제부 또는 표제부에서 주차대수를 조회합니다."""
    bun_pad = str(bun).strip().zfill(4)
    ji_pad = str(ji).strip().zfill(4)
    sigungu = str(sigungu).strip()
    bjdong = str(bjdong).strip()
    url_recap = "http://apis.data.go.kr/1613000/BldRgstHubService/getBrRecapTitleInfo"
    for plat in [0, 1, 2]:
        query = f"?serviceKey={API_KEY}&sigunguCd={sigungu}&bjdongCd={bjdong}&platGbCd={plat}&bun={bun_pad}&ji={ji_pad}&numOfRows=10&pageNo=1&_type=json"
        try:
            req = urllib.request.Request(url_recap + query)
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.getcode() == 200:
                    res_body = response.read().decode('utf-8')
                    if res_body.strip():
                        data = json.loads(res_body)
                        items = data.get("response", {}).get("body", {}).get("items", {})
                        if items:
                            item_list = items.get("item", [])
                            if isinstance(item_list, dict): item_list = [item_list]
                            if item_list:
                                pk = int(item_list[0].get('totPkngCnt', 0) or 0)
                                if pk > 0: return pk
                                pk_sum = 0
                                for p_type in ['indrAutoUtcnt', 'indrMechUtcnt', 'oudrAutoUtcnt', 'oudrMechUtcnt']:
                                    val = item_list[0].get(p_type, 0)
                                    if val: pk_sum += int(val)
                                if pk_sum > 0: return pk_sum
        except Exception:
            pass
    return 0

def get_expos_data(sigungu, bjdong, bun, ji, dong_name="", ho_name="", is_underground=False, plat_code=None):
    bun_pad = str(bun).strip().zfill(4)
    ji_pad = str(ji).strip().zfill(4)
    sigungu = str(sigungu).strip()
    bjdong = str(bjdong).strip()
    url_info = "http://apis.data.go.kr/1613000/BldRgstHubService/getBrExposInfo"
    url_area = "http://apis.data.go.kr/1613000/BldRgstHubService/getBrExposPubuseAreaInfo"
    
    result = {'area': '', 'supply_area': '', 'flrNo': '', 'violBldYn': '확인불가(정부서버오류)'}
    ho_clean = re.sub(r'[^\d]', '', str(ho_name)) if ho_name else ""
    
    if plat_code is not None and str(plat_code) in ['0', '1', '2']:
        plat_list = [int(plat_code)]
    else:
        plat_list = [0, 1, 2]
    
    for plat in plat_list:
        query = f"?serviceKey={API_KEY}&sigunguCd={sigungu}&bjdongCd={bjdong}&platGbCd={plat}&bun={bun_pad}&ji={ji_pad}&numOfRows=100&pageNo=1&_type=json"
        
        try:
            # 1. 층수 및 위반건축물 여부 조회 (getBrExposInfo)
            for attempt in range(2):
                try:
                    req_info = urllib.request.Request(url_info + query)
                    req_info.add_header('User-Agent', 'Mozilla/5.0')
                    req_info.add_header('Accept', 'application/json, text/plain, */*')
                    res_info = urllib.request.urlopen(req_info, timeout=10)
                    if res_info.getcode() == 200:
                        res_body = res_info.read().decode('utf-8')
                        if res_body.strip():
                            data = json.loads(res_body)
                            if data.get('response', {}).get('header', {}).get('resultCode') == '00':
                                items = data.get("response", {}).get("body", {}).get("items", {})
                                if items:
                                    item_list = items.get("item", [])
                                    if isinstance(item_list, dict): item_list = [item_list]
                                    
                                    matched_candidates = []
                                    for item in item_list:
                                        item_dong = str(item.get('dongNm') or '')
                                        item_ho = str(item.get('hoNm') or '')
                                        item_flr_no = item.get('flrNo')
                                        item_flr_gb = str(item.get('flrGbCdNm') or '')
                                        item_flr_nm = str(item.get('flrNoNm') or '')
                                        
                                        dong_match = (dong_name in item_dong) if dong_name else True
                                        if not dong_match:
                                            continue
                                            
                                        item_ho_clean = re.sub(r'[^\d]', '', item_ho)
                                        ho_match = False
                                        if ho_name:
                                            if str(ho_name) in item_ho or item_ho in str(ho_name):
                                                ho_match = True
                                            elif ho_clean and item_ho_clean and ho_clean == item_ho_clean:
                                                ho_match = True
                                        else:
                                            ho_match = True
                                            
                                        if ho_match:
                                            item_is_ug = (
                                                (item_flr_no is not None and str(item_flr_no).startswith('-')) or
                                                item_flr_gb == '지하' or
                                                '지하' in item_flr_nm or
                                                '지층' in item_flr_nm or
                                                '지하' in item_ho or
                                                '지층' in item_ho or
                                                'B' in item_ho.upper()
                                            )
                                            score = 0
                                            if is_underground == item_is_ug:
                                                score += 10
                                            if ho_clean and item_ho_clean == ho_clean:
                                                score += 5
                                            if ho_name and str(ho_name) == item_ho:
                                                score += 5
                                            matched_candidates.append((score, item))
                                            
                                    if matched_candidates:
                                        matched_candidates.sort(key=lambda x: x[0], reverse=True)
                                        best_item = matched_candidates[0][1]
                                        raw_flr = best_item.get('flrNo')
                                        best_flr_gb = str(best_item.get('flrGbCdNm') or '')
                                        best_flr_nm = str(best_item.get('flrNoNm') or '')
                                        best_ho = str(best_item.get('hoNm') or '')
                                        best_is_ug = (
                                            (raw_flr is not None and str(raw_flr).startswith('-')) or
                                            best_flr_gb == '지하' or
                                            '지하' in best_flr_nm or
                                            '지층' in best_flr_nm or
                                            '지하' in best_ho or
                                            '지층' in best_ho or
                                            'B' in best_ho.upper() or
                                            is_underground
                                        )
                                        if raw_flr is not None and str(raw_flr).strip():
                                            flr_str = str(raw_flr).strip()
                                            if best_is_ug and not flr_str.startswith('-'):
                                                result['flrNo'] = f"-{flr_str}"
                                            else:
                                                result['flrNo'] = flr_str
                                        elif best_is_ug:
                                            result['flrNo'] = "-1"
                                        else:
                                            result['flrNo'] = ""
                                        result['violBldYn'] = best_item.get('violBldYn', 'N')
                                break
                    break
                except Exception:
                    time.sleep(0.3)
            
            # 2. 전용면적 조회 (getBrExposPubuseAreaInfo)
            for attempt in range(2):
                try:
                    req_area = urllib.request.Request(url_area + query)
                    req_area.add_header('User-Agent', 'Mozilla/5.0')
                    req_area.add_header('Accept', 'application/json, text/plain, */*')
                    res_area = urllib.request.urlopen(req_area, timeout=10)
                    if res_area.getcode() == 200:
                        res_body = res_area.read().decode('utf-8')
                        if res_body.strip():
                            data = json.loads(res_body)
                            if data.get('response', {}).get('header', {}).get('resultCode') == '00':
                                items = data.get("response", {}).get("body", {}).get("items", {})
                                if items:
                                    item_list = items.get("item", [])
                                    if isinstance(item_list, dict): item_list = [item_list]
                                    
                                    matched_area_items = []
                                    for item in item_list:
                                        item_dong = str(item.get('dongNm') or '')
                                        item_ho = str(item.get('hoNm') or '')
                                        item_ho_clean = re.sub(r'[^\d]', '', item_ho)
                                        
                                        dong_match = (dong_name in item_dong) if dong_name else True
                                        if not dong_match:
                                            continue
                                            
                                        ho_match = False
                                        if ho_name:
                                            if str(ho_name) in item_ho or item_ho in str(ho_name):
                                                ho_match = True
                                            elif ho_clean and item_ho_clean and ho_clean == item_ho_clean:
                                                ho_match = True
                                        else:
                                            ho_match = True
                                            
                                        if ho_match:
                                            item_flr_gb = str(item.get('flrGbCdNm') or '')
                                            item_is_ug = (
                                                item_flr_gb == '지하' or
                                                '지하' in item_ho or 
                                                '지층' in item_ho or 
                                                'B' in item_ho.upper() or 
                                                '지하' in str(item.get('flrNoNm', '')) or
                                                '지층' in str(item.get('flrNoNm', '')) or
                                                str(item.get('flrNo', '')).startswith('-')
                                            )
                                            score = 0
                                            if is_underground == item_is_ug:
                                                score += 10
                                            if ho_clean and item_ho_clean == ho_clean:
                                                score += 5
                                            matched_area_items.append((score, item))
                                            
                                    if matched_area_items:
                                        max_score = max(x[0] for x in matched_area_items)
                                        top_items = [x[1] for x in matched_area_items if x[0] == max_score]
                                        area_exclusive = 0.0
                                        area_supply = 0.0
                                        for item in top_items:
                                            val = item.get('area')
                                            if val:
                                                f_val = float(val)
                                                area_supply += f_val
                                                if str(item.get('exposPubuseGbCd', '')) == '1':
                                                    area_exclusive += f_val
                                                    
                                        if area_supply > 0:
                                            result['area'] = str(round(area_exclusive, 2)) if area_exclusive > 0 else ''
                                            result['supply_area'] = str(round(area_supply, 2))
                                            break
                                break
                    break
                except Exception:
                    time.sleep(0.3)
                    
            if result['flrNo'] or result['area']:
                return result
                
        except Exception as e:
            continue
            
    print(f"전유부 API 호출 실패: 해당 주소에 전유부 데이터가 없습니다.")
    return None

def get_floor_data(sigungu, bjdong, bun, ji, floor_name):
    import urllib.request, json
    bun_pad = str(bun).strip().zfill(4)
    ji_pad = str(ji).strip().zfill(4)
    sigungu = str(sigungu).strip()
    bjdong = str(bjdong).strip()
    url_floor = "http://apis.data.go.kr/1613000/BldRgstHubService/getBrFlrOulnInfo"
    query = f"?serviceKey={API_KEY}&sigunguCd={sigungu}&bjdongCd={bjdong}&platGbCd=0&bun={bun_pad}&ji={ji_pad}&numOfRows=100&pageNo=1&_type=json"
    
    result = {'area': '', 'supply_area': '', 'flrNo': '', 'violBldYn': 'N'}
    
    try:
        req = urllib.request.Request(url_floor + query)
        req.add_header('User-Agent', 'Mozilla/5.0')
        res = urllib.request.urlopen(req)
        if res.getcode() == 200:
            res_body = res.read().decode('utf-8')
            if not res_body.strip():
                result['violBldYn'] = '확인불가(정부서버오류)'
                return result
                
            data = json.loads(res_body)
            items = data.get("response", {}).get("body", {}).get("items", {})
            if items:
                item_list = items.get("item", [])
                if isinstance(item_list, dict): item_list = [item_list]
                
                for item in item_list:
                    api_flr_name = str(item.get('flrNoNm', '')).replace(" ", "")
                    api_flr_gb = str(item.get('flrGbCdNm', ''))
                    
                    is_req_ug = (str(floor_name).startswith('-') or '지하' in str(floor_name) or '지층' in str(floor_name))
                    api_is_ug = ('지하' in api_flr_gb or '지' in api_flr_name or str(item.get('flrNo', '')).startswith('-'))
                    
                    req_num = re.sub(r'[^\d]', '', str(floor_name))
                    api_num = re.sub(r'[^\d]', '', api_flr_name)
                    
                    match = False
                    if is_req_ug == api_is_ug and req_num and api_num and req_num == api_num:
                        match = True
                    elif str(floor_name).replace(" ", "") in api_flr_name or api_flr_name in str(floor_name).replace(" ", ""):
                        match = True
                        
                    if match:
                        area = item.get('area', '')
                        result['area'] = str(area)
                        result['supply_area'] = str(area) # 전체 층이므로 공급/전용 동일
                        result['flrNo'] = item.get('flrNo', '')
                        result['etcPurps'] = str(item.get('etcPurps', '') or '')
                        result['strctCdNm'] = str(item.get('strctCdNm', '') or '')
                        return result
    except Exception as e:
        print("층별개요 조회 중 오류:", e)
        result['violBldYn'] = '확인불가(정부서버오류)'
        
    return result
