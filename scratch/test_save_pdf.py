import sys
sys.path.append(r"d:\부동산업무\antigravity\consult_diary")
from trade_viewer import save_briefing_report_pdf

try:
    save_briefing_report_pdf(
        address="서울특별시 마포구 중동 395",
        trades=[{"aptNm": "건영월드컵", "jibun": "395", "excluUseAr": 59.7, "dealAmt": "80,000"}],
        jeonses=[],
        wolses=[],
        prop_type_name="아파트",
        filename_pdf="test_output.pdf",
        apt_groups=[{"label": "전용 59.7㎡형", "min": 59.0, "max": 60.0}],
        period_label="최근 24개월",
        is_expanded=True,
        target_build_year=None,
        target_area=59.7,
        target_floor=None,
        desired_info={},
        expansion_mode="auto",
        target_bld_nm="건영월드컵",
        target_bun="395",
        target_ji=""
    )
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
