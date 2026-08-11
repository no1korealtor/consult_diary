import time
import sys
import os
import json
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.common.by import By

# 기존 봇 모듈들 가져오기
from lh_auto_upload import run_lh_auto_upload
from serve_auto_upload import run_serve_auto_upload
from audit_serve_list import run_audit_serve_list
from building_viewer import run_building_viewer
from trade_viewer import run_trade_viewer
from market_analyser import run_market_analysis
import serve_auto_upload  # _kept_alive_driver 공유를 위해 모듈 직접 참조

_auth_driver = None  # 중개수첩 인증용 브라우저 (최초 1회만 로그인)

# ─── 배포 정보 ───────────────────────────────────────────
CONTACT_NAME    = "조항준"
CONTACT_PHONE   = "010-9128-0586"
SPONSOR_BANK    = "신한은행"
SPONSOR_ACCOUNT = "218-12-036791"
TRIAL_MONTHS    = 3          # 무료 체험 기간 (개월)
TRIAL_FILE_NAME = "trial_start.json"  # exe 폴더에 저장됨
# ─────────────────────────────────────────────────────────

def _get_trial_file_path():
    """exe 실행 시에는 exe 폴더, 스크립트 실행 시에는 스크립트 폴더에 저장"""
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, TRIAL_FILE_NAME)

def _get_member_file_path():
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "member_info.json")

