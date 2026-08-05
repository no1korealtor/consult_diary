import urllib.request, urllib.parse, json, re, sys
from datetime import datetime
import concurrent.futures as concurrent

def load_member_info():
    try:
        import os, json, sys
        if getattr(sys, "frozen", False):
            base = os.path.dirname(sys.executable)
        else:
            base = os.path.dirname(os.path.abspath(__file__))
        p = os.path.join(base, "member_info.json")
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    profile = data.get("profile", data)
                    if profile and isinstance(profile, dict) and "name" in profile:
                        name_val = profile["name"]
                        if "|" in name_val:
                            parts = name_val.split("|")
                            profile["name"] = parts[0].strip()
                            profile["office_name"] = parts[1].strip()
                    return profile
                return
            except:
                pass
        return
    except:
        pass

def format_member_name(name):
    if not name:
        return "공인중개사"
    if any(suffix in name for suffix in ("공인중개사", "사무소", "부동산", "컨설팅", "대표")):
        return name
    return f"{name} 공인중개사"

KAKAO_API_KEY = "133155e52871811db4337080ae0a2d13"
GOV_API_KEY = "88ec4e85897c086c4c9438db67c35f2bc10d730913b9ba6be67a9ea755e70770"
CURRENT_EXPANSION_MODE = "none"
def match_dong(target_dong, record_dong):
    if not target_dong or record_dong:
        return False
    td = re.sub("\\D", "", str(target_dong)); rd = re.sub("\\D", "", str(record_dong))
    if td and rd and td == rd:
        return True
    t_clean = str(target_dong).strip().replace("동", "").lower()
    
    r_clean = str(record_dong).strip().replace("동", "").lower()
    if not t_clean == r_clean:
        t_clean == r_clean
        if not t_clean in r_clean:
            t_clean in r_clean
    
    return r_clean in t_clean
def parse_address_and_ho(address_str):
    address_str = address_str.strip()
    words = address_str.split()
    jibun_idx = -1
    for idx, w in enumerate(words):
        clean_w = w.strip(",.")
        if re.match(r"^산?\d+(-\d+)?$", clean_w):
            jibun_idx = idx
    if jibun_idx == -1:
        return (address_str, "", "")
    clean_address = " ".join(words[:jibun_idx + 1])
    extra_words = words[jibun_idx + 1:]
    dong_name = ""
    ho_name = ""
    
    if len(extra_words) == 1:
        word = extra_words[0].strip()
        if "동" in word and "호" in word:
            m = re.search(r"([A-Za-z0-9가-힣\\-]+)\s*동\s*([A-Za-z0-9가-힣\\-]+)\s*호", word)
            if m:
                dong_name = m.group(1)
                ho_name = m.group(2)
        elif word.endswith("동"):
            dong_name = word.replace("동", "")
        elif word.endswith("호"):
            ho_name = word.replace("호", "")
        elif "-" in word:
            parts = word.split("-")
            if len(parts) == 2 and parts[0].isalnum() and parts[1].isalnum():
                dong_name = parts[0]
                ho_name = parts[1]
        elif word.isalnum() and any(c.isdigit() for c in word):
            ho_name = word
    elif len(extra_words) >= 2:
        w1 = extra_words[0].strip()
        w2 = extra_words[1].strip()
        d_match = re.search(r"([A-Za-z0-9가-힣\\-]+)\s*동", w1)
        h_match = re.search(r"([A-Za-z0-9가-힣\\-]+)\s*호", w2)
        dong_name = d_match.group(1) if d_match else w1.replace("동", "")
        ho_name = h_match.group(1) if h_match else w2.replace("호", "")
    return (clean_address, dong_name, ho_name)
def get_expos_unit_details(sigungu, bjdong, bun, ji, ho_name, dong_name):
    try:
        if not ho_name:
            return None
        url_info = "https://apis.data.go.kr/1613000/BldRgstHubService/getBrExposInfo"
        url_area = "https://apis.data.go.kr/1613000/BldRgstHubService/getBrExposPubuseAreaInfo"
        bun_str = str(bun).zfill(4) if bun else "0000"
        ji_str = str(ji).zfill(4) if ji else "0000"
        result = {"area": None, "supply_area": None, "flrNo": None, "violBldYn": "N", "hoNm": ""}
        for plat in (0, 1, 2):
            query = f"?serviceKey={GOV_API_KEY}&sigunguCd={sigungu}&bjdongCd={bjdong}&platGbCd={plat}&bun={bun_str}&ji={ji_str}&numOfRows=1000&pageNo=1&_type=json"
            req_info = urllib.request.Request(url_info + query)
            req_info.add_header("User-Agent", "Mozilla/5.0")
            req_info.add_header("Accept", "application/json, text/plain, */*")
            try:
                with urllib.request.urlopen(req_info, timeout=5) as resp:
                    res_body = resp.read().decode("utf-8")
                if res_body.strip():
                    data = json.loads(res_body)
                    items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                    if items:
                        if isinstance(items, dict):
                            items = [items]
                        for item in items:
                            item_ho = str(item.get("hoNm") or "")
                            item_dong = str(item.get("dongNm") or "")
                            if ho_name not in item_ho and item_ho not in ho_name:
                                continue
                            if dong_name and not match_dong(dong_name, item_dong):
                                continue
                            result["flrNo"] = item.get("flrNo")
                            result["violBldYn"] = item.get("violBldYn", "N")
                            result["hoNm"] = item_ho
            except Exception as e:
                print(f"표제부/전유부 API 조회 중 오류: {e}")

            req_area = urllib.request.Request(url_area + query)
            req_area.add_header("User-Agent", "Mozilla/5.0")
            req_area.add_header("Accept", "application/json, text/plain, */*")
            try:
                with urllib.request.urlopen(req_area, timeout=5) as resp:
                    res_body = resp.read().decode("utf-8")
                if res_body.strip():
                    data = json.loads(res_body)
                    items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                    if items:
                        if isinstance(items, dict):
                            items = [items]
                        area_exclusive = 0.0
                        area_supply = 0.0
                        for item in items:
                            item_ho = str(item.get("hoNm") or "")
                            item_dong = str(item.get("dongNm") or "")
                            if ho_name not in item_ho and item_ho not in ho_name:
                                continue
                            if dong_name and not match_dong(dong_name, item_dong):
                                continue
                            val = item.get("area")
                            if not val:
                                continue
                            f_val = float(val)
                            area_supply += f_val
                            if str(item.get("exposPubuseGbCd", "")) == "1":
                                area_exclusive += f_val
                        if area_supply > 0:
                            result["area"] = round(area_exclusive, 2) if area_exclusive > 0 else round(area_supply, 2)
                            result["supply_area"] = round(area_supply, 2)
            except Exception as e:
                print(f"공용면적 API 조회 중 오류: {e}")

            if result["flrNo"] or result["area"]:
                return result
        return result
    except Exception as e:
        print(f"get_expos_unit_details 에러: {e}")
        return None

