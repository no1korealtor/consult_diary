-- ==============================================================================
-- [데이터베이스 자동 암호화 및 권한별 마스킹 적용 스크립트]
-- 이 코드를 Supabase SQL Editor에 복사하고 RUN 하세요.
-- ==============================================================================

-- 1. 암호화 모듈 활성화
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 2. 안전한 암호화/복호화 함수 생성 (비밀키: 'my_secret_key_2026' - 원하시면 변경하세요)
CREATE OR REPLACE FUNCTION encrypt_data(data TEXT) RETURNS TEXT AS $$
BEGIN
    IF data IS NULL THEN RETURN NULL; END IF;
    RETURN encode(pgp_sym_encrypt(data, 'my_secret_key_2026'), 'base64');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION decrypt_data(data TEXT) RETURNS TEXT AS $$
BEGIN
    IF data IS NULL THEN RETURN NULL; END IF;
    RETURN pgp_sym_decrypt(decode(data, 'base64'), 'my_secret_key_2026');
EXCEPTION WHEN OTHERS THEN
    RETURN data; -- 이미 복호화된 데이터나 구형 데이터면 그대로 반환
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. 마스킹 함수 생성 (권한 체크 포함)
CREATE OR REPLACE FUNCTION get_masked_phone(phone_text TEXT) RETURNS TEXT AS $$
DECLARE
    user_role TEXT;
BEGIN
    IF phone_text IS NULL THEN RETURN NULL; END IF;
    
    -- 현재 로그인한 사용자의 롤을 가져옴 (users 테이블 확인)
    SELECT role INTO user_role FROM public.users WHERE id = auth.uid();
    
    -- 대표자(admin)면 마스킹 없이 원본 반환
    IF user_role = 'admin' THEN
        RETURN phone_text;
    END IF;
    
    -- 직원이면 가운데 자리 마스킹 처리 (010-****-1234)
    -- 하이픈이 있는 경우와 없는 경우 모두 처리
    IF phone_text LIKE '%-%-%' THEN
        RETURN regexp_replace(phone_text, '(?<=\d{2,3}-)\d{3,4}(?=-\d{4})', '****');
    ELSE
        IF length(phone_text) >= 10 THEN
            RETURN substr(phone_text, 1, 3) || '-****-' || substr(phone_text, length(phone_text)-3);
        END IF;
    END IF;
    
    RETURN '***-****-****';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION get_masked_address(address_text TEXT) RETURNS TEXT AS $$
DECLARE
    user_role TEXT;
BEGIN
    IF address_text IS NULL THEN RETURN NULL; END IF;
    
    SELECT role INTO user_role FROM public.users WHERE id = auth.uid();
    
    IF user_role = 'admin' THEN
        RETURN address_text;
    END IF;
    
    -- 직원이면 상세 동/호수를 ***로 가림
    RETURN regexp_replace(address_text, '\d+동|\d+호', '***', 'g');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ==============================================================================
-- 매물 장부 (properties) 암호화 마이그레이션
-- ==============================================================================

-- 기존 테이블을 _raw 로 이름 변경
ALTER TABLE IF EXISTS public.properties RENAME TO properties_raw;

-- 기존 데이터 암호화 (이미 암호화된 건 제외)
UPDATE public.properties_raw 
SET 
    address = encrypt_data(address),
    owner_phone = encrypt_data(owner_phone),
    tenant_phone = encrypt_data(tenant_phone)
WHERE address NOT LIKE 'LS0%' AND address IS NOT NULL AND length(address) < 100;

-- 거울(View) 생성
CREATE OR REPLACE VIEW public.properties AS
SELECT 
    id, user_id, building_id, room_id,
    get_masked_address(decrypt_data(address)) AS address,
    deal_types, sale_price, deposit, monthly_rent, area_m2, area_py, land_share_m2, land_share_py,
    room_count, occupancy_type, occupancy_date, pet_allowed, parking_allowed, parking_fee, 
    loan_allowed, lh_sh_allowed, is_basement,
    get_masked_phone(decrypt_data(owner_phone)) AS owner_phone,
    get_masked_phone(decrypt_data(tenant_phone)) AS tenant_phone,
    status, memo, created_at, updated_at
FROM public.properties_raw;

