# -*- coding: utf-8 -*-
import os
import sys
import re
import urllib.request
import urllib.parse
import json
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

from trade_viewer import (
    get_kakao_address_info, parse_address_and_ho, classify_property_type,
    parse_money_input, match_dong
)
from building_viewer import (
    get_vworld_apartment_house_price, get_vworld_individual_house_price,
    get_building_title_info, format_assessed_price
)

VWORLD_KEY = "80194C85-0EE3-3220-A3C1-3268AD8756B9"

def register_korean_font():
    """ReportLab용 맑은고딕 또는 기본 윈도우 한글 폰트 등록"""
    font_paths = [
        "C:\\Windows\\Fonts\\malgun.ttf",
        "C:\\Windows\\Fonts\\gulim.ttc",
        "C:\\Windows\\Fonts\\batang.ttc",
        "C:\\Windows\\Fonts\\맑은.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont("KoreanFont", path))
                pdfmetrics.registerFont(TTFont("KoreanFont-Bold", path))
                return True
            except Exception:
                pass
    try:
        pdfmetrics.registerFont(TTFont("KoreanFont", "Helvetica"))
        pdfmetrics.registerFont(TTFont("KoreanFont-Bold", "Helvetica-Bold"))
    except Exception:
        pass
    return False

register_korean_font()

def format_money_hangul(val):
    """금액(원)을 한글 표기(억/만 원)로 변환"""
    if not val or val == 0:
        return "0원"
    eok = val // 100_000_000
    man = (val % 100_000_000) // 10_000
    rem = val % 10_000
    res = ""
    if eok > 0:
        res += f"{eok}억 "
    if man > 0:
        res += f"{man:,}만 "
    if rem > 0 and not eok and not man:
        res += f"{rem:,}"
    res += "원"
    return re.sub(r'\s+', ' ', res).replace(' 만', '만').strip()

def generate_agreement_pdf(address, prop_name, house_price, mortgage, deposit, partial_amt, is_exempt, landlord_name="", tenant_name="", output_dir="종합분석보고서"):
    """
    민간임대주택에 관한 특별법 시행령에 따른
    「임대보증금 일부보증(또는 면제)에 대한 임차인 동의서」 A4 1페이지 법정 제출용 PDF 생성
    """
    os.makedirs(output_dir, exist_ok=True)
    clean_fn = re.sub(r'[^0-9a-zA-Z가-힣]', '_', address).strip('_')
    clean_fn = re.sub(r'_+', '_', clean_fn)
    prefix = "임대보증금_보증면제_동의서" if is_exempt else "임대보증금_일부보증_동의서"
    pdf_path = os.path.join(output_dir, f"{prefix}_{clean_fn}.pdf")

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=35,
        bottomMargin=35
    )

    styles = getSampleStyleSheet()
    title_text = "임대보증금 보증 가입의무 면제에 대한 동의서" if is_exempt else "임대보증금 일부보증에 대한 동의서"

    title_style = ParagraphStyle(
        "AgTitle",
        parent=styles["Normal"],
        fontName="KoreanFont",
        fontSize=18,
        leading=22,
        alignment=1,
        textColor=colors.HexColor("#1A202C"),
        spaceAfter=12
    )

    sub_law_style = ParagraphStyle(
        "AgSubLaw",
        parent=styles["Normal"],
        fontName="KoreanFont",
        fontSize=8.5,
        leading=12,
        alignment=2,
        textColor=colors.HexColor("#718096"),
        spaceAfter=10
    )

    h2_style = ParagraphStyle(
        "AgH2",
        parent=styles["Normal"],
        fontName="KoreanFont",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    tbl_hdr_style = ParagraphStyle(
        "TblHdr",
        parent=styles["Normal"],
        fontName="KoreanFont",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#2D3748"),
        alignment=1
    )

    tbl_cell_left = ParagraphStyle(
        "TblCellLeft",
        parent=styles["Normal"],
        fontName="KoreanFont",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#2D3748"),
        alignment=0
    )

    tbl_cell_center = ParagraphStyle(
        "TblCellCenter",
        parent=styles["Normal"],
        fontName="KoreanFont",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#2D3748"),
        alignment=1
    )

    tbl_cell_right = ParagraphStyle(
        "TblCellRight",
        parent=styles["Normal"],
        fontName="KoreanFont",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#2D3748"),
        alignment=2
    )

    bold_cell_right = ParagraphStyle(
        "BoldCellRight",
        parent=styles["Normal"],
        fontName="KoreanFont",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#C53030"),
        alignment=2
    )

    body_style = ParagraphStyle(
        "AgBody",
        parent=styles["Normal"],
        fontName="KoreanFont",
        fontSize=9,
        leading=14,
        textColor=colors.HexColor("#2D3748"),
        firstLineIndent=10
    )

    story = []

    # 1. 헤더 & 법령 근거
    story.append(Paragraph("【 민간임대주택에 관한 특별법 시행령 별지 표준서식 】", sub_law_style))
    story.append(Paragraph(f"<b>{title_text}</b>", title_style))
    story.append(Spacer(1, 4))

    # 상단 장식 구분선
    div_table = Table([[""]], colWidths=[515], rowHeights=[2])
    div_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#2B6CB0")),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(div_table)
    story.append(Spacer(1, 8))

    # 2. 임대주택의 표시
    story.append(Paragraph("<b>1. 임대주택의 표시</b>", h2_style))
    bld_data = [
        [Paragraph("<b>주택 소재지</b>", tbl_hdr_style), Paragraph(address, tbl_cell_left)],
        [Paragraph("<b>주택 유형</b>", tbl_hdr_style), Paragraph(prop_name, tbl_cell_left)]
    ]
    bld_table = Table(bld_data, colWidths=[100, 415])
    bld_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EDF2F7")),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(bld_table)
    story.append(Spacer(1, 8))

    # 3. 보증 대상 금액 및 주택가격 등의 현황
    story.append(Paragraph("<b>2. 보증 대상 금액 및 주택가격 등의 현황</b>", h2_style))
    total_debt = mortgage + deposit
    limit_60 = int(house_price * 0.60)

    price_data = [
        [Paragraph("<b>구 분</b>", tbl_hdr_style), Paragraph("<b>금 액</b>", tbl_hdr_style), Paragraph("<b>산출 기준 및 비고</b>", tbl_hdr_style)],
        [Paragraph("① 산정 주택가격", tbl_cell_center), Paragraph(f"{house_price:,} 원", tbl_cell_right), Paragraph(f"{format_money_hangul(house_price)} (공시가격 적용비율 반영)", tbl_cell_left)],
        [Paragraph("② 선순위 담보권 설정금액", tbl_cell_center), Paragraph(f"{mortgage:,} 원", tbl_cell_right), Paragraph(f"{format_money_hangul(mortgage)} (근저당권 등)", tbl_cell_left)],
        [Paragraph("③ 임대보증금", tbl_cell_center), Paragraph(f"{deposit:,} 원", tbl_cell_right), Paragraph(f"{format_money_hangul(deposit)} (계약 체결 보증금)", tbl_cell_left)],
        [Paragraph("④ 총 부채금액 (② + ③)", tbl_cell_center), Paragraph(f"{total_debt:,} 원", tbl_cell_right), Paragraph(f"{format_money_hangul(total_debt)} (부채비율: {(total_debt/house_price)*100:.1f}%)", tbl_cell_left)],
        [Paragraph("⑤ 주택가격의 60% 금액", tbl_cell_center), Paragraph(f"{limit_60:,} 원", tbl_cell_right), Paragraph(f"{format_money_hangul(limit_60)} (① × 60% 안전기준선)", tbl_cell_left)],
    ]

    if is_exempt:
        price_data.append([
            Paragraph("<b>⑥ 보증 가입 대상 금액</b>", tbl_hdr_style),
            Paragraph("<b>0 원 (가입의무 면제)</b>", bold_cell_right),
            Paragraph("<b>총 부채(④) ≤ 주택가격 60%(⑤) 로 전액 면제</b>", tbl_cell_left)
        ])
    else:
        price_data.append([
            Paragraph("<b>⑥ 보증 가입 대상 금액</b>", tbl_hdr_style),
            Paragraph(f"<b>{partial_amt:,} 원</b>", bold_cell_right),
            Paragraph(f"<b>{format_money_hangul(partial_amt)}</b> (④ - ⑤ 일부보증 금액)", tbl_cell_left)
        ])

    calc_table = Table(price_data, colWidths=[150, 140, 225])
    calc_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#FFF5F5")),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(calc_table)
    story.append(Spacer(1, 8))

    # 4. 법정 확인 및 동의 조항
    story.append(Paragraph("<b>3. 임차인 확인 및 동의 내용</b>", h2_style))
    if is_exempt:
        consent_text = (
            "본인은 위 임대주택의 임차인으로서 <b>「민간임대주택에 관한 특별법」 제49조제2항제3호</b> 및 "
            "같은 법 시행령 제40조에 따라, <b>선순위 담보권 설정금액과 임대보증금을 합한 총 부채금액이 "
            f"주택가격의 100분의 60 이하({format_money_hangul(limit_60)})</b>에 해당함을 확인하였으며, "
            "임대사업자가 <b>임대보증금 보증(보증보험)에 가입하지 않는 것에 대하여 충분한 설명을 듣고 이해하였기에 이에 동의합니다.</b>"
        )
    else:
        consent_text = (
            "본인은 위 임대주택의 임차인으로서 <b>「민간임대주택에 관한 특별법」 제49조제2항</b> 및 "
            "같은 법 시행령 제39조제2항에 따라, 선순위 담보권 설정금액과 임대보증금을 합한 금액에서 "
            f"주택가격의 100분의 60에 해당하는 금액을 뺀 금액(<b>금 {partial_amt:,}원 / {format_money_hangul(partial_amt)}</b>)에 대해서만 "
            "임대사업자가 <b>임대보증금 보증(일부보증)에 가입하는 것에 대하여 충분한 설명을 듣고 이해하였기에 이에 동의합니다.</b>"
        )

    consent_p = Paragraph(consent_text, body_style)
    cond_box = Table([[consent_p]], colWidths=[515])
    cond_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E0")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(cond_box)
    story.append(Spacer(1, 12))

    # 5. 작성일자
    today_str = datetime.now().strftime("%Y년   %m월   %d일")
    date_style = ParagraphStyle(
        "AgDate",
        parent=styles["Normal"],
        fontName="KoreanFont",
        fontSize=10,
        alignment=1,
        spaceAfter=14
    )
    story.append(Paragraph(today_str, date_style))

    # 6. 임대사업자 및 임차인 서명란
    l_name_disp = f"<b>{landlord_name}</b>" if landlord_name else "___________________"
    t_name_disp = f"<b>{tenant_name}</b>" if tenant_name else "___________________"

    sig_data = [
        [
            Paragraph("<b>임 대 사 업 자 (임대인)</b>", tbl_hdr_style),
            Paragraph("<b>임   차   인 (동의인)</b>", tbl_hdr_style)
        ],
        [
            Paragraph(
                f"성 명 (상호): {l_name_disp} (서명 또는 인)<br/>"
                f"생년월일 (등록번호): ___________________<br/>"
                f"연 락 처: ___________________",
                tbl_cell_left
            ),
            Paragraph(
                f"성 명: {t_name_disp} (서명 또는 인)<br/>"
                f"생년월일: ___________________<br/>"
                f"연 락 처: ___________________",
                tbl_cell_left
            )
        ]
    ]
    sig_table = Table(sig_data, colWidths=[255, 260])
    sig_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(sig_table)
    story.append(Spacer(1, 10))

    # 하단 유의사항
    notice_style = ParagraphStyle(
        "NoticeP",
        parent=styles["Normal"],
        fontName="KoreanFont",
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor("#718096")
    )
    story.append(Paragraph("※ 첨부서류: 1. 표준임대차계약서 사본 1부  2. 임차인 주민등록등본 또는 신분증 사본 1부", notice_style))
    story.append(Paragraph("※ 본 동의서는 민간임대주택에 관한 특별법에 따른 보증보험 가입 및 지자체(렌트홈) 임대차계약 신고 시 필수 첨부서류입니다.", notice_style))

    doc.build(story)
    return pdf_path

def get_housing_ratio(prop_type, assessed_price):
    """
    주택유형 및 공시가격 구간별 국토교통부 고시 주택가격 인정비율
    """
    if prop_type in ("1", "2"):  # 아파트, 연립/다세대
        if assessed_price < 900_000_000:
            return 1.40, "140% (공동주택 9억 미만)"
        elif assessed_price < 1_500_000_000:
            return 1.35, "135% (공동주택 9억~15억)"
        else:
            return 1.30, "130% (공동주택 15억 이상)"
    elif prop_type == "3":  # 오피스텔
        return 1.20, "120% (주거용 오피스텔 기준시가)"
    else:  # 단독/다가구
        return 1.70, "170% (개별단독주택가격 기준)"

def run_rental_guarantee_calculator():
    """
    주택임대사업자 임대보증금 보증보험 가입금액 및 보증료 계산기 메인 루틴
    """
    while True:
        print("\n" + "="*64)
        print("   ■ 주택임대사업자 임대보증금 보증보험 가입금액 계산기 ■   ")
        print("="*64)
        print(" [안내] 민간임대주택에 관한 특별법 제49조에 따른 보증보험")
        print("        (HUG / SGI) 가입 적격 여부, 일부보증 면제 요건 및")
        print("        임대인(75%)·임차인(25%) 부담 보증료를 자동 산출합니다.")
        print("        (종료 및 상위 메뉴로 이동하려면 'q' 또는 엔터 입력)")
        print("-"*64)

        address_input = input("\n[입력] 주택 주소 (예: 성산동 200-104 202호): ").strip()
        if not address_input or address_input.lower() == 'q':
            break

        clean_address, dong_name, ho_name = parse_address_and_ho(address_input)
        print(f"\n -> 주소 확인: {clean_address} (동: {dong_name or '없음'}, 호: {ho_name or '없음'})")
        addr_info = get_kakao_address_info(clean_address)
        if not addr_info:
            print(" [!] 주소 변환에 실패했습니다. 도로명이나 지번을 다시 확인해 주세요.")
            continue

        bun_val = str(addr_info.get("bun", "0")).zfill(4)
        ji_val = str(addr_info.get("ji", "0")).zfill(4)
        pnu = f"{addr_info['sigunguCd']}{addr_info['bjdongCd']}1{bun_val}{ji_val}"

        # 1. 건축물 표제부 및 주택 유형 확인
        print(" -> 건축물 표제부 및 주택 유형 확인 중...")
        titles = get_building_title_info(addr_info["sigunguCd"], addr_info["bjdongCd"], addr_info["bun"], addr_info["ji"])
        prop_type = "2"  # 기본 다세대/연립 가정
        prop_name = "연립/다세대주택"
        if titles:
            t0 = titles[0]
            if dong_name:
                for t in titles:
                    if match_dong(dong_name, t.get("dongNm", "")) or match_dong(dong_name, t.get("bldNm", "")):
                        t0 = t
                        break
            main_purp = t0.get("mainPurpsCdNm", "")
            bld_name = t0.get("bldNm", "").strip() or t0.get("dongNm", "").strip()
            etc_purp = t0.get("etcPurps", "")
            hhld_cnt = int(t0.get("hhldCnt", 0) or 0)
            prop_type = classify_property_type(main_purp, bld_name, etc_purp, hhld_cnt)
            type_names = {"1": "아파트", "2": "연립/다세대(빌라)", "3": "오피스텔", "4": "단독/다가구"}
            prop_name = type_names.get(prop_type, main_purp or "주거용 주택")

        print(f" -> 주택 유형 판정: {prop_name}")

        # 2. 공시가격 자동 조회
        print(" -> 국토교통부 공시가격 실시간 조회 중...")
        assessed_price = None
        assessed_year = ""
        if prop_type in ("1", "2", "3"):  # 공동주택 및 오피스텔
            apt_info = get_vworld_apartment_house_price(VWORLD_KEY, pnu, dong_name, ho_name)
            if apt_info and apt_info.get("price"):
                assessed_price = apt_info["price"]
                assessed_year = apt_info.get("year", "")
        else:  # 단독/다가구
            indiv_info = get_vworld_individual_house_price(VWORLD_KEY, pnu)
            if indiv_info and indiv_info.get("price"):
                assessed_price = indiv_info["price"]
                assessed_year = indiv_info.get("year", "")

        if assessed_price:
            print(f" -> 공시가격 확인 성공! ({assessed_year}년 기준: {format_assessed_price(assessed_price)})")
        else:
            print(" -> [참고] 공공데이터에서 해당 호실의 공시가격을 자동으로 찾지 못했습니다.")
            p_in = input("    공시가격을 직접 입력해 주세요 (단위: 만원, 예: 19500, 1.95억): ").strip()
            val_man = parse_money_input(p_in)
            if val_man and val_man > 0:
                assessed_price = val_man * 10_000
            else:
                print(" [!] 올바른 가격이 입력되지 않아 계산을 중단합니다.")
                continue

        # 3. 주택가격 산정
        default_ratio, ratio_desc = get_housing_ratio(prop_type, assessed_price)
        calc_house_price = int(assessed_price * default_ratio)

        print("\n" + "-"*64)
        print(f" [주택가격 산정 기준] {ratio_desc}")
        print(f"  - 공시가격      : {format_assessed_price(assessed_price)} ({assessed_price:,}원)")
        print(f"  - 산정 주택가격 : {format_assessed_price(calc_house_price)} ({calc_house_price:,}원)")
        print("-"*64)

        adj = input(" [선택] 감정평가액이나 KB시세가 있다면 입력 (없으면 그냥 엔터): ").strip()
        if adj:
            adj_man = parse_money_input(adj)
            if adj_man and adj_man > 0:
                calc_house_price = adj_man * 10_000
                print(f" -> 적용 주택가격(감정가/시세 반영): {format_assessed_price(calc_house_price)} ({calc_house_price:,}원)")
        else:
            print(" -> 공시가격 기준 산정금액을 그대로 적용합니다.")

        # 4. 임대차 및 담보권 정보 입력
        print("\n" + "-"*64)
        print(" [임대차 및 선순위 담보 정보 입력]")
        deposit_in = input("  - 임대보증금 입력 (필수, 단위: 만원, 예: 20000, 2억, 2억 5000): ").strip()
        deposit_man = parse_money_input(deposit_in)
        while not deposit_man or deposit_man <= 0:
            print("  [!] 올바른 보증금을 입력해 주세요.")
            deposit_in = input("  - 임대보증금 입력: ").strip()
            deposit_man = parse_money_input(deposit_in)
        deposit_val = deposit_man * 10_000

        mortgage_in = input("  - 선순위 담보권 설정금액 (근저당권 등, 없으면 엔터 또는 0): ").strip()
        mortgage_man = parse_money_input(mortgage_in) if mortgage_in else 0
        mortgage_val = (mortgage_man or 0) * 10_000

        fee_rate_in = input("  - 예상 연간 보증료율 % 입력 (기본값: 0.15% [엔터]): ").strip()
        try:
            fee_rate = float(fee_rate_in) / 100.0 if fee_rate_in else 0.0015
        except:
            fee_rate = 0.0015

        # 5. 부채비율 및 가입 적격 여부 판정
        total_debt = mortgage_val + deposit_val
        debt_ratio = (total_debt / calc_house_price) * 100.0 if calc_house_price > 0 else 999.0
        limit_60 = int(calc_house_price * 0.60)
        partial_base = total_debt - limit_60

        print("\n" + "="*64)
        print("             [보증보험 가입 요건 및 금액 분석 결과]             ")
        print("="*64)
        print(f" 1. 주택가격 산정  : {format_assessed_price(calc_house_price)} ({calc_house_price:,}원)")
        print(f" 2. 선순위 담보권  : {format_assessed_price(mortgage_val)} ({mortgage_val:,}원)")
        print(f" 3. 임대보증금     : {format_assessed_price(deposit_val)} ({deposit_val:,}원)")
        print(f" 4. 총 부채금액    : {format_assessed_price(total_debt)} ({total_debt:,}원)")
        print(f" 5. 총 부채비율    : {debt_ratio:.2f}% (한도: 주택가격의 100% 이내)")
        print("-"*64)

        if debt_ratio > 100.0:
            excess = total_debt - calc_house_price
            print(" [X] [판정 결과: 보증보험 가입 불가 (부채비율 100% 초과)]")
            print(f"    - 현재 부채비율이 {debt_ratio:.1f}%로 법정 한도(100%)를 초과합니다.")
            print(f"    - 가입을 위해서는 임대보증금을 최소 {format_assessed_price(excess)} 이상 낮추거나,")
            print(f"      선순위 근저당을 해당 금액만큼 상환·감액 등기해야 합니다.")
            print("="*64)
            input("\n엔터를 누르면 다음 계산을 진행합니다...")
            continue

        print(" [O] [판정 결과: 보증보험 가입 가능 (부채비율 100% 이내 적격)]")
        print("-"*64)

        # 6. 보증 대상 금액 판정 (전액 보증 vs 일부 보증)
        full_guarantee_amt = deposit_val

        is_exempt = False
        partial_guarantee_amt = 0
        if partial_base <= 0:
            is_exempt = True
            partial_guarantee_amt = 0
        else:
            partial_guarantee_amt = min(partial_base, deposit_val)

        print(" [보증 가입 대상 금액 비교]")
        print(f"  - 60% 안전기준선 : {format_assessed_price(limit_60)} (주택가격 × 60%)")
        print(f"  - 총 부채 - 60%선 : {format_assessed_price(partial_base)} ({partial_base:,}원)")
        print("")
        print(f"  ▶ [방식 A] 전액 보증 가입 시 : {format_assessed_price(full_guarantee_amt)} (보증금 전액)")

        if is_exempt:
            print("  ▶ [방식 B] 일부 보증 적용 시 : ★ 보증보험 가입의무 면제 대상! (가입금액 0원)")
            print("     (총 부채가 주택가격의 60% 이하이므로, 임차인 서면동의 시 보증보험 미가입 가능)")
        else:
            print(f"  ▶ [방식 B] 일부 보증 적용 시 : ★ {format_assessed_price(partial_guarantee_amt)} ★ ({partial_guarantee_amt:,}원)")
            reduction_ratio = ((full_guarantee_amt - partial_guarantee_amt) / full_guarantee_amt) * 100.0
            print(f"     (전액 가입 대비 보증 대상 금액이 {reduction_ratio:.1f}% 대폭 절감됩니다!)")

        print("-"*64)

        # 7. 예상 보증료 시뮬레이션 (법정 분담: 임대인 75% / 임차인 25%)
        print(f" [예상 연간 보증료 시뮬레이션 (보증료율 연 {fee_rate*100:.3f}% 적용 시)]")
        full_fee = int(full_guarantee_amt * fee_rate)
        full_landlord = int(full_fee * 0.75)
        full_tenant = full_fee - full_landlord

        print(f"  - 전액 보증 가입 시 (대상: {format_assessed_price(full_guarantee_amt)}): ")
        print(f"     - 연간 총 보증료: {full_fee:,} 원")
        print(f"     - 임대사업자 부담 (75%): {full_landlord:,} 원")
        print(f"     - 임차인 부담     (25%): {full_tenant:,} 원")

        if not is_exempt:
            part_fee = int(partial_guarantee_amt * fee_rate)
            part_landlord = int(part_fee * 0.75)
            part_tenant = part_fee - part_landlord
            save_fee = full_fee - part_fee

            print(f"  - 일부 보증 가입 시 (대상: {format_assessed_price(partial_guarantee_amt)}): ")
            print(f"     - 연간 총 보증료: {part_fee:,} 원")
            print(f"     - 임대사업자 부담 (75%): {part_landlord:,} 원")
            print(f"     - 임차인 부담     (25%): {part_tenant:,} 원")
            print(f"     ▶ 일부보증 선택 시 연간 보증료 총 {save_fee:,}원 절감!")
        else:
            print("  - 일부 보증(면제) 적용 시: 보증료 부담 0원 (전액 면제)")

        print("-"*64)
        print(" [공인중개사 실무 체크포인트 & 주의사항]")
        print("  1. '일부 보증' 또는 '면제'를 적용하려면 반드시 [임차인의 일부보증 동의서]를")
        print("     서면으로 받아 표준임대차계약서와 함께 지자체(렌트홈)에 신고해야 합니다.")
        print("  2. 선순위 근저당권이 세대별로 분리되어 있어야 하며, 다가구주택의 경우")
        print("     선순위 세입자들의 보증금 총액이 선순위 담보권에 합산됩니다.")
        print("  3. 임차인의 25% 보증료 분담금은 계약 체결 또는 갱신 시 임대인이 대납 후")
        print("     임차인에게 영수증을 제시하고 청구·정산하는 것이 일반적입니다.")
        print("  4. 보증보험 미가입 시 민간임대주택법 제65조에 따라 보증금의 최대 10%")
        print("     (최고 3,000만원 한도)의 과태료가 부과될 수 있습니다.")
        print("="*64)

        # 8. 임차인 동의서 A4 PDF 자동 작성 및 인쇄 연동
        if is_exempt or (partial_guarantee_amt < full_guarantee_amt and partial_guarantee_amt >= 0):
            doc_label = "보증면제" if is_exempt else "일부보증"
            print(f"\n [서식 자동출력] 임차인의 「{doc_label} 동의서(A4 표준서식)」 출력이 가능합니다.")
            print(f"    ※ 민간임대주택에 관한 특별법 시행령에 따른 법정 제출용 표준 양식입니다.")
            print_in = input(f" ▶ {doc_label} 동의서(A4 PDF)를 생성하여 바로 인쇄/확인하시겠습니까? (y/n) [기본값: y]: ").strip().lower()
            if print_in != 'n':
                l_name = input("  - 임대사업자(임대인) 성명 [엔터 시 서명용 밑줄]: ").strip()
                t_name = input("  - 임차인(세입자) 성명   [엔터 시 서명용 밑줄]: ").strip()

                # 전체 주소 표기 정리
                road_addr = addr_info.get("roadAddress", "")
                jibun_addr = addr_info.get("jibunAddress", "")
                unit_str = ""
                if dong_name and ho_name:
                    unit_str = f"{dong_name} {ho_name}"
                elif ho_name:
                    unit_str = f"{ho_name}"
                elif dong_name:
                    unit_str = f"{dong_name}"

                base_addr = road_addr if road_addr else clean_address
                if unit_str and unit_str not in base_addr:
                    full_disp_addr = f"{base_addr} {unit_str}".strip()
                else:
                    full_disp_addr = base_addr

                if jibun_addr and jibun_addr not in full_disp_addr:
                    full_disp_addr += f" ({jibun_addr})"

                try:
                    pdf_file = generate_agreement_pdf(
                        address=full_disp_addr,
                        prop_name=prop_name,
                        house_price=calc_house_price,
                        mortgage=mortgage_val,
                        deposit=deposit_val,
                        partial_amt=partial_guarantee_amt,
                        is_exempt=is_exempt,
                        landlord_name=l_name,
                        tenant_name=t_name,
                        output_dir="종합분석보고서"
                    )
                    abs_pdf = os.path.abspath(pdf_file)
                    print(f"\n [성공] 동의서가 성공적으로 생성되었습니다: {abs_pdf}")
                    if sys.platform == "win32" and os.path.exists(abs_pdf):
                        try:
                            os.startfile(abs_pdf)
                            print(" [안내] 기본 PDF 뷰어(인쇄 화면)를 자동으로 실행하였습니다.")
                        except Exception as e:
                            print(f" [!] 자동 실행 실패: {e}")
                except Exception as e:
                    print(f" [!] 동의서 PDF 생성 중 오류 발생: {e}")

        input("\n확인 후 엔터를 누르면 다음 주소를 계산합니다...")

if __name__ == '__main__':
    run_rental_guarantee_calculator()
