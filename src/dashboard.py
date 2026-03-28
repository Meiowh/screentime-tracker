"""Dashboard — returns a complete HTML string for a single-page screen time dashboard.
Theme: Kawaii Night Sky — cute dreamy dark purple/pink with floating star particles.
"""


def render_dashboard() -> str:
    return r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Screen Time Tracker</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=LXGW+WenKai:wght@400;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#0c0a1a;--surface:rgba(30,20,60,0.55);--surface2:rgba(45,30,80,0.5);
  --border:rgba(192,132,252,0.15);--border-hover:rgba(192,132,252,0.35);
  --text:#ede9fe;--text-dim:#a78bfa;--text-muted:#5b4a8a;
  --primary:#c084fc;--secondary:#f472b6;
  --accent:#38bdf8;--green:#4ade80;--amber:#fbbf24;--red:#f87171;
  --gradient:linear-gradient(135deg,#c084fc,#f472b6);
  --gradient2:linear-gradient(135deg,#7c3aed,#c084fc);
  --glow-primary:rgba(192,132,252,0.25);--glow-pink:rgba(244,114,182,0.25);
  --glow-green:rgba(74,222,128,0.25);--glow-red:rgba(248,113,113,0.25);
}
body{
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Inter',system-ui,sans-serif;
  background:var(--bg);color:var(--text);min-height:100vh;overflow-x:hidden;
  position:relative;
}

/* Floating star particles (CSS only) */
.stars{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;overflow:hidden}
.star{position:absolute;border-radius:50%;background:#fff;opacity:0;animation:twinkle var(--dur) var(--delay) ease-in-out infinite}
@keyframes twinkle{0%,100%{opacity:0;transform:scale(0.5)}50%{opacity:var(--opacity);transform:scale(1)}}
.star.shape{border-radius:0;background:none;font-size:var(--size);line-height:1;animation:twinkleShape var(--dur) var(--delay) ease-in-out infinite}
@keyframes twinkleShape{0%,100%{opacity:0;transform:scale(0.5) rotate(0deg)}50%{opacity:var(--opacity);transform:scale(1) rotate(20deg)}}

.container{max-width:900px;margin:0 auto;padding:20px 16px 40px;position:relative;z-index:1}

/* Headings use LXGW WenKai */
h1,h2,h3,.tab,.ctrl-btn,.stat-label,.card-header,.alert-text,.total-label{font-family:'LXGW WenKai',-apple-system,BlinkMacSystemFont,sans-serif}

/* Animations */
@keyframes fadeInUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeInLeft{from{opacity:0;transform:translateX(-12px)}to{opacity:1;transform:translateX(0)}}
@keyframes countPop{from{opacity:0;transform:scale(0.85)}to{opacity:1;transform:scale(1)}}
@keyframes owlFloat{0%,100%{transform:translateY(0) rotate(-5deg)}50%{transform:translateY(-10px) rotate(5deg)}}
@keyframes alertPulse{0%,100%{border-color:var(--red);box-shadow:0 0 20px var(--glow-red)}50%{border-color:#ff8a8a;box-shadow:0 0 40px var(--glow-red),0 0 80px rgba(248,113,113,0.1)}}
@keyframes softPulse{0%,100%{opacity:1}50%{opacity:0.7}}
@keyframes glowPulse{0%,100%{box-shadow:0 0 15px var(--glow-green)}50%{box-shadow:0 0 30px var(--glow-green),0 0 60px var(--glow-green)}}
@keyframes barGrow{from{width:0}to{width:var(--tw)}}
@keyframes dotBounce{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.4;transform:scale(0.8)}}
@keyframes shimmer{0%{background-position:-200% 0}100%{background-position:200% 0}}
@keyframes hoverLift{from{transform:translateY(0)}to{transform:translateY(-4px)}}
@keyframes sparkle{0%,100%{opacity:0.3;transform:scale(0.8)}50%{opacity:1;transform:scale(1.2)}}

/* Glassmorphism card base */
.glass{
  background:var(--surface);
  backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
  border:1px solid var(--border);
  border-radius:20px;
  transition:all 0.3s ease;
}
.glass:hover{border-color:var(--border-hover);transform:translateY(-2px);box-shadow:0 8px 32px rgba(0,0,0,0.3)}

/* Header */
.header{text-align:center;padding:36px 0 28px;position:relative;animation:fadeInUp 0.6s ease}
.header::before{content:'';position:absolute;top:-20px;left:50%;transform:translateX(-50%);width:300px;height:300px;background:radial-gradient(circle,rgba(192,132,252,0.08),transparent 70%);pointer-events:none}
.header h1{
  font-family:'LXGW WenKai',sans-serif;
  font-size:2em;font-weight:700;
  background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  letter-spacing:0.05em;
}
.header-sub{font-size:0.85em;color:var(--text-muted);margin-top:4px;font-family:'LXGW WenKai',sans-serif}
.header-meta{display:flex;align-items:center;justify-content:center;gap:12px;margin-top:10px;color:var(--text-dim);font-size:0.8em}
.status-dot{width:7px;height:7px;border-radius:50%;background:var(--green);animation:dotBounce 2s ease infinite;display:inline-block}
.total-big{
  font-size:3.8em;font-weight:800;margin-top:16px;
  background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  animation:countPop 0.6s ease;line-height:1.1;
  filter:drop-shadow(0 0 20px rgba(192,132,252,0.3));
}
.total-label{color:var(--text-dim);font-size:0.82em;margin-top:6px;letter-spacing:3px}

/* Alert banners */
.alert-banner{padding:18px 22px;border-radius:20px;margin-bottom:16px;display:none;animation:fadeInUp 0.4s ease;text-align:center;backdrop-filter:blur(12px)}
.alert-banner.show{display:block}
.night-owl-banner{
  background:linear-gradient(135deg,rgba(88,28,135,0.4),rgba(124,58,237,0.2));
  border:1px solid rgba(192,132,252,0.3);
  box-shadow:0 4px 24px rgba(139,92,246,0.15);
}
.night-owl-banner .owl-icon{font-size:2.2em;animation:owlFloat 3s ease-in-out infinite;display:inline-block}
.night-owl-banner .alert-text{color:#ddd6fe;font-size:0.9em;margin-top:8px;font-weight:500}
.all-nighter-banner{
  background:linear-gradient(135deg,rgba(127,29,29,0.4),rgba(185,28,28,0.2));
  border:1px solid var(--red);
  animation:alertPulse 2s ease-in-out infinite;
}
.all-nighter-banner .alert-icon{font-size:2em}
.all-nighter-banner .alert-text{color:#fecaca;font-size:0.9em;margin-top:8px;font-weight:600}

/* Current activity card */
.current-card{
  padding:22px;border-radius:20px;
  background:linear-gradient(135deg,rgba(6,78,59,0.3),rgba(4,120,87,0.15));
  border:1px solid rgba(74,222,128,0.2);
  margin-bottom:20px;display:none;
  animation:glowPulse 3s ease-in-out infinite;
  backdrop-filter:blur(12px);
}
.current-card.show{display:block;animation:fadeInUp 0.4s ease,glowPulse 3s ease-in-out infinite}
.current-label{display:flex;align-items:center;gap:8px;color:var(--green);font-size:0.75em;text-transform:uppercase;letter-spacing:2px;font-weight:600}
.current-label .live-dot{width:9px;height:9px;border-radius:50%;background:var(--green);animation:dotBounce 1.5s ease infinite}
.current-app{font-size:1.5em;font-weight:700;margin-top:10px}
.current-duration{color:var(--green);font-size:1.1em;margin-top:6px;font-variant-numeric:tabular-nums}

/* Stats grid */
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:22px}
.stat-card{
  background:var(--surface);backdrop-filter:blur(12px);
  border-radius:20px;padding:18px 14px;
  border:1px solid var(--border);
  text-align:center;transition:all 0.3s ease;
  position:relative;overflow:hidden;
  animation:fadeInUp 0.5s ease backwards;
}
.stat-card:nth-child(1){animation-delay:0.05s}
.stat-card:nth-child(2){animation-delay:0.1s}
.stat-card:nth-child(3){animation-delay:0.15s}
.stat-card:nth-child(4){animation-delay:0.2s}
.stat-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--gradient);opacity:0;transition:opacity 0.3s}
.stat-card:hover{border-color:var(--border-hover);transform:translateY(-4px);box-shadow:0 8px 24px rgba(0,0,0,0.3)}.stat-card:hover::before{opacity:1}
.stat-icon{font-size:1.6em;margin-bottom:8px}
.stat-value{font-size:1.6em;font-weight:700;color:var(--primary)}
.stat-label{font-size:0.72em;color:var(--text-dim);margin-top:6px;letter-spacing:1px}

/* Tabs */
.tabs{
  display:flex;gap:6px;margin-bottom:22px;
  background:var(--surface);backdrop-filter:blur(12px);
  border-radius:20px;padding:6px;
  border:1px solid var(--border);
}
.tab{
  flex:1;padding:12px 8px;
  background:transparent;border:none;border-radius:16px;
  color:var(--text-dim);cursor:pointer;font-size:0.84em;
  text-align:center;transition:all 0.3s ease;font-weight:500;
}
.tab.active{
  background:var(--gradient);color:#fff;
  box-shadow:0 4px 16px rgba(192,132,252,0.3);
  font-weight:700;
}
.tab:hover:not(.active){color:var(--text);background:rgba(192,132,252,0.08)}
.tab-panel{display:none;animation:fadeInUp 0.35s ease}.tab-panel.show{display:block}

/* App ranking */
.app-list{display:flex;flex-direction:column;gap:10px}
.app-row{
  display:flex;align-items:center;gap:14px;
  background:var(--surface);backdrop-filter:blur(12px);
  border-radius:20px;padding:16px 18px;
  border:1px solid var(--border);
  transition:all 0.3s ease;
  animation:fadeInLeft 0.35s ease backwards;
}
.app-row:hover{border-color:var(--border-hover);background:var(--surface2);transform:translateX(4px);box-shadow:0 4px 20px rgba(0,0,0,0.2)}
.app-row.active-session{border-color:rgba(74,222,128,0.25);box-shadow:0 0 20px var(--glow-green)}
.app-rank{
  width:28px;height:28px;border-radius:10px;
  background:var(--surface2);
  display:flex;align-items:center;justify-content:center;
  font-size:0.72em;font-weight:700;color:var(--text-dim);flex-shrink:0;
}
.app-rank.gold{background:linear-gradient(135deg,#fbbf24,#f59e0b);color:#451a03;box-shadow:0 2px 8px rgba(251,191,36,0.3)}
.app-rank.silver{background:linear-gradient(135deg,#d1d5db,#9ca3af);color:#1f2937}
.app-rank.bronze{background:linear-gradient(135deg,#d97706,#b45309);color:#fff}
.app-icon{font-size:1.5em;flex-shrink:0}
.app-info{flex:1;min-width:0}
.app-name{font-size:0.92em;font-weight:600;display:flex;align-items:center;gap:10px}
.app-badge{font-size:0.6em;padding:3px 10px;border-radius:20px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px}
.app-badge.live{background:rgba(74,222,128,0.15);color:var(--green);border:1px solid rgba(74,222,128,0.3)}
.app-meta{font-size:0.73em;color:var(--text-dim);margin-top:4px;display:flex;gap:12px}
.app-bar-bg{height:5px;background:rgba(192,132,252,0.1);border-radius:3px;margin-top:8px;overflow:hidden}
.app-bar-fill{height:100%;border-radius:3px;background:var(--gradient);transition:width 0.8s cubic-bezier(0.22,1,0.36,1)}
.app-bar-fill.live{background:linear-gradient(90deg,var(--green),#86efac)}
.app-right{display:flex;align-items:center;gap:12px;flex-shrink:0}
.app-time{text-align:right}
.app-time-value{font-size:1.2em;font-weight:700;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.app-time-pct{font-size:0.68em;color:var(--text-dim)}

/* Hourly heatmap */
.heatmap-wrap{background:var(--surface);backdrop-filter:blur(12px);border-radius:20px;padding:22px;border:1px solid var(--border)}
.heatmap-title{font-size:0.88em;color:var(--text-dim);margin-bottom:16px;text-align:center;font-family:'LXGW WenKai',sans-serif}
.heatmap{display:grid;grid-template-columns:repeat(12,1fr);gap:5px;margin-top:8px}
.heatmap-cell{
  aspect-ratio:1;border-radius:8px;
  display:flex;align-items:center;justify-content:center;
  font-size:0.62em;color:var(--text-dim);
  background:rgba(30,20,60,0.5);border:1px solid var(--border);
  transition:all 0.25s;cursor:default;position:relative;
}
.heatmap-cell:hover{transform:scale(1.18);z-index:1;box-shadow:0 0 12px rgba(192,132,252,0.2)}
.heatmap-cell.l1{background:rgba(192,132,252,0.1);border-color:rgba(192,132,252,0.2)}
.heatmap-cell.l2{background:rgba(192,132,252,0.25);border-color:rgba(192,132,252,0.35);color:var(--text)}
.heatmap-cell.l3{background:rgba(192,132,252,0.45);border-color:rgba(192,132,252,0.55);color:#fff}
.heatmap-cell.l4{background:rgba(192,132,252,0.7);border-color:var(--primary);color:#fff;font-weight:700;box-shadow:0 0 8px var(--glow-primary)}
.heatmap-legend{display:flex;align-items:center;justify-content:center;gap:8px;margin-top:14px;font-size:0.68em;color:var(--text-dim)}
.heatmap-legend-cell{width:16px;height:16px;border-radius:4px}

/* Weekly chart */
.weekly-wrap{background:var(--surface);backdrop-filter:blur(12px);border-radius:20px;padding:22px;border:1px solid var(--border)}
.weekly-title{font-size:0.88em;color:var(--text-dim);margin-bottom:10px;text-align:center;font-family:'LXGW WenKai',sans-serif}
.weekly-chart{display:flex;align-items:flex-end;justify-content:space-around;height:180px;gap:10px;padding:20px 0 0}
.week-col{display:flex;flex-direction:column;align-items:center;flex:1;height:100%;justify-content:flex-end}
.week-bar{
  width:100%;max-width:60px;border-radius:12px 12px 0 0;
  background:var(--gradient2);min-height:4px;
  transition:height 0.6s cubic-bezier(0.22,1,0.36,1);
  position:relative;cursor:default;
}
.week-bar.today{background:var(--gradient);box-shadow:0 0 12px var(--glow-primary)}
.week-bar:hover{filter:brightness(1.2)}
.week-bar-val{font-size:0.72em;color:var(--text-dim);margin-bottom:8px;font-weight:500}
.week-bar-label{font-size:0.74em;color:var(--text-dim);margin-top:10px}
.week-bar-label.today{color:var(--primary);font-weight:700}

/* Longest session */
.longest-card{
  background:var(--surface);backdrop-filter:blur(12px);
  border-radius:20px;padding:22px;
  border:1px solid var(--border);margin-bottom:20px;
  animation:fadeInUp 0.5s ease;
}
.longest-card .card-header{display:flex;align-items:center;gap:10px;font-size:0.82em;color:var(--text-dim);letter-spacing:1px;margin-bottom:14px}
.longest-value{font-size:2.2em;font-weight:800;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.longest-app{font-size:0.95em;color:var(--text);margin-top:6px}
.longest-time{font-size:0.8em;color:var(--text-dim);margin-top:6px}

/* Status indicators */
.status-row{display:flex;gap:12px;margin-bottom:20px}
.status-pill{
  flex:1;display:flex;align-items:center;gap:10px;
  padding:12px 16px;
  background:var(--surface);backdrop-filter:blur(12px);
  border-radius:16px;border:1px solid var(--border);
  font-size:0.8em;color:var(--text-dim);
  transition:all 0.3s ease;
}
.status-pill .s-icon{font-size:1.2em}
.status-pill .s-text{flex:1}
.status-pill.active{border-color:rgba(74,222,128,0.3);color:var(--green);box-shadow:0 0 12px var(--glow-green)}

/* Session correction panel */
.correction-panel{
  background:var(--surface);backdrop-filter:blur(12px);
  border-radius:20px;padding:22px;
  border:1px solid var(--border);margin-bottom:20px;
}
.correction-panel h3{font-size:0.88em;color:var(--text-dim);margin-bottom:16px;display:flex;align-items:center;gap:10px}
.session-list{max-height:340px;overflow-y:auto;display:flex;flex-direction:column;gap:8px}
.session-item{
  display:flex;align-items:center;gap:12px;
  padding:12px 14px;
  background:rgba(12,10,26,0.6);border-radius:14px;
  font-size:0.82em;border:1px solid transparent;
  transition:all 0.25s;
}
.session-item:hover{border-color:var(--border);background:rgba(30,20,60,0.4)}
.session-item .si-app{font-weight:600;min-width:90px}
.session-item .si-time{color:var(--text-dim);flex:1;font-variant-numeric:tabular-nums}
.session-item .si-dur{color:var(--primary);font-weight:600;min-width:55px;text-align:right}
.session-item .si-actions{display:flex;gap:6px}
.si-btn{
  padding:5px 12px;border-radius:10px;
  border:1px solid var(--border);background:transparent;
  color:var(--text-dim);font-size:0.75em;
  cursor:pointer;transition:all 0.25s;
}
.si-btn:hover{border-color:var(--primary);color:var(--primary);background:rgba(192,132,252,0.08)}
.si-btn.danger:hover{border-color:var(--red);color:var(--red);background:rgba(248,113,113,0.08)}

/* Controls */
.controls{display:flex;gap:10px;justify-content:center;margin:28px 0}
.ctrl-btn{
  padding:12px 24px;border-radius:16px;
  border:1px solid var(--border);
  background:var(--surface);backdrop-filter:blur(12px);
  color:var(--text-dim);font-size:0.85em;
  cursor:pointer;transition:all 0.3s ease;font-weight:600;
}
.ctrl-btn:hover{
  border-color:var(--primary);color:var(--primary);
  transform:translateY(-2px);
  box-shadow:0 6px 20px rgba(0,0,0,0.3);
  background:rgba(192,132,252,0.05);
}
.ctrl-btn.danger:hover{border-color:var(--red);color:var(--red);background:rgba(248,113,113,0.05)}

/* Footer */
.footer{
  text-align:center;color:var(--text-muted);
  font-size:0.72em;margin-top:36px;padding-bottom:28px;
  font-family:'LXGW WenKai',sans-serif;
}
.footer .sparkle{animation:sparkle 2s ease-in-out infinite;display:inline-block}

/* Modal */
.modal-overlay{
  position:fixed;top:0;left:0;right:0;bottom:0;
  background:rgba(12,10,26,0.75);
  backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);
  display:none;align-items:center;justify-content:center;z-index:100;
}
.modal-overlay.show{display:flex}
.modal{
  background:linear-gradient(160deg,rgba(30,20,60,0.95),rgba(45,30,80,0.9));
  backdrop-filter:blur(20px);
  border-radius:24px;padding:28px;
  border:1px solid var(--border);
  width:90%;max-width:420px;
  animation:fadeInUp 0.35s ease;
  box-shadow:0 20px 60px rgba(0,0,0,0.5);
}
.modal h3{
  font-size:1.1em;margin-bottom:18px;
  font-family:'LXGW WenKai',sans-serif;
  background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
.modal label{display:block;font-size:0.82em;color:var(--text-dim);margin-bottom:8px}
.modal input{
  width:100%;padding:12px 14px;border-radius:12px;
  border:1px solid var(--border);
  background:rgba(12,10,26,0.6);color:var(--text);
  font-size:0.88em;margin-bottom:14px;
  transition:border-color 0.3s;
}
.modal input:focus{outline:none;border-color:var(--primary);box-shadow:0 0 12px var(--glow-primary)}
.modal-actions{display:flex;gap:10px;justify-content:flex-end}
.modal-actions button{
  padding:10px 20px;border-radius:12px;
  border:1px solid var(--border);
  background:var(--surface);color:var(--text-dim);
  cursor:pointer;font-size:0.85em;transition:all 0.25s;
  font-family:'LXGW WenKai',sans-serif;
}
.modal-actions button.primary{background:var(--gradient);color:#fff;border:none;font-weight:700;box-shadow:0 4px 16px rgba(192,132,252,0.3)}
.modal-actions button:hover{transform:translateY(-2px)}

/* Scrollbar */
::-webkit-scrollbar{width:5px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:rgba(192,132,252,0.2);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:rgba(192,132,252,0.4)}

/* Loading shimmer */
.loading{
  background:linear-gradient(90deg,rgba(30,20,60,0.5) 25%,rgba(45,30,80,0.5) 50%,rgba(30,20,60,0.5) 75%);
  background-size:200% 100%;animation:shimmer 1.5s infinite;
  border-radius:12px;min-height:40px;
}

/* Responsive */
@media(max-width:600px){
  .stats-grid{grid-template-columns:repeat(2,1fr)}
  .heatmap{grid-template-columns:repeat(6,1fr)}
  .total-big{font-size:2.8em}
  .header h1{font-size:1.5em}
  .app-row{padding:14px}
  .weekly-chart{height:140px}
  .tabs{flex-wrap:wrap}
  .tab{font-size:0.78em;padding:10px 6px}
  .session-item{flex-wrap:wrap;gap:8px}
  .session-item .si-time{min-width:100%;order:3;font-size:0.75em}
  .status-row{flex-direction:column}
}
</style>
</head>
<body>

<!-- Floating star particles (generated by CSS + HTML) -->
<div class="stars" id="starField"></div>

<div class="container">

<!-- Night Owl Alert -->
<div class="alert-banner night-owl-banner" id="nightOwl">
  <span class="owl-icon">&#x1f63a;</span>
  <div class="alert-text" id="nightOwlText">&#x1f319; &#x5979;&#x8fd8;&#x5728;&#x718a;&#x591c;&#x54e6;&#xff5e;&#x5feb;&#x7761;&#x5427;&#xff01;</div>
</div>

<!-- All-Nighter Alert -->
<div class="alert-banner all-nighter-banner" id="allNighter">
  <span class="alert-icon">&#x1f6a8;</span>
  <div class="alert-text" id="allNighterText">&#x26a0;&#xfe0f; &#x901a;&#x5b35;&#x8b66;&#x62a5;&#xff01;&#x5979;&#x4e00;&#x6574;&#x665a;&#x6ca1;&#x7761;&#xff01;</div>
</div>

<!-- Header -->
<div class="header">
  <h1>&#x2728; &#x5c4f;&#x5e55;&#x65f6;&#x95f4;&#x8ffd;&#x8e2a;&#x5668; &#x2728;</h1>
  <div class="header-sub">&#x2726; &#x5c0f;&#x59b9;&#x7684;&#x624b;&#x673a;&#x4f7f;&#x7528;&#x62a5;&#x544a; &#x2726;</div>
  <div class="header-meta">
    <span class="status-dot" id="statusDot"></span>
    <span id="dateDisplay">&#x52a0;&#x8f7d;&#x4e2d;...</span>
  </div>
  <div class="total-big" id="totalTime">--</div>
  <div class="total-label">&#x2727; &#x4eca;&#x65e5;&#x603b;&#x5c4f;&#x5e55;&#x65f6;&#x95f4; &#x2727;</div>
</div>

<!-- Current Activity -->
<div class="current-card" id="currentCard">
  <div class="current-label"><div class="live-dot"></div> &#x6b63;&#x5728;&#x4f7f;&#x7528;</div>
  <div class="current-app" id="currentApp">--</div>
  <div class="current-duration" id="currentDur">--</div>
</div>

<!-- Stats Grid -->
<div class="stats-grid" id="statsGrid">
  <div class="stat-card"><div class="stat-icon">&#x23f3;</div><div class="stat-value" id="statTotal">--</div><div class="stat-label">&#x603b;&#x65f6;&#x957f;</div></div>
  <div class="stat-card"><div class="stat-icon">&#x1f4f1;</div><div class="stat-value" id="statApps">--</div><div class="stat-label">&#x4f7f;&#x7528;&#x5e94;&#x7528;</div></div>
  <div class="stat-card"><div class="stat-icon">&#x1f44b;</div><div class="stat-value" id="statOpens">--</div><div class="stat-label">&#x6253;&#x5f00;&#x6b21;&#x6570;</div></div>
  <div class="stat-card"><div class="stat-icon">&#x1f451;</div><div class="stat-value" id="statTop">--</div><div class="stat-label">&#x6700;&#x5e38;&#x7528;</div></div>
</div>

<!-- Tabs -->
<div class="tabs">
  <div class="tab active" data-tab="apps" onclick="switchTab('apps')">&#x1f4f1; &#x5e94;&#x7528;&#x6392;&#x884c;</div>
  <div class="tab" data-tab="heatmap" onclick="switchTab('heatmap')">&#x1f525; &#x65f6;&#x6bb5;&#x70ed;&#x529b;&#x56fe;</div>
  <div class="tab" data-tab="weekly" onclick="switchTab('weekly')">&#x1f4ca; &#x6bcf;&#x5468;&#x8d8b;&#x52bf;</div>
  <div class="tab" data-tab="sessions" onclick="switchTab('sessions')">&#x1f4cb; &#x4f1a;&#x8bdd;&#x8bb0;&#x5f55;</div>
</div>

<!-- Tab: Apps -->
<div class="tab-panel show" id="panel-apps">
  <div class="app-list" id="appList"><div class="loading" style="height:200px"></div></div>
</div>

<!-- Tab: Heatmap -->
<div class="tab-panel" id="panel-heatmap">
  <div class="heatmap-wrap">
    <div class="heatmap-title">&#x2726; 24&#x5c0f;&#x65f6;&#x6d3b;&#x52a8;&#x70ed;&#x529b;&#x56fe;&#xff08;&#x8fd1;7&#x5929;&#xff09; &#x2726;</div>
    <div class="heatmap" id="heatmap"></div>
    <div class="heatmap-legend">
      <span>&#x5c11;</span>
      <div class="heatmap-legend-cell" style="background:rgba(30,20,60,0.5)"></div>
      <div class="heatmap-legend-cell" style="background:rgba(192,132,252,0.1)"></div>
      <div class="heatmap-legend-cell" style="background:rgba(192,132,252,0.25)"></div>
      <div class="heatmap-legend-cell" style="background:rgba(192,132,252,0.45)"></div>
      <div class="heatmap-legend-cell" style="background:rgba(192,132,252,0.7)"></div>
      <span>&#x591a;</span>
    </div>
  </div>
</div>

<!-- Tab: Weekly -->
<div class="tab-panel" id="panel-weekly">
  <div class="weekly-wrap">
    <div class="weekly-title">&#x2726; &#x6bcf;&#x5468;&#x5c4f;&#x5e55;&#x65f6;&#x95f4;&#x8d8b;&#x52bf; &#x2726;</div>
    <div class="weekly-chart" id="weeklyChart"></div>
  </div>
</div>

<!-- Tab: Sessions -->
<div class="tab-panel" id="panel-sessions">
  <div class="correction-panel">
    <h3>&#x1f4cb; &#x6700;&#x8fd1;&#x4f1a;&#x8bdd;&#x8bb0;&#x5f55;</h3>
    <div class="session-list" id="sessionList"><div class="loading" style="height:150px"></div></div>
  </div>
</div>

<!-- Longest Session -->
<div class="longest-card" id="longestCard" style="display:none">
  <div class="card-header">&#x1f3c6; &#x4eca;&#x65e5;&#x6700;&#x957f;&#x4f1a;&#x8bdd;</div>
  <div class="longest-value" id="longestValue">--</div>
  <div class="longest-app" id="longestApp">--</div>
  <div class="longest-time" id="longestTime">--</div>
</div>

<!-- Status row -->
<div class="status-row" id="statusRow">
  <div class="status-pill" id="chargingStatus"><span class="s-icon">&#x1f50b;</span><span class="s-text">&#x672a;&#x77e5;</span></div>
  <div class="status-pill" id="locationStatus"><span class="s-icon">&#x1f3e0;</span><span class="s-text">&#x672a;&#x77e5;</span></div>
</div>

<!-- Controls -->
<div class="controls">
  <button class="ctrl-btn" onclick="refreshAll()">&#x1f504; &#x5237;&#x65b0;</button>
  <button class="ctrl-btn danger" onclick="resetAll()">&#x23f9; &#x91cd;&#x7f6e;&#x5168;&#x90e8;</button>
</div>

<!-- Footer -->
<div class="footer">
  <span class="sparkle">&#x2728;</span> &#x5c4f;&#x5e55;&#x65f6;&#x95f4;&#x8ffd;&#x8e2a;&#x5668; v3.0 &middot; &#x6bcf;30&#x79d2;&#x81ea;&#x52a8;&#x5237;&#x65b0; &middot; <span id="lastUpdated">--</span> <span class="sparkle">&#x2728;</span>
</div>

</div>

<!-- Edit Modal -->
<div class="modal-overlay" id="editModal">
  <div class="modal">
    <h3>&#x270f;&#xfe0f; &#x7f16;&#x8f91;&#x4f1a;&#x8bdd;</h3>
    <input type="hidden" id="editSessionId">
    <label>&#x4f1a;&#x8bdd;&#x4fe1;&#x606f;&#xff1a;<span id="editSessionInfo" style="color:var(--text)"></span></label>
    <label style="margin-top:10px">&#x65b0;&#x7ed3;&#x675f;&#x65f6;&#x95f4;&#xff08;YYYY-MM-DD HH:MM:SS&#xff09;</label>
    <input type="text" id="editEndTime" placeholder="2026-03-27 14:30:00">
    <div class="modal-actions">
      <button onclick="closeModal()">&#x53d6;&#x6d88;</button>
      <button class="primary" onclick="saveEdit()">&#x4fdd;&#x5b58;</button>
    </div>
  </div>
</div>

<script>
/* Generate star field */
(function(){
  const field=document.getElementById('starField');
  const chars=['\u2726','\u2727','\u2728','\u2606','\u00b7'];
  let html='';
  for(let i=0;i<50;i++){
    const x=Math.random()*100;
    const y=Math.random()*100;
    const dur=3+Math.random()*6;
    const delay=Math.random()*8;
    const op=0.15+Math.random()*0.35;
    if(Math.random()>0.4){
      const size=1+Math.random()*2;
      html+=`<div class="star" style="left:${x}%;top:${y}%;width:${size}px;height:${size}px;--dur:${dur}s;--delay:${delay}s;--opacity:${op}"></div>`;
    }else{
      const c=chars[Math.floor(Math.random()*chars.length)];
      const sz=8+Math.random()*14;
      html+=`<div class="star shape" style="left:${x}%;top:${y}%;--size:${sz}px;--dur:${dur}s;--delay:${delay}s;--opacity:${op}">${c}</div>`;
    }
  }
  field.innerHTML=html;
})();

const API = window.location.origin;
const ICONS = {
  '\u76f8\u518c':'\ud83d\uddbc\ufe0f','\u5907\u5fd8\u5f55':'\ud83d\udcdd','Safari\u6d4f\u89c8\u5668':'\ud83e\udded',
  '\u624b\u673a\u8bbe\u7f6e':'\u2699\ufe0f','\u5c0f\u7ea2\u4e66':'\ud83d\udcd5','WeChat':'\ud83d\udcac',
  'Telegram':'\u2708\ufe0f','\u7535\u8bdd':'\ud83d\udcde','Oura':'\ud83d\udc8d','\u76f8\u673a':'\ud83d\udcf7',
  'Discord':'\ud83c\udfae','\u4fe1\u606f':'\ud83d\udc8c','YouTube':'\u25b6\ufe0f','Twitter':'\ud83d\udc26',
  'Instagram':'\ud83d\udcf8','TikTok':'\ud83c\udfb5','Claude':'\ud83e\udd16','\u8ba1\u7b97\u5668':'\ud83d\udd22',
  '\u5929\u6c14':'\ud83c\udf24\ufe0f','\u5730\u56fe':'\ud83d\uddfa\ufe0f','\u97f3\u4e50':'\ud83c\udfb5','\u90ae\u4ef6':'\ud83d\udce7',
  '\u65e5\u5386':'\ud83d\udcc5','\u65f6\u949f':'\u23f0','\u6587\u4ef6':'\ud83d\udcc1','App Store':'\ud83c\udfea',
  '\u5065\u5eb7':'\u2764\ufe0f','\u6296\u97f3':'\ud83c\udfb5',
  'Safari':'\ud83e\udded','Notes':'\ud83d\udcdd','Settings':'\u2699\ufe0f',
  'Photos':'\ud83d\uddbc\ufe0f','Camera':'\ud83d\udcf7','Messages':'\ud83d\udc8c','Phone':'\ud83d\udcde',
  'Mail':'\ud83d\udce7','Calendar':'\ud83d\udcc5','Clock':'\u23f0','Files':'\ud83d\udcc1',
  'Health':'\u2764\ufe0f','Maps':'\ud83d\uddfa\ufe0f','Weather':'\ud83c\udf24\ufe0f','Music':'\ud83c\udfb5',
  'Calculator':'\ud83d\udd22'
};
function ic(n){return ICONS[n]||'\ud83d\udcf1';}

const WEEKDAY_CN = ['\u5468\u65e5','\u5468\u4e00','\u5468\u4e8c','\u5468\u4e09','\u5468\u56db','\u5468\u4e94','\u5468\u516d'];

function fmt(sec){
  if(!sec||sec<0) return '0\u79d2';
  sec=Math.round(sec);
  if(sec<60) return sec+'\u79d2';
  const m=Math.floor(sec/60);
  if(m<60) return m+'\u5206\u949f';
  const h=Math.floor(m/60),rm=m%60;
  return rm?h+'\u5c0f\u65f6'+rm+'\u5206':h+'\u5c0f\u65f6';
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
      const using=night.currently_using||((night.night_apps&&night.night_apps.length)?night.night_apps.join(', '):'\u624b\u673a');
      document.getElementById('nightOwlText').innerHTML=
        '\ud83c\udf19 \u5979\u8fd8\u5728\u718a\u591c\u54e6\uff5e\u6b63\u5728\u7528: '+using+' \u2014 \u5feb\u53eb\u5979\u53bb\u7761\u89c9\uff01';
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
      let rankClass='';
      if(i===0) rankClass='gold';
      else if(i===1) rankClass='silver';
      else if(i===2) rankClass='bronze';
      return `<div class="app-row ${isActive?'active-session':''}" style="animation-delay:${i*0.05}s">
        <div class="app-rank ${rankClass}">${i+1}</div>
        <div class="app-icon">${ic(a.app)}</div>
        <div class="app-info">
          <div class="app-name">${a.app}${isActive?'<span class="app-badge live">\u2726 LIVE</span>':''}</div>
          <div class="app-meta"><span>${a.open_count} \u6b21\u6253\u5f00</span><span>${a.percentage}%</span>${isActive?'<span>'+a.current_session_formatted+'</span>':''}</div>
          <div class="app-bar-bg"><div class="app-bar-fill ${isActive?'live':''}" style="width:${pct}%"></div></div>
        </div>
        <div class="app-right">
          <div class="app-time">
            <div class="app-time-value">${a.total_formatted}</div>
            <div class="app-time-pct">${a.total_minutes}\u5206\u949f</div>
          </div>
        </div>
      </div>`;
    }).join('')||'<div style="text-align:center;padding:40px;color:var(--text-dim)">\u2727 \u4eca\u5929\u8fd8\u6ca1\u6709\u6d3b\u52a8\u54e6 \u2727</div>';

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
        if(last.type==='charging_start'){pill.classList.add('active');pill.querySelector('.s-text').textContent='\u5145\u7535\u4e2d'}
        else{pill.classList.remove('active');pill.querySelector('.s-text').textContent='\u672a\u5145\u7535'}
      }
    }catch(e){}
    try{
      const locRes=await fetch(API+'/api/event/location_history');
      const locData=await locRes.json();
      if(locData.events&&locData.events.length>0){
        const last=locData.events[0];
        const pill=document.getElementById('locationStatus');
        if(last.type==='arrived_home'){pill.classList.add('active');pill.querySelector('.s-text').textContent='\u5728\u5bb6'}
        else{pill.classList.remove('active');pill.querySelector('.s-text').textContent='\u5916\u51fa'}
      }
    }catch(e){}

    document.getElementById('lastUpdated').textContent='\u66f4\u65b0\u4e8e '+new Date().toLocaleTimeString();
    if(currentTab==='weekly') loadWeekly();
    if(currentTab==='heatmap') loadHeatmap();
    if(currentTab==='sessions') loadSessions();
  }catch(e){
    console.error(e);
    document.getElementById('totalTime').textContent='\u52a0\u8f7d\u5931\u8d25';
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
      const dayOfWeek=new Date(date+'T00:00:00').getDay();
      const cnDay=WEEKDAY_CN[dayOfWeek]||d.weekday;
      return `<div class="week-col">
        <div class="week-bar-val">${d.total_formatted}</div>
        <div class="week-bar ${isToday?'today':''}" style="height:${h}px" title="${date}: ${d.total_formatted}"></div>
        <div class="week-bar-label ${isToday?'today':''}">${cnDay}${isToday?' \u2726':''}</div>
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
      const info=hours[h]||{total_seconds:0,session_count:0,total_formatted:'0\u5206'};
      const ratio=info.total_seconds/maxSec;
      let level='';
      if(ratio>0.75) level='l4';
      else if(ratio>0.5) level='l3';
      else if(ratio>0.25) level='l2';
      else if(ratio>0) level='l1';
      const label=h.toString().padStart(2,'0');
      html+=`<div class="heatmap-cell ${level}" title="${label}:00 - ${info.total_formatted} (${info.session_count} \u6b21\u4f1a\u8bdd)">${label}</div>`;
    }
    document.getElementById('heatmap').innerHTML=html;
  }catch(e){}
}

async function loadSessions(){
  try{
    const res=await fetch(API+'/api/screentime/sessions');
    const data=await res.json();
    document.getElementById('sessionList').innerHTML=data.sessions.map(s=>{
      const endStr=s.end?s.end.split(' ').pop():'\u8fdb\u884c\u4e2d';
      const startStr=s.start.split(' ').pop();
      return `<div class="session-item">
        <span class="si-app">${ic(s.app)} ${s.app}</span>
        <span class="si-time">${startStr} \u2192 ${endStr}</span>
        <span class="si-dur">${s.duration_formatted}</span>
        <div class="si-actions">
          <button class="si-btn" onclick="editSession(${s.id},'${s.app.replace(/'/g,"\\'")}','${s.start}')">\u7f16\u8f91</button>
          <button class="si-btn danger" onclick="deleteSession(${s.id})">\u5220\u9664</button>
        </div>
      </div>`;
    }).join('')||'<div style="text-align:center;padding:20px;color:var(--text-dim)">\u2727 \u6682\u65e0\u4f1a\u8bdd\u8bb0\u5f55 \u2727</div>';
  }catch(e){}
}

async function resetAll(){
  if(!confirm('\u786e\u5b9a\u8981\u91cd\u7f6e\u6240\u6709\u6d3b\u52a8\u4f1a\u8bdd\u5417\uff1f')) return;
  await fetch(API+'/api/screentime/reset_all');
  refreshAll();
}

function editSession(id,app,start){
  document.getElementById('editSessionId').value=id;
  document.getElementById('editSessionInfo').textContent=app+' \u5f00\u59cb\u4e8e '+start;
  document.getElementById('editEndTime').value='';
  document.getElementById('editModal').classList.add('show');
}

function closeModal(){document.getElementById('editModal').classList.remove('show')}

async function saveEdit(){
  const id=document.getElementById('editSessionId').value;
  const endTime=document.getElementById('editEndTime').value;
  if(!endTime){alert('\u8bf7\u8f93\u5165\u7ed3\u675f\u65f6\u95f4');return}
  try{
    await fetch(API+'/api/screentime/correct/'+id,{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({end_ts:endTime})
    });
    closeModal();
    refreshAll();
  }catch(e){alert('\u4fdd\u5b58\u5931\u8d25')}
}

async function deleteSession(id){
  if(!confirm('\u786e\u5b9a\u8981\u5220\u9664\u8fd9\u4e2a\u4f1a\u8bdd\u5417\uff1f')) return;
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
