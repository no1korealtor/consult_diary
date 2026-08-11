import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET

API_KEY = "88ec4e85897c086c4c9438db67c35f2bc10d730913b9ba6be67a9ea755e70770"

def get_building_data(sigungu, bjdong, bun, ji):
    url = "http://apis.data.go.kr/1613000/BldRgstHubService/getBrTitleInfo"
    query = f"?serviceKey={API_KEY}&sigunguCd={sigungu}&bjdongCd={bjdong}&platGbCd=0&bun={bun}&ji={ji}&numOfRows=10&pageNo=1&_type=json"
    
    building_info = {}
    
    try:
        req = urllib.request.Request(url + query)
        req.add_header("User-Agent", "Mozilla/5.0")
        req.add_header("Accept", "application/json, text/plain, */*")
        with urllib.request.urlopen(req) as response:
            res_text = response.read().decode('utf-8')
            if not res_text.strip():
                print("[API 오류] 정부 서버에서 빈 응답을 반환했습니다. (서버 점검 중이거나 일시적 오류일 수 있습니다.)")
                return None
                
            json_data = json.loads(res_text)
            
            header = json_data.get('response', {}).get('header', {})
            if header.get('resultCode') != '00':
                print(f"[API 오류] {header.get('resultMsg')}")
                return None
                
            items = json_data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
            if not items:
                print("[조회 실패] 데이터가 없습니다.")
                return None
                
            item = items[0] # 첫 번째 동 정보 기준
            
            # 1. 면적 정보
            building_info['totArea'] = str(item.get('totArea', 0))
            building_info['platArea'] = str(item.get('platArea', 0))
            building_info['archArea'] = str(item.get('archArea', 0))
            
            # 2. 층수 및 승강기 정보
            building_info['grndFlrCnt'] = str(item.get('grndFlrCnt', 0))
            building_info['ugrndFlrCnt'] = str(item.get('ugrndFlrCnt', 0))
            building_info['rideUseElvtCnt'] = str(item.get('rideUseElvtCnt', 0) or 0)
            building_info['emgenUseElvtCnt'] = str(item.get('emgenUseElvtCnt', 0) or 0)
            
            # 3. 세대수 / 가구수 (둘 중 큰 값 적용)
            hhld = int(item.get('hhldCnt', 0))
            fmly = int(item.get('fmlyCnt', 0))
            building_info['households'] = str(max(hhld, fmly))
            
            # 4. 주차 대수 계산 (옥내/옥외 기계/자주식 합산)
            parking = 0
            for p_type in ['indrAutoUtcnt', 'indrMechUtcnt', 'oudrAutoUtcnt', 'oudrMechUtcnt']:
                val = item.get(p_type, 0)
                if val:
                    parking += int(val)
            building_info['totalParking'] = str(parking)
            building_info['canPark'] = "Y" if parking > 0 else "N"
            
            # 주차대수가 0이면 총괄표제부를 한번 더 확인
            if parking == 0:
                basis_parking = get_basis_ouln_data(sigungu, bjdong, bun, ji)
                if basis_parking > 0:
                    building_info['totalParking'] = str(basis_parking)
                    building_info['canPark'] = "Y"

            
            # 5. 위반건축물, 용도, 승인일
            viol = str(item.get('violBldYn', 'N')).strip()
            building_info['violBldYn'] = viol if viol else "N"
            
            building_info['purpose'] = item.get('mainPurpsCdNm', "")
            building_info['bldNm'] = item.get('bldNm', "")
            building_info['etcPurps'] = item.get('etcPurps', "")
            building_info['regstrGbCd'] = str(item.get('regstrGbCd', '')).strip()
            building_info['regstrGbCdNm'] = str(item.get('regstrGbCdNm', '')).strip()
            
            apr = str(item.get('useAprDay', ""))
            if apr and len(apr) == 8:
                building_info['aprYear'] = apr[:4]
                building_info['aprMonth'] = apr[4:6]
                building_info['aprDay'] = apr[6:8]
            else:
                building_info['aprYear'] = building_info['aprMonth'] = building_info['aprDay'] = ""
                
            return building_info

    except json.JSONDecodeError:
        print("[API 오류] 응답을 JSON으로 변환할 수 없습니다. 정부 서버 오류일 가능성이 높습니다.")
        return None
    except Exception as e:
        print(f"오류: {e}")
        return None

if __name__ == "__main__":
    print("데이터 추출 테스트 (대림동 1056-1)...")
    res = get_building_data("11560", "13300", "1056", "0001")
    if res:
        for k, v in res.items():
            print(f"{k}: {v}")


