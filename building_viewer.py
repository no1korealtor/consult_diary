import urllib.request as urllib, urllib.parse as urllib, json, requests, re, sys, os
from datetime import datetime

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
        return "중개"
    if any(suffix in name for suffix in ("중개", "공인", "부동산", "방", "대표")):
        return name
    return f"{name} 중개"

KAKAO_API_KEY = "133155e52871811db4337080ae0a2d13"
GOV_API_KEY = "88ec4e85897c086c4c9438db67c35f2bc10d730913b9ba6be67a9ea755e70770"
def get_kakao_address_info(address_str):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": address_str}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        data = res.json()
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

def get_vworld_land_info(vworld_key, pnu):
    url = f"https://api.vworld.kr/ned/data/getLandCharacteristics?key={vworld_key}&domain=http://localhost&pnu={pnu}&format=json&numOfRows=10&pageNo=1"
    req = urllib.request.Request(url)
    req.add_header("Referer", "http://localhost")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            items = data.get("landCharacteristicss", {}).get("field", [])
            if not items:
                items = data.get("response", {}).get("landCharacteristicss", {}).get("field", [])
        if items:
            if isinstance(items, dict):
                items = [items]
            return items[0]
        return None
    except Exception as e:
        print(f"공시지가 조회 에러: {e}")
        return None

def get_vworld_land_use_info(vworld_key, pnu, sigungu_cd):
    url = f"https://api.vworld.kr/ned/data/getLandUseAttr?key={vworld_key}&domain=http://localhost&pnu={pnu}&format=json&numOfRows=100&pageNo=1"
    req = urllib.request.Request(url)
    req.add_header("Referer", "http://localhost")
    result = {
        "moatown": False,
        "moatown_name": "",
        "redev": False,
        "redev_name": "",
        "permit": False,
        "permit_name": "",
        "regulated": False,
        "regulated_name": ""
    }
    regulated_districts = {
        "11680": "강남구 (투기과열지구/조정대상지역)",
        "11650": "서초구 (투기과열지구/조정대상지역)",
        "11710": "송파구 (투기과열지구/조정대상지역)",
        "11170": "용산구 (투기과열지구/조정대상지역)"
    }
    if sigungu_cd in regulated_districts:
        result["regulated"] = True
        result["regulated_name"] = regulated_districts[sigungu_cd]
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
            permit_list = []
            for item in items:
                name = item.get("prposAreaDstrcCodeNm", "")
                if not name:
                    continue
                if any(kw in name for kw in ("소규모주택정비 관리지역", "소규모주택정비관리지역")) or ("소규모주택" in name and "관리지역" in name):
                    moatown_list.append(name)
                if any(kw in name for kw in ("정비구역", "재개발", "재건축", "도시환경정비")):
                    redev_list.append(name)
                if "토지거래계약에관한허가구역" in name or "토지거래허가" in name:
                    permit_list.append(name)
            if moatown_list:
                result["moatown"] = True
                result["moatown_name"] = ", ".join(list(set(moatown_list)))
            if redev_list:
                result["redev"] = True
                result["redev_name"] = ", ".join(list(set(redev_list)))
            if permit_list:
                result["permit"] = True
                result["permit_name"] = ", ".join(list(set(permit_list)))
        return result
    except Exception as e:
        print(f"토지이용계획 조회 에러: {e}")
        return result

def get_vworld_apartment_house_price(vworld_key, pnu, dong_name, ho_name):
    url = f"https://api.vworld.kr/ned/data/getApartHousingPriceAttr?key={vworld_key}&domain=http://localhost&pnu={pnu}&format=json&numOfRows=1000&pageNo=1"
    req = urllib.request.Request(url)
    req.add_header("Referer", "http://localhost")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            items = data.get("apartHousingPrices", {}).get("field", [])
            if not items:
                items = data.get("response", {}).get("apartHousingPrices", {}).get("field", [])
        if items:
            if isinstance(items, dict):
                items = [items]
            def match_part(target, item):
                if not target:
                    return True
                if not item:
                    return False
                t_str = str(target).strip().lower()
                i_str = str(item).strip().lower()
                if t_str == i_str:
                    return True
                t_clean = t_str.replace("호", "").replace("동", "")
                i_clean = i_str.replace("호", "").replace("동", "")
                if t_clean == i_clean:
                    return True
                t_num = re.sub("[^0-9]", "", t_clean)
                i_num = re.sub("[^0-9]", "", i_clean)
                if t_num and i_num:
                    return int(t_num) == int(i_num)
                return False

            matched_items = []
            for item in items:
                item_dong = item.get("dongNm", "") or ""
                item_ho = item.get("hoNm", "") or ""
                if ho_name:
                    if match_part(ho_name, item_ho):
                        if dong_name:
                            if match_part(dong_name, item_dong):
                                matched_items.append(item)
                        else:
                            matched_items.append(item)
                else:
                    matched_items.append(item)
            if matched_items:
                items_sorted = sorted(matched_items, key=lambda x: x.get("stdrYear", ""), reverse=True)
                for item in items_sorted:
                    price_val = item.get("pblntfPc")
                    year_val = item.get("stdrYear")
                    if price_val and year_val:
                        return {"year": year_val, "price": int(price_val)}
        return None
    except Exception as e:
        print(f"공동주택가격 조회 에러: {e}")
        return None

def format_assessed_price(val):
    if not val:
        return "정보없음"
    if val >= 100_000_000:
        eok = val // 100_000_000
        man = val % 100_000_000 // 10_000
        if man > 0:
            return f"{eok}억 {man:,}만원"
        return f"{eok}억원"
    man = val // 10_000
    return f"{man:,}만원"

def get_building_title_info(sigungu, bjdong, bun, ji):
    bun_str = str(bun).zfill(4) if bun else "0000"
    ji_str = str(ji).zfill(4) if ji else "0000"
    url = "https://apis.data.go.kr/1613000/BldRgstHubService/getBrTitleInfo"
    query = f"?serviceKey={GOV_API_KEY}&sigunguCd={sigungu}&bjdongCd={bjdong}&platGbCd=0&bun={bun_str}&ji={ji_str}&numOfRows=10&pageNo=1&_type=json"
    try:
        req = urllib.request.Request(url + query)
        req.add_header("User-Agent", "Mozilla/5.0")
        req.add_header("Accept", "application/json, text/plain, */*")
        with urllib.request.urlopen(req, timeout=5) as response:
            res_text = response.read().decode("utf-8")
        if not res_text.strip():
            return None
        json_data = json.loads(res_text)
        items = json_data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
        if not items:
            return None
        if isinstance(items, dict):
            return [items]
        return items
    except Exception as e:
        print(f"get_building_title_info 에러: {e}")
        return None

def get_expos_info_list(sigungu, bjdong, bun, ji):
    bun_str = str(bun).zfill(4) if bun else "0000"
    ji_str = str(ji).zfill(4) if ji else "0000"
    url = "https://apis.data.go.kr/1613000/BldRgstHubService/getBrExposInfo"
    query = f"?serviceKey={GOV_API_KEY}&sigunguCd={sigungu}&bjdongCd={bjdong}&platGbCd=0&bun={bun_str}&ji={ji_str}&numOfRows=100&pageNo=1&_type=json"
    try:
        req = urllib.request.Request(url + query)
        req.add_header("User-Agent", "Mozilla/5.0")
        req.add_header("Accept", "application/json, text/plain, */*")
        with urllib.request.urlopen(req, timeout=5) as response:
            res_text = response.read().decode("utf-8")
        if not res_text.strip():
            return None
        json_data = json.loads(res_text)
        items = json_data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
        if not items:
            return None
        if isinstance(items, dict):
            return [items]
        return items
    except Exception as e:
        print(f"get_expos_info_list 에러: {e}")
        return None

def get_building_floor_info(sigungu, bjdong, bun, ji):
    bun_str = str(bun).zfill(4) if bun else "0000"
    ji_str = str(ji).zfill(4) if ji else "0000"
    url = "https://apis.data.go.kr/1613000/BldRgstHubService/getBrFlrOulnInfo"
    query = f"?serviceKey={GOV_API_KEY}&sigunguCd={sigungu}&bjdongCd={bjdong}&platGbCd=0&bun={bun_str}&ji={ji_str}&numOfRows=100&pageNo=1&_type=json"
    try:
        req = urllib.request.Request(url + query)
        req.add_header("User-Agent", "Mozilla/5.0")
        req.add_header("Accept", "application/json, text/plain, */*")
        with urllib.request.urlopen(req, timeout=5) as response:
            res_text = response.read().decode("utf-8")
        if not res_text.strip():
            return None
        json_data = json.loads(res_text)
        items = json_data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
        if not items:
            return None
        if isinstance(items, dict):
            return [items]
        return items
    except Exception as e:
        print(f"get_building_floor_info 에러: {e}")
        return None

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
def mask_building_name(name):
    if not name:
        return ""
    name_str = str(name).strip()
    if len(name_str) <= 2:
        return "**"
    
    return "**" + name_str[slice(2, None, None)]