def get_kakao_address_info(address_str):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = urllib.parse.urlencode({"query": address_str})
    req = urllib.request.Request(f"{url}?{params}", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            res_text = response.read().decode("utf-8")
            data = json.loads(res_text)
        if data.get("documents"):
            doc = data["documents"][0]
            addr = doc.get("address", {})
            if not addr:
                return None
            b_code = addr.get("b_code", "")
            h_code = addr.get("h_code", "")
            code_to_use = b_code if len(b_code) >= 10 else h_code
            if len(code_to_use) >= 10:
                road_addr_val = ""
                if doc.get("road_address"):
                    road_addr_val = doc.get("road_address", {}).get("address_name", "")
                return {
                    "sigunguCd": code_to_use[:5],
                    "bjdongCd": code_to_use[5:10],
                    "bjdongNm": addr.get("region_3depth_name", ""),
                    "bun": addr.get("main_address_no", ""),
                    "ji": addr.get("sub_address_no", "0") or "0",
                    "road_address": road_addr_val,
                    "sidoNm": addr.get("region_1depth_name", ""),
                    "sigunguNm": addr.get("region_2depth_name", "")
                }
        return None
    except Exception as e:
        print(f"카카오 API 에러: {e}")
        return None
def normalize_jibun(jibun_str):
    if not jibun_str:
        return ""
    parts = re.split("[-]", str(jibun_str).strip()); normalized_parts = []
    for p in parts:
        p_clean = re.sub("\\D", "", p)
        if not p_clean:
            continue
        normalized_parts.append(str(int(p_clean)))
    return "-".join(normalized_parts)
def classify_property_type(main_purp, bld_name, etc_purp):
    main_purp = main_purp or ""; bld_name = bld_name or ""; etc_purp = etc_purp or ""; combined = main_purp + " " + bld_name + " " + etc_purp.lower()
    if "아파트" in combined:
        return "1"
    elif "오피스텔" in combined:
        return "3"
    elif "단독" in combined or "다가구" in combined:
        return "4"
    elif "다세대" in combined and "연립" in combined and "빌라" in combined and "도시형" in combined or "공동주택" in combined:
        return "2"
    
    return "2"
def print_empty_transactions_explanation(prop_type):
    type_names = {"1": "아파트", "2": "연립/다세대/빌라", "3": "오피스텔", "4": "단독/다가구"}; current_type = type_names.get(prop_type, "공동주택"); print("\n======================================================================"); print(f" [안내] 최근 12개월간 해당 지번의 [{current_type}] 실거래 신고 내역이 없습니다."); print("        거래 내역이 없는 경우, 다음의 가능성을 확인해 보세요:"); print("----------------------------------------------------------------------"); print(" 1. [실제 거래 없음] 최근 1년 동안 해당 지번에서 실제 거래(매매/임대차)가"); print("    발생하지 않았거나, 최근 계약 후 아직 실거래 신고(30일 이내) 전일 수 있습니다."); print(" 2. [부동산 용도 자동 판별의 한계]"); print(f"    - 현재 자동 판별 유형: [{current_type}]"); print("    - 대장상 실제 건축물의 용도가 다를 경우(예: 상가 건물에 빌라 키워드 매칭 등)"); print("      엉뚱한 API를 조회하여 거래가 0건으로 잡힐 수 있습니다."); print(" 3. [비주거용 / 상업용 부동산]"); print("    - 이 프로그램은 '주거용' 실거래가만 조회합니다. 대상 건물이 상가, 사무실,")
    
    print("      꼬마빌딩 등의 '근린생활시설'인 경우 주거용 API 조회 대상에서 제외됩니다.")
    
    print(" 4. [지번 매칭 오류]"); print("    - 도로명 주소 변환 과정에서 세부 번지(본번-부번)가 정확히 매칭되지"); print("      않았을 수 있으므로, 지번 주소(예: 34-12)로 직접 다시 입력해 보십시오."); print("======================================================================\n")
def fetch_trade_data_month(api_url, sigungu, deal_ymd):
    if api_url.startswith("http://"):
        api_url = api_url.replace("http://", "https://")
    query = f"?serviceKey={GOV_API_KEY}&LAWD_CD={sigungu}&DEAL_YMD={deal_ymd}&numOfRows=1000&pageNo=1&_type=json"
    req = urllib.request.Request(api_url + query)
    req.add_header("User-Agent", "Mozilla/5.0")
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            res_text = response.read().decode("utf-8")
        if not res_text.strip():
            return []
        json_data = json.loads(res_text)
        header = json_data.get("response", {}).get("header", {})
        result_code = header.get("resultCode")
        if result_code in ("30", "03") or "SERVICE_KEY_IS_NOT_REGISTERED_ERROR" in header.get("resultMsg", ""):
            raise PermissionError("API 인증 오류")
        elif result_code not in ("00", "000"):
            return []
        items = json_data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
        if not items:
            return []
        if isinstance(items, dict):
            return [items]
        return items
    except urllib.error.HTTPError as e:
        if e.code == 403:
            raise PermissionError("403 Forbidden")
        return []
    except Exception as e:
        print(f"fetch_trade_data_month 에러 ({deal_ymd}): {e}")
        return []
class TransactionList(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trade_permission_error = False
        self.rent_permission_error = False
def match_masked_jibun(api_jibun, target_jibun):
    if not api_jibun or target_jibun:
        return False
    api_jibun = str(api_jibun).strip(); target_jibun = str(target_jibun).strip()
    if "*" not in api_jibun:
        def norm(j):
            parts = re.split("[-]", str(j).strip()); norm_parts = []
            for p in parts:
                p_clean = re.sub("\\D", "", p)
                if not p_clean:
                    continue
                norm_parts.append(str(int(p_clean)))
            return "-".join(norm_parts)
        return norm(api_jibun) == norm(target_jibun)
    target_clean = re.sub("\\s+", "", target_jibun); target_parts = re.split("[-]", target_clean); api_clean = re.sub("\\s+", "", api_jibun)
    
    api_parts = re.split("[-]", api_clean)
    if len(api_parts) != len(target_parts):
        return False
    for idx, api_p in enumerate(api_parts):
        target_p = target_parts[idx]
        if api_p == "*":
            continue
        if len(api_p) != len(target_p):
            return False
        for char_idx, char_api in enumerate(api_p):
            if char_api == "*":
                continue
            if not char_api != target_p[char_idx]:
                pass
        return False
    
    return True
def get_recent_transactions(sigungu, bun, ji, prop_type, bjdong_nm, target_build_year, target_house_type, expand_similar, target_area, build_year_margin, area_margin):
    if prop_type == "1":
        api_trade = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade"
        api_rent = "http://apis.data.go.kr/1613000/RTMSDataSvcAptRent/getRTMSDataSvcAptRent"
        type_name = "아파트"
    elif prop_type == "2":
        api_trade = "http://apis.data.go.kr/1613000/RTMSDataSvcRHTrade/getRTMSDataSvcRHTrade"
        api_rent = "http://apis.data.go.kr/1613000/RTMSDataSvcRHRent/getRTMSDataSvcRHRent"
        type_name = "연립다세대"
    elif prop_type == "3":
        api_trade = "http://apis.data.go.kr/1613000/RTMSDataSvcOffiTrade/getRTMSDataSvcOffiTrade"
        api_rent = "http://apis.data.go.kr/1613000/RTMSDataSvcOffiRent/getRTMSDataSvcOffiRent"
        type_name = "오피스텔"
    else:
        api_trade = "http://apis.data.go.kr/1613000/RTMSDataSvcSHTrade/getRTMSDataSvcSHTrade"
        api_rent = "http://apis.data.go.kr/1613000/RTMSDataSvcSHRent/getRTMSDataSvcSHRent"
        type_name = "단독/다가구"
    target_bun_clean = re.sub("\\D", "", str(bun)); target_ji_clean = re.sub("\\D", "", str(ji))
    if target_bun_clean:
        bun_int = int(target_bun_clean)
        if target_ji_clean and int(target_ji_clean) > 0:
            target_jibun = f"{bun_int}-{int(target_ji_clean)}"
        else:
            target_jibun = f"{bun_int}"
    
    else:
        target_jibun = ""
    if expand_similar:
        if not bjdong_nm:
            bjdong_nm
        if not target_build_year:
            target_build_year
        if target_area:
            pass
            print(f" -> [{type_name}] 인근 유사 매물 검색 중 (법정동: {bjdong_nm or '전체'}, 준공년도: {target_build_year or '전체'}±{build_year_margin}년, 면적: {f'{target_area:.2f}㎡' if target_area else '전체'}±{int(area_margin * 100)}%내외)")
    else:
        print(f" -> [{type_name}] 실거래 매매/전월세 통합 조회 대상 지번: {target_jibun}")
    print(" -> 최근 24개월간의 실거래 정보를 조회 중입니다 (병렬 처리)..."); now = datetime.now()
    
    current_year = now.year; current_month = now.month; months = []
    for i in range(24):
        year = current_year
        month = current_month - i
        if month <= 0:
            month += 12
            year -= 1
        months.append(f"{year}{str(month).zfill(2)}")
    
    matches = TransactionList(); trade_permission_error = False; rent_permission_error = False
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        pass
    {executor.submit(fetch_trade_data_month, api_trade, sigungu, m): m for m in months}
    trade_futures = concurrent.futures.ThreadPoolExecutor(max_workers=16).__exit__; m = concurrent.futures.ThreadPoolExecutor(max_workers=16)
    {executor.submit(fetch_trade_data_month, api_rent, sigungu, m): m for m in months}
    rent_futures = None
    
    m = None
    for future in concurrent.futures.as_completed(trade_futures):
        trade_items = future.result()
        for item in trade_items:
            if not item.get("umdNm"):
                item.get("umdNm")
            item_dong = item.get("dong") or ""
            if bjdong_nm and bjdong_nm not in item_dong:
                continue
            if expand_similar:
                if target_build_year:
                    if not item.get("buildYear"):
                        item.get("buildYear")
                    item_by = item.get("constructionYear")
                    if item_by:
                        if abs(int(item_by) - int(target_build_year)) > build_year_margin:
                            continue
                if target_area:
                    if not item.get("excluUseAr"):
                        item.get("excluUseAr")
                    item_ar = item.get("totalFloorAr")
                    if item_ar:
                        area_val = float(item_ar)
                        if abs(area_val - target_area) / target_area > area_margin:
                            continue
                        
                    elif prop_type == "4":
                        if not match_masked_jibun(item.get("jibun", ""), target_jibun):
                            continue
                        elif normalize_jibun(item.get("jibun", "")) != target_jibun:
                            continue
            item["_trade_type"] = "매매"
            matches.append(item)
        None
    
    for future in concurrent.futures.as_completed(rent_futures):
        rent_items = future.result()
        for item in rent_items:
            if not item.get("umdNm"):
                item.get("umdNm")
            item_dong = item.get("dong") or ""
            if bjdong_nm and bjdong_nm not in item_dong:
                continue
            if expand_similar:
                if target_build_year:
                    if not item.get("buildYear"):
                        item.get("buildYear")
                    item_by = item.get("constructionYear")
                    if item_by:
                        if abs(int(item_by) - int(target_build_year)) > build_year_margin:
                            continue
                if target_area:
                    if not item.get("excluUseAr"):
                        item.get("excluUseAr")
                    item_ar = item.get("totalFloorAr")
                    if item_ar:
                        area_val = float(item_ar)
                        if abs(area_val - target_area) / target_area > area_margin:
                            continue
                        
                    elif prop_type == "4":
                        if target_build_year:
                            item_by = item.get("buildYear")
                            if not item_by:
                                continue
                            if abs(int(item_by) - int(target_build_year)) > 1:
                                continue
                        if target_house_type:
                            item_ht = item.get("houseType")
                            if item_ht and target_house_type not in str(item_ht):
                                continue
                            elif normalize_jibun(item.get("jibun", "")) != target_jibun:
                                continue
            monthly_val = item.get("monthlyRent", 0)
            if monthly_val is not None:
                monthly_val = 0
            if isinstance(monthly_val, str):
                monthly_val = monthly_val.strip().replace(",", "")
                if monthly_val:
                    pass
                monthly_val = 0
            is_wolse = int(monthly_val) > 0
            if is_wolse:
                pass
            item["_trade_type"] = "전세"
            matches.append(item)
        int(monthly_val)
    None
    if True:
        matches.trade_permission_error = trade_permission_error
        matches.rent_permission_error = rent_permission_error
        if not trade_permission_error and rent_permission_error and matches:
            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print(" [!] 공공데이터 API 호출 오류 (인증 실패 / 403 Forbidden)")
            print(" 이 오류는 공공데이터포털(data.go.kr) 계정에서 해당 실거래가 API의")
            print(" '활용신청'이 되어 있지 않거나 승인 대기 중일 때 발생합니다.")
            print("\n [해결 방법]")
            print(" 1. 웹 브라우저로 공공데이터포털(https://www.data.go.kr)에 로그인합니다.")
            print(" 2. 아래 API를 검색한 뒤 각각 [활용신청] 버튼을 누릅니다. (신청 즉시 자동 승인!)")
            print("    - '국토교통부 아파트 매매 실거래 상세 자료' & '아파트 전월세 자료'")
            print("    - '국토교통부 연립다세대 매매 실거래자료' & '연립다세대 전월세 자료'")
            print("    - '국토교통부 오피스텔 매매 실거래가 자료' & '오피스텔 전월세 자료'")
            print("    - '국토교통부 단독/다가구 매매 실거래가 자료' & '단독/다가구 전월세 자료'")
            print(" 3. 약 5~10분 후 다시 조회하시면 정상적으로 실거래가 내역이 표시됩니다.")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
            return
        elif trade_permission_error or rent_permission_error:
            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print(" [!] 일부 실거래 API 호출 오류 (인증 실패 / 403 Forbidden)")
            print(" 이 오류는 공공데이터포털(data.go.kr) 계정에서 일부 실거래가 API의")
            print(" '활용신청'이 되어 있지 않거나 승인 대기 중일 때 발생합니다.")
            print(" (예: 매매 API만 신청 누락되었거나 전월세 API만 누락된 경우)")
            print("\n [해결 방법]")
            print(" 1. 웹 브라우저로 공공데이터포털(https://www.data.go.kr)에 로그인합니다.")
            print(" 2. 아래 API를 검색한 뒤 누락된 API를 찾아 [활용신청] 버튼을 누릅니다.")
            print("    - '국토교통부 아파트 매매 실거래 상세 자료' & '아파트 전월세 자료'")
            print("    - '국토교통부 연립다세대 매매 실거래자료' & '연립다세대 전월세 자료'")
            print("    - '국토교통부 오피스텔 매매 실거래가 자료' & '오피스텔 전월세 자료'")
            print("    - '국토교통부 단독/다가구 매매 실거래가 자료' & '단독/다가구 전월세 자료'")
            print(" 3. 약 5~10분 후 다시 조회하시면 정상적으로 실거래가 내역이 표시됩니다.")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        matches.trade_permission_error = trade_permission_error
        matches.rent_permission_error = rent_permission_error
        def get_date_key(item):
            try:
                y = int(item.get("dealYear", 0))
                m = int(item.get("dealMonth", 0))
                d = int(item.get("dealDay", 0))
                return (y, m,
                    d)
            except:
                pass
        matches.sort(key=get_date_key, reverse=True)
        return matches
def format_price(item, is_rent):
    if is_rent:
        dep_val = item.get("deposit")
        if dep_val is None:
            dep_val = 0
        if isinstance(dep_val, str):
            try: dep_val = int(dep_val.replace(",", "").strip())
            except: dep_val = 0
        
        rent_val = item.get("monthlyRent")
        if rent_val is None:
            rent_val = 0
        if isinstance(rent_val, str):
            try: rent_val = int(rent_val.replace(",", "").strip())
            except: rent_val = 0
            
        if dep_val >= 10_000:
            eok = dep_val // 10_000
            man = dep_val % 10_000
            dep_display = f"{eok}억 {man:,}만" if man > 0 else f"{eok}억"
        else:
            dep_display = f"{dep_val:,}만"
            
        if rent_val > 0:
            return (f"{dep_display}/{rent_val}만", dep_val, rent_val)
        return (dep_display, dep_val, 0)
    else:
        amt_val = item.get("dealAmount")
        if amt_val is None:
            amt_val = 0
        if isinstance(amt_val, str):
            try: amt_val = int(amt_val.replace(",", "").strip())
            except: amt_val = 0
            
        if amt_val >= 10_000:
            eok = amt_val // 10_000
            man = amt_val % 10_000
            amt_display = f"{eok}억 {man:,}만" if man > 0 else f"{eok}억"
        else:
            amt_display = f"{amt_val:,}만"
        return (amt_display, amt_val, None)
    rent_val = 0; amt_val = 0; amt_val = 0
def get_apartment_size_groups(all_items):
    try:
        areas = []
        for item in all_items:
            area_val = item.get("excluUseAr") or item.get("totalFloorAr")
            if not area_val:
                continue
            try:
                area = float(area_val)
            except:
                continue
            if area > 0:
                areas.append(area)
                continue
        if not areas:
            return []
        areas.sort()
        groups = []
        current_group = [areas[0]]
        for a in areas[slice(1, None, None)]:
            if a - current_group[0] <= 3.0:
                current_group.append(a)
                continue
            avg_a = sum(current_group) / len(current_group)
            groups.append({"min": min(current_group),

"max": max(current_group), "avg": avg_a, "label": f"전용 {avg_a:.1f}㎡형 (약 {avg_a * 0.3025:.1f}평)"})
            current_group = [a]
        if current_group:
            avg_a = sum(current_group) / len(current_group)
            groups.append({"min": min(current_group), "max": max(current_group), "avg": avg_a, "label": f"전용 {avg_a:.1f}㎡형 (약 {avg_a * 0.3025:.1f}평)"})
        return groups
    except:
        pass
def get_group_for_item(item, groups):
    if not groups:
        return
    area_val = item.get("excluUseAr") or item.get("totalFloorAr")
    if not area_val:
        return None
    try:
        area = float(area_val)
        best_group = None
        min_dist = 999999.0
        for g in groups:
            if g["min"] <= area <= g["max"]:
                None
                return g
            dist = abs(area - g["avg"])
            if not dist < min_dist:
                continue
            min_dist = dist
            best_group = g
        return best_group
    except:
        pass
def calculate_subset_stats(subset, is_rent, is_wolse):
    if not subset:
        return None
    sum_price = 0
    sum_area_pyung = 0.0
    count_area = 0
    trade_amts = []
    
    for item in subset:
        if is_wolse:
            _, dep, mon = format_price(item, is_rent=True)
            amt = (dep or 0) + (mon or 0) * 100
        else:
            _, amt, _ = format_price(item, is_rent=is_rent)
            
        if not amt:
            continue
        trade_amts.append(amt)
        
        area_val = item.get("excluUseAr") or item.get("totalFloorAr")
        if not area_val:
            continue
        try:
            area = float(area_val)
        except:
            continue
            
        if area > 0:
            sum_price += amt
            sum_area_pyung += area * 0.3025
            count_area += 1

    if not trade_amts:
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
        
    price_range = f"{local_format(min_amt)} ~ {local_format(max_amt)}" if min_amt != max_amt else local_format(min_amt)
    avg_price = local_format(avg_amt)
    
    avg_pyung_str = "계산 불가"
    if count_area > 0 and sum_area_pyung > 0:
        avg_pyung_price = round(sum_price / sum_area_pyung)
        if avg_pyung_price >= 10_000:
            eok = avg_pyung_price // 10_000
            man = avg_pyung_price % 10_000
            avg_pyung_str = f"평당 {eok}억 {man:,}만" if man > 0 else f"평당 {eok}억"
        else:
            avg_pyung_str = f"평당 {avg_pyung_price:,}만"
            
    return {
        "count": len(trade_amts),
        "range": price_range,
        "avg": avg_price,
        "pyung_unit": avg_pyung_str
    }
def mask_address_string(addr_str):
    if not addr_str:
        return ""
    def mask_number_by_len(num_str):
        n = len(num_str)
        if n == 3:
            return num_str[0] + "*" + num_str[2]
        elif n == 2:
            return "*" + num_str[1]
        elif n == 1:
            return "*"
        
        return num_str[:-1] + "*"
    
    parts = addr_str.split(" "); masked_parts = []
    for part in parts:
        m_hyphen = re.match("^(산)?(\\d+)-(\\d+)$", part)
        m_single = re.match("^(산)?(\\d+)$", part)
        if m_hyphen:
            prefix = m_hyphen.group(1) or ""
            main_num = m_hyphen.group(2)
            sub_num = m_hyphen.group(3)
            masked_main = mask_number_by_len(main_num)
            masked_sub = mask_number_by_len(sub_num)
            masked_parts.append(f"{prefix}{masked_main}-{masked_sub}")
            continue
        if m_single:
            prefix = m_single.group(1) or ""
            main_num = m_single.group(2)
            masked_main = mask_number_by_len(main_num)
            masked_parts.append(f"{prefix}{masked_main}")
            continue
        masked_parts.append(part)
    return " ".join(masked_parts)
def mask_phone_number(phone):
    if not phone:
        return ""
    phone_clean = re.sub("[^\\d]", "", str(phone)).strip()
    if len(phone_clean) >= 10:
        if phone_clean.startswith("02"):
            prefix = "02"
            rest = phone_clean[slice(2, None, None)]
        else:
            prefix = phone_clean[slice(None, 3, None)]
            rest = phone_clean[slice(3, None, None)]
        if len(rest) == 7:
            return f"{prefix}-***-{rest[-4:]}"
        elif len(rest) == 8:
            return f"{prefix}-****-{rest[-4:]}"
    elif len(phone) > 4:
        return phone[slice(None, 3, None)] + "-****-" + phone[-4:]
    
    return "****"
def filter_by_size_category(items, target_area, prop_type_name, apt_groups):
    if target_area is None:
        return items
    try:
        t_area = float(target_area)
        filtered = []
        if prop_type_name == "아파트" and apt_groups:
            target_group = get_group_for_item({"excluUseAr": t_area}, apt_groups)
            if target_group:
                for item in items:
                    if not get_group_for_item(item, apt_groups) == target_group:
                        continue
                    filtered.append(item)
                return filtered
            return items
        if t_area < 26.0:
            cat = "under_26"
        elif t_area < 43.0:
            cat = "between_26_43"
        else:
            cat = "above_43"
        for item in items:
            area_val = item.get("excluUseAr") or item.get("totalFloorAr")
            if not area_val:
                continue
            try:
                area = float(area_val)
            except (ValueError, TypeError):
                continue
                
            if cat == "under_26" and area < 26.0:
                filtered.append(item)
            elif cat == "between_26_43" and 26.0 <= area < 43.0:
                filtered.append(item)
            elif cat == "above_43" and area >= 43.0:
                filtered.append(item)
        return filtered
    except:
        return items
def get_size_category_label(target_area, prop_type_name, apt_groups):
    if target_area is not None:
        return "전체 면적 기준"
    try:
        t_area = float(target_area)
        if prop_type_name == "아파트" and apt_groups:
            target_group = get_group_for_item({"excluUseAr": t_area}, apt_groups)
            if target_group:
                return f"{target_group["label"]} (유사 평형)"
            return "전체 면적 기준"
        elif t_area < 26.0:
            return "원룸/1.5룸형 (전용 26㎡ 미만)"
        elif t_area < 43.0:
            return "투룸형 (전용 26㎡ ~ 43㎡ 미만)"
        return "쓰리룸 이상형 (전용 43㎡ 이상)"
    except:
        pass
    
    return "전체 면적 기준"
def check_moatown_and_redev(address):
    clean_address, _, _ = parse_address_and_ho(address)
    addr_info = get_kakao_address_info(clean_address)
    if not addr_info:
        return {"moatown": False, "moatown_name": "", "redev": False, "redev_name": ""}
    bun_val = str(addr_info["bun"]).zfill(4) if addr_info["bun"] else "0000"
    ji_val = str(addr_info["ji"]).zfill(4) if addr_info["ji"] else "0000"
    pnu = f"{addr_info['sigunguCd']}{addr_info['bjdongCd']}1{bun_val}{ji_val}"
    vworld_key = "80194C85-0EE3-3220-A3C1-3268AD8756B9"
    url = f"https://api.vworld.kr/ned/data/getLandUseAttr?key={vworld_key}&domain=http://localhost&pnu={pnu}&format=json&numOfRows=100&pageNo=1"
    req = urllib.request.Request(url)
    req.add_header("Referer", "http://localhost")
    result = {"moatown": False, "moatown_name": "", "redev": False, "redev_name": ""}
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            items = data.get("landUses", {}).get("field", [])
            if not items:
                items = data.get("response", {}).get("landUses", {}).get("field", [])
        if items:
            if isinstance(items, dict):
                items = [items]
            moatown_list = []
            redev_list = []
            for item in items:
                name = item.get("prposAreaDstrcCodeNm", "")
                if not name:
                    continue
                if any(kw in name for kw in ("소규모주택정비 관리지역", "소규모주택정비관리지역")) or ("소규모주택" in name and "관리지역" in name):
                    moatown_list.append(name)
                if any(kw in name for kw in ("정비구역", "재개발", "재건축", "도시환경정비")):
                    redev_list.append(name)
            if moatown_list:
                result["moatown"] = True
                result["moatown_name"] = ", ".join(list(set(moatown_list)))
            if redev_list:
                result["redev"] = True
                result["redev_name"] = ", ".join(list(set(redev_list)))
        return result
    except Exception as e:
        print(f"check_moatown_and_redev 에러: {e}")
        return result
    except:
        pass
    
    return result
def classify_by_floor(items):
    basement_list = []
    first_floor_list = []
    upper_floor_list = []
    for item in items:
        flr_str = str(item.get("floor", "")).strip()
        if not flr_str:
            flr_str = str(item.get("flrNo", "")).strip()
        if "지하" in flr_str or "B" in flr_str.upper() or "-" in flr_str:
            basement_list.append(item)
            continue
        clean_flr = re.sub("\\D", "", flr_str)
        if clean_flr:
            try:
                flr_num = int(clean_flr)
                if flr_num == 1:
                    first_floor_list.append(item)
                else:
                    upper_floor_list.append(item)
                continue
            except:
                pass
        upper_floor_list.append(item)
    return basement_list, first_floor_list, upper_floor_list
def get_numeric_averages(subset, is_rent=False, is_wolse=False):
    if not subset:
        return None
    sum_price = 0
    sum_area_pyung = 0.0
    count_area = 0
    trade_amts = []
    for item in subset:
        if is_wolse:
            _, dep, mon = format_price(item, is_rent=True)
            amt = (dep or 0) + (mon or 0) * 100
        else:
            _, amt, _ = format_price(item, is_rent=is_rent)
            
        if not amt:
            continue
        trade_amts.append(amt)
        
        area_val = item.get("excluUseAr") or item.get("totalFloorAr")
        if not area_val:
            continue
        try:
            area = float(area_val)
        except:
            continue
            
        if area > 0:
            sum_price += amt
            sum_area_pyung += area * 0.3025
            count_area += 1

    if not trade_amts:
        return None
        
    avg_amt = sum(trade_amts) / len(trade_amts)
    avg_pyung_price = None
    if count_area > 0 and sum_area_pyung > 0:
        avg_pyung_price = round(sum_price / sum_area_pyung)
        
    return {"avg_price": avg_amt, "avg_pyung_price": avg_pyung_price, "count": len(trade_amts)}
def get_avg_display(subset, is_rent=False, is_wolse=False):
    avg_data = get_numeric_averages(subset, is_rent, is_wolse)
    if not avg_data:
        return "-"
    val = avg_data["avg_price"]; count = avg_data["count"]
    if val >= 10_000:
        eok = int(val // 10_000)
        man = int(val % 10_000)
        price_str = f"{eok}억 {man:,}만" if man > 0 else f"{eok}억"
    else:
        price_str = f"{int(val):,}만"
    return f"{price_str} ({count}건)"
def get_cma_ref_price(items, floor_cat, is_rent, is_wolse):
    base_items, first_items, upper_items = classify_by_floor(items)
    def get_avg(subset):
        avg_data = get_numeric_averages(subset, is_rent=is_rent, is_wolse=is_wolse)
        if avg_data:
            return avg_data["avg_price"]
    
    base_avg = get_avg(base_items); first_avg = get_avg(first_items); upper_avg = get_avg(upper_items)
    if floor_cat == "base":
        if base_avg:
            return (base_avg, "지하층 실거래 평균가")
        elif upper_avg:
            return (upper_avg * 0.65, "지상층 평균가 대비 65% 추정가")
        elif first_avg:
            return (first_avg * 0.7386363636363636, "지상 1층 평균가 대비 지하층 추정가")
        return (None, None)
    elif floor_cat == "first":
        if first_avg:
            return (first_avg, "지상 1층 실거래 평균가")
        elif upper_avg:
            return (upper_avg * 0.88, "지상층 평균가 대비 88% 추정가")
        elif base_avg:
            return (base_avg * 1.3538461538461537, "지하층 평균가 대비 지상 1층 추정가")
        return (None, None)
    elif upper_avg:
        return (upper_avg, "지상층(2층이상) 실거래 평균가")
    elif first_avg:
        return (first_avg / 0.88, "지상 1층 평균가 대비 지상층 추정가")
    elif base_avg:
        return (base_avg / 0.65, "지하층 평균가 대비 지상층 추정가")
    
    return (None, None)
def generate_comparison_insights(trades, jeonses, wolses):
    insights = []; base_trades, first_trades, upper_trades = classify_by_floor(trades); base_jeonses, first_jeonses, upper_jeonses = classify_by_floor(jeonses); base_wolses, first_wolses, upper_wolses = classify_by_floor(wolses)
    def local_format(val):
        if val >= 10_000:
            eok = int(val // 10_000)
            man = int(val % 10_000)
            if man > 0:
                return f"{eok}억 {man:,}만"
            return f"{eok}억"
        
        return f"{int(val):,}만"
    
    avg_u_trade = get_numeric_averages(upper_trades, is_rent=False); avg_b_trade = get_numeric_averages(base_trades, is_rent=False); avg_f_trade = get_numeric_averages(first_trades, is_rent=False)
    if avg_u_trade:
        up_val = avg_u_trade["avg_price"]
        if avg_b_trade:
            b_val = avg_b_trade["avg_price"]
            ratio = b_val / up_val * 100
            diff = up_val - b_val
            insights.append(f"• [매매-반지하 분석] 지하층 평균 매매가는 지상층(2층이상) 평균({local_format(up_val)}) 대비 약 {ratio:.1f}% 수준으로, 평균 {local_format(diff)} 원 저렴하게 형성되었습니다.")
        else:
            est_val = up_val * 0.65
            insights.append(f"• [매매-반지하 추정] 인근 지상층 평균 매매가({local_format(up_val)}) 기준, 지하층(반지하) 적정 시세는 약 {local_format(est_val)} 원으로 추정됩니다 (감가율 65% 적용).")
        if avg_f_trade:
            f_val = avg_f_trade["avg_price"]
            ratio = f_val / up_val * 100
            diff = up_val - f_val
            insights.append(f"• [매매-1층 분석] 지상 1층 평균 매매가는 지상층(2층이상) 평균({local_format(up_val)}) 대비 약 {ratio:.1f}% 수준으로, 평균 {local_format(diff)} 원 차이를 보입니다.")
        else:
            est_val = up_val * 0.88
            insights.append(f"• [매매-1층 추정] 인근 지상층 평균 매매가({local_format(up_val)}) 기준, 지상 1층 적정 시세는 약 {local_format(est_val)} 원으로 추정됩니다 (감가율 88% 적용).")
    avg_u_jeonse = get_numeric_averages(upper_jeonses, is_rent=True); avg_b_jeonse = get_numeric_averages(base_jeonses, is_rent=True); avg_f_jeonse = get_numeric_averages(first_jeonses, is_rent=True)
    if avg_u_jeonse:
        up_val = avg_u_jeonse["avg_price"]
        if avg_b_jeonse:
            b_val = avg_b_jeonse["avg_price"]
            ratio = b_val / up_val * 100
            diff = up_val - b_val
            insights.append(f"• [전세-반지하 분석] 지하층 평균 전세가는 지상층(2층이상) 평균({local_format(up_val)}) 대비 약 {ratio:.1f}% 수준으로, 평균 {local_format(diff)} 원 낮게 형성되었습니다.")
        else:
            est_val = up_val * 0.65
            insights.append(f"• [전세-반지하 추정] 인근 지상층 평균 전세가({local_format(up_val)}) 기준, 지하층(반지하) 적정 전세 시세는 약 {local_format(est_val)} 원으로 추정됩니다 (65% 적용).")
        if avg_f_jeonse:
            f_val = avg_f_jeonse["avg_price"]
            ratio = f_val / up_val * 100
            diff = up_val - f_val
            insights.append(f"• [전세-1층 분석] 지상 1층 평균 전세가는 지상층(2층이상) 평균({local_format(up_val)}) 대비 약 {ratio:.1f}% 수준으로, 평균 {local_format(diff)} 원 차이가 납니다.")
        else:
            est_val = up_val * 0.88
            insights.append(f"• [전세-1층 추정] 인근 지상층 평균 전세가({local_format(up_val)}) 기준, 지상 1층 적정 전세 시세는 약 {local_format(est_val)} 원으로 추정됩니다 (88% 적용).")
    if avg_u_trade and avg_b_trade:
        b_val = avg_b_trade["avg_price"]
        est_up_val = b_val / 0.65
        insights.append(f"• [매매-지상층 추정] 인근 지하층 평균 매매가({local_format(b_val)}) 기준, 지상층(2층이상)의 적정 매매가는 약 {local_format(est_up_val)} 원으로 추정됩니다 (65% 보정 역산).")
    
    if avg_u_jeonse and avg_b_jeonse:
        b_val = avg_b_jeonse["avg_price"]
        est_up_val = b_val / 0.65
        insights.append(f"• [전세-지상층 추정] 인근 지하층 평균 전세가({local_format(b_val)}) 기준, 지상층(2층이상)의 적정 전세가는 약 {local_format(est_up_val)} 원으로 추정됩니다 (65% 보정 역산).")
    return insights
def save_briefing_report_pdf(address, trades, jeonses, wolses, prop_type_name, filename_pdf, apt_groups, period_label, is_expanded, target_build_year, target_area, target_floor, desired_info, expansion_mode):
    if expansion_mode == "auto":
        expansion_mode = CURRENT_EXPANSION_MODE
    if is_expanded and expansion_mode == "none":
        expansion_mode = "strict"
    masked_address = mask_address_string(address)
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib import colors
        import os
        font_paths = ["C:\\Windows\\Fonts\\malgun.ttf", "C:\\Windows\\Fonts\\gulim.ttc", "C:\\Windows\\Fonts\\batang.ttc", "C:\\Windows\\Fonts\\맑은.ttf"]
        registered = False
        for path in font_paths:
            if not os.path.exists(path):
                continue
            pdfmetrics.registerFont(TTFont("KoreanFont", path))
            registered = True
        if not registered:
            pdfmetrics.registerFont(TTFont("KoreanFont", "Helvetica"))
        doc = SimpleDocTemplate(filename_pdf, pagesize=A4, rightMargin=47, leftMargin=47, topMargin=40, bottomMargin=60)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("MainTitle", parent=styles["Normal"], fontName="KoreanFont", fontSize=20, leading=24, textColor=colors.HexColor("#1A365D"), alignment=1, spaceAfter=15, bold=True)
        h2_style = ParagraphStyle("SectionHeading", parent=styles["Normal"], fontName="KoreanFont", fontSize=11, leading=15, textColor=colors.HexColor("#2C5282"), spaceBefore=14, spaceAfter=6, bold=True)
        label_style = ParagraphStyle("MetaLabel", parent=styles["Normal"], fontName="KoreanFont", fontSize=9, leading=13, textColor=colors.HexColor("#4A5568"), bold=True)
        value_style = ParagraphStyle("MetaValue", parent=styles["Normal"], fontName="KoreanFont", fontSize=9, leading=13, textColor=colors.HexColor("#2D3748"))
        table_hdr_style = ParagraphStyle("TableHdr", parent=styles["Normal"], fontName="KoreanFont", fontSize=9, leading=12, textColor=colors.white, alignment=1, bold=True)
        table_cell_style = ParagraphStyle("TableCell", parent=styles["Normal"], fontName="KoreanFont", fontSize=9, leading=13, textColor=colors.HexColor("#2D3748"))
        table_cell_style_center = ParagraphStyle("TableCellCenter", parent=table_cell_style, alignment=1)
        table_cell_style_right = ParagraphStyle("TableCellRight", parent=table_cell_style, alignment=2)
        notice_title_style = ParagraphStyle("NoticeTitle", parent=styles["Normal"], fontName="KoreanFont", fontSize=9, leading=12, textColor=colors.HexColor("#718096"), bold=True, spaceBefore=15, spaceAfter=4)
        notice_body_style = ParagraphStyle("NoticeBody", parent=styles["Normal"], fontName="KoreanFont", fontSize=8, leading=12, textColor=colors.HexColor("#718096"))
        story = []
        accent_bar = Table([[""]], colWidths=[500], rowHeights=[4])
        accent_bar.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1A365D")), ("BOTTOMPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0)]))
        story.append(accent_bar)
        story.append(Spacer(1, 15))
        pdf_title = "인근 유사 매물 실거래 시세 브리핑" if is_expanded else "인근 실거래 시세 브리핑"
        story.append(Paragraph(pdf_title, title_style))
        story.append(Spacer(1, 10))
        meta_data = [[Paragraph("<b>조회 대상 주소</b>", label_style), Paragraph(masked_address, value_style)],
            
            [Paragraph("<b>부동산 유형</b>", label_style), Paragraph(prop_type_name, value_style)], [Paragraph("<b>분석 기준 기간</b>", label_style),

Paragraph(f"{period_label} (국토교통부 실거래가 기준)", value_style)]]
        if desired_info and desired_info.get("room_count_label"):
            meta_data.append([Paragraph("<b>분석 대상 방 개수</b>", label_style), Paragraph(desired_info["room_count_label"], value_style)])
        if target_floor is None:
            floor_lbl = f"지하 {abs(target_floor)}층" if target_floor < 0 else f"{target_floor}층"
            meta_data.append([Paragraph("<b>분석 대상 층수</b>", label_style), Paragraph(floor_lbl, value_style)])
        if is_expanded:
            cond_parts = []
            if expansion_mode == "relaxed":
                if target_build_year:
                    cond_parts.append(f"준공년도 ±5년 ({target_build_year - 5}~{target_build_year + 5}년)")
                if target_area:
                    cond_parts.append(f"전용면적 ±20% ({target_area * 0.8:.1f}~{target_area * 1.2:.1f}㎡)")
                cond_str = cond_parts and "동일 법정동 전체"
                cond_str += " (넓은 유사 범위)"
            elif target_build_year:
                cond_parts.append(f"준공년도 ±3년 ({target_build_year - 3}~{target_build_year + 3}년)")
            if target_area:
                cond_parts.append(f"전용면적 ±15% ({target_area * 0.85:.1f}~{target_area * 1.15:.1f}㎡)")
            cond_str = cond_parts and "동일 법정동 전체"
            cond_str += " (엄격한 유사 범위)"
            meta_data.append([Paragraph("<b>유사 매물 기준</b>", label_style), Paragraph(cond_str, value_style)])
        meta_data.append([Paragraph("<b>보고서 발행일</b>", label_style),

Paragraph(datetime.now().strftime("%Y년 %m월 %d일"), value_style)])
        meta_table = Table(meta_data, colWidths=[100, 400])
        meta_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")), ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),