def get_basis_ouln_data(sigungu, bjdong, bun, ji):
    import urllib.request, json
    url = "http://apis.data.go.kr/1613000/BldRgstHubService/getBrBasisOulnInfo"
    query = f"?serviceKey={API_KEY}&sigunguCd={sigungu}&bjdongCd={bjdong}&platGbCd=0&bun={bun}&ji={ji}&numOfRows=10&pageNo=1&_type=json"
    
    try:
        req = urllib.request.Request(url + query)
        response = urllib.request.urlopen(req)
        if response.getcode() == 200:
            res_body = response.read().decode('utf-8')
            if not res_body.strip(): return 0
            data = json.loads(res_body)
            items = data.get("response", {}).get("body", {}).get("items", {})
            if not items: return 0
            
            item_list = items.get("item", [])
            if isinstance(item_list, dict): item_list = [item_list]
            
            if item_list:
                item = item_list[0]
                parking = 0
                for p_type in ['indrAutoUtcnt', 'indrMechUtcnt', 'oudrAutoUtcnt', 'oudrMechUtcnt']:
                    val = item.get(p_type, 0)
                    if val: parking += int(val)
                return parking
    except:
        pass
    return 0

def get_expos_data(sigungu, bjdong, bun, ji, dong_name="", ho_name=""):
    url_info = "http://apis.data.go.kr/1613000/BldRgstHubService/getBrExposInfo"
    url_area = "http://apis.data.go.kr/1613000/BldRgstHubService/getBrExposPubuseAreaInfo"
    
    result = {'area': '', 'supply_area': '', 'flrNo': '', 'violBldYn': '확인불가(정부서버오류)'}
    
    for plat in [0, 1, 2]:
        query = f"?serviceKey={API_KEY}&sigunguCd={sigungu}&bjdongCd={bjdong}&platGbCd={plat}&bun={bun}&ji={ji}&numOfRows=100&pageNo=1&_type=json"
        
        try:
            # 1. 층수 및 위반건축물 여부 조회 (getBrExposInfo)
            req_info = urllib.request.Request(url_info + query)
            req_info.add_header('User-Agent', 'Mozilla/5.0')
            req_info.add_header('Accept', 'application/json, text/plain, */*')
            res_info = urllib.request.urlopen(req_info)
            if res_info.getcode() == 200:
                res_body = res_info.read().decode('utf-8')
                if res_body.strip():
                    data = json.loads(res_body)
                    items = data.get("response", {}).get("body", {}).get("items", {})
                    if items:
                        item_list = items.get("item", [])
                        if isinstance(item_list, dict): item_list = [item_list]
                        
                        for item in item_list:
                            item_dong = str(item.get('dongNm') or '')
                            item_ho = str(item.get('hoNm') or '')
                            dong_match = (dong_name in item_dong) if dong_name else True
                            ho_match = (ho_name in item_ho) if ho_name else True
                            
                            if dong_match and ho_match:
                                result['flrNo'] = item.get('flrNo')
                                result['violBldYn'] = item.get('violBldYn', 'N')
                                break
            
            # 2. 전용면적 조회 (getBrExposPubuseAreaInfo)
            req_area = urllib.request.Request(url_area + query)
            req_area.add_header('User-Agent', 'Mozilla/5.0')
            req_area.add_header('Accept', 'application/json, text/plain, */*')
            res_area = urllib.request.urlopen(req_area)
            if res_area.getcode() == 200:
                res_body = res_area.read().decode('utf-8')
                if res_body.strip():
                    data = json.loads(res_body)
                    items = data.get("response", {}).get("body", {}).get("items", {})
                    if items:
                        item_list = items.get("item", [])
                        if isinstance(item_list, dict): item_list = [item_list]
                        
                        area_exclusive = 0.0
                        area_supply = 0.0
                        
                        for item in item_list:
                            item_dong = str(item.get('dongNm') or '')
                            item_ho = str(item.get('hoNm') or '')
                            dong_match = (dong_name in item_dong) if dong_name else True
                            ho_match = (ho_name in item_ho) if ho_name else True
                            
                            if dong_match and ho_match:
                                val = item.get('area')
                                if val:
                                    f_val = float(val)
                                    area_supply += f_val
                                    # exposPubuseGbCd: 1(전유), 2(공용)
                                    if str(item.get('exposPubuseGbCd', '')) == '1':
                                        area_exclusive += f_val
                                        
                        if area_supply > 0:
                            result['area'] = str(round(area_exclusive, 2)) if area_exclusive > 0 else ''
                            result['supply_area'] = str(round(area_supply, 2))
                                
            if result['flrNo'] or result['area']:
                return result
                
        except Exception as e:
            continue
            
    print(f"전유부 API 호출 실패: 해당 주소에 전유부 데이터가 없습니다.")
    return None

def get_floor_data(sigungu, bjdong, bun, ji, floor_name):
    import urllib.request, json
    url_floor = "http://apis.data.go.kr/1613000/BldRgstHubService/getBrFlrOulnInfo"
    query = f"?serviceKey={API_KEY}&sigunguCd={sigungu}&bjdongCd={bjdong}&platGbCd=0&bun={bun}&ji={ji}&numOfRows=100&pageNo=1&_type=json"
    
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
                    if floor_name in api_flr_name or api_flr_name in floor_name:
                        area = item.get('flrArea', '')
                        result['area'] = str(area)
                        result['supply_area'] = str(area) # 전체 층이므로 공급/전용 동일
                        result['flrNo'] = item.get('flrNo', '')
                        return result
    except Exception as e:
        print("층별개요 조회 중 오류:", e)
        result['violBldYn'] = '확인불가(정부서버오류)'
        
    return result
