// propertyMatcher.test.js
const assert = require('assert');
const { findMatchingProperties } = require('./propertyMatcher');

// --- [1단계: 테스트 데이터 준비] ---
const properties = [
  { id: 1, type: '매매', price: 40000, title: '4억 매매가' },
  { id: 2, type: '매매', price: 50000, title: '5억 매매가' },
  { id: 3, type: '매매', price: 60000, title: '6억 매매가' },
  { id: 4, type: '전세', price: 40000, title: '4억 전세가' }, // 가격은 맞지만 종류가 다름
];

// 고객의 조건: 매매를 원하고, 최대 예산은 5억(50000)
const clientCondition = {
  type: '매매',
  maxPrice: 50000
};

console.log("테스트 1: '매매' 매물 중 고객의 '최대 예산' 이하인 매물만 찾아야 한다.");

// --- [2단계: 테스트 실행 및 검증] ---
try {
  const matched = findMatchingProperties(properties, clientCondition);
  
  // 기대 결과 1: 조건에 맞는 매물은 id 1, id 2 총 '2개'여야 합니다.
  assert.strictEqual(matched.length, 2, `매칭된 매물의 개수가 틀렸습니다. (기대값: 2, 실제값: ${matched.length})`);
  
  // 기대 결과 2: 정확히 id 1번과 2번이 나와야 합니다.
  assert.strictEqual(matched[0].id, 1);
  assert.strictEqual(matched[1].id, 2);
  
  console.log("✅ 테스트 1 통과!");
} catch (error) {
  console.error("❌ 테스트 1 실패: " + error.message);
}
