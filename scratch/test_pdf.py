import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

def test_generate_pdf():
    # 1. 폰트 경로 탐색 및 등록
    font_path = "C:\\Windows\\Fonts\\malgun.ttf"
    if not os.path.exists(font_path):
        font_path = "C:\\Windows\\Fonts\\gulim.ttc"
    
    print(f"Using font: {font_path}")
    pdfmetrics.registerFont(TTFont('MalgunGothic', font_path))
    
    # 2. PDF 생성 경로
    pdf_filename = "test_output.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    # custom style
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Normal'],
        fontName='MalgunGothic',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1A365D'),
        alignment=1, # Center
        spaceAfter=20
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='MalgunGothic',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=10
    )
    
    story = []
    story.append(Paragraph("시세 브리핑 테스트 제목", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("안녕하세요. 한글 테스트입니다. 잘 나오나요?", body_style))
    
    doc.build(story)
    print(f"PDF successfully created: {os.path.abspath(pdf_filename)}")

if __name__ == "__main__":
    test_generate_pdf()
