-- ==============================================================================
-- [긴급 보안 권한(RLS) 해제 복구 스크립트]
-- 테이블에 보안(RLS)이 켜져서 데이터가 안 보이는 현상을 해결합니다.
-- ==============================================================================

DO $$
DECLARE
    tbl_name text;
BEGIN
    FOR tbl_name IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
    LOOP
        -- 각 테이블마다 모든 사용자가 접근할 수 있도록 임시 허용 정책(Policy) 생성
        EXECUTE format('DROP POLICY IF EXISTS "Allow all operations" ON public.%I;', tbl_name);
        EXECUTE format('CREATE POLICY "Allow all operations" ON public.%I FOR ALL USING (true) WITH CHECK (true);', tbl_name);
    END LOOP;
END
$$;

NOTIFY pgrst, 'reload schema';
