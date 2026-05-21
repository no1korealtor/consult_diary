-- ==============================================================================
-- [긴급 복구] 암호화 롤백 스크립트
-- ==============================================================================

-- 1. 매물 장부(properties) 복구
DROP TRIGGER IF EXISTS properties_insert ON public.properties;
DROP TRIGGER IF EXISTS properties_update ON public.properties;
DROP FUNCTION IF EXISTS properties_insert_trigger();
DROP FUNCTION IF EXISTS properties_update_trigger();

DROP VIEW IF EXISTS public.properties;

-- 데이터 원상 복구 (복호화)
UPDATE public.properties_raw 
SET 
    address = decrypt_data(address),
    owner_phone = decrypt_data(owner_phone),
    tenant_phone = decrypt_data(tenant_phone)
WHERE address LIKE 'LS0%' OR owner_phone LIKE 'LS0%' OR tenant_phone LIKE 'LS0%'; 
-- (pgp_sym_encrypt 출력은 base64이므로 다를 수 있지만, decrypt_data는 원본이거나 암호문이면 복호화합니다)
-- 좀 더 안전하게 모든 행을 복호화:
UPDATE public.properties_raw 
SET 
    address = decrypt_data(address),
    owner_phone = decrypt_data(owner_phone),
    tenant_phone = decrypt_data(tenant_phone);

ALTER TABLE public.properties_raw RENAME TO properties;


-- 2. 고객 장부(client_requests) 복구
DROP TRIGGER IF EXISTS client_requests_insert ON public.client_requests;
DROP TRIGGER IF EXISTS client_requests_update ON public.client_requests;
DROP FUNCTION IF EXISTS client_requests_insert_trigger();
DROP FUNCTION IF EXISTS client_requests_update_trigger();

DROP VIEW IF EXISTS public.client_requests;

UPDATE public.client_requests_raw 
SET client_phone = decrypt_data(client_phone);

ALTER TABLE public.client_requests_raw RENAME TO client_requests;

-- 3. 스키마 캐시 새로고침 (Supabase/PostgREST용)
NOTIFY pgrst, 'reload schema';
