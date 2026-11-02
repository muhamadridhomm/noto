HTML_CSS_STYLES = """
:root {
  --bg: #F8FAFC;
  --card-bg: #FFFFFF;
  --card-border: #E2E8F0;
  --text-main: #0F172A;
  --text-muted: #64748B;
  --text-subtle: #94A3B8;

  /* Pillar Colors */
  --etom-bg: #EEF2FF; --etom-text: #4338CA; --etom-border: #C7D2FE;
  --tam-bg: #ECFDF5; --tam-text: #047857; --tam-border: #A7F3D0;
  --sid-bg: #FFFBEB; --sid-text: #B45309; --sid-border: #FDE68A;
  --oda-bg: #F0F9FF; --oda-text: #0369A1; --oda-border: #BAE6FD;

  /* Status Colors */
  --status-done-bg: #DCFCE7; --status-done-text: #15803D; --status-done-border: #86EFAC;
  --status-prog-bg: #DBEAFE; --status-prog-text: #1D4ED8; --status-prog-border: #93C5FD;
  --status-rev-bg: #FEF3C7; --status-rev-text: #B45309; --status-rev-border: #FCD34D;
  --status-todo-bg: #F1F5F9; --status-todo-text: #475569; --status-todo-border: #CBD5E1;
  --status-block-bg: #FFE4E6; --status-block-text: #BE123C; --status-block-border: #FDA4AF;

  /* Priority Colors */
  --prio-urgent-bg: #FFE4E6; --prio-urgent-text: #BE123C;
  --prio-high-bg: #FFEDD5; --prio-high-text: #C2410C;
  --prio-normal-bg: #DBEAFE; --prio-normal-text: #1D4ED8;
  --prio-low-bg: #F1F5F9; --prio-low-text: #64748B;

  /* Track Colors */
  --track-a-bg: #F1F5F9; --track-a-text: #334155; --track-a-indicator: #64748B;
  --track-b-bg: #F5F3FF; --track-b-text: #6D28D9; --track-b-indicator: #8B5CF6;
  --track-c-bg: #F0FDF4; --track-c-text: #15803D; --track-c-indicator: #22C55E;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", Helvetica, Arial, sans-serif;
  background-color: var(--bg);
  color: var(--text-main);
  line-height: 1.5;
  padding: 32px 24px;
  -webkit-font-smoothing: antialiased;
}

.container {
  max-width: 1280px;
  margin: 0 auto;
}

/* Top Executive Header */
.header-card {
  background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
  color: #FFFFFF;
  padding: 32px;
  border-radius: 20px;
  box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.25);
  margin-bottom: 24px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 16px;
}
.header-badge-tag {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  background: rgba(255, 255, 255, 0.12);
  color: #38BDF8;
  padding: 4px 10px;
  border-radius: 6px;
  margin-bottom: 8px;
}
.header-title-wrap h1 {
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -0.025em;
  color: #FFFFFF;
}
.header-title-wrap p {
  font-size: 13.5px;
  color: #94A3B8;
  margin-top: 6px;
  max-width: 820px;
  line-height: 1.6;
}
.header-meta-group {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}
.header-timestamp {
  font-size: 11.5px;
  font-family: ui-monospace, monospace;
  color: #CBD5E1;
  background: rgba(255, 255, 255, 0.08);
  padding: 5px 12px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.header-meta-pills {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.header-pill {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.08);
  color: #E2E8F0;
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.12);
}
.kpi-item {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 14px 18px;
  border-radius: 12px;
}
.kpi-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #94A3B8;
  font-weight: 600;
}
.kpi-val {
  font-size: 24px;
  font-weight: 800;
  color: #FFFFFF;
  margin-top: 4px;
}
.kpi-sub {
  font-size: 11px;
  color: #64748B;
  margin-top: 2px;
}
.kpi-val.highlight { color: #34D399; }
.kpi-val.blue { color: #60A5FA; }

/* View Switcher & Toolbar */
.control-toolbar {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  padding: 16px 20px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.toolbar-row-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}
.view-switcher-tabs {
  display: flex;
  background: #F1F5F9;
  padding: 4px;
  border-radius: 10px;
  gap: 4px;
  flex-wrap: wrap;
}
.view-tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 8px;
  border: none;
  background: transparent;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}
.view-tab-btn:hover {
  color: var(--text-main);
}
.view-tab-btn.active {
  background: #FFFFFF;
  color: var(--text-main);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}
.toolbar-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}
.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid var(--card-border);
  background: #FFFFFF;
  font-size: 11.5px;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}
.action-btn:hover {
  background: #F8FAFC;
  color: var(--text-main);
  border-color: #CBD5E1;
}

.toolbar-row-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid #F1F5F9;
}
.search-input-wrap {
  position: relative;
  flex: 1;
  min-width: 240px;
  max-width: 400px;
}
.search-input-wrap input {
  width: 100%;
  padding: 8px 12px 8px 34px;
  border-radius: 8px;
  border: 1px solid var(--card-border);
  background: #F8FAFC;
  font-size: 12.5px;
  color: var(--text-main);
  outline: none;
}
.search-input-wrap input:focus {
  border-color: #94A3B8;
  background: #FFFFFF;
}
.search-icon {
  position: absolute;
  left: 10px;
  top: 9px;
  width: 15px;
  height: 15px;
  stroke: #94A3B8;
}

.filter-pills-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.filter-group-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-subtle);
}
.pill-btn {
  padding: 4px 10px;
  border-radius: 6px;
  border: 1px solid var(--card-border);
  background: #FFFFFF;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s;
}
.pill-btn:hover {
  background: #F8FAFC;
}
.pill-btn.active {
  background: #0F172A;
  color: #FFFFFF;
  border-color: #0F172A;
}

/* Sub-Mode Selector Bar */
.submode-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 16px;
  padding: 10px 16px;
  background: #FFFFFF;
  border: 1px solid var(--card-border);
  border-radius: 12px;
}
.submode-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.submode-label {
  font-size: 11.5px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.sub-tab-btn {
  padding: 4px 12px;
  border-radius: 6px;
  border: none;
  background: transparent;
  font-size: 11.5px;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s;
}
.sub-tab-btn:hover {
  background: #F1F5F9;
  color: var(--text-main);
}
.sub-tab-btn.active {
  background: #EEF2FF;
  color: #4F46E5;
}

/* 1. SWIMLANE VIEW */
.swimlanes-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.swimlane-lane {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  transition: all 0.2s ease;
}
.swimlane-lane.collapsed .swimlane-cards-grid,
.swimlane-lane.collapsed .checklist-rows-wrapper {
  display: none;
}
.swimlane-lane.collapsed .chevron-icon {
  transform: rotate(-90deg);
}
.swimlane-lane-header {
  background: #F8FAFC;
  border-bottom: 1px solid var(--card-border);
  padding: 14px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  cursor: pointer;
  user-select: none;
}
.swimlane-lane-header:hover {
  background: #F1F5F9;
}
.lane-title-group {
  display: flex;
  align-items: center;
  gap: 10px;
}
.track-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.track-indicator.track-a { background: var(--track-a-indicator); }
.track-indicator.track-b { background: var(--track-b-indicator); }
.track-indicator.track-c { background: var(--track-c-indicator); }
.lane-title {
  font-size: 13.5px;
  font-weight: 700;
  color: var(--text-main);
}
.lane-count-badge {
  font-size: 11px;
  font-weight: 600;
  background: #E2E8F0;
  color: #475569;
  padding: 2px 8px;
  border-radius: 6px;
}
.lane-progress-group {
  display: flex;
  align-items: center;
  gap: 12px;
}
.lane-progress-text {
  font-size: 11.5px;
  font-family: ui-monospace, monospace;
  font-weight: 600;
  color: var(--text-muted);
}
.progress-bar-track {
  width: 110px;
  height: 8px;
  background: #E2E8F0;
  border-radius: 99px;
  overflow: hidden;
}
.progress-bar-fill {
  height: 100%;
  background: #16A34A;
  border-radius: 99px;
  transition: width 0.3s ease;
}
.chevron-icon {
  transition: transform 0.2s ease;
  color: var(--text-muted);
}

.swimlane-cards-grid {
  padding: 16px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 14px;
}

/* Task Card (Grid) */
.task-card {
  background: #FFFFFF;
  border: 1px solid var(--card-border);
  border-radius: 12px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 10px;
  transition: all 0.15s ease;
}
.task-card:hover {
  border-color: #CBD5E1;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}
.task-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}
.task-badges {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.task-title {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--text-main);
  line-height: 1.45;
}
.task-title.done {
  color: #94A3B8;
  text-decoration: line-through;
}
.task-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 8px;
}
.meta-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 10.5px;
  padding: 2px 7px;
  border-radius: 5px;
  font-weight: 500;
}
.group-tag { background: #F1F5F9; color: #475569; }
.track-tag { background: #F8FAFC; color: #334155; border: 1px solid #E2E8F0; font-weight: 600; }
.date-tag { background: #F8FAFC; color: var(--text-muted); font-family: ui-monospace, monospace; font-size: 10.5px; display: inline-flex; align-items: center; gap: 4px; padding: 2px 6px; border-radius: 4px; border: 1px solid #E2E8F0; }

/* 2. CHECKLIST (PER BARIS) VIEW */
.checklist-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.checklist-group {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}
.checklist-group.collapsed .checklist-rows-wrapper {
  display: none;
}
.checklist-group.collapsed .chevron-icon {
  transform: rotate(-90deg);
}
.checklist-rows-wrapper {
  display: flex;
  flex-direction: column;
}
.checklist-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-bottom: 1px solid #F1F5F9;
  gap: 14px;
  transition: background 0.15s ease;
}
.checklist-row:last-child {
  border-bottom: none;
}
.checklist-row:hover {
  background: #F8FAFC;
}
.checklist-main-col {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  flex: 1;
  min-width: 0;
}
.custom-checkbox {
  width: 18px;
  height: 18px;
  border-radius: 5px;
  border: 2px solid #CBD5E1;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  margin-top: 2px;
  transition: all 0.15s ease;
}
.custom-checkbox:hover {
  border-color: #94A3B8;
}
.custom-checkbox.checked {
  background: #16A34A;
  border-color: #16A34A;
}
.check-svg {
  width: 12px;
  height: 12px;
  stroke: #FFFFFF;
  display: none;
}
.custom-checkbox.checked .check-svg {
  display: block;
}
.checklist-text-wrap {
  flex: 1;
  min-width: 0;
}
.checklist-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
  line-height: 1.45;
  transition: all 0.15s ease;
}
.checklist-title.done {
  color: #94A3B8;
  text-decoration: line-through;
}
.checklist-sub {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}
.checklist-meta-col {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  flex-wrap: wrap;
  justify-content: flex-end;
}

/* 3. TIMELINE & GANTT ROADMAP */
.timeline-main-wrapper {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.gantt-wrapper {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  overflow-x: auto;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  padding: 24px;
}
.gantt-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.gantt-title-row h3 {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-main);
}
.gantt-grid {
  display: grid;
  grid-template-columns: 260px repeat(10, minmax(88px, 1fr));
  background: #E2E8F0;
  gap: 1px;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  overflow: hidden;
}
.gantt-cell {
  background: #FFFFFF;
  padding: 10px 12px;
  font-size: 11px;
  display: flex;
  align-items: center;
}
.gantt-header-cell {
  background: #F8FAFC;
  font-weight: 700;
  font-size: 11px;
  text-transform: uppercase;
  color: var(--text-muted);
  justify-content: center;
  letter-spacing: 0.03em;
}
.gantt-label-cell {
  background: #F8FAFC;
  font-weight: 600;
  color: var(--text-main);
  border-right: 1px solid #E2E8F0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 2px;
}
.gantt-label-title {
  font-size: 11.5px;
  font-weight: 700;
  color: var(--text-main);
}
.gantt-label-sub {
  font-size: 10px;
  color: var(--text-muted);
}
.gantt-bar-cell {
  background: #FFFFFF;
  position: relative;
  padding: 6px 4px;
}
.gantt-bar {
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 10px;
  font-size: 10.5px;
  font-weight: 700;
  color: #FFFFFF;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  transition: transform 0.15s ease;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.gantt-bar:hover {
  transform: translateY(-1px);
}
.gantt-bar.track-a { background: linear-gradient(90deg, #475569, #334155); }
.gantt-bar.track-b { background: linear-gradient(90deg, #7C3AED, #6D28D9); }
.gantt-bar.track-c { background: linear-gradient(90deg, #16A34A, #15803D); }
.gantt-bar.subtrack-bar { height: 22px; font-size: 10px; border-radius: 4px; opacity: 0.9; }

.gantt-milestone-marker {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: #F0FDFA;
  border: 1px solid #99F6E4;
  color: #0D9488;
  font-size: 9.5px;
  font-weight: 700;
  padding: 3px 6px;
  border-radius: 6px;
  white-space: nowrap;
}

/* Chronological Phase Stream */
.phase-stream-container {
  display: flex;
  flex-direction: column;
  gap: 0;
  position: relative;
  margin-top: 8px;
}
.phase-stream-item {
  display: flex;
  gap: 20px;
  position: relative;
}
.phase-stream-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 24px;
}
.phase-stream-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #0F172A;
  border: 3px solid #E2E8F0;
  margin-top: 6px;
  flex-shrink: 0;
}
.phase-stream-dot.phase-1 { background: #64748B; border-color: #CBD5E1; }
.phase-stream-dot.phase-2 { background: #8B5CF6; border-color: #DDD6FE; }
.phase-stream-dot.phase-3 { background: #0284C7; border-color: #BAE6FD; }
.phase-stream-dot.phase-4 { background: #D97706; border-color: #FDE68A; }
.phase-stream-dot.phase-5 { background: #16A34A; border-color: #BBF7D0; }

.phase-stream-line {
  flex: 1;
  width: 2px;
  background: #E2E8F0;
  margin: 6px 0;
}
.phase-stream-item:last-child .phase-stream-line {
  display: none;
}
.phase-stream-card {
  flex: 1;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 14px;
  padding: 18px 22px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}
.phase-stream-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--card-border);
}
.phase-stream-title {
  font-size: 14px;
  font-weight: 800;
  color: var(--text-main);
}
.phase-stream-desc {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.5;
  margin-bottom: 14px;
}

/* 4. DATA TABLE VIEW */
.matrix-table-wrap {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  overflow-x: auto;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}
.matrix-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  text-align: left;
}
.matrix-table th {
  background: #F8FAFC;
  padding: 10px 14px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
  border-bottom: 1px solid var(--card-border);
  cursor: pointer;
  user-select: none;
}
.matrix-table th:hover {
  color: var(--text-main);
  background: #F1F5F9;
}
.matrix-table td {
  padding: 10px 14px;
  border-bottom: 1px solid #F1F5F9;
  vertical-align: middle;
}
.matrix-table tr:hover td {
  background: #F8FAFC;
}
.col-num { width: 40px; color: var(--text-subtle); text-align: center; }
.col-code { width: 110px; }
.col-title { min-width: 320px; }
.col-pillar { width: 90px; text-align: center; }
.col-track { width: 95px; text-align: center; }
.col-status { width: 110px; text-align: center; }
.col-priority { width: 90px; text-align: center; }
.col-date { width: 140px; }

.cell-title { font-weight: 600; color: var(--text-main); line-height: 1.4; }
.cell-title.done { color: #94A3B8; text-decoration: line-through; }
.cell-sub { font-size: 10.5px; color: var(--text-muted); margin-top: 2px; }
.date-text { font-family: ui-monospace, monospace; font-size: 11px; color: var(--text-muted); }

/* 5. KANBAN BOARD VIEW */
.kanban-board {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  align-items: flex-start;
}
.kanban-column {
  background: #F8FAFC;
  border: 1px solid var(--card-border);
  border-radius: 14px;
  padding: 14px;
  min-height: 480px;
}
.kanban-column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--card-border);
}
.kanban-col-title-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.status-dot.status-to-do { background: #94A3B8; }
.status-dot.status-in-progress { background: #3B82F6; }
.status-dot.status-in-review { background: #F59E0B; }
.status-dot.status-done { background: #10B981; }
.kanban-col-title {
  font-size: 12.5px;
  font-weight: 700;
  color: var(--text-main);
}
.kanban-col-count {
  font-size: 11px;
  font-weight: 700;
  background: #E2E8F0;
  color: #475569;
  padding: 2px 7px;
  border-radius: 99px;
}
.kanban-cards-wrapper {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.kanban-card {
  background: #FFFFFF;
  border: 1px solid var(--card-border);
  border-radius: 10px;
  padding: 12px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.kanban-card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.kanban-card-title {
  font-size: 12px;
  font-weight: 600;
  line-height: 1.4;
  color: var(--text-main);
}
.kanban-card-title.done {
  color: #94A3B8;
  text-decoration: line-through;
}
.kanban-card-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 10px;
}
.kanban-empty {
  font-size: 11px;
  color: #94A3B8;
  font-style: italic;
  text-align: center;
  padding: 20px 0;
}

/* 6. MILESTONES VIEW */
.timeline-container {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  padding: 28px 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}
.timeline-item {
  display: flex;
  gap: 20px;
  position: relative;
}
.timeline-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 24px;
}
.timeline-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #0D9488;
  border: 3px solid #CCFBF1;
  margin-top: 4px;
}
.timeline-line {
  flex: 1;
  width: 2px;
  background: #E2E8F0;
  margin: 4px 0;
}
.timeline-item:last-child .timeline-line {
  display: none;
}
.timeline-content {
  flex: 1;
  background: #F8FAFC;
  border: 1px solid var(--card-border);
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 20px;
}
.timeline-header {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}
.timeline-date {
  font-size: 11.5px;
  font-family: ui-monospace, monospace;
  font-weight: 600;
  color: #0F766E;
  background: #F0FDFA;
  padding: 2px 8px;
  border-radius: 6px;
  border: 1px solid #CCFBF1;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.timeline-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-main);
}
.timeline-desc {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 6px;
  line-height: 1.5;
}
.timeline-footer {
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid #E2E8F0;
  font-size: 11px;
  color: var(--text-subtle);
}

/* Notes & Details Accordions */
.task-notes-details, .table-notes-details, .kanban-notes-details, .checklist-notes-details {
  margin-top: 6px;
}
.task-notes-summary, .table-notes-summary, .kanban-notes-summary, .checklist-notes-summary {
  font-size: 10px;
  font-weight: 600;
  color: #4F46E5;
  cursor: pointer;
  user-select: none;
}
.task-notes-content, .table-notes-content, .kanban-notes-content, .checklist-notes-content {
  margin-top: 4px;
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 6px;
  padding: 8px 10px;
  font-size: 10px;
  font-family: ui-monospace, monospace;
  color: #334155;
  white-space: pre-wrap;
  line-height: 1.45;
}

/* Badges */
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 99px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.02em;
  text-align: center;
}
.pillar-etom { background: var(--etom-bg); color: var(--etom-text); border: 1px solid var(--etom-border); }
.pillar-tam { background: var(--tam-bg); color: var(--tam-text); border: 1px solid var(--tam-border); }
.pillar-sid { background: var(--sid-bg); color: var(--sid-text); border: 1px solid var(--sid-border); }
.pillar-oda { background: var(--oda-bg); color: var(--oda-text); border: 1px solid var(--oda-border); }

.status-done { background: var(--status-done-bg); color: var(--status-done-text); border: 1px solid var(--status-done-border); }
.status-in-progress { background: var(--status-prog-bg); color: var(--status-prog-text); border: 1px solid var(--status-prog-border); }
.status-in-review { background: var(--status-rev-bg); color: var(--status-rev-text); border: 1px solid var(--status-rev-border); }
.status-to-do { background: var(--status-todo-bg); color: var(--status-todo-text); border: 1px solid var(--status-todo-border); }
.status-blocked { background: var(--status-block-bg); color: var(--status-block-text); border: 1px solid var(--status-block-border); }

.priority-urgent { background: var(--prio-urgent-bg); color: var(--prio-urgent-text); font-weight: 800; }
.priority-high { background: var(--prio-high-bg); color: var(--prio-high-text); }
.priority-normal { background: var(--prio-normal-bg); color: var(--prio-normal-text); }
.priority-low { background: var(--prio-low-bg); color: var(--prio-low-text); }

.track-track-a { background: var(--track-a-bg); color: var(--track-a-text); border: 1px solid #CBD5E1; }
.track-track-b { background: var(--track-b-bg); color: var(--track-b-text); border: 1px solid #DDD6FE; }
.track-track-c { background: var(--track-c-bg); color: var(--track-c-text); border: 1px solid #BBF7D0; }
.badge-teal { background: #F0FDFA; color: #0D9488; border: 1px solid #CCFBF1; }

.icon-inline {
  width: 12px;
  height: 12px;
  display: inline-block;
  vertical-align: -1px;
}
.svg-icon {
  width: 15px;
  height: 15px;
}

/* Print Formatting */
@media print {
  body { background: #FFFFFF; padding: 0; color: #000000; }
  .control-toolbar, .submode-bar { display: none !important; }
  .header-card { box-shadow: none; border-radius: 0; background: #0F172A !important; -webkit-print-color-adjust: exact; }
  .swimlane-lane, .matrix-table-wrap, .kanban-column, .timeline-container, .checklist-group, .gantt-wrapper { page-break-inside: avoid; border: 1px solid #CBD5E1; }
  details { open: true !important; }
  details[open] pre { white-space: pre-wrap !important; }
}
"""


