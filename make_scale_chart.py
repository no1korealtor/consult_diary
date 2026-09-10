import math
from PIL import Image, ImageDraw, ImageFont

def make_notehead(color='#ffffff', outline='#00f2fe'):
    w, h = 32, 24
    im = Image.new('RGBA', (w, h), (0,0,0,0))
    d = ImageDraw.Draw(im)
    d.ellipse((3, 3, w - 3, h - 3), fill=color, outline=outline, width=1)
    im = im.rotate(22, resample=Image.BICUBIC)
    return im

def create_harmonica_scale_chart():
    width = 1200
    height = 1060
    img = Image.new('RGB', (width, height), color='#1e1e2f')
    draw = ImageDraw.Draw(img)

    f_title = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 24)
    f_sub = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 13)
    f_section = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 16)
    f_clef = ImageFont.truetype('C:/Windows/Fonts/seguisym.ttf', 56)
    f_note_name = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 16)
    f_eng_name = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 13)
    f_num = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 22)
    f_badge = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 13)
    f_badge_tag = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 10)
    f_tip_title = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 14)
    f_tip = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 13)
    f_tip_bd = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 13)

    # Notehead stamps
    head_white = make_notehead('#ffffff', '#00f2fe')
    head_gold = make_notehead('#f1c40f', '#ff9f43')

    # Header Card
    draw.rounded_rectangle((20, 15, width - 20, 80), radius=14, fill='#2a2a40', outline='#3a3a5a', width=1)
    draw.text((40, 24), "♪ 하모니카 오선보 계이름 · 음역 대조표 (높은음자리표 전음역)", font=f_title, fill="#4facfe")
    draw.text((40, 54), "하모니카 악보는 오직 높은음자리표만 사용! 저음 덧줄(저음 5·6·7)부터 고음까지 22홀(C키) 홀 번호 & 호흡법(불어/마셔) 매칭", font=f_sub, fill="#a0a0b0")

    sections = [
        {
            "title": "1. 저음역 (Low Octave) : 높은음자리표 아래 덧줄 (하모니카 1~7번 홀)",
            "subtitle": "※ '섬집 아기' 첫 음 등 가요·동요 멜로디에 자주 등장하는 아래 덧줄 저음부",
            "tag_color": "#0984e3",
            "notes": [
                {"name": "저음 도", "eng": "C3", "num": "1", "dot": "bottom", "hole": "2홀", "act": "불어", "is_blow": True, "step": -9},
                {"name": "저음 레", "eng": "D3", "num": "2", "dot": "bottom", "hole": "1홀", "act": "마셔", "is_blow": False, "step": -8},
                {"name": "저음 미", "eng": "E3", "num": "3", "dot": "bottom", "hole": "4홀", "act": "불어", "is_blow": True, "step": -7},
                {"name": "저음 파", "eng": "F3", "num": "4", "dot": "bottom", "hole": "3홀", "act": "마셔", "is_blow": False, "step": -6},
                {"name": "저음 솔", "eng": "G3", "num": "5", "dot": "bottom", "hole": "6홀", "act": "불어", "is_blow": True, "step": -5, "highlight": True},
                {"name": "저음 라", "eng": "A3", "num": "6", "dot": "bottom", "hole": "5홀", "act": "마셔", "is_blow": False, "step": -4},
                {"name": "저음 시", "eng": "B3", "num": "7", "dot": "bottom", "hole": "7홀", "act": "마셔", "is_blow": False, "step": -3},
            ]
        },
        {
            "title": "2. 중음역 (Middle Octave) : 가온 도부터 기본 5선 (하모니카 8~15번 홀)",
            "subtitle": "※ 가장 기본이 되는 주 멜로디 음역대 (가온 도 = 8번 홀 불기)",
            "tag_color": "#d63031",
            "notes": [
                {"name": "가온 도", "eng": "C4", "num": "1", "dot": "none", "hole": "8홀", "act": "불어", "is_blow": True, "step": -2},
                {"name": "중음 레", "eng": "D4", "num": "2", "dot": "none", "hole": "9홀", "act": "마셔", "is_blow": False, "step": -1},
                {"name": "중음 미", "eng": "E4", "num": "3", "dot": "none", "hole": "10홀", "act": "불어", "is_blow": True, "step": 0},
                {"name": "중음 파", "eng": "F4", "num": "4", "dot": "none", "hole": "11홀", "act": "마셔", "is_blow": False, "step": 1},
                {"name": "중음 솔", "eng": "G4", "num": "5", "dot": "none", "hole": "12홀", "act": "불어", "is_blow": True, "step": 2},
                {"name": "중음 라", "eng": "A4", "num": "6", "dot": "none", "hole": "13홀", "act": "마셔", "is_blow": False, "step": 3},
                {"name": "중음 시", "eng": "B4", "num": "7", "dot": "none", "hole": "15홀", "act": "마셔", "is_blow": False, "step": 4},
            ]
        },
        {
            "title": "3. 고음역 (High Octave) : 높은 5선 및 위 덧줄 (하모니카 14, 16~22번 홀)",
            "subtitle": "※ 고조되는 후렴구 및 맑은 고음 음역대",
            "tag_color": "#00b894",
            "notes": [
                {"name": "높은 도", "eng": "C5", "num": "1", "dot": "top", "hole": "14홀", "act": "불어", "is_blow": True, "step": 5},
                {"name": "높은 레", "eng": "D5", "num": "2", "dot": "top", "hole": "17홀", "act": "마셔", "is_blow": False, "step": 6},
                {"name": "높은 미", "eng": "E5", "num": "3", "dot": "top", "hole": "16홀", "act": "불어", "is_blow": True, "step": 7},
                {"name": "높은 파", "eng": "F5", "num": "4", "dot": "top", "hole": "19홀", "act": "마셔", "is_blow": False, "step": 8},
                {"name": "높은 솔", "eng": "G5", "num": "5", "dot": "top", "hole": "18홀", "act": "불어", "is_blow": True, "step": 9},
                {"name": "높은 라", "eng": "A5", "num": "6", "dot": "top", "hole": "21홀", "act": "마셔", "is_blow": False, "step": 10},
                {"name": "높은 시", "eng": "B5", "num": "7", "dot": "top", "hole": "22홀", "act": "마셔", "is_blow": False, "step": 11},
                {"name": "최고 도", "eng": "C6", "num": "1", "dot": "top-double", "hole": "20홀", "act": "불어", "is_blow": True, "step": 12},
            ]
        }
    ]

    sec_top = 95
    sec_height = 275
    line_sp = 14
    half_sp = line_sp / 2.0

    for s_idx, sec in enumerate(sections):
        curr_y = sec_top + s_idx * (sec_height + 15)
        # Section box
        draw.rounded_rectangle((20, curr_y, width - 20, curr_y + sec_height), radius=14, fill='#232338', outline='#35354e', width=1)
        
        # Header bar
        draw.rectangle((20, curr_y, width - 20, curr_y + 36), fill='#2a2a44')
        draw.rounded_rectangle((32, curr_y + 7, 36, curr_y + 29), radius=2, fill=sec['tag_color'])
        draw.text((46, curr_y + 8), sec['title'], font=f_section, fill='#ffffff')
        draw.text((680, curr_y + 11), sec['subtitle'], font=f_sub, fill='#8e9aaf')

        staff_x_start = 60
        staff_x_end = width - 40

        # Adjust Line 1 baseline according to octave requirements:
        if s_idx == 0:
            staff_y0 = curr_y + 82   # low notes go down to +145
        elif s_idx == 1:
            staff_y0 = curr_y + 115  # middle notes from +129 to +87
        else:
            staff_y0 = curr_y + 140  # high notes go up to +56

        # Draw 5 staff lines
        for l in range(5):
            ly = staff_y0 - l * line_sp
            draw.line([(staff_x_start, ly), (staff_x_end, ly)], fill='#6c7a9c', width=1)

        # Treble clef symbol centered around Line 2 (G4)
        # Line 2 is at staff_y0 - line_sp
        clef_y = staff_y0 - 4 * line_sp - 14
        draw.text((staff_x_start + 10, clef_y), '\U0001D11E', font=f_clef, fill='#4facfe')

        notes = sec['notes']
        note_start_x = staff_x_start + 85
        note_avail_width = (staff_x_end - 20) - note_start_x
        note_spacing = note_avail_width / len(notes)

        for n_idx, note in enumerate(notes):
            nx = int(note_start_x + n_idx * note_spacing + note_spacing * 0.45)
            step = note['step']
            ny = int(staff_y0 - step * half_sp)

            # Highlight card for '엄' (저음 솔)
            if note.get('highlight'):
                draw.rounded_rectangle((nx - 40, curr_y + 42, nx + 40, curr_y + sec_height - 10), radius=10, fill='#2c2642', outline='#f39c12', width=2)
                draw.rounded_rectangle((nx - 36, curr_y + 46, nx + 36, curr_y + 64), radius=6, fill='#f39c12')
                draw.text((nx - 33, curr_y + 48), "★섬집아기 '엄'", font=f_badge_tag, fill='#1e1e2f')

            # Ledger lines
            if step <= -2:
                for ls in range(-2, step - 1, -2):
                    ly = int(staff_y0 - ls * half_sp)
                    draw.line([(nx - 18, ly), (nx + 18, ly)], fill='#8ba4c9', width=2)
            if step >= 10:
                for ls in range(10, step + 1, 2):
                    ly = int(staff_y0 - ls * half_sp)
                    draw.line([(nx - 18, ly), (nx + 18, ly)], fill='#8ba4c9', width=2)

            # Paste rotated notehead
            head_img = head_gold if note.get('highlight') else head_white
            hw, hh = head_img.size
            img.paste(head_img, (nx - hw//2, ny - hh//2), head_img)

            # Stem
            stem_color = '#f1c40f' if note.get('highlight') else '#ffffff'
            if step < 4:
                # Stem up on right side
                draw.line([(nx + 7, ny - 1), (nx + 7, ny - 36)], fill=stem_color, width=2)
            else:
                # Stem down on left side
                draw.line([(nx - 7, ny + 1), (nx - 7, ny + 36)], fill=stem_color, width=2)

            # Info text positioning (well separated from staff)
            info_y = curr_y + 172
            num_str = note['num']
            dot_type = note['dot']
            num_color = '#ff758c' if note['is_blow'] else '#00f2fe'

            # 1. Number Notation (숫자보)
            if dot_type == 'bottom':
                draw.text((nx - 6, info_y), num_str, font=f_num, fill=num_color)
                draw.ellipse((nx - 3, info_y + 26, nx + 3, info_y + 32), fill=num_color)
            elif dot_type == 'top':
                draw.ellipse((nx - 3, info_y - 4, nx + 3, info_y + 2), fill=num_color)
                draw.text((nx - 6, info_y + 4), num_str, font=f_num, fill=num_color)
            elif dot_type == 'top-double':
                draw.ellipse((nx - 7, info_y - 4, nx - 1, info_y + 2), fill=num_color)
                draw.ellipse((nx + 1, info_y - 4, nx + 7, info_y + 2), fill=num_color)
                draw.text((nx - 6, info_y + 4), num_str, font=f_num, fill=num_color)
            else:
                draw.text((nx - 6, info_y), num_str, font=f_num, fill=num_color)

            # 2. 계이름 & 영어 음이름
            draw.text((nx - 24, info_y + 32), note['name'], font=f_note_name, fill='#ffffff')
            draw.text((nx - 12, info_y + 52), f"({note['eng']})", font=f_eng_name, fill='#9aa0a6')

            # 3. Harmonica Hole & Blow/Draw Badge
            badge_y = info_y + 72
            badge_color = '#ff758c' if note['is_blow'] else '#4facfe'
            badge_border = '#ff4757' if note['is_blow'] else '#00d2d3'
            
            draw.rounded_rectangle((nx - 28, badge_y, nx + 28, badge_y + 22), radius=6, fill='#1b1b2d', outline=badge_border, width=1)
            action_text = f"{note['hole']} {note['act']}"
            draw.text((nx - 24, badge_y + 3), action_text, font=f_badge, fill=badge_color)

    # Bottom Tip Banner
    tip_box_y = height - 90
    draw.rounded_rectangle((20, tip_box_y, width - 20, height - 12), radius=12, fill='#1e293b', outline='#3b82f6', width=2)
    draw.text((36, tip_box_y + 10), "★ 하모니카 저음(아래 덧줄) 악보 완벽 정복 팁", font=f_tip_title, fill='#38bdf8')
    tip_text_1 = "• 하모니카는 오직 높은음자리표 하나만 사용합니다! 가온 도(8번홀)보다 낮은 음은 오선 아래 '덧줄'을 그어 표기합니다."
    tip_text_2 = "• 덧줄 세는 법 : [덧줄 1개 = 가온 도(1)] → [덧줄 1개 아래 = 저음 시(7.)] → [덧줄 2개 = 저음 라(6.)] → [덧줄 2개 아래 = 저음 솔(5.)]"
    tip_text_3 = "• '섬집 아기' 첫 소절: [엄 (저음 솔 5. = 덧줄 2개 아래, 6홀 불기)] → [마 (가온 도 1 = 덧줄 1개, 8홀 불기)] → [가 (중음 레 2 = 9홀 마시기)] → [섬 (중음 미 3 = 10홀 불기)]"
    draw.text((36, tip_box_y + 30), tip_text_1, font=f_tip, fill='#cbd5e1')
    draw.text((36, tip_box_y + 48), tip_text_2, font=f_tip, fill='#93c5fd')
    draw.text((36, tip_box_y + 66), tip_text_3, font=f_tip, fill='#fef08a')

    out_path = 'd:/부동산업무/antigravity/consult_diary/scale_reference.png'
    img.save(out_path, format='PNG')
    print('Generated successfully at:', out_path)

if __name__ == '__main__':
    create_harmonica_scale_chart()
