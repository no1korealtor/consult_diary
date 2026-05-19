-- 1. schedules (일정/할일) 테이블 생성
-- 기존의 'deals' 테이블을 대체하며, 모임, 잔금, 정산, 일반 미팅 등의 일정을 관리합니다.
CREATE TABLE IF NOT EXISTS schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID, -- 작성자 (authClient users.id)
    
    -- 연관 데이터 연결 (선택사항)
    building_id UUID REFERENCES buildings(id) ON DELETE CASCADE,
    room_id UUID REFERENCES rooms(id) ON DELETE CASCADE,
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    client_id UUID REFERENCES client_requests(id) ON DELETE CASCADE, -- 고객과 연결
    
    -- 일정 기본 정보
    schedule_type TEXT NOT NULL, -- '모임', '잔금', '정산', '미팅', '기타'
    schedule_date DATE,          -- 일정 날짜 (기존 balance_date)
    schedule_time TIME,          -- 일정 시간 (새로 추가됨)
    
    -- 장소 정보 (새로 추가됨, 기존에는 memo에 태그로 저장했음)
    location TEXT,
    location_detail TEXT,
    
    -- 링크 정보
    url TEXT,
    url_name TEXT,
    
    -- 모임/수요조사 관련 정보
    is_proposal BOOLEAN DEFAULT FALSE,
    proposal_deadline TIMESTAMP WITH TIME ZONE,
    min_attendance INTEGER,
    
    -- 상태 관리
    status TEXT DEFAULT '예정', -- '예정', '승인대기', '완료', '취소'
    cancel_reason TEXT,
    
    -- 기타 메모
    memo TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. schedule_attendances (일정/모임 참석 여부) 테이블 생성
-- 기존 'deal_attendances' 테이블을 대체합니다.
CREATE TABLE IF NOT EXISTS schedule_attendances (
    schedule_id UUID REFERENCES schedules(id) ON DELETE CASCADE,
    user_id UUID,
    status TEXT, -- '참석', '불참', '미정'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (schedule_id, user_id)
);

-- 3. RLS (Row Level Security) 설정
-- 인증은 애플리케이션 레벨(authClient)에서 처리하므로 DB 접근은 모두 허용합니다.
ALTER TABLE schedules ENABLE ROW LEVEL SECURITY;
ALTER TABLE schedule_attendances ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow all operations on schedules" ON schedules;
DROP POLICY IF EXISTS "Allow all operations on schedule_attendances" ON schedule_attendances;

CREATE POLICY "Allow all operations on schedules" 
ON schedules FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations on schedule_attendances" 
ON schedule_attendances FOR ALL USING (true) WITH CHECK (true);

-- 4. 기존 deals 테이블의 데이터를 schedules로 마이그레이션 (옵션)
-- 데이터가 많지 않다고 하셨으므로, 아래 쿼리를 실행하면 기존 deals 데이터를
-- 어느 정도 새로운 테이블로 복사해 올 수 있습니다. (메모 파싱은 복잡하여 그대로 memo에 복사됩니다)
INSERT INTO schedules (
    id, user_id, building_id, room_id, property_id, 
    schedule_type, schedule_date, memo, created_at
)
SELECT 
    id, user_id, building_id, room_id, property_id, 
    contract_type, balance_date, memo, created_at
FROM deals
ON CONFLICT (id) DO NOTHING;

INSERT INTO schedule_attendances (schedule_id, user_id, status)
SELECT deal_id, user_id, status
FROM deal_attendances
ON CONFLICT (schedule_id, user_id) DO NOTHING;
