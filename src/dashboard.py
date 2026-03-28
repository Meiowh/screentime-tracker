"""Dashboard — returns a complete HTML string for a single-page screen time dashboard."""


def render_dashboard() -> str:
    return r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Screen Time Tracker</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#06060c;--surface:#0d0d18;--surface2:#13132a;--border:#1a1a3a;
  --border-hover:#2d2d5e;--text:#e0dfe8;--text-dim:#6b6b8d;--text-muted:#3d3d5e;
  --accent:#8b5cf6;--accent2:#6d28d9;--accent-glow:#8b5cf640;
  --pink:#ec4899;--pink-glow:#ec489940;
  --green:#10b981;--green-glow:#10b98140;
  --red:#ef4444;--red-glow:#ef444440;
  --amber:#f59e0b;--amber-glow:#f59e0b40;
  --blue:#3b82f6;
  --gradient:linear-gradient(135deg,#8b5cf6,#ec4899);
  --gradient2:linear-gradient(135deg,#6d28d9,#8b5cf6);
}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Inter',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;overflow-x:hidden}
.container{max-width:900px;margin:0 auto;padding:20px 16px 40px}

/* Animations */
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.75}}
@keyframes glow{0%,100%{box-shadow:0 0 15px var(--accent-glow)}50%{box-shadow:0 0 30px var(--accent-glow),0 0 60px var(--accent-glow)}}
@keyframes slideUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
@keyframes slideIn{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:translateX(0)}}
@keyframes countUp{from{opacity:0;transform:scale(.9)}to{opacity:1;transform:scale(1)}}
@keyframes owlFloat{0%,100%{transform:translateY(0) rotate(-3deg)}50%{transform:translateY(-8px) rotate(3deg)}}
@keyframes alertPulse{0%,100%{border-color:var(--red);box-shadow:0 0 20px var(--red-glow)}50%{border-color:#ff6b6b;box-shadow:0 0 40px var(--red-glow),0 0 80px #ef444420}}
@keyframes barGrow{from{width:0}to{width:var(--target-width)}}
@keyframes dotPulse{0%,100%{opacity:1}50%{opacity:.3}}
@keyframes shimmer{0%{background-position:-200% 0}100%{background-position:200% 0}}

/* Header */
.header{text-align:center;padding:32px 0 24px;position:relative}
.header::before{content:'';position:absolute;top:0;left:50%;transform:translateX(-50%);width:200px;height:200px;background:radial-gradient(circle,#8b5cf615,transparent 70%);pointer-events:none}
.header h1{font-size:1.8em;font-weight:700;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;letter-spacing:-.02em}
.header-meta{display:flex;align-items:center;justify-content:center;gap:12px;margin-top:8px;color:var(--text-dim);font-size:.8em}
.status-dot{width:6px;height:6px;border-radius:50%;background:var(--green);animation:dotPulse 2s ease infinite;display:inline-block}
.total-big{font-size:3.5em;font-weight:800;margin-top:16px;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;animation:countUp .6s ease;line-height:1.1}
.total-label{color:var(--text-dim);font-size:.78em;margin-top:4px;text-transform:uppercase;letter-spacing:2px}

/* Alert banners */
.alert-banner{padding:16px 20px;border-radius:16px;margin-bottom:16px;display:none;animation:slideUp .4s ease;text-align:center;backdrop-filter:blur(10px)}
.alert-banner.show{display:block}
.night-owl-banner{background:linear-gradient(135deg,#1a0e2e,#2d1044);border:1px solid #8b5cf655}
.night-owl-banner .owl-icon{font-size:2em;animation:owlFloat 3s ease-in-out infinite;display:inline-block}
.night-owl-banner .alert-text{color:#c4b5fd;font-size:.88em;margin-top:6px;font-weight:500}
.all-nighter-banner{background:linear-gradient(135deg,#2a0a0a,#3d0f0f);border:1px solid var(--red);animation:alertPulse 2s ease-in-out infinite}
.all-nighter-banner .alert-icon{font-size:1.8em}
.all-nighter-banner .alert-text{color:#fca5a5;font-size:.88em;margin-top:6px;font-weight:600}

/* Current activity card */
.current-card{padding:20px;border-radius:16px;background:linear-gradient(135deg,#061a14,#0a1f17);border:1px solid #10b98133;margin-bottom:20px;display:none;animation:glow 3s ease-in-out infinite}
.current-card.show{display:block}
.current-label{display:flex;align-items:center;gap:6px;color:var(--green);font-size:.72em;text-transform:uppercase;letter-spacing:2px;font-weight:600}
.current-label .live-dot{width:8px;height:8px;border-radius:50%;background:var(--green);animation:dotPulse 1.5s ease infinite}
.current-app{font-size:1.4em;font-weight:700;margin-top:8px}
.current-duration{color:var(--green);font-size:1em;margin-top:4px;font-variant-numeric:tabular-nums}

/* Stats grid */
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:20px}
.stat-card{background:var(--surface);border-radius:14px;padding:16px 12px;border:1px solid var(--border);text-align:center;transition:all .25s;position:relative;overflow:hidden}
.stat-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--gradient);opacity:0;transition:opacity .25s}
.stat-card:hover{border-color:var(--border-hover);transform:translateY(-2px)}.stat-card:hover::before{opacity:1}
.stat-icon{font-size:1.3em;margin-bottom:6px}
.stat-value{font-size:1.5em;font-weight:700;color:var(--accent)}
.stat-label{font-size:.68em;color:var(--text-dim);margin-top:4px;text-transform:uppercase;letter-spacing:.5px}

/* Tabs */
.tabs{display:flex;gap:4px;margin-bottom:20px;background:var(--surface);border-radius:12px;padding:4px;border:1px solid var(--border)}
.tab{flex:1;padding:10px;background:transparent;border:none;border-radius:10px;color:var(--text-dim);cursor:pointer;font-size:.82em;text-align:center;transition:all .2s;font-weight:500}
.tab.active{background:var(--surface2);color:var(--accent);box-shadow:0 2px 8px #00000030}
.tab:hover:not(.active){color:var(--text)}
.tab-panel{display:none;animation:slideUp .3s ease}.tab-panel.show{display:block}

/* App ranking */
.app-list{display:flex;flex-direction:column;gap:8px}
.app-row{display:flex;align-items:center;gap:12px;background:var(--surface);border-radius:14px;padding:14px 16px;border:1px solid var(--border);transition:all .25s;animation:slideIn .3s ease backwards}
.app-row:hover{border-color:var(--border-hover);background:var(--surface2);transform:translateX(3px)}
.app-row.active-session{border-color:#10b98133;box-shadow:0 0 15px var(--green-glow)}
.app-rank{width:24px;height:24px;border-radius:8px;background:var(--surface2);display:flex;align-items:center;justify-content:center;font-size:.7em;font-weight:700;color:var(--text-dim);flex-shrink:0}
.app-rank.top{background:var(--gradient);color:#fff}
.app-icon{font-size:1.4em;flex-shrink:0}
.app-info{flex:1;min-width:0}
.app-name{font-size:.9em;font-weight:600;display:flex;align-items:center;gap:8px}
.app-badge{font-size:.6em;padding:2px 8px;border-radius:20px;font-weight:600;text-transform:uppercase;letter-spacing:.5px}
.app-badge.live{background:#10b98120;color:var(--green)}
.app-meta{font-size:.72em;color:var(--text-dim);margin-top:3px;display:flex;gap:10px}
.app-bar-bg{height:4px;background:var(--border);border-radius:2px;margin-top:8px;overflow:hidden}
.app-bar-fill{height:100%;border-radius:2px;background:var(--gradient);transition:width .8s cubic-bezier(.22,1,.36,1)}
.app-bar-fill.live{background:linear-gradient(90deg,var(--green),#34d399)}
.app-right{display:flex;align-items:center;gap:12px;flex-shrink:0}
.app-time{text-align:right}
.app-time-value{font-size:1.15em;font-weight:700;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.app-time-pct{font-size:.65em;color:var(--text-dim)}

/* Hourly heatmap */
.heatmap{display:grid;grid-template-columns:repeat(12,1fr);gap:4px;margin-top:8px}
.heatmap-cell{aspect-ratio:1;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:.6em;color:var(--text-dim);background:var(--surface);border:1px solid var(--border);transition:all .25s;cursor:default;position:relative}
.heatmap-cell:hover{transform:scale(1.15);z-index:1}
.heatmap-cell.l1{background:#8b5cf615;border-color:#8b5cf630}
.heatmap-cell.l2{background:#8b5cf630;border-color:#8b5cf650;color:var(--text)}
.heatmap-cell.l3{background:#8b5cf650;border-color:#8b5cf670;color:#fff}
.heatmap-cell.l4{background:#8b5cf680;border-color:#8b5cf6;color:#fff;font-weight:700}
.heatmap-label{font-size:.65em;color:var(--text-muted);text-align:center;margin-top:2px}
.heatmap-row{display:contents}
.heatmap-legend{display:flex;align-items:center;justify-content:center;gap:6px;margin-top:12px;font-size:.65em;color:var(--text-dim)}
.heatmap-legend-cell{width:14px;height:14px;border-radius:3px}

/* Weekly chart */
.weekly-chart{display:flex;align-items:flex-end;justify-content:space-around;height:180px;gap:8px;padding:20px 0 0}
.week-col{display:flex;flex-direction:column;align-items:center;flex:1;height:100%;justify-content:flex-end}
.week-bar{width:100%;max-width:60px;border-radius:8px 8px 0 0;background:var(--gradient2);min-height:4px;transition:height .6s cubic-bezier(.22,1,.36,1);position:relative;cursor:default}
.week-bar.today{background:var(--gradient)}
.week-bar:hover{filter:brightness(1.2)}
.week-bar-val{font-size:.7em;color:var(--text-dim);margin-bottom:6px;font-weight:500}
.week-bar-label{font-size:.72em;color:var(--text-dim);margin-top:8px}
.week-bar-label.today{color:var(--accent);font-weight:600}

/* Longest session */
.longest-card{background:var(--surface);border-radius:16px;padding:20px;border:1px solid var(--border);margin-bottom:20px}
.longest-card .card-header{display:flex;align-items:center;gap:8px;font-size:.78em;color:var(--text-dim);text-transform:uppercase;letter-spacing:1px;margin-bottom:12px}
.longest-value{font-size:2em;font-weight:800;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.longest-app{font-size:.95em;color:var(--text);margin-top:4px}
.longest-time{font-size:.78em;color:var(--text-dim);margin-top:4px}

/* Status indicators */
.status-row{display:flex;gap:10px;margin-bottom:20px}
.status-pill{flex:1;display:flex;align-items:center;gap:8px;padding:10px 14px;background:var(--surface);border-radius:12px;border:1px solid var(--border);font-size:.78em;color:var(--text-dim)}
.status-pill .s-icon{font-size:1.1em}
.status-pill .s-text{flex:1}
.status-pill.active{border-color:var(--green);color:var(--green)}

/* Session correction panel */
.correction-panel{background:var(--surface);border-radius:16px;padding:20px;border:1px solid var(--border);margin-bottom:20px}
.correction-panel h3{font-size:.85em;color:var(--text-dim);margin-bottom:14px;display:flex;align-items:center;gap:8px}
.session-list{max-height:300px;overflow-y:auto;display:flex;flex-direction:column;gap:6px}
.session-item{display:flex;align-items:center;gap:10px;padding:10px 12px;background:var(--bg);border-radius:10px;font-size:.8em;border:1px solid transparent;transition:all .2s}
.session-item:hover{border-color:var(--border)}
.session-item .si-app{font-weight:600;min-width:80px}
.session-item .si-time{color:var(--text-dim);flex:1;font-variant-numeric:tabular-nums}
.session-item .si-dur{color:var(--accent);font-weight:600;min-width:50px;text-align:right}
.session-item .si-actions{display:flex;gap:4px}
.si-btn{padding:4px 10px;border-radius:6px;border:1px solid var(--border);background:transparent;color:var(--text-dim);font-size:.75em;cursor:pointer;transition:all .2s}
.si-btn:hover{border-color:var(--accent);color:var(--accent)}
.si-btn.danger:hover{border-color:var(--red);color:var(--red)}

/* Controls */
.controls{display:flex;gap:8px;justify-content:center;margin:24px 0}
.ctrl-btn{padding:10px 20px;border-radius:12px;border:1px solid var(--border);background:var(--surface);color:var(--text-dim);font-size:.82em;cursor:pointer;transition:all .25s;font-weight:500}
.ctrl-btn:hover{border-color:var(--accent);color:var(--accent);transform:translateY(-1px);box-shadow:0 4px 12px #00000030}
.ctrl-btn.danger:hover{border-color:var(--red);color:var(--red)}

/* Footer */
.footer{text-align:center;color:var(--text-muted);font-size:.7em;margin-top:32px;padding-bottom:24px}

/* Modal */
.modal-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:#00000080;backdrop-filter:blur(4px);display:none;align-items:center;justify-content:center;z-index:100}
.modal-overlay.show{display:flex}
.modal{background:var(--surface);border-radius:16px;padding:24px;border:1px solid var(--border);width:90%;max-width:400px;animation:slideUp .3s ease}
.modal h3{font-size:1em;margin-bottom:16px}
.modal label{display:block;font-size:.8em;color:var(--text-dim);margin-bottom:6px}
.modal input{width:100%;padding:10px 12px;border-radius:8px;border:1px solid var(--border);background:var(--bg);color:var(--text);font-size:.85em;margin-bottom:12px}
.modal input:focus{outline:none;border-color:var(--accent)}
.modal-actions{display:flex;gap:8px;justify-content:flex-end}
.modal-actions button{padding:8px 16px;border-radius:8px;border:1px solid var(--border);background:var(--surface);color:var(--text-dim);cursor:pointer;font-size:.82em;transition:all .2s}
.modal-actions button.primary{background:var(--gradient);color:#fff;border:none}
.modal-actions button:hover{transform:translateY(-1px)}

/* Scrollbar */
::-webkit-scrollbar{width:4px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}

/* Loading shimmer */
.loading{background:linear-gradient(90deg,var(--surface) 25%,var(--surface2) 50%,var(--surface) 75%);background-size:200% 100%;animation:shimmer 1.5s infinite;border-radius:8px;min-height:40px}

/* Responsive */
@media(max-width:600px){
  .stats-grid{grid-template-columns:repeat(2,1fr)}
  .heatmap{grid-template-columns:repeat(6,1fr)}
  .total-big{font-size:2.5em}
  .header h1{font-size:1.4em}
  .app-row{padding:12px}
  .weekly-chart{height:140px}
}
</style>
</head>
<body>
<div class="container">

<!-- Night Owl Alert -->
<div class="alert-banner night-owl-banner" id="nightOwl">
  <span class="owl-icon">&#x1f989;</span>
  <div class="alert-text" id="nightOwlText">She's staying up late!</div>
</div>

<!-- All-Nighter Alert -->
<div class="alert-banner all-nighter-banner" id="allNighter">
  <span class="alert-icon">&#x1f6a8;</span>
  <div class="alert-text" id="allNighterText">ALL-NIGHTER DETECTED</div>
</div>

<!-- Header -->
<div class="header">
  <h1>Screen Time Tracker</h1>
  <div class="header-meta">
    <span class="status-dot" id="statusDot"></span>
    <span id="dateDisplay">Loading...</span>
  </div>
  <div class="total-big" id="totalTime">--</div>
  <div class="total-label">Total Screen Time Today</div>
</div>

<!-- Current Activity -->
<div class="current-card" id="currentCard">
  <div class="current-label"><div class="live-dot"></div> Currently Using</div>
  <div class="current-app" id="currentApp">--</div>
  <div class="current-duration" id="currentDur">--</div>
</div>

<!-- Stats Grid -->
<div class="stats-grid" id="statsGrid">
  <div class="stat-card"><div class="stat-icon">&#x23f1;</div><div class="stat-value" id="statTotal">--</div><div class="stat-label">Total Time</div></div>
  <div class="stat-card"><div class="stat-icon">&#x1f4f1;</div><div class="stat-value" id="statApps">--</div><div class="stat-label">Apps Used</div></div>
  <div class="stat-card"><div class="stat-icon">&#x1f446;</div><div class="stat-value" id="statOpens">--</div><div class="stat-label">Opens</div></div>
  <div class="stat-card"><div class="stat-icon">&#x1f451;</div><div class="stat-value" id="statTop">--</div><div class="stat-label">Top App</div></div>
</div>

<!-- Tabs -->
<div class="tabs">
  <div class="tab active" data-tab="apps" onclick="switchTab('apps')">&#x1f4f1; Apps</div>
  <div class="tab" data-tab="heatmap" onclick="switchTab('heatmap')">&#x1f525; Heatmap</div>
  <div class="tab" data-tab="weekly" onclick="switchTab('weekly')">&#x1f4ca; Weekly</div>
  <div class="tab" data-tab="sessions" onclick="switchTab('sessions')">&#x1f4cb; Sessions</div>
</div>

<!-- Tab: Apps -->
<div class="tab-panel show" id="panel-apps">
  <div class="app-list" id="appList"><div class="loading" style="height:200px"></div></div>
</div>

<!-- Tab: Heatmap -->
<div class="tab-panel" id="panel-heatmap">
  <div style="background:var(--surface);border-radius:16px;padding:20px;border:1px solid var(--border)">
    <div style="font-size:.85em;color:var(--text-dim);margin-bottom:14px;text-align:center">Hourly Activity Heatmap (Last 7 Days)</div>
    <div class="heatmap" id="heatmap"></div>
    <div class="heatmap-legend">
      <span>Less</span>
      <div class="heatmap-legend-cell" style="background:var(--surface)"></div>
      <div class="heatmap-legend-cell" style="background:#8b5cf615"></div>
      <div class="heatmap-legend-cell" style="background:#8b5cf630"></div>
      <div class="heatmap-legend-cell" style="background:#8b5cf650"></div>
      <div class="heatmap-legend-cell" style="background:#8b5cf680"></div>
      <span>More</span>
    </div>
  </div>
</div>

<!-- Tab: Weekly -->
<div class="tab-panel" id="panel-weekly">
  <div style="background:var(--surface);border-radius:16px;padding:20px;border:1px solid var(--border)">
    <div style="font-size:.85em;color:var(--text-dim);margin-bottom:8px;text-align:center">Weekly Screen Time</div>
    <div class="weekly-chart" id="weeklyChart"></div>
  </div>
</div>

<!-- Tab: Sessions -->
<div class="tab-panel" id="panel-sessions">
  <div class="correction-panel">
    <h3>&#x1f4cb; Recent Sessions</h3>
    <div class="session-list" id="sessionList"><div class="loading" style="height:150px"></div></div>
  </div>
</div>

<!-- Longest Session -->
<div class="longest-card" id="longestCard" style="display:none">
  <div class="card-header">&#x1f3c6; Longest Session Today</div>
  <div class="longest-value" id="longestValue">--</div>
  <div class="longest-app" id="longestApp">--</div>
  <div class="longest-time" id="longestTime">--</div>
</div>

<!-- Status row -->
<div class="status-row" id="statusRow">
  <div class="status-pill" id="chargingStatus"><span class="s-icon">&#x1f50b;</span><span class="s-text">Unknown</span></div>
  <div class="status-pill" id="locationStatus"><span class="s-icon">&#x1f3e0;</span><span class="s-text">Unknown</span></div>
</div>

<!-- Controls -->
<div class="controls">
  <button class="ctrl-btn" onclick="refreshAll()">&#x1f504; Refresh</button>
  <button class="ctrl-btn danger" onclick="resetAll()">&#x23f9; Reset All</button>
</div>

<!-- Footer -->
<div class="footer">
  Screen Time Tracker v3.0 &middot; Auto-refreshes every 30s &middot; <span id="lastUpdated">--</span>
</div>

</div>

<!-- Edit Modal -->
<div class="modal-overlay" id="editModal">
  <div class="modal">
    <h3>Edit Session</h3>
    <input type="hidden" id="editSessionId">
    <label>Session: <span id="editSessionInfo" style="color:var(--text)"></span></label>
    <label style="margin-top:8px">New End Time (YYYY-MM-DD HH:MM:SS)</label>
    <input type="text" id="editEndTime" placeholder="2026-03-27 14:30:00">
    <div class="modal-actions">
      <button onclick="closeModal()">Cancel</button>
      <button class="primary" onclick="saveEdit()">Save</button>
    </div>
  </div>
</div>

<script>
const API = window.location.origin;
const ICONS = {
  '\u76f8\u518c':'&#x1f5bc;','\u5907\u5fd8\u5f55':'&#x1f4dd;','Safari\u6d4f\u89c8\u5668':'&#x1f9ed;',
  '\u624b\u673a\u8bbe\u7f6e':'&#x2699;','\u5c0f\u7ea2\u4e66':'&#x1f4d5;','WeChat':'&#x1f4ac;',
  'Telegram':'&#x2708;','\u7535\u8bdd':'&#x1f4de;','Oura':'&#x1f48d;','\u76f8\u673a':'&#x1f4f7;',
  'Discord':'&#x1f3ae;','\u4fe1\u606f':'&#x1f48c;','YouTube':'&#x25b6;','Twitter':'&#x1f426;',
  'Instagram':'&#x1f4f8;','TikTok':'&#x1f3b5;','Claude':'&#x1f916;','\u8ba1\u7b97\u5668':'&#x1f522;',
  '\u5929\u6c14':'&#x1f324;','\u5730\u56fe':'&#x1f5fa;','\u97f3\u4e50':'&#x1f3b5;','\u90ae\u4ef6':'&#x1f4e7;',
  '\u65e5\u5386':'&#x1f4c5;','\u65f6\u949f':'&#x23f0;','\u6587\u4ef6':'&#x1f4c1;','App Store':'&#x1f3ea;',
  '\u5065\u5eb7':'&#x2764;','Safari':'&#x1f9ed;','Notes':'&#x1f4dd;','Settings':'&#x2699;',
  'Photos':'&#x1f5bc;','Camera':'&#x1f4f7;','Messages':'&#x1f48c;','Phone':'&#x1f4de;',
  'Mail':'&#x1f4e7;','Calendar':'&#x1f4c5;','Clock':'&#x23f0;','Files':'&#x1f4c1;',
  'Health':'&#x2764;','Maps':'&#x1f5fa;','Weather':'&#x1f324;','Music':'&#x1f3b5;',
  'Calculator':'&#x1f522;'
};
function ic(n){return ICONS[n]||'&#x1f4f1;'}

function fmt(sec){
  if(!sec||sec<0) return '0s';
  sec=Math.round(sec);
  if(sec<60) return sec+'s';
  const m=Math.floor(sec/60);
  if(m<60) return m+'m';
  const h=Math.floor(m/60),rm=m%60;
  return rm?h+'h '+rm+'m':h+'h';
}

function fmtMins(mins){return fmt(mins*60)}

let currentTab='apps';
let activeSessionStart=null;
let activeApp=null;
let timerInterval=null;

function switchTab(tab){
  currentTab=tab;
  document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('active',t.dataset.tab===tab));
  document.querySelectorAll('.tab-panel').forEach(p=>p.classList.toggle('show',p.id==='panel-'+tab));
  if(tab==='weekly') loadWeekly();
  if(tab==='heatmap') loadHeatmap();
  if(tab==='sessions') loadSessions();
}

function startLiveTimer(){
  if(timerInterval) clearInterval(timerInterval);
  if(!activeSessionStart) return;
  timerInterval = setInterval(()=>{
    const now=Date.now();
    const dur=Math.floor((now-activeSessionStart)/1000);
    const el=document.getElementById('currentDur');
    if(el) el.textContent=fmt(dur);
  },1000);
}

async function refreshAll(){
  try{
    const [todayRes,nightRes,allNightRes,longestRes]=await Promise.all([
      fetch(API+'/api/screentime/today'),
      fetch(API+'/api/screentime/nightowl'),
      fetch(API+'/api/screentime/allnighter'),
      fetch(API+'/api/screentime/longest'),
    ]);
    const data=await todayRes.json();
    const night=await nightRes.json();
    const allNight=await allNightRes.json();
    const longest=await longestRes.json();

    // Night owl banner
    const owlBanner=document.getElementById('nightOwl');
    if(night.is_staying_up_late){
      owlBanner.classList.add('show');
      document.getElementById('nightOwlText').textContent=
        'She\'s staying up late! Using: '+(night.currently_using||night.night_apps.join(', ')||'phone');
    }else{owlBanner.classList.remove('show')}

    // All-nighter banner
    const allBanner=document.getElementById('allNighter');
    if(allNight.is_all_nighter){allBanner.classList.add('show')}else{allBanner.classList.remove('show')}

    // Header
    document.getElementById('dateDisplay').textContent=data.date+' \u00b7 '+data.current_time+' '+data.timezone;
    document.getElementById('totalTime').textContent=data.total_formatted;

    // Current activity
    const curCard=document.getElementById('currentCard');
    const activeApps=data.apps.filter(a=>a.status==='active');
    if(activeApps.length>0){
      curCard.classList.add('show');
      const a=activeApps[0];
      document.getElementById('currentApp').innerHTML=ic(a.app)+' '+a.app;
      activeSessionStart=Date.now()-(a.current_session_seconds*1000);
      activeApp=a.app;
      startLiveTimer();
      document.getElementById('statusDot').style.background='var(--green)';
    }else{
      curCard.classList.remove('show');
      activeSessionStart=null;
      activeApp=null;
      if(timerInterval){clearInterval(timerInterval);timerInterval=null}
      document.getElementById('statusDot').style.background='var(--text-muted)';
    }

    // Stats
    document.getElementById('statTotal').textContent=data.total_formatted;
    document.getElementById('statApps').textContent=data.app_count;
    document.getElementById('statOpens').textContent=data.total_opens;
    document.getElementById('statTop').innerHTML=data.apps.length>0?ic(data.apps[0].app):'-';
    if(data.apps.length>0){
      document.querySelector('#statsGrid .stat-card:last-child .stat-label').textContent=data.apps[0].app;
    }

    // App list
    const maxSec=data.apps.length>0?data.apps[0].total_seconds:1;
    document.getElementById('appList').innerHTML=data.apps.map((a,i)=>{
      const isActive=a.status==='active';
      const pct=Math.max(2,a.total_seconds/maxSec*100);
      return `<div class="app-row ${isActive?'active-session':''}" style="animation-delay:${i*0.04}s">
        <div class="app-rank ${i<3?'top':''}">${i+1}</div>
        <div class="app-icon">${ic(a.app)}</div>
        <div class="app-info">
          <div class="app-name">${a.app}${isActive?'<span class="app-badge live">LIVE</span>':''}</div>
          <div class="app-meta"><span>${a.open_count} opens</span><span>${a.percentage}%</span>${isActive?'<span>'+a.current_session_formatted+'</span>':''}</div>
          <div class="app-bar-bg"><div class="app-bar-fill ${isActive?'live':''}" style="width:${pct}%"></div></div>
        </div>
        <div class="app-right">
          <div class="app-time">
            <div class="app-time-value">${a.total_formatted}</div>
            <div class="app-time-pct">${a.total_minutes}m</div>
          </div>
        </div>
      </div>`;
    }).join('')||'<div style="text-align:center;padding:40px;color:var(--text-dim)">No activity yet today</div>';

    // Longest session
    const lc=document.getElementById('longestCard');
    if(longest.found){
      lc.style.display='block';
      document.getElementById('longestValue').textContent=longest.duration_formatted;
      document.getElementById('longestApp').innerHTML=ic(longest.app)+' '+longest.app;
      document.getElementById('longestTime').textContent=longest.started+' \u2192 '+longest.ended;
    }else{lc.style.display='none'}

    // Status pills (charging & location from recent events)
    try{
      const chargeRes=await fetch(API+'/api/event/charging_history');
      const chargeData=await chargeRes.json();
      if(chargeData.events&&chargeData.events.length>0){
        const last=chargeData.events[0];
        const pill=document.getElementById('chargingStatus');
        if(last.type==='charging_start'){pill.classList.add('active');pill.querySelector('.s-text').textContent='Charging'}
        else{pill.classList.remove('active');pill.querySelector('.s-text').textContent='Not charging'}
      }
    }catch(e){}
    try{
      const locRes=await fetch(API+'/api/event/location_history');
      const locData=await locRes.json();
      if(locData.events&&locData.events.length>0){
        const last=locData.events[0];
        const pill=document.getElementById('locationStatus');
        if(last.type==='arrived_home'){pill.classList.add('active');pill.querySelector('.s-text').textContent='At home'}
        else{pill.classList.remove('active');pill.querySelector('.s-text').textContent='Away'}
      }
    }catch(e){}

    document.getElementById('lastUpdated').textContent='Updated '+new Date().toLocaleTimeString();
    if(currentTab==='weekly') loadWeekly();
    if(currentTab==='heatmap') loadHeatmap();
    if(currentTab==='sessions') loadSessions();
  }catch(e){
    console.error(e);
    document.getElementById('totalTime').textContent='Error';
  }
}

async function loadWeekly(){
  try{
    const res=await fetch(API+'/api/screentime/weekly');
    const data=await res.json();
    const days=Object.entries(data.days).sort((a,b)=>a[0].localeCompare(b[0]));
    const maxSec=Math.max(...days.map(([_,d])=>d.total_seconds),1);
    const todayStr=new Date().toISOString().slice(0,10);
    document.getElementById('weeklyChart').innerHTML=days.map(([date,d])=>{
      const h=Math.max(4,d.total_seconds/maxSec*140);
      const isToday=date===todayStr;
      return `<div class="week-col">
        <div class="week-bar-val">${d.total_formatted}</div>
        <div class="week-bar ${isToday?'today':''}" style="height:${h}px" title="${date}: ${d.total_formatted}"></div>
        <div class="week-bar-label ${isToday?'today':''}">${d.weekday}${isToday?' *':''}</div>
      </div>`;
    }).join('');
  }catch(e){}
}

async function loadHeatmap(){
  try{
    const res=await fetch(API+'/api/screentime/hourly');
    const data=await res.json();
    const hours=data.hours;
    const maxSec=Math.max(...Object.values(hours).map(h=>h.total_seconds),1);
    let html='';
    for(let h=0;h<24;h++){
      const info=hours[h]||{total_seconds:0,session_count:0,total_formatted:'0m'};
      const ratio=info.total_seconds/maxSec;
      let level='';
      if(ratio>0.75) level='l4';
      else if(ratio>0.5) level='l3';
      else if(ratio>0.25) level='l2';
      else if(ratio>0) level='l1';
      const label=h.toString().padStart(2,'0');
      html+=`<div class="heatmap-cell ${level}" title="${label}:00 - ${info.total_formatted} (${info.session_count} sessions)">${label}</div>`;
    }
    document.getElementById('heatmap').innerHTML=html;
  }catch(e){}
}

async function loadSessions(){
  try{
    const res=await fetch(API+'/api/screentime/sessions');
    const data=await res.json();
    document.getElementById('sessionList').innerHTML=data.sessions.map(s=>{
      const endStr=s.end?s.end.split(' ').pop():'active';
      const startStr=s.start.split(' ').pop();
      return `<div class="session-item">
        <span class="si-app">${ic(s.app)} ${s.app}</span>
        <span class="si-time">${startStr} \u2192 ${endStr}</span>
        <span class="si-dur">${s.duration_formatted}</span>
        <div class="si-actions">
          <button class="si-btn" onclick="editSession(${s.id},'${s.app}','${s.start}')">Edit</button>
          <button class="si-btn danger" onclick="deleteSession(${s.id})">Del</button>
        </div>
      </div>`;
    }).join('')||'<div style="text-align:center;padding:20px;color:var(--text-dim)">No sessions</div>';
  }catch(e){}
}

async function resetAll(){
  if(!confirm('Reset all active sessions?')) return;
  await fetch(API+'/api/screentime/reset_all');
  refreshAll();
}

function editSession(id,app,start){
  document.getElementById('editSessionId').value=id;
  document.getElementById('editSessionInfo').textContent=app+' started '+start;
  document.getElementById('editEndTime').value='';
  document.getElementById('editModal').classList.add('show');
}

function closeModal(){document.getElementById('editModal').classList.remove('show')}

async function saveEdit(){
  const id=document.getElementById('editSessionId').value;
  const endTime=document.getElementById('editEndTime').value;
  if(!endTime){alert('Please enter an end time');return}
  try{
    await fetch(API+'/api/screentime/correct/'+id,{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({end_ts:endTime})
    });
    closeModal();
    refreshAll();
  }catch(e){alert('Error saving')}
}

async function deleteSession(id){
  if(!confirm('Delete this session?')) return;
  await fetch(API+'/api/screentime/session/'+id,{method:'DELETE'});
  refreshAll();
}

// Init
refreshAll();
setInterval(refreshAll,30000);

// Close modal on backdrop click
document.getElementById('editModal').addEventListener('click',function(e){
  if(e.target===this) closeModal();
});
</script>
</body>
</html>"""
