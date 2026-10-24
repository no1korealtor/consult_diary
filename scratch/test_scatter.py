import sys
import os
from datetime import datetime

# sys.path setup
sys.path.append(os.path.abspath("."))
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle
from reportlab.lib import colors

def create_scatter_plot_drawing(transactions, title="실거래 산포도"):
    trades = []
    jeonses = []
    min_date = None
    max_date = None
    
    for t in transactions:
        ymd = str(t.get("dealYmd", ""))
        day = str(t.get("dealDay", "1")).zfill(2)
        if len(ymd) >= 6:
            try:
                dt = datetime(int(ymd[:4]), int(ymd[4:6]), int(day))
                
                # Check price
                if t.get("_trade_type") == "매매":
                    price_str = str(t.get("dealAmount", "0")).replace(",", "").strip()
                else:
                    price_str = str(t.get("deposit", "0")).replace(",", "").strip()
                    
                price = int(price_str)
                if price <= 0: continue
                
                if not min_date or dt < min_date: min_date = dt
                if not max_date or dt > max_date: max_date = dt
                
                if t.get("_trade_type") == "매매":
                    trades.append((dt, price))
                elif t.get("_trade_type") == "전세":
                    jeonses.append((dt, price))
            except Exception as e:
                pass
                
    all_prices = [p for _, p in trades + jeonses]
    if not all_prices:
        d = Drawing(515, 100)
        d.add(Rect(0, 0, 515, 100, fillColor=colors.HexColor('#F8FAFC'), strokeColor=colors.HexColor('#E2E8F0')))
        d.add(String(257, 50, "산포도를 그릴 데이터가 없습니다.", textAnchor='middle', fontName='KoreanFont', fontSize=10, fillColor=colors.HexColor('#718096')))
        return d
        
    min_p = min(all_prices)
    max_p = max(all_prices)
    diff = max_p - min_p
    if diff == 0: diff = 10000
    min_p = max(0, min_p - diff * 0.1)
    max_p = max_p + diff * 0.1
    
    dw = 515
    dh = 200
    d = Drawing(dw, dh)
    
    d.add(Rect(0, 0, dw, dh, fillColor=colors.HexColor('#F8FAFC'), strokeColor=colors.HexColor('#E2E8F0'), strokeWidth=1, rx=5, ry=5))
    d.add(String(15, dh - 20, f"🎯 {title} - 전체 면적 매매/전세 가격 분포", fontName='KoreanFont', fontSize=9, fillColor=colors.HexColor('#0F172A'), textAnchor='start'))
    
    # Legends
    d.add(Circle(dw - 100, dh - 17, 3, fillColor=colors.HexColor('#EF4444'), strokeColor=None))
    d.add(String(dw - 90, dh - 20, "매매", fontName='KoreanFont', fontSize=8, fillColor=colors.HexColor('#475569')))
    
    d.add(Circle(dw - 50, dh - 17, 3, fillColor=colors.HexColor('#3B82F6'), strokeColor=None))
    d.add(String(dw - 40, dh - 20, "전세", fontName='KoreanFont', fontSize=8, fillColor=colors.HexColor('#475569')))
    
    cx = 50
    cy = 30
    cw = dw - 70
    ch = dh - 60
    
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
        
        for dt, p in trades:
            x = cx + ((dt - min_date).days / total_days) * cw
            y = cy + ((p - min_p) / (max_p - min_p)) * ch
            d.add(Circle(x, y, 2.5, fillColor=colors.HexColor('#EF4444'), strokeColor=colors.HexColor('#B91C1C'), strokeWidth=0.5))
            
        for dt, p in jeonses:
            x = cx + ((dt - min_date).days / total_days) * cw
            y = cy + ((p - min_p) / (max_p - min_p)) * ch
            d.add(Circle(x, y, 2.5, fillColor=colors.HexColor('#3B82F6'), strokeColor=colors.HexColor('#1D4ED8'), strokeWidth=0.5))
            
        d.add(String(cx, cy - 15, min_date.strftime("%Y.%m"), fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor('#718096'), textAnchor='middle'))
        d.add(String(cx + cw, cy - 15, max_date.strftime("%Y.%m"), fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor('#718096'), textAnchor='middle'))
        
    return d

print("Done")
