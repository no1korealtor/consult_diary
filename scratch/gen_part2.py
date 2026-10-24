# -*- coding: utf-8 -*-
body_dom = """<body>
  <div class="container">
    <header>
      <div class="header-top">
        <div class="title-group">
          <h1><span>🏙️</span> 마포구 성산동 다세대·빌라 대지지분 분석기</h1>
          <p class="subtitle">모아타운·재개발 추진지역 실거래 652건 전수 분석 (2024.10 ~ 2026.08) | 신축 vs 구축 듀얼 곡선 회귀 모델</p>
        </div>
        <div class="tag-badge"><span>●</span> 2024.10 ~ 2026.08 전수 조사</div>
      </div>
    </header>

    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">📊 분석 거래 건수</div>
        <div class="kpi-val" id="kpi-count">652건</div>
        <div class="kpi-sub" id="kpi-count-sub">전체 652건 중 100% 반영</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">🏛️ 구축 (5년 초과) 평균 평당가</div>
        <div class="kpi-val" style="color: #38bdf8;" id="kpi-old-price">5,186만</div>
        <div class="kpi-sub">575건 | 모아타운 투자 주타깃</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">🏗️ 신축 (5년 이하) 평균 평당가</div>
        <div class="kpi-val" style="color: #fb923c;" id="kpi-new-price">7,380만</div>
        <div class="kpi-sub">77건 | 건물 감가 미반영 시세</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">🚀 신축 프리미엄 격차</div>
        <div class="kpi-val" style="color: #4ade80;" id="kpi-premium">+2,194만</div>
        <div class="kpi-sub">구축 대비 +42.3% 프리미엄 형성</div>
      </div>
    </div>

    <div class="filter-panel">
      <div class="filter-row">
        <div class="filter-label">건축 연한:</div>
        <div class="btn-group" id="filter-age">
          <button class="filter-btn active" data-val="all">전체 (652)</button>
          <button class="filter-btn old" data-val="old">구축 5년 초과 (575)</button>
          <button class="filter-btn new" data-val="new">신축 5년 이하 (77)</button>
        </div>
      </div>

      <div class="filter-row">
        <div class="filter-label">지분 구간:</div>
        <div class="btn-group" id="filter-bracket">
          <button class="filter-btn active" data-val="all">전체 구간</button>
          <button class="filter-btn" data-val="under5">초소형 (&lt; 5평)</button>
          <button class="filter-btn" data-val="5to8">소형 (5 ~ 8평)</button>
          <button class="filter-btn" data-val="8to12">중형 (8 ~ 12평)</button>
          <button class="filter-btn" data-val="over12">대형 (&ge; 12평)</button>
        </div>
      </div>

      <div class="filter-row">
        <div class="filter-label">계약 기간:</div>
        <div class="btn-group" id="filter-period">
          <button class="filter-btn active" data-val="all">최근 24개월</button>
          <button class="filter-btn" data-val="12m">최근 12개월</button>
          <button class="filter-btn" data-val="6m">최근 6개월</button>
        </div>
        <input type="text" id="search-input" class="search-input" placeholder="건물명 또는 지번 검색 (예: 현대, 50-15)">
        <button class="filter-btn" id="btn-reset" style="margin-left: 6px;">초기화</button>
        <div class="filter-status" id="filter-status-text">필터 결과: 652건</div>
      </div>
    </div>

    <div class="chart-container-card">
      <div class="chart-header">
        <div class="chart-title"><span>📈</span> 대지지분(평) vs 지분 평당가(만원/평) 듀얼 곡선 산점도</div>
        <div class="chart-legend-custom">
          <div class="legend-item">
            <div class="legend-color" style="background: rgba(56, 189, 248, 0.7); border: 1px solid #38bdf8;"></div>
            <span>구축 거래 (5년 초과)</span>
          </div>
          <div class="legend-item">
            <div class="legend-color" style="background: rgba(251, 146, 60, 0.8); border: 1px solid #fb923c;"></div>
            <span>신축 거래 (5년 이하)</span>
          </div>
          <div class="legend-item">
            <div class="legend-line" style="background: #0284c7; height: 3px;"></div>
            <span>구축 적정 추세선</span>
          </div>
          <div class="legend-item">
            <div class="legend-line" style="background: #ea580c; height: 2px; border-top: 2px dashed #ea580c;"></div>
            <span>신축 프리미엄선</span>
          </div>
        </div>
      </div>
      <div class="chart-box">
        <canvas id="scatterChart"></canvas>
      </div>
    </div>

    <div class="bracket-grid" id="bracket-cards-container"></div>

    <div class="table-card">
      <div class="table-header">
        <div class="table-title"><span>🎯</span> 저평가 급매 발굴기 (회귀곡선 기준 최대 할인 거래 TOP 10)</div>
        <div style="font-size: 0.82rem; color: #94a3b8;">* 동일 대지지분의 추세선 적정 단가 대비 가장 저렴하게 매매된 순서입니다.</div>
      </div>
      <div class="table-responsive">
        <table>
          <thead>
            <tr>
              <th>순위</th>
              <th>건물명 / 층</th>
              <th>구분</th>
              <th>준공년</th>
              <th>계약월</th>
              <th>대지지분</th>
              <th>전용면적</th>
              <th>실거래가</th>
              <th>지분 평당가</th>
              <th>적정 기준가</th>
              <th>할인율 (괴리율)</th>
            </tr>
          </thead>
          <tbody id="bargain-tbody"></tbody>
        </table>
      </div>
    </div>

    <div class="table-card">
      <div class="table-header">
        <div class="table-title"><span>📋</span> 실거래 전수 상세 데이터</div>
        <button class="export-btn" id="btn-export-csv"><span>📥</span> 엑셀(CSV) 다운로드</button>
      </div>
      <div class="table-responsive">
        <table>
          <thead>
            <tr>
              <th onclick="sortTable('date')">계약월 ↕</th>
              <th onclick="sortTable('name')">건물명 ↕</th>
              <th onclick="sortTable('floor')">층 ↕</th>
              <th onclick="sortTable('year')">준공 ↕</th>
              <th onclick="sortTable('pyung')">대지지분(평) ↕</th>
              <th onclick="sortTable('excl_p')">전용(평) ↕</th>
              <th onclick="sortTable('deal')">실거래가 ↕</th>
              <th onclick="sortTable('unit_price')">지분 평당가 ↕</th>
              <th onclick="sortTable('cat_exp')">기준 곡선가 ↕</th>
              <th onclick="sortTable('diff_pct')">괴리율 ↕</th>
            </tr>
          </thead>
          <tbody id="full-tbody"></tbody>
        </table>
      </div>
      <div class="pagination">
        <button class="page-btn" id="btn-prev-page">이전</button>
        <span class="page-info" id="page-info">1 / 1</span>
        <button class="page-btn" id="btn-next-page">다음</button>
      </div>
    </div>

    <div class="guide-grid">
      <div class="guide-card">
        <h3>💡 1. 대지지분 평단가 역비례 곡선의 원리</h3>
        <p>
          그래프에서 보듯 대지지분이 3~4평 수준의 초소형 빌라는 평당가가 8,000만~1억 원을 상회하는 반면,
          12평 이상의 대형 빌라는 3,000만원 선으로 수렴합니다.<br>
          이는 소액 투자자들이 총 매매가(2~3억 대)가 낮은 물건에 집중되면서 평당가 프리미엄이 붙기 때문입니다.
          모아타운 감정평가는 평당 단가가 아닌 <strong>총 대지지분 면적에 비례</strong>하여 권리가액이 산정되므로,
          지나치게 평당가가 높은 초소형은 추가분담금 부담이 커질 수 있습니다.
        </p>
      </div>
      <div class="guide-card">
        <h3>⚖️ 2. 준공 5년 기준(신축 vs 구축)의 실무적 핵심</h3>
        <p>
          모아타운 및 소규모재개발 구역은 <strong>노후도 57%(모아타운 기준)</strong> 충족이 사업 승인의 핵심 열쇠입니다.
          준공 5년 이내의 신축 빌라는 노후도 산정에서 불리할 뿐만 아니라,
          지분 쪼개기 방지 및 조합원 분양권 취득 기준일(권리산정기준일) 제한에 걸릴 위험이 있습니다.<br>
          또한 신축은 건물값 프리미엄이 평당 2,000만원 이상 포함되어 있어, 순수 대지지분 가치 기준으로는 구축 5년 초과 매물이 투자 효율이 월등히 높습니다.
        </p>
      </div>
      <div class="guide-card">
        <h3>🎯 3. 성산동 모아타운 황금 구간: [5~8평 구축]</h3>
        <p>
          성산동 분석 결과, <strong>지분 5~8평 구간의 구축 빌라</strong>는 평균 4.14억원(평당 5,854만원) 수준으로 거래되며,
          신축 대비 26.8% 저렴하면서도 전세가율이 방어되어 갭투자 실투자금을 최소화할 수 있습니다.<br>
          재개발 추진 시 국민평형(84㎡) 또는 59㎡ 배정에 가장 안정적인 지분 면적을 확보하는 핵심 주력 물건군입니다.
        </p>
      </div>
    </div>

  </div>
"""

with open("land_value_analyzer.html", "a", encoding="utf-8") as f:
    f.write(body_dom)
print("Part 2 appended successfully.")
