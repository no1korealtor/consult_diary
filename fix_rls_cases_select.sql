-- cases 테이블에 대한 익명(anon) 사용자 SELECT 허용 (새로 추가)
CREATE POLICY "Allow anonymous select cases" ON public.cases FOR SELECT TO anon USING (true);
