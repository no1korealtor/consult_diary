-- 1. users 테이블에 중개등록번호(registration_number) 컬럼 추가
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS registration_number text;

-- 2. 설명
-- 이 SQL 스크립트를 Supabase 대시보드의 SQL Editor에 붙여넣고 실행(Run)해 주세요.
-- 컬럼 추가 후 '내 정보' 및 '회원가입'에서 등록번호 입력이 정상적으로 데이터베이스에 저장됩니다.
