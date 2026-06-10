-- 1. study_logs 테이블에 사용자 구분을 위한 creator 필드 추가 (없는 경우)
ALTER TABLE study_logs ADD COLUMN IF NOT EXISTS creator text;

-- 2. study_logs 테이블의 RLS(행 수준 보안) 정책 초기화 및 허용
-- RLS 활성화
ALTER TABLE study_logs ENABLE ROW LEVEL SECURITY;

-- 기존 정책이 있다면 삭제 (충돌 방지)
DROP POLICY IF EXISTS "Allow anonymous inserts" ON study_logs;
DROP POLICY IF EXISTS "Allow anonymous selects" ON study_logs;

-- 누구나(익명 사용자 포함) 데이터를 추가할 수 있도록 허용 (학습 기록 저장용)
CREATE POLICY "Allow anonymous inserts" ON study_logs 
FOR INSERT TO anon 
WITH CHECK (true);

-- 누구나(익명 사용자 포함) 데이터를 볼 수 있도록 허용 (대시보드 조회용)
CREATE POLICY "Allow anonymous selects" ON study_logs 
FOR SELECT TO anon 
USING (true);
