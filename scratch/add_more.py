import sys

def patch_more(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    more_funcs = """
def get_size_category_label(target_area, prop_type_name, apt_groups):
    if target_area is None:
        return "전체 면적"
    try:
        t_area = float(target_area)
        if prop_type_name == "아파트" and apt_groups:
            target_group = get_group_for_item({"excluUseAr": t_area}, apt_groups)
            if target_group:
                return target_group["label"]
            return f"전용면적 {t_area}㎡ 인근"
            
        if t_area < 26.0:
            return "원룸/1.5룸형 (전용 26㎡ 미만)"
        elif t_area < 43.0:
            return "투룸형 (전용 26㎡ ~ 43㎡ 미만)"
        else:
            return "쓰리룸 이상형 (전용 43㎡ 이상)"
    except:
        return "알 수 없음"

def generate_comparison_insights(cma_trades, cma_jeonses, cma_wolses):
    insights = []
    if len(cma_trades) > 0 and len(cma_jeonses) > 0:
        insights.append("• 매매와 전세 실거래가 활발하게 이루어지고 있습니다.")
    else:
        insights.append("• 비교 대상 거래 건수가 다소 제한적입니다.")
    return insights

def get_avg_display(items, is_rent, is_wolse=False):
    if not items:
        return "거래 없음"
    stats = calculate_subset_stats(items, is_rent, is_wolse)
    if not stats:
        return "거래 없음"
    return f"{stats['avg']} ({stats['count']}건)"
"""
    if "def get_size_category_label(" not in content:
        content = more_funcs + "\n" + content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Patched {file_path}")
    else:
        print("already patched")

patch_more('trade_viewer.py')
