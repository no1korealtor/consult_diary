import sys
import os
from datetime import datetime
from collections import defaultdict

sys.path.append(os.path.abspath("."))
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle
from reportlab.lib import colors

def create_group_scatter_plot_drawing(transactions, title="평형별 단지 비교 산포도", target_type="매매"):
    points_by_apt = defaultdict(list)
    min_date = None
    max_date = None
    
    PALETTE = [
        '#EF4444', # Red
        '#3B82F6', # Blue
        '#10B981', # Green
        '#F59E0B', # Orange
        '#8B5CF6', # Purple
        '#14B8A6', # Teal
        '#EC4899', # Pink
        '#6366F1'  # Indigo
    ]
    
    for t in transactions:
        if t.get("_trade_type") != target_type:
            continue
            
        try:
            dy = t.get("dealYear")
            dm = t.get("dealMonth")
            dd = t.get("dealDay", 1)
            if dy is None or dm is None: continue
                
            dt = datetime(int(dy), int(dm), int(dd))
            
            if target_type == "매매":
                price_str = str(t.get("dealAmount", "0")).replace(",", "").strip()
            else:
                price_str = str(t.get("deposit", "0") or t.get("guaranteeAmt", "0")).replace(",", "").strip()
                
            price = int(price_str)
            if price <= 0: continue
            
            if not min_date or dt < min_date: min_date = dt
            if not max_date or dt > max_date: max_date = dt
            
            apt_name = (t.get('aptNm') or t.get('mhouseNm') or '알수없음').strip()
            points_by_apt[apt_name].append((dt, price))
        except Exception as e:
            pass
            
    all_prices = []
    for pts in points_by_apt.values():
        all_prices.extend([p for _, p in pts])
        
    if not all_prices:
        return None
        
    min_p = min(all_prices)
    max_p = max(all_prices)
    diff = max_p - min_p
    if diff == 0: diff = 10000
    min_p = max(0, min_p - diff * 0.1)
    max_p = max_p + diff * 0.2 # extra space for labels
    
    dw = 515
    dh = 200
    d = Drawing(dw, dh)
    
    d.add(Rect(0, 0, dw, dh, fillColor=colors.HexColor('#F8FAFC'), strokeColor=colors.HexColor('#E2E8F0'), strokeWidth=1, rx=5, ry=5))
    d.add(String(15, dh - 20, f"🎯 {title}", fontName='KoreanFont', fontSize=9, fillColor=colors.HexColor('#0F172A'), textAnchor='start'))
    
    cx = 50
    cy = 30
    cw = dw - 70
    ch = dh - 60
    
    # Grid lines (Y)
    for i in range(5):
        y_val = cy + i * (ch / 4)
        price_val = min_p + i * ((max_p - min_p) / 4)
        d.add(Line(cx, y_val, cx + cw, y_val, strokeColor=colors.HexColor('#E2E8F0'), strokeWidth=0.5))
        if price_val >= 10000:
            lbl = f"{price_val/10000:.1f}억"
        else:
            lbl = f"{int(price_val):,}만"
        d.add(String(cx - 5, y_val - 3, lbl, fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor('#718096'), textAnchor='end'))
        
    if min_date and max_date and min_date != max_date:
        total_days = (max_date - min_date).days
        if total_days == 0: total_days = 1
        
        # Assign colors and draw points
        apt_names = sorted(points_by_apt.keys())
        color_map = {}
        
        legend_x = dw - 15
        
        for i, name in enumerate(apt_names):
            color = PALETTE[i % len(PALETTE)]
            color_map[name] = color
            
            pts = points_by_apt[name]
            # find max price for this apt
            max_pt_price = -1
            max_pt_dt = None
            
            for dt, p in pts:
                if p > max_pt_price:
                    max_pt_price = p
                    max_pt_dt = dt
                    
                x = cx + ((dt - min_date).days / total_days) * cw
                y = cy + ((p - min_p) / (max_p - min_p)) * ch
                d.add(Circle(x, y, 3, fillColor=colors.HexColor(color), strokeColor=colors.HexColor('#ffffff'), strokeWidth=0.5))
                
            # Draw label for highest point
            if max_pt_dt:
                x = cx + ((max_pt_dt - min_date).days / total_days) * cw
                y = cy + ((max_pt_price - min_p) / (max_p - min_p)) * ch
                lbl = f"최고 {max_pt_price/10000:.1f}억" if max_pt_price >= 10000 else f"최고 {max_pt_price:,}만"
                d.add(String(x, y + 5, lbl, fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor(color), textAnchor='middle'))
                
            # Draw legend (right aligned, stacking to the left)
            # name len roughly name*8
            str_w = len(name) * 8 + 15
            legend_x -= str_w
            d.add(Circle(legend_x + 5, dh - 17, 3, fillColor=colors.HexColor(color), strokeColor=None))
            d.add(String(legend_x + 12, dh - 20, name, fontName='KoreanFont', fontSize=8, fillColor=colors.HexColor('#475569')))
            
        d.add(String(cx, cy - 15, min_date.strftime("%Y.%m.%d"), fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor('#718096'), textAnchor='middle'))
        d.add(String(cx + cw, cy - 15, max_date.strftime("%Y.%m.%d"), fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor('#718096'), textAnchor='middle'))
        
    return d

print("Done")
