-- 1. 새로운 사용자 배열 필드 추가
ALTER TABLE study_words ADD COLUMN memorized_users text[] DEFAULT '{}';

-- 2. 기존 암기 데이터를 '아람'의 기록으로 마이그레이션 (기존에 공부했던 것은 아람이의 진도로 처리)
UPDATE study_words 
SET memorized_users = ARRAY['아람']
WHERE is_memorized = true;

-- 3. (선택사항) 모든 마이그레이션과 앱 테스트가 끝나면 기존 컬럼을 삭제할 수 있습니다.
-- ALTER TABLE study_words DROP COLUMN is_memorized;
