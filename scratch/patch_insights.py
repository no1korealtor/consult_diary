with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.strip().startswith("[Paragraph(ins, insight_p_style) for ins in insights_list]"):
        lines[i] = '        insight_paragraphs = [Paragraph(ins, insight_p_style) for ins in insights_list]\n'
    elif line.strip().startswith('insight_paragraphs = "🟢 해당"'):
        lines[i] = ''
    elif line.strip().startswith('ins = f" ({moa_status['):
        lines[i] = ''
    elif line.strip().startswith('[[p] for p in insight_paragraphs]'):
        lines[i] = '        insight_box_data = [[p] for p in insight_paragraphs]\n'
    elif line.strip().startswith('insight_box_data = "🟢 해당"'):
        lines[i] = ''
    elif line.strip().startswith('p = ", ".join(cond_parts)'):
        lines[i] = ''

with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