("INNERGRID", (0, 0), (-1, -1), 0.5,

colors.HexColor("#EDF2F7")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6), ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12)]))
        story.append(meta_table)
        story.append(Spacer(1, 8))
        if is_expanded:
            explain_text = "※ 본 브리핑은 인근 유사 매물의 거래 사례를 포함하여 작성되었습니다."
            story.append(Paragraph(explain_text, ParagraphStyle("ExplainStyle", parent=styles["Normal"], fontName="KoreanFont", fontSize=8, textColor=colors.HexColor("#718096"), leading=10)))
            story.append(Spacer(1, 8))
        def build_summary_table(section_title, items, is_rent=False, is_wolse=False):
            sect_heading = Paragraph(section_title, h2_style); headers = [Paragraph("<b>면적 구분</b>", table_hdr_style), Paragraph("<b>거래 건수</b>", table_hdr_style), Paragraph("<b>실거래가 범위</b>", table_hdr_style), Paragraph("<b>평균 실거래가</b>", table_hdr_style), Paragraph("<b>전용 평단가</b>", table_hdr_style)]; table_content = [headers]; has_rows = False
            while prop_type_name == "아파트" and apt_groups:
                for g in apt_groups:
                    [t for t in items if not get_group_for_item(t, apt_groups) == g]
                    g_subset = None
                    t = None
                    stats = calculate_subset_stats(g_subset, is_rent, is_wolse)
                    if not stats:
                        continue
                    suffix = ""
                    table_content.append([Paragraph(g["label"], table_cell_style), Paragraph(f"{stats['count']}건", table_cell_style_center), Paragraph(stats["range"] + suffix, table_cell_style_right),
Paragraph(stats["avg"] + suffix, table_cell_style_right), Paragraph(stats["pyung_unit"], table_cell_style_right)])
                    has_rows = True
                break
            under_26 = []; between_26_43 = []; above_43 = []
            for item in items:
                area_val = item.get("excluUseAr") or item.get("totalFloorAr") or 0.0
                try: area = float(area_val)
                except: area = 0.0
                if area < 26.0: under_26.append(item)
                elif area < 43.0: between_26_43.append(item)
                else: above_43.append(item)
            
            size_categories = [("원룸/1.5룸형 (전용 26㎡ 미만)", under_26), ("투룸형 (전용 26㎡ ~ 43㎡ 미만)", between_26_43),
                               ("쓰리룸 이상형 (전용 43㎡ 이상)", above_43)]
            for label, subset in size_categories:
                stats = calculate_subset_stats(subset, is_rent, is_wolse)
                if not stats:
                    continue
                suffix = ""
                table_content.append([Paragraph(label, table_cell_style),
                                      Paragraph(f"{stats['count']}건", table_cell_style_center),
                                      Paragraph(stats["range"] + suffix, table_cell_style_right),
                                      Paragraph(stats["avg"] + suffix, table_cell_style_right),
                                      Paragraph(stats["pyung_unit"], table_cell_style_right)])
                has_rows = True
            
            if not has_rows:
                table_content.append([Paragraph(f"{period_label}간 신고된 거래 사례가 없습니다.", table_cell_style_center), "", "", "", ""])
            
            t = Table(table_content, colWidths=[150, 50, 120, 90, 90])
            t_style = [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
                       ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                       ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                       ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                       ("TOPPADDING", (0, 0), (-1, -1), 5),
                       ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0"))]
            if has_rows:
                for idx in range(1, len(table_content)):
                    bg_color = colors.HexColor("#FFFFFF") if idx % 2 == 1 else colors.HexColor("#F7FAFC")
                    t_style.append(("BACKGROUND", (0, idx), (-1, idx), bg_color))
            else:
                t_style.append(("SPAN", (0, 1), (-1, 1)))
                t_style.append(("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#FFFFFF")))
            t.setStyle(TableStyle(t_style))
            return (sect_heading, t)
        h, t = build_summary_table("■ [매매] 시세 요약", trades, is_rent=False)
        story.append(h)
        story.append(Spacer(1, 4))
        story.append(t)
        h, t = build_summary_table("■ [전세] 시세 요약", jeonses, is_rent=True)
        story.append(h)
        story.append(Spacer(1, 4))
        story.append(t)
        h, t = build_summary_table("■ [월세] 시세 요약 (보증금 + 월세 * 100 환산 기준)", wolses, is_rent=True, is_wolse=True)
        story.append(h)
        story.append(Spacer(1, 4))
        story.append(t)
        story.append(Spacer(1, 10))
        story.append(Paragraph("■ [층수별 & 개발구역 적정시세 분석 (CMA)]", h2_style))
        story.append(Spacer(1, 4))
        moa_status = check_moatown_and_redev(address)
        if moa_status["moatown"]:
            if moa_status["moatown_name"]:
                pass
        moa_display = "⚪ 미해당"
        if moa_status["redev"]:
            if moa_status["redev_name"]:
                pass
        redev_display = "⚪ 미해당"
        dev_table_data = [[Paragraph("<b>모아타운 지정</b>", label_style), Paragraph(moa_display, value_style), Paragraph("<b>재개발 정비구역</b>", label_style), Paragraph(redev_display, value_style)]]
        dev_table = Table(dev_table_data, colWidths=[100, 150, 100, 150])
        dev_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1),