def mask_ho_name(ho):
    if not ho:
        return ""
    ho_str = str(ho).strip(); digits = re.findall("\\d+", ho_str)
    if digits:
        return ho_str.replace(digits[0], "***")
    
    return "***"
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
def save_building_report_pdf(address, bld_data, filename_pdf):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib import colors
        import os
        from datetime import datetime
        font_paths = ["C:\\Windows\\Fonts\\malgun.ttf", "C:\\Windows\\Fonts\\gulim.ttc", "C:\\Windows\\Fonts\\batang.ttc", "C:\\Windows\\Fonts\\맑은.ttf"]
        registered = False
        for path in font_paths:
            if not os.path.exists(path):
                continue
            pdfmetrics.registerFont(TTFont("KoreanFont", path))
            registered = True
            None
        colors
        if not registered:
            pdfmetrics.registerFont(TTFont("KoreanFont", "Helvetica"))
        doc = SimpleDocTemplate(filename_pdf, pagesize=A4, rightMargin=47, leftMargin=47, topMargin=40, bottomMargin=60)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("MainTitle", parent=styles["Normal"], fontName="KoreanFont", fontSize=18, leading=22, textColor=colors.HexColor("#1A365D"), alignment=1, spaceAfter=15, bold=True)
        h2_style = ParagraphStyle("SectionHeading", parent=styles["Normal"], fontName="KoreanFont", fontSize=11, leading=15, textColor=colors.HexColor("#2C5282"), spaceBefore=14, spaceAfter=6, bold=True)
        label_style = ParagraphStyle("MetaLabel", parent=styles["Normal"], fontName="KoreanFont", fontSize=9, leading=13, textColor=colors.HexColor("#4A5568"), bold=True)
        value_style = ParagraphStyle("MetaValue", parent=styles["Normal"], fontName="KoreanFont", fontSize=9, leading=13, textColor=colors.HexColor("#2D3748"))
        table_hdr_style = ParagraphStyle("TableHdr", parent=styles["Normal"], fontName="KoreanFont", fontSize=9, leading=12, textColor=colors.white, alignment=1, bold=True)
        table_cell_style = ParagraphStyle("TableCell", parent=styles["Normal"], fontName="KoreanFont", fontSize=9, leading=13, textColor=colors.HexColor("#2D3748"))
        table_cell_style_center = ParagraphStyle("TableCellCenter", parent=table_cell_style, alignment=1)
        table_cell_style_right = ParagraphStyle("TableCellRight", parent=table_cell_style, alignment=2)
        story = []
        accent_bar = Table([[""]], colWidths=[500], rowHeights=[4])
        accent_bar.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1A365D")), ("BOTTOMPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0)]))
        story.append(accent_bar)
        story.append(Spacer(1, 15))
        story.append(Paragraph("부동산 건축물대장 및 토지 정보", title_style))
        story.append(Spacer(1, 10))
        bld_nm_str = bld_data["bld_nm"] and "정보없음"
        if bld_data["dong_nm"]:
            bld_nm_str += f" {bld_data["dong_nm"]}동"
        if bld_data["ho_name"]:
            bld_nm_str += f" {mask_ho_name(bld_data["ho_name"])}호"
        meta_data = [[Paragraph("<b>조회 대상 주소</b>", label_style),

Paragraph(address, value_style)], [Paragraph("<b>건물 정보</b>", label_style),

Paragraph(bld_nm_str, value_style)],
            
            [Paragraph("<b>보고서 발행일</b>", label_style), Paragraph(datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S"), value_style)]]
        phone_no = bld_data.get("phone_number")
        if phone_no:
            meta_data.append([Paragraph("<b>의뢰인 연락처</b>", label_style), Paragraph(mask_phone_number(phone_no), value_style)])
        meta_table = Table(meta_data, colWidths=[100, 400])
        meta_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")), ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")), ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6), ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12)]))
        story.append(meta_table)
        story.append(Spacer(1, 10))
        if not bld_data.get("ride_elvt", 0):
            bld_data.get("ride_elvt", 0)
        ride_elvt = 0
        if not bld_data.get("emgen_elvt", 0):
            bld_data.get("emgen_elvt", 0)
        emgen_elvt = 0
        if not bld_data.get("elvt_cnt", 0):
            bld_data.get("elvt_cnt", 0)
        total_elvt = 0
        if not bld_data.get("grnd_cnt", 0):
            bld_data.get("grnd_cnt", 0)
        grnd_cnt_int = int(0)
        if total_elvt > 0:
            elvt_pdf_val = f"있음 (승용 {ride_elvt}대 / 비상용 {emgen_elvt}대)"
        elif grnd_cnt_int >= 4:
            elvt_pdf_val = "<font color='#E53E3E'><b>❌ 없음 (⚠️ 감가요인)</b></font>"
        else:
            elvt_pdf_val = "없음"
        story.append(Paragraph("■ [기본 건축물 정보]", h2_style))
        bld_type_label = "집합건물" if bld_data["is_jibbap"] else "일반건물"
        bld_info_data = [
            [Paragraph("<b>건물 유형</b>", label_style), Paragraph(bld_type_label, value_style),
             Paragraph("<b>대지면적</b>", label_style), Paragraph(f"{bld_data['plat_area']} ㎡", value_style)],
            [Paragraph("<b>주용도</b>", label_style), Paragraph(bld_data["main_purp"], value_style),
             Paragraph("<b>건물구조</b>", label_style), Paragraph(bld_data["structure"], value_style)],
            [Paragraph("<b>건축면적</b>", label_style), Paragraph(f"{bld_data['arch_area']} ㎡", value_style),
             Paragraph("<b>연면적</b>", label_style), Paragraph(f"{bld_data['tot_area']} ㎡ (용적률산정: {bld_data['vl_rat_tot_area']} ㎡)", value_style)],
            [Paragraph("<b>층수</b>", label_style), Paragraph(f"지상 {bld_data['grnd_cnt']}층 / 지하 {bld_data['ugrnd_cnt']}층", value_style),
             Paragraph("<b>세대/가구수</b>", label_style), Paragraph(f"공동주택 {bld_data['hhld']}세대 / 다가구 {bld_data['fmly']}가구", value_style)],
            [Paragraph("<b>총 주차대수</b>", label_style), Paragraph(f"{bld_data['parking']} 대", value_style),
             Paragraph("<b>사용승인일</b>", label_style), Paragraph(bld_data['apr_day'], value_style)],
            [Paragraph("<b>위반 여부</b>", label_style), Paragraph(bld_data['viol_str'], value_style),
             Paragraph("<b>엘리베이터</b>", label_style), Paragraph(elvt_pdf_val, value_style)]
        ]
        if bld_data.get("room_count_label"):
            bld_info_data.append([Paragraph("<b>방 개수</b>", label_style), Paragraph(bld_data["room_count_label"], value_style), Paragraph("", label_style), Paragraph("", value_style)])
        info_table = Table(bld_info_data, colWidths=[100, 150, 100, 150])
        info_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFFFF")), ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")), ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8)]))
        story.append(info_table)
        story.append(Spacer(1, 10))
        story.append(Paragraph("■ [토지 및 공시지가 정보]", h2_style))
        lndcgr = bld_data.get("lndcgr") or "정보없음"
        use_zone = bld_data.get("use_zone") or "정보없음"
        land_price_str = "정보없음"
        if bld_data.get("land_price_m2"):
            p_m2 = bld_data["land_price_m2"]
            p_py = round(p_m2 / 0.3025)
            land_price_str = f"㎡당 {p_m2:,}원 (평당 약 {p_py:,}원)"
            if bld_data.get("land_price_year"):
                land_price_str = f"{bld_data["land_price_year"]}년 기준 {land_price_str}"
        house_price_str = "정보없음"
        if bld_data["is_jibbap"] and bld_data.get("indiv_house_price"):
            price_val = bld_data["indiv_house_price"]
            formatted_p = format_assessed_price(price_val)
            price_126 = int(price_val * 1.26)
            formatted_126 = format_assessed_price(price_126)
            house_price_str = f"{formatted_p} (126%: {formatted_126})"
            if bld_data.get("indiv_house_price_year"):
                house_price_str = f"{bld_data["indiv_house_price_year"]}년 기준 {house_price_str}"
        if bld_data["is_jibbap"]:
            land_price_data = [
                [Paragraph("<b>개별공시지가</b>", label_style), Paragraph(land_price_str, value_style),
                 Paragraph("<b>공동주택가격</b>", label_style), Paragraph(house_price_str, value_style)]
            ]
        else:
            land_price_data = [
                [Paragraph("<b>개별공시지가</b>", label_style), Paragraph(land_price_str, value_style),
                 Paragraph("<b>개별주택가격</b>", label_style), Paragraph(house_price_str, value_style)]
            ]
        land_table = Table(land_price_data, colWidths=[100, 150, 100, 150])
        land_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1),

