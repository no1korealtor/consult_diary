import os

with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start = -1
end = -1
for i, line in enumerate(lines):
    if line.strip() == 'if True:' and i > 1000:
        if start == -1:
            start = i
    if line.strip() == 'print(f"\\\\n [오류] PDF 브리핑 파일 생성 중 오류 발생: {e}")' and i > 1000:
        end = i
        break

replacement = """        if kakao_img or naver_img:
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
                    reg_part = f" | {m_reg}" if m_reg else ""
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
            except Exception as e:
                import traceback; traceback.print_exc()
                pass
        doc.build(story, onFirstPage=draw_page_decorations, onLaterPages=draw_page_decorations)
        print(f"       -> PDF 파일 위치: {os.path.abspath(filename_pdf)}")
    except Exception as e:
        import traceback; traceback.print_exc()
        print(f"\\n [오류] PDF 브리핑 파일 생성 중 오류 발생: {e}")
"""

if start != -1 and end != -1:
    new_lines = lines[:start] + [replacement] + lines[end+1:]
    with open('trade_viewer.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
