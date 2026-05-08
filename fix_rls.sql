-- 1. 고객(customers) 테이블에 대한 익명(anon) 사용자 INSERT/SELECT 허용
CREATE POLICY "Allow anonymous insert customers" ON public.customers FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY "Allow anonymous select customers" ON public.customers FOR SELECT TO anon USING (true);

-- 2. 상담 접수(cases) 테이블에 대한 익명(anon) 사용자 INSERT/SELECT 허용
CREATE POLICY "Allow anonymous insert cases" ON public.cases FOR INSERT TO anon WITH CHECK (true);

-- 3. 로그(logs) 테이블에 대한 익명(anon) 사용자 INSERT 허용
CREATE POLICY "Allow anonymous insert logs" ON public.logs FOR INSERT TO anon WITH CHECK (true);
