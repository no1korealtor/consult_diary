# -*- coding: utf-8 -*-
css_head = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>마포구 성산동 빌라 대지지분 평단가 분석기 | 모아타운·재개발</title>
  <link rel="icon" type="image/png" href="icon.png">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <style>
    :root {
      --bg-dark: #090d16;
      --card-bg: #111827;
      --card-border: #1f293d;
      --card-hover: #1e293b;
      --primary: #3b82f6;
      --primary-light: #60a5fa;
      --old-color: #38bdf8;
      --new-color: #fb923c;
      --bargain: #10b981;
      --text-main: #f3f4f6;
      --text-muted: #9ca3af;
      --text-dim: #6b7280;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Pretendard', sans-serif; }
    body { background: var(--bg-dark); color: var(--text-main); min-height: 100vh; padding: 20px; line-height: 1.5; }
    .container { max-width: 1400px; margin: 0 auto; display: flex; flex-direction: column; gap: 20px; }
    header {
      background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 60%, #1e293b 100%);
      border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 16px; padding: 24px 30px;
      display: flex; flex-direction: column; gap: 12px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5);
    }
    .header-top { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px; }
    h1 { font-size: 1.75rem; font-weight: 800; color: #ffffff; display: flex; align-items: center; gap: 10px; }
    .subtitle { color: #94a3b8; font-size: 0.95rem; font-weight: 500; }
    .tag-badge {
      display: inline-flex; align-items: center; gap: 6px; background: rgba(59, 130, 246, 0.15);
      border: 1px solid rgba(59, 130, 246, 0.4); color: #93c5fd; padding: 5px 12px; border-radius: 9999px;
      font-size: 0.82rem; font-weight: 600;
    }
    .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }
    .kpi-card {
      background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 14px; padding: 18px 20px;
      display: flex; flex-direction: column; gap: 8px; transition: transform 0.2s, border-color 0.2s;
    }
    .kpi-card:hover { transform: translateY(-2px); border-color: #374151; }
    .kpi-label { font-size: 0.85rem; font-weight: 600; color: var(--text-muted); display: flex; align-items: center; gap: 6px; }
    .kpi-val { font-size: 1.65rem; font-weight: 800; color: #fff; }
    .kpi-sub { font-size: 0.8rem; color: var(--text-dim); }
    .filter-panel { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 14px; padding: 18px 22px; display: flex; flex-direction: column; gap: 14px; }
    .filter-row { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; }
    .filter-label { font-size: 0.85rem; font-weight: 700; color: #cbd5e1; min-width: 75px; }
    .btn-group { display: flex; flex-wrap: wrap; gap: 6px; }
    .filter-btn {
      background: #1f293d; color: #94a3b8; border: 1px solid #334155; padding: 6px 14px; border-radius: 8px;
      font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: all 0.2s;
    }
    .filter-btn:hover { background: #334155; color: #fff; }
    .filter-btn.active { background: var(--primary); color: #fff; border-color: var(--primary-light); box-shadow: 0 0 12px rgba(59, 130, 246, 0.4); }
    .filter-btn.active.old { background: #0284c7; border-color: #38bdf8; box-shadow: 0 0 12px rgba(56, 189, 248, 0.4); }
    .filter-btn.active.new { background: #ea580c; border-color: #fb923c; box-shadow: 0 0 12px rgba(251, 146, 60, 0.4); }
    .search-input {
      background: #1f293d; border: 1px solid #334155; color: #fff; padding: 7px 14px; border-radius: 8px;
      font-size: 0.85rem; flex: 1; min-width: 180px; max-width: 320px;
    }
    .search-input:focus { outline: none; border-color: var(--primary-light); box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3); }
    .filter-status { margin-left: auto; font-size: 0.85rem; color: #38bdf8; font-weight: 600; }
    .chart-container-card {
      background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 16px; padding: 22px;
      display: flex; flex-direction: column; gap: 16px;
    }
    .chart-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
    .chart-title { font-size: 1.15rem; font-weight: 700; color: #f1f5f9; display: flex; align-items: center; gap: 8px; }
    .chart-legend-custom { display: flex; flex-wrap: wrap; gap: 14px; font-size: 0.82rem; font-weight: 600; }
    .legend-item { display: flex; align-items: center; gap: 6px; }
    .legend-color { width: 14px; height: 14px; border-radius: 4px; }
    .legend-line { width: 20px; height: 3px; border-radius: 2px; }
    .chart-box { position: relative; height: 520px; width: 100%; }
    .bracket-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; }
    .bracket-card {
      background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 14px; padding: 18px 20px;
      display: flex; flex-direction: column; gap: 12px; cursor: pointer; transition: all 0.2s;
    }
    .bracket-card:hover { border-color: var(--primary); transform: translateY(-2px); }
    .bracket-card.active { border-color: var(--primary-light); background: rgba(30, 41, 59, 0.9); box-shadow: 0 0 15px rgba(59, 130, 246, 0.25); }
    .bracket-head { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 10px; }
    .bracket-title { font-size: 1.05rem; font-weight: 700; color: #fff; }
    .bracket-count { font-size: 0.8rem; font-weight: 600; padding: 2px 8px; border-radius: 6px; background: #1f293d; color: #94a3b8; }
    .bracket-stats { display: flex; flex-direction: column; gap: 6px; font-size: 0.85rem; }
    .stat-row { display: flex; justify-content: space-between; color: var(--text-muted); }
    .stat-row b { color: #f3f4f6; }
    .premium-badge { display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 0.78rem; font-weight: 700; background: rgba(251, 146, 60, 0.2); color: #fb923c; }
    .bracket-insight { font-size: 0.8rem; color: #94a3b8; background: rgba(15, 23, 42, 0.6); padding: 8px 10px; border-radius: 6px; border-left: 3px solid var(--primary); }
    .table-card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 16px; padding: 22px; display: flex; flex-direction: column; gap: 16px; }
    .table-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
    .table-title { font-size: 1.15rem; font-weight: 700; color: #f1f5f9; display: flex; align-items: center; gap: 8px; }
    .table-responsive { overflow-x: auto; border: 1px solid var(--card-border); border-radius: 10px; }
    table { width: 100%; border-collapse: collapse; font-size: 0.85rem; text-align: left; }
    th { background: #1f293d; color: #cbd5e1; padding: 10px 12px; font-weight: 700; border-bottom: 1px solid var(--card-border); white-space: nowrap; cursor: pointer; }
    td { padding: 9px 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); color: #e2e8f0; white-space: nowrap; }
    tr:hover td { background: rgba(59, 130, 246, 0.08); }
    .badge-old { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); padding: 2px 7px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
    .badge-new { background: rgba(251, 146, 60, 0.15); color: #fb923c; border: 1px solid rgba(251, 146, 60, 0.3); padding: 2px 7px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
    .badge-bargain { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); padding: 2px 8px; border-radius: 9999px; font-size: 0.78rem; font-weight: 700; }
    .badge-over { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); padding: 2px 8px; border-radius: 9999px; font-size: 0.78rem; font-weight: 700; }
    .pagination { display: flex; justify-content: flex-end; align-items: center; gap: 8px; margin-top: 10px; }
    .page-btn { background: #1f293d; border: 1px solid #334155; color: #cbd5e1; padding: 5px 12px; border-radius: 6px; font-size: 0.8rem; cursor: pointer; }
    .page-btn:disabled { opacity: 0.4; cursor: not-allowed; }
    .page-info { font-size: 0.82rem; color: var(--text-dim); }
    .guide-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 16px; }
    .guide-card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 14px; padding: 20px; display: flex; flex-direction: column; gap: 10px; }
    .guide-card h3 { font-size: 1rem; font-weight: 700; color: #93c5fd; display: flex; align-items: center; gap: 8px; }
    .guide-card p { font-size: 0.85rem; color: #cbd5e1; line-height: 1.6; }
    .export-btn {
      background: #047857; color: #fff; border: 1px solid #10b981; padding: 6px 14px; border-radius: 8px;
      font-size: 0.85rem; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px;
    }
    .export-btn:hover { background: #059669; }
    @media (max-width: 768px) {
      body { padding: 10px; }
      h1 { font-size: 1.35rem; }
      .chart-box { height: 380px; }
      .filter-row { flex-direction: column; align-items: flex-start; }
      .search-input { max-width: 100%; width: 100%; }
    }
  </style>
</head>
"""

with open("land_value_analyzer.html", "w", encoding="utf-8") as f:
    f.write(css_head)
print("Part 1 written successfully.")