HTML_JS_SCRIPTS = """
let currentView = 'swimlane';
let currentSwimlaneSubmode = 'grid';
let currentChecklistMode = 'track';
let currentTimelineMode = 'gantt';

let filters = {
  status: 'all',
  pillar: 'all',
  track: 'all'
};

function switchView(viewName, btn) {
  currentView = viewName;
  document.querySelectorAll('.view-tab-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');

  const views = ['swimlane', 'checklist', 'timeline', 'table', 'kanban', 'milestones'];
  views.forEach(v => {
    const el = document.getElementById('view' + capitalize(v));
    if (el) el.style.display = (v === viewName) ? 'block' : 'none';
  });

  filterAll();
}

function capitalize(s) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function switchSwimlaneSubmode(mode, btn) {
  currentSwimlaneSubmode = mode;
  btn.parentElement.querySelectorAll('.sub-tab-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');

  document.querySelectorAll('.swimlane-cards-grid').forEach(el => {
    el.style.display = (mode === 'grid') ? 'grid' : 'none';
  });
  document.querySelectorAll('.swimlane-rows-grid').forEach(el => {
    el.style.display = (mode === 'checklist') ? 'flex' : 'none';
  });
  filterAll();
}

function switchSwimlaneMode(mode, btn) {
  btn.parentElement.querySelectorAll('.sub-tab-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');

  document.getElementById('swimlaneGroupTrack').style.display = (mode === 'track') ? 'flex' : 'none';
  document.getElementById('swimlaneGroupPillar').style.display = (mode === 'pillar') ? 'flex' : 'none';
  document.getElementById('swimlaneGroupSubtrack').style.display = (mode === 'subtrack') ? 'flex' : 'none';
  filterAll();
}

function switchChecklistMode(mode, btn) {
  currentChecklistMode = mode;
  btn.parentElement.querySelectorAll('.sub-tab-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');

  document.getElementById('checklistGroupTrack').style.display = (mode === 'track') ? 'flex' : 'none';
  document.getElementById('checklistGroupPillar').style.display = (mode === 'pillar') ? 'flex' : 'none';
  document.getElementById('checklistGroupSubtrack').style.display = (mode === 'subtrack') ? 'flex' : 'none';
  document.getElementById('checklistGroupFlat').style.display = (mode === 'flat') ? 'flex' : 'none';
  filterAll();
}

function switchTimelineMode(mode, btn) {
  currentTimelineMode = mode;
  btn.parentElement.querySelectorAll('.sub-tab-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');

  document.getElementById('timelineGanttSection').style.display = (mode === 'gantt') ? 'block' : 'none';
  document.getElementById('timelineStreamSection').style.display = (mode === 'stream') ? 'block' : 'none';
  filterAll();
}

function setFilter(type, value, btn) {
  filters[type] = value;
  const parent = btn.parentElement;
  const btns = parent.querySelectorAll(`button[onclick*="'${type}'"]`);
  btns.forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  filterAll();
}

function toggleSwimlane(headerEl) {
  const lane = headerEl.closest('.swimlane-lane, .checklist-group');
  if (lane) {
    lane.classList.toggle('collapsed');
  }
}

function toggleTaskChecklist(checkboxEl, taskId) {
  const isChecked = checkboxEl.classList.toggle('checked');
  const row = checkboxEl.closest('.checklist-row');
  if (!row) return;

  const titleEl = row.querySelector('.checklist-title');
  const statusBadge = row.querySelector('.checklist-status-badge');

  if (isChecked) {
    if (titleEl) titleEl.classList.add('done');
    row.setAttribute('data-status', 'Done');
    if (statusBadge) {
      statusBadge.textContent = 'Done';
      statusBadge.className = 'badge status-done checklist-status-badge';
    }
  } else {
    if (titleEl) titleEl.classList.remove('done');
    row.setAttribute('data-status', 'To Do');
    if (statusBadge) {
      statusBadge.textContent = 'To Do';
      statusBadge.className = 'badge status-to-do checklist-status-badge';
    }
  }

  syncTaskStateAcrossViews(taskId, isChecked);
  updateLiveMetrics();
}

function syncTaskStateAcrossViews(taskId, isChecked) {
  // Sync all checklist boxes with this task ID
  document.querySelectorAll(`.checklist-row[data-id="${taskId}"]`).forEach(r => {
    const box = r.querySelector('.custom-checkbox');
    const t = r.querySelector('.checklist-title');
    const sb = r.querySelector('.checklist-status-badge');
    if (box) {
      if (isChecked) box.classList.add('checked');
      else box.classList.remove('checked');
    }
    if (t) {
      if (isChecked) t.classList.add('done');
      else t.classList.remove('done');
    }
    r.setAttribute('data-status', isChecked ? 'Done' : 'To Do');
    if (sb) {
      sb.textContent = isChecked ? 'Done' : 'To Do';
      sb.className = isChecked ? 'badge status-done checklist-status-badge' : 'badge status-to-do checklist-status-badge';
    }
  });

  // Sync task cards
  document.querySelectorAll(`.task-card[data-id="${taskId}"]`).forEach(c => {
    const t = c.querySelector('.task-title');
    if (t) {
      if (isChecked) t.classList.add('done');
      else t.classList.remove('done');
    }
    c.setAttribute('data-status', isChecked ? 'Done' : 'To Do');
  });

  // Sync matrix table rows
  document.querySelectorAll(`.matrix-row[data-id="${taskId}"]`).forEach(tr => {
    const t = tr.querySelector('.cell-title');
    if (t) {
      if (isChecked) t.classList.add('done');
      else t.classList.remove('done');
    }
    tr.setAttribute('data-status', isChecked ? 'Done' : 'To Do');
  });

  // Sync kanban cards
  document.querySelectorAll(`.kanban-card[data-id="${taskId}"]`).forEach(kc => {
    const t = kc.querySelector('.kanban-card-title');
    if (t) {
      if (isChecked) t.classList.add('done');
      else t.classList.remove('done');
    }
    kc.setAttribute('data-status', isChecked ? 'Done' : 'To Do');
  });
}

function updateLiveMetrics() {
  const allRows = document.querySelectorAll('#checklistGroupFlat .checklist-row');
  let total = allRows.length;
  if (total === 0) {
    total = document.querySelectorAll('.matrix-row').length;
  }
  let completed = 0;
  allRows.forEach(r => {
    if (r.getAttribute('data-status') === 'Done') completed++;
  });

  const pct = total > 0 ? ((completed / total) * 100).toFixed(1) : '0.0';

  const kpiCompleted = document.getElementById('kpiCompleted');
  const kpiRate = document.getElementById('kpiRate');
  if (kpiCompleted) kpiCompleted.textContent = completed;
  if (kpiRate) kpiRate.textContent = pct + '%';

  // Update lane progress bars
  document.querySelectorAll('.swimlane-lane, .checklist-group').forEach(groupEl => {
    const rows = groupEl.querySelectorAll('.checklist-row, .task-card');
    let gDone = 0;
    rows.forEach(r => {
      if (r.getAttribute('data-status') === 'Done') gDone++;
    });
    const gTotal = rows.length;
    const gPct = gTotal > 0 ? Math.round((gDone / gTotal) * 100) : 0;

    const progText = groupEl.querySelector('.lane-progress-text');
    const progFill = groupEl.querySelector('.progress-bar-fill');
    if (progText) progText.textContent = `${gDone}/${gTotal} done (${gPct}%)`;
    if (progFill) progFill.style.width = gPct + '%';
  });
}

function filterAll() {
  const query = (document.getElementById('searchInput').value || '').toLowerCase().trim();
  const elements = document.querySelectorAll('.task-card, .matrix-row, .kanban-card, .checklist-row');

  elements.forEach(el => {
    const elStatus = el.getAttribute('data-status');
    const elPillar = el.getAttribute('data-pillar');
    const elTrack = el.getAttribute('data-track');
    const elSearch = el.getAttribute('data-search') || '';

    let matchStatus = true;
    if (filters.status === 'active') {
      matchStatus = (elStatus !== 'Done');
    } else if (filters.status !== 'all') {
      matchStatus = (elStatus === filters.status);
    }

    let matchPillar = true;
    if (filters.pillar !== 'all') {
      matchPillar = (elPillar === filters.pillar);
    }

    let matchTrack = true;
    if (filters.track !== 'all') {
      matchTrack = (elTrack === filters.track);
    }

    let matchQuery = true;
    if (query) {
      matchQuery = elSearch.includes(query);
    }

    if (matchStatus && matchPillar && matchTrack && matchQuery) {
      el.style.display = '';
    } else {
      el.style.display = 'none';
    }
  });
}

function toggleAllNotes(expand) {
  document.querySelectorAll('details').forEach(d => {
    d.open = expand;
  });
}

function sortTable(n) {
  const table = document.querySelector('.matrix-table');
  if (!table) return;
  let rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
  switching = true;
  dir = "asc";
  while (switching) {
    switching = false;
    rows = table.rows;
    for (i = 1; i < (rows.length - 1); i++) {
      shouldSwitch = false;
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i + 1].getElementsByTagName("TD")[n];
      const xText = (x ? x.innerText : '').toLowerCase();
      const yText = (y ? y.innerText : '').toLowerCase();
      if (dir == "asc") {
        if (xText > yText) { shouldSwitch = true; break; }
      } else if (dir == "desc") {
        if (xText < yText) { shouldSwitch = true; break; }
      }
    }
    if (shouldSwitch) {
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      switchcount++;
    } else {
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
}
"""