-- 데이터를 저장할 때 자동으로 암호화하여 저장하게 하는 트리거
CREATE OR REPLACE FUNCTION properties_insert_trigger()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.properties_raw (
        id, user_id, building_id, room_id, address, deal_types, sale_price, deposit, monthly_rent,
        area_m2, area_py, land_share_m2, land_share_py, room_count, occupancy_type, occupancy_date,
        pet_allowed, parking_allowed, parking_fee, loan_allowed, lh_sh_allowed, is_basement,
        owner_phone, tenant_phone, status, memo
    ) VALUES (
        COALESCE(NEW.id, uuid_generate_v4()), NEW.user_id, NEW.building_id, NEW.room_id, 
        encrypt_data(NEW.address), NEW.deal_types, NEW.sale_price, NEW.deposit, NEW.monthly_rent,
        NEW.area_m2, NEW.area_py, NEW.land_share_m2, NEW.land_share_py, NEW.room_count, NEW.occupancy_type, NEW.occupancy_date,
        NEW.pet_allowed, NEW.parking_allowed, NEW.parking_fee, NEW.loan_allowed, NEW.lh_sh_allowed, NEW.is_basement,
        encrypt_data(NEW.owner_phone), encrypt_data(NEW.tenant_phone), NEW.status, NEW.memo
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER properties_insert
INSTEAD OF INSERT ON public.properties
FOR EACH ROW EXECUTE FUNCTION properties_insert_trigger();

CREATE OR REPLACE FUNCTION properties_update_trigger()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE public.properties_raw SET
        building_id = NEW.building_id, room_id = NEW.room_id, 
        address = CASE WHEN NEW.address = OLD.address THEN address ELSE encrypt_data(NEW.address) END,
        deal_types = NEW.deal_types, sale_price = NEW.sale_price, deposit = NEW.deposit, monthly_rent = NEW.monthly_rent,
        area_m2 = NEW.area_m2, area_py = NEW.area_py, land_share_m2 = NEW.land_share_m2, land_share_py = NEW.land_share_py,
        room_count = NEW.room_count, occupancy_type = NEW.occupancy_type, occupancy_date = NEW.occupancy_date,
        pet_allowed = NEW.pet_allowed, parking_allowed = NEW.parking_allowed, parking_fee = NEW.parking_fee, 
        loan_allowed = NEW.loan_allowed, lh_sh_allowed = NEW.lh_sh_allowed, is_basement = NEW.is_basement,
        owner_phone = CASE WHEN NEW.owner_phone = OLD.owner_phone THEN owner_phone ELSE encrypt_data(NEW.owner_phone) END,
        tenant_phone = CASE WHEN NEW.tenant_phone = OLD.tenant_phone THEN tenant_phone ELSE encrypt_data(NEW.tenant_phone) END,
        status = NEW.status, memo = NEW.memo, updated_at = NOW()
    WHERE id = NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER properties_update
INSTEAD OF UPDATE ON public.properties
FOR EACH ROW EXECUTE FUNCTION properties_update_trigger();

-- ==============================================================================
-- 고객 장부 (client_requests) 암호화 마이그레이션
-- ==============================================================================

ALTER TABLE IF EXISTS public.client_requests RENAME TO client_requests_raw;

UPDATE public.client_requests_raw 
SET client_phone = encrypt_data(client_phone)
WHERE client_phone IS NOT NULL AND length(client_phone) < 100;

CREATE OR REPLACE VIEW public.client_requests AS
SELECT 
    id, user_id, client_name,
    get_masked_phone(decrypt_data(client_phone)) AS client_phone,
    target_types, max_budget, max_monthly, occupancy_type, occupancy_date, occupancy_period_memo,
    min_room_count, need_pet, need_parking, need_loan, need_lh_sh, need_exclude_basement,
    status, memo, viewed_properties, created_at, updated_at
FROM public.client_requests_raw;

CREATE OR REPLACE FUNCTION client_requests_insert_trigger()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.client_requests_raw (
        id, user_id, client_name, client_phone, target_types, max_budget, max_monthly, 
        occupancy_type, occupancy_date, occupancy_period_memo, min_room_count, need_pet, 
        need_parking, need_loan, need_lh_sh, need_exclude_basement, status, memo, viewed_properties
    ) VALUES (
        COALESCE(NEW.id, uuid_generate_v4()), NEW.user_id, NEW.client_name, encrypt_data(NEW.client_phone), 
        NEW.target_types, NEW.max_budget, NEW.max_monthly, NEW.occupancy_type, NEW.occupancy_date, NEW.occupancy_period_memo, 
        NEW.min_room_count, NEW.need_pet, NEW.need_parking, NEW.need_loan, NEW.need_lh_sh, NEW.need_exclude_basement, 
        NEW.status, NEW.memo, NEW.viewed_properties
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER client_requests_insert
INSTEAD OF INSERT ON public.client_requests
FOR EACH ROW EXECUTE FUNCTION client_requests_insert_trigger();

CREATE OR REPLACE FUNCTION client_requests_update_trigger()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE public.client_requests_raw SET
        client_name = NEW.client_name,
        client_phone = CASE WHEN NEW.client_phone = OLD.client_phone THEN client_phone ELSE encrypt_data(NEW.client_phone) END,
        target_types = NEW.target_types, max_budget = NEW.max_budget, max_monthly = NEW.max_monthly,
        occupancy_type = NEW.occupancy_type, occupancy_date = NEW.occupancy_date, occupancy_period_memo = NEW.occupancy_period_memo,
        min_room_count = NEW.min_room_count, need_pet = NEW.need_pet, need_parking = NEW.need_parking, 
        need_loan = NEW.need_loan, need_lh_sh = NEW.need_lh_sh, need_exclude_basement = NEW.need_exclude_basement,
        status = NEW.status, memo = NEW.memo, viewed_properties = NEW.viewed_properties, updated_at = NOW()
    WHERE id = NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER client_requests_update
INSTEAD OF UPDATE ON public.client_requests
FOR EACH ROW EXECUTE FUNCTION client_requests_update_trigger();

-- 완료