colors.HexColor("#FFFFFF")), ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),

("INNERGRID",

(0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8)]))
        story.append(land_table)
        story.append(Spacer(1, 10))
        story.append(Paragraph("■ [토지이용규제 및 개발구역 정보]", h2_style))
        dev_status = "⚪ 해당없음"
        if reg["moatown"]:
            dev_status = f"⚠️ 모아타운 ({reg['moatown_name']})"
        elif reg["redev"]:
            dev_status = f"⚠️ 정비구역 ({reg['redev_name']})"

        reg_status = "⚪ 비규제지역"
        if reg["permit"]:
            reg_status = f"⚠️ 토지거래허가 ({reg['permit_name']})"
        elif reg["regulated"]:
            reg_status = f"⚠️ 규제지역 ({reg['regulated_name']})"

        reg_table_data = [
            [Paragraph("<b>개발구역지정</b>", label_style), Paragraph(dev_status, value_style),
             Paragraph("<b>규제 및 허가</b>", label_style), Paragraph(reg_status, value_style)]
        ]
        reg_table = Table(reg_table_data, colWidths=[100, 150, 100, 150])
        reg_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFFFF")), ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")), ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("LEFTPADDING", (0, 0), (-1, -1), 8),

("RIGHTPADDING", (0, 0), (-1, -1), 8)]))
        story.append(reg_table)
        story.append(Spacer(1, 10))
        if bld_data.get("ho_details"):
            hd = bld_data["ho_details"]
            story.append(Paragraph(f"■ [{mask_ho_name(bld_data["ho_name"])}호 전유부분 상세 정보]", h2_style))
            pyung_area = "정보없음"
            if hd.get("area"):
                a = float(hd["area"])
                pyung_area = f"{a:.2f}㎡ (약 {round(a * 0.3025, 1)}평)"
            supply_area = "정보없음"
            if hd.get("supply_area"):
                sa = float(hd["supply_area"])
                supply_area = f"{sa:.2f}㎡ (약 {round(sa * 0.3025, 1)}평)"
            land_share_str = "정보없음"
            if hd.get("land_share"):
                l_area = float(hd["land_share"])
                land_share_str = f"{l_area:.2f} ㎡ ({round(l_area * 0.3025, 1)}평)"
            apt_price_str = "정보없음"
            if hd.get("apt_price"):
                price_val = hd["apt_price"]
                formatted_p = format_assessed_price(price_val)
                price_126 = int(price_val * 1.26)
                formatted_126 = format_assessed_price(price_126)
                apt_price_str = f"{formatted_p} (126%: {formatted_126})"
                if hd.get("apt_price_year"):
                    apt_price_str = f"{hd['apt_price_year']}년 기준 {apt_price_str}"
            viol_status = "⚠️ 위반건축물" if hd.get("viol_yn") == "Y" else "정상 (위반 없음)"
            ho_table_data = [
                [Paragraph("<b>해당 층수</b>", label_style), Paragraph(f"{hd['flr_no']}층", value_style), Paragraph("<b>위반 여부</b>", label_style), Paragraph(viol_status, value_style)],
                [Paragraph("<b>전용면적</b>", label_style), Paragraph(pyung_area, value_style), Paragraph("<b>공급면적</b>", label_style), Paragraph(supply_area, value_style)],
                [Paragraph("<b>대지지분</b>", label_style), Paragraph(land_share_str, value_style), Paragraph("<b>공동주택가격</b>", label_style), Paragraph(apt_price_str, value_style)]
            ]
            ho_table = Table(ho_table_data, colWidths=[100, 150, 100, 150])
            ho_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFFFF")), ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),

("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8)]))
            story.append(ho_table)
            story.append(Spacer(1, 10))
        if bld_data.get("floor_map"):
            dong_desc = bld_data["dong_nm"] and ""
            story.append(Paragraph(f"■ [호수별 구성]{dong_desc} (총 {bld_data["expos_list_count"]}개 호실)", h2_style))
            floor_rows = []
            fm = bld_data["floor_map"]
            sorted_floors_list = sorted(fm.keys(), key=(lambda x: int(re.sub("[^0-9-]", "", x)) if re.sub("[^0-9-]", "", x) else 0))
            for flr in sorted_floors_list:
                hos = sorted(list(fm[flr]))
                hos_str = ", ".join(hos)
                floor_rows.append([Paragraph(f"<b>{flr}층</b>", label_style),

Paragraph(hos_str, value_style)])
            f" [{bld_data["dong_nm"]}동]"
            floor_table = Table(floor_rows, colWidths=[80, 420])
            floor_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFFFF")), ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),

("INNERGRID", (0, 0), (-1, -1), 0.5,

colors.HexColor("#EDF2F7")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8)]))
            story.append(floor_table)
            story.append(Spacer(1, 10))
        elif bld_data.get("distinct_dongs"):
            dongs_str = ", ".join(bld_data["distinct_dongs"])
            story.append(Paragraph(f"■ [참고] 이 지번에는 여러 개의 동({dongs_str})이 존재합니다. 상세 호수 조회를 원하시면 동 정보(예: 101동)를 입력해 주세요.", value_style))
            story.append(Spacer(1, 10))
        if bld_data.get("floors"):
            story.append(Paragraph("■ [층별 면적 및 용도]", h2_style))
            headers = [Paragraph("<b>층 구분</b>", table_hdr_style), Paragraph("<b>주용도</b>", table_hdr_style), Paragraph("<b>면적</b>", table_hdr_style), Paragraph("<b>구조</b>", table_hdr_style)]
            floor_content = [headers]
            for f in bld_data["floors"]:
                area_float = float(f["area"])
                pyung = round(area_float * 0.3025, 1)
                area_str = f"{area_float:.2f} ㎡ ({pyung}평)"
                floor_content.append([Paragraph(f["flr_desc"], table_cell_style_center),

Paragraph(f["main_purp"], table_cell_style),

Paragraph(area_str, table_cell_style_right), Paragraph(f["structure"], table_cell_style)])
            fl_table = Table(floor_content, colWidths=[100, 150, 130, 120])
            fl_table_style = [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B6CB0")), ("ALIGN", (0, 0), (-1, -1), "LEFT"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 5), ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0"))]
            for idx in range(1, len(floor_content)):
                bg_color = colors.HexColor("#FFFFFF") if idx % 2 == 1 else colors.HexColor("#F7FAFC")
                fl_table_style.append(("BACKGROUND", (0, idx), (-1, idx), bg_color))
            f"{hd["supply_area"]:.2f} ㎡ ({round(hd["supply_area"] * 0.3025, 1)}평)"
            fl_table.setStyle(TableStyle(fl_table_style))
            story.append(fl_table)
            story.append(Spacer(1, 10))
        if not bld_data["is_jibbap"]:
            story.append(Paragraph("■ [대지지분 정보]", h2_style))
            share_rows = []
            while bld_data.get("land_shares_raw"):
                seen = set()
                for item in bld_data["land_shares_raw"]:
                    rate = item["rate"]
                    ho = item["ho"]
                    if ho and ho != "0000":
                        pass
                    ho_str = ""
                    if not rate:
                        continue
                    if not rate not in seen:
                        continue
                    seen.add(rate)
                    share_rows.append([Paragraph("대지지분 비율", label_style), Paragraph(f"{rate}{ho_str}", value_style)])
                None
                break
            share_rows.append([Paragraph("대지지분 형태", label_style),

Paragraph(f"단독 소유 (대지면적 {bld_data["plat_area"]} ㎡ 전체)", value_style)])
            share_table = Table(share_rows, colWidths=[120, 380])
            share_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFFFF")),

