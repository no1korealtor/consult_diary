with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if line.strip().startswith("if target_floor is None:") and "floor_cat = \"upper\"" in lines[i-1]:
        start_idx = i - 1
    if line.strip().startswith("print(f\"\\n [오류] 브리핑 파일 저장 중 오류 발생: {e}\")"):
        end_idx = i

if start_idx != -1 and end_idx != -1:
    replacement = """            floor_cat = "upper"
            if target_floor is not None:
                try:
                    fl = int(target_floor)
                    if fl < 0 or "지하" in str(target_floor):
                        floor_cat = "base"
                    elif fl == 1:
                        floor_cat = "first"
                    else:
                        floor_cat = "upper"
                except:
                    floor_cat = "base"
                    if "지하" not in str(target_floor) and "지" in str(target_floor):
                        pass
            
            ref_val, ref_desc = get_cma_ref_price(match_list, floor_cat, is_rent=trade_type != "매매", is_wolse=trade_type == "월세")
            report_lines.append("■ [희망 거래가 분석 및 적정성 평가]")
            phone_no = desired_info.get("phone_number")
            if phone_no:
                masked_phone = mask_phone_number(phone_no)
                report_lines.append(f"  • 의뢰인 연락처  : {masked_phone}")
            
            price_label_str = "알 수 없음" # Assuming it exists
            if trade_type == "매매":
                price_label_str = local_format_price(d_price)
            elif trade_type == "전세":
                price_label_str = local_format_price(d_price)
            else:
                price_label_str = f"보증금 {local_format_price(d_price)} / 월세 {d_monthly}만원"
            report_lines.append(f"  • 의뢰 고객 희망 조건: {price_label_str}")
            
            if ref_val:
                report_lines.append(f"  • 적정 시세 기준선  : {local_format_price(ref_val)} ({ref_desc})")
                d_converted = d_price
                if trade_type == "월세":
                    d_converted = d_price + (d_monthly * 100)
                diff = d_converted - ref_val
                pct = diff / ref_val * 100
                ref_val_str = local_format_price(ref_val)
                diff_val_str = local_format_price(abs(diff))
                if abs(pct) <= 5.0:
                    eval_title = "적절함 (인근 시세 수준)"
                    detail_desc = f"희망 하시는 거래 조건은 인근 적정 시세({ref_val_str}, {ref_desc} 기준) 대비 약 {abs(pct):.1f}% 차이로, 현재 시장 가격대 범위 내에서 매우 적정하게 책정된 상태입니다."
                elif diff < 0:
                    eval_title = "저렴함 (시세 대비 가격경쟁력 우수)"
                    detail_desc = f"희망 하시는 거래 조건은 인근 적정 시세({ref_val_str}, {ref_desc} 기준) 대비 약 {diff_val_str} ({abs(pct):.1f}%) 저렴하게 책정되어 있습니다. 시장 진입 시 빠른 거래 성사가 예상되어 가격 경쟁력이 높습니다."
                else:
                    eval_title = "높음 (가격 조정 권장)"
                    detail_desc = f"희망 하시는 거래 조건은 인근 적정 시세({ref_val_str}, {ref_desc} 기준) 대비 약 {diff_val_str} ({pct:.1f}%) 높게 책정되어 있습니다. 거래 성사 및 빠른 중개를 위해 의뢰인과의 상의를 통한 가격 조정을 권장합니다."
            else:
                report_lines.append(f"  • 적정 시세 기준선  : 판단 불가 (비교 사례 부족)")
                eval_title = "보류 (비교 사례 부족)"
                detail_desc = "인근 지역 내 유사한 거래 사례(동일 면적대 및 층수별 사례)가 부족하여 자동 적정성 평가가 제한적입니다. 주변 법정동 및 대체 매물 시세를 추가로 고려하시기 바랍니다."
            
            report_lines.append(f"  • 거래희망가 평가 결과: {eval_title}")
            report_lines.append(f"  • 종합 의견: {detail_desc}")
            report_lines.append("--------------------------------------------------------------------------------")
            
        report_lines.append("■ [안내] 시세 데이터 수집 및 분석 기준 안내")
        report_lines.append("  • 아파트/다세대빌라/오피스텔: 입력 주소와 100% 동일 지번(단지/건물)의 실거래가 기준입니다.")
        report_lines.append("  • 단독/다가구 주택:")
        report_lines.append("    - 매매: 지번 매칭 및 국토교통부 마스킹 범위 내 인접 필지 실거래가 기준입니다.")
        report_lines.append("    - 전월세: 국토교통부 지번 미제공 정책에 따라 동일 법정동 내 건축년도(±1년) 및 유형이 일치하는")
        report_lines.append("             인근 유사 주택의 거래 사례를 기준으로 자동 산출한 시세입니다.")
        report_lines.append("================================================================================")
        report_lines.append("※ 본 브리핑 자료는 중개업무 참고용으로 법적 효력을 가지지 않습니다.")
        report_lines.append("================================================================================")
        console_content = "\\n".join(report_lines)
        
        member = load_member_info()
        m_name = "조항준 공인중개사"
        phone_line = "📞 010-9128-0586\\n☎ 02-375-4489"
        addr_lines = ["📍 서울 마포구 모래내로 7길 52"]
        if member:
            m_name = format_member_name(member.get("name", "")) or m_name
            m_phone = member.get("phone", "")
            if m_phone:
                phone_line = f"📞 {m_phone}"
            m_addr = member.get("office_address", "")
            if m_addr:
                addr_lines = [f"📍 {m_addr}"]
            m_reg = member.get("registration_number", "")
            if m_reg:
                addr_lines.append(f"등록번호: {m_reg}")
        
        report_lines.append("──────────────────────────────")
        report_lines.append("")
        report_lines.append("        감사합니다.")
        report_lines.append("")
        report_lines.append("이번 분석이 도움이 되셨기를 바랍니다.")
        report_lines.append("")
        report_lines.append("──────────────────────────────")
        report_lines.append("")
        report_lines.append(m_name)
        report_lines.append("")
        report_lines.append("데이터 기반 부동산 분석")
        report_lines.append("매매 · 임대차 · 투자 상담")
        report_lines.append("")
        report_lines.append(phone_line)
        report_lines.append("")
        for al in addr_lines:
            report_lines.append(al)
        report_lines.append("")
        report_lines.append("──────────────────────────────")
        report_lines.append("")
        report_lines.append('"데이터로 설명하고,')
        report_lines.append('신뢰로 연결합니다."')
        report_lines.append("")
        report_lines.append("SHINDAERIM PROPERTY INTELLIGENCE")
        
        report_content = "\\n".join(report_lines)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_content)
        print("\\n [알림] 시세 브리핑 자료가 성공적으로 저장되었습니다!")
        print(f"       -> 텍스트 파일 위치: {os.path.abspath(filename)}")
        
        pdf_filename = filename.replace(".txt", ".pdf")
        save_briefing_report_pdf(address, trades, jeonses, wolses, prop_type_name, pdf_filename, apt_groups, period_label, is_expanded, target_build_year, target_area, target_floor=target_floor, desired_info=desired_info, expansion_mode=expansion_mode)
        
        try:
            import shutil
            unified_dir = "종합분석보고서"
            os.makedirs(unified_dir, exist_ok=True)
            unified_txt = os.path.join(unified_dir, f"시세브리핑_{safe_addr.replace(' ', '_')}.txt")
            unified_pdf = os.path.join(unified_dir, f"시세브리핑_{safe_addr.replace(' ', '_')}.pdf")
            shutil.copy2(filename, unified_txt)
            if os.path.exists(pdf_filename):
                shutil.copy2(pdf_filename, unified_pdf)
            print("       -> 종합분석보고서 통합 폴더에도 복사본이 저장되었습니다.")
        except Exception as copy_err:
            print(f"       [!] 통합 폴더 복사 중 오류 발생: {copy_err}")
            
    except Exception as e:
        import traceback; traceback.print_exc()
        try:
            print("\\n" + console_content + "\\n")
            open(filename, "w", encoding="utf-8")
        except:
            pass
        print(f"\\n [오류] 브리핑 파일 저장 중 오류 발생: {e}")
"""
    new_lines = lines[:start_idx] + [replacement + "\n"] + lines[end_idx+1:]
    with open('trade_viewer.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Patched!")
else:
    print(f"Not found! start_idx={start_idx}, end_idx={end_idx}")