colors.HexColor("#F7FAFC")),

("BOX", (0, 0), (-1, -1),

1,

colors.HexColor("#E2E8F0")), ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8)]))
        story.append(dev_table)
        story.append(Spacer(1, 6))
        cma_trades = filter_by_size_category(trades, target_area, prop_type_name, apt_groups)
        cma_jeonses = filter_by_size_category(jeonses, target_area, prop_type_name, apt_groups)
        cma_wolses = filter_by_size_category(wolses, target_area, prop_type_name, apt_groups)
        size_label = get_size_category_label(target_area, prop_type_name, apt_groups)
        story.append(Paragraph(f"<b>비교 기준 면적 구분</b>: {size_label}", value_style))
        story.append(Spacer(1, 4))
        base_trades, first_trades, upper_trades = classify_by_floor(cma_trades)
        base_jeonses, first_jeonses, upper_jeonses = classify_by_floor(cma_jeonses)
        base_wolses, first_wolses, upper_wolses = classify_by_floor(cma_wolses)
        floor_table_content = [[Paragraph("<b>층 구분</b>", table_hdr_style),

Paragraph("<b>매매 평균 (건수)</b>", table_hdr_style), Paragraph("<b>전세 평균 (건수)</b>", table_hdr_style), Paragraph("<b>월세 환산 평균 (건수)</b>", table_hdr_style)], [Paragraph("지하층 (반지하)", table_cell_style), Paragraph(get_avg_display(base_trades, is_rent=False), table_cell_style_center),

Paragraph(get_avg_display(base_jeonses, is_rent=True), table_cell_style_center), Paragraph(get_avg_display(base_wolses, is_rent=True, is_wolse=True), table_cell_style_center)], [Paragraph("지상 1층", table_cell_style), Paragraph(get_avg_display(first_trades, is_rent=False), table_cell_style_center),

Paragraph(get_avg_display(first_jeonses, is_rent=True), table_cell_style_center), Paragraph(get_avg_display(first_wolses, is_rent=True, is_wolse=True), table_cell_style_center)], [Paragraph("2층 이상 (지상층)", table_cell_style), Paragraph(get_avg_display(upper_trades, is_rent=False), table_cell_style_center),

Paragraph(get_avg_display(upper_jeonses, is_rent=True), table_cell_style_center), Paragraph(get_avg_display(upper_wolses, is_rent=True, is_wolse=True), table_cell_style_center)]]
        floor_table = Table(floor_table_content, colWidths=[110, 130, 130, 130])
        fl_table_style = [("BACKGROUND", (0, 0), (-1, 0),

colors.HexColor("#2B6CB0")), ("ALIGN", (0, 0), (-1, -1), "LEFT"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 5), ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0"))]
        for idx in range(1, 4):
            bg_color = colors.HexColor("#FFFFFF") if idx % 2 == 1 else colors.HexColor("#F7FAFC")
            fl_table_style.append(("BACKGROUND", (0, idx), (-1, idx), bg_color))
        f" ({moa_status["redev_name"]})" + ""
        floor_table.setStyle(TableStyle(fl_table_style))
        story.append(floor_table)
        story.append(Spacer(1, 6))
        insights_list = generate_comparison_insights(cma_trades, cma_jeonses, cma_wolses)
        insight_p_style = ParagraphStyle("InsightP", parent=styles["Normal"], fontName="KoreanFont", fontSize=8.5, leading=12.5, textColor=colors.HexColor("#2D3748"))
        insight_paragraphs = [Paragraph(ins, insight_p_style) for ins in insights_list]
        if not insight_paragraphs:
            insight_paragraphs = [Paragraph("• 충분한 비교 대상 거래 사례가 없어 자동 비율 분석을 생략합니다.", insight_p_style)]
        insight_box_data = [[p] for p in insight_paragraphs]
        insight_box = Table(insight_box_data, colWidths=[500])
        insight_box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFDF5")),

("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#ECC94B")), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8)]))
        story.append(insight_box)
        if desired_info:
            trade_type = desired_info.get("trade_type", "매매")
            d_price = desired_info.get("price", 0)
            d_monthly = desired_info.get("monthly_rent", 0)
            d_converted = d_price + (d_monthly * 100)
            
            def local_format_price(val):
                if val >= 10_000:
                    eok = int(val // 10_000)
                    man = int(val % 10_000)
                    if man > 0:
                        return f"{eok}억 {man:,}만"
                    return f"{eok}억"
                return f"{int(val):,}만"
                
            if trade_type == "월세":
                price_label_str = f"월세 {local_format_price(d_price)} / {local_format_price(d_monthly)}"
            else:
                price_label_str = f"{trade_type} {local_format_price(d_price)}"
            cma_trades = filter_by_size_category(trades, target_area, prop_type_name, apt_groups)
            cma_jeonses = filter_by_size_category(jeonses, target_area, prop_type_name, apt_groups)
            cma_wolses = filter_by_size_category(wolses, target_area, prop_type_name, apt_groups)
            if trade_type == "매매":
                match_list = cma_trades
            elif trade_type == "전세":
                match_list = cma_jeonses
            else:
                match_list = cma_wolses
            floor_cat = "upper"
            if target_floor is None:
                fl = int(target_floor)
                if fl < 0 or "지하" in str(target_floor):
                    floor_cat = "base"
                elif fl == 1:
                    floor_cat = "first"
                else:
                    floor_cat = "upper"
            ref_val, ref_desc = get_cma_ref_price(match_list, floor_cat, is_rent=trade_type != "매매", is_wolse=trade_type == "월세")
            story.append(Spacer(1, 10))
            story.append(Paragraph("■ [의뢰 희망가 시세 적정성 평가]", h2_style))
            story.append(Spacer(1, 4))
            eval_p_body = ParagraphStyle("EvalBodyStyle", parent=styles["Normal"], fontName="KoreanFont", fontSize=8.5, leading=13, textColor=colors.HexColor("#2D3748"))
            phone_no = desired_info.get("phone_number")
            phone_line = ""
            if phone_no:
                masked_phone = mask_phone_number(phone_no)
                phone_line = f"<b>• 의뢰인 연락처</b>: {masked_phone}<br/>"
                
            if not ref_val:
                eval_title = "보류 (비교 사례 부족)"
                detail_desc = "인근 지역 내 유사한 거래 사례가 부족하여 자동 적정성 평가가 제한적입니다."
                eval_color = "#718096"
                bg_color = colors.HexColor("#F7FAFC")
                border_color = colors.HexColor("#CBD5E0")
                ref_str = "판단 불가 (비교 사례 부족)"
            else:
                diff = d_converted - ref_val
                pct = diff / ref_val * 100
                ref_val_str = local_format_price(ref_val)
                diff_val_str = local_format_price(abs(diff))
                ref_str = f"{ref_val_str} ({ref_desc})"
                if abs(pct) <= 5.0:
                    eval_title = "적절함 (인근 시세 수준)"
                    detail_desc = f"희망 하시는 거래 조건은 인근 적정 시세 대비 약 {abs(pct):.1f}% 차이로 매우 적정합니다."
                    eval_color = "#38A169"
                    bg_color = colors.HexColor("#F0FFF4")
                    border_color = colors.HexColor("#9AE6B4")
                elif diff < 0:
                    eval_title = "저렴함 (시세 대비 가격경쟁력 우수)"
                    detail_desc = f"희망 하시는 거래 조건은 적정 시세 대비 약 {diff_val_str}({abs(pct):.1f}%) 저렴합니다."
                    eval_color = "#3182CE"
                    bg_color = colors.HexColor("#EBF8FF")
                    border_color = colors.HexColor("#90CDF4")
                else:
                    eval_title = "높음 (가격 조정 권장)"
                    detail_desc = f"희망 하시는 거래 조건은 적정 시세 대비 약 {diff_val_str}({pct:.1f}%) 높습니다. 조정이 필요합니다."
                    eval_color = "#E53E3E"
                    bg_color = colors.HexColor("#FFF5F5")
                    border_color = colors.HexColor("#FEB2B2")
                    
            eval_content = f"{phone_line}<b>• 의뢰 고객 희망 조건</b>: {price_label_str}<br/><b>• 적정 시세 기준선</b>: {ref_str}<br/><b>• 거래희망가 평가 결과</b>: <font color='{eval_color}'><b>{eval_title}</b></font><br/><b>• 종합 의견</b>: {detail_desc}"
            eval_box = Table([[Paragraph(eval_content, eval_p_body)]], colWidths=[500])
            eval_box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), bg_color), ("BOX", (0, 0), (-1, -1), 1, border_color), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8), ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10)]))
            story.append(eval_box)
        story.append(Spacer(1, 10))
        story.append(Paragraph("■ [안내] 시세 데이터 수집 및 분석 기준 안내", notice_title_style))
        story.append(Spacer(1, 4))
        notice_text = "• 아파트/다세대빌라/오피스텔: 입력 주소와 100% 동일 지번(단지/건물)의 실거래가 기준입니다.<br/>• 단독/다가구 주택:<br/>  - 매매: 지번 매칭 및 국토교통부 마스킹 범위 내 인접 필지 실거래가 기준입니다.<br/>  - 전월세: 국토교통부 지번 미제공 정책에 따라 동일 법정동 내 건축년도(±1년) 및 유형이 일치하는 인근 유사 주택의 거래 사례를 기준으로 자동 산출한 시세입니다.<br/>• 본 브리핑 자료는 중개업무 참고용으로 법적 효력을 가지지 않습니다."
        notice_box = Table([[Paragraph(notice_text, notice_body_style)]], colWidths=[500])
        notice_box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),

