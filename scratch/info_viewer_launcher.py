import os
import sys
import json
import re
from datetime import date
from dateutil.relativedelta import relativedelta

# Import our unified viewer function
from building_viewer import run_building_viewer

# Windows 한글 인코딩 깨짐 방지 및 터미널 인코딩 설정
if sys.platform == 'win32':
    try:
        sys.stdin.reconfigure(encoding='utf-8', errors='replace')
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# ─── 배포 정보 ───────────────────────────────────────────
CONTACT_NAME    = "조항준"
CONTACT_PHONE   = "010-9128-0586"
SPONSOR_BANK    = "신한은행"
SPONSOR_ACCOUNT = "218-12-036791"
TRIAL_MONTHS    = 1          # 1개월 무료 체험 기간
TRIAL_FILE_NAME = "info_trial_start.json"
# ─────────────────────────────────────────────────────────

def _get_trial_file_path():
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, TRIAL_FILE_NAME)

def _generate_signature(start_date_str):
    import hashlib
    TRIAL_SALT = "korealtor_viewer_secure_salt_2026"
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
    reg_name = "KorealtorViewer"
    
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
    print("   부동산 정보 간편 조회기 (배포용 260707)")
    print("   건축물대장 열람 / 실거래가(매매·전월세) 비교")
    print("=" * 54)
    print(f"   개발·문의 : {CONTACT_NAME}  {CONTACT_PHONE}")
    print(f"   후원계좌  : {SPONSOR_BANK} {SPONSOR_ACCOUNT} ({CONTACT_NAME})")
    print("=" * 54)

    in_trial = check_trial()
    if not in_trial:
        input("\n종료하려면 엔터를 누르세요...")
        sys.exit(0)

    print("\n[!!] [필독] 법적 고지 및 면책 조항 (공공데이터 오류 주의) [!!]")
    print("1. 본 프로그램이 자동으로 가져오는 데이터는 '정부 공공데이터 API'에 의존합니다.")
    print("   이 데이터는 실제 발급받은 공문서(PDF)와 간혹 다를 수 있으므로 참고용으로만 사용하시기 바랍니다.")
    print("2. 따라서 본 프로그램을 사용하여 발생한 정보 오류, 사고 등 어떠한 형태의 불이익에 대해서도")
    print("   **개발자 및 배포자는 일체의 법적 책임을 지지 않습니다.**")
    print("3. 매물 계약 전에는 반드시 정부24에서 실제 대장을 발급받아 교차 검증하시기 바랍니다.")
    print("=================================================================\n")

    try:
        run_building_viewer()
    except KeyboardInterrupt:
        print("\n\n[종료] 사용자가 프로그램을 중단했습니다.")
    except Exception as e:
        print("\n" + "="*50)
        print(f"[시스템오류] {e}")
        input("종료하려면 엔터를 누르세요...")

if __name__ == "__main__":
    run_launcher()
