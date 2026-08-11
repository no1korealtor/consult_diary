import os

def update_file(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # For PDF CTA
    content = content.replace(
        'story.append(Paragraph(\'"데이터로 설명하고,<br/>신뢰로 연결합니다."\', italic_quote_style))',
        'story.append(Paragraph(\'"본 자료는 참고용이며, 정확한 시세와 매물 상담은 직접 전화주시면 친절하게 안내해 드립니다.<br/><font color="#E53E3E"><b>지금 바로 전화주시면, 고객님께 딱 맞는 최적의 매물을 찾아드립니다!</b></font>"<br/><br/>데이터로 설명하고, 신뢰로 연결합니다.\', italic_quote_style))'
    )

    # For TEXT CTA in trade_viewer
    content = content.replace(
        'report_lines.append("※ 본 브리핑 자료는 중개업무 참고용으로 법적 효력을 가지지 않습니다.")\n                    report_lines.append("================================================================================")',
        'report_lines.append("※ 본 브리핑 자료는 중개업무 참고용으로 법적 효력을 가지지 않습니다.")\n                    report_lines.append("🎯 [상담 안내] 정확한 현장 시세와 매물 상담은 저희 사무소로 직접 전화 주시면 친절히 안내해 드립니다.")\n                    report_lines.append("   부담 없이 지금 바로 연락 주세요! 고객님께 딱 맞는 최적의 매물을 찾아드립니다!")\n                    report_lines.append("================================================================================")'
    )
    
    # For TEXT CTA in building_viewer
    content = content.replace(
        'report_lines.append("※ 본 브리핑 자료는 중개업무 참고용으로 법적 효력을 가지지 않습니다.")\n                report_lines.append("================================================================================")',
        'report_lines.append("※ 본 브리핑 자료는 중개업무 참고용으로 법적 효력을 가지지 않습니다.")\n                report_lines.append("🎯 [상담 안내] 정확한 현장 시세와 매물 상담은 저희 사무소로 직접 전화 주시면 친절히 안내해 드립니다.")\n                report_lines.append("   부담 없이 지금 바로 연락 주세요! 고객님께 딱 맞는 최적의 매물을 찾아드립니다!")\n                report_lines.append("================================================================================")'
    )

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'{file_path} CTA updated')

update_file(r'd:\부동산업무\antigravity\consult_diary\trade_viewer.py')
update_file(r'd:\부동산업무\antigravity\consult_diary\building_viewer.py')