("BOX", (0, 0), (-1, -1), 0.5,

colors.HexColor("#E2E8F0")), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8), ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10)]))
        story.append(notice_box)
        def find_img_file(name):
            for d in (".", "scratch", ".."):
                for ext in (".png", ".jpg", ".jpeg"):
                    p_path = os.path.join(d, name + ext)
                    if os.path.exists(p_path):
                        return p_path
            return None
        center_bold_style = ParagraphStyle("FooterCenterBold", parent=styles["Normal"], fontName="KoreanFont", fontSize=11, leading=15, textColor=colors.HexColor("#1A365D"), alignment=1, bold=True)
        center_normal_style = ParagraphStyle("FooterCenterNormal", parent=styles["Normal"], fontName="KoreanFont", fontSize=9.5, leading=14, textColor=colors.HexColor("#4A5568"), alignment=1)
        italic_quote_style = ParagraphStyle("FooterItalicQuote", parent=styles["Normal"], fontName="KoreanFont", fontSize=11, leading=16, textColor=colors.HexColor("#2D3748"), alignment=1)
        def get_divider():
            t_div = Table([[""]], colWidths=[500], rowHeights=[1]); t_div.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
            return t_div
        story.append(Spacer(1, 15))
        story.append(get_divider())
        story.append(Spacer(1, 10))
        story.append(Paragraph("감사합니다.", center_bold_style))
        story.append(Spacer(1, 5))
        story.append(Paragraph("이번 분석이 도움이 되셨기를 바랍니다.", center_normal_style))
        story.append(Spacer(1, 10))
        story.append(get_divider())
        story.append(Spacer(1, 12))
        member = load_member_info() or {}
        m_name = format_member_name(member.get("name", "관리자"))
        m_phone = member.get("phone", "")
        m_addr = member.get("office_address", "")
        m_reg = member.get("registration_number", "")
        story.append(Paragraph(f"<b>{m_name}</b>", center_bold_style))
        story.append(Spacer(1, 8))
        profile_path = find_img_file("profile")
        profile_img = None
        if profile_path:
            from reportlab.platypus import Image
            profile_img = Image(profile_path, width=70, height=90)
        if profile_img:
            profile_row = Table([[profile_img]], colWidths=[500])
            profile_row.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
            story.append(profile_row)
            story.append(Spacer(1, 10))
        story.append(Paragraph("데이터 기반 부동산 분석<br/>매매 · 임대차 · 투자 상담", center_normal_style))
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"📞 {m_phone}", center_bold_style))
        story.append(Spacer(1, 10))
        addr_text = f"📍 {m_addr}"
        if m_reg:
            addr_text += f"<br/>등록번호: {m_reg}"
        story.append(Paragraph(addr_text, center_normal_style))
        story.append(Spacer(1, 10))
        kakao_path = find_img_file("kakao_qr")
        naver_path = find_img_file("naver_qr")
        kakao_img = None
        if kakao_path:
            from reportlab.platypus import Image
            kakao_img = Image(kakao_path, width=70, height=70)
        naver_img = None
        if naver_path:
            from reportlab.platypus import Image
            naver_img = Image(naver_path, width=70, height=70)
            
        if kakao_img or naver_img:
            cols = []
            widths = []
            if kakao_img:
                cols.append(kakao_img)
                widths.append(70)
            if kakao_img and naver_img:
                cols.append("")
                widths.append(20)
            if naver_img:
                cols.append(naver_img)
                widths.append(70)
            qr_table = Table([cols], colWidths=widths)
            qr_table.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
            qr_row = Table([[qr_table]], colWidths=[500])
            qr_row.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
            story.append(qr_row)
            story.append(Spacer(1, 12))
        
        story.append(get_divider())
        story.append(Spacer(1, 10))
        story.append(Paragraph('"데이터로 설명하고,<br/>신뢰로 연결합니다."', italic_quote_style))
        story.append(Spacer(1, 8))
        story.append(Paragraph("<b>SHINDAERIM PROPERTY INTELLIGENCE</b>", center_bold_style))
        def draw_page_decorations(canvas, doc_obj):
            try:
                canvas.saveState()
                member = load_member_info()
                if member:
                    m_name = format_member_name(member.get("name", ""))
                    m_phone = member.get("phone", "")
                    m_addr = member.get("office_address", "")
                    m_reg = member.get("registration_number", "")
                    if m_reg:
                        pass
                    reg_part = ""
                    office_info = f"{m_name} | {m_addr} | Tel: {m_phone}{reg_part}"
                else:
                    office_info = "신대림공인중개사사무소 | 서울 마포구 모래내로 7길 52 | Tel 02-375-4489 | HP 010-9128-0586"
                    if os.path.exists("office_info.txt"):
                        try:
                            with open("office_info.txt", "r", encoding="utf-8") as f:
                                content = f.read().strip()
                                if content:
                                    office_info = content
                        except:
                            pass
                
                canvas.setStrokeColor(colors.HexColor("#E2E8F0"))
                canvas.setLineWidth(0.5)
                canvas.line(47, 45, A4[0] - 47, 45)
                canvas.setFont("KoreanFont", 8)
                canvas.setFillColor(colors.HexColor("#718096"))
                canvas.drawString(47, 30, office_info)
                page_num_str = f"- {doc_obj.page} -"
                canvas.drawRightString(A4[0] - 47, 30, page_num_str)
                canvas.restoreState()
            except:
                pass
        
        doc.build(story, onFirstPage=draw_page_decorations, onLaterPages=draw_page_decorations)
        print(f"       -> PDF 파일 위치: {os.path.abspath(filename_pdf)}")
        pass
    except Exception as e:
        import traceback; traceback.print_exc()
        print(f"\n [오류] PDF 브리핑 파일 생성 중 오류 발생: {e}")
    kakao_img = None; naver_img = None
    
    try:
        pass
    except Exception as e:
        print(f"\n [오류] PDF 브리핑 파일 생성 중 오류 발생: {e}")
def save_briefing_report(address, trades, jeonses, wolses, prop_type_name, period_label="1년", is_expanded=False, target_build_year=None, target_area=None, target_floor=None, desired_info=None, expansion_mode="none"):
    try:
        if expansion_mode == "auto":
            expansion_mode = CURRENT_EXPANSION_MODE
        if is_expanded and expansion_mode == "none":
            expansion_mode = "strict"
        import os
        os.makedirs("시세브리핑", exist_ok=True)
        masked_address = mask_address_string(address)
        safe_addr = "".join([c for c in address if c not in (" ", "-", "_")]).strip()
        filename = f"시세브리핑/시세브리핑_{safe_addr.replace(" ", "_")}.txt"
        apt_groups = []
        if prop_type_name == "아파트":
            all_items = trades + jeonses + wolses
            apt_groups = get_apartment_size_groups(all_items)
        report_lines = []
        report_lines.append("================================================================================")
        if is_expanded:
            report_lines.append(f"          [ {masked_address} 인근 유사 매물 실거래 시세 브리핑 ]")
        else:
            report_lines.append(f"               [ {masked_address} 인근 실거래 시세 브리핑 ]")
        report_lines.append("================================================================================")
        report_lines.append(f"※ 본 자료는 국토교통부 {period_label} 실거래 내역을 분석한 결과입니다.")
        report_lines.append(f"※ 부동산 유형: {prop_type_name}")
        if desired_info and desired_info.get("room_count_label"):
            report_lines.append(f"※ 분석 대상 방 개수: {desired_info["room_count_label"]}")
        if target_floor is None:
            floor_lbl = f"지하 {abs(target_floor)}층" if target_floor < 0 else f"{target_floor}층"
            report_lines.append(f"※ 분석 대상 층수: {floor_lbl}")
        if is_expanded:
            cond_parts = []
            if expansion_mode == "relaxed":
                if target_build_year:
                    cond_parts.append(f"준공년도 ±5년 ({target_build_year - 5}~{target_build_year + 5}년)")
                if target_area:
                    cond_parts.append(f"전용면적 ±20% ({target_area * 0.8:.1f}~{target_area * 1.2:.1f}㎡)")
                cond_str = cond_parts and "동일 법정동 전체"
                report_lines.append("※ [확장 분석] 대상 지번 및 엄격한 조건의 실거래 데이터가 부족하여, 설득력 있는 시세 분석을 위해")
                report_lines.append("※             비교 범위를 넓은 기준의 유사 매물 사례로 확장하여 분석을 진행하였습니다.")
                report_lines.append(f"※ 유사 매물 기준 (넓음): {cond_str}")
            elif target_build_year:
                cond_parts.append(f"준공년도 ±3년 ({target_build_year - 3}~{target_build_year + 3}년)")
            if target_area:
                cond_parts.append(f"전용면적 ±15% ({target_area * 0.85:.1f}~{target_area * 1.15:.1f}㎡)")
            cond_str = cond_parts and "동일 법정동 전체"
            report_lines.append("※ [확장 분석] 대상 지번의 거래 사례 부족으로 동일 법정동 내 엄격한 기준의 유사 매물 사례를 분석하였습니다.")
            report_lines.append(f"※ 유사 매물 기준 (엄격): {cond_str}")
        report_lines.append("--------------------------------------------------------------------------------")
        def get_subset_info(subset, is_rent=False, is_wolse=False):
            stats = calculate_subset_stats(subset, is_rent, is_wolse)
            if not stats:
                return "거래 사례 없음"
            suffix = ""
            return f"\n      • 거래 건수: {stats["count"]}건\n      • 가격 범위: {stats["range"]}{suffix}\n      • 평균 가격: {stats["avg"]}{suffix}\n      • 전용 평단가: {stats["pyung_unit"]}"
        def group_items(items):
            under_26 = []; between_26_43 = []; above_43 = []
            if not items:
                return (under_26, between_26_43, above_43)
            for item in items:
                area_val = item.get("excluUseAr") or item.get("totalFloorAr") or 0.0
                try: area = float(area_val)
                except: area = 0.0
                if area < 26.0: under_26.append(item)
                elif area < 43.0: between_26_43.append(item)
                else: above_43.append(item)
            return (under_26, between_26_43, above_43)
        report_lines.append("■ [매매] 시세 요약")
        if prop_type_name == "아파트" and apt_groups:
            for idx, g in enumerate(apt_groups):
                g_trades = [t for t in trades if get_group_for_item(t, apt_groups) == g]
                report_lines.append(f"  {idx + 1}) {g['label']}: {get_subset_info(g_trades, is_rent=False)}")
        else:
            u26, b26_43, a43 = group_items(trades)
            report_lines.append(f"  1) 원룸/1.5룸형 (전용 26㎡ 미만): {get_subset_info(u26, is_rent=False)}")
            report_lines.append(f"  2) 투룸형 (전용 26㎡ ~ 43㎡ 미만): {get_subset_info(b26_43, is_rent=False)}")
            report_lines.append(f"  3) 쓰리룸 이상형 (전용 43㎡ 이상): {get_subset_info(a43, is_rent=False)}")
            
        report_lines.append("--------------------------------------------------------------------------------")
        report_lines.append("■ [전세] 시세 요약")
        if prop_type_name == "아파트" and apt_groups:
            for idx, g in enumerate(apt_groups):
                g_jeonses = [t for t in jeonses if get_group_for_item(t, apt_groups) == g]
                report_lines.append(f"  {idx + 1}) {g['label']}: {get_subset_info(g_jeonses, is_rent=True)}")
        else:
            u26_j, b26_43_j, a43_j = group_items(jeonses)
            report_lines.append(f"  1) 원룸/1.5룸형 (전용 26㎡ 미만): {get_subset_info(u26_j, is_rent=True)}")
            report_lines.append(f"  2) 투룸형 (전용 26㎡ ~ 43㎡ 미만): {get_subset_info(b26_43_j, is_rent=True)}")
            report_lines.append(f"  3) 쓰리룸 이상형 (전용 43㎡ 이상): {get_subset_info(a43_j, is_rent=True)}")
            
        report_lines.append("--------------------------------------------------------------------------------")
        report_lines.append("■ [월세] 시세 요약 (보증금 + 월세 * 100 환산 기준)")
        if prop_type_name == "아파트" and apt_groups:
            for idx, g in enumerate(apt_groups):
                g_wolses = [t for t in wolses if get_group_for_item(t, apt_groups) == g]
                report_lines.append(f"  {idx + 1}) {g['label']}: {get_subset_info(g_wolses, is_rent=True, is_wolse=True)}")
        else:
            u26_w, b26_43_w, a43_w = group_items(wolses)
            report_lines.append(f"  1) 원룸/1.5룸형 (전용 26㎡ 미만): {get_subset_info(u26_w, is_rent=True, is_wolse=True)}")
            report_lines.append(f"  2) 투룸형 (전용 26㎡ ~ 43㎡ 미만): {get_subset_info(b26_43_w, is_rent=True, is_wolse=True)}")
            report_lines.append(f"  3) 쓰리룸 이상형 (전용 43㎡ 이상): {get_subset_info(a43_w, is_rent=True, is_wolse=True)}")
        report_lines.append("--------------------------------------------------------------------------------")
        report_lines.append("■ [층수별 & 개발구역 적정시세 분석 (CMA)]")
        moa_info = check_moatown_and_redev(address)
        if moa_info["moatown"]:
            if moa_info["moatown_name"]:
                pass
        moa_val = "⚪ 미해당"
        if moa_info["redev"]:
            if moa_info["redev_name"]:
                pass
        redev_val = "⚪ 미해당"
        report_lines.append(f"  • 모아타운 지정 여부: {moa_val}")
        report_lines.append(f"  • 재개발 정비구역 여부: {redev_val}")
        report_lines.append("  • 층수별 실거래 평균가 비교:")
        report_lines.append("    ----------------------------------------------------------------------------")
        report_lines.append("    구분            | 매매 평균 (건수)        | 전세 평균 (건수)        | 월세 환산 평균 (건수)")
        report_lines.append("    ----------------------------------------------------------------------------")
        cma_trades = filter_by_size_category(trades, target_area, prop_type_name, apt_groups)
        cma_jeonses = filter_by_size_category(jeonses, target_area, prop_type_name, apt_groups)
        cma_wolses = filter_by_size_category(wolses, target_area, prop_type_name, apt_groups)
        size_label = get_size_category_label(target_area, prop_type_name, apt_groups)
        report_lines.append(f"  • 비교 기준 면적 구분: {size_label}")
        base_trades, first_trades, upper_trades = classify_by_floor(cma_trades)
        base_jeonses, first_jeonses, upper_jeonses = classify_by_floor(cma_jeonses)
        base_wolses, first_wolses, upper_wolses = classify_by_floor(cma_wolses)
        report_lines.append(f"    지하층(반지하)  | {get_avg_display(base_trades, False).ljust(22)} | {get_avg_display(base_jeonses, True).ljust(22)} | {get_avg_display(base_wolses, True, True)}")
        report_lines.append(f"    지상 1층        | {get_avg_display(first_trades, False).ljust(22)} | {get_avg_display(first_jeonses, True).ljust(22)} | {get_avg_display(first_wolses, True, True)}")
        report_lines.append(f"    2층 이상(지상층)| {get_avg_display(upper_trades, False).ljust(22)} | {get_avg_display(upper_jeonses, True).ljust(22)} | {get_avg_display(upper_wolses, True, True)}")
        report_lines.append("    ----------------------------------------------------------------------------")
        insights = generate_comparison_insights(cma_trades, cma_jeonses, cma_wolses)
        report_lines.append("  • 분석 및 적정 시세 가이드 (CMA Insights):")
        while insights:
            for ins in insights:
                report_lines.append(f"    {ins}")
            f" ({moa_info["redev_name"]})" + ""
            break
        report_lines.append("    - 충분한 비교 대상 거래 사례가 없어 자동 비율 분석을 생략합니다.")
        report_lines.append("--------------------------------------------------------------------------------")
        if desired_info:
            trade_type = desired_info.get("trade_type", "매매")
            d_price = desired_info.get("price", 0)
            d_monthly = desired_info.get("monthly_rent", 0)
            d_converted = d_price + (d_monthly * 100)
            def local_format_price(val):
                if val >= 10_000:
                    eok = int(val // 10_000)
                    man = int(val % 10_000)
                    if man > 0:
                        return f"{eok}억 {man:,}만"
                    return f"{eok}억"
                
                return f"{int(val):,}만"
            cma_trades = filter_by_size_category(trades, target_area, prop_type_name, apt_groups)
            cma_jeonses = filter_by_size_category(jeonses, target_area, prop_type_name, apt_groups)
            cma_wolses = filter_by_size_category(wolses, target_area, prop_type_name, apt_groups)
            
            if trade_type == "월세":
                price_label_str = f"월세 {local_format_price(d_price)} / {local_format_price(d_monthly)}"
            else:
                price_label_str = f"{trade_type} {local_format_price(d_price)}"
                
            if trade_type == "매매":
                match_list = cma_trades
            elif trade_type == "전세":
                match_list = cma_jeonses
            else:
                match_list = cma_wolses
            floor_cat = "upper"
            if target_floor is not None:
                try:
                    fl = int(target_floor)
                    if fl < 0 or "지하" in str(target_floor):
                        floor_cat = "base"
                    elif fl == 1:
                        floor_cat = "first"
                    else:
                        floor_cat = "upper"
                except: pass
            
            ref_val, ref_desc = get_cma_ref_price(match_list, floor_cat, is_rent=trade_type != "매매", is_wolse=trade_type == "월세")
            
            report_lines.append("■ [희망 거래가 분석 및 적정성 평가]")
            phone_no = desired_info.get("phone_number")
            if phone_no:
                masked_phone = mask_phone_number(phone_no)
                report_lines.append(f"  • 의뢰인 연락처  : {masked_phone}")
                
            if d_converted == 0:
                report_lines.append("  • 의뢰 고객 희망 조건: 미지정 (시세 정보 브리핑)")
                report_lines.append("  • 거래희망가 평가 결과: 생략")
                report_lines.append("  • 종합 의견: 고객의 희망 거래가 정보가 입력되지 않아 적정성 평가를 생략합니다. 본 자료는 단순 시세 정보 (인근 시세 및 실거래 브리핑) 목적으로 활용하시기 바랍니다.")
            else:
                report_lines.append(f"  • 의뢰 고객 희망 조건: {price_label_str}")
                
                if not ref_val:
                    report_lines.append(f"  • 적정 시세 기준선  : 판단 불가 (비교 사례 부족)")
                else:
                    report_lines.append(f"  • 적정 시세 기준선  : {local_format_price(ref_val)} ({ref_desc})")
                
                if ref_val:
                    diff = d_converted - ref_val
                    pct = diff / ref_val * 100
                    ref_val_str = local_format_price(ref_val)
                    diff_val_str = local_format_price(abs(diff))
                    if abs(pct) <= 5.0:
                        eval_title = "적절함 (인근 시세 수준)"
                        detail_desc = f"희망 하시는 거래 조건은 인근 적정 시세({ref_val_str}, {ref_desc} 기준) 대비 약 {abs(pct):.1f}% 차이로, 현재 시장 가격대 범위 내에서 매우 적정하게 책정된 상태입니다."
                    elif diff < 0:
                        eval_title = "저렴함 (시세 대비 가격경쟁력 우수)"
                        detail_desc = f"희망 하시는 거래 조건은 인근 적정 시세({ref_val_str}, {ref_desc} 기준) 대비 약 {diff_val_str} ({abs(pct):.1f}%) 저렴하게 책정되어 있습니다. 시장 진입 시 빠른 거래 성사가 예상되어 가격 경쟁력이 높습니다."
                    else:
                        eval_title = "높음 (가격 조정 권장)"
                        detail_desc = f"희망 하시는 거래 조건은 인근 적정 시세({ref_val_str}, {ref_desc} 기준) 대비 약 {diff_val_str} ({pct:.1f}%) 높게 책정되어 있습니다. 거래 성사 및 빠른 중개를 위해 의뢰인과의 상의를 통한 가격 조정을 권장합니다."
                else:
                    eval_title = "보류 (비교 사례 부족)"
                    detail_desc = "인근 지역 내 유사한 거래 사례(동일 면적대 및 층수별 사례)가 부족하여 자동 적정성 평가가 제한적입니다. 주변 법정동 및 대체 매물 시세를 추가로 고려하시기 바랍니다."
                report_lines.append(f"  • 거래희망가 평가 결과: {eval_title}")
                report_lines.append(f"  • 종합 의견: {detail_desc}")
            report_lines.append("--------------------------------------------------------------------------------")
        report_lines.append("■ [안내] 시세 데이터 수집 및 분석 기준 안내")
        report_lines.append("  • 아파트/다세대빌라/오피스텔: 입력 주소와 100% 동일 지번(단지/건물)의 실거래가 기준입니다.")
        report_lines.append("  • 단독/다가구 주택:")
        report_lines.append("    - 매매: 지번 매칭 및 국토교통부 마스킹 범위 내 인접 필지 실거래가 기준입니다.")
        report_lines.append("    - 전월세: 국토교통부 지번 미제공 정책에 따라 동일 법정동 내 건축년도(±1년) 및 유형이 일치하는")
        report_lines.append("             인근 유사 주택의 거래 사례를 기준으로 자동 산출한 시세입니다.")
        report_lines.append("================================================================================")
        report_lines.append("※ 본 브리핑 자료는 중개업무 참고용으로 법적 효력을 가지지 않습니다.")
        report_lines.append("================================================================================")
        console_content = "\n".join(report_lines)
        member = load_member_info()
        if member:
            m_name = format_member_name(member.get("name", ""))
            m_phone = member.get("phone", "")
            m_addr = member.get("office_address", "")
            m_reg = member.get("registration_number", "")
            phone_line = f"📞 {m_phone}"
            addr_lines = [f"📍 {m_addr}"]
            if m_reg:
                addr_lines.append(f"등록번호: {m_reg}")
        else:
            m_name = "조항준 공인중개사"
            phone_line = "📞 010-9128-0586\n☎ 02-375-4489"
            addr_lines = ["📍 서울 마포구 모래내로 7길 52"]
        report_lines.append("──────────────────────────────")
        report_lines.append("")
        report_lines.append("        감사합니다.")
        report_lines.append("")
        report_lines.append("이번 분석이 도움이 되셨기를 바랍니다.")
        report_lines.append("")
        report_lines.append("──────────────────────────────")
        report_lines.append("")
        report_lines.append(m_name)
        report_lines.append("")
        report_lines.append("데이터 기반 부동산 분석")
        report_lines.append("매매 · 임대차 · 투자 상담")
        report_lines.append("")
        report_lines.append(phone_line)
        report_lines.append("")
        for al in addr_lines:
            report_lines.append(al)
        report_lines.append("")
        report_lines.append("──────────────────────────────")
        report_lines.append("")
        report_lines.append('"데이터로 설명하고,')
        report_lines.append('신뢰로 연결합니다."')
        report_lines.append("")
        report_lines.append("SHINDAERIM PROPERTY INTELLIGENCE")
        report_content = "\n".join(report_lines)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_content)
        print("\n [알림] 시세 브리핑 자료가 성공적으로 저장되었습니다!")
        print(f"       -> 텍스트 파일 위치: {os.path.abspath(filename)}")
        pdf_filename = filename.replace(".txt", ".pdf")
        save_briefing_report_pdf(address, trades, jeonses, wolses, prop_type_name, pdf_filename, apt_groups, period_label, is_expanded, target_build_year, target_area, target_floor=target_floor, desired_info=desired_info, expansion_mode=expansion_mode)
        import shutil
        unified_dir = "종합분석보고서"
        os.makedirs(unified_dir, exist_ok=True)
        unified_txt = os.path.join(unified_dir, f"시세브리핑_{safe_addr.replace(' ', '_')}.txt")
        unified_pdf = os.path.join(unified_dir, f"시세브리핑_{safe_addr.replace(' ', '_')}.pdf")
        shutil.copy2(filename, unified_txt)
        if os.path.exists(pdf_filename):
            shutil.copy2(pdf_filename, unified_pdf)
        print("       -> 종합분석보고서 통합 폴더에도 복사본이 저장되었습니다.")
    except Exception as e:
        import traceback; traceback.print_exc()
        print(f"\n [오류] 브리핑 파일 저장 중 오류 발생: {e}")