("BOX", (0, 0), (-1, -1), 1,

colors.HexColor("#E2E8F0")), ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8)]))
            story.append(share_table)
        def find_img_file(name):
            for d in (".", "scratch", ".."):
                for ext in (".png", ".jpg", ".jpeg"):
                    p_path = os.path.join(d, name + ext)
                    if not os.path.exists(p_path):
                        pass
                    None
                    None
                return p_path
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
        member = load_member_info()
        if member:
            m_name = format_member_name(member.get("name", ""))
            m_phone = member.get("phone", "")
            m_addr = member.get("office_address", "")
            m_reg = member.get("registration_number", "")
        else:
            m_name = "조항준 공인중개사"
            m_phone = "010-9128-0586<br/>☎ 02-375-4489"
            m_addr = "서울 마포구 모래내로 7길 52"
            m_reg = ""
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
            while 1:
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
                story.append(Paragraph('"본 자료는 참고용이며, 정확한 시세와 매물 상담은 직접 전화주시면 친절하게 안내해 드립니다.<br/><font color="#E53E3E"><b>지금 바로 전화주시면, 고객님께 딱 맞는 최적의 매물을 찾아드립니다!</b></font>"<br/><br/>데이터로 설명하고, 신뢰로 연결합니다.', italic_quote_style))
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
                                    canvas.setStrokeColor(colors.HexColor("#E2E8F0"))
                                    canvas.setLineWidth(0.5)
                                    canvas.line(47, 45, A4[0] - 47, 45)
                                    canvas.setFont("KoreanFont", 8)
                                    canvas.setFillColor(colors.HexColor("#718096"))
                                    canvas.drawString(47, 30, office_info)
                                    canvas.drawRightString(A4[0] - 47, 30, page_num_str)
                                    canvas.restoreState()
                    except:
                        pass
                doc.build(story, onFirstPage=draw_page_decorations, onLaterPages=draw_page_decorations)
                print(f"       -> PDF 파일 위치: {os.path.abspath(filename_pdf)}")
        grnd_cnt_int = 0
    except Exception as e:
        print(f" [!] PDF 파일 생성 중 오류 발생: {e}")
