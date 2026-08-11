import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

def register_korean_font():
    font_paths = [
        "C:\\Windows\\Fonts\\malgun.ttf",       # Malgun Gothic
        "C:\\Windows\\Fonts\\gulim.ttc",        # Gulim
        "C:\\Windows\\Fonts\\batang.ttc",       # Batang
        "C:\\Windows\\Fonts\\맑은.ttf",
    ]
    
    registered = False
    for path in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont('KoreanFont', path))
                registered = True
                print(f"Registered Korean font: {path}")
                break
            except Exception as e:
                print(f"Failed to register font {path}: {e}")
                continue
                
    if not registered:
        print("No Korean font registered, falling back to Helvetica")
        pdfmetrics.registerFont(TTFont('KoreanFont', 'Helvetica'))

def test_generate_briefing_pdf():
    register_korean_font()
    
    pdf_filename = "test_briefing_report.pdf"
    
    # Page setup
    doc = SimpleDocTemplate(
        pdf_filename, 
        pagesize=A4, 
        rightMargin=47, 
        leftMargin=47, 
        topMargin=40, 
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Normal'],
        fontName='KoreanFont',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1A365D'),
        alignment=1, # Center
        spaceAfter=15,
        bold=True
    )
    
    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='KoreanFont',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#2C5282'),
        spaceBefore=14,
        spaceAfter=6,
        bold=True
    )
    
    label_style = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='KoreanFont',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#4A5568'),
        bold=True
    )
    
    value_style = ParagraphStyle(
        'MetaValue',
        parent=styles['Normal'],
        fontName='KoreanFont',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#2D3748')
    )
    
    table_hdr_style = ParagraphStyle(
        'TableHdr',
        parent=styles['Normal'],
        fontName='KoreanFont',
        fontSize=9,
        leading=12,
        textColor=colors.white,
        alignment=1, # Center
        bold=True
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='KoreanFont',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#2D3748')
    )
    
    table_cell_style_center = ParagraphStyle(
        'TableCellCenter',
        parent=table_cell_style,
        alignment=1 # Center
    )
    
    table_cell_style_right = ParagraphStyle(
        'TableCellRight',
        parent=table_cell_style,
        alignment=2 # Right
    )
    
    notice_title_style = ParagraphStyle(
        'NoticeTitle',
        parent=styles['Normal'],
        fontName='KoreanFont',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#718096'),
        bold=True,
        spaceBefore=15,
        spaceAfter=4
    )
    
    notice_body_style = ParagraphStyle(
        'NoticeBody',
        parent=styles['Normal'],
        fontName='KoreanFont',
        fontSize=8,
        leading=12,
        textColor=colors.HexColor('#718096')
    )
    
    story = []
    
    # 1. Header Bar Accent
    # We can draw it using a small Table
    accent_bar = Table([[""]], colWidths=[500], rowHeights=[4])
    accent_bar.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1A365D')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(accent_bar)
    story.append(Spacer(1, 15))
    
    # 2. Main Title
    story.append(Paragraph("부동산 실거래 시세 브리핑", title_style))
    story.append(Spacer(1, 10))
    
    # 3. Metadata Box
    address = "서울특별시 마포구 성산동 138-4"
    prop_type_name = "연립/다세대/빌라"
    
    meta_data = [
        [Paragraph("<b>조회 대상 주소</b>", label_style), Paragraph(address, value_style)],
        [Paragraph("<b>부동산 유형</b>", label_style), Paragraph(prop_type_name, value_style)],
        [Paragraph("<b>분석 기준 기간</b>", label_style), Paragraph("최근 12개월 (국토교통부 실거래가 기준)", value_style)],
        [Paragraph("<b>보고서 발행일</b>", label_style), Paragraph(datetime.now().strftime("%Y년 %m월 %d일"), value_style)]
    ]
    meta_table = Table(meta_data, colWidths=[100, 400])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#EDF2F7')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))
    
    # Helper to generate table
    def build_summary_table(section_title, data_rows):
        sect_heading = Paragraph(section_title, h2_style)
        
        headers = [
            Paragraph("<b>면적 구분</b>", table_hdr_style),
            Paragraph("<b>거래 건수</b>", table_hdr_style),
            Paragraph("<b>실거래가 범위</b>", table_hdr_style),
            Paragraph("<b>평균 실거래가</b>", table_hdr_style),
            Paragraph("<b>전용 평단가</b>", table_hdr_style)
        ]
        
        table_content = [headers]
        
        if not data_rows:
            table_content.append([
                Paragraph("최근 12개월간 신고된 거래 사례가 없습니다.", table_cell_style_center),
                "", "", "", ""
            ])
        else:
            for row in data_rows:
                table_content.append([
                    Paragraph(row[0], table_cell_style),
                    Paragraph(row[1], table_cell_style_center),
                    Paragraph(row[2], table_cell_style_right),
                    Paragraph(row[3], table_cell_style_right),
                    Paragraph(row[4], table_cell_style_right)
                ])
                
        t = Table(table_content, colWidths=[150, 50, 120, 90, 90])
        
        t_style = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2B6CB0')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ]
        
        # Alternating row colors
        if data_rows:
            for idx in range(1, len(table_content)):
                bg_color = colors.HexColor('#FFFFFF') if idx % 2 == 1 else colors.HexColor('#F7FAFC')
                t_style.append(('BACKGROUND', (0, idx), (-1, idx), bg_color))
        else:
            t_style.append(('SPAN', (0,1), (-1,1)))
            t_style.append(('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#FFFFFF')))
            
        t.setStyle(TableStyle(t_style))
        return sect_heading, t
    
    # 4. Sections
    # 매매
    sales_rows = [
        ["원룸/1.5룸형 (전용 26㎡ 미만)", "3건", "1억 2,000만 ~ 1억 4,500만", "1억 3,200만", "평당 2,150만"],
        ["투룸형 (전용 26㎡ ~ 43㎡ 미만)", "12건", "2억 1,000만 ~ 2억 7,800만", "2억 4,300만", "평당 2,380만"],
        ["쓰리룸 이상형 (전용 43㎡ 이상)", "5건", "3억 4,000만 ~ 4억 2,000만", "3억 8,500만", "평당 2,520만"]
    ]
    h, t = build_summary_table("■ [매매] 시세 요약", sales_rows)
    story.append(h)
    story.append(Spacer(1, 4))
    story.append(t)
    
    # 전세
    jeonse_rows = [
        ["원룸/1.5룸형 (전용 26㎡ 미만)", "1건", "9,500만", "9,500만", "평당 1,580만"],
        ["투룸형 (전용 26㎡ ~ 43㎡ 미만)", "8건", "1억 8,000만 ~ 2억 2,000만", "1억 9,800만", "평당 1,820만"],
        ["쓰리룸 이상형 (전용 43㎡ 이상)", "0건", "거래 사례 없음", "거래 사례 없음", "계산 불가"] # let's just mock empty or let build_summary_table handle empty
    ]
    # Filter out empty or display as is
    h, t = build_summary_table("■ [전세] 시세 요약", jeonse_rows)
    story.append(h)
    story.append(Spacer(1, 4))
    story.append(t)
    
    # 월세
    wolse_rows = [
        ["원룸/1.5룸형 (전용 26㎡ 미만)", "2건", "1,000만/45만 ~ 1,000만/50만", "1,000만/48만", "평당 1,650만"],
        ["투룸형 (전용 26㎡ ~ 43㎡ 미만)", "4건", "2,000만/75만 ~ 3,000만/80만", "2,500만/77만", "평당 1,780만"],
        ["쓰리룸 이상형 (전용 43㎡ 이상)", "0건", "거래 사례 없음", "거래 사례 없음", "계산 불가"]
    ]
    h, t = build_summary_table("■ [월세] 시세 요약 (보증금 + 월세 * 100 환산 기준)", wolse_rows)
    story.append(h)
    story.append(Spacer(1, 4))
    story.append(t)
    
    # 5. Notice / Disclaimer
    story.append(Spacer(1, 10))
    story.append(Paragraph("■ [안내] 시세 데이터 수집 및 분석 기준 안내", notice_title_style))
    story.append(Spacer(1, 4))
    
    notice_text = (
        "• 아파트/다세대빌라/오피스텔: 입력 주소와 100% 동일 지번(단지/건물)의 실거래가 기준입니다.<br/>"
        "• 단독/다가구 주택:<br/>"
        "  - 매매: 지번 매칭 및 국토교통부 마스킹 범위 내 인접 필지 실거래가 기준입니다.<br/>"
        "  - 전월세: 국토교통부 지번 미제공 정책에 따라 동일 법정동 내 건축년도(±1년) 및 유형이 일치하는 인근 유사 주택의 거래 사례를 기준으로 자동 산출한 시세입니다.<br/>"
        "• 본 브리핑 자료는 중개업무 참고용으로 법적 효력을 가지지 않습니다."
    )
    
    # Wrap notice in a gray box
    notice_box = Table([[Paragraph(notice_text, notice_body_style)]], colWidths=[500])
    notice_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(notice_box)
    
    doc.build(story)
    print(f"Mock Briefing PDF successfully created: {os.path.abspath(pdf_filename)}")

if __name__ == "__main__":
    test_generate_briefing_pdf()