def attempt_background_sync():
    import json
    import requests
    import os
    
    p_path = _get_member_file_path()
    if not os.path.exists(p_path):
        return None
        
    try:
        with open(p_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        return None
        
    if not isinstance(data, dict):
        return None
        
    token = data.get("token")
    if not token or not token.get("access_token") or not token.get("refresh_token"):
        return None
        
    access_token = token["access_token"]
    refresh_token = token["refresh_token"]
    user_id = token.get("user_id")
    if not user_id:
        return None
        
    # 1. Try to fetch profile with existing access token
    headers = {
        "apikey": "sb_publishable_Y3waCN-Y0LA26BC80eUO-g_Njmuq1Hu",
        "Authorization": f"Bearer {access_token}"
    }
    url = f"https://yqolkvmrfvumpwlxjimp.supabase.co/rest/v1/users?id=eq.{user_id}&select=*"
    
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            profiles = res.json()
            if profiles:
                p = profiles[0]
                if p.get("role"):
                    # Keep manually entered office_name if it exists in the old profile
                    old_office_name = data.get("profile", {}).get("office_name")
                    data["profile"] = p
                    if old_office_name and not data["profile"].get("office_name"):
                        data["profile"]["office_name"] = old_office_name
                    with open(p_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    return data["profile"]
                else:
                    # Unapproved
                    return "unapproved"
    except Exception:
        pass
        
    # 2. Access token failed or expired. Try to refresh
    refresh_url = "https://yqolkvmrfvumpwlxjimp.supabase.co/auth/v1/token?grant_type=refresh_token"
    refresh_headers = {
        "apikey": "sb_publishable_Y3waCN-Y0LA26BC80eUO-g_Njmuq1Hu",
        "Content-Type": "application/json"
    }
    refresh_body = {"refresh_token": refresh_token}
    
    try:
        r_res = requests.post(refresh_url, headers=refresh_headers, json=refresh_body)
        if r_res.status_code == 200:
            r_data = r_res.json()
            new_access_token = r_data.get("access_token")
            new_refresh_token = r_data.get("refresh_token")
            new_user_id = r_data.get("user", {}).get("id")
            
            if new_access_token and new_refresh_token and new_user_id:
                # Fetch profile with new access token
                headers["Authorization"] = f"Bearer {new_access_token}"
                url = f"https://yqolkvmrfvumpwlxjimp.supabase.co/rest/v1/users?id=eq.{new_user_id}&select=*"
                res = requests.get(url, headers=headers)
                if res.status_code == 200:
                    profiles = res.json()
                    if profiles:
                        p = profiles[0]
                        if p.get("role"):
                            # Keep manually entered office_name if it exists in the old profile
                            old_office_name = data.get("profile", {}).get("office_name")
                            new_data = {
                                "profile": p,
                                "token": {
                                    "access_token": new_access_token,
                                    "refresh_token": new_refresh_token,
                                    "user_id": new_user_id
                                }
                            }
                            if old_office_name and not new_data["profile"].get("office_name"):
                                new_data["profile"]["office_name"] = old_office_name
                            with open(p_path, 'w', encoding='utf-8') as f:
                                json.dump(new_data, f, ensure_ascii=False, indent=2)
                            return new_data["profile"]
                        else:
                            return "unapproved"
    except Exception:
        pass
        
    return None

def perform_login_flow():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    import requests
    import time
    
    print("\n[안내] 크롬 창이 열립니다. 중개수첩 로그인 페이지에서 로그인을 완료해 주세요.")
    print("      (※ 중개수첩의 아이디(ID)는 회원가입 시 등록하신 '이메일 주소'입니다.)")
    print("      로그인이 정상 완료되면 자동으로 정보를 동기화하고 창을 닫습니다.")
    print("      ※ 로그인 연동 시 혜택: 생성되는 모든 보고서(시세브리핑 등) 하단에")
    print("        본인의 중개사무소 정보(상호, 대표자명, 연락처 등)가 자동으로 기입 및 서명되어")
    print("        더욱 전문적인 보고서를 만드실 수 있습니다.")
    
    options = Options()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)
    
    LOGIN_URL = "https://www.xn--h49ay03b72eh1d.kr/login.html"
    driver.get(LOGIN_URL)
    
    profile = None
    try:
        while True:
            try:
                current_url = driver.current_url.lower()
                if any(x in current_url for x in ["index.html", "deal-register.html", "dashboard"]):
                    time.sleep(1.0)
                    token_str = driver.execute_script("return localStorage.getItem('sb-yqolkvmrfvumpwlxjimp-auth-token')")
                    if token_str:
                        token_data = json.loads(token_str)
                        access_token = token_data.get("access_token")
                        refresh_token = token_data.get("refresh_token")
                        user_id = token_data.get("user", {}).get("id")
                        
                        if access_token and refresh_token and user_id:
                            headers = {
                                "apikey": "sb_publishable_Y3waCN-Y0LA26BC80eUO-g_Njmuq1Hu",
                                "Authorization": f"Bearer {access_token}"
                            }
                            url = f"https://yqolkvmrfvumpwlxjimp.supabase.co/rest/v1/users?id=eq.{user_id}&select=*"
                            res = requests.get(url, headers=headers)
                            if res.status_code == 200:
                                profiles = res.json()
                                if profiles:
                                    p = profiles[0]
                                    if not p.get("role"):
                                        print("\n[알림] 아직 승인되지 않은 회원 계정입니다.")
                                        print("      관리자 승인이 완료된 후 정보 연동이 가능합니다.")
                                        time.sleep(3)
                                        break
                                    
                                    p_path = _get_member_file_path()
                                    save_data = {
                                        "profile": p,
                                        "token": {
                                            "access_token": access_token,
                                            "refresh_token": refresh_token,
                                            "user_id": user_id
                                        }
                                    }
                                    with open(p_path, 'w', encoding='utf-8') as f:
                                        json.dump(save_data, f, ensure_ascii=False, indent=2)
                                    profile = p
                                    print(f"\n[성공] {p.get('name', '')} 공인중개사님 로그인 및 정보 연동 완료!")
                                    break
            except Exception:
                pass
            
            try:
                _ = driver.title
            except:
                print("\n[알림] 로그인 창이 닫혔거나 작업이 중단되었습니다.")
                break
                
            time.sleep(1)
    finally:
        try:
            driver.quit()
        except:
            pass
            
    return profile

def perform_register_flow():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    import time
    
    print("\n[안내] 크롬 창이 열립니다. 회원가입 페이지에서 신청서를 작성해 주세요.")
    print("      가입 완료 후 관리자 승인이 나면 로그인 및 정보 연동을 하실 수 있습니다.")
    
    options = Options()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)
    
    REGISTER_URL = "https://www.xn--h49ay03b72eh1d.kr/register.html"
    driver.get(REGISTER_URL)
    
    print("가입 완료 후 브라우저 창을 닫아주세요.")
    while True:
        try:
            _ = driver.title
        except:
            break
        time.sleep(1)

