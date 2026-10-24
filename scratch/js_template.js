  <script>
    const rawData = __DATA__;

    const A_OLD = 12316.95, B_OLD = -3409.53;
    const A_NEW = 10211.72, B_NEW = -1609.57;

    function calcOldCurve(x) {
      return Math.max(1500, A_OLD + B_OLD * Math.log(x));
    }
    function calcNewCurve(x) {
      return Math.max(2500, A_NEW + B_NEW * Math.log(x));
    }

    let state = {
      age: 'all',
      bracket: 'all',
      period: 'all',
      search: '',
      sortCol: 'date',
      sortAsc: false,
      page: 1,
      pageSize: 20
    };

    let chartInstance = null;

    function getFilteredData() {
      return rawData.filter(d => {
        if (state.age === 'old' && d.is_new) return false;
        if (state.age === 'new' && !d.is_new) return false;

        if (state.bracket === 'under5' && !(d.pyung < 5)) return false;
        if (state.bracket === '5to8' && !(d.pyung >= 5 && d.pyung < 8)) return false;
        if (state.bracket === '8to12' && !(d.pyung >= 8 && d.pyung < 12)) return false;
        if (state.bracket === 'over12' && !(d.pyung >= 12)) return false;

        if (state.period === '6m' && d.date < '2026.03') return false;
        if (state.period === '12m' && d.date < '2025.09') return false;

        if (state.search) {
          const q = state.search.toLowerCase();
          const mName = d.name && d.name.toLowerCase().includes(q);
          const mJibun = d.jibun && d.jibun.includes(q);
          if (!mName && !mJibun) return false;
        }
        return true;
      });
    }

    function initChart() {
      const ctx = document.getElementById('scatterChart').getContext('2d');
      const curveOldPts = [];
      const curveNewPts = [];
      for (let x = 2.0; x <= 20.0; x += 0.25) {
        curveOldPts.push({ x: Number(x.toFixed(2)), y: Math.round(calcOldCurve(x)) });
        curveNewPts.push({ x: Number(x.toFixed(2)), y: Math.round(calcNewCurve(x)) });
      }

      chartInstance = new Chart(ctx, {
        type: 'scatter',
        data: {
          datasets: [
            {
              label: '구축 실거래 (5년 초과)',
              data: [],
              backgroundColor: 'rgba(56, 189, 248, 0.65)',
              borderColor: '#38bdf8',
              borderWidth: 1,
              pointRadius: 5.5,
              pointHoverRadius: 8,
              order: 2
            },
            {
              label: '신축 실거래 (5년 이하)',
              data: [],
              backgroundColor: 'rgba(251, 146, 60, 0.75)',
              borderColor: '#fb923c',
              borderWidth: 1.5,
              pointRadius: 6,
              pointHoverRadius: 8.5,
              order: 1
            },
            {
              label: '구축 적정 회귀선',
              type: 'line',
              data: curveOldPts,
              borderColor: '#0284c7',
              borderWidth: 3,
              fill: false,
              pointRadius: 0,
              tension: 0.4,
              order: 3
            },
            {
              label: '신축 프리미엄 회귀선',
              type: 'line',
              data: curveNewPts,
              borderColor: '#ea580c',
              borderWidth: 2.5,
              borderDash: [6, 4],
              fill: false,
              pointRadius: 0,
              tension: 0.4,
              order: 4
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: { duration: 400 },
          scales: {
            x: {
              type: 'linear',
              position: 'bottom',
              min: 1,
              max: 20,
              title: {
                display: true,
                text: '대지지분 (평)',
                color: '#94a3b8',
                font: { size: 13, weight: 'bold' }
              },
              grid: { color: 'rgba(255, 255, 255, 0.06)' },
              ticks: { color: '#94a3b8' }
            },
            y: {
              min: 1000,
              max: 13000,
              title: {
                display: true,
                text: '지분 평당가 (만원/평)',
                color: '#94a3b8',
                font: { size: 13, weight: 'bold' }
              },
              grid: { color: 'rgba(255, 255, 255, 0.06)' },
              ticks: {
                color: '#94a3b8',
                callback: val => val.toLocaleString() + '만'
              }
            }
          },
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: 'rgba(15, 23, 42, 0.95)',
              titleColor: '#ffffff',
              bodyColor: '#e2e8f0',
              borderColor: 'rgba(99, 102, 241, 0.4)',
              borderWidth: 1,
              padding: 12,
              displayColors: false,
              callbacks: {
                title: function(items) {
                  const item = items[0];
                  if (item.datasetIndex >= 2) return item.dataset.label;
                  const raw = item.raw.rawItem;
                  const fl = raw.floor > 0 ? raw.floor + '층' : (raw.floor < 0 ? '지층' : '옥탑');
                  return `${raw.name} (${fl})`;
                },
                label: function(item) {
                  if (item.datasetIndex >= 2) {
                    return `${item.raw.x}평 기준: ${item.raw.y.toLocaleString()}만원/평`;
                  }
                  const d = item.raw.rawItem;
                  const dealEok = (d.deal / 10000).toFixed(2);
                  const expDiff = d.diff_pct;
                  const diffSign = expDiff > 0 ? '+' : '';
                  const statusLabel = expDiff <= -15 ? '🔥 저평가 급매' : (expDiff >= 15 ? '⚠️ 고평가/호가' : '적정 시세');
                  return [
                    `• 실거래가: ${d.deal.toLocaleString()}만원 (${dealEok}억)`,
                    `• 대지지분: ${d.pyung}평 (${d.land_m2}㎡)`,
                    `• 전용면적: ${d.excl_p}평 (${d.excl_m2}㎡)`,
                    `• 지분 평당가: ${d.unit_price.toLocaleString()}만원/평`,
                    `• 계약월 / 준공: ${d.date} / ${d.year}년 (${d.is_new ? '신축' : '구축'})`,
                    `• 기준곡선가: ${d.cat_exp.toLocaleString()}만원 (${diffSign}${expDiff}% | ${statusLabel})`
                  ];
                }
              }
            }
          }
        }
      });
    }

    function updateChart(filtered) {
      const oldPts = [];
      const newPts = [];

      filtered.forEach(d => {
        const pt = { x: d.pyung, y: d.unit_price, rawItem: d };
        if (d.is_new) {
          newPts.push(pt);
        } else {
          oldPts.push(pt);
        }
      });

      chartInstance.data.datasets[0].data = oldPts;
      chartInstance.data.datasets[1].data = newPts;
      chartInstance.update();
    }

    function updateKPIs(filtered) {
      const total = filtered.length;
      document.getElementById('kpi-count').innerText = total.toLocaleString() + '건';
      document.getElementById('kpi-count-sub').innerText = `전체 652건 중 ${((total / 652) * 100).toFixed(1)}%`;

      const oldList = filtered.filter(d => !d.is_new);
      const newList = filtered.filter(d => d.is_new);

      if (oldList.length > 0) {
        const avgOld = Math.round(oldList.reduce((s, d) => s + d.unit_price, 0) / oldList.length);
        document.getElementById('kpi-old-price').innerText = avgOld.toLocaleString() + '만';
      } else {
        document.getElementById('kpi-old-price').innerText = '-';
      }

      if (newList.length > 0) {
        const avgNew = Math.round(newList.reduce((s, d) => s + d.unit_price, 0) / newList.length);
        document.getElementById('kpi-new-price').innerText = avgNew.toLocaleString() + '만';
      } else {
        document.getElementById('kpi-new-price').innerText = '-';
      }

      if (oldList.length > 0 && newList.length > 0) {
        const avgOld = oldList.reduce((s, d) => s + d.unit_price, 0) / oldList.length;
        const avgNew = newList.reduce((s, d) => s + d.unit_price, 0) / newList.length;
        const diff = Math.round(avgNew - avgOld);
        document.getElementById('kpi-premium').innerText = `+${diff.toLocaleString()}만`;
      } else {
        document.getElementById('kpi-premium').innerText = '-';
      }

      document.getElementById('filter-status-text').innerText = `필터 결과: ${total}건`;
    }

    function renderBrackets() {
      const brackets = [
        {
          id: 'under5',
          label: '1. 초소형 (< 5평)',
          fn: d => d.pyung < 5,
          desc: '소액 갭투자 집중, 지분 평당가 왜곡 최고조',
          suitability: '단기 차익형 (분담금 주의)'
        },
        {
          id: '5to8',
          label: '2. 소형 (5 ~ 8평)',
          fn: d => d.pyung >= 5 && d.pyung < 8,
          desc: '모아타운 실투자 1순위 황금 밸런스 구간',
          suitability: '최고 추천 (59㎡/84㎡ 배정 안정적)'
        },
        {
          id: '8to12',
          label: '3. 중형 (8 ~ 12평)',
          fn: d => d.pyung >= 8 && d.pyung < 12,
          desc: '실거주 겸용 매물 다수, 안정적 감평 기대',
          suitability: '실거주 투자 겸용 (84㎡ 유력)'
        },
        {
          id: 'over12',
          label: '4. 대형 (≥ 12평)',
          fn: d => d.pyung >= 12,
          desc: '대지지분당 단가 최저, 대형평형 및 원플러스원',
          suitability: '대형 분양권 or 1+1 노림수'
        }
      ];

      const container = document.getElementById('bracket-cards-container');
      container.innerHTML = '';

      brackets.forEach(b => {
        const items = rawData.filter(b.fn);
        const olds = items.filter(d => !d.is_new);
        const news = items.filter(d => d.is_new);

        const avgPyung = items.length ? (items.reduce((s, d) => s + d.pyung, 0) / items.length).toFixed(2) : 0;
        const avgDeal = items.length ? Math.round(items.reduce((s, d) => s + d.deal, 0) / items.length) : 0;
        const avgOldP = olds.length ? Math.round(olds.reduce((s, d) => s + d.unit_price, 0) / olds.length) : 0;
        const avgNewP = news.length ? Math.round(news.reduce((s, d) => s + d.unit_price, 0) / news.length) : 0;
        const premPct = avgOldP > 0 && avgNewP > 0 ? (((avgNewP - avgOldP) / avgOldP) * 100).toFixed(1) : 0;

        const card = document.createElement('div');
        card.className = `bracket-card ${state.bracket === b.id ? 'active' : ''}`;
        card.onclick = () => {
          if (state.bracket === b.id) {
            setBracketFilter('all');
          } else {
            setBracketFilter(b.id);
          }
        };

        card.innerHTML = `
          <div class="bracket-head">
            <span class="bracket-title">${b.label}</span>
            <span class="bracket-count">${items.length}건 (${olds.length}구 / ${news.length}신)</span>
          </div>
          <div class="bracket-stats">
            <div class="stat-row"><span>평균 지분 / 매매가:</span> <b>${avgPyung}평 / ${(avgDeal / 10000).toFixed(2)}억</b></div>
            <div class="stat-row"><span>구축 평당가:</span> <b style="color: #38bdf8;">${avgOldP.toLocaleString()}만원</b></div>
            <div class="stat-row"><span>신축 평당가:</span> <b style="color: #fb923c;">${avgNewP.toLocaleString()}만원</b> <span class="premium-badge">+${premPct}%</span></div>
          </div>
          <div class="bracket-insight">
            <strong>${b.suitability}</strong><br>
            ${b.desc}
          </div>
        `;
        container.appendChild(card);
      });
    }

    function renderBargains(filtered) {
      const tbody = document.getElementById('bargain-tbody');
      tbody.innerHTML = '';
      const sorted = [...filtered].sort((a, b) => a.diff_pct - b.diff_pct).slice(0, 10);

      sorted.forEach((d, idx) => {
        const tr = document.createElement('tr');
        const badgeClass = d.is_new ? 'badge-new' : 'badge-old';
        const flStr = d.floor > 0 ? `${d.floor}층` : (d.floor < 0 ? '지층' : '옥탑');

        tr.innerHTML = `
          <td style="font-weight: 800; color: #38bdf8;">#${idx + 1}</td>
          <td><b>${d.name}</b> (${flStr})</td>
          <td><span class="${badgeClass}">${d.is_new ? '신축' : '구축'}</span></td>
          <td>${d.year}년</td>
          <td>${d.date}</td>
          <td><b>${d.pyung}평</b> <span style="font-size: 0.75rem; color: #94a3b8;">(${d.land_m2}㎡)</span></td>
          <td>${d.excl_p}평</td>
          <td style="color: #fff; font-weight: 700;">${(d.deal / 10000).toFixed(2)}억 <span style="font-size: 0.75rem; color: #94a3b8;">(${d.deal.toLocaleString()}만)</span></td>
          <td style="color: #38bdf8; font-weight: 700;">${d.unit_price.toLocaleString()}만원</td>
          <td style="color: #94a3b8;">${d.cat_exp.toLocaleString()}만원</td>
          <td><span class="badge-bargain">${d.diff_pct}%</span></td>
        `;

        tr.onclick = () => {
          alert(`[${d.name} ${flStr}]
• 실거래가: ${d.deal.toLocaleString()}만원 (${(d.deal / 10000).toFixed(2)}억)
• 대지지분: ${d.pyung}평 (${d.land_m2}㎡)
• 전용면적: ${d.excl_p}평 (${d.excl_m2}㎡)
• 지분평당가: ${d.unit_price.toLocaleString()}만원/평
• 기준곡선가: ${d.cat_exp.toLocaleString()}만원/평
• 할인율: ${d.diff_pct}% (저평가 급매)`);
        };

        tbody.appendChild(tr);
      });
    }

    function renderFullTable(filtered) {
      const tbody = document.getElementById('full-tbody');
      tbody.innerHTML = '';

      const sorted = [...filtered].sort((a, b) => {
        let va = a[state.sortCol];
        let vb = b[state.sortCol];
        if (typeof va === 'string') {
          return state.sortAsc ? va.localeCompare(vb) : vb.localeCompare(va);
        }
        return state.sortAsc ? va - vb : vb - va;
      });

      const total = sorted.length;
      const totalPages = Math.max(1, Math.ceil(total / state.pageSize));
      if (state.page > totalPages) state.page = totalPages;

      const start = (state.page - 1) * state.pageSize;
      const pageItems = sorted.slice(start, start + state.pageSize);

      pageItems.forEach(d => {
        const tr = document.createElement('tr');
        const flStr = d.floor > 0 ? `${d.floor}층` : (d.floor < 0 ? '지층' : '옥탑');
        const diffBadge = d.diff_pct < -10 
          ? `<span class="badge-bargain">${d.diff_pct}%</span>` 
          : (d.diff_pct > 15 ? `<span class="badge-over">+${d.diff_pct}%</span>` : `${d.diff_pct > 0 ? '+' : ''}${d.diff_pct}%`);

        tr.innerHTML = `
          <td>${d.date}</td>
          <td><b>${d.name}</b></td>
          <td>${flStr}</td>
          <td>${d.year} <span class="${d.is_new ? 'badge-new' : 'badge-old'}" style="font-size: 0.7rem;">${d.is_new ? '신' : '구'}</span></td>
          <td><b>${d.pyung}평</b></td>
          <td>${d.excl_p}평</td>
          <td style="color: #fff; font-weight: 700;">${(d.deal / 10000).toFixed(2)}억</td>
          <td style="color: #38bdf8; font-weight: 700;">${d.unit_price.toLocaleString()}만</td>
          <td style="color: #94a3b8;">${d.cat_exp.toLocaleString()}만</td>
          <td>${diffBadge}</td>
        `;
        tbody.appendChild(tr);
      });

      document.getElementById('page-info').innerText = `${state.page} / ${totalPages} (총 ${total}건)`;
      document.getElementById('btn-prev-page').disabled = state.page <= 1;
      document.getElementById('btn-next-page').disabled = state.page >= totalPages;
    }

    function sortTable(col) {
      if (state.sortCol === col) {
        state.sortAsc = !state.sortAsc;
      } else {
        state.sortCol = col;
        state.sortAsc = (col === 'diff_pct' || col === 'unit_price' || col === 'pyung');
      }
      refresh();
    }

    function setBracketFilter(bVal) {
      state.bracket = bVal;
      document.querySelectorAll('#filter-bracket .filter-btn').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-val') === bVal);
      });
      state.page = 1;
      refresh();
    }

    function refresh() {
      const filtered = getFilteredData();
      updateChart(filtered);
      updateKPIs(filtered);
      renderBrackets();
      renderBargains(filtered);
      renderFullTable(filtered);
    }

    document.addEventListener('DOMContentLoaded', () => {
      initChart();

      document.querySelectorAll('#filter-age .filter-btn').forEach(btn => {
        btn.onclick = () => {
          document.querySelectorAll('#filter-age .filter-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          state.age = btn.getAttribute('data-val');
          state.page = 1;
          refresh();
        };
      });

      document.querySelectorAll('#filter-bracket .filter-btn').forEach(btn => {
        btn.onclick = () => {
          setBracketFilter(btn.getAttribute('data-val'));
        };
      });

      document.querySelectorAll('#filter-period .filter-btn').forEach(btn => {
        btn.onclick = () => {
          document.querySelectorAll('#filter-period .filter-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          state.period = btn.getAttribute('data-val');
          state.page = 1;
          refresh();
        };
      });

      const sInput = document.getElementById('search-input');
      sInput.oninput = () => {
        state.search = sInput.value.trim();
        state.page = 1;
        refresh();
      };

      document.getElementById('btn-reset').onclick = () => {
        state.age = 'all';
        state.bracket = 'all';
        state.period = 'all';
        state.search = '';
        state.page = 1;
        sInput.value = '';
        document.querySelectorAll('.filter-btn').forEach(b => {
          b.classList.toggle('active', b.getAttribute('data-val') === 'all');
        });
        refresh();
      };

      document.getElementById('btn-prev-page').onclick = () => {
        if (state.page > 1) {
          state.page--;
          renderFullTable(getFilteredData());
        }
      };
      document.getElementById('btn-next-page').onclick = () => {
        state.page++;
        renderFullTable(getFilteredData());
      };

      document.getElementById('btn-export-csv').onclick = () => {
        const filtered = getFilteredData();
        if (!filtered.length) return alert('내보낼 데이터가 없습니다.');

        let csv = '\uFEFF계약월,건물명,지번,층수,준공년도,구분,대지지분(평),대지지분(㎡),전용(평),전용(㎡),실거래가(만원),지분평당가(만원),기준곡선가(만원),괴리율(%)\n';
        filtered.forEach(d => {
          csv += `"${d.date}","${d.name}","${d.jibun}",${d.floor},${d.year},"${d.is_new ? '신축' : '구축'}",${d.pyung},${d.land_m2},${d.excl_p},${d.excl_m2},${d.deal},${d.unit_price},${d.cat_exp},${d.diff_pct}\n`;
        });

        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `성산동_다세대_대지지분실거래_${new Date().toISOString().slice(0, 10)}.csv`;
        link.click();
      };

      refresh();
    });
  </script>
</body>
</html>