def print_comparison_table(transactions, prop_type, target_floor, target_area, address_name, sigunguCd, bun, ji, bjdong_nm, target_build_year, target_house_type, save_report, desired_info):
    global CURRENT_EXPANSION_MODE
    is_expanded = False; expansion_mode = "none"; CURRENT_EXPANSION_MODE = "none"
    try:
        type_names = {"1": "아파트", "2": "연립/다세대/빌라", "3": "오피스텔", "4": "단독/다가구"}
        prop_type_name = type_names.get(prop_type, "일반 부동산")
        trades_initial = [t for t in transactions if t.get("_trade_type") == "매매"]
        t_24_initial = len(trades_initial)
        tot_24_initial = len(transactions)
        
        if sigunguCd and bjdong_nm:
            if tot_24_initial < 3 or t_24_initial <= 1:
                print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print(f" ⚠️ 조회하신 지번의 실거래 데이터가 부족합니다 (최근 24개월 매매 {t_24_initial}건 / 전체 {tot_24_initial}건).")
                print("    동일 법정동 내 유사 조건의 인근 매물 실거래 사례로 범위를 확장할 수 있습니다.")
                print("    [선택안내]")
                print("    1. 엄격한 유사 기준 (권장 - 준공년도 ±3년, 전용면적 ±15%이내)")
                print("    2. 넓은 유사 기준 (비교 사례 부족 시 - 준공년도 ±5년, 전용면적 ±20%이내)")
                print("    3. 확장하지 않음 (해당 지번의 거래만 표시)")
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                if True:
                    expand_choice = input("[입력] 분석 범위를 선택하세요 (1: 엄격한 기준 | 2: 넓은 기준 | 3: 미확장) [기본값: 1]: ").strip()
                    if not expand_choice:
                        expand_choice = "1"
                    if expand_choice == "1":
                        print(" -> 인근 유사 매물 데이터 수집 중 (엄격한 기준: 준공년도 ±3년, 전용면적 ±15%)...")
                        expanded_txs = get_recent_transactions(sigunguCd, bun, ji, prop_type, bjdong_nm, target_build_year=target_build_year, target_house_type=target_house_type, expand_similar=True, target_area=target_area, build_year_margin=3, area_margin=0.15)
                    if expand_choice == "2":
                        print(" -> 인근 유사 매물 데이터 수집 중 (넓은 기준: 준공년도 ±5년, 전용면적 ±20%)...")
                        expanded_txs = get_recent_transactions(sigunguCd, bun, ji, prop_type, bjdong_nm, target_build_year=target_build_year, target_house_type=target_house_type, expand_similar=True, target_area=target_area, build_year_margin=5, area_margin=0.2)
                        if expanded_txs:
                            transactions = expanded_txs
                            is_expanded = True
                            expansion_mode = "relaxed"
                            print(f" -> 넓은 기준의 유사 매물 {len(transactions)}건을 발견하여 분석을 진행합니다.")
                        else:
                            print(" -> 넓은 기준 조건의 유사 매물도 존재하지 않아 확장을 생략합니다.")
                    CURRENT_EXPANSION_MODE = expansion_mode
                    if not transactions:
                        print_empty_transactions_explanation(prop_type)
                        type_names = {"1": "아파트", "2": "연립/다세대/빌라", "3": "오피스텔", "4": "단독/다가구"}
                        prop_type_name = type_names.get(prop_type, "일반 부동산")
                        if save_report:
                            display_addr = address_name and "조회 대상 주소"
                            save_briefing_report(display_addr, [], [], [], prop_type_name, "최근 24개월", is_expanded=is_expanded, target_build_year=target_build_year, target_area=target_area, target_floor=target_floor, desired_info=desired_info, expansion_mode=expansion_mode)
                        return ([], [], [],
                            prop_type_name, "최근 24개월", is_expanded)
                    trades_full = [t for t in transactions if t.get("_trade_type") == "매매"]
                    jeonses_full = [t for t in transactions if t.get("_trade_type") == "전세"]
                    wolses_full = [t for t in transactions if t.get("_trade_type") == "월세"]
                    def count_in_months(items, limit):
                        try:
                            now = datetime.now()
                            cnt = 0
                            for item in items:
                                yr = int(item.get("dealYear", 0))
                                mo = int(item.get("dealMonth", 0))
                                if ((now.year) - yr) * 12 + (now.month) - mo < limit:
                                    cnt += 1
                                    continue
                            return cnt
                        except:
                            pass
                    t_6 = count_in_months(trades_full, 6)
                    j_6 = count_in_months(jeonses_full, 6)
                    w_6 = count_in_months(wolses_full, 6)
                    tot_6 = t_6 + j_6 + w_6
                    t_12 = count_in_months(trades_full, 12)
                    j_12 = count_in_months(jeonses_full, 12)
                    w_12 = count_in_months(wolses_full, 12)
                    tot_12 = t_12 + j_12 + w_12
                    t_24 = len(trades_full)
                    j_24 = len(jeonses_full)
                    w_24 = len(wolses_full)
                    tot_24 = t_24 + j_24 + w_24
                    print("\n======================================================================")
                    if is_expanded:
                        print(" [인근 유사 매물 실거래 수집 건수 요약 (최근 24개월)]")
                    else:
                        print(" [실거래 수집 건수 요약 (최근 24개월)]")
                    print("----------------------------------------------------------------------")
                    print(f" - 최근  6개월: 매매 {t_6}건 / 전세 {j_6}건 / 월세 {w_6}건 (총 {tot_6}건)")
                    print(f" - 최근 12개월: 매매 {t_12}건 / 전세 {j_12}건 / 월세 {w_12}건 (총 {tot_12}건)")
                    print(f" - 최근 24개월: 매매 {t_24}건 / 전세 {j_24}건 / 월세 {w_24}건 (총 {tot_24}건)")
                    if desired_info and desired_info.get("room_count_label"):
                        print(f" * 분석 대상 방 개수: {desired_info["room_count_label"]}")
                    if target_floor is None:
                        floor_lbl = f"지하 {abs(target_floor)}층" if target_floor < 0 else f"{target_floor}층"
                        print(f" * 분석 대상 층수  : {floor_lbl}")
                    print("======================================================================")
                    default_opt = "3"
                    print(" * 기본 분석 기간: 최근 2년 (24개월) [기본값: 3]")
                    user_choice = input("[입력] 분석에 사용할 기간을 선택하세요 (1: 6개월 | 2: 1년 | 3: 2년): ").strip()
                    if not user_choice:
                        user_choice = default_opt
                    if user_choice == "1":
                        selected_limit = 6
                        selected_label = "최근 6개월"
                    elif user_choice == "3":
                        selected_limit = 24
                        selected_label = "최근 24개월"
                    else:
                        selected_limit = 12
                        selected_label = "최근 12개월(1년)"
                    print(f" -> [{selected_label}] 기준으로 분석 및 브리핑 보고서를 생성합니다.")
                    def filter_by_months(items, limit):
                        try:
                            now = datetime.now()
                            filtered = []
                            for item in items:
                                yr = int(item.get("dealYear", 0))
                                mo = int(item.get("dealMonth", 0))
                                if ((now.year) - yr) * 12 + (now.month) - mo < limit:
                                    filtered.append(item)
                                    continue
                            return filtered
                        except:
                            pass
                    transactions = filter_by_months(transactions, selected_limit)
                    if not transactions:
                        print_empty_transactions_explanation(prop_type)
                        type_names = {"1": "아파트", "2": "연립/다세대/빌라", "3": "오피스텔", "4": "단독/다가구"}
                        prop_type_name = type_names.get(prop_type, "일반 부동산")
                        if save_report:
                            display_addr = address_name and "조회 대상 주소"
                            save_briefing_report(display_addr, [], [], [], prop_type_name, selected_label, is_expanded=is_expanded, target_build_year=target_build_year, target_area=target_area, target_floor=target_floor, desired_info=desired_info, expansion_mode=expansion_mode)
                        return ([], [], [],
                            prop_type_name, selected_label, is_expanded)
                    apt_groups = []
                    if prop_type == "1":
                        apt_groups = get_apartment_size_groups(transactions)
                    def format_single_price(val):
                        if val >= 10_000:
                            eok = int(val // 10_000)
                            man = int(val % 10_000)
                            if man > 0:
                                return f"{eok}억 {man:,}만"
                            return f"{eok}억"
                        
                        return f"{int(val):,}만"
                    def format_pyung_price(val):
                        val = round(val)
                        if val >= 10_000:
                            eok = val // 10_000
                            man = val % 10_000
                            if man > 0:
                                return f"평당 {eok}억 {man:,}만"
                            return f"평당 {eok}억"
                        
                        return f"평당 {val:,}만"
                    def print_grouped_stats(items, label_prefix, is_rent, is_wolse):
                        if not items:
                            return
                        under_26 = []; between_26_43 = []; above_43 = []
                        for item in items:
                            area_val = item.get("excluUseAr") or item.get("totalFloorAr") or 0.0
                            try: area = float(area_val)
                            except: area = 0.0
                            if area < 26.0: under_26.append(item)
                            elif area < 43.0: between_26_43.append(item)
                            else: above_43.append(item)
                        print(divider_line)
                        print(f" [평균 및 가격 범위 요약] 전체 {len(items)}건 중:")
                        def print_subset_stats(subset, group_name):
                            if not subset:
                                print(f"   • {group_name}: 거래 사례 없음")
                                return
                            sum_price_for_area = 0; sum_area_pyung = 0.0; count_area = 0; sum_price_for_land = 0; sum_land_pyung = 0.0; count_land = 0; area_unit_prices = []; land_unit_prices = []; trade_amts = []
                            for item in subset:
                                _, amt, _ = format_price(item, is_rent=is_rent)
                                if not amt:
                                    continue
                                trade_amts.append(amt)
                                area_val = item.get("excluUseAr") or item.get("totalFloorAr") or 0.0
                                try: area = float(area_val)
                                except: area = 0.0
                                if area > 0:
                                    sum_price_for_area += amt
                                    sum_area_pyung += area * 0.3025
                                    count_area += 1
                                    area_unit_prices.append(amt / (area * 0.3025))
                                    
                                land_val = item.get("landAr") or 0.0
                                try: land_area = float(land_val)
                                except: land_area = 0.0
                                if land_area > 0:
                                    sum_price_for_land += amt
                                    sum_land_pyung += land_area * 0.3025
                                    count_land += 1
                                    land_unit_prices.append(amt / (land_area * 0.3025))
                                    
                            price_range_str = ""
                            if trade_amts:
                                min_amt = min(trade_amts)
                                max_amt = max(trade_amts)
                                if min_amt == max_amt:
                                    price_range_str = format_single_price(min_amt)
                                else:
                                    price_range_str = f"{format_single_price(min_amt)} ~ {format_single_price(max_amt)}"
                            avg_area_str = "계산 불가"
                            if count_area > 0 and sum_area_pyung > 0:
                                avg_area_price = round(sum_price_for_area / sum_area_pyung)
                                avg_area_str = format_pyung_price(avg_area_price)
                                if area_unit_prices:
                                    min_u = min(area_unit_prices)
                                    max_u = max(area_unit_prices)
                                    if round(min_u) != round(max_u):
                                        avg_area_str += f" (최저 {format_pyung_price(min_u)} ~ 최고 {format_pyung_price(max_u)})"
                            avg_land_str = "계산 불가"
                            if count_land > 0 and sum_land_pyung > 0:
                                avg_land_price = round(sum_price_for_land / sum_land_pyung)
                                avg_land_str = format_pyung_price(avg_land_price)
                                if land_unit_prices:
                                    min_u = min(land_unit_prices)
                                    max_u = max(land_unit_prices)
                                    if round(min_u) != round(max_u):
                                        avg_land_str += f" (최저 {format_pyung_price(min_u)} ~ 최고 {format_pyung_price(max_u)})"
                            print(f"   • {group_name} - 총 {len(subset)}건:")
                            if price_range_str:
                                suffix = ""
                                print(f"     - {label_prefix} 범위: {price_range_str}{suffix}")
                            print(f"     - 전용 평단가: {avg_area_str}")
                            if count_land > 0:
                                print(f"     - 지분 평단가: {avg_land_str}")
                                return
                        if prop_type == "1" and apt_groups:
                            for g in apt_groups:
                                g_items = [t for t in items if get_group_for_item(t, apt_groups) == g]
                                print_subset_stats(g_items, g["label"])
                        else:
                            print_subset_stats(under_26, "전용 26㎡ 미만 (원룸/1.5룸형)")
                            print_subset_stats(between_26_43, "전용 26㎡ 이상 ~ 43㎡ 미만 (투룸형)")
                            print_subset_stats(above_43, "전용 43㎡ 이상 (쓰리룸 이상형)")
                        print("═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════")
                    if prop_type == "4":
                        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        print(" [안내] 단독/다가구 임대차(전월세) 실거래 정보 안내")
                        print(" 1. 단독/다가구 임대차 API는 국토교통부 보안 정책상 상세 지번(번지수) 정보를 제공하지 않습니다.")
                        print(" 2. 따라서, 본 시스템은 입력하신 주소와 동일한 법정동 내에서 '유사한 건축년도 및 주택유형'의 모든 거래 사례를")
                        print("    대안으로 수집하여 보여줍니다. (특정 단독 주택 단 한 곳만의 전월세 거래 내역이 아닙니다.)")
                        print(" 3. 매매 실거래 정보는 상세 지번 매칭이 적용되나, 마스킹 범위(예: 2**)에 따라 인근 거래가 포함될 수 있습니다.")
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    [t for t in transactions if not t.get("_trade_type") == "매매"]
                    trades = address_name
                    t = None
                    [t for t in transactions if not t.get("_trade_type") == "전세"]
                    jeonses = None
                    t = None
                    [t for t in transactions if not t.get("_trade_type") == "월세"]
                    wolses = None
                    t = None
                    def get_sort_key(item):
                        area_val = item.get("excluUseAr") or item.get("totalFloorAr") or 0.0
                        try:
                            area = float(area_val)
                        except:
                            area = 0.0
                        try:
                            y = int(item.get("dealYear", 0))
                            m = int(item.get("dealMonth", 0))
                            d = int(item.get("dealDay", 0))
                        except:
                            y, m, d = 0, 0, 0
                        return (area, -y, -m, -d)
                    trades.sort(key=get_sort_key)
                    jeonses.sort(key=get_sort_key)
                    wolses.sort(key=get_sort_key)
                    target_str = []
                    if target_floor is None:
                        target_str.append(f"{target_floor}층")
                    if target_area is None:
                        pyung = round(target_area * 0.3025, 1)
                        target_str.append(f"{target_area:.2f}㎡({pyung}평)")
                    target_desc = target_str and ""
                    def get_terminal_width(text):
                        w = 0
                        for c in text:
                            if ord(c) > 127:
                                w += 2
                                continue
                            w += 1
                        return w
                    def pad_double_width(text, width, align):
                        text = str(text); w = get_terminal_width(text)
                        if w >= width:
                            return text
                        pad_len = width - w
                        if align == "right":
                            return " " * pad_len + text
                        elif align == "left":
                            return text + " " * pad_len
                        left_pad = pad_len // 2; right_pad = pad_len - left_pad
                        return " " * left_pad + text + " " * right_pad
                    def get_pyung_price_str(amt_val, rent_val, area):
                        if area or area <= 0:
                            return ""
                        try:
                            r_val = rent_val and 0
                            converted = amt_val + r_val * 100
                            pyung_area = area * 0.3025
                            pyung_price = round(converted / pyung_area)
                            if pyung_price >= 10_000:
                                eok = pyung_price // 10_000
                                man = pyung_price % 10_000
                                if man > 0:
                                    return f"평당 {eok}억 {man:,}만"
                                return f"평당 {eok}억"
                            return f"평당 {pyung_price:,}만"
                        except:
                            pass
                        
                        return ""
                    col_seq = pad_double_width("순번", 4, "center")
                    col_date = pad_double_width("계약일", 10, "center")
                    col_type = pad_double_width("유형", 4, "center")
                    col_price = pad_double_width("거래금액", 26, "center")
                    col_area = pad_double_width("전용면적(평)", 18, "center")
                    col_land = pad_double_width("토지지분(평)", 18, "center")
                    col_floor = pad_double_width("동/층", 11, "center")
                    col_comp = "비교 (기준 대비 차이)"
                    header_line = f" {col_seq} | {col_date} | {col_type} | {col_price} | {col_area} | {col_land} | {col_floor} | {col_comp}"
                    divider_line = "-------------------------------------------------------------------------------------------------------------------------------------"
                    if trades:
                        print("\n═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════")
                        title_text = f"[ 해당 지번/인근 최근 실거래 매매 내역{target_desc} ]" if prop_type == "4" else f"[ 해당 지번 최근 실거래 매매 내역{target_desc} ]"
                        print(pad_double_width(title_text, 133, "center"))
                        print("═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════")
                        print(header_line)
                        print(divider_line)
                        printed_under_26_header = False
                        printed_26_43_header = False
                        printed_above_43_header = False
                        printed_groups = set()
                        for idx, item in enumerate(trades):
                            price_display, amt_val, _ = format_price(item, is_rent=False)
                            if not item.get("excluUseAr"):
                                item.get("excluUseAr")
                            area_val = item.get("totalFloorAr")
                            area = None
                            if area_val is None:
                                area = float(area_val)
                                pyung = round(area * 0.3025, 1)
                                area_display = f"{area:.2f}㎡ ({pyung}평)"
                            else:
                                area_display = "-"
                            if prop_type == "1" and apt_groups:
                                g = get_group_for_item(item, apt_groups)
                                if g and g["label"] not in printed_groups:
                                    print("-------------------------------------------------------------------------------------------------------------------------------------")
                                    print(pad_double_width(f"▼ {g["label"]} ▼", 133, "center"))
                                    print("-------------------------------------------------------------------------------------------------------------------------------------")
                                    printed_groups.add(g["label"])
                                elif area is None:
                                    if not area < 26.0 and printed_under_26_header:
                                        print("-------------------------------------------------------------------------------------------------------------------------------------")
                                        print(pad_double_width("▼ 전용 26㎡ 미만 (원룸/1.5룸형) ▼", 133, "center"))
                                        print("-------------------------------------------------------------------------------------------------------------------------------------")
                                        printed_under_26_header = True
                                    elif not 26.0 <= area < 43.0 and printed_26_43_header:
                                        print("-------------------------------------------------------------------------------------------------------------------------------------")
                                        print(pad_double_width("▼ 전용 26㎡ 이상 ~ 43㎡ 미만 (투룸형) ▼", 133, "center"))
                                        print("-------------------------------------------------------------------------------------------------------------------------------------")
                                        printed_26_43_header = True
                                    elif not area >= 43.0 and printed_above_43_header:
                                        print("-------------------------------------------------------------------------------------------------------------------------------------")
                                        print(pad_double_width("▼ 전용 43㎡ 이상 (쓰리룸 이상형) ▼", 133, "center"))
                                        print("-------------------------------------------------------------------------------------------------------------------------------------")
                                        printed_above_43_header = True
                            land_val = item.get("landAr")
                            land_display = "-"
                            if land_val is None:
                                land_area = float(land_val)
                                if land_area > 0:
                                    land_pyung = round(land_area * 0.3025, 1)
                                    land_display = f"{land_area:.2f}㎡ ({land_pyung}평)"
                            price_display_with_pyung = price_display
                            floor_str = str(item.get("floor", "")).strip()
                            dong_info = str(item.get("aptDong", "")).strip()
                            if dong_info:
                                if not dong_info.endswith("동"):
                                    dong_info = dong_info + "동"
                                dong_prefix = f"{dong_info} "
                            else:
                                dong_prefix = ""
                            floor = int(floor_str)
                            floor_display = f"{dong_prefix}{floor}층"
                            year = item.get("dealYear", "")
                            month = str(item.get("dealMonth", "")).zfill(2)
                            day = str(item.get("dealDay", "")).zfill(2)
                            date_str = f"{year}-{month}-{day}"
                            diff_parts = []
                            if target_floor is not None or target_area is None:
                                if target_floor is None and floor is None:
                                    floor_diff = floor - target_floor
                                    if floor_diff > 0:
                                        diff_parts.append(f"+{floor_diff}층")
                                    elif floor_diff < 0:
                                        diff_parts.append(f"{floor_diff}층")
                                    else:
                                        diff_parts.append("층동일")
                                if target_area is None and area is None:
                                    area_diff = area - target_area
                                    if abs(area_diff) > 0.01:
                                        if area_diff > 0:
                                            pass
                                        diff_parts.append("+", f"{""}{area_diff:.2f}㎡")
                                    else:
                                        diff_parts.append("면적동일")
                                if diff_parts:
                                    pass
                                comparison = "층/면적 동일"
                            elif idx == 0:
                                base_price = amt_val
                                base_floor = floor
                                base_area = area
                                comparison = "★ 기준 (가장 최근 거래)"
                            elif base_price is None and amt_val is None:
                                price_diff = base_price - amt_val
                                if price_diff > 0:
                                    diff_parts.append(f"매매가 +{price_diff:,}만")
                                elif price_diff < 0:
                                    diff_parts.append(f"매매가 {price_diff:,}만")
                                else:
                                    diff_parts.append("매매가동일")
                            if base_floor is None and floor is None:
                                floor_diff = base_floor - floor
                                if floor_diff > 0:
                                    diff_parts.append(f"+{floor_diff}층")
                                elif floor_diff < 0:
                                    diff_parts.append(f"{floor_diff}층")
                                else:
                                    diff_parts.append("층동일")
                            if base_area is None and area is None:
                                area_diff = base_area - area
                                if abs(area_diff) > 0.01:
                                    if area_diff > 0:
                                        pass
                                    diff_parts.append("+", f"{""}{area_diff:.2f}㎡")
                                else:
                                    diff_parts.append("면적동일")
                            comparison = ", ".join(diff_parts)
                            seq_display = pad_double_width(idx + 1, 4, "center")
                            date_display = pad_double_width(date_str, 10, "center")
                            type_display = pad_double_width("매매", 4, "center")
                            price_display_padded = pad_double_width(price_display_with_pyung, 26, "right")
                            area_display_padded = pad_double_width(area_display, 18, "right")
                            land_display_padded = pad_double_width(land_display, 18, "right")
                            floor_display_padded = pad_double_width(floor_display, 11, "right")
                            print(f" {seq_display} | {date_display} | {type_display} | {price_display_padded} | {area_display_padded} | {land_display_padded} | {floor_display_padded} | {comparison}")
                        ", ".join(diff_parts)
                        print_grouped_stats(trades, "실거래가", is_rent=False, is_wolse=False)
                    elif getattr(transactions, "trade_permission_error", False):
                        print("\n [!] 실거래 매매 API 권한 오류(403 Forbidden)로 인해 매매 내역을 가져오지 못했습니다.")
                        print("     (공공데이터포털에서 해당 매매 API 활용신청 상태를 확인해 주세요.)")
                    else:
                        print("\n [참고] 최근 12개월 동안 해당 지번의 신고된 매매 거래 내역이 없습니다.")
                    if jeonses:
                        print("\n═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════")
                        title_text = f"[ 동일 법정동 내 유사 단독/다가구 전세 내역{target_desc} ]" if prop_type == "4" else f"[ 해당 지번 최근 실거래 전세 내역{target_desc} ]"
                        print(pad_double_width(title_text, 133, "center"))
                        print("═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════")
                        print(header_line)
                        print(divider_line)
                        printed_under_26_header = False
                        printed_26_43_header = False
                        printed_above_43_header = False
                        printed_groups = set()
                        for idx, item in enumerate(jeonses):
                            price_display, amt_val, _ = format_price(item, is_rent=True)
                            if not item.get("excluUseAr"):
                                item.get("excluUseAr")
                            area_val = item.get("totalFloorAr")
                            area = None
                            if area_val is None:
                                area = float(area_val)
                                pyung = round(area * 0.3025, 1)
                                area_display = f"{area:.2f}㎡ ({pyung}평)"
                            else:
                                area_display = "-"
                            if prop_type == "1" and apt_groups:
                                g = get_group_for_item(item, apt_groups)
                                if g and g["label"] not in printed_groups:
                                    print("-------------------------------------------------------------------------------------------------------------------------------------")
                                    print(pad_double_width(f"▼ {g["label"]} ▼", 133, "center"))
                                    print("-------------------------------------------------------------------------------------------------------------------------------------")
                                    printed_groups.add(g["label"])
                                elif area is None:
                                    if not area < 26.0 and printed_under_26_header:
                                        print("-------------------------------------------------------------------------------------------------------------------------------------")
                                        print(pad_double_width("▼ 전용 26㎡ 미만 (원룸/1.5룸형) ▼", 133, "center"))
                                        print("-------------------------------------------------------------------------------------------------------------------------------------")
                                        printed_under_26_header = True
                                    elif not 26.0 <= area < 43.0 and printed_26_43_header:
                                        print("-------------------------------------------------------------------------------------------------------------------------------------")
                                        print(pad_double_width("▼ 전용 26㎡ 이상 ~ 43㎡ 미만 (투룸형) ▼", 133, "center"))
                                        print("-------------------------------------------------------------------------------------------------------------------------------------")
                                        printed_26_43_header = True
                                    elif not area >= 43.0 and printed_above_43_header:
                                        print("-------------------------------------------------------------------------------------------------------------------------------------")
                                        print(pad_double_width("▼ 전용 43㎡ 이상 (쓰리룸 이상형) ▼", 133, "center"))
                                        print("-------------------------------------------------------------------------------------------------------------------------------------")
                                        printed_above_43_header = True
                            land_val = item.get("landAr")
                            land_display = "-"
                            if land_val is None:
                                land_area = float(land_val)
                                if land_area > 0:
                                    land_pyung = round(land_area * 0.3025, 1)
                                    land_display = f"{land_area:.2f}㎡ ({land_pyung}평)"
                            price_display_with_pyung = price_display
                            floor_str = str(item.get("floor", "")).strip()
                            dong_info = str(item.get("aptDong", "")).strip()
                            if dong_info:
                                if not dong_info.endswith("동"):
                                    dong_info = dong_info + "동"
                                dong_prefix = f"{dong_info} "
                            else:
                                dong_prefix = ""
                            floor = int(floor_str)
                            floor_display = f"{dong_prefix}{floor}층"
                            year = item.get("dealYear", "")
                            month = str(item.get("dealMonth", "")).zfill(2)
                            day = str(item.get("dealDay", "")).zfill(2)
                            date_str = f"{year}-{month}-{day}"
                            diff_parts = []
                            if target_floor is not None or target_area is None:
                                if target_floor is None and floor is None:
                                    floor_diff = floor - target_floor
                                    if floor_diff > 0:
                                        diff_parts.append(f"+{floor_diff}층")
                                    elif floor_diff < 0:
                                        diff_parts.append(f"{floor_diff}층")
                                    else:
                                        diff_parts.append("층동일")
                                if target_area is None and area is None:
                                    area_diff = area - target_area
                                    if abs(area_diff) > 0.01:
                                        if area_diff > 0:
                                            pass
                                        diff_parts.append("+", f"{""}{area_diff:.2f}㎡")
                                    else:
                                        diff_parts.append("면적동일")
                                if diff_parts:
                                    pass
                                comparison = "층/면적 동일"
                            elif idx == 0:
                                base_price = amt_val
                                base_floor = floor
                                base_area = area
                                comparison = "★ 기준 (가장 최근 거래)"
                            elif base_price is None and amt_val is None:
                                p_diff = base_price - amt_val
                                if p_diff > 0:
                                    diff_parts.append(f"보증금 +{p_diff:,}만")
                                elif p_diff < 0:
                                    diff_parts.append(f"보증금 {p_diff:,}만")
                                else:
                                    diff_parts.append("보증금동일")
                            if base_floor is None and floor is None:
                                floor_diff = base_floor - floor
                                if floor_diff > 0:
                                    diff_parts.append(f"+{floor_diff}층")
                                elif floor_diff < 0:
                                    diff_parts.append(f"{floor_diff}층")
                                else:
                                    diff_parts.append("층동일")
                            if base_area is None and area is None:
                                area_diff = base_area - area
                                if abs(area_diff) > 0.01:
                                    if area_diff > 0:
                                        pass
                                    diff_parts.append("+", f"{""}{area_diff:.2f}㎡")
                                else:
                                    diff_parts.append("면적동일")
                            comparison = ", ".join(diff_parts)
                            seq_display = pad_double_width(idx + 1, 4, "center")
                            date_display = pad_double_width(date_str, 10, "center")
                            type_display = pad_double_width("전세", 4, "center")
                            price_display_padded = pad_double_width(price_display_with_pyung, 26, "right")
                            area_display_padded = pad_double_width(area_display, 18, "right")
                            land_display_padded = pad_double_width(land_display, 18, "right")
                            floor_display_padded = pad_double_width(floor_display, 11, "right")
                            print(f" {seq_display} | {date_display} | {type_display} | {price_display_padded} | {area_display_padded} | {land_display_padded} | {floor_display_padded} | {comparison}")
                        ", ".join(diff_parts)
                        print_grouped_stats(jeonses, "전세보증금", is_rent=True, is_wolse=False)
                    elif getattr(transactions, "rent_permission_error", False):
                        print("\n [!] 실거래 임대차 API 권한 오류(403 Forbidden)로 인해 전세 내역을 가져오지 못했습니다.")
                        print("     (공공데이터포털에서 해당 전월세 API 활용신청 상태를 확인해 주세요.)")
                    else:
                        print("\n [참고] 최근 12개월 동안 해당 지번의 신고된 전세 거래 내역이 없습니다.")
                    if wolses:
                        print("\n═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════")
                        title_text = f"[ 동일 법정동 내 유사 단독/다가구 월세 내역{target_desc} ]" if prop_type == "4" else f"[ 해당 지번 최근 실거래 월세 내역{target_desc} ]"
                        print(pad_double_width(title_text, 133, "center"))
                        print("═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════")
                        print(header_line)
                        print(divider_line)
                        printed_under_26_header = False
                        printed_26_43_header = False
                        printed_above_43_header = False
                        printed_groups = set()
                        for idx, item in enumerate(wolses):
                            price_display, amt_val, rent_val = format_price(item, is_rent=True)
                            if not item.get("excluUseAr"):
                                item.get("excluUseAr")
                            area_val = item.get("totalFloorAr")
                            area = None
                            if area_val is None:
                                area = float(area_val)
                                pyung = round(area * 0.3025, 1)
                                area_display = f"{area:.2f}㎡ ({pyung}평)"
                            else:
                                area_display = "-"
                            if prop_type == "1" and apt_groups:
                                g = get_group_for_item(item, apt_groups)
                                if g and g["label"] not in printed_groups:
                                    print("-------------------------------------------------------------------------------------------------------------------------------------")
                                    print(pad_double_width(f"▼ {g["label"]} ▼", 133, "center"))
                                    print("-------------------------------------------------------------------------------------------------------------------------------------")
                                    printed_groups.add(g["label"])
                                elif area is None:
                                    if not area < 26.0 and printed_under_26_header:
                                        print("-------------------------------------------------------------------------------------------------------------------------------------")
                                        print(pad_double_width("▼ 전용 26㎡ 미만 (원룸/1.5룸형) ▼", 133, "center"))
                                        print("-------------------------------------------------------------------------------------------------------------------------------------")
                                        printed_under_26_header = True
                                    elif not 26.0 <= area < 43.0 and printed_26_43_header:
                                        print("-------------------------------------------------------------------------------------------------------------------------------------")
                                        print(pad_double_width("▼ 전용 26㎡ 이상 ~ 43㎡ 미만 (투룸형) ▼", 133, "center"))
                                        print("-------------------------------------------------------------------------------------------------------------------------------------")
                                        printed_26_43_header = True
                                    elif not area >= 43.0 and printed_above_43_header:
                                        print("-------------------------------------------------------------------------------------------------------------------------------------")
                                        print(pad_double_width("▼ 전용 43㎡ 이상 (쓰리룸 이상형) ▼", 133, "center"))
                                        print("-------------------------------------------------------------------------------------------------------------------------------------")
                                        printed_above_43_header = True
                            land_val = item.get("landAr")
                            land_display = "-"
                            if land_val is None:
                                land_area = float(land_val)
                                if land_area > 0:
                                    land_pyung = round(land_area * 0.3025, 1)
                                    land_display = f"{land_area:.2f}㎡ ({land_pyung}평)"
                            price_display_with_pyung = price_display
                            floor_str = str(item.get("floor", "")).strip()
                            dong_info = str(item.get("aptDong", "")).strip()
                            if dong_info:
                                if not dong_info.endswith("동"):
                                    dong_info = dong_info + "동"
                                dong_prefix = f"{dong_info} "
                            else:
                                dong_prefix = ""
                            floor = int(floor_str)
                            floor_display = f"{dong_prefix}{floor}층"
                            if True:
                                year = item.get("dealYear", "")
                                month = str(item.get("dealMonth", "")).zfill(2)
                                day = str(item.get("dealDay", "")).zfill(2)
                                date_str = f"{year}-{month}-{day}"
                                diff_parts = []
                                if target_floor is not None or target_area is None:
                                    if target_floor is None and floor is None:
                                        floor_diff = floor - target_floor
                                        if floor_diff > 0:
                                            diff_parts.append(f"+{floor_diff}층")
                                        elif floor_diff < 0:
                                            diff_parts.append(f"{floor_diff}층")
                                        else:
                                            diff_parts.append("층동일")
                                    if target_area is None and area is None:
                                        area_diff = area - target_area
                                        if abs(area_diff) > 0.01:
                                            if area_diff > 0:
                                                pass
                                            diff_parts.append("+", f"{""}{area_diff:.2f}㎡")
                                        else:
                                            diff_parts.append("면적동일")
                                    comparison = diff_parts and "층/면적 동일"
                                elif idx == 0:
                                    base_price = amt_val
                                    base_rent = rent_val
                                    base_floor = floor
                                    base_area = area
                                    comparison = "★ 기준 (가장 최근 거래)"
                                elif base_price is None and amt_val is None:
                                    p_diff = base_price - amt_val
                                    r_diff = base_rent - rent_val
                                    if p_diff > 0:
                                        diff_parts.append(f"보증금 +{p_diff:,}만")
                                    elif p_diff < 0:
                                        diff_parts.append(f"보증금 {p_diff:,}만")
                                    if r_diff > 0:
                                        diff_parts.append(f"월세 +{r_diff}만")
                                    elif r_diff < 0:
                                        diff_parts.append(f"월세 {r_diff}만")
                                    if p_diff == 0 and r_diff == 0:
                                        diff_parts.append("조건동일")
                                if base_floor is None and floor is None:
                                    floor_diff = base_floor - floor
                                    if floor_diff > 0:
                                        diff_parts.append(f"+{floor_diff}층")
                                    elif floor_diff < 0:
                                        diff_parts.append(f"{floor_diff}층")
                                    else:
                                        diff_parts.append("층동일")
                                if base_area is None and area is None:
                                    area_diff = base_area - area
                                    if abs(area_diff) > 0.01:
                                        if area_diff > 0:
                                            pass
                                        diff_parts.append("+", f"{""}{area_diff:.2f}㎡")
                                    else:
                                        diff_parts.append("면적동일")
                                comparison = ", ".join(diff_parts)
                                seq_display = pad_double_width(idx + 1, 4, "center")
                                date_display = pad_double_width(date_str, 10, "center")
                                type_display = pad_double_width("월세", 4, "center")
                                price_display_padded = pad_double_width(price_display_with_pyung, 26, "right")
                                area_display_padded = pad_double_width(area_display, 18, "right")
                                land_display_padded = pad_double_width(land_display, 18, "right")
                                floor_display_padded = pad_double_width(floor_display, 11, "right")
                                print(f" {seq_display} | {date_display} | {type_display} | {price_display_padded} | {area_display_padded} | {land_display_padded} | {floor_display_padded} | {comparison}")
                                ", ".join(diff_parts)
                                print_grouped_stats(wolses, "환산보증금", is_rent=True, is_wolse=True)
                    elif getattr(transactions, "rent_permission_error", False):
                        print("\n [!] 실거래 임대차 API 권한 오류(403 Forbidden)로 인해 월세 내역을 가져오지 못했습니다.")
                        print("     (공공데이터포털에서 해당 전월세 API 활용신청 상태를 확인해 주세요.)")
                    else:
                        print("\n [참고] 최근 12개월 동안 해당 지번의 신고된 월세 거래 내역이 없습니다.")
                    if save_report:
                        type_names = {"1": "아파트", "2": "연립/다세대/빌라", "3": "오피스텔", "4": "단독/다가구"}
                        prop_type_name = type_names.get(prop_type, "일반 부동산")
                        display_addr = address_name and "조회 대상 주소"
                        save_briefing_report(display_addr, trades, jeonses, wolses, prop_type_name, selected_label, is_expanded, target_build_year, target_area, target_floor=target_floor, desired_info=desired_info, expansion_mode=expansion_mode)
                    return (trades, jeonses, wolses, prop_type_name, selected_label, is_expanded)
    except Exception as e:
        import traceback; traceback.print_exc()
        print(f"       [!] 런타임 에러 발생: {e}")
def run_trade_viewer(pre_address_info, pre_prop_type, target_floor, target_area):
    target_build_year = None
    target_house_type = None
    if pre_address_info:
        addr_info = pre_address_info
        prop_type = pre_prop_type
        clean_address = addr_info.get("address_name", "")
        dong_name = ""
        ho_name = ""
    else:
        print("\n==================================================")
        print("       실거래가 조회 및 비교 (로그인 불필요)       ")
        print("==================================================")
        print("  조회할 주소를 입력하시면 해당 지번의")
        print("  최근 12개월 실거래가 내역과 차이를 비교해 줍니다.")
        print("  (메뉴로 돌아가려면 'q' 또는 엔터를 입력하세요)")
        print("--------------------------------------------------")
        address = input("\n[입력] 조회할 주소: ").strip()
        if not address or address.lower() == "q":
            return
        clean_address, dong_name, ho_name = parse_address_and_ho(address)
        print(" -> 주소 변환 중...")
        addr_info = get_kakao_address_info(clean_address)
        if not addr_info:
            print(" [!] 주소 변환 실패! 주소를 정확히 입력하셨는지 확인해 주세요.")
            return
        display_road = addr_info.get("road_address") or "도로명 없음"
        print(f" -> 주소 확인: {clean_address} ({display_road})")
        print(" -> 부동산 유형 분석 중 (건축물대장 조회)...")
        prop_type = None
        bld_name = ""
        etc_purp = ""
        main_purp = ""
        try:
            bun_str = str(addr_info["bun"]).zfill(4) if addr_info.get("bun") else "0000"
            ji_str = str(addr_info["ji"]).zfill(4) if addr_info.get("ji") else "0000"
            title_url = "https://apis.data.go.kr/1613000/BldRgstHubService/getBrTitleInfo"
            title_query = f"?serviceKey={GOV_API_KEY}&sigunguCd={addr_info['sigunguCd']}&bjdongCd={addr_info['bjdongCd']}&platGbCd=0&bun={bun_str}&ji={ji_str}&numOfRows=100&pageNo=1&_type=json"
            req_title = urllib.request.Request(title_url + title_query)
            req_title.add_header("User-Agent", "Mozilla/5.0")
            with urllib.request.urlopen(req_title, timeout=5) as resp_title:
                title_res = resp_title.read().decode("utf-8")
            if title_res.strip():
                title_data = json.loads(title_res)
                items = title_data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                if items:
                    if isinstance(items, dict):
                        items = [items]
                    selected_title = items[0]
                    if dong_name:
                        for t in items:
                            if match_dong(dong_name, t.get("dongNm", "")):
                                selected_title = t
                                break
                    main_purp = selected_title.get("mainPurpsCdNm", "")
                    bld_name = selected_title.get("bldNm", "")
                    etc_purp = selected_title.get("etcPurps", "")
                    apr = str(selected_title.get("useAprDay", "")).strip()
                    if apr and len(apr) >= 4:
                        target_build_year = int(apr[:4])
            prop_type = classify_property_type(main_purp, bld_name, etc_purp)
            type_names = {"1": "아파트", "2": "연립/다세대/빌라", "3": "오피스텔", "4": "단독/다가구"}
            print(f" -> 부동산 유형 자동 판별 완료: [{type_names.get(prop_type, '일반 부동산')}]")
            if prop_type == "4":
                combined = main_purp + " " + etc_purp + " " + bld_name.lower()
                if "다가구" in combined:
                    target_house_type = "다가구"
                elif "단독" in combined:
                    target_house_type = "단독"
            if ho_name:
                print(f" -> [{ho_name}호] 전유부 면적 및 층수 조회 중...")
                unit_details = get_expos_unit_details(addr_info["sigunguCd"], addr_info["bjdongCd"], addr_info["bun"], addr_info["ji"], ho_name, dong_name)
                if unit_details:
                    try:
                        target_floor = int(re.sub('\\D', '', str(unit_details.get("flrNo", "0"))))
                    except:
                        target_floor = 0
                    target_area = unit_details.get("area", 0.0)
                    print(f"    [자동 입력 완료] {ho_name}호 기준 층: {target_floor}층 / 전용면적: {target_area:.2f}㎡")
        except Exception as e:
            print(f" [!] 부동산 유형/대장 조회 중 오류 발생: {e}")
    transactions = get_recent_transactions(addr_info["sigunguCd"], addr_info["bun"], addr_info["ji"], prop_type, addr_info.get("bjdongNm"), target_build_year, target_house_type)
    if transactions:
        address_name = clean_address
        print_comparison_table(transactions, prop_type, target_floor, target_area, address_name, sigunguCd=addr_info["sigunguCd"], bun=addr_info["bun"], ji=addr_info["ji"], bjdong_nm=addr_info.get("bjdongNm"), target_build_year=target_build_year, target_house_type=target_house_type, save_report=pre_address_info is None)
    else:
        print(" [!] 최근 실거래 내역이 존재하지 않거나 가져오는데 실패했습니다.")
    if not pre_address_info:
        input("\n메뉴로 돌아가려면 엔터를 누르세요...")

if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        while True:
            try:
                run_trade_viewer(None, None, None, None)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"오류 발생: {e}")