def handle_startup_auth(in_trial):
    print("\n[인증] 중개수첩 회원 상태를 확인하고 있습니다...")
    bg_result = attempt_background_sync()
    
    if isinstance(bg_result, dict):
        if "name" in bg_result and "|" in bg_result["name"]:
            parts = bg_result["name"].split("|")
            bg_result["name"] = parts[0].strip()
            bg_result["office_name"] = parts[1].strip()
        print(f"\n[인증 완료] 중개수첩 회원({bg_result.get('name', '')})으로 백그라운드 자동 연동되었습니다.")
        return bg_result
    elif bg_result == "unapproved":
        print("\n[알림] 아직 승인되지 않은 회원 계정입니다.")
        print("      관리자 승인이 완료된 후 정보 연동이 가능합니다.")
        input("\n엔터를 누르면 메뉴 선택으로 진행합니다...")
        
    member_path = _get_member_file_path()
    member = None
    if os.path.exists(member_path):
        try:
            with open(member_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    member = data.get("profile", data)
                    if member and isinstance(member, dict) and "name" in member and "|" in member["name"]:
                        parts = member["name"].split("|")
                        member["name"] = parts[0].strip()
                        member["office_name"] = parts[1].strip()
        except:
            pass
            
    while True:
        print("\n" + "="*50)
        print(" [ 중개수첩 회원 인증 및 정보 연동 ]")
        if member:
            print(f" 현재 로그인된 계정: {member.get('name', '')} 공인중개사")
            print(f" 연동 정보: {member.get('office_address', '')} | {member.get('phone', '')}")
            print("-" * 50)
            print(" 1. 로그인 정보 유지하고 자동화 메뉴로 이동")
            print(" 2. 다른 계정으로 로그인 (정보 새로 연동)")
            print(" 3. 회원 로그아웃 (비회원/체험 모드로 전환)")
        else:
            print(" 현재 비회원 / 체험 모드로 설정되어 있습니다.")
            print(" ※ 로그인 연동 시 혜택: 생성되는 모든 보고서(시세브리핑, 종합분석 등)에")
            print("   내 중개사무소 정보(상호, 대표자명, 연락처 등)가 자동으로 반영 및 서명됩니다.")
            print("-" * 50)
            print(" 1. 중개수첩 로그인 및 내 정보 연동 (추천)")
            print(" 2. 중개수첩 회원가입하러 가기")
            if in_trial:
                print(" 3. 비회원 무료 체험 바로 시작하기")
            else:
                print(" 3. 종료")
        print("="*50)
        
        choice = input("[입력] 원하시는 작업의 번호를 입력하세요: ").strip()
        
        if member:
            if choice == '1':
                print("\n[알림] 연동된 회원 정보로 보고서 서명이 자동 작성됩니다.")
                return member
            elif choice == '2':
                new_member = perform_login_flow()
                if new_member:
                    member = new_member
            elif choice == '3':
                if os.path.exists(member_path):
                    try:
                        os.remove(member_path)
                    except:
                        pass
                print("\n[알림] 로그아웃되었습니다. 비회원 상태로 시작합니다.")
                member = None
            else:
                print("잘못된 입력입니다.")
        else:
            if choice == '1':
                new_member = perform_login_flow()
                if new_member:
                    member = new_member
            elif choice == '2':
                perform_register_flow()
            elif choice == '3':
                if in_trial:
                    print("\n[알림] 비회원 무료체험 모드로 시작합니다. (보고서는 기본 정보로 생성)")
                    return None
                else:
                    print("프로그램을 종료합니다.")
                    sys.exit(0)
            else:
                print("잘못된 입력입니다.")

def _generate_signature(start_date_str):
    import hashlib
    TRIAL_SALT = "korealtor_secure_salt_2026"
    raw_str = f"{start_date_str}_{TRIAL_SALT}"
    return hashlib.sha256(raw_str.encode('utf-8')).hexdigest()

def _get_registry_date(reg_name):
    import winreg
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\{reg_name}")
        val, _ = winreg.QueryValueEx(key, "TrialStart")
        return val
    except Exception:
        return None

def _set_registry_date(reg_name, date_str):
    import winreg
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\{reg_name}")
        winreg.SetValueEx(key, "TrialStart", 0, winreg.REG_SZ, date_str)
    except Exception:
        pass

def check_trial():
    trial_path = _get_trial_file_path()
    reg_name = "Korealtor"
    
    # 1. Read Registry
    reg_date_str = _get_registry_date(reg_name)
    
    # 2. Read File
    file_date_str = None
    file_sig = None
    file_exists = os.path.exists(trial_path)
    
    if file_exists:
        try:
            with open(trial_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            file_date_str = data.get("start")
            file_sig = data.get("signature")
        except Exception:
            file_exists = False

    # 3. Check for modification / mismatch
    if file_exists and file_date_str:
        # Validate signature
        expected_sig = _generate_signature(file_date_str)
        if file_sig != expected_sig:
            print("\n[보안 알림] 시스템 파일 조작이 감지되었습니다. 사용이 제한됩니다.")
            print(f"   계속 사용하시려면 아래 연락처로 문의해 주세요.")
            print(f"   담당자 : {CONTACT_NAME}  |  전화 : {CONTACT_PHONE}")
            return False
            
        # Compare with Registry
        if reg_date_str and reg_date_str != file_date_str:
            print("\n[보안 알림] 비정상적인 사용 기간 변경이 감지되었습니다. 사용이 제한됩니다.")
            print(f"   계속 사용하시려면 아래 연락처로 문의해 주세요.")
            print(f"   담당자 : {CONTACT_NAME}  |  전화 : {CONTACT_PHONE}")
            return False

    # 4. Handle Missing States (Self-healing & Initial setup)
    if not file_exists and not reg_date_str:
        # First execution ever
        start_date = date.today()
        start_str = start_date.isoformat()
        sig = _generate_signature(start_str)
        try:
            with open(trial_path, 'w', encoding='utf-8') as f:
                json.dump({"start": start_str, "signature": sig}, f)
        except Exception:
            pass
        _set_registry_date(reg_name, start_str)
        print(f"\n[무료체험] 오늘({start_date})부터 {TRIAL_MONTHS}개월 무료 체험이 시작됩니다!")
        start_val = start_date
    elif not file_exists and reg_date_str:
        # Local file deleted, restore from registry
        start_str = reg_date_str
        sig = _generate_signature(start_str)
        try:
            with open(trial_path, 'w', encoding='utf-8') as f:
                json.dump({"start": start_str, "signature": sig}, f)
        except Exception:
            pass
        start_val = date.fromisoformat(start_str)
    elif file_exists and not reg_date_str:
        # Registry cleared/missing, restore from file
        start_str = file_date_str
        _set_registry_date(reg_name, start_str)
        start_val = date.fromisoformat(start_str)
    else:
        # Both exist and match
        start_val = date.fromisoformat(file_date_str)
        
    # 5. Check expiration
    expiry_date = start_val + relativedelta(months=TRIAL_MONTHS)
    today = date.today()
    days_left = (expiry_date - today).days

    if today < expiry_date:
        print(f"\n[무료체험] 체험 기간 중입니다. (시작: {start_val} / 만료: {expiry_date} / 남은일: {days_left}일)")
        return True
    else:
        print(f"\n[체험 만료] 무료 체험 기간이 종료되었습니다. (만료일: {expiry_date})")
        print(f"   계속 사용하시려면 아래 연락처로 문의해 주세요.")
        print(f"   담당자 : {CONTACT_NAME}  |  전화 : {CONTACT_PHONE}")
        print(f"   후원계좌: {SPONSOR_BANK} {SPONSOR_ACCOUNT} ({CONTACT_NAME})")
        return False

def run_launcher():
    print("=" * 54)
    print("   안티그래비티 통합 봇 런처 (배포용 260707)")
    print("   매물광고 자동 등록 / 대량 검증 프로그램")
    print("=" * 54)
    print(f"   개발·문의 : {CONTACT_NAME}  {CONTACT_PHONE}")
    print(f"   후원계좌  : {SPONSOR_BANK} {SPONSOR_ACCOUNT} ({CONTACT_NAME})")
    print("=" * 54)

    # ── 3개월 무료 체험 검증 ──────────────────────────────
    in_trial = check_trial()
    # ──────────────────────────────────────────────────────

    # ── 중개수첩 회원 인증 및 정보 연동 ──
    member = handle_startup_auth(in_trial)
    if not member and not in_trial:
        print("\n[안내] 무료 체험 기간이 만료되었습니다.")
        print("      본 프로그램을 사용하시려면 로그인하여 정보를 연동해 주세요.")
        input("\n엔터를 누르면 프로그램을 종료합니다...")
        sys.exit(0)

    print("\n[!!] [필독] 법적 고지 및 면책 조항 (공공데이터 오류 주의) [!!]")
    print("1. 본 봇이 자동으로 가져오는 데이터는 '정부 공공데이터 API'에 의존합니다.")
    print("   하지만 이 정부 API 데이터 자체가 실제 발급받은 공문서(PDF)와 다를 수 있습니다.")
    print("   [실제 적발 사례] 마포구 성산동의 한 주택은 실제 대장(갑)에는 노란색으로")
    print("   '위반건축물' 표기가 선명하지만, 정부 API는 이를 '위반 아님(N)'으로 잘못 내려주었습니다.")
    print("   만약 이를 확인하지 않고 매물을 등록/중개할 경우 표시광고 위반 및 중개대상물 확인·설명서")
    print("   기재 누락으로 인해 **'과태료 부과 사유'**가 될 수 있습니다.")
    print("2. 따라서 본 프로그램을 사용하여 발생한 매물 등록 오류, 위반건축물 미고지 사고 등")
    print("   어떠한 형태의 불이익에 대해서도 **개발자 및 배포자는 일체의 법적 책임을 지지 않습니다.**")
    print("3. 자동화 봇은 단순 '입력 보조 도구'일 뿐입니다. 매물 등록 및 계약 전, 반드시 중개사님께서 직접")
    print("   **정부24에서 실제 공부(건축물대장 등)를 발급받아 눈으로 직접 대조 및 교차 검증**하시기 바랍니다.")
    print("=================================================================\n")
    
    print("[참고] 프로그램 권장 사용 대상")
    print(" - 본 봇은 **'다세대, 다가구, 빌라, 단독주택'** 등 입력 항목이 복잡하고")
    print("   손이 많이 가는 매물 등록에 최적화되어 있습니다.")
    print(" - 아파트의 경우 기본적으로 입력할 항목이 적어 자동화의 체감이 크지 않을 수 있습니다.")
    print("--------------------------------------------------\n")
    
    # 통합 메뉴 제공
    while True:
        print("\n" + "="*50)
        print(" [ 자동화 메뉴판 ] ")
        print(" 1. LH 전세임대포털 매물 자동 등록 (로그인 필요)")
        print(" 2. 부동산써브 매물 자동 등록 (로그인 필요)")
        print(" 3. 부동산써브 매물 대량 검증 (로그인 필요)")
        print(" 4. 부동산 통합 조회 (대장 + 실거래가 비교)")
        print(" 5. 중개수첩 로그인 및 정보연동 관리")
        print(" 6. 동네별 부동산 시장 동향 분석")
        print(" 7. 부동산써브 등록 매물 A4 광고 전단지 인쇄 (로그인 필요)")
        print(" 0. 프로그램 종료")
        print("="*50)
        
        choice = input("[입력] 원하시는 작업의 번호를 입력하세요: ")
        
        if choice in ['1', '2', '3', '7']:
            # ── 인증 로직 ──
            auth_ok = False

            # member_info.json 확인
            m_path = _get_member_file_path()
            m_info = None
            if os.path.exists(m_path):
                try:
                    with open(m_path, 'r', encoding='utf-8') as f:
                        m_info = json.load(f)
                except:
                    pass
            
            if m_info and (m_info.get("profile", {}).get("role") or m_info.get("role")):
                p_info = m_info.get("profile", m_info)
                print(f"\n[인증 완료] 중개수첩 회원({p_info.get('name', '')})으로 자동 인증되었습니다.")
                auth_ok = True
            elif in_trial:
                print("\n[무료체험] 체험 기간 중이므로 중개수첩 로그인을 생략합니다.")
                auth_ok = True
            else:
                # Fallback
                new_member = perform_login_flow()
                if new_member and new_member.get("role"):
                    auth_ok = True
                else:
                    print("\n[인증 실패] 승인된 중개수첩 계정으로 로그인해야 작동합니다.")
                    input("엔터를 누르면 메뉴로 돌아갑니다...")
                    continue

            try:
                if choice == '1':
                    print("\n>> 'LH 자동 등록'으로 화면을 이동합니다...")
                    run_lh_auto_upload()
                elif choice == '2':
                    print("\n>> '부동산써브 자동 등록'으로 화면을 이동합니다...")
                    if serve_auto_upload._kept_alive_driver is not None:
                        try:
                            _ = serve_auto_upload._kept_alive_driver.current_url
                            print(" -> 기존에 열린 써브 브라우저를 재사용합니다! (로그인 유지됨)")
                        except Exception:
                            serve_auto_upload._kept_alive_driver = None
                    run_serve_auto_upload()
                elif choice == '3':
                    print("\n>> '부동산써브 대량 검증'으로 화면을 이동합니다...")
                    run_audit_serve_list()
                elif choice == '7':
                    print("\n>> '부동산써브 등록 매물 A4 광고 전단지 인쇄'로 화면을 이동합니다...")
                    if serve_auto_upload._kept_alive_driver is not None:
                        try:
                            _ = serve_auto_upload._kept_alive_driver.current_url
                            print(" -> 기존에 열린 써브 브라우저를 재사용합니다! (로그인 유지됨)")
                        except Exception:
                            serve_auto_upload._kept_alive_driver = None
                    from serve_print_flyer import run_serve_print_flyer
                    run_serve_print_flyer()
            except Exception as e:
                print("\n" + "="*50)
                print("[오류] 작업 중 문제가 발생했습니다.")
                print(f"내용: {str(e).split('Stacktrace:')[0].strip()}")
                print("메뉴로 돌아갑니다...")
                print("="*50)
                input("확인 후 엔터를 누르세요...")
                
        elif choice == '4':
            try:
                run_building_viewer()
            except Exception as e:
                print("\n" + "="*50)
                print("[오류] 부동산 통합 조회 중 문제가 발생했습니다.")
                print(f"내용: {e}")
                print("메뉴로 돌아갑니다...")
                print("="*50)
                input("확인 후 엔터를 누르세요...")

        elif choice == '5':
            member = handle_startup_auth(in_trial)
            if not member and not in_trial:
                print("\n[안내] 무료 체험 기간이 만료되었습니다. 프로그램을 종료합니다.")
                sys.exit(0)
                
        elif choice == '6':
            try:
                run_market_analysis()
            except Exception as e:
                print("\n" + "="*50)
                print("[오류] 동향 분석 중 문제가 발생했습니다.")
                print(f"내용: {e}")
                print("메뉴로 돌아갑니다...")
                print("="*50)
                input("확인 후 엔터를 누르세요...")

        elif choice == '0':
            print("프로그램을 종료합니다.")
            sys.exit(0)
            
        else:
            print("잘못된 입력입니다. 다시 선택해주세요.")

if __name__ == "__main__":
    try:
        run_launcher()
    except KeyboardInterrupt:
        print("\n\n[종료] 사용자가 프로그램을 중단했습니다.")
    except Exception as e:
        print("\n" + "="*50)
        print("[치명적 오류] 프로그램 실행 중 예상치 못한 오류가 발생했습니다.")
        print(f"오류 내용: {e}")
        print("="*50)
    finally:
        input("\n프로그램을 종료하려면 엔터를 누르세요...")