def save_building_report(address, bld_data):
    import os; os.makedirs("건축물대장", exist_ok=True)
    safe_addr = "".join([c for c in address if c not in (" ", "-", "_")]).strip();
    
    masked_address = mask_address_string(address)
    
    lines = []
    
    lines.append("================================================================================"); lines.append(f"               [ {masked_address} 건축물대장 및 토지 정보 ]"); lines.append("================================================================================"); lines.append("※ 본 보고서는 대장 조회를 통해 실시간 분석한 결과입니다.")
    
    lines.append(f"※ 조회 일시: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
    
    phone_no = bld_data.get("phone_number")
    if phone_no:
        lines.append(f"※ 의뢰인 연락처: {mask_phone_number(phone_no)}")
    lines.append("--------------------------------------------------------------------------------"); lines.append("■ [기본 건축물 정보]")
    bld_type_str = "집합건물 (공동주택/아파트/오피스텔 등)" if bld_data["is_jibbap"] else "일반건물 (단독/다가구/상가주택 등)"
    lines.append(f"  • 건물 유형: {bld_type_str}")
    
    masked_bld_nm = bld_data.get("bld_nm") or "정보없음"
    dong_nm_suffix = f" / {bld_data['dong_nm']}동" if bld_data.get("dong_nm") else ""
    lines.append(f"  • 건물명/동: {masked_bld_nm}{dong_nm_suffix}")
    lines.append(f"  • 대지면적 : {bld_data['plat_area']} ㎡")
    lines.append(f"  • 지목     : {bld_data.get('lndcgr') or '정보없음'}")
    lines.append(f"  • 용도지역 : {bld_data.get('use_zone') or '정보없음'}")
    
    if bld_data.get("land_price_m2"):
        p_m2 = bld_data["land_price_m2"]
        p_py = round(p_m2 / 0.3025)
        land_price_str = f"㎡당 {p_m2:,}원 (평당 약 {p_py:,}원)"
        if bld_data.get("land_price_year"):
            land_price_str = f"({bld_data["land_price_year"]}년) {land_price_str}"
    
    lines.append(f"  • 공시지가 : {land_price_str}"); lines.append(f"  • 건축면적 : {bld_data["arch_area"]} ㎡")
    
    lines.append(f"  • 연면적   : {bld_data["tot_area"]} ㎡ (용적률산정연면적: {bld_data["vl_rat_tot_area"]} ㎡)"); lines.append(f"  • 건물구조 : {bld_data["structure"]}"); lines.append(f"  • 주용도   : {bld_data["main_purp"]}")
    
    lines.append(f"  • 층수     : 지상 {bld_data["grnd_cnt"]}층 / 지하 {bld_data["ugrnd_cnt"]}층"); lines.append(f"  • 세대/가구: 공동주택 {bld_data["hhld"]}세대 / 다가구 {bld_data["fmly"]}가구"); lines.append(f"  • 주차대수 : {bld_data["parking"]} 대")
    
    lines.append(f"  • 사용승인 : {bld_data["apr_day"]}"); lines.append(f"  • 위반여부 : {bld_data["viol_str"]}")
    if not bld_data.get("ride_elvt", 0):
        bld_data.get("ride_elvt", 0)
    ride_elvt = 0
    
    if not bld_data.get("emgen_elvt", 0):
        bld_data.get("emgen_elvt", 0)
    emgen_elvt = 0
    if not bld_data.get("elvt_cnt", 0):
        bld_data.get("elvt_cnt", 0)
    total_elvt = 0
    try:
        if not bld_data.get("grnd_cnt", 0):
            bld_data.get("grnd_cnt", 0)
        grnd_cnt_int = int(0)
        if total_elvt > 0:
            elvt_txt = f"있음 (승용 {ride_elvt}대 / 비상용 {emgen_elvt}대)"
        elif grnd_cnt_int >= 4:
            elvt_txt = "❌ 없음 (⚠️ 4층 이상 엘리베이터 없음 - 감가요인)"
        else:
            elvt_txt = "없음"
        lines.append(f"  • 엘리베이터: {elvt_txt}")
        if bld_data.get("room_count_label"):
            lines.append(f"  • 방 개수  : {bld_data["room_count_label"]}")
        if bld_data["is_jibbap"] and bld_data.get("indiv_house_price"):
            price_val = bld_data["indiv_house_price"]
            formatted_p = format_assessed_price(price_val)
            price_126 = int(price_val * 1.26)
            formatted_126 = format_assessed_price(price_126)
            year_str = bld_data.get("indiv_house_price_year") and ""
            lines.append(f"  • 주택공시가격: {year_str}{formatted_p} (126%: {formatted_126})")
        lines.append("--------------------------------------------------------------------------------")
        reg = bld_data["reg_info"]
        lines.append("■ [토지 규제 및 구역 지정 정보]")
        moa_val = "⚪ 미해당"
        if reg and reg.get("moatown"):
            moa_val = reg.get("moatown_name") and f" ({reg["moatown_name"]})" + ""
        lines.append(f"  • 모아타운 여부: {moa_val}")
        redev_val = "⚪ 미해당"
        if reg and reg.get("redev"):
            redev_val = reg.get("redev_name") and f" ({reg["redev_name"]})" + ""
        lines.append(f"  • 정비구역 여부: {redev_val}")
        permit_val = "⚪ 미지정"
        if reg and reg.get("permit"):
            permit_val = reg.get("permit_name") and f" ({reg["permit_name"]})" + ""
        lines.append(f"  • 토지거래허가 : {permit_val}")
        reg_val = "⚪ 비규제지역"
        if reg and reg.get("regulated"):
            reg_val = reg.get("regulated_name") and f" ({reg["regulated_name"]})" + ""
        lines.append(f"  • 조정대상지역 : {reg_val}")
        lines.append("--------------------------------------------------------------------------------")
        if bld_data.get("ho_details"):
            hd = bld_data["ho_details"]
            lines.append(f"■ [{mask_ho_name(bld_data["ho_name"])}호 전유부분 상세 정보]")
            lines.append(f"  • 해당 층수: {hd["flr_no"]}층")
            if hd.get("area"):
                pyung = round(hd["area"] * 0.3025, 1)
                lines.append(f"  • 전용면적: {hd["area"]:.2f} ㎡ ({pyung}평)")
            if hd.get("supply_area"):
                spyung = round(hd["supply_area"] * 0.3025, 1)
                lines.append(f"  • 공급면적: {hd["supply_area"]:.2f} ㎡ ({spyung}평)")
            land_share_str = "정보없음"
            if hd.get("land_share"):
                l_area = float(hd["land_share"])
                l_pyung = round(l_area * 0.3025, 1)
                land_share_str = f"{l_area:.2f} ㎡ ({l_pyung}평)"
            lines.append(f"  • 대지지분: {land_share_str}")
            viol_status = hd.get("viol_yn") == "Y" and "정상 (위반 없음)"
            lines.append(f"  • 위반 여부: {viol_status}")
            if hd.get("apt_price"):
                price_val = hd["apt_price"]
                formatted_p = format_assessed_price(price_val)
                price_126 = int(price_val * 1.26)
                formatted_126 = format_assessed_price(price_126)
                year_str = hd.get("apt_price_year") and ""
                lines.append(f"  • 공동주택가격: {year_str}{formatted_p} (126%: {formatted_126})")
            lines.append("--------------------------------------------------------------------------------")
        if bld_data.get("floor_map"):
            fm = bld_data["floor_map"]
            dong_desc = bld_data["dong_nm"] and ""
            lines.append(f"■ [호수별 구성]{dong_desc} (총 {bld_data["expos_list_count"]}개 호실)")
            sorted_floors_list = sorted(fm.keys(), key=(lambda x: int(re.sub("[^0-9-]", "", x)) if re.sub("[^0-9-]", "", x) else 0))
            for flr in sorted_floors_list:
                hos = sorted(list(fm[flr]))
                hos_str = ", ".join(hos)
                lines.append(f"  • {flr}층: {hos_str}")
            f" [{bld_data["dong_nm"]}동]"
            lines.append("--------------------------------------------------------------------------------")
        elif bld_data.get("distinct_dongs"):
            dongs_str = ", ".join(bld_data["distinct_dongs"])
            lines.append(f"■ [참고] 이 지번에는 여러 개의 동({dongs_str})이 존재합니다.")
            lines.append("         정확한 호수 구성을 확인하려면 동 정보(예: 101동)를 입력해 주세요.")
            lines.append("--------------------------------------------------------------------------------")
        if bld_data.get("floors"):
            lines.append("■ [층별 면적 및 용도]")
            for f in bld_data["floors"]:
                area_float = float(f["area"])
                pyung = round(area_float * 0.3025, 1)
                area_str = f"{area_float:.2f} ㎡ ({pyung}평)"
                lines.append(f"  • {f["flr_desc"]}: {f["main_purp"]} | {area_str} | {f["structure"]}")
            f"({hd["apt_price_year"]}년) "
            lines.append("--------------------------------------------------------------------------------")
        if not bld_data["is_jibbap"]:
            lines.append("■ [대지지분 정보]")
            while bld_data.get("land_shares_raw"):
                seen = set()
                for item in bld_data["land_shares_raw"]:
                    rate = item["rate"]
                    ho = item["ho"]
                    if ho and ho != "0000":
                        pass
                    ho_str = ""
                    if not rate:
                        continue
                    if not rate not in seen:
                        continue
                    seen.add(rate)
                    lines.append(f"  • 대지지분 비율: {rate}{ho_str}")
                None
                break
            lines.append(f"  • 대지 지분: 단독 소유 (대지면적: {bld_data["plat_area"]} ㎡ 전체)")
            lines.append("--------------------------------------------------------------------------------")
        member = load_member_info()
        if member:
            m_name = format_member_name(member.get("name", ""))
            m_phone = member.get("phone", "")
            m_addr = member.get("office_address", "")
            m_reg = member.get("registration_number", "")
            phone_line = f"📞 {m_phone}"
            addr_lines = [f"📍 {m_addr}"]
        lines.append("──────────────────────────────")
        lines.append("")
        lines.append("        감사합니다.")
        lines.append("")
        lines.append("이번 분석이 도움이 되셨기를 바랍니다.")
        lines.append("")
        lines.append("──────────────────────────────")
        lines.append("")
        lines.append(m_name)
        lines.append("")
        lines.append("데이터 기반 부동산 분석")
        lines.append("매매 · 임대차 · 투자 상담")
        lines.append("")
        lines.append(phone_line)
        lines.append("")
        for al in addr_lines:
            lines.append(al)
        "⚠️ 규제지역" if m_reg else "⚠️ 위반건축물 지정!!"
        lines.append("")
        lines.append("──────────────────────────────")
        lines.append("")
        lines.append('"데이터로 설명하고,')
        lines.append('신뢰로 연결합니다."')
        lines.append("")
        lines.append("SHINDAERIM PROPERTY INTELLIGENCE")
        txt_content = "\n".join(lines)
        with open(filename_txt, "w", encoding="utf-8") as f:
            f.write(txt_content)
        print("\n [알림] 건축물대장 분석 보고서가 성공적으로 저장되었습니다!")
        print(f"       -> 텍스트 파일 위치: {os.path.abspath(filename_txt)}")
        save_building_report_pdf(masked_address, bld_data, filename_pdf)
        import shutil
        unified_dir = "종합분석보고서"
        os.makedirs(unified_dir, exist_ok=True)
        unified_txt = os.path.join(unified_dir, f"건축물대장_{safe_addr.replace(" ", "_")}.txt")
        unified_pdf = os.path.join(unified_dir, f"건축물대장_{safe_addr.replace(" ", "_")}.pdf")
        shutil.copy2(filename_txt, unified_txt)
        if os.path.exists(filename_pdf):
            shutil.copy2(filename_pdf, unified_pdf)
        print("       -> 종합분석보고서 통합 폴더에도 복사본이 저장되었습니다.")
        return
        open(filename_txt, "w", encoding="utf-8")
        c = "⚠️ 지정됨"
    except:
        grnd_cnt_int = 0
    sorted_floors_list = sorted(fm.keys())
    
    area_str = f"{f["area"]} ㎡"
    if not __exception__(__exception__, "🟢 해당", __exception__):
        pass
    open(filename_txt, "w", encoding="utf-8").__exit__
def run_building_viewer():
    try:
        print("\n============================================================")
        print("      건물 정보 조회 및 물건 분석 (CMA 보고서)      ")
        print("============================================================")
        print("  ※ [안내] 일부 공공데이터포털 시스템 점검 시 정보가 누락될 수 있으며,")
        print("            그 외의 경우 정상 조회됩니다.")
        print("  ------------------------------------------------------------")
        print("  조회할 주소를 입력하시면 건축물대장(표제부/전유부), 공시지가,")
        print("  그리고 해당 지번의 최근 실거래(매매/임대차) 내역을 일괄 조회하여 보여줍니다.")
        print("  (메뉴로 돌아가려면 'q' 또는 엔터를 입력하세요)")
        print("------------------------------------------------------------")
        address = input("\n[입력] 조회할 건물 주소 (예: 성산동 138-4 402호): ").strip()
        if not address or address.lower() == "q":
            return
        from trade_viewer import parse_address_and_ho, get_expos_unit_details, classify_property_type, get_recent_transactions, print_comparison_table, match_dong, print_empty_transactions_explanation
        clean_address, dong_name, ho_name = parse_address_and_ho(address)
        bld_nm = ""
        dong_nm = ""
        is_jibbap = False
        plat_area_val = "0"
        land_info = None
        land_price_info = None
        hhld = 0
        fmly = 0
        parking = 0
        apr_str = "정보없음"
        viol = "N"
        viol_str = "정상 (위반 없음)"
        print(" -> 주소 변환 및 검색 중...")
        addr_info = get_kakao_address_info(clean_address)
        if not addr_info:
            print(" [!] 주소 변환 실패! 주소를 정확히 입력하셨는지 확인해 주세요.")
            return
        display_road = addr_info.get("road_address") or "도로명 없음"
        print(f" -> 주소 확인: {clean_address} ({display_road})")
        print(" -> 건축물 표제부 조회 중...")
        titles = get_building_title_info(addr_info["sigunguCd"], addr_info["bjdongCd"], addr_info["bun"], addr_info["ji"])
        if not titles:
            print(" [!] 등록된 표제부(건물 정보) 데이터가 없습니다. (단독 필지 또는 미등록 대지)")
            return
        selected_title = titles[0]
        if dong_name:
            for t in titles:
                if match_dong(dong_name, t.get("dongNm", "")):
                    selected_title = t
                    break
        main_purp = selected_title.get("mainPurpsCdNm", "")
        bld_name = selected_title.get("bldNm", "")
        etc_purp = selected_title.get("etcPurps", "")
        prop_type = classify_property_type(main_purp, bld_name, etc_purp)
        reg_gb_cd = str(selected_title.get("regstrGbCd", "")).strip()
        reg_gb_nm = str(selected_title.get("regstrGbCdNm", "")).strip()
        if reg_gb_cd:
            is_jibbap = (reg_gb_cd == "2" or reg_gb_nm == "집합")
        else:
            is_jibbap = prop_type in ("1", "2", "3")
        bun_val = str(addr_info["bun"]).zfill(4) if addr_info.get("bun") else "0000"
        ji_val = str(addr_info["ji"]).zfill(4) if addr_info.get("ji") else "0000"
        pnu = f"{addr_info['sigunguCd']}{addr_info['bjdongCd']}1{bun_val}{ji_val}"
        vworld_key = "80194C85-0EE3-3220-A3C1-3268AD8756B9"
        land_share = ""
        if ho_name:
            try:
                from serve_auto_upload import get_vworld_land_share
                land_share = get_vworld_land_share(vworld_key, pnu, "", ho_name)
            except Exception as e:
                print(f"대지지분 조회 에러: {e}")
        print("\n═══════════════════════════════════════════════════════")
        bld_nm = selected_title.get("bldNm", "").strip()
        dong_nm = selected_title.get("dongNm", "").strip()
        bld_tag = f" ({bld_nm})" if bld_nm else ""
        dong_tag = f" / {dong_nm}동" if dong_nm else ""
        print(f" [건물대장] {clean_address}{bld_tag}{dong_tag}")
        print("═══════════════════════════════════════════════════════")
        land_info = get_vworld_land_info(vworld_key, pnu)
        plat_area_val = str(selected_title.get("platArea", "0")).strip()
        try:
            plat_area_float = float(plat_area_val)
        except:
            plat_area_float = 0.0
        if plat_area_float == 0.0 and land_info and land_info.get("area") and float(land_info["area"]) > 0:
            plat_area_val = land_info["area"]
        print(f"  • 대지면적  : {plat_area_val} ㎡")
        if land_info:
            if land_info.get("lndcgr"):
                print(f"  • 지목      : {land_info['lndcgr']}")
            if land_info.get("use_zone"):
                print(f"  • 용도지역  : {land_info['use_zone']}")
        land_price_info = get_vworld_land_price(vworld_key, pnu)
        if land_price_info:
            p_m2 = land_price_info["price"]
            p_py = round(p_m2 / 0.3025)
            print(f"  • 공시지가  : {land_price_info['year']}년 기준 ㎡당 {p_m2:,}원 (평당 약 {p_py:,}원)")
        print(f"  • 건축면적  : {selected_title.get('archArea', '0')} ㎡")
        print(f"  • 연면적    : {selected_title.get('totArea', '0')} ㎡ (용적률산정연면적: {selected_title.get('vlRatEstTotArea', '0')} ㎡)")
        print(f"  • 건물구조  : {selected_title.get('strctCdNm', '정보없음')}")
        print(f"  • 주용도    : {selected_title.get('mainPurpsCdNm', '정보없음')}")
        print(f"  • 층수      : 지상 {selected_title.get('grndFlrCnt', '0')}층 / 지하 {selected_title.get('ugrndFlrCnt', '0')}층")
        try:
            hhld = int(selected_title.get("hhldCnt", 0) or 0)
        except:
            hhld = 0
        try:
            fmly = int(selected_title.get("fmlyCnt", 0) or 0)
        except:
            fmly = 0
        max_units = max(hhld, fmly)
        print(f"  • 세대/가구 : 공동주택 {hhld}세대 / 다가구 {fmly}가구 (총 {max_units}호실)")
        parking = 0
        for p_type in ("indrAutoUtcnt", "indrMechUtcnt", "oudrAutoUtcnt", "oudrMechUtcnt"):
            try:
                val = selected_title.get(p_type, 0)
                parking += int(val or 0)
            except:
                pass
        print(f"  • 총 주차대수: {parking} 대")
        apr = str(selected_title.get("useAprDay", "")).strip()
        apr_str = "정보없음"
        if apr and len(apr) == 8:
            apr_str = f"{apr[:4]}년 {apr[4:6]}월 {apr[6:8]}일"
        elif apr:
            apr_str = apr
        print(f"  • 사용승인일: {apr_str}")
        target_build_year = None
        if apr and len(apr) >= 4:
            try:
                target_build_year = int(apr[:4])
            except:
                pass
        target_house_type = None
        if prop_type == "4":
            combined = main_purp + " " + etc_purp + " " + bld_name.lower()
            if "다가구" in combined:
                target_house_type = "다가구"
            elif "단독" in combined:
                target_house_type = "단독"
        viol = str(selected_title.get("violBldYn", "N")).strip()
        viol_str = "⚠️ 위반건축물 지정!!" if viol == "Y" else "정상 (위반 없음)"
        print(f"  • 위반 여부 : {viol_str}")
        try:
            ride_elvt = int(selected_title.get("rideUseElvtCnt", 0) or 0)
        except:
            ride_elvt = 0
        try:
            emgen_elvt = int(selected_title.get("emgenUseElvtCnt", 0) or 0)
            total_elvt = ride_elvt + emgen_elvt
        except:
            pass
        try:
            grnd_cnt_int = int(selected_title.get("grndFlrCnt", 0) or 0)
        except:
            grnd_cnt_int = 0
        if total_elvt > 0:
            elvt_str = f"있음 (승용 {ride_elvt}대 / 비상용 {emgen_elvt}대)"
        elif grnd_cnt_int >= 4:
            elvt_str = "❌ 없음 (⚠️ 4층 이상 엘리베이터 없음 - 감가요인)"
        else:
            elvt_str = "없음"
        print(f"  • 엘리베이터: {elvt_str}")
        if not is_jibbap:
            indiv_house_price = get_vworld_individual_house_price(vworld_key, pnu)
            if indiv_house_price:
                price_val = indiv_house_price["price"]
                formatted_p = format_assessed_price(price_val)
                price_126 = int(price_val * 1.26)
                formatted_126 = format_assessed_price(price_126)
                print(f"  • 주택공시가격: {indiv_house_price['year']}년 기준 {formatted_p} (126%: {formatted_126})")
        print(" -> 토지이용규제 및 개발구역(모아타운/정비구역/허가구역) 정보 조회 중...")
        reg_info = get_vworld_land_use_info(vworld_key, pnu, addr_info["sigunguCd"])
        if reg_info:
            print("───────────────────────────────────────────────────────")
            print("  [ 토지규제 및 구역지정 정보 ]")
            dev_status = "⚪ 해당없음"
            if reg_info["moatown"]:
                dev_status = f"⚠️ 모아타운지정 ({reg_info['moatown_name']})"
            elif reg_info["redev"]:
                dev_status = f" 정비구역지정 ({reg_info['redev_name']})"
            print(f"  • 개발구역지정 : {dev_status}")
            reg_status = "⚪ 비규제지역"
            if reg_info["permit"]:
                reg_status = f"⚠️ 토지거래허가구역 ({reg_info['permit_name']})"
            elif reg_info["regulated"]:
                reg_status = f"⚠️ 규제지역 ({reg_info['regulated_name']})"
            print(f"  • 규제 및 허가 : {reg_status}")
        print("═══════════════════════════════════════════════════════")
        target_floor = None
        target_area = None
        unit_info = None
        floor_map = {}
        expos_list_count = 0
        if is_jibbap:
            if ho_name:
                print(f"\n -> 요청하신 [{ho_name}호] 전유부 상세 정보 조회 중...")
                unit_info = get_expos_unit_details(addr_info["sigunguCd"], addr_info["bjdongCd"], addr_info["bun"], addr_info["ji"], ho_name, dong_name)
            print("\n -> 전유부(가구/호수 리스트) 조회 중...")
            expos_list = get_expos_info_list(addr_info["sigunguCd"], addr_info["bjdongCd"], addr_info["bun"], addr_info["ji"])
            if expos_list:
                distinct_dongs = set((item.get("dongNm", "").strip() for item in expos_list))
                if dong_name and len(distinct_dongs) > 1:
                    print("--------------------------------------------------")
                    dongs_str = ", ".join(sorted(list(distinct_dongs)))
                    print(f"  [참고] 이 지번에는 여러 개의 동({dongs_str})이 존재합니다.")
                    print("         정확한 호수 구성을 확인하려면 동 정보(예: 101동)를 입력해 주세요.")
                    print("--------------------------------------------------")
                else:
                    filtered_count = 0
                    for item in expos_list:
                        item_dong = item.get("dongNm", "") or ""
                        if dong_name and not match_dong(dong_name, item_dong):
                            continue
                        flr = str(item.get("flrNo", "")).strip()
                        ho = str(item.get("hoNm", "")).strip()
                        if not flr or not ho:
                            continue
                        if flr not in floor_map:
                            floor_map[flr] = set()
                        floor_map[flr].add(ho)
                        filtered_count += 1
                    expos_list_count = filtered_count
                    print("--------------------------------------------------")
                    dong_desc = f" [{dong_name}동]" if dong_name else ""
                    print(f"  [호수별 구성]{dong_desc} 총 {filtered_count}개 전유부분 등록됨")
                    sorted_floors = sorted(floor_map.keys(), key=(lambda x: int(re.sub("[^0-9-]", "", x)) if re.sub("[^0-9-]", "", x) else 0))
                    for flr in sorted_floors:
                        hos = sorted(list(floor_map[flr]))
                        hos_str = ", ".join(hos)
                        print(f"   • {flr}층: {hos_str}")
                    print("--------------------------------------------------")
            else:
                print("  [참고] 등록된 개별 호수 구성(전유부분)이 없습니다.")
        else:
            print("\n -> 일반건축물 층별 면적(개요) 정보 조회 중...")
            floors = get_building_floor_info(addr_info["sigunguCd"], addr_info["bjdongCd"], addr_info["bun"], addr_info["ji"])
            if floors:
                print("--------------------------------------------------")
                print("   [ 건축물대장 층별 면적 및 용도 ]")
                print("--------------------------------------------------")
                def get_floor_sort_key(f):
                    flr_no_str = str(f.get("flrNo", "0")).strip()
                    flr_gb = f.get("flrGbCdNm", "") or ""
                    try:
                        val = int(re.sub("[^0-9-]", "", flr_no_str))
                        if "지하" in flr_gb:
                            return -100 + val
                        elif "옥탑" in flr_gb:
                            return 100 + val
                        return val
                    except:
                        return 0
                sorted_floors = sorted(floors, key=get_floor_sort_key)
                for f in sorted_floors:
                    flr_gb = f.get("flrGbCdNm", "") or ""
                    flr_no = f.get("flrNo", "") or ""
                    flr_desc = f"{flr_gb} {flr_no}".strip()
                    structure = f.get("strctCdNm", "") or "정보없음"
                    main_purps = f.get("mainPurpsCdNm", "") or "정보없음"
                    area_val = f.get("area", "0")
                    try:
                        area_float = float(area_val)
                    except:
                        area_float = 0.0
                    pyung = round(area_float * 0.3025, 1)
                    area_str = f"{area_float:.2f} ㎡ ({pyung}평)"
                    print(f"  • {flr_desc}: {main_purps} | {area_str} | {structure}")
                print("--------------------------------------------------")
            else:
                print("  [참고] 등록된 층별 개요 정보가 없습니다.")
            print("\n -> 일반건축물 토지대장 및 지분 정보 조회 중...")
            url_lda = f"https://api.vworld.kr/ned/data/ldaregList?key={vworld_key}&domain=http://localhost&pnu={pnu}&format=json&numOfRows=100&pageNo=1"
            req_lda = urllib.request.Request(url_lda)
            req_lda.add_header("Referer", "http://localhost")
            try:
                with urllib.request.urlopen(req_lda, timeout=5) as resp_lda:
                    lda_data = json.loads(resp_lda.read().decode("utf-8"))
                    items = lda_data.get("ldaregVOList", {}).get("ldaregVOList", [])
            except Exception as e:
                print(f"토지대장 조회 에러: {e}")
        print("\n==================================================")
        cma_choice = input("[입력] 물건 분석(CMA) 및 시세 브리핑 보고서 생성을 진행하시겠습니까? (y/n) [기본값: n]: ").strip().lower()
        if cma_choice != "y":
            print(" -> 물건 분석을 진행하지 않고 종료합니다. (보고서가 저장되지 않습니다)")
            print("═══════════════════════════════════════════════════════")
            return
        if not is_jibbap and ho_name:
            print("\n [안내] 해당 건물은 일반건축물이지만 호실이 지정되어 있어 집합건축물(호별대장)처럼 분석합니다.")
            unit_info = get_expos_unit_details(addr_info["sigunguCd"], addr_info["bjdongCd"], addr_info["bun"], addr_info["ji"], ho_name, dong_name)
        elif is_jibbap and not ho_name:
            print("\n [안내] 해당 건물은 집합건축물(호별대장 있음)이지만 호실이 지정되지 않았습니다.")
            ho_input = input("[입력] 분석을 진행할 호실 번호를 입력해 주세요 (예: 201호, 건너뜀 시 엔터): ").strip()
            if ho_input:
                ho_name = ho_input.replace("호", "").strip()
                print(f" -> 요청하신 [{ho_name}호] 전유부 상세 정보 조회 중...")
                unit_info = get_expos_unit_details(addr_info["sigunguCd"], addr_info["bjdongCd"], addr_info["bun"], addr_info["ji"], ho_name, dong_name)
        if unit_info:
            print("--------------------------------------------------")
            print(f"   [ {unit_info.get('hoNm', ho_name)}호 전유부분 상세 정보 ]")
            print("--------------------------------------------------")
            print(f"  • 해당 층수  : {unit_info.get('flrNo')}층")
            if unit_info.get("area"):
                pyung = round(unit_info["area"] * 0.3025, 1)
                print(f"  • 전용면적  : {unit_info['area']:.2f} ㎡ ({pyung}평)")
                target_area = unit_info["area"]
            if unit_info.get("supply_area"):
                spyung = round(unit_info["supply_area"] * 0.3025, 1)
                print(f"  • 공급면적  : {unit_info['supply_area']:.2f} ㎡ ({spyung}평)")
            try:
                from serve_auto_upload import get_vworld_land_share
                land_share = get_vworld_land_share(vworld_key, pnu, "", ho_name)
                if land_share:
                    l_area = float(land_share)
                    l_pyung = round(l_area * 0.3025, 1)
                    print(f"  • 대지지분  : {l_area:.2f} ㎡ ({l_pyung}평)")
            except Exception as e:
                print(f"대지지분 조회 중 오류: {e}")
            viol_status = "⚠️ 위반건축물" if unit_info.get("viol_yn") == "Y" or unit_info.get("violBldYn") == "Y" else "정상 (위반 없음)"
            print(f"  • 위반 여부  : {viol_status}")
            apt_house_price = get_vworld_apartment_house_price(vworld_key, pnu, dong_name, ho_name)
            if apt_house_price:
                price_val = apt_house_price["price"]
                formatted_p = format_assessed_price(price_val)
                price_126 = int(price_val * 1.26)
                formatted_126 = format_assessed_price(price_126)
                print(f"  • 공동주택가격: {apt_house_price['year']}년 기준 {formatted_p} (126%: {formatted_126})")
            print("--------------------------------------------------")
            try:
                target_floor = int(re.sub('\\D', '', str(unit_info.get("flrNo", "0"))))
            except:
                target_floor = 0
        elif is_jibbap and ho_name:
            print(f" [!] 전유부 대장에서 [{ho_name}호]의 상세 정보를 찾지 못했습니다.")
        
        print("\n[희망 거래 형태 선택]")
        print("  1: 매매")
        print("  2: 전세")
        print("  3: 월세")
        t_choice = input("[입력] 번호를 선택하세요 (1/2/3): ").strip()
        while t_choice not in ("1", "2", "3"):
            print(" [!] 올바른 번호(1, 2, 3)를 입력해 주세요.")
            t_choice = input("[입력] 번호를 선택하세요 (1/2/3): ").strip()
        trade_type_map = {"1": "매매", "2": "전세", "3": "월세"}
        trade_type = trade_type_map[t_choice]
        room_choice = ""
        room_label = ""
        if not is_jibbap and trade_type in ("전세", "월세"):
            print("\n [안내] 해당 건물은 호별 면적 구분이 없는 일반건축물(단독/다가구)입니다.")
            print("        원활한 시세 비교(CMA)를 위해 분석할 임대차 매물의 방 개수 유형을 선택해 주세요.")
            print("  1: 원룸 / 1.5룸형")
            print("  2: 투룸형")
            print("  3: 쓰리룸 이상형")
            room_input = input("[입력] 번호를 선택하세요 (1/2/3): ").strip()
            while room_input not in ("1", "2", "3"):
                print(" [!] 올바른 번호(1, 2, 3)를 입력해 주세요.")
                room_input = input("[입력] 번호를 선택하세요 (1/2/3): ").strip()
            room_choice = room_input
            if room_choice == "1":
                room_label = "원룸/1.5룸형"
                target_area = 20.0
            elif room_choice == "2":
                room_label = "투룸형"
                target_area = 35.0
            elif room_choice == "3":
                room_label = "쓰리룸 이상형"
                target_area = 55.0
            floor_input = input("\n[입력] 해당 임대차 매물의 층수를 입력해 주세요 (숫자만 입력, 예: 반지하는 -1, 1층은 1, 2층은 2 등): ").strip()
            try:
                target_floor = int(floor_input.replace("층", "").strip())
            except:
                target_floor = 1
        client_phone = input("[입력] 의뢰인 전화번호 입력 (예: 010-1234-5678, 생략 시 엔터): ").strip()
        target_price = 0
        target_monthly = 0
        if trade_type == "매매":
            while True:
                price_input = input("[입력] 매매 희망가 입력 (단위: 만원, 예: 85000): ").strip()
                if price_input.isdigit():
                    target_price = int(price_input)
                    break
                print(" [!] 숫자만 입력해 주세요.")
        elif trade_type == "전세":
            while True:
                price_input = input("[입력] 보증금 입력 (단위: 만원, 예: 50000): ").strip()
                if price_input.isdigit():
                    target_price = int(price_input)
                    break
                print(" [!] 숫자만 입력해 주세요.")
        elif trade_type == "월세":
            while True:
                dep_input = input("[입력] 보증금 입력 (단위: 만원, 예: 10000): ").strip()
                if dep_input.isdigit():
                    target_price = int(dep_input)
                    break
                print(" [!] 숫자만 입력해 주세요.")
            while True:
                mon_input = input("[입력] 월세 입력 (단위: 만원, 예: 150): ").strip()
                if mon_input.isdigit():
                    target_monthly = int(mon_input)
                    break
                print(" [!] 숫자만 입력해 주세요.")
        desired_info = {"trade_type": trade_type, "price": target_price, "monthly_rent": target_monthly, "phone_number": client_phone, "room_count_choice": room_choice, "room_count_label": room_label}
        print("\n -> 최근 실거래(매매/임대차) 내역 및 자동 비교 조회 중...")
        transactions = get_recent_transactions(addr_info["sigunguCd"], addr_info["bun"], addr_info["ji"], prop_type, addr_info.get("bjdongNm"), target_build_year, target_house_type)
        trades = []
        jeonses = []
        wolses = []
        prop_type_name = "일반 부동산"
        selected_label = "최근 12개월"
        is_expanded = False
        if transactions:
            trades = [t for t in transactions if t.get("trade_type") == "매매"]
            jeonses = [t for t in transactions if t.get("trade_type") == "전세"]
            wolses = [t for t in transactions if t.get("trade_type") == "월세"]
            type_names = {"1": "아파트", "2": "연립/다세대/빌라", "3": "오피스텔", "4": "단독/다가구"}
            prop_type_name = type_names.get(prop_type, "일반 부동산")
        bld_data = {
            "is_jibbap": is_jibbap,
            "bld_nm": locals().get("bld_nm", ""),
            "dong_nm": locals().get("dong_nm", ""),
            "plat_area": locals().get("plat_area", 0.0),
            "lndcgr": locals().get("lndcgr", ""),
            "use_zone": locals().get("use_zone", ""),
            "land_price_m2": locals().get("land_price_m2"),
            "land_price_year": locals().get("land_price_year"),
            "arch_area": locals().get("arch_area", 0.0),
            "tot_area": locals().get("tot_area", 0.0),
            "vl_rat_tot_area": locals().get("vl_rat_tot_area", 0.0),
            "structure": locals().get("structure", ""),
            "main_purp": locals().get("main_purp", ""),
            "grnd_cnt": locals().get("grnd_cnt", 0),
            "ugrnd_cnt": locals().get("ugrnd_cnt", 0),
            "hhld": locals().get("hhld", 0),
            "fmly": locals().get("fmly", 0),
            "parking": locals().get("parking", 0),
            "apr_day": locals().get("apr_day", ""),
            "viol_str": locals().get("viol_str", "정상"),
            "ride_elvt": locals().get("ride_elvt", 0),
            "emgen_elvt": locals().get("emgen_elvt", 0),
            "elvt_cnt": locals().get("elvt_cnt", 0),
            "room_count_label": locals().get("room_label"),
            "indiv_house_price": locals().get("indiv_house_price"),
            "indiv_house_price_year": locals().get("indiv_house_price_year"),
            "reg_info": locals().get("reg_info", {"moatown": False, "moatown_name": "", "redev": False, "redev_name": "", "permit": False, "permit_name": "", "regulated": False, "regulated_name": ""}),
            "ho_details": locals().get("unit_info"),
            "ho_name": locals().get("ho_name", ""),
            "floor_map": locals().get("floor_map"),
            "expos_list_count": locals().get("expos_list_count", 0),
            "distinct_dongs": locals().get("distinct_dongs", []),
            "floors": locals().get("floors", []),
            "land_shares_raw": locals().get("items", [])
        }
        save_building_report(addr_info.get("road_address") or clean_address, bld_data)
        from trade_viewer import save_briefing_report
        display_addr = addr_info.get("road_address") or clean_address or "조회 대상 주소"
        save_briefing_report(display_addr, trades, jeonses, wolses, prop_type_name, period_label=selected_label, is_expanded=is_expanded, target_build_year=target_build_year, target_area=target_area, target_floor=target_floor, desired_info=desired_info)
        target_addr_str = addr_info.get("road_address") or clean_address
        safe_addr_for_open = "".join([c for c in target_addr_str if c not in (" ", "-", "_")]).strip()
        bld_pdf_path = os.path.abspath(f"종합분석보고서/건축물대장_{safe_addr_for_open.replace(' ', '_')}.pdf")
        brief_pdf_path = os.path.abspath(f"종합분석보고서/시세브리핑_{safe_addr_for_open.replace(' ', '_')}.pdf")
        opened_any = False
        if sys.platform == "win32":
            if os.path.exists(bld_pdf_path):
                os.startfile(bld_pdf_path)
                opened_any = True
            if os.path.exists(brief_pdf_path):
                os.startfile(brief_pdf_path)
                opened_any = True
        if opened_any:
            print("\n [안내] 생성된 PDF 보고서(건축물대장 및 시세브리핑)를 자동으로 실행하였습니다.")
            print("        (종합분석보고서 폴더 내에 함께 저장되어 있습니다.)")
        print("\n==================================================")
        upload_choice = input("[입력] 수집된 정보와 가격으로 부동산써브(Serve) 광고 자동 등록을 진행하시겠습니까? (y/n) [기본값: n]: ").strip().lower()
        if upload_choice == "y":
            sigungu_name = ""
            if clean_address:
                parts = clean_address.split(" ")
                if len(parts) >= 2:
                    sigungu_name = " ".join(parts[:2])
            bunji_val = addr_info["bun"]
            if addr_info.get("ji") and addr_info["ji"] != "0":
                bunji_val += "-" + addr_info["ji"]
            preset_data = {
                "trade_type": trade_type,
                "price": target_price,
                "monthly_rent": target_monthly,
                "phone_number": client_phone,
                "sigunguCd": addr_info["sigunguCd"],
                "bjdongCd": addr_info["bjdongCd"],
                "sigungu_name": sigungu_name,
                "bjdong_name": addr_info.get("bjdongNm", ""),
                "bunji_val": bunji_val,
                "ho_name": ho_name,
                "dong_name": dong_nm
            }
            print(" -> 부동산써브 자동 매물 등록 연동을 시작합니다...")
            from serve_auto_upload import run_serve_auto_upload
            run_serve_auto_upload(preset_data)
        print("═══════════════════════════════════════════════════════")
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        while True:
            try:
                run_building_viewer()
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"오류 발생: {e}")