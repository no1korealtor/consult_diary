-- properties (매물장) 테이블
CREATE TABLE IF NOT EXISTS properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID, -- authClient의 users.id 저장 (DB 분리로 FK 제거)
    building_id UUID REFERENCES buildings(id) ON DELETE CASCADE,
    room_id UUID REFERENCES rooms(id) ON DELETE CASCADE,
    address TEXT, -- 빠른 매물 등록을 위한 텍스트 주소/동호수
    
    -- 거래 종류 및 금액
    deal_types TEXT[] NOT NULL DEFAULT '{}', -- ['매매', '전세', '월세'] 등 다중 선택
    sale_price BIGINT,     -- 매매가 (만원)
    deposit BIGINT,        -- 보증금/전세금 (만원)
    monthly_rent BIGINT,   -- 월세 (만원)
    
    -- 면적 및 지분 (평과 ㎡ 병기)
    area_m2 NUMERIC,
    area_py NUMERIC,
    land_share_m2 NUMERIC,
    land_share_py NUMERIC,
    
    -- 구조
    room_count INTEGER,
    
    -- 입주 조건
    occupancy_type TEXT, -- '즉시입주', '날짜확정', '날짜협의', '입주불가(세안고)'
    occupancy_date DATE,
    
    -- 세부 조건
    pet_allowed BOOLEAN,
    parking_allowed BOOLEAN,
    parking_fee INTEGER, -- 주차비
    loan_allowed BOOLEAN, -- 전세대출 가능 여부
    lh_sh_allowed BOOLEAN, -- LH/SH 가능 여부
    is_basement BOOLEAN DEFAULT FALSE, -- 지층/반지하 여부
    
    -- 상태 및 메모
    status TEXT DEFAULT '거래가능', -- '거래가능', '보류', '거래완료'
    memo TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- client_requests (손님 조건 장부) 테이블
CREATE TABLE IF NOT EXISTS client_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID, -- authClient의 users.id 저장 (DB 분리로 FK 제거)
    -- 손님 정보
    client_name TEXT NOT NULL,
    client_phone TEXT,
    
    -- 희망 거래 종류 및 예산
    target_types TEXT[] NOT NULL DEFAULT '{}', -- ['매매', '전세', '월세']
    max_budget BIGINT,     -- 최대 예산(매매가/보증금)
    max_monthly BIGINT,    -- 최대 월세
    
    -- 희망 입주 조건
    occupancy_type TEXT, -- '날짜확정', '시기조정가능(예: 7~8월)', '무관'
    occupancy_date DATE,
    occupancy_period_memo TEXT, -- 대략적인 시기 텍스트
    
    -- 필요 구조 및 조건
    min_room_count INTEGER,
    need_pet BOOLEAN DEFAULT FALSE,
    need_parking BOOLEAN DEFAULT FALSE,
    need_loan BOOLEAN DEFAULT FALSE,
    need_lh_sh BOOLEAN DEFAULT FALSE,
    need_exclude_basement BOOLEAN DEFAULT FALSE, -- 지층/반지하 제외 여부
    
    -- 상태 및 메모
    status TEXT DEFAULT '탐색중', -- '탐색중', '계약완료', '변심/종료'
    memo TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS (Row Level Security) 설정
-- 매물장과 손님장부 테이블 모두 누구나 읽고 쓸 수 있도록 허용합니다. (인증은 authClient에서 처리하므로 DB 프로젝트에서는 anon 권한 허용)
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE client_requests ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow all operations for authenticated users on properties" ON properties;
DROP POLICY IF EXISTS "Allow all operations for authenticated users on client_requests" ON client_requests;

CREATE POLICY "Allow all operations on properties" 
ON properties FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations on client_requests" 
ON client_requests FOR ALL USING (true) WITH CHECK (true);
